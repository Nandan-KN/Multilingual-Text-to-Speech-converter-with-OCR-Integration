"""
Flashy Neon-Cyberpunk Multilingual Vision Voice Canvas
Built with Gradio 6.0+ featuring Glassmorphism, Neon Glow, and Multimodal Support.
Languages: English, Telugu (తెలుగు), Kannada (ಕನ್ನಡ), and Hindi (हिंदी).
"""

import os
import io
import time
import base64
import tempfile
import gradio as gr
from PIL import Image
import numpy as np

import config
from preprocessing import preprocess_for_ocr, load_as_cv2_image, check_image_health
from ocr_engine import extract_text_multilingual, detect_script_from_text
from tts_engine import synthesize_speech, clean_text_for_speech, detect_text_script_for_tts, VOICE_CATALOG
from document_loader import load_text_from_file, extract_from_pdf
from translator import translate_text, LANG_MAP

# ---------------------------------------------------------
# Cyberpunk Neon Glassmorphism Custom CSS
# ---------------------------------------------------------
CYBERPUNK_NEON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --neon-cyan: #00f2fe;
    --neon-purple: #9d4edd;
    --neon-pink: #ff007f;
    --neon-blue: #4facfe;
    --bg-dark: #070913;
    --card-bg: rgba(13, 17, 33, 0.75);
}

body, .gradio-container {
    background-color: var(--bg-dark) !important;
    background-image: 
        radial-gradient(circle at 15% 15%, rgba(79, 172, 254, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(255, 0, 127, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(157, 78, 221, 0.08) 0%, transparent 60%) !important;
    font-family: 'Plus Jakarta Sans', 'Nirmala UI', sans-serif !important;
    color: #e2e8f0 !important;
}

/* Flashy Hero Header */
.neon-hero {
    background: linear-gradient(135deg, rgba(13, 19, 43, 0.85) 0%, rgba(23, 14, 38, 0.85) 100%);
    border: 1px solid rgba(0, 242, 254, 0.35);
    border-radius: 20px;
    padding: 30px 40px;
    margin-bottom: 25px;
    box-shadow: 0 0 35px rgba(0, 242, 254, 0.15), inset 0 0 25px rgba(157, 78, 221, 0.1);
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}

.neon-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00f2fe, #ff007f, transparent);
    animation: scanline 3s linear infinite;
}

@keyframes scanline {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.neon-title {
    font-family: 'Orbitron', 'Plus Jakarta Sans', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: 1px;
    margin: 0;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 30%, #ff007f 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(0, 242, 254, 0.3);
}

.neon-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 10px;
    line-height: 1.6;
}

.neon-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 16px;
}

.neon-badge {
    background: rgba(0, 242, 254, 0.08);
    border: 1px solid rgba(0, 242, 254, 0.3);
    color: #00f2fe;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 9999px;
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.15);
}

/* Flashy Neon Buttons */
.neon-btn-primary button {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #7000ff 100%) !important;
    color: #050814 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.08rem !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 16px 30px !important;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
}

.neon-btn-primary button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 0 40px rgba(0, 242, 254, 0.7), 0 0 20px rgba(255, 0, 127, 0.5) !important;
}

.neon-btn-secondary button {
    background: rgba(157, 78, 221, 0.15) !important;
    border: 1px solid rgba(157, 78, 221, 0.5) !important;
    color: #c084fc !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}

.neon-btn-secondary button:hover {
    background: rgba(157, 78, 221, 0.3) !important;
    border-color: #ff007f !important;
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.3) !important;
}

/* Glassmorphism Cards */
.gradio-card, .block, .panel {
    background: var(--card-bg) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
}

.gradio-card:hover {
    border-color: rgba(0, 242, 254, 0.3) !important;
}

/* Tabs */
.tab-nav button {
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}

.tab-nav button.selected {
    color: #00f2fe !important;
    border-bottom: 2px solid #00f2fe !important;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.5) !important;
}

/* Textareas & Inputs */
textarea, input {
    background: rgba(7, 10, 22, 0.8) !important;
    border: 1px solid rgba(0, 242, 254, 0.2) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    font-family: 'Nirmala UI', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
}

