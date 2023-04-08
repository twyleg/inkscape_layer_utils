# Copyright (C) 2023 twyleg
import copy
import os
from os import PathLike
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import Element, ElementTree


class Object:
    def __init__(self, object_element: Element) -> None:
        self.object_element = object_element
        self.tag = object_element.tag
        self.id = object_element.attrib['id']

    def __str__(self) -> str:
        return f'Object: tag={self.tag}, id={self.id}'

    def set_fill_color(self, color: str) -> None:
        style = self.object_element.attrib['style']
        style_dict = OrderedDict(item.split(':') for item in style.split(';'))
        style_dict['fill'] = color
        self.object_element.attrib['style'] = ';'.join([f'{key}:{value}' for key, value in style_dict.items()])


class Group:
    def __init__(self, group_element: Element):
        self.group_element: Element = group_element
        self.id = group_element.attrib['id']
        self.objects: OrderedDict[str, Object] = self.__parse_objects()
        self.groups: OrderedDict[str, Group] = self.__parse_groups()

    def __parse_objects(self) -> OrderedDict[str, Object]:
        object_dict: OrderedDict[str, Object] = OrderedDict()

        for element in self.group_element:
            if not element.tag == '{http://www.w3.org/2000/svg}g':
                object = Object(element)
                object_dict[object.id] = object

        return object_dict

    def __parse_groups(self) -> OrderedDict[str, 'Group']:
        group_dict: OrderedDict[str, 'Group'] = OrderedDict()

        for group_element in self.group_element.findall('{http://www.w3.org/2000/svg}g'):
            groupmode = group_element.get('{http://www.inkscape.org/namespaces/inkscape}groupmode')
            if not groupmode or groupmode != 'layer':
                group = Group(group_element)
                group_dict[group.id] = group

        return group_dict

    def fill_all_objects(self, color: str) -> None:
        for object in self.objects.values():
            object.set_fill_color(color)


class Layer(Group):
    def __init__(self, layer_element: Element, parent_layer_path: Optional[str]):
        super().__init__(layer_element)
        self.layer_element: Element = layer_element
        if parent_layer_path:
            self.layer_name = layer_element.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
            self.layer_path = f'/{self.layer_name}' if parent_layer_path == '/' else '/'.join([parent_layer_path, self.layer_name])
        else:
            self.layer_name = '/'
            self.layer_path = '/'
        self.layers: OrderedDict[str, Layer] = self.__parse_layers()

    def __str__(self):
        return f'Layer: name={self.layer_name}'

    def __parse_layers(self) -> OrderedDict[str, 'Layer']:
        layer_dict: OrderedDict[str, Layer] = OrderedDict()

        for group_element in self.layer_element.findall('{http://www.w3.org/2000/svg}g'):
            groupmode = group_element.get('{http://www.inkscape.org/namespaces/inkscape}groupmode')
            if groupmode and groupmode == 'layer':
                layer = Layer(group_element, self.layer_path)
                layer_dict[layer.layer_name] = layer

        return layer_dict

    def find_first_layer_by_name(self, layer_name: str) -> Optional['Layer']:
        expected_layer = self.layers.get(layer_name)

        if expected_layer is not None:
            return expected_layer
        else:
            for layer in self.layers.values():
                expected_layer = layer.find_first_layer_by_name(layer_name)
                if expected_layer:
                    return expected_layer
        return None

    def get_layer_by_path(self, path: str):
        if path == '/':
            return self
        else:
            layer_names = path[1:].split('/')
            current_layer = self
            for layer_name in layer_names:
                current_layer = current_layer.layers[layer_name]
                if current_layer is None:
                    break
            return current_layer

    def get_all_layer_paths(self) -> List[str]:
        layer_paths: List[str] = [self.layer_path]
        for layer in self.layers.values():
            layer_paths.extend(layer.get_all_layer_paths())
        return layer_paths

    def remove_all_layers(self) -> None:
        for layer in self.layers.values():
            self.layer_element.remove(layer.layer_element)
        self.layers.clear()

    def remove_all_objects_and_groups(self) -> None:
        for object in self.objects.values():
            self.layer_element.remove(object.object_element)
        for group in self.groups.values():
            self.layer_element.remove(group.group_element)
        self.objects.clear()
        self.groups.clear()

    def remove_layers_if_path_not_matching(self, paths: List[str]) -> None:
        layers_to_remove: List['Layer'] = []
        for layer in self.layers.values():
            remove_layer = True
            for path in paths:
                if path.startswith(layer.layer_path):
                    remove_layer = False
                    break

            if remove_layer:
                layers_to_remove.append(layer)

            layer.remove_layers_if_path_not_matching(paths)

        for layer_to_remove in layers_to_remove:
            self.layer_element.remove(layer_to_remove.layer_element)
            del self.layers[layer_to_remove.layer_name]

        if self.layer_path != '/' and self.layer_path not in paths:
            self.remove_all_objects_and_groups()


class Image(Layer):

    def __init__(self, element_tree: ElementTree) -> None:
        super().__init__(element_tree.getroot(), None)
        self.element_tree: ElementTree = element_tree

    def extract_layer(self, path: str, preserve_layer_paths=True) -> 'Image':
        if path == '/':
            return copy.deepcopy(self)
        else:
            return self.extract_layers([path], preserve_layer_paths)

    def extract_layers(self, paths: List[str], preserve_layer_paths=True) -> 'Image':
        new_image = copy.deepcopy(self)

        if preserve_layer_paths:
            new_image.remove_layers_if_path_not_matching(paths)
        else:
            layers_to_extract: List[Layer] = []
            for path in paths:
                layers_to_extract.append(copy.deepcopy(new_image.get_layer_by_path(path)))

            new_image.remove_all_layers()

            for layer_to_extract in layers_to_extract:
                new_image.layers[layer_to_extract.layer_name] = layer_to_extract
                new_image.layer_element.append(layer_to_extract.layer_element)
        return new_image

    def extract_all_layers(self) -> dict[str, 'Image']:
        layer_path_list = self.get_all_layer_paths()
        return dict((layer_path, self.extract_layer(layer_path)) for layer_path in layer_path_list)

    def extract_all_layers_to_file(self, output_dir: PathLike, base_name: str) -> None:
        extracted_images = self.extract_all_layers()
        for layer_path, extracted_image in extracted_images.items():
            if layer_path == '/':
                extracted_image.save(Path(output_dir) / f'{base_name}.svg')
            else:
                extracted_image.save(Path(output_dir) / f'{base_name}{layer_path.replace("/", "_")}.svg')

    def save(self, path: PathLike) -> None:
        os.makedirs(Path(path).parent, exist_ok=True)
        self.element_tree.write(path)
