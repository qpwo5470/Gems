#!/usr/bin/env python3
"""Test thermal printer on Windows without dependencies"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from thermal_printer import ThermalPrinter

def test_thermal_printer():
    """Test basic thermal printer functionality"""
    print("Testing HMK-072 thermal printer...")
    
    # Initialize printer
    printer = ThermalPrinter(port=0, baudrate=19200, interface='USB')
    
    # Try to connect
    if printer.connect():
        print("✓ Connected successfully!")
        
        # Print test receipt
        printer.set_align(printer.ALIGN_CENTER)
        printer.set_text_size(2, 2)
        printer.print_line("열두시 프린터 테스트")
        printer.print_line("Thermal Printer Test")
        
        printer.set_text_size(1, 1)
        printer.print_line("="*32)
        printer.print_line("Connection: USB")
        printer.print_line("Model: HMK-072")
        printer.print_line("="*32)
        
        # Test image printing if exists
        test_image = "thermal_print.png"
        if os.path.exists(test_image):
            print(f"Printing image: {test_image}")
            printer.print_image(test_image)
        
        printer.feed_lines(3)
        printer.cut_paper(printer.CUT_PARTIAL)
        
        printer.disconnect()
        print("✓ Test completed!")
    else:
        print("✗ Failed to connect to printer")
        print("Make sure:")
        print("- Printer is connected via USB")
        print("- Printer is powered on")
        print("- No other program is using the printer")

if __name__ == "__main__":
    test_thermal_printer()