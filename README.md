# Multilingual Vision Voice Canvas 🎙️⚡

A state-of-the-art Multimodal Document OCR, Neural Translation, and High-Clarity Speech Synthesis Studio for:
**English**, **Telugu (తెలుగు)**, **Kannada (ಕನ್ನಡ)**, and **Hindi (हिंदी)**.

Built with **Gradio 6.0+**, **Streamlit**, **OpenCV**, **PyMuPDF**, **Tesseract-OCR**, **EasyOCR**, and **Microsoft Edge-TTS Indian Neural Voice Engine**.

---

## ⚡ Two Complete User Interfaces Included

You can launch and use either of the two user interfaces:

### 1. ⚡ Flashy Cyberpunk Neon Interface (Gradio)
👉 **URL:** [http://localhost:7860](http://localhost:7860)  
👉 **Command:** `python gradio_app.py`
- **Visual Style**: Cyberpunk Neon Glassmorphism (`#00f2fe` neon cyan, `#ff007f` neon magenta, `#9d4edd` electric violet).
- **Features**:
  - Scanning neon hero header with glowing badges.
  - Multi-tabbed intake: **Image Studio**, **PDF Studio**, **Plain Text Studio**, and **Instant Sample Loaders**.
  - Animated glowing buttons (`🚀 EXTRACT & SYNTHESIZE IMAGE / PDF / TEXT`).
  - One-click **Quick Language Transformer Ribbon** (`[🇮🇳 తెలుగు] [🇮🇳 ಕನ್ನಡ] [🇮🇳 हिंदी] [🇬🇧 English]`).
  - Embedded high-clarity neural audio player with autoplay and waveform display.
  - Instant text restoration from raw un-translated OCR output.

### 2. 🌌 Studio Glassmorphism Interface (Streamlit)
👉 **URL:** [http://localhost:8501](http://localhost:8501)  
👉 **Command:** `streamlit run app.py`
- **Visual Style**: Deep slate glassmorphism with subtle glow borders and animated CSS audio waveform visualizer.
- **Features**:
  - 4-Stage visual pipeline stepper (`Intake` &rarr; `OCR` &rarr; `Translation` &rarr; `Voice`).
  - Side-by-side tabbed text comparison (Active Output vs Raw OCR vs Script Distribution).
  - Multi-page PDF page gallery with rendered page previews.
  - Speed presets and voice gender controls.
  - Dual text and MP3 export hub.

---

## 🏛️ Project Structure

```
multilingual-ocr-tts/
├── gradio_app.py               # Flashy Cyberpunk Neon Gradio Interface (Port 7860)
├── app.py                      # Studio Glassmorphism Streamlit Interface (Port 8501)
├── document_loader.py          # Unified loader for Text, PDF (digital & scanned), and Images
├── preprocessing.py            # OpenCV pipeline (Bilateral denoising, CLAHE, Adaptive threshold, Deskew)
├── ocr_engine.py               # Tesseract-OCR & EasyOCR with multi-script auto-detection
├── tts_engine.py               # Clean neural speech synthesis (Unicode NFC, sentence chunking, thread-safe runner)
├── translator.py               # Translation engine (GoogleTranslator + MyMemory fallback)
├── config.py                   # Language packs, voice catalogs, and system paths
├── generate_samples.py         # Generates image sample cards
├── generate_sample_docs.py     # Generates sample PDF and TXT documents
├── sample_images/              # Sample images for testing
├── sample_documents/           # Sample PDF and TXT documents for testing
├── tessdata/                   # Traineddata language packs (eng, tel, kan, hin, osd)
├── requirements.txt            # Project dependencies
└── README.md                   # Complete documentation
```

---

## 🚀 Quickstart

### Launch Both Interfaces:
1. **Launch the Flashy Gradio Interface:**
   ```bash
   python gradio_app.py
   ```
   Open [http://localhost:7860](http://localhost:7860)

2. **Launch the Streamlit Studio Interface:**
   ```bash
   streamlit run app.py
   ```
   Open [http://localhost:8501](http://localhost:8501)
