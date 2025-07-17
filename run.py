#!/usr/bin/env python3
import os
import subprocess
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0"
    ]
    subprocess.run(cmd)
