"""Simplified startup script for Windows"""
import os
import sys
import platform

def main():
    print("=" * 60)
    print("Gems Station Launcher for Windows")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.version()}")
    print(f"Python: {platform.python_version()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check for required files
    required_files = ['gemini_api_key.txt', 'credentials.json']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("\n⚠️  Warning: Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nThese files may be required for full functionality.")
    
    # Try importing required modules
    print("\nChecking dependencies...")
    try:
        import selenium
        print(f"✅ selenium {selenium.__version__}")
    except ImportError:
        print("❌ selenium not installed - run: pip install selenium")
        sys.exit(1)
    
    try:
        import webdriver_manager
        print(f"✅ webdriver_manager installed")
    except ImportError:
        print("❌ webdriver_manager not installed - run: pip install webdriver-manager")
        sys.exit(1)
    
    try:
        import win32print
        print("✅ pywin32 installed")
    except ImportError:
        print("❌ pywin32 not installed - run: pip install pywin32")
        sys.exit(1)
    
    try:
        import google.generativeai
        print("✅ google-generativeai installed")
    except ImportError:
        print("❌ google-generativeai not installed - run: pip install google-generativeai")
        sys.exit(1)
    
    # Run the main script
    print("\n" + "=" * 60)
    print("Starting Gems Station...")
    print("=" * 60 + "\n")
    
    try:
        # Import and run the main script
        from google_gems import main as run_gems
        run_gems()
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()