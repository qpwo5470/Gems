#!/usr/bin/env python3
"""Test printing through Windows print system"""

import win32print
import win32ui
from PIL import Image, ImageWin
import os

def list_printers():
    """List all Windows printers"""
    print("=== Available Printers ===")
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    
    for printer in printers:
        print(f"Name: {printer[2]}")
        print(f"Description: {printer[1]}")
        print(f"Port: {printer[0]}")
        print("-" * 40)
    
    return [p[2] for p in printers]

def print_to_windows_printer(printer_name=None):
    """Print using Windows printer API"""
    
    if printer_name is None:
        # Get default printer
        printer_name = win32print.GetDefaultPrinter()
    
    print(f"\nUsing printer: {printer_name}")
    
    # Open printer
    hprinter = win32print.OpenPrinter(printer_name)
    
    try:
        # Start a print job
        job_info = ("Python Thermal Test", None, "RAW")
        hjob = win32print.StartDocPrinter(hprinter, 1, job_info)
        
        try:
            win32print.StartPagePrinter(hprinter)
            
            # Send raw text
            test_data = b"Windows Printer Test\n"
            test_data += b"="*32 + b"\n"
            test_data += b"If you see this, Windows printing works!\n"
            test_data += b"\n" * 5
            
            win32print.WritePrinter(hprinter, test_data)
            
            win32print.EndPagePrinter(hprinter)
            print("✓ Data sent to printer")
            
        finally:
            win32print.EndDocPrinter(hprinter)
            
    finally:
        win32print.ClosePrinter(hprinter)

def print_bitmap_windows(printer_name=None, image_path="test_thermal.bmp"):
    """Print bitmap using Windows GDI"""
    
    if printer_name is None:
        printer_name = win32print.GetDefaultPrinter()
    
    print(f"\nPrinting bitmap to: {printer_name}")
    
    # Create device context
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    
    # Open bitmap
    if os.path.exists(image_path):
        bmp = Image.open(image_path)
        
        # Start document
        hdc.StartDoc("Bitmap Test")
        hdc.StartPage()
        
        # Draw bitmap
        dib = ImageWin.Dib(bmp)
        dib.draw(hdc.GetHandleOutput(), (0, 0, bmp.width, bmp.height))
        
        hdc.EndPage()
        hdc.EndDoc()
        
        print("✓ Bitmap sent to printer")
    else:
        print(f"✗ Image not found: {image_path}")
    
    # Cleanup
    del hdc

if __name__ == "__main__":
    print("Windows Printer Test")
    print("=" * 50)
    
    # First install win32print if needed:
    # pip install pywin32
    
    try:
        # List printers
        printers = list_printers()
        
        # Find HMK printer
        hmk_printer = None
        for p in printers:
            if "HMK" in p.upper():
                hmk_printer = p
                break
        
        if hmk_printer:
            print(f"\n✓ Found HMK printer: {hmk_printer}")
            
            # Test raw printing
            print("\n--- Testing Raw Print ---")
            print_to_windows_printer(hmk_printer)
            
            # Create test bitmap if needed
            if not os.path.exists("test_thermal.bmp"):
                from bitmap_converter import create_test_bitmap
                create_test_bitmap()
            
            # Test bitmap printing
            print("\n--- Testing Bitmap Print ---")
            print_bitmap_windows(hmk_printer, "test_thermal.bmp")
            
        else:
            print("\n✗ No HMK printer found in Windows")
            print("Using default printer instead...")
            print_to_windows_printer()
            
    except ImportError:
        print("\n✗ pywin32 not installed")
        print("Install it with: pip install pywin32")
    except Exception as e:
        print(f"\n✗ Error: {e}")