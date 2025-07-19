"""Convert images to bitmap format for thermal printer"""

from PIL import Image
import os

def convert_to_bitmap(input_path: str, output_path: str = None) -> str:
    """Convert image to 1-bit BMP format for thermal printer
    
    Args:
        input_path: Path to input image (PNG, JPG, etc.)
        output_path: Path for output BMP (optional)
        
    Returns:
        Path to the created bitmap file
    """
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}.bmp"
    
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert to grayscale first
        img_gray = img.convert('L')
        
        # Convert to 1-bit (black and white)
        img_bw = img_gray.point(lambda x: 0 if x < 128 else 255, '1')
        
        # Save as BMP
        img_bw.save(output_path, 'BMP')
        
        print(f"Converted to bitmap: {output_path}")
        print(f"Size: {img_bw.size}")
        print(f"Mode: {img_bw.mode}")
        
        return output_path
        
    except Exception as e:
        print(f"Error converting to bitmap: {e}")
        return None

def create_test_bitmap():
    """Create a simple test bitmap"""
    # Create a simple black and white image
    img = Image.new('1', (384, 200), 1)  # 384 is common thermal printer width
    
    # Draw some test content
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Draw rectangle border
    draw.rectangle([0, 0, 383, 199], outline=0, width=2)
    
    # Draw text (will use default font)
    draw.text((192, 50), "THERMAL PRINTER TEST", anchor="mm", fill=0)
    draw.text((192, 100), "HMK-072", anchor="mm", fill=0)
    draw.text((192, 150), "Bitmap Mode", anchor="mm", fill=0)
    
    # Save
    img.save("test_thermal.bmp", "BMP")
    print("Created test_thermal.bmp")
    return "test_thermal.bmp"

if __name__ == "__main__":
    # Create test bitmap
    test_bmp = create_test_bitmap()
    
    # Convert existing images
    if os.path.exists("thermal_print.png"):
        convert_to_bitmap("thermal_print.png", "thermal_print.bmp")
    
    if os.path.exists("test_thermal_print.png"):
        convert_to_bitmap("test_thermal_print.png", "test_thermal_print.bmp")