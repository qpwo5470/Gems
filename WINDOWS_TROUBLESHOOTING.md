# Windows Troubleshooting Guide for Gems Station

## Common Issues and Solutions

### Chrome Driver Hanging on Startup

If Chrome opens but the script hangs, try these solutions:

1. **Test Chrome Driver First**
   ```cmd
   python test_chrome_windows.py
   ```
   This will test if Chrome driver works at all on your system.

2. **Update Chrome and ChromeDriver**
   ```cmd
   pip install --upgrade selenium webdriver-manager
   ```

3. **Disable Windows Defender Real-time Protection Temporarily**
   Windows Defender might interfere with ChromeDriver. Try disabling it temporarily while testing.

4. **Run as Administrator**
   Right-click on `run_gems.bat` and select "Run as administrator"

5. **Check Chrome Installation**
   - Ensure Chrome is installed in the default location
   - Try opening Chrome manually first
   - Close all Chrome instances before running the script

### ARM64/Parallels Specific Issues

Since you're running Windows ARM64 on Parallels:

1. **Use x64 Emulation**
   The script should automatically use x64 emulation for Chrome and ChromeDriver

2. **Increase Parallels Resources**
   - Allocate at least 4GB RAM to the Windows VM
   - Allocate at least 2 CPU cores

3. **Disable Hardware Acceleration in Chrome**
   1. Open Chrome manually
   2. Go to Settings → System
   3. Turn off "Use hardware acceleration when available"
   4. Restart Chrome

### Python Package Issues

If you get errors about missing packages:

```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Install Windows-specific packages
pip install pywin32==306
pip install pyinstaller==6.3.0
```

### Printer Issues

1. **Check Printer Installation**
   ```cmd
   python -c "import win32print; print([p[2] for p in win32print.EnumPrinters(2)])"
   ```
   This should show "HWASUNG HMK-072" in the list

2. **Test Printing**
   ```cmd
   python test_windows_print.py
   ```

### Script Hanging Issues

If the script hangs at any point:

1. **Check Task Manager**
   - Look for multiple Chrome or ChromeDriver processes
   - End all Chrome-related processes and try again

2. **Delete Chrome User Data**
   ```cmd
   rmdir /s /q chrome_user_data
   ```
   This will reset Chrome profile and require login again

3. **Run in Debug Mode**
   Edit `google_gems.py` and add at the top:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Alternative Startup Methods

1. **Direct Python Execution**
   ```cmd
   python google_gems.py
   ```

2. **With Explicit UTF-8 Encoding**
   ```cmd
   set PYTHONIOENCODING=utf-8
   python google_gems.py
   ```

3. **Using the Launcher Script**
   ```cmd
   python run_gems_windows.py
   ```

### If Nothing Works

1. **Collect Debug Information**
   ```cmd
   python test_chrome_windows.py > debug_output.txt 2>&1
   ```

2. **Check the output for specific errors**

3. **Common Error Messages:**
   - "DevToolsActivePort file doesn't exist" - Chrome failed to start properly
   - "chromedriver.exe not found" - ChromeDriver download failed
   - "timeout: Timed out receiving message from renderer" - Page loading issue

### Manual ChromeDriver Installation

If automatic ChromeDriver download fails:

1. Check your Chrome version: chrome://version/
2. Download matching ChromeDriver from: https://chromedriver.chromium.org/
3. Place chromedriver.exe in the project directory
4. Modify `google_gems.py` to use local driver:
   ```python
   service = Service('./chromedriver.exe')
   ```