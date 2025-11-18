#!/usr/bin/env python3
"""
Quick launcher for MAGI System Web UI.
Checks dependencies and launches Streamlit.
"""

import sys
import subprocess


def check_streamlit():
    """Check if Streamlit is installed."""
    try:
        import streamlit

        return True, streamlit.__version__
    except ImportError:
        return False, None


def check_lm_studio():
    """Check if LM Studio server is reachable."""
    try:
        import requests

        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("🧠 MAGI System - Web UI Launcher")
    print("=" * 60)
    print()

    # Check Streamlit
    print("Checking dependencies...")
    streamlit_ok, version = check_streamlit()

    if not streamlit_ok:
        print("❌ Streamlit not found!")
        print()
        print("Installing Streamlit...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "streamlit"], check=True
            )
            print("✅ Streamlit installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Streamlit.")
            print("Please run manually: pip install streamlit")
            sys.exit(1)
    else:
        print(f"✅ Streamlit found (version {version})")

    # Check LM Studio
    print("Checking LM Studio server...")
    if check_lm_studio():
        print("✅ LM Studio server is running")
    else:
        print("⚠️  LM Studio server not detected")
        print("   Make sure to start LM Studio before initializing the council")

    print()
    print("=" * 60)
    print("Starting Web UI...")
    print("=" * 60)
    print()
    print("The web interface will open in your browser automatically.")
    print("If it doesn't open, navigate to: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server.")
    print()

    # Launch Streamlit
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.headless",
                "false",
            ]
        )
    except KeyboardInterrupt:
        print("\n\nShutting down Web UI...")
        print("Goodbye! 👋")


if __name__ == "__main__":
    main()
