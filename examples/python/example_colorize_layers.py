# Copyright (C) 2023 twyleg
from pathlib import Path

from inkscape_layer_utils.image import Image

FILE_DIR = Path(__file__).parent
INPUT_DIR = FILE_DIR / "../../resources/test_images"
OUTPUT_DIR = FILE_DIR / "output" / Path(__file__).name

if __name__ == "__main__":
    print(f"Running example - Output directory = {OUTPUT_DIR}")

    image = Image.load_from_file(INPUT_DIR / "test_image_0.svg")

    eyes_layer = image.get_layer_by_path("/face/eyes")
    eyes_layer.fill_all_objects("#FF0000", recursive=True)

    image.save(OUTPUT_DIR / "colorized_eyes_layer.svg")
