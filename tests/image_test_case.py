# Copyright (C) 2024 twyleg
import unittest
import tempfile
import xml.etree.ElementTree as ET

from pathlib import Path
from inkscape_layer_utils.image import Image, LayerUnknownError


FILE_PATH = Path(__file__).parent


class ImageTestCase(unittest.TestCase):
    def __init__(self, test_image_path: Path, *args, **kwargs):
        super().__init__(*args)
        self.test_image_path = test_image_path

    @classmethod
    def prepare_output_directory(cls) -> Path:
        tmp_dir = tempfile.mkdtemp()
        return Path(tmp_dir)

    def prepare_test_image(self) -> Image:
        element_tree = ET.parse(self.test_image_path)
        return Image(element_tree)

    def assert_image_element_trees_equal(
        self, expected_image_element_tree: ET.Element, actual_image_element_tree: ET.Element
    ):
        self.assertEqual(ET.tostring(expected_image_element_tree), ET.tostring(actual_image_element_tree))

    def assert_images_equal(self, expected_image_filepath: str, actual_image: Image):
        expected_element_tree = ET.parse(FILE_PATH / expected_image_filepath)
        root_node = expected_element_tree.getroot()
        self.assert_image_element_trees_equal(root_node, actual_image.layer_element)

    def assert_images_from_file_equal(self, expected_image_filepath: Path, actual_image_filepath: Path):
        expected_element_tree = ET.parse(expected_image_filepath)
        actual_element_tree = ET.parse(actual_image_filepath)
        expected_root_node = expected_element_tree.getroot()
        actual_root_node = actual_element_tree.getroot()
        self.assert_image_element_trees_equal(expected_root_node, actual_root_node)

    def save_image_to_tmp_directory(self, image: Image) -> None:
        image.save(self.output_dir_path / f"{self.shortDescription()}.svg")

    def setUp(self) -> None:
        self.output_dir_path = self.prepare_output_directory()
        self.test_image = self.prepare_test_image()
