#!/usr/bin/env python3
"""
Run the ROV Web Interface
Builds the React app and starts the web server
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function"""
    web_path = Path(__file__).parent / "web"
    
    print("🚀 Starting ROV Web Interface...")
    
    # Check if we're in the right directory
    if not web_path.exists():
        print(f"❌ Web directory not found: {web_path}")
        return 1
    
    # Check if node_modules exists
    node_modules = web_path / "node_modules"
    if not node_modules.exists():
        print("📦 Installing npm dependencies...")
        if not run_command("npm install", cwd=web_path):
            print("❌ Failed to install npm dependencies")
            return 1
    
    # Build the React app
    print("🔨 Building React app...")
    if not run_command("npm run build", cwd=web_path):
        print("❌ Failed to build React app")
        return 1
    
    # Install Python dependencies
    print("🐍 Installing Python dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        # Try using the virtual environment's pip first
        venv_pip = Path(__file__).parent.parent / "rov-venv-linux" / "bin" / "pip"
        if venv_pip.exists():
            if not run_command(f"{venv_pip} install -r {requirements_file}"):
                print("❌ Failed to install Python dependencies")
                return 1
        else:
            # Fall back to system pip with break-system-packages
            if not run_command(f"pip install --break-system-packages -r {requirements_file}"):
                print("❌ Failed to install Python dependencies")
                return 1
    
    # Start the web server
    print("🌐 Starting web server...")
    print("📱 Open http://localhost:3000 in your browser")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Change to surface directory and run the web server
        os.chdir(Path(__file__).parent)
        
        # Use the virtual environment's Python if available
        venv_python = Path(__file__).parent.parent / "rov-venv-linux" / "bin" / "python"
        if venv_python.exists():
            subprocess.run([str(venv_python), "web_server.py"], check=True)
        else:
            subprocess.run(["python", "web_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
