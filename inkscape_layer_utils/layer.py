from collections import OrderedDict
from typing import List
from xml.etree.ElementTree import Element
from inkscape_layer_utils.object import Object, parse_objects


class Layer:

    def __init__(self, layer_element: Element, parent_layer_path: str):
        self.layer_element: Element = layer_element
        self.layer_name: str = layer_element.get('{http://www.inkscape.org/namespaces/inkscape}label')
        self.layer_path: str = f'/{self.layer_name}' if parent_layer_path == '/' else '/'.join([parent_layer_path, self.layer_name])
        self.layers: OrderedDict[str, Layer] = parse_layers(layer_element, self.layer_path)
        self.objects: OrderedDict[str, Object] = parse_objects(layer_element)

    def __str__(self):
        return f'Layer: name={self.layer_name}'

    def print_structure(self, level=1):
        for object in self.objects.values():
            print(f'{" " * level * 2}{object}')
        for layer in self.layers.values():
            print(f'{" " * level * 2}{layer}')
            layer.print_structure(level+1)

    def find_first_layer_by_name(self, layer_name: str) -> 'Layer':
        return find_first_layer_by_name(layer_name, self)

    def get_layer_by_path(self, path: str) -> 'Layer':
        return get_layer_by_path(path, self)

    def fill_objects(self, style: str, color: str) -> str:
        pass


def find_first_layer_by_name(layer_name: str, parent_layer) -> Layer:
    expected_layer = parent_layer.layers.get(layer_name)

    if expected_layer is not None:
        return expected_layer
    else:
        for layer in parent_layer.layers.values():
            expected_layer = find_first_layer_by_name(layer_name, layer)
            if expected_layer:
                return expected_layer


def get_layer_by_path(path: str, parent_layer):
    if path == '/':
        return parent_layer
    else:
        layer_names = path[1:].split('/')
        current_layer = parent_layer
        for layer_name in layer_names:
            current_layer = current_layer.layers[layer_name]
            if current_layer is None:
                break
        return current_layer


def get_all_layer_paths(parent_layer: 'Layer') -> List[str]:
    layer_paths: List[str] = [parent_layer.layer_path]
    for layer in parent_layer.layers.values():
        layer_paths.extend(get_all_layer_paths(layer))
    return layer_paths


def parse_layers(parent_element: Element, parent_layer_path: str) -> OrderedDict[str, Layer]:
    layer_dict: OrderedDict[str, Layer] = OrderedDict()

    for layer_element in parent_element.findall('{http://www.w3.org/2000/svg}g'):
        layer = Layer(layer_element, parent_layer_path)
        layer_dict[layer.layer_name] = layer

    return layer_dict
