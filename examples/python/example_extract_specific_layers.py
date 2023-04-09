# Copyright (C) 2023 twyleg
from pathlib import Path

from inkscape_layer_utils.image import Image

FILE_DIR = Path(__file__).parent
INPUT_DIR = FILE_DIR / "../../resources/test_images"
OUTPUT_DIR = FILE_DIR / "output" / Path(__file__).stem

if __name__ == "__main__":
    print(f"Running example - Output directory = {OUTPUT_DIR}")

    image = Image.load_from_file(INPUT_DIR / "test_image_0.svg")

    layers_to_extract_by_path = [
        "/background",
        "/face/mouth",
        "/face/nose"
    ]

    print("Extracting the following layers to a single file:")
    for layer_path in layers_to_extract_by_path:
        print(f"  {layer_path}")

    image_with_extracted_layers = image.extract_layers(layers_to_extract_by_path)
    image_with_extracted_layers.save(OUTPUT_DIR / "image_with_specific_layers.svg")

    print("Done!")
