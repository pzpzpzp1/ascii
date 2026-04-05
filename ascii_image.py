"""
AsciiImage class for storing and rendering ASCII art.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, Callable
import characters


class AsciiImage:
    """
    Represents an ASCII art image as a 2D array of characters.
    """

    def __init__(self, char_array: np.ndarray):
        """
        Initialize an AsciiImage with a 2D array of characters.

        Args:
            char_array: 2D numpy array of single-character strings
        """
        self.char_array = char_array
        self.height, self.width = char_array.shape

    def save(self, outname: str, font_size: int = 12, bg_color=(255, 255, 255),
             text_color=(0, 0, 0)):
        """
        Render the ASCII image as a PNG and save it.

        Args:
            outname: Output filename for the PNG
            font_size: Size of the monospace font to use
            bg_color: Background color tuple (R, G, B)
            text_color: Text color tuple (R, G, B)
        """
        # Try to load a monospace font, fall back to default if unavailable
        try:
            # Common monospace font paths
            font_paths = [
                "/System/Library/Fonts/Courier.dfont",  # macOS
                "/Library/Fonts/Courier New.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
                "C:\\Windows\\Fonts\\consola.ttf",  # Windows
                "C:\\Windows\\Fonts\\cour.ttf",  # Windows
            ]

            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break

            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # Calculate character dimensions
        # Use a test character to determine size
        test_img = Image.new('RGB', (100, 100))
        test_draw = ImageDraw.Draw(test_img)
        bbox = test_draw.textbbox((0, 0), 'M', font=font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        # Create image with appropriate size
        img_width = self.width * char_width
        img_height = self.height * char_height
        image = Image.new('RGB', (img_width, img_height), color=bg_color)
        draw = ImageDraw.Draw(image)

        # Draw each character
        for y in range(self.height):
            for x in range(self.width):
                char = self.char_array[y, x]
                pos_x = x * char_width
                pos_y = y * char_height
                draw.text((pos_x, pos_y), char, fill=text_color, font=font)

        # Save the image
        os.makedirs(os.path.dirname(outname) if os.path.dirname(outname) else '.', exist_ok=True)
        image.save(outname)

    @classmethod
    def from_image(cls, img: Image.Image, scale: float, method: str, **misc_args):
        """
        Convert a PIL Image to an AsciiImage.

        Args:
            img: PIL Image to convert
            scale: Scale factor to resize image before conversion
            method: Method name for conversion (e.g., 'greedy_iou')
            **misc_args: Additional arguments specific to the method

        Returns:
            AsciiImage instance
        """
        from methods import get_method

        # Get the conversion method
        conversion_func = get_method(method)

        # Apply the method to convert image to ASCII
        char_array = conversion_func(img, scale, **misc_args)

        return cls(char_array)

    def __str__(self):
        """Return string representation of the ASCII art."""
        return '\n'.join(''.join(row) for row in self.char_array)

    def to_text_file(self, filename: str):
        """Save ASCII art to a text file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(self))
