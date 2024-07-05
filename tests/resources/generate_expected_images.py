# Copyright (C) 2023 twyleg
from pathlib import Path

from inkscape_layer_utils.image import Image

SCRIPT_DIR = Path(__file__).parent

test_image_layer_extraction_0 = Image.load_from_file(SCRIPT_DIR / "test_images/test_image_layer_extraction_0.svg")
test_image_coloring_0 = Image.load_from_file(SCRIPT_DIR / "test_images/test_image_coloring_0.svg")
test_image_coloring_1 = Image.load_from_file(SCRIPT_DIR / "test_images/test_image_coloring_0.svg")


extracted_single_layer_by_path_with_layer_path_preservation = test_image_layer_extraction_0.extract_layer("/face/eyes/right")
extracted_single_layer_by_path_with_layer_path_preservation.save(
    SCRIPT_DIR / "expected_images/test_image_layer_extraction_extracted_single_layer_by_path_with_layer_path_preservation.svg"
)

extracted_single_layer_by_path_without_layer_path_preservation = test_image_layer_extraction_0.extract_layer(
    "/face/eyes/right", preserve_layer_paths=False
)
extracted_single_layer_by_path_without_layer_path_preservation.save(
    SCRIPT_DIR / "expected_images/test_image_layer_extraction_extracted_single_layer_by_path_without_layer_path_preservation.svg"
)

extracted_multiple_layers_by_path_and_preserve_layer_paths = test_image_layer_extraction_0.extract_layers(
    ["/face/eyes/right", "/face/eyes/left", "/outline"],
    preserve_layer_paths=True,
)
extracted_multiple_layers_by_path_and_preserve_layer_paths.save(
    SCRIPT_DIR / "expected_images/test_image_layer_extraction_extracted_multiple_layers_by_path_and_preserve_layer_paths.svg"
)

test_image_coloring_0.find_layers_by_name("text")[0].fill_all_objects("#FF0000")
extracted_single_layer_by_path_with_stroke_painted_text = test_image_coloring_0.extract_layer("/text", preserve_layer_paths=True)
extracted_single_layer_by_path_with_stroke_painted_text.save(
    SCRIPT_DIR / "expected_images/test_image_coloring_extracted_single_layer_by_path_with_stroke_painted_text.svg"
)

left_eye_layer = test_image_coloring_1.get_layer_by_path("/face/eyes/left")
right_eye_layer = test_image_coloring_1.get_layer_by_path("/face/eyes/right")
left_eye_layer.set_stroke_opacity_of_all_objects(0.0)
left_eye_layer.fill_all_objects("#000000", True)
right_eye_layer.set_fill_opacity_of_all_objects(1.0)
right_eye_layer.set_stroke_opacity_of_all_objects(1.0)
test_image_coloring_1.save(
    SCRIPT_DIR / "expected_images/test_image_coloring_set_opacity.svg"
)

