#!/usr/bin/env python3
import os
import subprocess
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")
    print(f"Starting Streamlit on port {port}")
    print(f"Python executable: {sys.executable}")
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.serverAddress", "0.0.0.0"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
