from PIL import Image
from io import BytesIO

def process_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    return "This is an image of a crop field."  # placeholder
