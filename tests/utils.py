from io import BytesIO

from PIL import Image, ImageDraw


def generate_image(text=None):
    img = Image.new('RGB', (10, 10))

    if text:
        d = ImageDraw.Draw(img)
        d.text((0, 0), text)

    fh = BytesIO()
    img.save(fh, format='PNG')
    return fh
