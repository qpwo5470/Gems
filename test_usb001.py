#!/usr/bin/env python3
"""Test thermal printer specifically on USB001"""

from thermal_printer import ThermalPrinter

# Connect to USB001
printer = ThermalPrinter(port=1, baudrate=19200, interface='USB')

print("Attempting to connect to HMK-072 on USB001...")
if printer.connect():
    print("✓ Connected successfully!")
    
    # Simple test
    printer.print_line("USB001 Connection Test")
    printer.print_line("프린터 연결 성공!")
    printer.feed_lines(3)
    printer.cut_paper()
    
    printer.disconnect()
else:
    print("✗ Connection failed")
    print("Make sure:")
    print("- Printer is on USB001 port")
    print("- Printer is powered on")
    print("- No other software is using the printer")