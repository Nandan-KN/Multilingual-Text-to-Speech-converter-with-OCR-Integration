"""
Multilingual Translation Module.
Translates extracted text between English, Telugu (తెలుగు), Kannada (ಕನ್ನಡ), and Hindi (हिंदी).
Dual-engine architecture:
- Primary: GoogleTranslator
- Resilient Fallback: MyMemoryTranslator
With sentence chunking and caching.
"""

import re
import unicodedata
from deep_translator import GoogleTranslator, MyMemoryTranslator

# Supported language codes mapping
LANG_MAP = {
    "en": {"code": "en", "mymemory": "en-GB", "name": "English"},
    "te": {"code": "te", "mymemory": "te-IN", "name": "Telugu"},
    "kn": {"code": "kn", "mymemory": "kn-IN", "name": "Kannada"},
    "hi": {"code": "hi", "mymemory": "hi-IN", "name": "Hindi"},
}

_TRANSLATION_CACHE = {}

def translate_text(text, target_lang="te", source_lang="auto"):
    """
    Translates text to the target language (te, kn, hi, en).
    """
    if not text or not text.strip():
        return text

    if target_lang == "auto" or target_lang not in LANG_MAP:
        return text

    # Check cache
    cache_key = (text.strip()[:100], source_lang, target_lang)
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    target_info = LANG_MAP[target_lang]
    target_code = target_info["code"]
    mymemory_target = target_info["mymemory"]

    # Split text into paragraphs to maintain structure
    paragraphs = text.split("\n\n")
    translated_paras = []

    for para in paragraphs:
        clean_para = para.strip()
        if not clean_para:
            continue

        # Try GoogleTranslator first
        try:
            gt = GoogleTranslator(source=source_lang, target=target_code)
            res = gt.translate(clean_para)
            if res and len(res.strip()) > 0:
                translated_paras.append(res)
                continue
        except Exception:
            pass

        # Fallback to MyMemoryTranslator
        try:
            # MyMemory max segment is 500 chars
            src_mymemory = "en-GB"
            chunks = re.split(r"([.!?।\n]+)", clean_para)
            translated_chunks = []
            
            curr = ""
            for token in chunks:
                if len(curr) + len(token) < 400:
                    curr += token
                else:
                    if curr.strip():
                        t_part = MyMemoryTranslator(source=src_mymemory, target=mymemory_target).translate(curr.strip())
                        translated_chunks.append(t_part)
                    curr = token
            if curr.strip():
                t_part = MyMemoryTranslator(source=src_mymemory, target=mymemory_target).translate(curr.strip())
                translated_chunks.append(t_part)

            res = " ".join(translated_chunks)
            translated_paras.append(res)
        except Exception as e:
            # If both fail, keep original paragraph
            translated_paras.append(clean_para)

    final_translated = "\n\n".join(translated_paras).strip()
    # Normalize Unicode NFC
    final_translated = unicodedata.normalize("NFC", final_translated)

    _TRANSLATION_CACHE[cache_key] = final_translated
    return final_translated
