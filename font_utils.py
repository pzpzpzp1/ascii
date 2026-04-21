from PIL import ImageFont, Image, ImageDraw

FONT_PATH = "fonts/Menlo.ttc"
FONT_SIZE = 12

def load_font() -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE)

def char_dims() -> tuple[int, int]:
    """Return (cell_width, cell_height) in pixels for the canonical font."""
    font = load_font()
    ascent, descent = font.getmetrics()
    h = ascent + descent
    tmp = Image.new('L', (1, 1))
    w = int(round(ImageDraw.Draw(tmp).textlength('M', font=font)))
    return w, h
