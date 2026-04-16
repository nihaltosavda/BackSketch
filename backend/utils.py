
from PIL import Image
from rembg import remove, new_session
import io

# Basic Settings
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

# Load model once
session = new_session("u2net")


# Validation Functions

def validate_file_size(file_bytes):
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File too large")


def validate_mime_type(content_type):
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Invalid file type")


def validate_image_bytes(file_bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        return img
    except:
        raise ValueError("Invalid image file")


# Background Removal

def remove_background(file_bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")

        # remove background
        output = remove(img, session=session)

        # convert to bytes
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")

        return buffer.getvalue()

    except Exception:
        raise RuntimeError("Error while removing background")


# Replace Background Color

def replace_background_color(file_bytes, color="#ffffff"):
    # first remove background
    transparent = remove_background(file_bytes)
    fg = Image.open(io.BytesIO(transparent)).convert("RGBA")

    # convert hex to RGB
    color = color.replace("#", "")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)

    # create background
    bg = Image.new("RGBA", fg.size, (r, g, b, 255))

    # combine images
    final = Image.alpha_composite(bg, fg).convert("RGB")

    buffer = io.BytesIO()
    final.save(buffer, format="PNG")

    return buffer.getvalue()