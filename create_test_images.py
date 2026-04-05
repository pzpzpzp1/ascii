"""
Script to generate sample test images for ASCII art conversion testing.
Creates images of varying sizes with different patterns.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_images():
    output_dir = "test images"
    os.makedirs(output_dir, exist_ok=True)

    # Image 1: Simple gradient (small)
    img1 = Image.new('RGB', (100, 100))
    draw1 = ImageDraw.Draw(img1)
    for y in range(100):
        intensity = int(255 * y / 100)
        draw1.rectangle([(0, y), (100, y+1)], fill=(intensity, intensity, intensity))
    img1.save(f"{output_dir}/gradient_small.png")

    # Image 2: Checkerboard pattern (medium)
    img2 = Image.new('RGB', (200, 200))
    draw2 = ImageDraw.Draw(img2)
    square_size = 20
    for i in range(0, 200, square_size):
        for j in range(0, 200, square_size):
            if (i // square_size + j // square_size) % 2 == 0:
                draw2.rectangle([(i, j), (i+square_size, j+square_size)], fill=(0, 0, 0))
            else:
                draw2.rectangle([(i, j), (i+square_size, j+square_size)], fill=(255, 255, 255))
    img2.save(f"{output_dir}/checkerboard_medium.png")

    # Image 3: Circle (medium)
    img3 = Image.new('RGB', (300, 300), color=(255, 255, 255))
    draw3 = ImageDraw.Draw(img3)
    draw3.ellipse([(50, 50), (250, 250)], fill=(0, 0, 0))
    img3.save(f"{output_dir}/circle_medium.png")

    # Image 4: Multiple circles (large)
    img4 = Image.new('RGB', (400, 400), color=(200, 200, 200))
    draw4 = ImageDraw.Draw(img4)
    draw4.ellipse([(50, 50), (150, 150)], fill=(0, 0, 0))
    draw4.ellipse([(200, 50), (350, 200)], fill=(100, 100, 100))
    draw4.ellipse([(100, 250), (300, 350)], fill=(50, 50, 50))
    img4.save(f"{output_dir}/circles_large.png")

    # Image 5: Horizontal stripes (small)
    img5 = Image.new('RGB', (150, 150))
    draw5 = ImageDraw.Draw(img5)
    stripe_height = 15
    for i in range(0, 150, stripe_height):
        color = 255 if (i // stripe_height) % 2 == 0 else 0
        draw5.rectangle([(0, i), (150, i+stripe_height)], fill=(color, color, color))
    img5.save(f"{output_dir}/stripes_small.png")

    # Image 6: Complex pattern (large)
    img6 = Image.new('RGB', (500, 500), color=(255, 255, 255))
    draw6 = ImageDraw.Draw(img6)
    for i in range(0, 500, 50):
        draw6.line([(i, 0), (500, 500-i)], fill=(0, 0, 0), width=2)
        draw6.line([(0, i), (500-i, 500)], fill=(0, 0, 0), width=2)
    img6.save(f"{output_dir}/lines_large.png")

    print("Created 6 test images in 'test images' folder")

if __name__ == "__main__":
    create_test_images()
