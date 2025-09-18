from io import BytesIO
import os

from PIL import Image


MAX_DIM = 512  # max width/height
MAX_BYTES = 2 * 1024 * 1024  # 2 MB


def process_avatar_upload(upload_file, dest_path, preferred_format="WEBP"):
    """
    upload_file: UploadFile
    dest_path: full path including filename where result should be saved
    preferred_format: 'WEBP' or 'JPEG'
    Returns saved relative path.
    """
    img = Image.open(upload_file.file)
    # convert to RGB if needed
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # resize with aspect ratio
    img.thumbnail((MAX_DIM, MAX_DIM))
    # save to buffer first with quality/compression loop if needed
    buf = BytesIO()
    quality = 85
    # try iterative reduce if result too big
    img.save(buf, format=preferred_format, quality=quality, optimize=True)
    size = buf.tell()
    while size > MAX_BYTES and quality > 30:
        quality -= 5
        buf.seek(0)
        buf.truncate()
        img.save(buf, format=preferred_format, quality=quality, optimize=True)
        size = buf.tell()
    # finally write to disk
    buf.seek(0)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(buf.read())
    return dest_path
