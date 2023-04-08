# Copyright (C) 2023 twyleg
import os
import unittest
import tempfile
import xml.etree.ElementTree as ET

from os import PathLike
from pathlib import Path
from inkscape_layer_utils.image import Image

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


class ImageTestCase(unittest.TestCase):

    @classmethod
    def prepare_output_directory(cls) -> Path:
        tmp_dir = tempfile.mkdtemp()
        return Path(tmp_dir)

    @classmethod
    def prepare_test_image(cls) -> Image:
        element_tree = ET.parse(Path(__file__).parent / 'resources/test_images/test_image_0.svg')
        return Image(element_tree)

    def assert_images_equal(self, expected_image_filepath: str, actual_image: Image):
        expected_element_tree = ET.parse(Path(__file__).parent / expected_image_filepath)
        root_node = expected_element_tree.getroot()
        self.assertEqual(ET.tostring(root_node), ET.tostring(actual_image.layer_element))

    def save_image_to_tmp_directory(self, image: Image) -> None:
        image.save(self.output_dir_path / f'{self.shortDescription()}.svg')

    def setUp(self) -> None:
        self.output_dir_path = self.prepare_output_directory()
        self.test_image = self.prepare_test_image()

    def test_ImageWithMultipleLayers_GetListOfLayers_CorrectListOfLayersReturned(self):
        self.assertEqual([
            '/',
            '/background',
            '/outline',
            '/face',
            '/face/mouth',
            '/face/eyes',
            '/face/eyes/right',
            '/face/eyes/left',
            '/face/nose'], self.test_image.get_all_layer_paths())

    def test_RequestedLayerAvailable_ExtractSingleLayerByPath_SingleLayerExtracted(self):
        extracted_layer_image = self.test_image.extract_layer('/face/eyes/right')
        self.assert_images_equal('resources/expected_images/extracted_single_layer_by_path.svg', extracted_layer_image)

    def test_RequestedLayerAvailable_ExtractSingleLayerByPathAndPreserveLayerPath_SingleLayerExtractedAndLayerPathPreserved(self):
        extracted_layer_image = self.test_image.extract_layer('/face/eyes/right', preserve_layer_paths=True)
        self.assert_images_equal('resources/expected_images/extracted_single_layer_by_path_and_preserve_layer_path.svg', extracted_layer_image)

    def test_RequestedLayersAvailable_ExtractMultipleLayerByPathAndPreserveLayerPaths_MultipleLayersExtractedAndLayerPathsPreserved(self):
        extracted_layer_image = self.test_image.extract_layers(['/face/eyes/right', '/face/eyes/left', '/outline'], preserve_layer_paths=True)
        self.assert_images_equal('resources/expected_images/extracted_multiple_layers_by_path_and_preserve_layer_paths.svg', extracted_layer_image)


if __name__ == '__main__':
    unittest.main()
