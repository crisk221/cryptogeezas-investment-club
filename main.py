import os
import sys
import subprocess

def main():
    print("=== CRYPTOGEEZAS DEPLOYMENT LAUNCHER ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    
    # List files in current directory
    print("Files in current directory:")
    for item in os.listdir("."):
        print(f"  - {item}")
    
    # Set the port
    port = os.environ.get('PORT', '8501')
    print(f"Using port: {port}")
    
    # Prepare the command
    command = [
        sys.executable, 
        '-m', 
        'streamlit', 
        'run', 
        'app.py',
        '--server.port', 
        str(port),
        '--server.address', 
        '0.0.0.0',
        '--server.headless', 
        'true'
    ]
    
    print(f"Executing command: {' '.join(command)}")
    
    # Execute streamlit
    try:
        result = subprocess.run(command, check=True)
        print(f"Streamlit exited with code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error running streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Received interrupt signal")
        sys.exit(0)

if __name__ == "__main__":
    main()
