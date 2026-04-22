"""
Generate a clean binary test image from randomly-sampled insta_tutorial characters.

The image is built directly from render_character_to_array outputs (not from
AsciiImage.save) so every pixel is exactly 0 or 255 — no antialiasing.
This means the eval threshold always falls back to 128 (no 'interesting' pixels),
which matches the threshold used inside render_character_to_array, guaranteeing
0-loss round-trip when verified.

Grid: 11 rows × 7 cols. Sidecar sets scale=2.0 so eval's 0.5 × 2.0 = 1.0
effective scale, preserving the image at its natural size.
"""
import json
import random
import numpy as np
from PIL import Image
import characters
from methods import render_character_to_array

ROWS, COLS = 11, 7
CW, CH = 7, 15
SEED = 42

random.seed(SEED)

char_list = characters.get_character_list('insta_tutorial')
print(f"Character set ({len(char_list)}): {''.join(char_list)!r}")

test_chars = [[random.choice(char_list) for _ in range(COLS)] for _ in range(ROWS)]

# Assemble from binary render arrays — no antialiasing
img_arr = np.full((ROWS * CH, COLS * CW), 255, dtype=np.uint8)
for r, row in enumerate(test_chars):
    for c, char in enumerate(row):
        arr = render_character_to_array(char, CW, CH)  # 1 = black pixel
        img_arr[r*CH:(r+1)*CH, c*CW:(c+1)*CW] = (1 - arr) * 255

img = Image.fromarray(img_arr, 'L').convert('RGB')
img_path = 'test images/random_test.png'
img.save(img_path)
print(f"Saved {img.size[0]}x{img.size[1]} image to {img_path}")

# Sidecar: scale=2.0 so effective eval scale = 0.5*2.0 = 1.0
with open('test images/random_test.json', 'w') as f:
    json.dump({'scale': 2.0, 'percentile': 50}, f, indent=2)

# Reference char array
ref_path = 'test images/random_test_reference.txt'
with open(ref_path, 'w', encoding='utf-8') as f:
    for row in test_chars:
        f.write(''.join(row) + '\n')

print(f"Reference saved to {ref_path}")
print("Grid:")
for row in test_chars:
    print(' ', ''.join(row))
