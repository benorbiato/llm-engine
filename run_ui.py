#!/usr/bin/env python3
"""
Main entry point for running the Streamlit UI locally.
"""

import sys
import os
import subprocess


if __name__ == "__main__":
    # Run streamlit with main_ui.py
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/entrypoints/main_ui.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--logger.level=info"
    ]
    
    subprocess.run(cmd)

