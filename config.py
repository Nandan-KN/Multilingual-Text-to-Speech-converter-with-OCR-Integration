"""
Configuration module for Multilingual OCR and Text-to-Speech (TTS) Studio.
Defines language mappings, voice catalogues, Tesseract/EasyOCR paths, and constants.
"""

import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESSDATA_DIR = os.path.join(BASE_DIR, "tessdata")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_images")
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "output_audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Detect and configure Tesseract executable
POSSIBLE_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    shutil.which("tesseract") or ""
]

TESSERACT_CMD = None
for p in POSSIBLE_TESSERACT_PATHS:
    if p and os.path.exists(p):
        TESSERACT_CMD = p
        break

# Configure TESSDATA_PREFIX environment variable
if os.path.exists(TESSDATA_DIR):
    os.environ["TESSDATA_PREFIX"] = TESSDATA_DIR

# Language definitions
LANGUAGES = {
    "Auto-Detect": {
        "code": "auto",
        "tesseract": "eng+hin+tel+kan",
        "easyocr": ["en", "hi", "te", "kn"],
        "edge_voice": "hi-IN-SwaraNeural",
        "edge_voice_male": "hi-IN-MadhurNeural",
        "gtts_code": "hi",
        "native_name": "Auto / స్వయంచాలక / ಸ್ವಯಂಚಾಲಿತ / स्वचालित",
        "flag": "🌐"
    },
    "English": {
        "code": "en",
        "tesseract": "eng",
        "easyocr": ["en"],
        "edge_voice": "en-IN-NeerjaNeural",
        "edge_voice_male": "en-IN-PrabhatNeural",
        "gtts_code": "en",
        "native_name": "English",
        "flag": "🇬🇧"
    },
    "Telugu (తెలుగు)": {
        "code": "te",
        "tesseract": "tel+eng",
        "easyocr": ["te", "en"],
        "edge_voice": "te-IN-ShrutiNeural",
        "edge_voice_male": "te-IN-MohanNeural",
        "gtts_code": "te",
        "native_name": "తెలుగు",
        "flag": "🇮🇳"
    },
    "Kannada (ಕನ್ನಡ)": {
        "code": "kn",
        "tesseract": "kan+eng",
        "easyocr": ["kn", "en"],
        "edge_voice": "kn-IN-SapnaNeural",
        "edge_voice_male": "kn-IN-GaganNeural",
        "gtts_code": "kn",
        "native_name": "ಕನ್ನಡ",
        "flag": "🇮🇳"
    },
    "Hindi (हिंदी)": {
        "code": "hi",
        "tesseract": "hin+eng",
        "easyocr": ["hi", "en"],
        "edge_voice": "hi-IN-SwaraNeural",
        "edge_voice_male": "hi-IN-MadhurNeural",
        "gtts_code": "hi",
        "native_name": "हिंदी",
        "flag": "🇮🇳"
    }
}

# Unicode Script Blocks for accurate script auto-detection
UNICODE_SCRIPT_BLOCKS = {
    "te": {
        "name": "Telugu",
        "label": "Telugu (తెలుగు)",
        "ranges": [(0x0C00, 0x0C7F)]
    },
    "kn": {
        "name": "Kannada",
        "label": "Kannada (ಕನ್ನಡ)",
        "ranges": [(0x0C80, 0x0CFF)]
    },
    "hi": {
        "name": "Hindi (Devanagari)",
        "label": "Hindi (हिंदी)",
        "ranges": [(0x0900, 0x097F)]
    },
    "en": {
        "name": "English (Latin)",
        "label": "English",
        "ranges": [(0x0041, 0x005A), (0x0061, 0x007A)]
    }
}

PREPROCESSING_MODES = [
    "Adaptive Gaussian Thresholding (Recommended for Indic)",
    "Otsu Binarization (Best for Uniform High Contrast)",
    "CLAHE Contrast Stretching (Preserves Delicate Glyph Curves)",
    "Pure Grayscale Denoised (Fast Baseline)"
]
