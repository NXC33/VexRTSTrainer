import os

IMAGE_FOLDER = "images"
PREFIX = "match_"
START_INDEX = 1
DIGITS = 3   # match_001, match_002, etc.

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")


def rename_images():
    files = [
        f for f in os.listdir(IMAGE_FOLDER)
        if f.endswith(VALID_EXTENSIONS)
    ]

    if not files:
        print("No image files found.")
        return

    # Sort by filename (usually matches phone capture order)
    files.sort()

    index = START_INDEX

    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        new_name = f"{PREFIX}{str(index).zfill(DIGITS)}{ext}"

        old_path = os.path.join(IMAGE_FOLDER, filename)
        new_path = os.path.join(IMAGE_FOLDER, new_name)

        # Prevent overwrite
        if os.path.exists(new_path):
            print(f"Skipping {filename} (target exists)")
            index += 1
            continue

        os.rename(old_path, new_path)
        print(f"{filename} → {new_name}")

        index += 1


if __name__ == "__main__":
    rename_images()
