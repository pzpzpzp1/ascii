from PIL import ImageFont

FONT_PATH = "fonts/Menlo.ttc"
FONT_SIZE = 12

def load_font() -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE)
