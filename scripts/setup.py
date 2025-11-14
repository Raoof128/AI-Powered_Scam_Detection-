#!/usr/bin/env python3
"""
Setup Script
~~~~~~~~~~~~

Initial setup for the scam detection platform.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"📦 {description}")
    print(f"{'=' * 60}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        return False


def main():
    """Main setup function."""
    print("\n🚀 Scam Detection Platform Setup")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = [
        "data/raw",
        "data/processed",
        "data/models",
        "data/models/bert_cache",
        "logs",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")

    # Create .env from template if it doesn't exist
    if not Path(".env").exists():
        print("\n📝 Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("  ✅ .env file created")
        except Exception as e:
            print(f"  ❌ Error creating .env: {e}")
    else:
        print("\n✅ .env file already exists")

    # Install Python dependencies
    if not run_command(
        "pip install -e .[dev]",
        "Installing Python dependencies"
    ):
        print("\n⚠️  Failed to install dependencies. Try manually:")
        print("    pip install -e .[dev]")
        return False

    # Download spaCy model
    if not run_command(
        "python -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    ):
        print("\n⚠️  Failed to download spaCy model. Try manually:")
        print("    python -m spacy download en_core_web_sm")
        return False

    # Install pre-commit hooks (optional)
    if Path(".git").exists():
        print("\n🔧 Setting up pre-commit hooks...")
        run_command("pre-commit install", "Installing pre-commit hooks")

    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review and update .env file with your configuration")
    print("2. Start the development server:")
    print("   uvicorn src.api.main:app --reload")
    print("\n3. Or use Docker:")
    print("   docker-compose up -d")
    print("\n4. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print("\n5. Start developing in notebooks/:")
    print("   jupyter notebook")
    print("\n" + "=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
