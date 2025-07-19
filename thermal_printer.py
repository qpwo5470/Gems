import ctypes
import os
from typing import Optional
import platform

class ThermalPrinter:
    """Windows thermal printer driver for HMK-072 using HW_API.dll"""
    
    # Constants from API
    INT_SERIAL = 1
    INT_USB = 0
    
    # Flow control
    XON_XOFF = 0
    RTS_CTS = 1
    DTR_DSR = 2
    
    # Cut modes
    CUT_FULL = 0
    CUT_PARTIAL = 1
    CUT_BM = 2
    
    # Alignment
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2
    
    # Font settings
    FONT_KR24_EN24 = 0
    FONT_KR16_EN24 = 1
    FONT_KR24_EN16 = 4
    FONT_KR16_EN16 = 5
    
    # Language/Region
    LANG_KO = 13
    LANG_EN = 0
    
    def __init__(self, port: int = 0, baudrate: int = 19200, interface: str = 'USB'):
        """Initialize thermal printer on Windows
        
        Args:
            port: Port number (0 for USB, 1 for LPT1)
            baudrate: Communication speed (default 19200 for HMK-072)
            interface: 'USB' or 'SERIAL' (LPT)
        """
        self.port = port
        self.baudrate = baudrate
        self.model = "HMK-072"
        self.interface = self.INT_USB if interface.upper() == 'USB' else self.INT_SERIAL
        self.is_connected = False
        self.dll = None
        
        # Load DLL based on architecture
        if platform.system() != 'Windows':
            raise OSError("This printer driver only works on Windows")
            
        try:
            # Determine DLL path based on architecture
            arch = 'x64' if platform.machine().endswith('64') else 'x86'
            dll_path = os.path.join(os.path.dirname(__file__), 
                                   'thermal', 'windows SDK', 'bin', arch, 'HW_API.dll')
            
            if not os.path.exists(dll_path):
                # Try alternative path
                dll_path = os.path.join('thermal', 'windows SDK', 'bin', arch, 'HW_API.dll')
            
            # Load the DLL
            self.dll = ctypes.CDLL(dll_path)
            
            # Configure function signatures
            self._configure_dll_functions()
            
        except Exception as e:
            raise RuntimeError(f"Failed to load HW_API.dll: {e}")
    
    def _configure_dll_functions(self):
        """Configure DLL function signatures"""
        # printerOpen(int interface_type, int port, string model, int flowcontrol, int baudrate)
        self.dll.printerOpen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, 
                                         ctypes.c_int, ctypes.c_int]
        self.dll.printerOpen.restype = ctypes.c_int
        
        # printStr(string str)
        self.dll.printStr.argtypes = [ctypes.c_char_p]
        self.dll.printStr.restype = ctypes.c_int
        
        # printImage(int linecnt, string filename)
        self.dll.printImage.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.dll.printImage.restype = ctypes.c_int
        
        # Other functions
        self.dll.printerClose.restype = ctypes.c_int
        self.dll.printerStatus.restype = ctypes.c_int
        self.dll.cut.argtypes = [ctypes.c_int]
        self.dll.cut.restype = ctypes.c_int
        self.dll.feedLine.argtypes = [ctypes.c_int]
        self.dll.feedLine.restype = ctypes.c_int
        self.dll.textAlign.argtypes = [ctypes.c_int]
        self.dll.textAlign.restype = ctypes.c_int
        self.dll.textBold.argtypes = [ctypes.c_int]
        self.dll.textBold.restype = ctypes.c_int
        self.dll.textSize.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.textSize.restype = ctypes.c_int
        self.dll.textFont.argtypes = [ctypes.c_int]
        self.dll.textFont.restype = ctypes.c_int
        self.dll.inter_font.argtypes = [ctypes.c_int]
        self.dll.inter_font.restype = ctypes.c_int
    
    def connect(self) -> bool:
        """Open connection to printer"""
        try:
            # printerOpen(interface_type, port, model, flowcontrol, baudrate)
            # For USB: interface_type=USB(0), port=0, flowcontrol=XON_XOFF(0)
            result = self.dll.printerOpen(
                self.interface,   # USB or Serial interface
                self.port,        # 0 for USB, 1 for LPT1
                self.model.encode('utf-8'),
                self.XON_XOFF,    # Flow control
                self.baudrate
            )
            
            self.is_connected = (result == 0)
            if self.is_connected:
                interface_name = "USB" if self.interface == self.INT_USB else f"LPT{self.port}"
                print(f"Connected to {self.model} on {interface_name}")
                # Set Korean font for better text support
                self.dll.inter_font(self.LANG_KO)
                self.dll.textFont(self.FONT_KR16_EN16)
            else:
                print(f"Failed to connect to printer. Error code: {result}")
                
            return self.is_connected
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close printer connection"""
        if self.is_connected:
            self.dll.printerClose()
            self.is_connected = False
            print("Disconnected from printer")
    
    def get_status(self) -> int:
        """Get printer status"""
        if not self.is_connected:
            return -1
        return self.dll.printerStatus()
    
    def print_text(self, text: str, encoding: str = 'cp949'):
        """Print text string"""
        if not self.is_connected:
            print("Printer not connected")
            return False
            
        try:
            # Convert to bytes with Korean encoding
            text_bytes = text.encode(encoding)
            result = self.dll.printStr(text_bytes)
            return result == 0
        except Exception as e:
            print(f"Print error: {e}")
            return False
    
    def print_line(self, text: str = ""):
        """Print text with newline"""
        return self.print_text(text + "\n")
    
    def set_align(self, align: int):
        """Set text alignment (0=left, 1=center, 2=right)"""
        if self.is_connected:
            self.dll.textAlign(align)
    
    def set_bold(self, bold: bool):
        """Set bold text"""
        if self.is_connected:
            self.dll.textBold(1 if bold else 0)
    
    def set_text_size(self, width: int = 1, height: int = 1):
        """Set text size multiplier (1-8)"""
        if self.is_connected:
            self.dll.textSize(width, height)
    
    def feed_lines(self, lines: int):
        """Feed paper by number of lines"""
        if self.is_connected:
            self.dll.feedLine(lines)
    
    def cut_paper(self, mode: int = CUT_PARTIAL):
        """Cut paper (0=full, 1=partial)"""
        if self.is_connected:
            self.dll.cut(mode)
    
    def print_image(self, image_path: str, line_count: int = 0):
        """Print image file
        
        Args:
            image_path: Path to image file
            line_count: Number of lines (0 for auto)
        """
        if not self.is_connected:
            print("Printer not connected")
            return False
            
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False
            
        try:
            # Convert path to bytes
            path_bytes = image_path.encode('utf-8')
            result = self.dll.printImage(line_count, path_bytes)
            return result == 0
        except Exception as e:
            print(f"Image print error: {e}")
            return False
    
    def print_receipt(self, image_path: str, cut: bool = True):
        """Print a receipt image with proper formatting"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            # Reset printer settings
            self.set_align(self.ALIGN_CENTER)
            self.set_bold(False)
            self.set_text_size(1, 1)
            
            # Print the image
            success = self.print_image(image_path)
            
            if success and cut:
                # Feed some lines and cut
                self.feed_lines(3)
                self.cut_paper(self.CUT_PARTIAL)
            
            return success
            
        except Exception as e:
            print(f"Receipt print error: {e}")
            return False
    
    def __del__(self):
        """Cleanup on destruction"""
        self.disconnect()


# Test function
if __name__ == "__main__":
    # Example usage - USB interface
    printer = ThermalPrinter(port=0, baudrate=19200, interface='USB')
    
    if printer.connect():
        # Test text printing
        printer.set_align(printer.ALIGN_CENTER)
        printer.set_text_size(2, 2)
        printer.print_line("HMK-072 프린터 테스트")
        
        printer.set_text_size(1, 1)
        printer.print_line("="*32)
        printer.print_line("한글 출력 테스트")
        printer.print_line("English Text Test")
        printer.print_line("="*32)
        
        # Feed and cut
        printer.feed_lines(3)
        printer.cut_paper(printer.CUT_PARTIAL)
        
        printer.disconnect()
    else:
        print("Failed to connect to printer")