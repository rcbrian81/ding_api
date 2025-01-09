import os
from PIL import Image
import imghdr


def upload_profile_picture(file_path):
    storage_dir = "storage_pfp"
    os.makedirs(storage_dir, exist_ok=True)

    file_size = os.path.getsize(file_path)
    if file_size > 2 * 1024 * 1024:
        return "Error: File size exceeds 2MB."

    file_type = imghdr.what(file_path)
    if file_type not in ["jpeg", "png", "bmp", "gif"]:
        return "Error: Unsupported file type. Supported types: jpeg, png, bmp, gif."

    try:

        img = Image.open(file_path)

        if file_type != "jpeg":
            img = img.convert("RGB")

        output_path = os.path.join(storage_dir, os.path.basename(file_path))
        output_path = os.path.splitext(output_path)[0] + ".jpg"
        img.save(output_path, format="JPEG", quality=85)
        return f"Success: File uploaded to {output_path}."

    except Exception as e:
        return f"Error: {e}"
