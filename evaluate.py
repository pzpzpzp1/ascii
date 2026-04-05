"""
Evaluation pipeline for ASCII art conversion methods.

This script runs all configured methods on all test images and generates
comprehensive visualizations showing each stage of the conversion process.
"""
import os
import glob
import yaml
import numpy as np
from PIL import Image
from ascii_image import AsciiImage
from methods import center_crop_to_ascii_ratio


def create_visualization(img_path: str, method_name: str, method_func: str,
                         scale: float, misc_args: dict, output_dir: str):
    """
    Create a visualization showing all stages of ASCII conversion.

    Args:
        img_path: Path to input image
        method_name: Name of the method for output naming
        method_func: Name of the conversion method
        scale: Scale factor
        misc_args: Additional method arguments
        output_dir: Directory to save output
    """
    # Load image
    img = Image.open(img_path).convert('RGB')

    # Step 1: Center crop
    char_aspect = misc_args.get('char_width', 8) / misc_args.get('char_height', 16)
    cropped_img = center_crop_to_ascii_ratio(img, char_aspect_ratio=char_aspect)

    # Resize for visualization consistency
    new_width = int(cropped_img.size[0] * scale)
    new_height = int(cropped_img.size[1] * scale)
    cropped_resized = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Step 2: Grayscale
    gray_img = cropped_resized.convert('L')
    gray_rgb = gray_img.convert('RGB')  # Convert back to RGB for concatenation

    # Step 3: Thresholded image
    gray_array = np.array(gray_img)
    percentile = misc_args.get('percentile', 50)
    threshold = np.percentile(gray_array, percentile)
    binary_array = (gray_array < threshold).astype(np.uint8) * 255
    threshold_img = Image.fromarray(binary_array).convert('RGB')

    # Step 4: Generate ASCII art
    ascii_img = AsciiImage.from_image(img, scale, method_func, **misc_args)

    # Save ASCII render
    temp_ascii_path = os.path.join(output_dir, 'temp_ascii.png')
    ascii_img.save(temp_ascii_path, font_size=12)

    # Load the rendered ASCII image
    ascii_render = Image.open(temp_ascii_path).convert('RGB')

    # Resize all images to same height for concatenation
    target_height = cropped_resized.size[1]

    def resize_to_height(img, target_h):
        aspect = img.size[0] / img.size[1]
        new_w = int(target_h * aspect)
        return img.resize((new_w, target_h), Image.Resampling.LANCZOS)

    cropped_resized = resize_to_height(cropped_resized, target_height)
    gray_rgb = resize_to_height(gray_rgb, target_height)
    threshold_img = resize_to_height(threshold_img, target_height)
    ascii_render = resize_to_height(ascii_render, target_height)

    # Create red separator bar (2 pixels wide)
    separator_width = 2
    separator = Image.new('RGB', (separator_width, target_height), color=(255, 0, 0))

    # Concatenate images horizontally with red separators
    images = [cropped_resized, separator, gray_rgb, separator, threshold_img, separator, ascii_render]
    total_width = sum(img.size[0] for img in images)

    concatenated = Image.new('RGB', (total_width, target_height))
    x_offset = 0
    for img in images:
        concatenated.paste(img, (x_offset, 0))
        x_offset += img.size[0]

    # Save the concatenated result
    img_basename = os.path.splitext(os.path.basename(img_path))[0]
    output_path = os.path.join(output_dir, f'{img_basename}_visualization.png')
    concatenated.save(output_path)

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
