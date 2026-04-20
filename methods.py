"""
ASCII art conversion methods and utilities.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple
import characters


def center_crop_to_ascii_ratio(img: Image.Image, char_aspect_ratio: float = 0.5) -> Image.Image:
    """
    Center-crop an image to an aspect ratio suitable for ASCII text rendering.

    Args:
        img: Input PIL Image
        char_aspect_ratio: Width/height ratio of individual characters (typically ~0.5 for monospace)

    Returns:
        Center-cropped PIL Image

    Note:
        Most monospace fonts have characters that are roughly twice as tall as they are wide.
        To make ASCII art appear with correct proportions, we need to account for this.
        If we want a square-looking ASCII output, we crop to width:height = 2:1 image.
    """
    width, height = img.size
    target_ratio = char_aspect_ratio

    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is too wide, crop width
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        # Image is too tall, crop height
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    return img


def render_character_to_array(char: str, width: int, height: int, font_size: int = 12) -> np.ndarray:
    """
    Render a single character as a binary numpy array.

    Args:
        char: Character to render
        width: Width of output array
        height: Height of output array
        font_size: Font size to use

    Returns:
        Binary numpy array (0 or 1) representing the character
    """
    # Create a small image to render the character
    img = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(img)

    font_paths = [
        "fonts/Menlo.ttc",
        "/System/Library/Fonts/Menlo.ttc",
        "fonts/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
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

    # Draw at natural top-left anchor — matches how save() positions each character
    draw.text((0, 0), char, fill=0, font=font)

    # Convert to numpy array and threshold
    arr = np.array(img)
    binary_arr = (arr < 128).astype(np.uint8)

    return binary_arr


def calculate_iou(arr1: np.ndarray, arr2: np.ndarray) -> float:
    """
    Calculate Intersection over Union between two binary arrays.
    """
    intersection = np.logical_and(arr1, arr2).sum()
    union = np.logical_or(arr1, arr2).sum()

    if union == 0:
        return 1.0  # both arrays empty — perfect match (space character)

    return intersection / union


def calculate_white_weighted_iou(arr1: np.ndarray, arr2: np.ndarray, white_weight: float = 2.0) -> float:
    """
    Convex blend of standard IOU (black matching) and white-pixel accuracy (white matching).
    alpha = white_weight / (1 + white_weight), so higher white_weight shifts weight toward white accuracy.
    score = (1 - alpha) * iou + alpha * white_acc
    """
    intersection = np.logical_and(arr1, arr2).sum()
    union = np.logical_or(arr1, arr2).sum()
    both_white = arr1.size - union

    iou = (intersection / union) if union > 0 else 1.0
    white_acc = both_white / arr1.size

    alpha = white_weight / (1.0 + white_weight)
    return (1.0 - alpha) * iou + alpha * white_acc


def greedy_iou_method(img: Image.Image, scale: float, percentile: float = 50,
                      char_set: str = 'extended', char_width: int = 8,
                      char_height: int = 16) -> np.ndarray:
    """
    Convert image to ASCII using greedy pixel-wise IOU matching.

    Args:
        img: Input PIL Image
        scale: Scale factor for resizing
        percentile: Percentile for thresholding (0-100)
        char_set: Character set to use ('minimal', 'standard', 'extended', 'all')
        char_width: Width of character cells in pixels
        char_height: Height of character cells in pixels

    Returns:
        2D numpy array of characters
    """
    # Step 1: Resize image based on scale
    new_width = int(img.size[0] * scale)
    new_height = int(img.size[1] * scale)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    gray_array = np.array(img.convert('L'))
    interesting = gray_array[(gray_array > 0) & (gray_array < 255)]
    threshold = np.percentile(interesting, percentile) if interesting.size > 0 else 128
    binary_img = (gray_array < threshold).astype(np.uint8)

    # Step 6: Calculate grid dimensions
    grid_height = new_height // char_height
    grid_width = new_width // char_width

    # Step 7: Pre-render all characters in the character set
    char_list = characters.get_character_list(char_set)
    char_renders = {}
    for char in char_list:
        char_renders[char] = render_character_to_array(char, char_width, char_height)

    # Step 8: Greedy matching - find best character for each grid cell
    result = np.empty((grid_height, grid_width), dtype=object)

    for y in range(grid_height):
        for x in range(grid_width):
            # Extract the image patch for this grid cell
            y_start = y * char_height
            y_end = min((y + 1) * char_height, new_height)
            x_start = x * char_width
            x_end = min((x + 1) * char_width, new_width)

            patch = binary_img[y_start:y_end, x_start:x_end]

            # Resize patch to char dimensions if needed
            if patch.shape != (char_height, char_width):
                patch_img = Image.fromarray((patch * 255).astype(np.uint8))
                patch_img = patch_img.resize((char_width, char_height), Image.Resampling.NEAREST)
                patch = (np.array(patch_img) > 128).astype(np.uint8)

            # Find best matching character
            best_char = ' '
            best_iou = -1

            for char, char_render in char_renders.items():
                iou = calculate_iou(patch, char_render)
                if iou > best_iou:
                    best_iou = iou
                    best_char = char

            result[y, x] = best_char

    return result


def greedy_iou_white_weighted_method(img: Image.Image, scale: float, percentile: float = 50,
                                     char_set: str = 'insta', char_width: int = 8,
                                     char_height: int = 16, white_weight: float = 2.0) -> np.ndarray:
    """
    Greedy IOU matching with white-pixel upweighting.
    White pixel matches count white_weight times more than black matches.
    """
    new_width = int(img.size[0] * scale)
    new_height = int(img.size[1] * scale)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    gray_array = np.array(img.convert('L'))
    interesting = gray_array[(gray_array > 0) & (gray_array < 255)]
    threshold = np.percentile(interesting, percentile) if interesting.size > 0 else 128
    binary_img = (gray_array < threshold).astype(np.uint8)

    grid_height = new_height // char_height
    grid_width = new_width // char_width

    char_list = characters.get_character_list(char_set)
    char_renders = {char: render_character_to_array(char, char_width, char_height)
                    for char in char_list}

    result = np.empty((grid_height, grid_width), dtype=object)

    for y in range(grid_height):
        for x in range(grid_width):
            y_start, y_end = y * char_height, min((y + 1) * char_height, new_height)
            x_start, x_end = x * char_width, min((x + 1) * char_width, new_width)
            patch = binary_img[y_start:y_end, x_start:x_end]

            if patch.shape != (char_height, char_width):
                patch_img = Image.fromarray((patch * 255).astype(np.uint8))
                patch_img = patch_img.resize((char_width, char_height), Image.Resampling.NEAREST)
                patch = (np.array(patch_img) > 128).astype(np.uint8)

            best_char = ' '
            best_score = -1
            for char, char_render in char_renders.items():
                score = calculate_white_weighted_iou(patch, char_render, white_weight)
                if score > best_score:
                    best_score = score
                    best_char = char

            result[y, x] = best_char

    return result


# Registry of available methods
METHODS = {
    'greedy_iou': greedy_iou_method,
    'greedy_iou_white_weighted': greedy_iou_white_weighted_method,
}


def get_method(method_name: str):
    """
    Get a conversion method by name.

    Args:
        method_name: Name of the method

    Returns:
        Method function

    Raises:
        ValueError: If method name is not found
    """
    if method_name not in METHODS:
        raise ValueError(f"Unknown method '{method_name}'. Available: {list(METHODS.keys())}")

    return METHODS[method_name]
