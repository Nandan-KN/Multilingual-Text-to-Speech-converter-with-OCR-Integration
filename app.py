"""
Multilingual Vision Voice Canvas
World-Class Multimodal Studio for OCR, Translation & Text-to-Speech (TTS)
Languages: English, Telugu (తెలుగు), Kannada (ಕನ್ನಡ), and Hindi (हिंदी).
"""

import os
import base64
import time
import io
import streamlit as st
from PIL import Image
import numpy as np

import config
from preprocessing import preprocess_for_ocr, load_as_cv2_image, check_image_health
from ocr_engine import extract_text_multilingual, detect_script_from_text
from tts_engine import synthesize_speech, clean_text_for_speech, detect_text_script_for_tts, VOICE_CATALOG
from document_loader import load_text_from_file, extract_from_pdf
from translator import translate_text, LANG_MAP

# ---------------------------------------------------------
# Page Config & Glassmorphism Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Multilingual Vision Voice Canvas",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# World-Class CSS: Modern Glassmorphism, Micro-interactions, Waveform Animation
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Nirmala UI', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Hero Banner */
    .hero-banner {
        background: radial-gradient(circle at 10% 20%, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.98) 90%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.4), 0 0 20px rgba(56, 189, 248, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0) 70%);
        pointer-events: none;
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        margin: 0;
        background: linear-gradient(120deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #CBD5E1;
        margin-top: 8px;
        margin-bottom: 0;
        line-height: 1.6;
        max-width: 900px;
    }

    .lang-pills-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }

    .lang-pill {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #F1F5F9;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Workflow Pipeline Stepper */
    .pipeline-stepper {
        display: flex;
        justify-content: space-between;
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 24px;
        gap: 10px;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 600;
        color: gray;
    }

    .step-item.active {
        color: #38BDF8;
    }

    .step-number {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(128, 128, 128, 0.2);
        color: inherit;
    }

    .step-item.active .step-number {
        background: linear-gradient(135deg, #0284C7, #4F46E5);
        color: white;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }

    /* Studio Card */
    .studio-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .studio-card:hover {
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
    }

    .card-header-title {
        font-size: 1.18rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-primary { background: #0284C7; color: white; }
    .badge-success { background: #059669; color: white; }
    .badge-purple { background: #7C3AED; color: white; }
    .badge-neutral {
        background: rgba(128, 128, 128, 0.14);
        color: inherit;
        border: 1px solid rgba(128, 128, 128, 0.22);
    }

    /* Primary Action Button */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.55rem 1.4rem;
        transition: all 0.2s ease;
    }
    
    .primary-btn > button {
        background: linear-gradient(135deg, #0284C7 0%, #4F46E5 50%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        font-size: 1.08rem !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.35) !important;
    }
    .primary-btn > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(79, 70, 229, 0.5) !important;
    }

    /* Text Area Styling */
    textarea {
        font-family: 'Nirmala UI', 'Segoe UI', -apple-system, sans-serif !important;
        font-size: 1.08rem !important;
        line-height: 1.68 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(128, 128, 128, 0.25) !important;
        padding: 14px !important;
    }

    /* Modern Waveform Audio Player Box */
    .audio-player-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.05) 0%, rgba(30, 41, 59, 0.08) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 22px;
        margin-top: 14px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.08);
    }

    /* CSS Animated Audio Waveform */
    .waveform-visualizer {
        display: flex;
        align-items: center;
        gap: 4px;
        height: 28px;
        margin-bottom: 14px;
    }

    .wave-bar {
        width: 4px;
        height: 8px;
        background: #38BDF8;
        border-radius: 4px;
        animation: wavePulse 1.2s ease-in-out infinite;
    }
    .wave-bar:nth-child(2) { animation-delay: 0.15s; background: #60A5FA; height: 16px; }
    .wave-bar:nth-child(3) { animation-delay: 0.3s; background: #818CF8; height: 24px; }
    .wave-bar:nth-child(4) { animation-delay: 0.45s; background: #A78BFA; height: 14px; }
    .wave-bar:nth-child(5) { animation-delay: 0.6s; background: #C084FC; height: 22px; }
    .wave-bar:nth-child(6) { animation-delay: 0.75s; background: #818CF8; height: 18px; }
    .wave-bar:nth-child(7) { animation-delay: 0.9s; background: #60A5FA; height: 10px; }

    @keyframes wavePulse {
        0%, 100% { transform: scaleY(0.4); opacity: 0.5; }
        50% { transform: scaleY(1.1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "Image (OCR)"
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_doc_name" not in st.session_state:
    st.session_state.current_doc_name = "None"
if "original_extracted_text" not in st.session_state:
    st.session_state.original_extracted_text = ""
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "pdf_result" not in st.session_state:
    st.session_state.pdf_result = None
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "active_language" not in st.session_state:
    st.session_state.active_language = "English"
if "pipeline_step" not in st.session_state:
    st.session_state.pipeline_step = 1

# ---------------------------------------------------------
# Premium Hero Header
# ---------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div>
            <h1 class="hero-title">🎙️ Multilingual Vision Voice Canvas</h1>
            <p class="hero-subtitle">
                The all-in-one multimodal studio that reads <b>Text</b>, <b>Images</b>, and <b>PDFs</b>, translates seamlessly, 
                and synthesizes high-clarity speech in natural Indian neural accents.
            </p>
            <div class="lang-pills-bar">
                <span class="lang-pill">🇬🇧 English</span>
                <span class="lang-pill">🇮🇳 తెలుగు (Telugu)</span>
                <span class="lang-pill">🇮🇳 ಕನ್ನಡ (Kannada)</span>
                <span class="lang-pill">🇮🇳 हिंदी (Hindi)</span>
                <span class="lang-pill" style="border-color: rgba(56, 189, 248, 0.4); color: #38BDF8;">✨ Multi-Script & Auto-Detect</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Interactive 4-Stage Pipeline Stepper
# ---------------------------------------------------------
p_step = st.session_state.pipeline_step
st.markdown(f"""
<div class="pipeline-stepper">
    <div class="step-item {'active' if p_step >= 1 else ''}">
        <span class="step-number">1</span>
        <span>Document Intake</span>
    </div>
    <span style="color: gray;">&rarr;</span>
    <div class="step-item {'active' if p_step >= 2 else ''}">
        <span class="step-number">2</span>
        <span>Vision OCR & Cleaning</span>
    </div>
    <span style="color: gray;">&rarr;</span>
    <div class="step-item {'active' if p_step >= 3 else ''}">
        <span class="step-number">3</span>
        <span>Language Translation</span>
    </div>
    <span style="color: gray;">&rarr;</span>
    <div class="step-item {'active' if p_step >= 4 else ''}">
        <span class="step-number">4</span>
        <span>Neural Voice Synthesis</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Studio Layout
# ---------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="large")

# =========================================================
# LEFT COLUMN: Multimodal Intake & Configuration Studio
# =========================================================
with col_left:
    st.markdown("### 📥 Multimodal Intake Studio")

    intake_selection = st.radio(
        "Select Document Modality:",
        ["🖼️ Image Studio", "📄 PDF Document Studio", "📝 Plain Text Studio", "✨ Instant Sample Gallery"],
        horizontal=True,
        key="intake_selector"
    )

    # 1. IMAGE STUDIO
    if "Image Studio" in intake_selection:
        st.session_state.input_mode = "Image"
        img_tab1, img_tab2 = st.tabs(["📁 File Uploader", "📷 Live Webcam Capture"])

        with img_tab1:
            img_file = st.file_uploader(
                "Upload Document Image (Drag & Drop Supported)",
                type=["png", "jpg", "jpeg", "webp", "bmp"],
                key="img_file_uploader",
                help="High-contrast PNG, JPG, or JPEG images work best."
            )
            if img_file is not None:
                st.session_state.current_image = Image.open(img_file)
                st.session_state.current_doc_name = img_file.name
                st.session_state.pipeline_step = 2

        with img_tab2:
            cam_shot = st.camera_input("Take Live Document Snapshot")
            if cam_shot is not None:
                st.session_state.current_image = Image.open(cam_shot)
                st.session_state.current_doc_name = "Camera_Capture.png"
                st.session_state.pipeline_step = 2

        if st.session_state.current_image is not None and st.session_state.input_mode == "Image":
            st.image(
                st.session_state.current_image,
                caption=f"📷 Active Image: {st.session_state.current_doc_name}",
                use_container_width=True
            )

        with st.expander("⚙️ Advanced Image Preprocessing Settings", expanded=False):
            preprocess_mode = st.selectbox(
                "Filter Mode",
                config.PREPROCESSING_MODES,
                index=0,
                help="Adaptive Gaussian preserves delicate Indic conjuncts and vowels."
            )
            denoise_level = st.slider("Bilateral Denoise Level", 1, 10, 5)
            auto_deskew = st.checkbox("Auto-Deskew Document Tilt", value=True)
            show_proc_preview = st.checkbox("Show Filtered Image Preview", value=False)

            if show_proc_preview and st.session_state.current_image is not None:
                try:
                    proc_arr, proc_pil, meta = preprocess_for_ocr(
                        st.session_state.current_image,
                        mode=preprocess_mode,
                        denoise_strength=denoise_level,
                        auto_deskew=auto_deskew
                    )
                    st.image(proc_pil, caption="Enhanced Filtered Image", use_container_width=True)
                except Exception as e:
                    st.warning(f"Preview warning: {e}")

    # 2. PDF STUDIO
    elif "PDF" in intake_selection:
        st.session_state.input_mode = "PDF"
        pdf_file = st.file_uploader(
            "Upload Multi-Page PDF Document (.pdf)",
            type=["pdf"],
            key="pdf_file_uploader",
            help="Extracts digital text instantly; automatically applies OCR on scanned pages."
        )
        if pdf_file is not None:
            st.session_state.pdf_bytes = pdf_file.read()
            st.session_state.current_doc_name = pdf_file.name
            st.session_state.pipeline_step = 2
            st.info(f"📄 Active PDF: `{pdf_file.name}` ({len(st.session_state.pdf_bytes) // 1024} KB)")

    # 3. TEXT STUDIO
    elif "Plain Text" in intake_selection:
        st.session_state.input_mode = "Text"
        text_tab1, text_tab2 = st.tabs(["✍️ Type / Paste Text", "📁 Upload .txt File"])

        with text_tab1:
            direct_text = st.text_area(
                "Type or paste text in any language:",
                height=180,
                placeholder="Type in English, Telugu, Kannada, or Hindi...",
                key="direct_text_area"
            )
            if st.button("Set Text for Processing", use_container_width=True):
                if direct_text.strip():
                    st.session_state.original_extracted_text = direct_text.strip()
                    st.session_state.extracted_text = direct_text.strip()
                    st.session_state.current_doc_name = "User_Direct_Text"
                    st.session_state.pipeline_step = 2
                    st.success("✅ Text loaded into editor!")
                else:
                    st.warning("Please type or paste some text first.")

        with text_tab2:
            txt_file = st.file_uploader("Upload Text Document (.txt)", type=["txt"])
            if txt_file is not None:
                txt_content, enc = load_text_from_file(txt_file.read(), txt_file.name)
                st.session_state.original_extracted_text = txt_content
                st.session_state.extracted_text = txt_content
                st.session_state.current_doc_name = txt_file.name
                st.session_state.pipeline_step = 2
                st.success(f"Loaded `{txt_file.name}` ({enc})!")

    # 4. SAMPLE GALLERY
    else:
        st.caption("Choose any pre-loaded high-resolution document for an instant 1-click test:")
        sample_category = st.selectbox("Category:", ["Image Cards", "PDF Documents", "Text Files"])

        if sample_category == "Image Cards":
            st.session_state.input_mode = "Image"
            s_map = {
                "English Sample Card": "sample_english.png",
                "Telugu (తెలుగు) Sample Card": "sample_telugu.png",
                "Kannada (ಕನ್ನಡ) Sample Card": "sample_kannada.png",
                "Hindi (हिंदी) Sample Card": "sample_hindi.png",
                "Multilingual Mixed Card": "sample_multilingual.png"
            }
            s_choice = st.selectbox("Choose Card:", list(s_map.keys()))
            if st.button("Load Image Card", use_container_width=True):
                p = os.path.join(config.SAMPLE_DIR, s_map[s_choice])
                if os.path.exists(p):
                    st.session_state.current_image = Image.open(p)
                    st.session_state.current_doc_name = s_map[s_choice]
                    st.session_state.pipeline_step = 2
                    st.success(f"Loaded {s_choice}!")

        elif sample_category == "PDF Documents":
            st.session_state.input_mode = "PDF"
            s_docs = os.path.join(config.BASE_DIR, "sample_documents")
            p_map = {
                "English Sample PDF": "sample_english.pdf",
                "Telugu (తెలుగు) Sample PDF": "sample_telugu.pdf",
                "Kannada (ಕನ್ನಡ) Sample PDF": "sample_kannada.pdf",
                "Hindi (हिंदी) Sample PDF": "sample_hindi.pdf"
            }
            p_choice = st.selectbox("Choose PDF:", list(p_map.keys()))
            if st.button("Load PDF Document", use_container_width=True):
                p = os.path.join(s_docs, p_map[p_choice])
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        st.session_state.pdf_bytes = f.read()
                    st.session_state.current_doc_name = p_map[p_choice]
                    st.session_state.pipeline_step = 2
                    st.success(f"Loaded {p_choice}!")

        else:
            st.session_state.input_mode = "Text"
            s_docs = os.path.join(config.BASE_DIR, "sample_documents")
            t_map = {
                "English Sample Text": "sample_english.txt",
                "Telugu (తెలుగు) Sample Text": "sample_telugu.txt",
                "Kannada (ಕನ್ನಡ) Sample Text": "sample_kannada.txt",
                "Hindi (हिंदी) Sample Text": "sample_hindi.txt"
            }
            t_choice = st.selectbox("Choose Text:", list(t_map.keys()))
            if st.button("Load Text File", use_container_width=True):
                p = os.path.join(s_docs, t_map[t_choice])
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        c = f.read()
                        st.session_state.original_extracted_text = c
                        st.session_state.extracted_text = c
                    st.session_state.current_doc_name = t_map[t_choice]
                    st.session_state.pipeline_step = 2
                    st.success(f"Loaded {t_choice}!")

    # -----------------------------------------------------
    # Target Language & Engine Configuration Card
    # -----------------------------------------------------
    st.markdown("---")
    st.markdown("#### 🌐 Target Language & Translation")

    c_lang, c_engine = st.columns([1, 1])
    with c_lang:
        language_choice = st.selectbox(
            "Target Output Language:",
            ["English", "Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "Auto-Detect"],
            index=0,
            help="Select the language in which you want to receive your text and speech."
        )
        st.session_state.active_language = language_choice

    with c_engine:
        ocr_engine_choice = st.selectbox(
            "OCR Engine:",
            ["Tesseract-OCR (Fast & Accurate)", "EasyOCR (Deep Learning)"],
            index=0,
            help="Tesseract is tuned with native Indic models."
        )

    auto_translate_to_target = st.checkbox(
        "🌐 Auto-Translate output to selected language (if document is in another language)",
        value=True,
        help="Ensures you always get the output in your selected language, even if the source is English."
    )

    # Main Hero Action Button
    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    extract_action = st.button(
        "🚀 Extract Content & Generate Voice",
        use_container_width=True,
        type="primary"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Execution Pipeline
    # -----------------------------------------------------
    if extract_action:
        try:
            target_lang_code = "en"
            if "Telugu" in language_choice: target_lang_code = "te"
            elif "Kannada" in language_choice: target_lang_code = "kn"
            elif "Hindi" in language_choice: target_lang_code = "hi"
            elif "English" in language_choice: target_lang_code = "en"
            else: target_lang_code = "auto"

            raw_text = ""
            detected_src_code = "en"

            # 1. Processing Image
            if st.session_state.input_mode == "Image":
                if st.session_state.current_image is None:
                    st.error("⚠️ Please upload an image, capture via webcam, or pick a sample card first.")
                else:
                    with st.spinner("🔍 Step 1/4: Enhancing image contrast & removing noise..."):
                        img_bgr = load_as_cv2_image(st.session_state.current_image)
                        is_healthy, health_msg, _ = check_image_health(img_bgr)
                        if not is_healthy: raise ValueError(health_msg)
                        proc_arr, proc_pil, _ = preprocess_for_ocr(img_bgr)

                    with st.spinner("📖 Step 2/4: Performing multilingual OCR extraction..."):
                        chosen_engine = "Tesseract-OCR" if "Tesseract" in ocr_engine_choice else "EasyOCR"
                        ocr_res = extract_text_multilingual(
                            proc_arr,
                            language_choice=language_choice,
                            engine_choice=chosen_engine
                        )
                        st.session_state.ocr_result = ocr_res
                        raw_text = ocr_res["text"]
                        detected_src_code = ocr_res["detected_lang_code"]

            # 2. Processing PDF
            elif st.session_state.input_mode == "PDF":
                if "pdf_bytes" not in st.session_state or not st.session_state.pdf_bytes:
                    st.error("⚠️ Please upload a PDF file or choose a sample PDF first.")
                else:
                    with st.spinner("📄 Step 1/3: Extracting text & scanning PDF pages..."):
                        chosen_engine = "Tesseract-OCR" if "Tesseract" in ocr_engine_choice else "EasyOCR"
                        pdf_res = extract_from_pdf(
                            st.session_state.pdf_bytes,
                            language_choice=language_choice,
                            engine_choice=chosen_engine
                        )
                        st.session_state.pdf_result = pdf_res
                        raw_text = pdf_res["text"]
                        detected_src_code = pdf_res["detected_lang_code"]

            # 3. Processing Plain Text
            else:
                if not st.session_state.extracted_text.strip():
                    st.error("⚠️ Please enter or upload some text first.")
                else:
                    raw_text = st.session_state.extracted_text.strip()
                    detected_src_code = detect_text_script_for_tts(raw_text)

            if raw_text.strip():
                st.session_state.original_extracted_text = raw_text.strip()
                final_text = raw_text.strip()
                final_speech_lang = target_lang_code if target_lang_code != "auto" else detected_src_code

                # Translation
                if auto_translate_to_target and target_lang_code != "auto" and target_lang_code != detected_src_code:
                    with st.spinner(f"🌐 Step 3/4: Translating content to {language_choice}..."):
                        final_text = translate_text(raw_text, target_lang=target_lang_code, source_lang=detected_src_code)
                        final_speech_lang = target_lang_code

                st.session_state.extracted_text = final_text
                st.session_state.pipeline_step = 3

                # Speech Synthesis
                with st.spinner(f"🎙️ Step 4/4: Synthesizing articulate {language_choice} speech..."):
                    audio_res = synthesize_speech(
                        text=st.session_state.extracted_text,
                        lang_code=final_speech_lang,
                        speed=1.0,
                        voice_gender="Female",
                        engine="edge-tts"
                    )
                    st.session_state.audio_data = audio_res
                    st.session_state.pipeline_step = 4

                st.toast(f"✅ Generated output in {language_choice}!", icon="🎉")
                st.success(f"✅ Content extracted & synthesized in **{language_choice}**!")

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =========================================================
# RIGHT COLUMN: Studio Output Canvas & Audio Console
# =========================================================
with col_right:
    st.markdown("### 📤 Studio Output & Clear Speech Console")

    # Document Metrics & Badges Bar
    if st.session_state.extracted_text.strip():
        det_code, det_name, dist = detect_script_from_text(st.session_state.extracted_text)
        doc_src = st.session_state.current_doc_name or "Document"
        w_count = len(st.session_state.extracted_text.split())
        est_time = max(1, round(w_count / 2.5)) # roughly 150 wpm

        st.markdown(f"""
        <div style="margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">
            <span class="badge badge-primary">🌐 Output: {st.session_state.active_language}</span>
            <span class="badge badge-purple">📝 Script: {det_name}</span>
            <span class="badge badge-neutral">📄 Source: {doc_src}</span>
            <span class="badge badge-neutral">⏱️ ~{est_time}s listen</span>
        </div>
        """, unsafe_allow_html=True)

    # Quick Translation Ribbon
    st.markdown("##### ⚡ Quick Language Switcher:")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_langs = [
        ("🇬🇧 English", "en", q_col1),
        ("🇮🇳 తెలుగు", "te", q_col2),
        ("🇮🇳 ಕನ್ನಡ", "kn", q_col3),
        ("🇮🇳 हिंदी", "hi", q_col4)
    ]

    for label, code, col in quick_langs:
        with col:
            if st.button(label, use_container_width=True, key=f"qbtn_{code}"):
                if st.session_state.extracted_text.strip():
                    with st.spinner(f"Translating to {label}..."):
                        base = st.session_state.original_extracted_text or st.session_state.extracted_text
                        translated = translate_text(base, target_lang=code)
                        st.session_state.extracted_text = translated
                        st.session_state.active_language = label.split()[1]
                        st.rerun()

    # Tabbed Text Editor View
    tab_editor, tab_original, tab_insights = st.tabs([
        "📝 Editable Output Text",
        "📄 Original Extracted Content",
        "📊 Script Composition"
    ])

    with tab_editor:
        user_edited_text = st.text_area(
            label="Editable Text (Speech will articulate this exact content):",
            value=st.session_state.extracted_text,
            height=220,
            placeholder="Extracted or translated text will appear here. You can freely edit, fix typos, or add notes...",
            key="studio_editor_box"
        )
        if user_edited_text != st.session_state.extracted_text:
            st.session_state.extracted_text = user_edited_text

        char_c = len(user_edited_text)
        word_c = len(user_edited_text.split()) if user_edited_text else 0
        st.caption(f"📊 **{char_c}** characters &bull; **{word_c}** words")

    with tab_original:
        if st.session_state.original_extracted_text:
            st.text_area(
                "Original Raw Extracted Content:",
                st.session_state.original_extracted_text,
                height=220,
                disabled=True
            )
            if st.button("Restore Original Text into Active Editor", use_container_width=True):
                st.session_state.extracted_text = st.session_state.original_extracted_text
                st.rerun()
        else:
            st.info("No original text loaded yet.")

    with tab_insights:
        if st.session_state.extracted_text.strip():
            _, _, dist = detect_script_from_text(st.session_state.extracted_text)
            if dist:
                st.markdown("**Character Distribution Across Scripts:**")
                for script_k, pct in dist.items():
                    s_name = {"te": "Telugu (తెలుగు)", "kn": "Kannada (ಕನ್ನಡ)", "hi": "Hindi (हिंदी)", "en": "English"}.get(script_k, script_k.upper())
                    st.progress(pct / 100.0, text=f"{s_name}: {pct}%")
        else:
            st.info("Script composition will be calculated once text is loaded.")

    # PDF Page Previews Gallery
    if st.session_state.pdf_result and st.session_state.pdf_result.get("page_previews"):
        with st.expander("📑 PDF Page Gallery", expanded=False):
            previews = st.session_state.pdf_result["page_previews"]
            p_cols = st.columns(min(len(previews), 3))
            for idx, p_img in enumerate(previews):
                col_idx = idx % 3
                with p_cols[col_idx]:
                    st.image(p_img, caption=f"Page {idx + 1}", use_container_width=True)

    # -----------------------------------------------------
    # Speech Synthesis & Voice Tuning Card
    # -----------------------------------------------------
    st.markdown("#### 🎚️ Neural Voice Studio")

    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        voice_default_idx = 0
        if "Telugu" in st.session_state.active_language: voice_default_idx = 1
        elif "Kannada" in st.session_state.active_language: voice_default_idx = 3
        elif "Hindi" in st.session_state.active_language: voice_default_idx = 5
        elif "English" in st.session_state.active_language: voice_default_idx = 7

        voice_selection = st.selectbox(
            "Speech Voice Profile:",
            [
                "Auto-Match Text Script (Recommended)",
                "👩 Telugu (Shruti - Female)",
                "👨 Telugu (Mohan - Male)",
                "👩 Kannada (Sapna - Female)",
                "👨 Kannada (Gagan - Male)",
                "👩 Hindi (Swara - Female)",
                "👨 Hindi (Madhur - Male)",
                "👩 English (Neerja - Indian English)",
                "👨 English (Prabhat - Indian English)",
                "Google TTS (Fallback)"
            ],
            index=voice_default_idx
        )

    with v_col2:
        playback_speed = st.slider(
            "Playback Speed:",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.05,
            help="1.0x is clear conversational tempo."
        )

    # Instant Re-Synthesize Action
    re_synth = st.button(
        "🔄 Synthesize / Re-Speak with Selected Voice & Speed",
        use_container_width=True,
        help="Synthesizes fresh, clear audio from your current editor content."
    )

    if re_synth:
        if not user_edited_text.strip():
            st.warning("⚠️ The text editor is empty. Enter or extract text first.")
        else:
            with st.spinner("🎙️ Synthesizing clear speech audio..."):
                try:
                    voice_gender = "Female"
                    forced_lang = "auto"
                    engine_type = "edge-tts"

                    if "Telugu" in voice_selection:
                        forced_lang = "te"
                        voice_gender = "Male" if "Mohan" in voice_selection else "Female"
                    elif "Kannada" in voice_selection:
                        forced_lang = "kn"
                        voice_gender = "Male" if "Gagan" in voice_selection else "Female"
                    elif "Hindi" in voice_selection:
                        forced_lang = "hi"
                        voice_gender = "Male" if "Madhur" in voice_selection else "Female"
                    elif "English" in voice_selection:
                        forced_lang = "en"
                        voice_gender = "Male" if "Prabhat" in voice_selection else "Female"
                    elif "Google TTS" in voice_selection:
                        engine_type = "gtts"
                        forced_lang = detect_text_script_for_tts(user_edited_text)
                    else:
                        forced_lang = detect_text_script_for_tts(user_edited_text)

                    audio_res = synthesize_speech(
                        text=user_edited_text,
                        lang_code=forced_lang,
                        speed=playback_speed,
                        voice_gender=voice_gender,
                        engine=engine_type
                    )
                    st.session_state.audio_data = audio_res
                    st.toast("✅ Voice synthesized successfully!", icon="🔊")
                except Exception as e:
                    st.error(f"Speech error: {e}")

    # -----------------------------------------------------
    # Animated Waveform Audio Player Console
    # -----------------------------------------------------
    st.markdown("#### 🎧 Audio Console")

    if st.session_state.audio_data:
        audio_info = st.session_state.audio_data
        audio_bytes = audio_info["audio_bytes"]
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

        html5_player = f"""
        <div class="audio-player-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="waveform-visualizer">
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                    </div>
                    <span style="font-weight: 700; font-size: 0.96rem;">
                        Voice: <span style="color: #38BDF8;">{audio_info['voice']}</span>
                    </span>
                </div>
                <span style="font-size: 0.85rem; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #0284C7; padding: 4px 12px; border-radius: 10px;">
                    {audio_info['speed']}x Speed
                </span>
            </div>
            <audio id="ttsAudio" controls style="width: 100%; border-radius: 10px; margin-bottom: 8px;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                Your browser does not support HTML5 audio.
            </audio>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: gray;">
                <span>Engine: <b>{audio_info['engine']}</b></span>
                <span>NFC-Normalized &bull; Studio Master Quality</span>
            </div>
        </div>
        """
        st.markdown(html5_player, unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3")

    else:
        st.info("💡 Audio player will illuminate here with visualizer once speech is synthesized.")

    # -----------------------------------------------------
    # Download Hub
    # -----------------------------------------------------
    st.markdown("#### 💾 Export & Download Hub")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        if st.session_state.extracted_text.strip():
            clean_name = st.session_state.current_doc_name.split(".")[0] or "document"
            target_slug = st.session_state.active_language.split()[0].lower()
            st.download_button(
                label=f"📄 Download Text ({target_slug})",
                data=st.session_state.extracted_text.encode("utf-8"),
                file_name=f"{clean_name}_{target_slug}.txt",
                mime="text/plain; charset=utf-8",
                use_container_width=True
            )
        else:
            st.button("📄 Download Text (.txt)", disabled=True, use_container_width=True)

    with dl_col2:
        if st.session_state.audio_data and st.session_state.audio_data.get("audio_bytes"):
            clean_name = st.session_state.current_doc_name.split(".")[0] or "speech"
            target_slug = st.session_state.active_language.split()[0].lower()
            st.download_button(
                label=f"🎵 Download Audio ({target_slug} .mp3)",
                data=st.session_state.audio_data["audio_bytes"],
                file_name=f"{clean_name}_{target_slug}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        else:
            st.button("🎵 Download Audio (.mp3)", disabled=True, use_container_width=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.85rem; padding: 14px 0;">
    <b>Multilingual Vision Voice Canvas</b> &bull; Next-Generation Multimodal Studio for Text, Images, and PDFs.<br>
    Fluent and articulate output in <b>English</b>, <b>Telugu (తెలుగు)</b>, <b>Kannada (ಕನ್ನಡ)</b>, and <b>Hindi (हिंदी)</b>.
</div>
""", unsafe_allow_html=True)
