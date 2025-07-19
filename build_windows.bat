@echo off
echo Building Gems Station for Windows...
echo.

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Create required files if missing
if not exist gemini_api_key.txt (
    echo Creating gemini_api_key.txt...
    echo YOUR_API_KEY_HERE > gemini_api_key.txt
)

if not exist credentials.json (
    echo Creating credentials.json...
    echo {"email": "your-email@gmail.com"} > credentials.json
)

REM Build with PyInstaller
echo Running PyInstaller...
pyinstaller google_gems.spec --noconfirm

REM Check if build was successful
if exist dist\GemsStation.exe (
    echo.
    echo Build successful!
    echo Executable created at: dist\GemsStation.exe
    echo.
    echo Next steps:
    echo 1. Copy gemini_api_key.txt to dist folder
    echo 2. Copy credentials.json to dist folder
    echo 3. Make sure HWASUNG HMK-072 printer is installed
    echo 4. Run GemsStation.exe
) else (
    echo.
    echo Build failed! Check error messages above.
)

pause