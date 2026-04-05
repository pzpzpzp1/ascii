"""
Quick demo script to test ASCII art conversion on a single image.
"""
from PIL import Image
from ascii_image import AsciiImage
import os


def main():
    # Find a test image
    test_images_dir = 'test images'
    test_images = [f for f in os.listdir(test_images_dir) if f.endswith('.png')]

    if not test_images:
        print("No test images found!")
        return

    # Use the first test image
    img_path = os.path.join(test_images_dir, test_images[0])
    print(f"Converting: {img_path}")

    # Load image
    img = Image.open(img_path)

    # Convert to ASCII
    ascii_art = AsciiImage.from_image(
        img,
        scale=0.5,
        method='greedy_iou',
        percentile=50,
        char_set='extended',
        char_width=8,
        char_height=16
    )

    # Create output directory
    os.makedirs('demo_output', exist_ok=True)

    # Save as PNG
    output_path = 'demo_output/demo_result.png'
    ascii_art.save(output_path)
    print(f"Saved to: {output_path}")

    # Also save as text
    text_path = 'demo_output/demo_result.txt'
    ascii_art.to_text_file(text_path)
    print(f"Text version saved to: {text_path}")

    # Print a preview
    print("\nASCII Preview (first 20 lines):")
    print("-" * 60)
    lines = str(ascii_art).split('\n')
    for line in lines[:20]:
        print(line)
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")


if __name__ == "__main__":
    main()
