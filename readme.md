# ASCII Art Conversion

Image to ASCII art converter with method evaluation framework.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Demo

Test the conversion on a single image:

```bash
python3 demo.py
```

### Run Full Evaluation Pipeline

Evaluate all methods on all test images:

```bash
python3 evaluate.py
```

Results will be saved to `output/` organized by method.

### Process Character Dumps

To add new characters to the character set, add characters to `characters/characterdump.txt` and run:

```bash
python3 characters.py
```

This will:
- Read from `characters/characterdump.txt` and `characters/uniquecharacterdump.txt`
- Detect and separate irregular characters (fullwidth, modifiers, etc.)
- Exclude characters already defined in `characters.py`
- Write new regular characters to `characters/uniquecharacterdump.txt`
- Write irregular characters to `characters/irregulars.txt` (preserved for future use)
- Reset `characters/characterdump.txt` to placeholder text

**Irregular characters** include fullwidth forms (like `Ａ` instead of `A`), modifier letters, and combining marks that may cause rendering issues in ASCII art.

### Run Specific Method

Example using the greedy IOU method:

```python
from PIL import Image
from ascii_image import AsciiImage

# Load an image
img = Image.open("path/to/image.png")

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

# Save as PNG
ascii_art.save("output.png")

# Or print to console
print(ascii_art)
```

## Main Files

- `characters.py` - Character set definitions
- `ascii_image.py` - AsciiImage class for storing and rendering ASCII art
- `methods.py` - Conversion methods and utilities
- `methods_config.yaml` - Configuration for evaluation methods
- `evaluate.py` - Full evaluation pipeline
