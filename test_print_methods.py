#!/usr/bin/env python3
"""Test different printing methods for HMK-072"""

from thermal_printer import ThermalPrinter
import os

def test_text_printing():
    """Test basic text printing"""
    print("=== Testing Text Printing ===")
    printer = ThermalPrinter(port=0, baudrate=19200, interface='SERIAL')
    
    if printer.connect():
        print("✓ Connected to printer")
        
        # Test 1: Simple text
        print("Test 1: Simple text...")
        success = printer.print_line("Hello World!")
        print(f"Result: {'Success' if success else 'Failed'}")
        
        # Test 2: Korean text
        print("Test 2: Korean text...")
        success = printer.print_line("안녕하세요!")
        print(f"Result: {'Success' if success else 'Failed'}")
        
        # Test 3: Formatted receipt
        print("Test 3: Formatted receipt...")
        printer.set_align(printer.ALIGN_CENTER)
        printer.set_text_size(2, 2)
        printer.print_line("Gourmet Gems")
        
        printer.set_text_size(1, 1)
        printer.print_line("-" * 32)
        
        printer.set_align(printer.ALIGN_LEFT)
        printer.print_line("이름: 시우")
        printer.print_line("타입: Unexpected Innovator")
        printer.print_line("음료: Negroni")
        printer.print_line("푸드: 파가든 브리오쉬 한우 버거")
        
        printer.print_line("-" * 32)
        printer.feed_lines(3)
        printer.cut_paper()
        
        printer.disconnect()
        return True
    else:
        print("✗ Failed to connect")
        return False

def test_image_formats():
    """Test different image formats and methods"""
    print("\n=== Testing Image Printing ===")
    printer = ThermalPrinter(port=0, baudrate=19200, interface='SERIAL')
    
    if printer.connect():
        print("✓ Connected to printer")
        
        # Check if image exists
        test_images = ["thermal_print.png", "test_thermal_print.png"]
        
        for img_path in test_images:
            if os.path.exists(img_path):
                print(f"\nTesting image: {img_path}")
                
                # Test with different line counts
                for lines in [0, 12, 24, 48]:
                    print(f"  Trying with {lines} lines...")
                    success = printer.print_image(img_path, lines)
                    if success:
                        print(f"  ✓ Success with {lines} lines!")
                        break
                    else:
                        print(f"  ✗ Failed with {lines} lines")
        
        printer.disconnect()
    else:
        print("✗ Failed to connect")

def test_raw_commands():
    """Test raw print commands"""
    print("\n=== Testing Raw Commands ===")
    printer = ThermalPrinter(port=0, baudrate=19200, interface='SERIAL')
    
    if printer.connect():
        print("✓ Connected to printer")
        
        # Test printer status
        status = printer.get_status()
        print(f"Printer status code: {status}")
        
        # Test raw text with encoding
        print("Testing different encodings...")
        
        # Try CP949 (Korean)
        printer.print_text("CP949: 한글 테스트\n", encoding='cp949')
        
        # Try UTF-8
        printer.print_text("UTF-8: 한글 테스트\n", encoding='utf-8')
        
        # Try EUC-KR
        printer.print_text("EUC-KR: 한글 테스트\n", encoding='euc-kr')
        
        printer.feed_lines(3)
        printer.disconnect()
    else:
        print("✗ Failed to connect")

if __name__ == "__main__":
    print("HMK-072 Printer Test Suite")
    print("=" * 50)
    
    # Test 1: Text printing
    if test_text_printing():
        print("\n✓ Text printing works!")
    
    # Test 2: Image formats
    test_image_formats()
    
    # Test 3: Raw commands
    test_raw_commands()
    
    print("\n" + "=" * 50)
    print("Testing complete!")