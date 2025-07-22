# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect numpy and pandas data files
numpy_datas = collect_data_files('numpy')
pandas_datas = collect_data_files('pandas')

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

# Add numpy and pandas data files
datas.extend(numpy_datas)
datas.extend(pandas_datas)

# Collect numpy and pandas binaries
numpy_bins = collect_dynamic_libs('numpy')
pandas_bins = collect_dynamic_libs('pandas')

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
    'pandas._libs',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.skiplist',
    'numpy',
    'numpy._distributor_init',
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'numpy.random._pickle',
    'numpy.random._common',
    'numpy.random._bounded_integers',
    'numpy.random._mt19937',
    'openpyxl',  # for pandas Excel support
]

# Collect google-generativeai submodules
hiddenimports += collect_submodules('google.generativeai')
hiddenimports += collect_submodules('google.ai')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('pandas')

a = Analysis(
    ['run_gems_windows.py'],
    pathex=[current_dir],
    binaries=numpy_bins + pandas_bins,
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
    upx=False,  # Disable UPX compression to avoid numpy issues
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