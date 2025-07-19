from PIL import Image, ImageDraw, ImageFont
import json
import os
import platform

# Import thermal printer only on Windows
if platform.system() == 'Windows':
    try:
        from thermal_printer import ThermalPrinter
    except ImportError:
        ThermalPrinter = None
else:
    ThermalPrinter = None

class ReceiptPrinter:
    def __init__(self, font_path=None, enable_thermal=True):
        """Initialize the receipt printer with font settings"""
        self.base_font_size = 36  # 3 times bigger (12 * 3)
        self.name_x = 302  # Right align position
        self.name_y = 66   # Bottom baseline position (moved down by 12 pixels from 54)
        self.max_width = 162  # Maximum text width
        self.bounding_x = 140  # Bounding box start x
        
        # Font settings
        if font_path and os.path.exists(font_path):
            self.font_path = font_path
        else:
            # Use the font from res folder
            self.font_path = "res/NotoSansKR-Medium.ttf"
            
            if not os.path.exists(self.font_path):
                print(f"Error: Font file not found at {self.font_path}")
                self.font_path = None
            else:
                print(f"Using font: {self.font_path}")
        
        # Initialize thermal printer on Windows
        self.thermal_printer = None
        if enable_thermal and platform.system() == 'Windows' and ThermalPrinter:
            try:
                # Use USB interface with port 0
                self.thermal_printer = ThermalPrinter(port=0, baudrate=19200, interface='USB')
                print("Thermal printer initialized")
            except Exception as e:
                print(f"Failed to initialize thermal printer: {e}")
    
    def get_optimal_font_size(self, name, max_width):
        """Calculate optimal font size to fit text within max_width"""
        font_size = self.base_font_size
        
        while font_size > 6:  # Minimum font size
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, font_size)
                else:
                    font = ImageFont.load_default()
                    return font  # Default font doesn't support size adjustment
                
                # Get text width
                bbox = font.getbbox(name)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    return font
                
                font_size -= 1
            except Exception as e:
                print(f"Error loading font size {font_size}: {e}")
                font_size -= 1
        
        # Return smallest size if nothing fits
        if self.font_path:
            return ImageFont.truetype(self.font_path, 6)
        else:
            return ImageFont.load_default()
    
    def add_name_to_receipt(self, data, output_path="thermal_print.png"):
        """Add customer name to pre-made receipt image"""
        
        # Extract data
        name = data.get('이름', '고객')
        type_number = data.get('번호', '1')  # Get type number, default to 1
        
        # Load the corresponding receipt image
        receipt_path = f"res/receipt/{type_number}.png"
        if not os.path.exists(receipt_path):
            print(f"Warning: Receipt image not found at {receipt_path}, using default")
            receipt_path = "res/receipt/1.png"  # Default to type 1
            
        try:
            # Open the receipt image
            img = Image.open(receipt_path)
            draw = ImageDraw.Draw(img)
            
            # Get optimal font size
            font = self.get_optimal_font_size(name, self.max_width)
            
            # Use name as is (don't add "님")
            full_name = name
            
            # Get text dimensions
            bbox = font.getbbox(full_name)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position (right-aligned at x=302, baseline at y=44)
            # Right align: text should end at x=302
            text_x = self.name_x - text_width
            
            # Baseline positioning: adjust y position based on font metrics
            # PIL draws from top-left, so we need to adjust for baseline
            text_y = self.name_y - text_height
            
            # Ensure text doesn't go beyond bounding box
            if text_x < self.bounding_x:
                text_x = self.bounding_x
            
            # Draw the text
            draw.text((text_x, text_y), full_name, font=font, fill='black')
            
            # Save the modified image
            img.save(output_path, 'PNG')
            print(f"Receipt saved to: {output_path}")
            print(f"Used type {type_number} receipt, added name: {full_name}")
            
            # Print to thermal printer if available
            if self.thermal_printer:
                self.print_to_thermal(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing receipt: {e}")
            return None
    
    def print_to_thermal(self, image_path: str) -> bool:
        """Send the receipt image to the thermal printer"""
        if not self.thermal_printer:
            print("Thermal printer not available")
            return False
        
        try:
            print("Sending to thermal printer...")
            success = self.thermal_printer.print_receipt(image_path, cut=True)
            if success:
                print("Receipt printed successfully!")
            else:
                print("Failed to print receipt")
            return success
        except Exception as e:
            print(f"Thermal printing error: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Test data
    test_data = {
        "이름": "김치맛강정은별로야",
        "번호": "3",
        "타입명": "Future Seeker",
        "타입_설명": "시대의 흐름을 꿰뚫어 보고, 자신만의 방식으로 새로운 유행을 만들어가는 마케터.",
        "성향_키워드": "#전략적 #넓은시야 #영감",
        "음료": "Negroni",
        "푸드": "아보카도 리코타 치즈 토스트"
    }
    
    printer = ReceiptPrinter()
    printer.add_name_to_receipt(test_data)