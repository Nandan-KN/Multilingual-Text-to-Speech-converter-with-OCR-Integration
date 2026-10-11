"""
Document Loader and Extractor Module.
Unified ingestion for:
1. Text files (.txt) and direct text pasting
2. PDF files (.pdf) - Native digital text extraction + Scanned page OCR fallback
3. Images (.png, .jpg, .jpeg, .webp, .bmp) & Camera capture
"""

import os
import io
import pymupdf
from PIL import Image
import numpy as np

import config
from preprocessing import preprocess_for_ocr, load_as_cv2_image, check_image_health
from ocr_engine import extract_text_multilingual

def load_text_from_file(file_bytes, filename="document.txt"):
    """
    Safely reads text file bytes using multiple encoding fallbacks (UTF-8, UTF-16, Latin-1).
    """
    encodings = ["utf-8", "utf-8-sig", "utf-16", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            text = file_bytes.decode(enc)
            return text.strip(), enc
        except UnicodeDecodeError:
            continue
    # Fallback with replacement
    return file_bytes.decode("utf-8", errors="replace").strip(), "utf-8 (lossy)"

def extract_from_pdf(
    file_bytes,
    language_choice="Auto-Detect",
    engine_choice="Tesseract-OCR",
    preprocess_mode="Adaptive Gaussian Thresholding (Recommended for Indic)",
    max_pages=15
):
    """
    Processes a PDF document:
    1. First attempts to extract native digital text from each page.
    2. If a page has insufficient digital text (< 20 characters), renders the page
       as a high-resolution image and runs our OCR pipeline.
    Returns:
        dict: {
            "text": str,
            "page_count": int,
            "processed_pages": int,
            "digital_text_pages": int,
            "ocr_pages": int,
            "page_previews": list of PIL.Image,
            "detected_lang_code": str,
            "detected_lang_name": str,
            "confidence": float
        }
    """
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    total_pages = len(doc)
    pages_to_process = min(total_pages, max_pages)

    full_extracted_pages = []
    page_previews = []
    digital_count = 0
    ocr_count = 0

    for i in range(pages_to_process):
        page = doc[i]
        
        # 1. Render page preview image (72 dpi for UI preview)
        preview_pix = page.get_pixmap(dpi=120)
        img_data = preview_pix.tobytes("png")
        pil_preview = Image.open(io.BytesIO(img_data))
        page_previews.append(pil_preview)

        # 2. Check for native selectable text in PDF
        page_text = page.get_text().strip()

        # If digital text exists and is meaningful (> 25 characters)
        if len(page_text) > 25:
            full_extracted_pages.append(f"--- Page {i + 1} ---\n{page_text}")
            digital_count += 1
        else:
            # Scanned or image-based PDF page -> Render at 200 DPI for high-accuracy OCR
            ocr_pix = page.get_pixmap(dpi=200)
            ocr_img_data = ocr_pix.tobytes("png")
            ocr_pil = Image.open(io.BytesIO(ocr_img_data))
            
            try:
                proc_arr, _, _ = preprocess_for_ocr(ocr_pil, mode=preprocess_mode)
                ocr_res = extract_text_multilingual(
                    proc_arr,
                    language_choice=language_choice,
                    engine_choice=engine_choice
                )
                extracted_page_text = ocr_res["text"]
                full_extracted_pages.append(f"--- Page {i + 1} (Scanned OCR) ---\n{extracted_page_text}")
                ocr_count += 1
            except Exception as ocr_err:
                full_extracted_pages.append(f"--- Page {i + 1} ---\n[OCR Note: {str(ocr_err)}]")

    doc.close()

    combined_text = "\n\n".join(full_extracted_pages).strip()

    from ocr_engine import detect_script_from_text
    det_code, det_name, distribution = detect_script_from_text(combined_text)

    return {
        "text": combined_text,
        "page_count": total_pages,
        "processed_pages": pages_to_process,
        "digital_text_pages": digital_count,
        "ocr_pages": ocr_count,
        "page_previews": page_previews,
        "detected_lang_code": det_code,
        "detected_lang_name": det_name,
        "script_distribution": distribution
    }
