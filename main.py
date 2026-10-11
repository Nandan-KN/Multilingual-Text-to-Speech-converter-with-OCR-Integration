"""
Master Unified Application Launcher for Multilingual Vision Voice Canvas.
Provides an interactive CLI and automated browser launcher for:
1. ⚡ Flashy Cyberpunk Neon Interface (Gradio - http://localhost:7860)
2. 🌌 Studio Glassmorphism Interface (Streamlit - http://localhost:8501)
3. 🚀 Dual-Launch (Both interfaces concurrently)
"""

import os
import sys
import subprocess
import webbrowser
import time
import argparse

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_dependencies():
    """Verifies that core packages are installed."""
    try:
        import gradio
        import streamlit
        import pytesseract
        import edge_tts
        print("✅ Core dependencies verified.")
        return True
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e}")
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def run_gradio(port=7860, auto_open=True):
    """Launches the Flashy Cyberpunk Neon Gradio Interface."""
    print(f"\n⚡ Starting Flashy Cyberpunk Neon Interface on http://localhost:{port}...")
    if auto_open:
        def open_browser():
            time.sleep(2.5)
            webbrowser.open(f"http://localhost:{port}")
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
    
    script = os.path.join(PROJECT_DIR, "gradio_app.py")
    subprocess.run([sys.executable, script])

def run_streamlit(port=8501, auto_open=True):
    """Launches the Studio Glassmorphism Streamlit Interface."""
    print(f"\n🌌 Starting Studio Glassmorphism Interface on http://localhost:{port}...")
    script = os.path.join(PROJECT_DIR, "app.py")
    cmd = [
        sys.executable, "-m", "streamlit", "run", script,
        f"--server.port={port}",
        "--server.headless=false" if auto_open else "--server.headless=true"
    ]
    subprocess.run(cmd)

def run_both():
    """Runs both Gradio and Streamlit servers concurrently."""
    print("\n🚀 Launching BOTH Interfaces Concurrently:")
    print("   ⚡ Flashy Gradio Interface:    http://localhost:7860")
    print("   🌌 Studio Streamlit Interface: http://localhost:8501\n")

    # Start Gradio in a background subprocess
    gradio_script = os.path.join(PROJECT_DIR, "gradio_app.py")
    p_gradio = subprocess.Popen([sys.executable, gradio_script])

    # Open browsers
    time.sleep(2)
    webbrowser.open("http://localhost:7860")
    webbrowser.open("http://localhost:8501")

    # Run Streamlit in foreground
    streamlit_script = os.path.join(PROJECT_DIR, "app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", streamlit_script, "--server.port=8501", "--server.headless=true"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        p_gradio.terminate()

def main():
    parser = argparse.ArgumentParser(description="Multilingual Vision Voice Canvas Launcher")
    parser.add_argument("--mode", choices=["gradio", "streamlit", "both"], default="menu",
                        help="Choose interface to run directly (gradio, streamlit, both)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    check_dependencies()

    if args.mode == "gradio":
        run_gradio(auto_open=not args.no_browser)
    elif args.mode == "streamlit":
        run_streamlit(auto_open=not args.no_browser)
    elif args.mode == "both":
        run_both()
    else:
        print("\n" + "="*60)
        print("  🎙️ MULTILINGUAL VISION VOICE CANVAS - STUDIO LAUNCHER")
        print("="*60)
        print("  Languages: English | Telugu (తెలుగు) | Kannada (ಕನ್ನಡ) | Hindi (हिंदी)")
        print("-" * 60)
        print("  Select interface to launch:")
        print("  [1] ⚡ Flashy Cyberpunk Neon Interface (Gradio)    -> Port 7860")
        print("  [2] 🌌 Studio Glassmorphism Interface (Streamlit) -> Port 8501")
        print("  [3] 🚀 Launch Both Interfaces Concurrently")
        print("  [4] ❌ Exit")
        print("="*60)
        
        choice = input("\nEnter choice [1-3] (Default: 1): ").strip()
        if choice == "2":
            run_streamlit(auto_open=True)
        elif choice == "3":
            run_both()
        elif choice == "4":
            print("Exiting.")
            sys.exit(0)
        else:
            run_gradio(auto_open=True)

if __name__ == "__main__":
    main()
