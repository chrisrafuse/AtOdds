#!/usr/bin/env python3
"""
Setup Virtual Environment for AtOdds Web API
Creates and configures virtual environment for Phase 6 web development
"""

import venv
import subprocess
import sys
import os
from pathlib import Path


def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    CR_venv_path = Path(".venv")
    
    if not CR_venv_path.exists():
        print("🔧 Creating virtual environment...")
        venv.create(CR_venv_path, with_pip=True, system_site_packages=False)
        print(f"✅ Virtual environment created at {CR_venv_path}")
    else:
        print(f"✅ Virtual environment already exists at {CR_venv_path}")
    
    return CR_venv_path


def get_python_path(CR_venv_path):
    """Get Python executable path in virtual environment"""
    if os.name == 'nt':  # Windows
        CR_python_path = CR_venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        CR_python_path = CR_venv_path / "bin" / "python"
    
    return str(CR_python_path)


def install_dependencies(CR_python_path):
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install requirements
    CR_requirements_files = [
        "requirements.txt",
        "requirements-web.txt"
    ]
    
    for CR_req_file in CR_requirements_files:
        if os.path.exists(CR_req_file):
            print(f"   Installing from {CR_req_file}...")
            CR_result = subprocess.run([
                CR_python_path, "-m", "pip", "install", "-r", CR_req_file
            ], capture_output=True, text=True)
            
            if CR_result.returncode == 0:
                print(f"   ✅ {CR_req_file} installed successfully")
            else:
                print(f"   ❌ Failed to install {CR_req_file}")
                print(f"   Error: {CR_result.stderr}")
                return False
        else:
            print(f"   ⚠️  {CR_req_file} not found, skipping")
    
    return True


def create_activate_script():
    """Create activation script for convenience"""
    if os.name == 'nt':  # Windows
        CR_activate_script = """@echo off
echo Activating AtOdds virtual environment...
call .venv\\Scripts\\activate.bat
echo Virtual environment activated!
echo.
echo To start the API server, run:
echo python apps/web/run_api.py
echo.
"""
        with open("activate.bat", "w") as f:
            f.write(CR_activate_script)
        print("✅ Created activate.bat")
    else:  # Unix-like
        CR_activate_script = """#!/bin/bash
echo "Activating AtOdds virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "To start the API server, run:"
echo "python apps/web/run_api.py"
echo ""
"""
        with open("activate.sh", "w") as f:
            f.write(CR_activate_script)
        os.chmod("activate.sh", 0o755)
        print("✅ Created activate.sh")


def main():
    """Main setup function"""
    print("🚀 Setting up AtOdds Web API Environment")
    print("=" * 50)
    
    # Create virtual environment
    CR_venv_path = create_virtual_environment()
    
    # Get Python path
    CR_python_path = get_python_path(CR_venv_path)
    
    # Install dependencies
    if not install_dependencies(CR_python_path):
        print("❌ Failed to install dependencies")
        return 1
    
    # Create activation script
    create_activate_script()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    if os.name == 'nt':
        print("1. Run: activate.bat")
    else:
        print("1. Run: source activate.sh")
    print("2. Run: python apps/web/run_api.py")
    print("3. Visit: http://localhost:8000/docs")
    print("\nOr manually activate with:")
    if os.name == 'nt':
        print(f"   {CR_venv_path}\\Scripts\\activate")
    else:
        print(f"   source {CR_venv_path}/bin/activate")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
