"""
Image Preprocessing Pipeline for Multilingual OCR.
Applies grayscale conversion, denoising, CLAHE contrast enhancement,
adaptive thresholding, and validation specifically tuned for Indic and Latin scripts.
"""

import cv2
import numpy as np
from PIL import Image

def load_as_cv2_image(image_source):
    """
    Safely convert various image sources (PIL.Image, bytes, numpy array, path)
    into a valid OpenCV BGR numpy array.
    """
    if isinstance(image_source, Image.Image):
        # Convert PIL to OpenCV BGR
        rgb = np.array(image_source.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    elif isinstance(image_source, bytes):
        nparr = np.frombuffer(image_source, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    elif isinstance(image_source, np.ndarray):
        if len(image_source.shape) == 2:
            return cv2.cvtColor(image_source, cv2.COLOR_GRAY2BGR)
        elif image_source.shape[2] == 4:
            return cv2.cvtColor(image_source, cv2.COLOR_RGBA2BGR)
        return image_source
    elif isinstance(image_source, str):
        return cv2.imread(image_source)
    else:
        raise ValueError(f"Unsupported image input type: {type(image_source)}")

def check_image_health(img_bgr):
    """
    Checks if an image is blank, solid color, corrupt, or has too little variance for OCR.
    Returns: (is_healthy: bool, message: str, metrics: dict)
    """
    if img_bgr is None or img_bgr.size == 0:
        return False, "Image could not be loaded or is empty.", {}

    h, w = img_bgr.shape[:2]
    if h < 20 or w < 20:
        return False, f"Image dimensions ({w}x{h}) are too small for OCR processing.", {}

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    std_dev = float(np.std(gray))
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    metrics = {
        "width": w,
        "height": h,
        "std_dev": round(std_dev, 2),
        "sharpness_var": round(laplacian_var, 2)
    }

    # Extremely low std deviation indicates a blank/solid canvas
    if std_dev < 4.0:
        return False, "The image appears to be blank or a single solid color with no readable content.", metrics

    # Extremely low sharpness combined with low std deviation indicates washed out / unreadable image
    if std_dev < 8.0 and laplacian_var < 5.0:
        return False, "The image lacks sufficient contrast and sharpness to detect any characters.", metrics

    return True, "Image passed health checks.", metrics

def deskew_image(gray_img):
    """
    Detects slight skew in text documents and straightens the image.
    Uses contour bounding box analysis.
    """
    try:
        # Invert colors so text is white
        thresh = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return gray_img, 0.0

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if skew is noticeable but not 90-degree rotated
        if abs(angle) > 0.5 and abs(angle) < 25.0:
            (h, w) = gray_img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                gray_img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated, round(angle, 2)
    except Exception:
        pass
    return gray_img, 0.0

def preprocess_for_ocr(
    image_source,
    mode="Adaptive Gaussian Thresholding (Recommended for Indic)",
    denoise_strength=5,
    auto_deskew=True
):
    """
    Full preprocessing pipeline:
    1. Validation / blank image check
    2. Conversion to grayscale
    3. Noise removal using Bilateral Filtering (preserves thin Indic strokes)
    4. CLAHE contrast enhancement
    5. Adaptive or Otsu thresholding
    6. Optional deskew
    """
    img_bgr = load_as_cv2_image(image_source)
    is_healthy, health_msg, metrics = check_image_health(img_bgr)
    if not is_healthy:
        raise ValueError(health_msg)

    # Grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Deskew if requested
    detected_skew = 0.0
    if auto_deskew:
        gray, detected_skew = deskew_image(gray)
    metrics["skew_angle"] = detected_skew

    # Denoising
    # Bilateral filter is preferred over Gaussian blur because it smoothens noise
    # while preserving glyph boundaries (crucial for Indic vowels, matras, and dots)
    d = max(3, int(denoise_strength * 2 - 1))
    denoised = cv2.bilateralFilter(gray, d=d, sigmaColor=50, sigmaSpace=50)

    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)

    # Thresholding branch
    if "Adaptive Gaussian" in mode:
        # Adaptive Gaussian thresholding works remarkably well on non-uniform lighting
        processed = cv2.adaptiveThreshold(
            contrast_enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=21,
            C=11
        )
    elif "Otsu" in mode:
        _, processed = cv2.threshold(
            contrast_enhanced,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    elif "CLAHE Contrast Stretching" in mode:
        processed = contrast_enhanced
    else:
        # Pure Grayscale
        processed = denoised

    # Convert back to PIL Image for Streamlit display
    pil_preview = Image.fromarray(processed)

    return processed, pil_preview, metrics
