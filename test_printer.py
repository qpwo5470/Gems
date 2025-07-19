#!/usr/bin/env python3
"""Simple test for thermal printer functionality"""

from receipt_printer import ReceiptPrinter
import json
import os

def test_receipt_generation():
    """Test receipt generation and printing"""
    
    # Test data
    test_data = {
        "이름": "햄부기햄북햄북어햄북스딱스",
        "번호": "2",
        "타입명": "Unexpected Innovator",
        "타입_설명": "틀을 깨는 아이디어로 고객에게 놀라움을 선사하고, 늘 새로운 변화를 시도하는 마케터.",
        "성향_키워드": "#열정 #변주 #모험적",
        "음료": "Negroni",
        "푸드": "파가든 브리오쉬 한우 버거"
    }
    
    print("=== Receipt Generation Test ===")
    print(f"Customer: {test_data['이름']}")
    print(f"Type: {test_data['타입명']} (#{test_data['번호']})")
    print(f"Pairing: {test_data['음료']} + {test_data['푸드']}")
    print("=" * 40)
    
    # Generate receipt
    printer = ReceiptPrinter()
    output_path = printer.add_name_to_receipt(test_data, "test_receipt.png")
    
    if output_path:
        print(f"✓ Receipt generated: {output_path}")
        
        # Check if thermal printer is available
        if printer.thermal_printer:
            print("\n✓ Thermal printer is connected")
            print("Receipt should be printing now...")
        else:
            print("\n✗ No thermal printer connected")
            print("Receipt image saved but not printed")
    else:
        print("✗ Failed to generate receipt")

def test_printer_connection():
    """Test printer connection only"""
    print("\n=== Printer Connection Test ===")
    
    try:
        from windows_thermal_printer import ThermalPrinter
        printer = ThermalPrinter()
        
        if printer.connect():
            print("✓ Printer connected successfully")
            
            # Simple test print
            printer.print_line("Printer Connection Test")
            printer.print_line("프린터 연결 테스트")
            printer.feed_lines(3)
            
            return True
        else:
            print("✗ Failed to connect to printer")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Thermal Printer Test")
    print("=" * 50)
    
    # Test 1: Connection
    test_printer_connection()
    
    # Test 2: Receipt generation
    print()
    test_receipt_generation()
    
    print("\n" + "=" * 50)
    print("Test complete!")