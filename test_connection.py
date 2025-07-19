#!/usr/bin/env python3
"""Debug printer connection issues"""

import ctypes
import os
import platform
import time

def test_direct_dll():
    """Test DLL functions directly"""
    print("=== Direct DLL Test ===")
    
    # Load DLL
    arch = 'x64' if platform.machine().endswith('64') else 'x86'
    dll_path = os.path.join(os.path.dirname(__file__), 
                           'thermal', 'windows SDK', 'bin', arch, 'HW_API.dll')
    
    print(f"Loading DLL from: {dll_path}")
    
    try:
        dll = ctypes.CDLL(dll_path)
        
        # Configure printerOpen
        dll.printerOpen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, 
                                    ctypes.c_int, ctypes.c_int]
        dll.printerOpen.restype = ctypes.c_int
        
        # Configure printerStatus
        dll.printerStatus.restype = ctypes.c_int
        
        # Configure printerClose
        dll.printerClose.restype = ctypes.c_int
        
        print("\n✓ DLL loaded successfully")
        
        # Test different connection parameters
        configs = [
            # Config 1: LPT0 with exact model
            {"interface": 1, "port": 0, "model": b"HMK-072", "flow": 0, "baud": 19200},
            # Config 2: LPT0 without dash
            {"interface": 1, "port": 0, "model": b"HMK072", "flow": 0, "baud": 19200},
            # Config 3: LPT0 with different baudrate
            {"interface": 1, "port": 0, "model": b"HMK-072", "flow": 0, "baud": 9600},
            # Config 4: Try as USB even though it shows as LPT
            {"interface": 0, "port": 0, "model": b"HMK-072", "flow": 0, "baud": 19200},
            # Config 5: Empty model string
            {"interface": 1, "port": 0, "model": b"", "flow": 0, "baud": 19200},
        ]
        
        for i, cfg in enumerate(configs):
            print(f"\n--- Test {i+1} ---")
            print(f"Interface: {'USB' if cfg['interface']==0 else 'SERIAL'}")
            print(f"Port: {cfg['port']}")
            print(f"Model: {cfg['model'].decode()}")
            print(f"Baudrate: {cfg['baud']}")
            
            # Open printer
            result = dll.printerOpen(cfg['interface'], cfg['port'], cfg['model'], 
                                   cfg['flow'], cfg['baud'])
            print(f"printerOpen result: {result}")
            
            if result == 0:
                print("✓ Connection successful!")
                
                # Wait a bit
                time.sleep(0.5)
                
                # Check status
                status = dll.printerStatus()
                print(f"printerStatus: {status}")
                
                # Try printing something
                dll.printStr.argtypes = [ctypes.c_char_p]
                dll.printStr.restype = ctypes.c_int
                
                test_result = dll.printStr(b"Test\n")
                print(f"printStr result: {test_result}")
                
                # Close
                dll.printerClose()
                print("Connection closed")
                
                return True
            else:
                print(f"✗ Connection failed with code: {result}")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_printer_driver():
    """Check Windows printer configuration"""
    print("\n=== Printer Driver Check ===")
    print("Run these commands in PowerShell to check printer setup:")
    print("")
    print("# Check if HMK-072 driver is installed:")
    print("Get-PrinterDriver | Where-Object {$_.Name -like '*HMK*'}")
    print("")
    print("# Check printer configuration:")
    print("Get-Printer | Where-Object {$_.Name -like '*HMK*'} | Format-List *")
    print("")
    print("# Check all printers:")
    print("Get-WmiObject Win32_Printer | Select Name, PortName, DriverName")

if __name__ == "__main__":
    print("HMK-072 Connection Debugger")
    print("=" * 50)
    
    # Test direct DLL calls
    if test_direct_dll():
        print("\n✓ Found working configuration!")
    else:
        print("\n✗ No working configuration found")
    
    # Show driver check commands
    check_printer_driver()
    
    print("\n" + "=" * 50)
    print("\nPossible issues:")
    print("1. The printer might need a specific driver mode")
    print("2. The model name might need to match exactly with driver")
    print("3. The printer might be in use by another program")
    print("4. Windows might be routing through a print spooler")
    print("\nTry:")
    print("- Restart the printer")
    print("- Check Windows Event Viewer for errors")
    print("- Install printer as 'Generic / Text Only' driver")