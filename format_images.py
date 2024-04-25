"""
Resizes images images from INPUT_DIR and saves them in OUTPUT_DIR, such that all are square, and have the length/width
of the largest image in INPUT_DIR.
"""

from PIL import Image
import os

if __name__ == "__main__":
    INPUT_DIR = "raw_images_v2"
    OUTPUT_DIR = "cropped_images_v2"

    max_dim = 0

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    _, _, file_names = next(os.walk(INPUT_DIR))
    for idx, file_name in enumerate(file_names):
        if file_name == "Thumbs.db":
            continue
        with Image.open(INPUT_DIR + "/" + file_name) as original_image:
            max_dim = max(max_dim, max(original_image.size))

    _, _, file_names = next(os.walk(INPUT_DIR))

    print(f"Max dimension is: {max_dim}")
    for idx, file_name in enumerate(file_names):
        if file_name == "Thumbs.db":
            continue
        with Image.open(INPUT_DIR + "/" + file_name) as original_image:
            max_dim = max(max_dim, max(original_image.size))

            resized_image = original_image.resize((max_dim, max_dim))

            resized_image.save(f"{OUTPUT_DIR}/{file_name}")
