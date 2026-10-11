from setuptools import setup, find_packages

setup(
    name="multilingual-vision-voice-canvas",
    version="1.0.0",
    description="Multilingual OCR, Translation & Neural Text-to-Speech Studio for English, Telugu, Kannada, and Hindi",
    author="Nandan K N",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "streamlit>=1.35.0",
        "gradio>=5.0.0",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "gTTS>=2.5.0",
        "edge-tts>=7.0.0",
        "Pillow>=10.0.0",
        "opencv-python-headless>=4.8.0",
        "numpy>=1.24.0",
        "pymupdf>=1.24.0",
        "deep-translator>=1.11.0",
        "pyttsx3>=2.90",
        "langdetect>=1.0.9",
    ],
    entry_points={
        "console_scripts": [
            "voice-canvas=main:main",
        ],
    },
)
