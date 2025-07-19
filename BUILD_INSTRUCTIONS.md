# Building Gems Station for Windows

## Prerequisites

1. Install Python 3.8+ on Windows
2. Install all dependencies:
   ```cmd
   pip install -r requirements.txt
   pip install pywin32
   pip install pyinstaller
   ```

## Build Steps

### Method 1: Using the build script

1. Double-click `build_windows.bat` or run in command prompt:
   ```cmd
   build_windows.bat
   ```

### Method 2: Manual build

1. Clean previous builds:
   ```cmd
   rmdir /s /q dist build
   ```

2. Build with PyInstaller:
   ```cmd
   pyinstaller google_gems.spec --noconfirm
   ```

## After Building

1. The executable will be in the `dist` folder: `dist\GemsStation.exe`

2. Copy these files to the `dist` folder:
   - `gemini_api_key.txt` (with your actual API key)
   - `credentials.json` (with your email)

3. The `dist` folder will contain:
   ```
   GemsStation.exe
   gemini_api_key.txt
   credentials.json
   res/ (folder with all resources)
   thermal/ (folder with printer DLLs)
   waiting_screen.html
   transition_screen.html
   ```

## Distribution

To distribute, zip the entire `dist` folder contents. Users need:
- Windows 10/11
- HWASUNG HMK-072 printer installed
- Chrome browser installed

## Troubleshooting

### Missing modules error
Add the module to `hiddenimports` in `google_gems.spec`

### DLL not found error
Make sure the DLL paths in the spec file match your directory structure

### Printer not working
Ensure the HWASUNG HMK-072 printer driver is installed on the target system

### Large file size
You can reduce size by:
- Setting `upx=True` in the spec file (already enabled)
- Excluding unnecessary packages in the `excludes` list
- Using `--onefile` option (but startup will be slower)

## Creating an installer

For professional distribution, consider using:
- NSIS (Nullsoft Scriptable Install System)
- Inno Setup
- WiX Toolset

These can create a proper Windows installer that:
- Checks for printer driver
- Creates desktop shortcuts
- Handles uninstallation properly