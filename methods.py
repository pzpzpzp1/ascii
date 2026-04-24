"""
ASCII art conversion methods and utilities.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple
import characters
import font_utils


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


def render_character_to_array(char: str, width: int, height: int) -> np.ndarray:
    """
    Render a single character as a binary numpy array.

    Args:
        char: Character to render
        width: Width of output array
        height: Height of output array

    Returns:
        Binary numpy array (0 or 1) representing the character
    """
    img = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(img)
    font = font_utils.load_font()
    draw.text((0, 0), char, fill=0, font=font)

    # Convert to numpy array and threshold
    arr = np.array(img)
    binary_arr = (arr < 128).astype(np.uint8)

    return binary_arr


def calculate_iou(arr1: np.ndarray, arr2: np.ndarray) -> float:
    """
    Generalized IOU for continuous ink values in [0,1] (0=white, 1=black).
    Reduces to standard binary IOU when inputs are binary.
    """
    intersection = np.minimum(arr1, arr2).sum()
    union        = np.maximum(arr1, arr2).sum()
    return (intersection / union) if union > 0 else 1.0


def calculate_white_weighted_iou(arr1: np.ndarray, arr2: np.ndarray, white_weight: float = 2.0) -> float:
    """
    Convex blend of IOU (ink matching) and white accuracy (white matching), generalized to [0,1] ink values.
    alpha = white_weight / (1 + white_weight)
    score = (1 - alpha) * iou + alpha * white_acc
    """
    intersection = np.minimum(arr1, arr2).sum()
    union        = np.maximum(arr1, arr2).sum()
    both_white   = (1.0 - np.maximum(arr1, arr2)).sum()

    iou       = (intersection / union) if union > 0 else 1.0
    white_acc = both_white / arr1.size

    alpha = white_weight / (1.0 + white_weight)
    return (1.0 - alpha) * iou + alpha * white_acc


def greedy_iou_method(img: Image.Image, scale: float, percentile: float = 50,
                      char_set: str = 'extended', char_width: int = 7,
                      char_height: int = 15) -> np.ndarray:
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
    new_width = int(img.size[0] * scale)
    new_height = int(img.size[1] * scale)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center-crop to exact char-cell multiples so the render is pixel-identical in size
    crop_w = (new_width // char_width) * char_width
    crop_h = (new_height // char_height) * char_height
    left = (new_width - crop_w) // 2
    top  = (new_height - crop_h) // 2
    img = img.crop((left, top, left + crop_w, top + crop_h))

    # ink_img: 0.0 = white (no ink), 1.0 = black (full ink)
    ink_img = 1.0 - np.array(img.convert('L'), dtype=np.float32) / 255.0

    grid_height = crop_h // char_height
    grid_width  = crop_w // char_width

    char_list = characters.get_character_list(char_set)
    char_renders = {char: render_character_to_array(char, char_width, char_height).astype(np.float32)
                    for char in char_list}

    result = np.empty((grid_height, grid_width), dtype=object)

    for y in range(grid_height):
        for x in range(grid_width):
            y_start = y * char_height
            y_end   = y_start + char_height
            x_start = x * char_width
            x_end   = x_start + char_width

            patch = ink_img[y_start:y_end, x_start:x_end]

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
                                     char_set: str = 'insta', char_width: int = 7,
                                     char_height: int = 15, white_weight: float = 2.0) -> np.ndarray:
    """
    Greedy IOU matching with white-pixel upweighting.
    White pixel matches count white_weight times more than black matches.
    """
    new_width = int(img.size[0] * scale)
    new_height = int(img.size[1] * scale)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center-crop to exact char-cell multiples so the render is pixel-identical in size
    crop_w = (new_width // char_width) * char_width
    crop_h = (new_height // char_height) * char_height
    left = (new_width - crop_w) // 2
    top  = (new_height - crop_h) // 2
    img = img.crop((left, top, left + crop_w, top + crop_h))

    # ink_img: 0.0 = white (no ink), 1.0 = black (full ink)
    ink_img = 1.0 - np.array(img.convert('L'), dtype=np.float32) / 255.0

    grid_height = crop_h // char_height
    grid_width  = crop_w // char_width

    char_list = characters.get_character_list(char_set)
    char_renders = {char: render_character_to_array(char, char_width, char_height).astype(np.float32)
                    for char in char_list}

    result = np.empty((grid_height, grid_width), dtype=object)

    for y in range(grid_height):
        for x in range(grid_width):
            y_start = y * char_height
            y_end   = y_start + char_height
            x_start = x * char_width
            x_end   = x_start + char_width
            patch = ink_img[y_start:y_end, x_start:x_end]

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
