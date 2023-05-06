# Copyright (C) 2023 twyleg
from pathlib import Path

from inkscape_layer_utils.image import Image

SCRIPT_DIR = Path(__file__).parent

test_image = Image.load_from_file(SCRIPT_DIR / "test_images/test_image_0.svg")


extracted_single_layer_by_path_with_layer_path_preservation = test_image.extract_layer("/face/eyes/right")
extracted_single_layer_by_path_with_layer_path_preservation.save(
    SCRIPT_DIR / "expected_images/extracted_single_layer_by_path_with_layer_path_preservation.svg"
)

extracted_single_layer_by_path_without_layer_path_preservation = test_image.extract_layer(
    "/face/eyes/right", preserve_layer_paths=False
)
extracted_single_layer_by_path_without_layer_path_preservation.save(
    SCRIPT_DIR / "expected_images/extracted_single_layer_by_path_without_layer_path_preservation.svg"
)

extracted_multiple_layers_by_path_and_preserve_layer_paths = test_image.extract_layers(
    ["/face/eyes/right", "/face/eyes/left", "/outline"],
    preserve_layer_paths=True,
)
extracted_multiple_layers_by_path_and_preserve_layer_paths.save(
    SCRIPT_DIR / "expected_images/extracted_multiple_layers_by_path_and_preserve_layer_paths.svg"
)
