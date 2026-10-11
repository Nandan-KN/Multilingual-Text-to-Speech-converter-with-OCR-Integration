"""
Generate sample PDF and TXT documents for testing Text, Image, and PDF input pipelines
in English, Telugu, Kannada, Hindi, and Mixed.
"""

import os
import pymupdf

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_documents")
os.makedirs(SAMPLE_DIR, exist_ok=True)

SAMPLES_DATA = {
    "english": {
        "title": "Artificial Intelligence and Multimodal Systems",
        "lang": "en",
        "content": (
            "Artificial Intelligence is rapidly advancing across multimodal perception and speech synthesis.\n\n"
            "By integrating optical document analysis with natural neural voice generation, "
            "users can seamlessly convert printed books, legal briefs, technical papers, and digital notes into lifelike spoken audio.\n\n"
            "This document verifies that English text, numerals like 2026, and punctuation are recognized accurately "
            "and synthesized with crystal-clear voice clarity."
        )
    },
    "telugu": {
        "title": "తెలుగు భాష మరియు సాంకేతిక పరిజ్ఞానం",
        "lang": "te",
        "content": (
            "నమస్కారం! తెలుగు భాష భారతదేశంలో అత్యంత ప్రాచీనమైన మరియు మధురమైన ద్రావిడ భాషలలో ఒకటి.\n\n"
            "ఈ ఆధునిక మల్టీలింగ్వల్ వ్యవస్థ ద్వారా తెలుగు పత్రాలను, చిత్రాలను మరియు పిడిఎఫ్ ఫైళ్లను క్షణాల్లో చదివి వినవచ్చు.\n\n"
            "ఆప్టికల్ క్యారెక్టర్ రికగ్నిషన్ మరియు న్యూరల్ టెక్స్ట్-టు-స్పీచ్ ద్వారా ప్రతి పదం స్పష్టంగా, సహజమైన శైలిలో వినిపిస్తుంది."
        )
    },
    "kannada": {
        "title": "ಕನ್ನಡ ಸಾಹಿತ್ಯ ಮತ್ತು ಆಧುನಿಕ ತಂತ್ರಜ್ಞಾನ",
        "lang": "kn",
        "content": (
            "ನಮಸ್ಕಾರ! ಕನ್ನಡ ಭಾಷೆ ಭಾರತದ ಅತ್ಯಂತ ಶ್ರೀಮಂತ, ಪ್ರಾಚೀನ ಮತ್ತು ಶಾಸ್ತ್ರೀಯ ಭಾಷೆಗಳಲ್ಲಿ ಪ್ರಮುಖವಾಗಿದೆ.\n\n"
            "ಈ ವ್ಯವಸ್ಥೆಯು ಕನ್ನಡ ಪಠ್ಯ, ಚಿತ್ರಗಳು ಮತ್ತು ಪಿಡಿಎಫ್ ದಾಖಲೆಗಳನ್ನು ಅತ್ಯಂತ ನಿಖರವಾಗಿ ಗುರುತಿಸುತ್ತದೆ.\n\n"
            "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಮತ್ತು ನೈಸರ್ಗಿಕ ಧ್ವನಿ ಸಂಶ್ಲೇಷಣೆಯ ಮೂಲಕ ಪ್ರತಿಯೊಂದು ಪದವೂ ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ಸುಲಭವಾಗಿ ಅರ್ಥವಾಗುವಂತೆ ಕೇಳಿಸುತ್ತದೆ."
        )
    },
    "hindi": {
        "title": "हिंदी भाषा और आधुनिक तकनीकी विकास",
        "lang": "hi",
        "content": (
            "नमस्ते! हिंदी भारत की एक प्रमुख, समृद्ध और अत्यंत लोकप्रिय भाषा है।\n\n"
            "यह आधुनिक बहुभाषी मंच मुद्रित पाठ, छवियों और पीडीएफ दस्तावेज़ों को पढ़कर उच्च गुणवत्ता वाली आवाज़ में प्रस्तुत करता है।\n\n"
            "इस प्रणाली का मुख्य उद्देश्य हर दस्तावेज़ को बिना किसी रुकावट के बिल्कुल स्पष्ट और समझने योग्य वाणी में बदलना है।"
        )
    }
}

def create_sample_files():
    for name, item in SAMPLES_DATA.items():
        # 1. Create .txt file
        txt_path = os.path.join(SAMPLE_DIR, f"sample_{name}.txt")
        full_text = f"{item['title']}\n\n{item['content']}"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"Created TXT: {txt_path}")

        # 2. Create .pdf file using pymupdf
        pdf_path = os.path.join(SAMPLE_DIR, f"sample_{name}.pdf")
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842) # A4

        # Draw a nice border and header
        rect = pymupdf.Rect(40, 40, 555, 802)
        page.draw_rect(rect, color=(0.8, 0.85, 0.9), width=1.5)
        
        # Insert title & text
        # For Indic fonts in PDF, we can use Nirmala font or fallback
        font_path = "C:/Windows/Fonts/Nirmala.ttc"
        if os.path.exists(font_path):
            page.insert_font(fontname="Nirmala", fontfile=font_path)
            fn = "Nirmala"
        else:
            fn = "helv"

        page.insert_text(pymupdf.Point(60, 90), item["title"], fontname=fn, fontsize=18, color=(0.1, 0.2, 0.4))
        
        # Insert body paragraphs
        y = 140
        for para in item["content"].split("\n\n"):
            # Insert textbox for multi-line wrapping
            text_rect = pymupdf.Rect(60, y, 535, y + 120)
            page.insert_textbox(text_rect, para, fontname=fn, fontsize=13, color=(0.15, 0.15, 0.2), lineheight=1.5)
            y += 110

        doc.save(pdf_path)
        doc.close()
        print(f"Created PDF: {pdf_path}")

if __name__ == "__main__":
    create_sample_files()
