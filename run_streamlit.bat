@echo off
title Multilingual Vision Voice Canvas - Streamlit Studio
color 0E
cd /d "%~dp0"
echo Starting Studio Glassmorphism Interface on http://localhost:8501...
python main.py --mode streamlit
pause
