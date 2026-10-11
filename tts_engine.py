"""
High-Fidelity Multilingual Text-to-Speech (TTS) Synthesis Engine.
Tuned specifically for clear, articulate speech in English, Telugu, Kannada, and Hindi.
Features:
- Unicode NFC normalization and OCR artifact removal
- Automatic script detection from text to prevent voice-language mismatch
- Natural Indian neural voices via Edge-TTS (Female & Male)
- Seamless sentence chunking for long documents and multi-page PDFs
- Resilient gTTS fallback
"""

import os
import io
import re
import asyncio
import hashlib
import unicodedata
from gtts import gTTS
import edge_tts
import concurrent.futures

import config

def run_in_clean_loop(coro):
    """
    Executes an async coroutine in a dedicated thread with its own clean asyncio loop.
    Avoids all nest_asyncio and uvicorn loop_factory conflicts in Python 3.12.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

# Voice catalogs for high-clarity speech
VOICE_CATALOG = {
    "te": {
        "name": "Telugu (తెలుగు)",
        "female": "te-IN-ShrutiNeural",
        "male": "te-IN-MohanNeural",
        "gtts": "te"
    },
    "kn": {
        "name": "Kannada (ಕನ್ನಡ)",
        "female": "kn-IN-SapnaNeural",
        "male": "kn-IN-GaganNeural",
        "gtts": "kn"
    },
    "hi": {
        "name": "Hindi (हिंदी)",
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
        "gtts": "hi"
    },
    "en": {
        "name": "English",
        "female": "en-IN-NeerjaNeural",
        "male": "en-IN-PrabhatNeural",
        "gtts": "en"
    }
}

def clean_text_for_speech(text):
    """
    Sanitizes raw or OCR text to maximize TTS clarity and natural pronunciation:
    - Normalizes Indic Unicode to NFC (merges vowel matras and conjuncts)
    - Removes page divider tags (e.g. '--- Page 1 ---')
    - Reconnects words broken across line wraps (e.g. 're-\ncognition' -> 'recognition')
    - Removes OCR noise artifacts (stray pipes, tildes, backslashes, bullets)
    - Unifies line breaks into smooth, flowing sentence structures
    """
    if not text:
        return ""

    # 1. Unicode NFC normalization (CRUCIAL for Indic scripts!)
    text = unicodedata.normalize("NFC", text)

    # 2. Strip page header tags from PDFs
    text = re.sub(r"--- Page \d+.*---", " ", text)

    # 3. Reconnect words split across lines by hyphens
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # 4. Remove soft hyphens and zero-width non-breaking spaces
    text = text.replace("\xad", "").replace("\ufeff", "")

    # 5. Remove stray OCR artifacts and punctuation noise
    text = re.sub(r"[|~_\\^`•*#@]+", " ", text)
    text = re.sub(r"\[\s*\]|\(\s*\)|\{\s*\}", " ", text)

    # 6. Unify line breaks within paragraphs
    # Split into lines and group by empty lines (true paragraphs)
    paragraphs = []
    current_para = []

    for line in text.split("\n"):
        clean_line = line.strip()
        if not clean_line:
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
        else:
            current_para.append(clean_line)

    if current_para:
        paragraphs.append(" ".join(current_para))

    # Join paragraphs with double newline
    joined_text = "\n\n".join(paragraphs)

    # 7. Collapse repeated spaces
    joined_text = re.sub(r"[ \t]+", " ", joined_text).strip()

    return joined_text

def detect_text_script_for_tts(text):
    """
    Detects the primary language of the text to ensure the appropriate native voice is assigned.
    """
    counts = {"te": 0, "kn": 0, "hi": 0, "en": 0}
    for char in text:
        cp = ord(char)
        if 0x0C00 <= cp <= 0x0C7F:
            counts["te"] += 1
        elif 0x0C80 <= cp <= 0x0CFF:
            counts["kn"] += 1
        elif 0x0900 <= cp <= 0x097F:
            counts["hi"] += 1
        elif (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
            counts["en"] += 1

    # Check Indic scripts first
    indic_total = counts["te"] + counts["kn"] + counts["hi"]
    if indic_total > 0:
        indic_counts = {"te": counts["te"], "kn": counts["kn"], "hi": counts["hi"]}
        top_lang = max(indic_counts.items(), key=lambda x: x[1])[0]
        return top_lang
    return "en"

def format_rate_string(speed_multiplier):
    """
    Converts 0.5x - 2.0x multiplier to edge-tts rate format: e.g. '+20%', '-15%'
    """
    percent = int(round((speed_multiplier - 1.0) * 100))
    if percent >= 0:
        return f"+{percent}%"
    else:
        return f"{percent}%"

def split_into_speech_chunks(text, max_chunk_chars=350):
    """
    Splits long documents into sentence-based chunks to prevent WebSocket drops
    and guarantee crystal-clear, unhurried articulation.
    """
    # Split by sentence terminators: . ! ? । or double newline
    sentence_delimiters = re.compile(r"([.!?।॥\n\n]+)")
    tokens = sentence_delimiters.split(text)

    chunks = []
    current_chunk = ""

    for i in range(0, len(tokens) - 1, 2):
        sentence = tokens[i].strip() + (tokens[i + 1] if i + 1 < len(tokens) else "")
        if not sentence.strip():
            continue

        if len(current_chunk) + len(sentence) < max_chunk_chars:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if len(tokens) % 2 == 1 and tokens[-1].strip():
        remainder = tokens[-1].strip()
        if len(current_chunk) + len(remainder) < max_chunk_chars:
            current_chunk += " " + remainder if current_chunk else remainder
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = remainder

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]

async def _synthesize_single_chunk_async(chunk_text, voice, rate_str):
    """
    Synthesizes a single chunk using Edge-TTS and returns bytes.
    """
    comm = edge_tts.Communicate(text=chunk_text, voice=voice, rate=rate_str)
    audio_stream = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_stream.extend(chunk["data"])
    return bytes(audio_stream)

def synthesize_speech(
    text,
    lang_code="auto",
    speed=1.0,
    voice_gender="Female",
    engine="edge-tts"
):
    """
    Unified speech synthesis pipeline:
    1. Sanitizes and NFC-normalizes text for clear pronunciation.
    2. Resolves voice to match the text's actual language.
    3. Splits text into manageable sentence chunks.
    4. Synthesizes each chunk and seamlessly concatenates audio.
    5. Automatic gTTS fallback if network issues arise.
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        raise ValueError("Cannot synthesize speech from empty or whitespace-only text.")

    # Determine language
    if lang_code == "auto" or lang_code not in VOICE_CATALOG:
        resolved_lang = detect_text_script_for_tts(cleaned_text)
    else:
        # Check if requested lang matches text script (e.g. if user selected English but text is pure Telugu)
        actual_script = detect_text_script_for_tts(cleaned_text)
        if actual_script in ["te", "kn", "hi"] and lang_code == "en":
            resolved_lang = actual_script
        else:
            resolved_lang = lang_code

    voice_info = VOICE_CATALOG.get(resolved_lang, VOICE_CATALOG["en"])
    is_male = (voice_gender.lower() == "male")
    selected_voice = voice_info["male"] if is_male else voice_info["female"]

    rate_str = format_rate_string(speed)

    # Hash key for disk caching
    cache_key = hashlib.md5(f"{cleaned_text}_{selected_voice}_{rate_str}_{engine}".encode("utf-8")).hexdigest()
    output_filename = f"speech_{resolved_lang}_{cache_key[:12]}.mp3"
    output_path = os.path.join(config.AUDIO_OUTPUT_DIR, output_filename)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        with open(output_path, "rb") as f:
            cached_bytes = f.read()
        return {
            "audio_bytes": cached_bytes,
            "file_path": output_path,
            "engine": f"{engine} (cached)",
            "voice": selected_voice,
            "speed": speed,
            "lang_code": resolved_lang,
            "cleaned_text": cleaned_text
        }

    actual_engine = engine

    if engine == "edge-tts":
        try:
            chunks = split_into_speech_chunks(cleaned_text, max_chunk_chars=350)
            all_audio = bytearray()

            async def _synthesize_all():
                for chunk in chunks:
                    chunk_bytes = await _synthesize_single_chunk_async(chunk, selected_voice, rate_str)
                    all_audio.extend(chunk_bytes)

            run_in_clean_loop(_synthesize_all())

            if len(all_audio) < 1000:
                raise RuntimeError("Edge-TTS generated empty audio stream.")

            with open(output_path, "wb") as f:
                f.write(all_audio)
            audio_bytes = bytes(all_audio)

        except Exception as edge_err:
            try:
                # Tier 2: Fallback to gTTS if edge-tts encounters an issue
                actual_engine = f"gTTS (fallback: {str(edge_err)[:25]})"
                gtts_lang = voice_info["gtts"]
                tts = gTTS(text=cleaned_text, lang=gtts_lang, slow=(speed < 0.85))
                tts.save(output_path)
                with open(output_path, "rb") as f:
                    audio_bytes = f.read()
                selected_voice = f"Google TTS ({gtts_lang})"
            except Exception as gtts_err:
                # Tier 3: 100% Offline Windows SAPI fallback (pyttsx3)
                import pyttsx3
                actual_engine = "pyttsx3 Offline Voice"
                output_wav = output_path.replace(".mp3", ".wav")
                engine_offline = pyttsx3.init()
                engine_offline.save_to_file(cleaned_text, output_wav)
                engine_offline.runAndWait()
                with open(output_wav, "rb") as f:
                    audio_bytes = f.read()
                output_path = output_wav
                selected_voice = "Windows SAPI5 Offline Voice"
    else:
        try:
            # gTTS selected by user
            gtts_lang = voice_info["gtts"]
            tts = gTTS(text=cleaned_text, lang=gtts_lang, slow=(speed < 0.85))
            tts.save(output_path)
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            selected_voice = f"Google TTS ({gtts_lang})"
        except Exception:
            import pyttsx3
            actual_engine = "pyttsx3 Offline Voice"
            output_wav = output_path.replace(".mp3", ".wav")
            engine_offline = pyttsx3.init()
            engine_offline.save_to_file(cleaned_text, output_wav)
            engine_offline.runAndWait()
            with open(output_wav, "rb") as f:
                audio_bytes = f.read()
            output_path = output_wav
            selected_voice = "Windows SAPI5 Offline Voice"

    return {
        "audio_bytes": audio_bytes,
        "file_path": output_path,
        "engine": actual_engine,
        "voice": selected_voice,
        "speed": speed,
        "lang_code": resolved_lang,
        "cleaned_text": cleaned_text
    }
