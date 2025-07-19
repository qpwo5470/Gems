"""Windows thermal printer driver using Windows Print API"""

import os
import platform
from typing import Optional

if platform.system() == 'Windows':
    try:
        import win32print
        import win32ui
        from PIL import Image, ImageWin
        WINDOWS_PRINT_AVAILABLE = True
    except ImportError:
        WINDOWS_PRINT_AVAILABLE = False
else:
    WINDOWS_PRINT_AVAILABLE = False


class WindowsThermalPrinter:
    """Windows printer driver for HWASUNG HMK-072"""
    
    def __init__(self, printer_name: str = "HWASUNG HMK-072"):
        """Initialize Windows thermal printer
        
        Args:
            printer_name: Windows printer name (default: "HWASUNG HMK-072")
        """
        self.printer_name = printer_name
        self.is_connected = False
        
        if not WINDOWS_PRINT_AVAILABLE:
            raise ImportError("pywin32 is required. Install with: pip install pywin32")
            
        # Check if printer exists
        self.check_printer()
    
    def check_printer(self) -> bool:
        """Check if printer is available in Windows"""
        try:
            printers = [p[2] for p in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            
            if self.printer_name in printers:
                self.is_connected = True
                print(f"✓ Found printer: {self.printer_name}")
                
                # Get printer info
                handle = win32print.OpenPrinter(self.printer_name)
                info = win32print.GetPrinter(handle, 2)
                win32print.ClosePrinter(handle)
                
                print(f"  Port: {info['pPortName']}")
                print(f"  Driver: {info['pDriverName']}")
                print(f"  Status: {'Ready' if info['Status'] == 0 else 'Not Ready'}")
                
                return True
            else:
                print(f"✗ Printer '{self.printer_name}' not found")
                print(f"Available printers: {', '.join(printers)}")
                return False
                
        except Exception as e:
            print(f"Error checking printer: {e}")
            return False
    
    def print_raw_text(self, text: str, encoding: str = 'cp949') -> bool:
        """Print raw text to printer"""
        if not self.is_connected:
            print("Printer not connected")
            return False
            
        try:
            # Open printer
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            # Start document
            job_info = ("Text Print", None, "RAW")
            hjob = win32print.StartDocPrinter(hprinter, 1, job_info)
            
            try:
                win32print.StartPagePrinter(hprinter)
                
                # Convert text to bytes
                if isinstance(text, str):
                    data = text.encode(encoding)
                else:
                    data = text
                    
                # Send data
                win32print.WritePrinter(hprinter, data)
                
                win32print.EndPagePrinter(hprinter)
                
            finally:
                win32print.EndDocPrinter(hprinter)
                
            win32print.ClosePrinter(hprinter)
            return True
            
        except Exception as e:
            print(f"Error printing text: {e}")
            return False
    
    def print_bitmap(self, image_path: str) -> bool:
        """Print bitmap image using Windows GDI"""
        if not self.is_connected:
            print("Printer not connected")
            return False
            
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return False
            
        try:
            # Convert to BMP if needed
            if not image_path.lower().endswith('.bmp'):
                from bitmap_converter import convert_to_bitmap
                bmp_path = convert_to_bitmap(image_path)
                if not bmp_path:
                    print("Failed to convert to bitmap")
                    return False
                image_path = bmp_path
            
            # Create printer device context
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(self.printer_name)
            
            # Open image
            img = Image.open(image_path)
            print(f"Original image: {img.size[0]}x{img.size[1]} pixels")
            
            # Simple crop from left to compensate for printer margin
            # Crop 7 pixels from the left side
            crop_left = 7
            width, height = img.size
            
            if width > crop_left:
                img = img.crop((crop_left, 0, width, height))
                print(f"Cropped {crop_left}px from left side")
                print(f"New image size: {img.size[0]}x{img.size[1]} pixels")
            
            # Start print job
            hdc.StartDoc("Bitmap Print")
            hdc.StartPage()
            
            # Get printer capabilities
            printer_width = hdc.GetDeviceCaps(110)   # PHYSICALWIDTH
            printer_height = hdc.GetDeviceCaps(111)  # PHYSICALHEIGHT
            offset_x = hdc.GetDeviceCaps(112)       # PHYSICALOFFSETX
            offset_y = hdc.GetDeviceCaps(113)       # PHYSICALOFFSETY
            
            print(f"Printer physical: {printer_width}x{printer_height}")
            print(f"Printer offset: {offset_x}, {offset_y}")
            
            # For thermal printers, we want to use full width starting from 0
            # Most thermal printers have no left margin when using raw printing
            img_ratio = img.size[0] / img.size[1]
            
            # Use full printer width
            print_width = printer_width
            print_height = int(print_width / img_ratio)
            
            # Convert to Windows DIB and print
            dib = ImageWin.Dib(img)
            
            # Print from left edge (image is already cropped)
            dib.draw(hdc.GetHandleOutput(), 
                    (0, 0,
                     print_width,
                     print_height))
            
            hdc.EndPage()
            hdc.EndDoc()
            
            # Cleanup
            del hdc
            
            print("✓ Bitmap sent to printer")
            return True
            
        except Exception as e:
            print(f"Error printing bitmap: {e}")
            return False
    
    def print_receipt(self, image_path: str, cut: bool = True) -> bool:
        """Print receipt image"""
        success = self.print_bitmap(image_path)
        
        if success and cut:
            # Send cut command as raw data
            # ESC/POS partial cut command
            self.print_raw_text("\n\n\n\x1D\x56\x01")
            
        return success
    
    def test_print(self) -> bool:
        """Test printer with simple output"""
        test_text = """
PRINTER TEST
============
HWASUNG HMK-072
Windows Print Mode
한글 출력 테스트

Status: OK
============



"""
        return self.print_raw_text(test_text)


# Make it compatible with existing code
class ThermalPrinter(WindowsThermalPrinter):
    """Compatibility wrapper for existing thermal printer code"""
    
    # Constants for compatibility
    INT_SERIAL = 1
    INT_USB = 0
    
    # Alignment constants
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2
    
    # Cut modes
    CUT_FULL = 0
    CUT_PARTIAL = 1
    CUT_BM = 2
    
    def __init__(self, port: int = 0, baudrate: int = 19200, interface: str = 'SERIAL'):
        # Ignore port/baudrate/interface - use Windows printer name
        super().__init__("HWASUNG HMK-072")
    
    def connect(self) -> bool:
        """Check if printer is available"""
        return self.check_printer()
    
    def disconnect(self):
        """No-op for Windows printing"""
        pass
    
    def get_status(self) -> int:
        """Get printer status"""
        return 0 if self.is_connected else -1
    
    def print_text(self, text: str, encoding: str = 'cp949'):
        """Print text string"""
        return self.print_raw_text(text, encoding)
    
    def print_line(self, text: str = ""):
        """Print text with newline"""
        return self.print_raw_text(text + "\n")
    
    def set_align(self, align: int):
        """No-op - alignment handled by Windows"""
        pass
    
    def set_bold(self, bold: bool):
        """No-op - bold handled by Windows"""
        pass
    
    def set_text_size(self, width: int = 1, height: int = 1):
        """No-op - size handled by Windows"""
        pass
    
    def feed_lines(self, lines: int):
        """Feed paper by number of lines"""
        self.print_raw_text("\n" * lines)
    
    def cut_paper(self, mode: int = 1):
        """Cut paper"""
        self.print_raw_text("\x1D\x56\x01")  # Partial cut
    
    def print_image(self, image_path: str, line_count: int = 0):
        """Print image file"""
        return self.print_bitmap(image_path)


if __name__ == "__main__":
    # Test the printer
    printer = ThermalPrinter()
    
    if printer.connect():
        print("\n--- Testing Windows Thermal Printer ---")
        
        # Test 1: Simple text
        print("Test 1: Simple text print")
        if printer.test_print():
            print("✓ Test print successful")
        else:
            print("✗ Test print failed")
        
        # Test 2: Bitmap
        if os.path.exists("test_thermal.bmp"):
            print("\nTest 2: Bitmap print")
            if printer.print_bitmap("test_thermal.bmp"):
                print("✓ Bitmap print successful")
            else:
                print("✗ Bitmap print failed")