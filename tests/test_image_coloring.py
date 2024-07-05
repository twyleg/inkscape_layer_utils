# Copyright (C) 2023 twyleg
import unittest
from pathlib import Path

from tests.image_test_case import ImageTestCase

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#

FILE_PATH = Path(__file__).parent


class Image1TestCase(ImageTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(FILE_PATH / "resources/test_images/test_image_coloring_0.svg", *args, **kwargs)

    def test_TestImageWithText_ColorizeText_TextColorized(
        self,
    ):
        self.test_image.find_layers_by_name("text")[0].fill_all_objects("#FF0000")
        extracted_single_layer_by_path_with_colorized_text = self.test_image.extract_layer(
            "/text", preserve_layer_paths=True
        )

        self.assert_images_equal(
            "resources/expected_images/test_image_coloring_extracted_single_layer_by_path_with_stroke_painted_text.svg",
            extracted_single_layer_by_path_with_colorized_text,
        )

    def test_TestImageWithText_ColorizeTransparentObject_TransparentObjectColorizedAndOpacitySet(
        self,
    ):
        left_eye_layer = self.test_image.get_layer_by_path("/face/eyes/left")
        right_eye_layer = self.test_image.get_layer_by_path("/face/eyes/right")

        left_eye_layer.set_stroke_opacity_of_all_objects(0.0)
        left_eye_layer.fill_all_objects("#000000", True)
        right_eye_layer.set_fill_opacity_of_all_objects(1.0)
        right_eye_layer.set_stroke_opacity_of_all_objects(1.0)

        self.assert_images_equal(
            "resources/expected_images/test_image_coloring_set_opacity.svg",
            self.test_image,
        )


if __name__ == "__main__":
    unittest.main()
