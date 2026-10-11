"""
Generate clean, high-resolution sample test images for English, Telugu, Kannada, Hindi, and Mixed Script.
Uses the Windows Nirmala UI font to render perfect native glyphs.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/Nirmala.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:/Windows/Fonts/arial.ttf"

def create_card_image(title, subtitle, paragraphs, filename, width=900, height=520):
    img = Image.new("RGB", (width, height), color=(252, 253, 255))
    draw = ImageDraw.Draw(img)

    # Subtle border
    draw.rectangle([(8, 8), (width - 9, height - 9)], outline=(210, 220, 235), width=2)
    # Header bar
    draw.rectangle([(8, 8), (width - 9, 65)], fill=(240, 245, 255))
    draw.line([(8, 65), (width - 9, 65)], fill=(210, 220, 235), width=2)

    try:
        title_font = ImageFont.truetype(FONT_PATH, 24)
        sub_font = ImageFont.truetype(FONT_PATH, 16)
        body_font = ImageFont.truetype(FONT_PATH, 20)
    except Exception:
        title_font = sub_font = body_font = ImageFont.load_default()

    draw.text((25, 20), title, fill=(20, 40, 80), font=title_font)
    draw.text((width - 260, 24), subtitle, fill=(100, 120, 150), font=sub_font)

    y = 90
    for para in paragraphs:
        draw.text((30, y), para, fill=(25, 30, 40), font=body_font)
        y += 45

    target_path = os.path.join(OUTPUT_DIR, filename)
    img.save(target_path, "PNG")
    print(f"Generated sample: {target_path} ({os.path.getsize(target_path)} bytes)")
    return target_path

def generate_all():
    # 1. English
    create_card_image(
        title="Multilingual OCR & TTS Studio - English Document",
        subtitle="Sample Test Card: English",
        paragraphs=[
            "Artificial Intelligence is transforming how we interact with technology.",
            "Optical Character Recognition allows computers to read printed documents.",
            "Text-to-Speech synthesis converts written words into natural spoken voice.",
            "This document tests high accuracy reading of English text with numbers 2026.",
            "Welcome to the Multilingual Vision Voice Canvas!"
        ],
        filename="sample_english.png"
    )

    # 2. Telugu
    create_card_image(
        title="బహుభాషా దృష్టి స్వరం - తెలుగు పత్రం",
        subtitle="నమూనా పత్రం: తెలుగు",
        paragraphs=[
            "నమస్కారం! తెలుగు భాష భారతదేశంలో అత్యంత ప్రాచీనమైన మరియు మధురమైన భాష.",
            "ఈ వ్యవస్థ తెలుగు లిపిని సులభంగా చదివి ఆడియో రూపంలోకి మారుస్తుంది.",
            "ఆప్టికల్ క్యారెక్టర్ రికగ్నిషన్ ద్వారా అక్షరాలు స్పష్టంగా గుర్తించబడతాయి.",
            "సాంకేతిక పరిజ్ఞానం ద్వారా సమాచారాన్ని వినడం ఇప్పుడు మరింత సులభం.",
            "మా విజన్ వాయిస్ కాన్వాస్ వేదికకు స్వాగతం సుస్వాగతం!"
        ],
        filename="sample_telugu.png"
    )

    # 3. Kannada
    create_card_image(
        title="ಬಹುಭಾಷಾ ದೃಷ್ಟಿ ಧ್ವನಿ - ಕನ್ನಡ ದಾಖಲೆ",
        subtitle="ಮಾದರಿ ದಾಖಲೆ: ಕನ್ನಡ",
        paragraphs=[
            "ನಮಸ್ಕಾರ! ಕನ್ನಡ ಭಾಷೆ ಭಾರತದ ಅತ್ಯಂತ ಪ್ರಾಚೀನ ಮತ್ತು ಸಮೃದ್ಧ ಭಾಷೆಗಳಲ್ಲಿ ಒಂದಾಗಿದೆ.",
            "ಈ ವ್ಯವಸ್ಥೆಯು ಕನ್ನಡ ಪಠ್ಯವನ್ನು ಸುಲಭವಾಗಿ ಗುರುತಿಸಿ ಸುಂದರ ಧ್ವನಿಗೆ ಪರಿವರ್ತಿಸುತ್ತದೆ.",
            "ಆಪ್ಟಿಕಲ್ ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ ತಂತ್ರಜ್ಞಾನವು ವೇಗವಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ.",
            "ಜ್ಞಾನ ಮತ್ತು ಮಾಹಿತಿಯನ್ನು ಎಲ್ಲರಿಗೂ ತಲುಪಿಸುವುದು ನಮ್ಮ ಮುಖ್ಯ ಉದ್ದೇಶವಾಗಿದೆ.",
            "ಮಲ್ಟಿಲಿಂಗ್ವಲ್ ವಿಷನ್ ವಾಯ್ಸ್ ಕ್ಯಾನ್ವಾಸ್ ಗೆ ಆತ್ಮೀಯ ಸ್ವಾಗತ!"
        ],
        filename="sample_kannada.png"
    )

    # 4. Hindi
    create_card_image(
        title="बहुभाषी दृष्टि और वाणी - हिंदी दस्तावेज़",
        subtitle="नमूना दस्तावेज़: हिंदी",
        paragraphs=[
            "नमस्ते! हिंदी भारत की एक प्रमुख, समृद्ध और सुंदर भाषा है।",
            "यह प्रणाली मुद्रित पाठ को पढ़कर प्राकृतिक आवाज़ में परिवर्तित करती है।",
            "ऑप्टिकल कैरेक्टर रिकग्निशन से अक्षरों की सही पहचान सुनिश्चित होती है।",
            "आधुनिक तकनीक ने पढ़ने और सुनने के अनुभव को बहुत आसान बना दिया है।",
            "मल्टीलिंगुअल विज़न वॉयस कैनवस में आपका हार्दिक स्वागत है!"
        ],
        filename="sample_hindi.png"
    )

    # 5. Mixed Multilingual
    create_card_image(
        title="Multilingual Mixed Document - బహుభాషా / ಕನ್ನಡ / हिंदी",
        subtitle="Mixed Script Test Card",
        paragraphs=[
            "India is a land of linguistic diversity and rich heritage.",
            "Telugu: నమస్కారం, జ్ఞానం అందరికీ అందాలి (Knowledge for all).",
            "Kannada: ನಮಸ್ಕಾರ, ಎಲ್ಲರಿಗೂ ಶುಭವಾಗಲಿ (Best wishes to everyone).",
            "Hindi: नमस्ते, आधुनिक तकनीक सभी को जोड़ती है (Tech connects all).",
            "Digital India Initiative 2026 - Multilingual Vision Voice Canvas."
        ],
        filename="sample_multilingual.png"
    )

if __name__ == "__main__":
    generate_all()
