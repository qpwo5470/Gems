"""Fix thermal printer margins by stretching the image"""

from PIL import Image
import os

class ThermalMarginFixer:
    def __init__(self, left_margin_mm=6.2, right_margin_mm=4.5, dpi=203):
        """Initialize with printer margin measurements
        
        Args:
            left_margin_mm: Left margin in millimeters
            right_margin_mm: Right margin in millimeters  
            dpi: Printer DPI (typically 203 for thermal printers)
        """
        self.left_margin_mm = left_margin_mm
        self.right_margin_mm = right_margin_mm
        self.dpi = dpi
        
        # Convert mm to pixels
        self.left_margin_px = int(left_margin_mm * dpi / 25.4)
        self.right_margin_px = int(right_margin_mm * dpi / 25.4)
        self.total_margin_px = self.left_margin_px + self.right_margin_px
        
        print(f"Margin compensation:")
        print(f"  Left: {self.left_margin_mm}mm = {self.left_margin_px}px")
        print(f"  Right: {self.right_margin_mm}mm = {self.right_margin_px}px")
        print(f"  Total: {self.left_margin_mm + self.right_margin_mm}mm = {self.total_margin_px}px")
    
    def fix_image_for_printing(self, image_path, output_path=None):
        """Adjust image to compensate for printer margins
        
        Args:
            image_path: Path to original image
            output_path: Path for adjusted image (optional)
            
        Returns:
            Path to adjusted image
        """
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            output_path = f"{base}_adjusted.png"
        
        # Open image
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"\nOriginal image: {width}x{height}px")
        
        # Calculate new dimensions
        # The printer will squeeze our image by total_margin_px
        # So we need to make it wider by that amount
        new_width = width + self.total_margin_px
        
        # Create new image with extra width
        new_img = Image.new(img.mode, (new_width, height), 'white')
        
        # Paste original image offset by left margin ratio
        # This distributes the extra width proportionally
        left_offset = int(self.left_margin_px * 1.2)  # Slightly more to compensate
        new_img.paste(img, (left_offset, 0))
        
        print(f"Adjusted image: {new_width}x{height}px")
        print(f"Content offset: {left_offset}px from left")
        
        # Save
        new_img.save(output_path)
        return output_path
    
    def create_test_pattern(self, width=673):
        """Create a test pattern to verify margin compensation"""
        height = 300
        
        # Create test image
        img = Image.new('RGB', (width, height), 'white')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw edge markers in red
        draw.rectangle([0, 0, width-1, height-1], outline='red', width=3)
        
        # Draw center line
        center = width // 2
        draw.line([(center, 0), (center, height)], fill='blue', width=2)
        
        # Draw measurement grid every 50px
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, 20)], fill='black', width=1)
            draw.text((x+2, 25), str(x), fill='black')
        
        # Save original
        img.save('margin_test_original.png')
        print("\nCreated margin_test_original.png")
        
        # Create adjusted version
        adjusted_path = self.fix_image_for_printing('margin_test_original.png', 
                                                   'margin_test_adjusted.png')
        print(f"Created {adjusted_path}")
        
        return adjusted_path


# Example usage
if __name__ == "__main__":
    # Initialize with your measured margins
    fixer = ThermalMarginFixer(left_margin_mm=6.2, right_margin_mm=4.5)
    
    # Create test pattern
    print("Creating test patterns...")
    fixer.create_test_pattern()
    
    # Test with actual receipt
    if os.path.exists('thermal_print.png'):
        print("\nAdjusting receipt image...")
        adjusted = fixer.fix_image_for_printing('thermal_print.png')
        print(f"Adjusted receipt saved as: {adjusted}")