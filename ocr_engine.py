"""
OCR Engine Abstraction Module.
Supports both Tesseract-OCR and EasyOCR with Indic multi-script parsing,
Unicode script auto-detection, mixed script confidence scoring, and error handling.
"""

import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image

import config

# Set Tesseract executable path if found
if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

if os.path.exists(config.TESSDATA_DIR):
    os.environ["TESSDATA_PREFIX"] = config.TESSDATA_DIR

# Global EasyOCR cache to prevent expensive model re-initializations
_EASYOCR_READERS = {}

def get_easyocr_reader(lang_list):
    """
    Caches EasyOCR Reader instances by language combination.
    """
    import easyocr
    key = tuple(sorted(lang_list))
    if key not in _EASYOCR_READERS:
        # gpu=False by default for universal compatibility
        _EASYOCR_READERS[key] = easyocr.Reader(lang_list, gpu=False)
    return _EASYOCR_READERS[key]

def detect_script_from_text(text):
    """
    Analyzes character counts across Unicode blocks for Telugu, Kannada, Hindi, and English.
    Returns:
        primary_lang_code (str): 'te', 'kn', 'hi', or 'en'
        primary_lang_name (str): Full display name
        script_distribution (dict): Percentage distribution of detected scripts
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

    total_chars = sum(counts.values())
    if total_chars == 0:
        return "en", "English", {"en": 100.0}

    distribution = {
        lang: round((count / total_chars) * 100, 1)
        for lang, count in counts.items() if count > 0
    }

    # Prioritize Indic scripts over English if any significant presence exists (> 15% of alphabetics)
    indic_counts = {"te": counts["te"], "kn": counts["kn"], "hi": counts["hi"]}
    top_indic_lang, top_indic_count = max(indic_counts.items(), key=lambda x: x[1])

    if top_indic_count > 0 and (top_indic_count >= counts["en"] * 0.25 or counts["en"] == 0):
        primary_code = top_indic_lang
    else:
        primary_code = max(counts.items(), key=lambda x: x[1])[0]

    code_to_name = {
        "en": "English",
        "te": "Telugu (తెలుగు)",
        "kn": "Kannada (ಕನ್ನಡ)",
        "hi": "Hindi (हिंदी)"
    }

    return primary_code, code_to_name.get(primary_code, "English"), distribution

def run_tesseract_ocr(image_np, selected_lang_code="auto"):
    """
    Performs OCR using Tesseract with traineddata and calculates word-level confidence.
    """
    if not config.TESSERACT_CMD or not os.path.exists(config.TESSERACT_CMD):
        raise RuntimeError(
            f"Tesseract executable was not found. Looked at: {config.POSSIBLE_TESSERACT_PATHS}"
        )

    # Determine Tesseract lang string
    if selected_lang_code == "auto":
        # Multi-script detection across all supported languages
        lang_str = "eng+hin+tel+kan"
    elif selected_lang_code in config.LANGUAGES:
        lang_str = config.LANGUAGES[selected_lang_code]["tesseract"]
    else:
        # Fallback by lookup
        for name, data in config.LANGUAGES.items():
            if data["code"] == selected_lang_code:
                lang_str = data["tesseract"]
                break
        else:
            lang_str = "eng"

    # Extract text with page segmentation mode 3 (Fully automatic page segmentation)
    tess_config = "--psm 3"
    raw_text = pytesseract.image_to_string(image_np, lang=lang_str, config=tess_config)
    cleaned_text = raw_text.strip()

    # Calculate average confidence
    try:
        data = pytesseract.image_to_data(image_np, lang=lang_str, config=tess_config, output_type=pytesseract.Output.DICT)
        confs = [int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit() and int(c) >= 0]
        avg_conf = round(float(np.mean(confs)), 1) if confs else 85.0
    except Exception:
        avg_conf = 85.0

    return cleaned_text, avg_conf

def run_easyocr(image_np, selected_lang_code="auto"):
    """
    Performs OCR using EasyOCR.
    """
    # EasyOCR does not allow mixing Devanagari and Telugu/Kannada in a single reader.
    # Therefore, if 'auto', we first run with ['hi', 'en'], then inspect or fallback.
    if selected_lang_code == "auto":
        lang_list = ["hi", "en"]
    elif selected_lang_code in config.LANGUAGES:
        lang_list = config.LANGUAGES[selected_lang_code]["easyocr"]
    else:
        lang_list = ["en"]

    reader = get_easyocr_reader(lang_list)
    results = reader.readtext(image_np)

    extracted_lines = []
    confidences = []
    for bbox, text, conf in results:
        extracted_lines.append(text)
        confidences.append(conf)

    cleaned_text = "\n".join(extracted_lines).strip()
    avg_conf = round(float(np.mean(confidences) * 100), 1) if confidences else 80.0

    return cleaned_text, avg_conf

def extract_text_multilingual(
    image_np,
    language_choice="Auto-Detect",
    engine_choice="Tesseract-OCR"
):
    """
    Unified entry point for OCR extraction.
    Returns:
        dict: {
            "text": str,
            "detected_lang_code": str ('en', 'te', 'kn', 'hi'),
            "detected_lang_name": str,
            "confidence": float (0-100),
            "script_distribution": dict,
            "engine": str
        }
    """
    lang_info = config.LANGUAGES.get(language_choice, config.LANGUAGES["Auto-Detect"])
    req_code = lang_info["code"]

    # Execute selected engine
    if engine_choice == "EasyOCR":
        try:
            text, conf = run_easyocr(image_np, selected_lang_code=req_code)
        except Exception as e:
            # Fallback to Tesseract if EasyOCR fails
            text, conf = run_tesseract_ocr(image_np, selected_lang_code=req_code)
            engine_choice = f"Tesseract-OCR (fallback from EasyOCR: {str(e)[:40]}...)"
    else:
        text, conf = run_tesseract_ocr(image_np, selected_lang_code=req_code)

    # Validate output
    if not text or len(text.strip()) == 0:
        raise ValueError(
            "The OCR engine completed processing but found no readable characters. "
            "Please ensure the image contains clear, in-focus text and that appropriate lighting or contrast is used."
        )

    # Detect script from extracted content
    detected_code, detected_name, distribution = detect_script_from_text(text)

    # If the user explicitly selected a language (not Auto-Detect), honor their selection
    final_lang_code = req_code if req_code != "auto" else detected_code
    final_lang_name = language_choice if req_code != "auto" else detected_name

    return {
        "text": text,
        "detected_lang_code": final_lang_code,
        "detected_lang_name": final_lang_name,
        "confidence": conf,
        "script_distribution": distribution,
        "engine": engine_choice
    }
