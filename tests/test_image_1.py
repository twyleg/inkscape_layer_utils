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
        super().__init__(FILE_PATH / "resources/test_images/test_image_1.svg", *args, **kwargs)

    def test_TestImageWithText_ColorizeText_TextColorized(
        self,
    ):
        self.test_image.find_layers_by_name("text")[0].fill_all_objects("#FF0000")
        extracted_single_layer_by_path_with_colorized_text = self.test_image.extract_layer(
            "/text", preserve_layer_paths=True
        )

        self.assert_images_equal(
            "resources/expected_images/extracted_single_layer_by_path_with_colorized_text.svg",
            extracted_single_layer_by_path_with_colorized_text,
        )


if __name__ == "__main__":
    unittest.main()
