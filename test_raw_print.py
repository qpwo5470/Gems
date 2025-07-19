#!/usr/bin/env python3
"""Test raw printing to verify data is being sent"""

import ctypes
import os
import time

def test_raw_printing():
    """Test sending raw data to printer"""
    
    # Load DLL
    dll_path = os.path.join(os.path.dirname(__file__), 
                           'thermal', 'windows SDK', 'bin', 'x64', 'HW_API.dll')
    
    print(f"Loading DLL: {dll_path}")
    dll = ctypes.CDLL(dll_path)
    
    # Configure functions
    dll.printerOpen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, 
                                ctypes.c_int, ctypes.c_int]
    dll.printerOpen.restype = ctypes.c_int
    
    dll.printStr.argtypes = [ctypes.c_char_p]
    dll.printStr.restype = ctypes.c_int
    
    dll.printCmd.argtypes = [ctypes.c_int]
    dll.printCmd.restype = ctypes.c_int
    
    dll.feedLine.argtypes = [ctypes.c_int]
    dll.feedLine.restype = ctypes.c_int
    
    dll.printerClose.restype = ctypes.c_int
    
    # Open printer - LPT0
    print("\nOpening printer on LPT0...")
    result = dll.printerOpen(1, 0, b"HMK-072", 0, 19200)
    print(f"printerOpen result: {result}")
    
    if result != 0:
        print("Failed to open printer")
        return False
    
    print("✓ Printer opened successfully")
    
    # Test different print methods
    tests = [
        # Test 1: Simple ASCII
        ("ASCII text", lambda: dll.printStr(b"Hello World\n")),
        
        # Test 2: Feed lines
        ("Feed 2 lines", lambda: dll.feedLine(2)),
        
        # Test 3: Korean text in CP949
        ("Korean CP949", lambda: dll.printStr("한글 테스트\n".encode('cp949'))),
        
        # Test 4: Print command (LF)
        ("Print LF command", lambda: dll.printCmd(10)),  # 10 = LF
        
        # Test 5: Multiple lines
        ("Multiple lines", lambda: dll.printStr(b"Line 1\nLine 2\nLine 3\n")),
        
        # Test 6: Feed and return
        ("Feed and CR", lambda: (dll.feedLine(1), dll.printCmd(13))),  # 13 = CR
    ]
    
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        result = test_func()
        if isinstance(result, tuple):
            result = result[0]
        print(f"Result: {result}")
        time.sleep(0.5)  # Small delay between tests
    
    # Feed paper to see if anything printed
    print("\nFeeding paper...")
    dll.feedLine(5)
    
    # Close printer
    print("\nClosing printer...")
    dll.printerClose()
    
    print("\n✓ Test complete")
    print("\nIf nothing printed, check:")
    print("1. Is the printer online/ready?")
    print("2. Is paper loaded?")
    print("3. Try power cycling the printer")
    print("4. Check if printer needs ESC/POS commands instead")
    
    return True

def test_esc_pos():
    """Test ESC/POS commands"""
    print("\n=== Testing ESC/POS Commands ===")
    
    dll_path = os.path.join(os.path.dirname(__file__), 
                           'thermal', 'windows SDK', 'bin', 'x64', 'HW_API.dll')
    dll = ctypes.CDLL(dll_path)
    
    # Configure
    dll.printerOpen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, 
                                ctypes.c_int, ctypes.c_int]
    dll.printerOpen.restype = ctypes.c_int
    dll.printStr.argtypes = [ctypes.c_char_p]
    dll.printStr.restype = ctypes.c_int
    dll.printerClose.restype = ctypes.c_int
    
    # Open
    if dll.printerOpen(1, 0, b"HMK-072", 0, 19200) != 0:
        print("Failed to open printer")
        return
    
    # ESC/POS init sequence
    print("Sending ESC/POS init...")
    dll.printStr(b"\x1B\x40")  # ESC @ - Initialize printer
    
    # Print test with ESC/POS
    dll.printStr(b"\x1B\x61\x01")  # ESC a 1 - Center align
    dll.printStr(b"ESC/POS TEST\n")
    dll.printStr(b"\x1B\x61\x00")  # ESC a 0 - Left align
    dll.printStr(b"If you see this, ESC/POS works!\n")
    
    # Feed and cut
    dll.printStr(b"\n\n\n")  # Feed lines
    dll.printStr(b"\x1D\x56\x01")  # GS V 1 - Partial cut
    
    dll.printerClose()
    print("ESC/POS test complete")

if __name__ == "__main__":
    print("Raw Printer Test")
    print("=" * 50)
    
    # Test 1: Raw printing
    test_raw_printing()
    
    # Test 2: ESC/POS
    test_esc_pos()