# utils.py
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def text_to_image(text, width=1080, height=200, fontsize=80, color="white", bg_color=(0,0,0,0), font_path=None):
    """
    Render multi-line text to a PNG image.
    Returns the path to the saved image.
    """
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Use system font or fallback
    if font_path is None:
        font_path = "arial.ttf"  # Windows default
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except Exception:
        font = ImageFont.load_default()

    # Split text into lines if needed
    lines = text.split("\n")
    y = 10
    for line in lines:
        try:
            # Updated for Pillow >= 10
            bbox = draw.textbbox((0,0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older Pillow
            w, h = font.getsize(line)

        draw.text(((width-w)//2, y), line, font=font, fill=color)
        y += h + 10

    # Save image
    path = Path("temp_text.png")
    img.save(path)
    return str(path)
