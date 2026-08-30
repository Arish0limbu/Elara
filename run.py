#!/usr/bin/env python3
"""
ELARA - Application Entry Point
This script provides a convenient way to start the ELARA application.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if the environment is properly configured."""
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("Warning: .env file not found.")
        print("   Copy .env.example to .env and configure your settings.")
        print("   Continuing with default settings...")
    
    # Check if required directories exist
    required_dirs = ["data", "logs", "workspace", "models"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"Creating directory: {dir_name}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # Check Python version
    if sys.version_info < (3, 12):
        print("Warning: Python 3.12+ is recommended")
        print(f"   Current version: {sys.version}")
    
    return True

def main():
    """Main entry point for ELARA application."""
    print("ELARA - Personal AI Voice Assistant")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    try:
        # Import and run the main application
        from app.main import ElaraApp
        
        print("Starting ELARA...")
        app = ElaraApp()
        app.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nELARA shutting down gracefully...")
        sys.exit(0)
    
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
