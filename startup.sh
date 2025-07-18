#!/bin/bash
echo "Starting Cryptogeezas Investment Club..."
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

# Set default port if not provided
PORT=${PORT:-8501}

echo "Using port: $PORT"
echo "Starting Streamlit..."

exec python3 -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
