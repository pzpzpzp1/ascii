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
        # Load a monospace font — prefer VSCode-style fonts
        font_paths = [
            "/System/Library/Fonts/Menlo.ttc",                          # macOS (VSCode default)
            "/Library/Fonts/Courier New.ttf",                           # macOS
            "/System/Library/Fonts/Courier.dfont",                      # macOS fallback
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",      # Linux
            "C:\\Windows\\Fonts\\consola.ttf",                          # Windows (Consolas)
            "C:\\Windows\\Fonts\\cour.ttf",                             # Windows
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except Exception:
                    continue
        if font is None:
            font = ImageFont.load_default()

        # Fixed cell dimensions: every character occupies exactly cell_w × cell_h pixels,
        # mirroring how a monospace .txt file looks in VSCode.
        ascent, descent = font.getmetrics()
        cell_h = ascent + descent  # already an integer for TrueType fonts

        tmp = Image.new('L', (1, 1))
        cell_w = int(round(ImageDraw.Draw(tmp).textlength('M', font=font)))

        image = Image.new('RGB', (self.width * cell_w, self.height * cell_h), color=bg_color)
        draw = ImageDraw.Draw(image)

        # Render each character into a cell-sized scratch image first, then paste.
        # This clips wide glyphs (e.g. katakana) that would otherwise bleed into
        # the neighbouring cell if drawn directly onto the full image.
        for row_idx in range(self.height):
            for col_idx in range(self.width):
                ch = self.char_array[row_idx, col_idx]
                cell_img = Image.new('RGB', (cell_w, cell_h), color=bg_color)
                ImageDraw.Draw(cell_img).text((0, 0), ch, fill=text_color, font=font)
                image.paste(cell_img, (col_idx * cell_w, row_idx * cell_h))

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
