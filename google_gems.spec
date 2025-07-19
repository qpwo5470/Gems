# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all data files
datas = [
    # HTML files
    ('waiting_screen.html', '.'),
    ('transition_screen.html', '.'),
    
    # Resource folder - entire directory with all images and files
    ('res', 'res'),
    
    # Thermal printer SDK
    ('thermal/windows SDK/bin/x64/HW_API.dll', 'thermal/windows SDK/bin/x64'),
    ('thermal/windows SDK/bin/x64/HwaUSB.dll', 'thermal/windows SDK/bin/x64'),
    ('thermal/windows SDK/bin/x86/HW_API.dll', 'thermal/windows SDK/bin/x86'),
    ('thermal/windows SDK/bin/x86/HwaUSB.dll', 'thermal/windows SDK/bin/x86'),
    
    # Configuration files - INCLUDE THE ACTUAL FILES
    ('credentials.json', '.'),
    ('gemini_api_key.txt', '.'),
    
    # Python modules that might be needed
    ('gemini_parser.py', '.'),
    ('receipt_printer.py', '.'),
    ('windows_thermal_printer.py', '.'),
]

# Hidden imports that might be missed
hiddenimports = [
    'PIL._tkinter_finder',
    'google.generativeai',
    'google.ai',
    'google.ai.generativelanguage_v1beta',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'win32print',
    'win32ui',
    'win32con',
    'pywintypes',
    'pythoncom',
    'pandas',
    'numpy',
    'openpyxl',  # for pandas Excel support
]

# Collect google-generativeai submodules
hiddenimports += collect_submodules('google.generativeai')
hiddenimports += collect_submodules('google.ai')

a = Analysis(
    ['run_gems_windows.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'scikit-learn',
        'notebook',
        'jupyter',
        'ipython',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
seen = set()
new_binaries = []
for item in a.binaries:
    name = item[0]
    if name not in seen:
        seen.add(name)
        new_binaries.append(item)
a.binaries = new_binaries

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GemsStation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False if you don't want console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='res/GEMS_icon.png' if os.path.exists('res/GEMS_icon.png') else None,
    version_file=None,
)