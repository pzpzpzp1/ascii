"""
Evaluation pipeline for ASCII art conversion methods.

This script runs all configured methods on all test images and generates
comprehensive visualizations showing each stage of the conversion process.
"""
import json
import os
import glob
import yaml
import numpy as np
from PIL import Image
from ascii_image import AsciiImage

_IMAGE_CONFIG_DEFAULTS = {'scale': 1.0, 'percentile': 50}


def _get_image_config(img_path: str) -> dict:
    """
    Read per-image config from a sidecar .json file next to the image.
    Creates the file with defaults if missing. Returns dict with 'scale' and 'percentile'.
    """
    base = os.path.splitext(img_path)[0]
    json_path = base + '.json'
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump(_IMAGE_CONFIG_DEFAULTS, f, indent=2)
        return dict(_IMAGE_CONFIG_DEFAULTS)
    with open(json_path, 'r') as f:
        data = json.load(f)
    for k, v in _IMAGE_CONFIG_DEFAULTS.items():
        data.setdefault(k, v)
    return data


def _open_rgb(path: str) -> Image.Image:
    """Open an image and composite any alpha channel onto white before returning RGB."""
    img = Image.open(path)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert('RGB')


def create_visualization(img_path: str, method_name: str, method_func: str,
                         scale: float, misc_args: dict, output_dir: str):
    """
    Create a visualization showing all stages of ASCII conversion.

    Panels (left to right): original | grayscale | threshold | ASCII render
    All panels use the full image at the given scale, preserving aspect ratio.

    Args:
        img_path: Path to input image
        method_name: Name of the method for output naming
        method_func: Name of the conversion method
        scale: Scale factor
        misc_args: Additional method arguments
        output_dir: Directory to save output
    """
    img = _open_rgb(img_path)

    img_config = _get_image_config(img_path)
    scale = scale * img_config['scale']
    percentile = img_config['percentile']
    misc_args = {**misc_args, 'percentile': percentile}

    # Scale the full image (no cropping)
    scaled = img.resize(
        (int(img.size[0] * scale), int(img.size[1] * scale)),
        Image.Resampling.LANCZOS
    )

    gray_img = scaled.convert('L')
    gray_array = np.array(gray_img)

    # Panel 2: threshold
    interesting = gray_array[(gray_array > 0) & (gray_array < 255)]
    threshold = np.percentile(interesting, percentile) if interesting.size > 0 else 128
    binary_array = (gray_array < threshold).astype(np.uint8) * 255
    threshold_img = Image.fromarray(binary_array).convert('RGB')

    ascii_img = AsciiImage.from_image(img, scale, method_func, **misc_args)
    temp_ascii_path = os.path.join(output_dir, 'temp_ascii.png')
    ascii_img.save(temp_ascii_path)
    ascii_render = Image.open(temp_ascii_path).convert('RGB')

    panels = [scaled, threshold_img, ascii_render]
    max_w = max(p.size[0] for p in panels)
    max_h = max(p.size[1] for p in panels)

    arrays = []
    for panel in panels:
        canvas = Image.new('RGB', (max_w, max_h), (255, 255, 255))
        canvas.paste(panel, ((max_w - panel.size[0]) // 2, (max_h - panel.size[1]) // 2))
        arrays.append(np.array(canvas, dtype=np.float32))

    overlaid = Image.fromarray(np.mean(arrays, axis=0).clip(0, 255).astype(np.uint8))

    img_basename = os.path.splitext(os.path.basename(img_path))[0]
    output_path = os.path.join(output_dir, f'{img_basename}_visualization.png')
    overlaid.save(output_path)

    # Save ASCII as text file
    txt_path = os.path.join(output_dir, f'{img_basename}_visualization.txt')
    ascii_img.to_text_file(txt_path)

    # Clean up temp file
    if os.path.exists(temp_ascii_path):
        os.remove(temp_ascii_path)

    print(f"  ✓ Created visualization: {output_path}")


def run_evaluation():
    """
    Run the full evaluation pipeline on all test images and methods.
    """
    print("="*60)
    print("ASCII Art Evaluation Pipeline")
    print("="*60)

    # Load methods configuration
    config_path = 'methods_config.yaml'
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' not found!")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    methods = config.get('methods', [])
    if not methods:
        print("Error: No methods defined in configuration!")
        return

    print(f"\nLoaded {len(methods)} method configurations")

    # Find all test images
    test_images_dir = 'test images'
    if not os.path.exists(test_images_dir):
        print(f"Error: Test images directory '{test_images_dir}' not found!")
        return

    test_images = glob.glob(os.path.join(test_images_dir, '*.png'))
    test_images.extend(glob.glob(os.path.join(test_images_dir, '*.jpg')))
    test_images.extend(glob.glob(os.path.join(test_images_dir, '*.jpeg')))

    if not test_images:
        print(f"Error: No test images found in '{test_images_dir}'!")
        return

    print(f"Found {len(test_images)} test images\n")

    # Process each method
    for i, method_config in enumerate(methods, 1):
        method_name = method_config['name']
        method_func = method_config['method']
        scale = method_config['scale']
        misc_args = method_config.get('misc_args', {})

        print(f"\n[{i}/{len(methods)}] Processing method: {method_name}")
        print(f"  Method: {method_func}")
        print(f"  Scale: {scale}")
        print(f"  Args: {misc_args}")

        # Create output directory for this method
        output_dir = os.path.join('output', method_name)
        os.makedirs(output_dir, exist_ok=True)

        # Process each test image
        for j, img_path in enumerate(test_images, 1):
            img_name = os.path.basename(img_path)
            print(f"  [{j}/{len(test_images)}] Processing: {img_name}")

            try:
                create_visualization(
                    img_path=img_path,
                    method_name=method_name,
                    method_func=method_func,
                    scale=scale,
                    misc_args=misc_args,
                    output_dir=output_dir
                )
            except Exception as e:
                print(f"  ✗ Error processing {img_name}: {str(e)}")

    print("\n" + "="*60)
    print("Evaluation complete!")
    print(f"Results saved to: output/")
    print("="*60)


if __name__ == "__main__":
    run_evaluation()
