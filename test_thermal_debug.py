#!/usr/bin/env python3
"""Debug thermal printer connection issues"""

import os
import sys
import ctypes
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dll_loading():
    """Test if DLL can be loaded"""
    print("=== DLL Loading Test ===")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Check DLL paths
    arch = 'x64' if platform.machine().endswith('64') else 'x86'
    dll_path = os.path.join(os.path.dirname(__file__), 
                           'thermal', 'windows SDK', 'bin', arch, 'HW_API.dll')
    
    print(f"\nChecking DLL path: {dll_path}")
    print(f"DLL exists: {os.path.exists(dll_path)}")
    
    if os.path.exists(dll_path):
        try:
            # Try to load DLL
            dll = ctypes.CDLL(dll_path)
            print("✓ DLL loaded successfully!")
            
            # Check if functions exist
            try:
                printerOpen = dll.printerOpen
                print("✓ printerOpen function found")
            except:
                print("✗ printerOpen function not found")
                
        except Exception as e:
            print(f"✗ Failed to load DLL: {e}")
            print("\nPossible issues:")
            print("- Missing dependencies (Visual C++ Redistributables)")
            print("- Architecture mismatch")
            print("- DLL is corrupted")

def test_printer_connection():
    """Test different connection parameters"""
    print("\n=== Printer Connection Test ===")
    
    try:
        from thermal_printer import ThermalPrinter
        
        # Test different configurations
        configs = [
            {"port": 0, "interface": "USB", "model": "HMK-072"},
            {"port": 0, "interface": "USB", "model": "HMK072"},  # Without dash
            {"port": 1, "interface": "USB", "model": "HMK-072"},  # Try port 1
            {"port": 0, "interface": "SERIAL", "model": "HMK-072"},  # Try serial
        ]
        
        for i, config in enumerate(configs):
            print(f"\nTest {i+1}: Port={config['port']}, Interface={config['interface']}, Model={config['model']}")
            
            try:
                printer = ThermalPrinter(port=config['port'], baudrate=19200, interface=config['interface'])
                printer.model = config['model']  # Override model
                
                result = printer.connect()
                if result:
                    print(f"✓ SUCCESS! Connected with config {i+1}")
                    
                    # Try to get status
                    status = printer.get_status()
                    print(f"Printer status: {status}")
                    
                    printer.disconnect()
                    return True
                else:
                    print(f"✗ Failed with config {i+1}")
                    
            except Exception as e:
                print(f"✗ Error with config {i+1}: {e}")
                
    except ImportError as e:
        print(f"✗ Failed to import thermal_printer: {e}")
    
    return False

def check_usb_devices():
    """Check if USB printer is detected by Windows"""
    print("\n=== USB Device Check ===")
    print("Run this in Windows PowerShell to see USB devices:")
    print("Get-PnpDevice -Class 'Printer' | Select-Object Status, FriendlyName")
    print("\nOr in Command Prompt:")
    print("wmic printer list brief")

if __name__ == "__main__":
    print("Thermal Printer Debug Tool")
    print("="*50)
    
    # Test 1: DLL Loading
    test_dll_loading()
    
    # Test 2: Printer Connection
    test_printer_connection()
    
    # Test 3: USB info
    check_usb_devices()
    
    print("\n" + "="*50)
    print("Debug complete!")
    print("\nIf all tests fail, please check:")
    print("1. Is the printer driver installed? (Check Device Manager)")
    print("2. Is the printer shown in Windows Printers & Scanners?")
    print("3. Can you print from other applications?")
    print("4. Try running as Administrator")