#!/usr/bin/env python3
"""Test full width printing on thermal printer"""

from PIL import Image, ImageDraw
from windows_thermal_printer import ThermalPrinter
import os

def create_edge_test_pattern():
    """Create a test pattern to check edge-to-edge printing"""
    
    # Create image with common thermal printer widths
    widths = [384, 576, 673]  # 58mm, 80mm, and your receipt width
    
    for width in widths:
        # Create bitmap
        height = 300
        img = Image.new('1', (width, height), 1)  # White background
        draw = ImageDraw.Draw(img)
        
        # Draw edge markers
        # Left edge - solid black line
        draw.line([(0, 0), (0, height-1)], fill=0, width=2)
        
        # Right edge - solid black line
        draw.line([(width-1, 0), (width-1, height-1)], fill=0, width=2)
        
        # Top and bottom edges
        draw.line([(0, 0), (width-1, 0)], fill=0, width=2)
        draw.line([(0, height-1), (width-1, height-1)], fill=0, width=2)
        
        # Draw ruler marks every 10 pixels
        for x in range(0, width, 10):
            if x % 50 == 0:
                # Major tick
                draw.line([(x, 0), (x, 20)], fill=0, width=1)
                draw.text((x+2, 25), str(x), fill=0)
            else:
                # Minor tick
                draw.line([(x, 0), (x, 10)], fill=0, width=1)
        
        # Center text
        center_x = width // 2
        draw.text((center_x, height//2), f"Width: {width}px", anchor="mm", fill=0)
        draw.text((center_x, height//2 + 20), "Edge-to-Edge Test", anchor="mm", fill=0)
        
        # Save
        filename = f"edge_test_{width}.bmp"
        img.save(filename, 'BMP')
        print(f"Created {filename}")
        
        # Print it
        printer = ThermalPrinter()
        if printer.connect():
            print(f"Printing {filename}...")
            if printer.print_bitmap(filename):
                print("✓ Printed successfully")
                print("Check if the lines reach both edges of the paper")
            else:
                print("✗ Failed to print")
            
            # Feed paper for easy checking
            printer.feed_lines(3)
        
    return True

if __name__ == "__main__":
    print("Full Width Printing Test")
    print("=" * 50)
    print("\nThis will print test patterns to check edge-to-edge printing")
    print("The pattern should have black lines at the very edges of the paper")
    print()
    
    create_edge_test_pattern()
    
    print("\n" + "=" * 50)
    print("Check the printout:")
    print("- Left edge should have a black line at the very edge")
    print("- Right edge should have a black line at the very edge")
    print("- If there's white space on the left, the printer driver is adding margins")