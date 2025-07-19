"""Text-based receipt printer for thermal printers"""

import json
from typing import Dict

class ReceiptTextPrinter:
    """Generate text-based receipts for thermal printers"""
    
    def __init__(self):
        self.width = 32  # Standard thermal printer width
    
    def center_text(self, text: str) -> str:
        """Center text within printer width"""
        return text.center(self.width)
    
    def print_receipt_text(self, data: Dict, printer) -> bool:
        """Print receipt as formatted text"""
        try:
            # Header
            printer.set_align(printer.ALIGN_CENTER)
            printer.set_text_size(2, 2)
            printer.print_line("")
            printer.print_line("Gourmet Gems")
            printer.print_line("")
            
            # Type name (large)
            printer.set_text_size(1, 2)
            type_name = data.get('타입명', 'Unknown')
            printer.print_line(type_name)
            printer.print_line("")
            
            # Reset size
            printer.set_text_size(1, 1)
            
            # Type description
            printer.set_align(printer.ALIGN_CENTER)
            description = data.get('타입_설명', '')
            if description:
                # Wrap long description
                words = description.split()
                line = ""
                for word in words:
                    if len(line + word) > 30:
                        printer.print_line(line.strip())
                        line = word + " "
                    else:
                        line += word + " "
                if line:
                    printer.print_line(line.strip())
            
            printer.print_line("")
            printer.print_line("-" * 32)
            printer.print_line("")
            
            # Personal Keywords
            printer.print_line("Personal Keywords")
            keywords = data.get('성향_키워드', '')
            if keywords:
                printer.print_line(keywords)
            
            printer.print_line("")
            printer.print_line("-" * 32)
            printer.print_line("")
            
            # Your Pairing
            printer.print_line("Your Pairing")
            printer.print_line("")
            
            printer.set_align(printer.ALIGN_LEFT)
            food = data.get('푸드', '')
            drink = data.get('음료', '')
            
            if food:
                printer.print_text("Food  ")
                printer.print_line(food)
            if drink:
                printer.print_text("Drink ")
                printer.print_line(drink)
            
            printer.print_line("")
            printer.print_line("")
            
            # Footer
            printer.set_align(printer.ALIGN_CENTER)
            printer.print_line("Google Marketing Live")
            printer.print_line("")
            
            # Customer name (large)
            printer.set_text_size(1, 2)
            name = data.get('이름', '고객')
            printer.print_line(name + " 님을 위한")
            printer.print_line("맞춤 추천")
            
            # Reset and finish
            printer.set_text_size(1, 1)
            printer.feed_lines(4)
            printer.cut_paper(printer.CUT_PARTIAL)
            
            return True
            
        except Exception as e:
            print(f"Error printing text receipt: {e}")
            return False


# Integrate with receipt_printer.py
def add_text_printing_method():
    """Add text printing method to ReceiptPrinter class"""
    
    code = '''
    def print_text_receipt(self, data: Dict) -> bool:
        """Print receipt as text instead of image"""
        if not self.thermal_printer:
            print("Thermal printer not available")
            return False
            
        try:
            from receipt_text_printer import ReceiptTextPrinter
            text_printer = ReceiptTextPrinter()
            return text_printer.print_receipt_text(data, self.thermal_printer)
        except Exception as e:
            print(f"Text printing error: {e}")
            return False
    '''
    return code


# Test function
if __name__ == "__main__":
    # Test data
    test_data = {
        "이름": "시우",
        "번호": "2",
        "타입명": "Unexpected Innovator",
        "타입_설명": "틀을 깨는 아이디어로 고객에게 놀라움을 선사하고, 늘 새로운 변화를 시도하는 마케터.",
        "성향_키워드": "#열정 #변주 #모험적",
        "음료": "Negroni",
        "푸드": "파가든 브리오쉬 한우 버거"
    }
    
    # Test with printer
    try:
        from thermal_printer import ThermalPrinter
        printer = ThermalPrinter(port=0, baudrate=19200, interface='SERIAL')
        
        if printer.connect():
            text_printer = ReceiptTextPrinter()
            success = text_printer.print_receipt_text(test_data, printer)
            if success:
                print("✓ Text receipt printed successfully!")
            else:
                print("✗ Failed to print text receipt")
            printer.disconnect()
        else:
            print("✗ Failed to connect to printer")
            
    except Exception as e:
        print(f"Error: {e}")