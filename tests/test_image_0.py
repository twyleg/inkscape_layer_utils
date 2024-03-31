# Copyright (C) 2023 twyleg
import unittest

from pathlib import Path
from inkscape_layer_utils.image import Image, LayerUnknownError

from tests.image_test_case import ImageTestCase

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#

FILE_PATH = Path(__file__).parent


class Image0TestCase(ImageTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(FILE_PATH / "resources/test_images/test_image_0.svg", *args, **kwargs)

    def test_ImageWithMultipleLayers_GetListOfLayers_CorrectListOfLayersReturned(self):
        self.assertEqual(
            [
                "/",
                "/background",
                "/outline",
                "/face",
                "/face/mouth",
                "/face/eyes",
                "/face/eyes/right",
                "/face/eyes/left",
                "/face/nose",
            ],
            self.test_image.get_all_layer_paths(),
        )

    def test_ImageWithMultipleLayers_FindExistingLayerByName_LayerReturned(self):
        self.assertEqual("right", self.test_image.find_layers_by_name("right")[0].layer_name)

    def test_ImageWithMultipleLayers_FindNonExistingLayerByName_EmptyLayerListReturned(self):
        self.assertEqual(0, len(self.test_image.find_layers_by_name("not_existing")))

    def test_ImageWithMultipleLayers_GetExistingLayerByPath_LayerReturned(self):
        self.assertEqual("left", self.test_image.get_layer_by_path("/face/eyes/left").layer_name)

    def test_ImageWithMultipleLayers_GetRootLayerByPath_RootLayerReturned(self):
        self.assertEqual("/", self.test_image.get_layer_by_path("/").layer_name)

    def test_ImageWithMultipleLayers_GetNonExistingLayerByPath_LayerUnknownErrorRaised(self):
        with self.assertRaises(LayerUnknownError):
            self.test_image.get_layer_by_path("/not/existing")

    def test_ImageWithMultipleLayers_GetLayerByInvalidPath_LayerUnknownErrorRaised(self):
        with self.assertRaises(LayerUnknownError):
            self.test_image.get_layer_by_path("invalid_path")

    def test_RequestedLayerAvailable_ExtractSingleLayerByPathWithPathPreservation_SingleLayerExtractedWithPathPreservation(
        self,
    ):
        extracted_layer_image = self.test_image.extract_layer("/face/eyes/right")
        self.assert_images_equal(
            "resources/expected_images/extracted_single_layer_by_path_with_layer_path_preservation.svg",
            extracted_layer_image,
        )

    def test_RequestedLayerAvailable_ExtractSingleLayerByPathWithoutPathPreservation_SingleLayerExtractedWithoutLayerPathPreservation(
        self,
    ):
        extracted_layer_image = self.test_image.extract_layer("/face/eyes/right", preserve_layer_paths=False)
        self.assert_images_equal(
            "resources/expected_images/extracted_single_layer_by_path_without_layer_path_preservation.svg",
            extracted_layer_image,
        )

    def test_RequestedLayersAvailable_ExtractMultipleLayerByPathAndPreserveLayerPaths_MultipleLayersExtractedAndLayerPathsPreserved(
        self,
    ):
        extracted_layer_image = self.test_image.extract_layers(
            ["/face/eyes/right", "/face/eyes/left", "/outline"],
            preserve_layer_paths=True,
        )
        self.assert_images_equal(
            "resources/expected_images/extracted_multiple_layers_by_path_and_preserve_layer_paths.svg",
            extracted_layer_image,
        )

    def test_RequestedLayersAvailable_ExtractAllLayersToFile_AllLayersExtractedAndWrittenToFile(
        self,
    ):
        layer_output_dir_path = self.output_dir_path / "layers"

        extracted_image_file_paths_by_layer_paths = self.test_image.extract_all_layers_to_file(
            layer_output_dir_path,
            "base_name",
        )

        self.assertEqual(extracted_image_file_paths_by_layer_paths["/"], layer_output_dir_path / "base_name.svg")
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/background"], layer_output_dir_path / "base_name_background.svg"
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/outline"], layer_output_dir_path / "base_name_outline.svg"
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face"], layer_output_dir_path / "base_name_face.svg"
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face/mouth"], layer_output_dir_path / "base_name_face_mouth.svg"
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face/eyes"], layer_output_dir_path / "base_name_face_eyes.svg"
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face/eyes/left"],
            layer_output_dir_path / "base_name_face_eyes_left.svg",
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face/eyes/right"],
            layer_output_dir_path / "base_name_face_eyes_right.svg",
        )
        self.assertEqual(
            extracted_image_file_paths_by_layer_paths["/face/nose"], layer_output_dir_path / "base_name_face_nose.svg"
        )

        self.assert_images_from_file_equal(
            extracted_image_file_paths_by_layer_paths["/face/eyes/right"],
            FILE_PATH / "resources/expected_images/extracted_single_layer_by_path_with_layer_path_preservation.svg",
        )


if __name__ == "__main__":
    unittest.main()
