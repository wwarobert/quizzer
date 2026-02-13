#!/usr/bin/env python3
"""
Quizzer Web Server Startup Script
Automatically checks dependencies and starts the Flask server.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, shell=True, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=shell, check=check, capture_output=True, text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_venv():
    """Check if virtual environment exists."""
    venv_path = Path(".venv")
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    return venv_path.exists() and python_exe.exists()


def create_venv():
    """Create virtual environment."""
    print("📦 Creating virtual environment...")
    success, stdout, stderr = run_command(f"{sys.executable} -m venv .venv")
    if success:
        print("✅ Virtual environment created")
        return True
    else:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False


def get_venv_python():
    """Get the path to the virtual environment Python executable."""
    if sys.platform == "win32":
        return Path(".venv") / "Scripts" / "python.exe"
    else:
        return Path(".venv") / "bin" / "python"


def check_module(python_exe, module_name):
    """Check if a module is installed."""
    cmd = f'"{python_exe}" -c "import {module_name}"'
    success, _, _ = run_command(cmd, check=False)
    return success


def install_requirements(python_exe):
    """Install requirements from requirements.txt."""
    if not Path("requirements.txt").exists():
        print("⚠️  requirements.txt not found")
        return True

    print("📦 Installing dependencies from requirements.txt...")
    cmd = f'"{python_exe}" -m pip install -r requirements.txt'
    success, stdout, stderr = run_command(cmd)

    if success:
        print("✅ All dependencies installed")
        return True
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False


def check_and_install_dependencies():
    """Check and install missing dependencies."""
    # Check if venv exists, create if not
    if not check_venv():
        print("🔍 Virtual environment not found")
        if not create_venv():
            return False

    python_exe = get_venv_python()

    # Check for Flask (main requirement)
    if not check_module(python_exe, "flask"):
        print("🔍 Flask not found, installing dependencies...")
        if not install_requirements(python_exe):
            return False
    else:
        print("✅ Dependencies already installed")

    return True


def start_server():
    """Start the Flask web server."""
    python_exe = get_venv_python()
    print("\n🚀 Starting Quizzer Web Server...")
    print("=" * 50)

    # Build command as list to avoid shell injection
    # Pass through any command-line arguments (e.g., --test-mode, --port, etc.)
    cmd = [str(python_exe), "web_quiz.py"] + sys.argv[1:]

    # Use subprocess.run without shell=True for security
    try:
        subprocess.run(cmd, shell=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")


def main():
    """Main entry point."""
    print("=" * 50)
    print("🎯 Quizzer Web Server Launcher")
    print("=" * 50)
    print()

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Check and install dependencies
    if not check_and_install_dependencies():
        print("\n❌ Failed to prepare dependencies")
        sys.exit(1)

    # Start the server
    start_server()


if __name__ == "__main__":
    main()
