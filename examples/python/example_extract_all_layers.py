# Copyright (C) 2023 twyleg
from pathlib import Path

from inkscape_layer_utils.image import Image

FILE_DIR = Path(__file__).parent
INPUT_DIR = FILE_DIR / "../../resources/test_images"
OUTPUT_DIR = FILE_DIR / "output" / Path(__file__).name

if __name__ == "__main__":
    print(f"Running example - Output directory = {OUTPUT_DIR}")

    image = Image.load_from_file(INPUT_DIR / "test_image_0.svg")

    print("Extracting the following layers to file:")
    for layer_path in image.get_all_layer_paths():
        print(f"  {layer_path}")
    print("Done!")

    image.extract_all_layers_to_file(OUTPUT_DIR, "test_image_0")
