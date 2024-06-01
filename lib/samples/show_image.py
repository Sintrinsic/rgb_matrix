from PIL import Image
from lib.simple_display_client import SimpleDisplayClient
import numpy as np
from PIL import ImageOps


def get_image_pixels(image_path, target_width):
    img = Image.open(image_path).convert('RGB')  # Ensure image is in RGB format
    # Rotate the image 90 degrees clockwise
    img = ImageOps.mirror(img)
    img = img.rotate(90, expand=True)

    pixels = np.array(img)
    print(pixels.shape)



    # Calculate the target height to maintain the aspect ratio
    aspect_ratio = img.height / img.width
    print(aspect_ratio)
    target_height = int(target_width / aspect_ratio)
    print(target_height)
    # Resize the image to the target width and calculated height
    img = img.resize((target_height, target_width), Image.LANCZOS)

    # Convert to NumPy array
    pixels = np.array(img)
    print(pixels.shape)

    return pixels
def main():
    client = SimpleDisplayClient(('192.168.1.62', 12345))
    image_pixels = get_image_pixels('media/pixel_image.png',64)
    client.send_matrix(image_pixels)
    client.close()

if __name__ == "__main__":
    main()