textarea:focus, input:focus {
    border-color: #00f2fe !important;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.3) !important;
}

/* Audio Player */
audio {
    border-radius: 12px !important;
    filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.3)) !important;
}
"""

# ---------------------------------------------------------
# Core Processing Handlers
# ---------------------------------------------------------
def process_image_intake(
    image,
    target_lang,
    ocr_engine,
    auto_translate,
    denoise_level,
    auto_deskew,
    voice_profile,
    speed
):
    if image is None:
        return "", "", None, "⚠️ Please upload or capture an image first.", ""

    try:
        # Preprocessing
        proc_arr, proc_pil, _ = preprocess_for_ocr(
            image,
            denoise_strength=int(denoise_level),
            auto_deskew=auto_deskew
        )

        chosen_engine = "Tesseract-OCR" if "Tesseract" in ocr_engine else "EasyOCR"
        ocr_res = extract_text_multilingual(
            proc_arr,
            language_choice=target_lang,
            engine_choice=chosen_engine
        )
        raw_text = ocr_res["text"]
        src_code = ocr_res["detected_lang_code"]

        target_code = "te" if "Telugu" in target_lang else ("kn" if "Kannada" in target_lang else ("hi" if "Hindi" in target_lang else ("en" if "English" in target_lang else "auto")))
        
        final_text = raw_text
        speech_lang = target_code if target_code != "auto" else src_code

        if auto_translate and target_code != "auto" and target_code != src_code:
            final_text = translate_text(raw_text, target_lang=target_code, source_lang=src_code)
            speech_lang = target_code

        # Voice selection
        v_gender = "Male" if any(k in voice_profile for k in ["Mohan", "Gagan", "Madhur", "Prabhat"]) else "Female"
        if "Telugu" in voice_profile: speech_lang = "te"
        elif "Kannada" in voice_profile: speech_lang = "kn"
        elif "Hindi" in voice_profile: speech_lang = "hi"
        elif "English" in voice_profile: speech_lang = "en"

        audio_res = synthesize_speech(
            text=final_text,
            lang_code=speech_lang,
            speed=float(speed),
            voice_gender=v_gender,
            engine="edge-tts"
        )

        meta = f"🌐 Language: {target_lang} | Script: {ocr_res['detected_lang_name']} ({src_code}) | Engine: {chosen_engine} | Voice: {audio_res['voice']}"
        stats = f"📊 Characters: {len(final_text)} | Words: {len(final_text.split())}"

        return final_text, raw_text, audio_res["file_path"], meta, stats

    except Exception as e:
        return f"Error: {e}", "", None, f"❌ Failed: {e}", ""

def process_pdf_intake(
    pdf_file,
    target_lang,
    ocr_engine,
    auto_translate,
    voice_profile,
    speed
):
    if pdf_file is None:
        return "", "", None, "⚠️ Please upload a PDF file first.", ""

    try:
        with open(pdf_file.name, "rb") as f:
            pdf_bytes = f.read()

        chosen_engine = "Tesseract-OCR" if "Tesseract" in ocr_engine else "EasyOCR"
        pdf_res = extract_from_pdf(
            pdf_bytes,
            language_choice=target_lang,
            engine_choice=chosen_engine
        )
        raw_text = pdf_res["text"]
        src_code = pdf_res["detected_lang_code"]

        target_code = "te" if "Telugu" in target_lang else ("kn" if "Kannada" in target_lang else ("hi" if "Hindi" in target_lang else ("en" if "English" in target_lang else "auto")))
        
        final_text = raw_text
        speech_lang = target_code if target_code != "auto" else src_code

        if auto_translate and target_code != "auto" and target_code != src_code:
            final_text = translate_text(raw_text, target_lang=target_code, source_lang=src_code)
            speech_lang = target_code

        v_gender = "Male" if any(k in voice_profile for k in ["Mohan", "Gagan", "Madhur", "Prabhat"]) else "Female"
        if "Telugu" in voice_profile: speech_lang = "te"
        elif "Kannada" in voice_profile: speech_lang = "kn"
        elif "Hindi" in voice_profile: speech_lang = "hi"
        elif "English" in voice_profile: speech_lang = "en"

        audio_res = synthesize_speech(
            text=final_text,
            lang_code=speech_lang,
            speed=float(speed),
            voice_gender=v_gender,
            engine="edge-tts"
        )

        meta = f"📄 PDF Pages: {pdf_res['processed_pages']} | Target: {target_lang} | Script: {pdf_res['detected_lang_name']} | Voice: {audio_res['voice']}"
        stats = f"📊 Characters: {len(final_text)} | Words: {len(final_text.split())}"

        return final_text, raw_text, audio_res["file_path"], meta, stats

    except Exception as e:
        return f"Error: {e}", "", None, f"❌ Failed: {e}", ""

def process_text_intake(
    input_text,
    target_lang,
    auto_translate,
    voice_profile,
    speed
):
    if not input_text or not input_text.strip():
        return "", "", None, "⚠️ Please enter or upload some text first.", ""

    try:
        raw_text = input_text.strip()
        src_code = detect_text_script_for_tts(raw_text)
        target_code = "te" if "Telugu" in target_lang else ("kn" if "Kannada" in target_lang else ("hi" if "Hindi" in target_lang else ("en" if "English" in target_lang else "auto")))

        final_text = raw_text
        speech_lang = target_code if target_code != "auto" else src_code

        if auto_translate and target_code != "auto" and target_code != src_code:
            final_text = translate_text(raw_text, target_lang=target_code, source_lang=src_code)
            speech_lang = target_code

        v_gender = "Male" if any(k in voice_profile for k in ["Mohan", "Gagan", "Madhur", "Prabhat"]) else "Female"
        if "Telugu" in voice_profile: speech_lang = "te"
        elif "Kannada" in voice_profile: speech_lang = "kn"
        elif "Hindi" in voice_profile: speech_lang = "hi"
        elif "English" in voice_profile: speech_lang = "en"

        audio_res = synthesize_speech(
            text=final_text,
            lang_code=speech_lang,
            speed=float(speed),
            voice_gender=v_gender,
            engine="edge-tts"
        )

        meta = f"📝 Plain Text | Target: {target_lang} | Detected Script: {src_code.upper()} | Voice: {audio_res['voice']}"
        stats = f"📊 Characters: {len(final_text)} | Words: {len(final_text.split())}"

        return final_text, raw_text, audio_res["file_path"], meta, stats

    except Exception as e:
        return f"Error: {e}", "", None, f"❌ Failed: {e}", ""

def quick_translate_handler(current_text, raw_text, target_choice):
    if not current_text or not current_text.strip():
        return current_text, "No text to translate."
    t_code = "te" if "Telugu" in target_choice else ("kn" if "Kannada" in target_choice else ("hi" if "Hindi" in target_choice else "en"))
    base = raw_text if raw_text.strip() else current_text
    translated = translate_text(base, target_lang=t_code)
    return translated, f"✅ Translated to {target_choice}!"

def re_synthesize_handler(text, voice_profile, speed):
    if not text or not text.strip():
        return None, "⚠️ Text is empty."
    try:
        v_gender = "Male" if any(k in voice_profile for k in ["Mohan", "Gagan", "Madhur", "Prabhat"]) else "Female"
        speech_lang = "auto"
        if "Telugu" in voice_profile: speech_lang = "te"
        elif "Kannada" in voice_profile: speech_lang = "kn"
        elif "Hindi" in voice_profile: speech_lang = "hi"
        elif "English" in voice_profile: speech_lang = "en"
        else: speech_lang = detect_text_script_for_tts(text)

        audio_res = synthesize_speech(
            text=text,
            lang_code=speech_lang,
            speed=float(speed),
            voice_gender=v_gender,
            engine="edge-tts"
        )
        return audio_res["file_path"], f"✅ Synthesized with {audio_res['voice']} ({speed}x)"
    except Exception as e:
        return None, f"❌ Speech error: {e}"

def load_sample_image(sample_name):
    s_map = {
        "English Sample Card": "sample_english.png",
        "Telugu (తెలుగు) Sample Card": "sample_telugu.png",
        "Kannada (ಕನ್ನಡ) Sample Card": "sample_kannada.png",
        "Hindi (हिंदी) Sample Card": "sample_hindi.png",
        "Multilingual Mixed Card": "sample_multilingual.png"
    }
    fn = s_map.get(sample_name, "sample_english.png")
    p = os.path.join(config.SAMPLE_DIR, fn)
    if os.path.exists(p):
        return Image.open(p)
    return None

def load_sample_text(sample_name):
    s_docs = os.path.join(config.BASE_DIR, "sample_documents")
    t_map = {
        "English Sample": "sample_english.txt",
        "Telugu (తెలుగు) Sample": "sample_telugu.txt",
        "Kannada (ಕನ್ನಡ) Sample": "sample_kannada.txt",
        "Hindi (हिंदी) Sample": "sample_hindi.txt"
    }
    fn = t_map.get(sample_name, "sample_english.txt")
    p = os.path.join(s_docs, fn)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_sample_pdf(sample_name):
    s_docs = os.path.join(config.BASE_DIR, "sample_documents")
    p_map = {
        "English Sample PDF": "sample_english.pdf",
        "Telugu (తెలుగు) Sample PDF": "sample_telugu.pdf",
        "Kannada (ಕನ್ನಡ) Sample PDF": "sample_kannada.pdf",
        "Hindi (हिंदी) Sample PDF": "sample_hindi.pdf"
    }
    fn = p_map.get(sample_name, "sample_english.pdf")
    p = os.path.join(s_docs, fn)
    if os.path.exists(p):
        return p
    return None

# ---------------------------------------------------------
# Build Gradio Blocks Application
# ---------------------------------------------------------
with gr.Blocks(title="Multilingual Vision Voice Canvas") as demo:
    # Flashy Hero Banner
    gr.HTML("""
    <div class="neon-hero">
        <h1 class="neon-title">⚡ MULTILINGUAL VISION VOICE CANVAS</h1>
        <p class="neon-subtitle">
            Next-Gen Multimodal Studio &bull; Optical Character Recognition &bull; Neural Translation &bull; High-Clarity Speech Synthesis
        </p>
        <div class="neon-badges">
            <span class="neon-badge">🇬🇧 ENGLISH</span>
            <span class="neon-badge">🇮🇳 తెలుగు (TELUGU)</span>
            <span class="neon-badge">🇮🇳 ಕನ್ನಡ (KANNADA)</span>
            <span class="neon-badge">🇮🇳 हिंदी (HINDI)</span>
            <span class="neon-badge" style="border-color: #ff007f; color: #ff007f;">✨ NEURAL VOICES</span>
            <span class="neon-badge" style="border-color: #9d4edd; color: #c084fc;">🚀 GPU ACCELERATED</span>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        # =====================================================
        # LEFT COLUMN: Flashy Input Studio
        # =====================================================
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Multimodal Input Terminal")

            with gr.Tabs():
                # Tab 1: Image Studio
                with gr.TabItem("🖼️ Image Studio"):
                    image_input = gr.Image(type="pil", label="Drop Image or Capture Webcam", sources=["upload", "webcam", "clipboard"])
                    sample_img_dropdown = gr.Dropdown(
                        label="⚡ Quick Load Sample Image Card",
                        choices=[
                            "English Sample Card",
                            "Telugu (తెలుగు) Sample Card",
                            "Kannada (ಕನ್ನಡ) Sample Card",
                            "Hindi (हिंदी) Sample Card",
                            "Multilingual Mixed Card"
                        ],
                        value="Telugu (తెలుగు) Sample Card"
                    )
                    load_img_btn = gr.Button("Load Sample Card", elem_classes=["neon-btn-secondary"], size="sm")

                    with gr.Accordion("⚙️ OpenCV Preprocessing Filters", open=False):
                        denoise_slider = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Bilateral Denoising Intensity")
                        deskew_chk = gr.Checkbox(value=True, label="Auto-Deskew Document Skew")

                # Tab 2: PDF Studio
                with gr.TabItem("📄 PDF Studio"):
                    pdf_input = gr.File(label="Upload PDF Document", file_types=[".pdf"], type="filepath")
                    sample_pdf_dropdown = gr.Dropdown(
                        label="⚡ Quick Load Sample PDF",
                        choices=["Telugu (తెలుగు) Sample PDF", "Kannada (ಕನ್ನಡ) Sample PDF", "Hindi (हिंदी) Sample PDF", "English Sample PDF"],
                        value="Telugu (తెలుగు) Sample PDF"
                    )
                    load_pdf_btn = gr.Button("Load Sample PDF", elem_classes=["neon-btn-secondary"], size="sm")

                # Tab 3: Text Studio
                with gr.TabItem("📝 Plain Text Studio"):
                    text_input = gr.Textbox(lines=6, placeholder="Paste or type text in any language here...", label="Direct Text Input")
                    sample_txt_dropdown = gr.Dropdown(
                        label="⚡ Quick Load Sample Text",
                        choices=["Telugu (తెలుగు) Sample", "Kannada (ಕನ್ನಡ) Sample", "Hindi (हिंदी) Sample", "English Sample"],
                        value="Telugu (తెలుగు) Sample"
                    )
                    load_txt_btn = gr.Button("Load Sample Text", elem_classes=["neon-btn-secondary"], size="sm")

            gr.Markdown("---")
            gr.Markdown("#### 🌐 Target Language & Engine Controls")

            with gr.Row():
                target_lang_select = gr.Dropdown(
                    label="Target Output Language",
                    choices=["Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "English", "Auto-Detect"],
                    value="Telugu (తెలుగు)"
                )
                ocr_engine_select = gr.Dropdown(
                    label="OCR Engine",
                    choices=["Tesseract-OCR (Indic Models)", "EasyOCR (Deep Learning)"],
                    value="Tesseract-OCR (Indic Models)"
                )

            auto_translate_chk = gr.Checkbox(
                value=True,
                label="🌐 Auto-Translate output to selected language (if document is in another language)"
            )

            with gr.Accordion("🎚️ Voice Profile & Tempo", open=False):
                voice_select = gr.Dropdown(
                    label="Neural Voice Profile",
                    choices=[
                        "Auto-Match Text Script (Recommended)",
                        "👩 Telugu (Shruti - Female)",
                        "👨 Telugu (Mohan - Male)",
                        "👩 Kannada (Sapna - Female)",
                        "👨 Kannada (Gagan - Male)",
                        "👩 Hindi (Swara - Female)",
                        "👨 Hindi (Madhur - Male)",
                        "👩 English (Neerja - Indian English)",
                        "👨 English (Prabhat - Indian English)"
                    ],
                    value="👩 Telugu (Shruti - Female)"
                )
                speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="Speech Rate / Speed")

            # Main Action Buttons for each modality
            extract_img_btn = gr.Button("🚀 EXTRACT & SYNTHESIZE IMAGE", elem_classes=["neon-btn-primary"])
            extract_pdf_btn = gr.Button("🚀 EXTRACT & SYNTHESIZE PDF", elem_classes=["neon-btn-primary"])
            extract_txt_btn = gr.Button("🚀 SYNTHESIZE PLAIN TEXT", elem_classes=["neon-btn-primary"])

        # =====================================================
        # RIGHT COLUMN: Flashy Output Console
        # =====================================================
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Holographic Output & Audio Console")

            status_banner = gr.Markdown("🟢 System Ready &bull; Waiting for Document Intake")
            stats_banner = gr.Markdown("📊 Characters: 0 | Words: 0")

            # Quick Translation Ribbon
            gr.Markdown("##### ⚡ Quick Language Transformer:")
            with gr.Row():
                q_te = gr.Button("🇮🇳 తెలుగు", elem_classes=["neon-btn-secondary"], size="sm")
                q_kn = gr.Button("🇮🇳 ಕನ್ನಡ", elem_classes=["neon-btn-secondary"], size="sm")
                q_hi = gr.Button("🇮🇳 हिंदी", elem_classes=["neon-btn-secondary"], size="sm")
                q_en = gr.Button("🇬🇧 English", elem_classes=["neon-btn-secondary"], size="sm")

            # Editable Text Area
            output_text = gr.Textbox(
                lines=10,
                label="📝 Active Document Content in Selected Language (Editable)",
                placeholder="Extracted and translated text will appear here..."
            )

            # Hidden Raw Text Cache for restoring original
            raw_text_cache = gr.Textbox(visible=False)

            with gr.Accordion("📄 View Raw Un-translated OCR Output", open=False):
                raw_text_display = gr.Textbox(lines=5, label="Original Extracted Raw Text", interactive=False)
                restore_btn = gr.Button("Restore Raw Text to Active Editor", size="sm")

            # Flashy Audio Console
            gr.HTML("""
            <div style="margin-top: 14px; margin-bottom: 6px; font-weight: 700; color: #00f2fe; display: flex; align-items: center; gap: 8px;">
                <span>🔊 HIGH-CLARITY NEURAL AUDIO PLAYER</span>
            </div>
            """)
            audio_output = gr.Audio(label="Neural Audio Output", type="filepath", autoplay=True)

            with gr.Row():
                re_synth_btn = gr.Button("🔄 Re-Synthesize Current Editor Text", elem_classes=["neon-btn-secondary"])

    # -----------------------------------------------------
    # Event Bindings
    # -----------------------------------------------------
    # Sample Loaders
    load_img_btn.click(load_sample_image, inputs=[sample_img_dropdown], outputs=[image_input])
    load_pdf_btn.click(load_sample_pdf, inputs=[sample_pdf_dropdown], outputs=[pdf_input])
    load_txt_btn.click(load_sample_text, inputs=[sample_txt_dropdown], outputs=[text_input])

    # Target language auto-syncs voice dropdown
    def sync_voice_dropdown(target_lang):
        if "Telugu" in target_lang: return "👩 Telugu (Shruti - Female)"
        elif "Kannada" in target_lang: return "👩 Kannada (Sapna - Female)"
        elif "Hindi" in target_lang: return "👩 Hindi (Swara - Female)"
        elif "English" in target_lang: return "👩 English (Neerja - Indian English)"
        return "Auto-Match Text Script (Recommended)"

    target_lang_select.change(sync_voice_dropdown, inputs=[target_lang_select], outputs=[voice_select])

    # Main Pipelines
    extract_img_btn.click(
        process_image_intake,
        inputs=[image_input, target_lang_select, ocr_engine_select, auto_translate_chk, denoise_slider, deskew_chk, voice_select, speed_slider],
        outputs=[output_text, raw_text_cache, audio_output, status_banner, stats_banner]
    ).then(lambda raw: raw, inputs=[raw_text_cache], outputs=[raw_text_display])

    extract_pdf_btn.click(
        process_pdf_intake,
        inputs=[pdf_input, target_lang_select, ocr_engine_select, auto_translate_chk, voice_select, speed_slider],
        outputs=[output_text, raw_text_cache, audio_output, status_banner, stats_banner]
    ).then(lambda raw: raw, inputs=[raw_text_cache], outputs=[raw_text_display])

    extract_txt_btn.click(
        process_text_intake,
        inputs=[text_input, target_lang_select, auto_translate_chk, voice_select, speed_slider],
        outputs=[output_text, raw_text_cache, audio_output, status_banner, stats_banner]
    ).then(lambda raw: raw, inputs=[raw_text_cache], outputs=[raw_text_display])

    # Quick Translation Buttons
    q_te.click(lambda curr, raw: quick_translate_handler(curr, raw, "Telugu (తెలుగు)"), inputs=[output_text, raw_text_cache], outputs=[output_text, status_banner])
    q_kn.click(lambda curr, raw: quick_translate_handler(curr, raw, "Kannada (ಕನ್ನಡ)"), inputs=[output_text, raw_text_cache], outputs=[output_text, status_banner])
    q_hi.click(lambda curr, raw: quick_translate_handler(curr, raw, "Hindi (हिंदी)"), inputs=[output_text, raw_text_cache], outputs=[output_text, status_banner])
    q_en.click(lambda curr, raw: quick_translate_handler(curr, raw, "English"), inputs=[output_text, raw_text_cache], outputs=[output_text, status_banner])

    # Restore raw text
    restore_btn.click(lambda raw: raw, inputs=[raw_text_cache], outputs=[output_text])

    # Re-synthesis
    re_synth_btn.click(
        re_synthesize_handler,
        inputs=[output_text, voice_select, speed_slider],
        outputs=[audio_output, status_banner]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        css=CYBERPUNK_NEON_CSS
    )
