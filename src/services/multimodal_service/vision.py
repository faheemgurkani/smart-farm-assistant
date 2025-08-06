from PIL import Image
from io import BytesIO

def process_image(image_bytes):
    """Process image and return basic information for debugging"""
    try:
        image = Image.open(BytesIO(image_bytes))
        return f"Image processed successfully. Size: {image.size}, Mode: {image.mode}, Format: {image.format}"
    except Exception as e:
        return f"Error processing image: {str(e)}"

def get_image_info(image_bytes):
    """Get basic image information"""
    try:
        image = Image.open(BytesIO(image_bytes))
        return {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
            "width": image.width,
            "height": image.height
        }
    except Exception as e:
        return {"error": str(e)}
