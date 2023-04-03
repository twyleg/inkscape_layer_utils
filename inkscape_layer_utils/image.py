import copy
import os
from os import PathLike
from collections import OrderedDict
from typing import List
from xml.etree.ElementTree import Element, ElementTree
from inkscape_layer_utils.layer import Layer, parse_layers, find_first_layer_by_name, get_layer_by_path, get_all_layer_paths
from inkscape_layer_utils.object import Object, parse_objects


class Image:

    def __init__(self, element_tree: ElementTree) -> None:
        self.element_tree: ElementTree = element_tree
        self.layer_element: Element = self.element_tree.getroot()
        self.layer_name: str = '/'
        self.layer_path: str = '/'
        self.layers: OrderedDict[str, Layer] = parse_layers(self.layer_element, '/')
        self.objects: OrderedDict[str, Object] = parse_objects(self.layer_element)

    def print_structure(self):
        print('Objects:')
        for object in self.objects.values():
            print(f'  {object}')

        print('Layers:')
        for layer in self.layers.values():
            print(f'  {layer}')
            layer.print_structure(2)

    def find_first_layer_by_name(self, layer_name: str) -> Layer:
        return find_first_layer_by_name(layer_name, self)

    def get_layer_by_path(self, path: str) -> Layer:
        return get_layer_by_path(path, self)

    def get_all_layer_paths(self) -> List[str]:
        return get_all_layer_paths(self)

    def extract_layer(self, path: str) -> 'Image':
        if path == '/':
            return copy.deepcopy(self)
        else:
            return self.extract_layers([path])

    def extract_layers(self, paths: List[str]) -> 'Image':
        new_image = copy.deepcopy(self)

        layers_to_extract: List[Layer] = []
        for path in paths:
            layers_to_extract.append(copy.deepcopy(new_image.get_layer_by_path(path)))

        for layer in new_image.layers.values():
            new_image.layer_element.remove(layer.layer_element)
        new_image.layers.clear()

        for layer_to_extract in layers_to_extract:
            new_image.layers[layer_to_extract.layer_name] = layer_to_extract
            new_image.layer_element.append(layer_to_extract.layer_element)
        return new_image

    def tear_apart(self) -> dict[str, 'Image']:
        layer_path_list = self.get_all_layer_paths()
        return dict((layer_path, self.extract_layer(layer_path)) for layer_path in layer_path_list)

    def tear_apart_to_file(self, output_dir: PathLike, base_name: str) -> None:
        extracted_images = self.tear_apart()
        for layer_path, extracted_image in extracted_images.items():
            if layer_path == '/':
                extracted_image.save(os.path.join(output_dir, f'{base_name}.svg'))
            else:
                extracted_image.save(os.path.join(output_dir, f'{base_name}{layer_path.replace("/", "_")}.svg'))

    def save(self, path: PathLike) -> None:
        self.element_tree.write(path)
