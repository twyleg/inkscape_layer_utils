# Copyright (C) 2023 twyleg
import copy
import os
import xml.etree.ElementTree as ET
from os import PathLike
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional, Dict
from xml.etree.ElementTree import Element, ElementTree


class LayerUnknownError(Exception):
    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return f"Layer with path '{self.path}' is unknown!"


class Object:
    """
    Represents a graphical object like <svg:rect> or <svg:path> within the SVG file.

    Attributes
    ----------
    object_element: Element
        ElementTree Element that represents the object.
    tag: str
        tag name of XML element.
    id: str
        Inkscape id of the object.

    """

    def __init__(self, object_element: Element) -> None:
        """
        Parameters
        ----------
        object_element: Element
           ElementTree Element that represents the object.
        """
        self.object_element = object_element
        self.tag: str = object_element.tag
        self.id: str = object_element.attrib["id"]

    def __str__(self) -> str:
        return f"Object: tag={self.tag}, id={self.id}"

    def set_fill_color(self, color: str, force=False) -> None:
        """
        Set the fill color of an object to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        """
        style = self.object_element.attrib["style"]
        style_dict = OrderedDict(item.split(":") for item in style.split(";"))
        if force:
            style_dict["fill"] = color
        else:
            if style_dict["fill"] != "none":
                style_dict["fill"] = color
        self.object_element.attrib["style"] = ";".join([f"{key}:{value}" for key, value in style_dict.items()])

    def set_stroke_paint_color(self, color: str, force=False) -> None:
        """
        Set the stroke paint color of an object to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        """
        style = self.object_element.attrib["style"]
        style_dict = OrderedDict(item.split(":") for item in style.split(";"))
        if force:
            style_dict["stroke"] = color
        else:
            if style_dict["stroke"] != "none":
                style_dict["stroke"] = color
        self.object_element.attrib["style"] = ";".join([f"{key}:{value}" for key, value in style_dict.items()])


class Group:
    """
    Represents a group (XML-Tag: <svg:g ...>) within the SVG file.

    Attributes
    ----------
    object_element: Element
        ElementTree Element that represents the group.
    id: str
        Inkscape id of the group.
    objects: OrderedDict[str, Object]
        Holds objects within the group by their id.
    groups: OrderedDict[str, Group]
        Holds groups within the group by their id (e.g. nested groups or groups within layers).

    """

    def __init__(self, group_element: Element):
        """
        Parameters
        ----------
        group_element: Element
           ElementTree Element that represents the group.
        """
        self.group_element: Element = group_element
        self.id = group_element.attrib["id"]
        self.objects: OrderedDict[str, Object] = self.__parse_objects()
        self.groups: OrderedDict[str, Group] = self.__parse_groups()

    def __parse_objects(self) -> OrderedDict[str, Object]:
        object_dict: OrderedDict[str, Object] = OrderedDict()

        for element in self.group_element:
            if not element.tag == "{http://www.w3.org/2000/svg}g":
                object = Object(element)
                object_dict[object.id] = object

        return object_dict

    def __parse_groups(self) -> OrderedDict[str, "Group"]:
        group_dict: OrderedDict[str, "Group"] = OrderedDict()

        for group_element in self.group_element.findall("{http://www.w3.org/2000/svg}g"):
            groupmode = group_element.get("{http://www.inkscape.org/namespaces/inkscape}groupmode")
            if not groupmode or groupmode != "layer":
                group = Group(group_element)
                group_dict[group.id] = group

        return group_dict

    def fill_all_objects(self, color: str, force=False) -> None:
        """
        Set the fill color of all objects within the group to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        """
        for group in self.groups.values():
            group.fill_all_objects(color, force)

        for object in self.objects.values():
            object.set_fill_color(color, force)

    def stroke_paint_all_objects(self, color: str, force=False) -> None:
        """
        Set the stroke paint color of all objects within the group to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        """
        for group in self.groups.values():
            group.stroke_paint_all_objects(color, force)

        for object in self.objects.values():
            object.set_stroke_paint_color(color, force)

    # def colorize_all_objects_if_already_colored(self, color: str, recursive=False) -> None:
    #     """
    #     Set the stroke paint and fill color of all objects within the group to the given value, if they are already colorized.
    #
    #     Parameters
    #     ----------
    #     color: str
    #         The color string in Hex RGB format. E.g. '#FF0000' for red.
    #     """
    #     for group in self.groups.values():
    #         group.colorize_all_objects_if_already_colored(color, recursive=recursive)
    #
    #     for object in self.objects.values():
    #         object.set_color_if_already_colored(color)


class Layer(Group):
    """
    Represents a layer (XML-Tag: <svg:g inkscape:groupmode="layer" ...>) within a SVG file.
    Layers (in Inkscape) are a special form of group which are marked by the attribute 'inkscape:groupmode="layer"'.

    Attributes
    ----------
    layer_element: Element
        ElementTree Element that represents the layer.
    layer_name: str
        Name of the layer or '/' when it is the root layer of the image.
    layer_path: str
        POSIX style path of the layer. This kind of path is not used by inkscape itself but introduced by this library
        to make identification and access of layers within complex multilayer images simple and convenient.
    layers: OrderedDict[str, Layer]
        Holds sublayers of this layer by their name.

    """

    def __init__(self, layer_element: Element, parent_layer_path: Optional[str]):
        """
        Parameters
        ----------
        layer_element: Element
           ElementTree Element that represents the layer
        parent_layer_path: Optional[str]
            Path of the parent layer to build up the path of this layer. If not provided, the layer is treated as the
            root layer, which results in a layer path equal to '/'.
        """
        super().__init__(layer_element)
        self.layer_element: Element = layer_element
        if parent_layer_path:
            self.layer_name = layer_element.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
            self.layer_path = (
                f"/{self.layer_name}" if parent_layer_path == "/" else "/".join([parent_layer_path, self.layer_name])
            )
        else:
            self.layer_name = "/"
            self.layer_path = "/"
        self.layers: OrderedDict[str, Layer] = self.__parse_layers()

    def __str__(self):
        return f"Layer: name={self.layer_name}"

    def __parse_layers(self) -> OrderedDict[str, "Layer"]:
        layer_dict: OrderedDict[str, Layer] = OrderedDict()

        for group_element in self.layer_element.findall("{http://www.w3.org/2000/svg}g"):
            groupmode = group_element.get("{http://www.inkscape.org/namespaces/inkscape}groupmode")
            if groupmode and groupmode == "layer":
                layer = Layer(group_element, self.layer_path)
                layer_dict[layer.layer_name] = layer

        return layer_dict

    def find_layers_by_name(self, layer_name: str) -> List["Layer"]:
        """
        Find all layers with the given name.

        Parameters
        ----------
        layer_name: str
            Name of the layers to search for.

        Returns
        -------
        List[Layer]
            List containing all layers with the given name.
        """
        layers: List["Layer"] = []

        result_on_current_layer = self.layers.get(layer_name)

        if result_on_current_layer:
            layers.append(result_on_current_layer)

        for layer in self.layers.values():
            layers.extend(layer.find_layers_by_name(layer_name))

        return layers

    def get_layer_by_path(self, path: str) -> "Layer":
        """
        Get a layer by its path.

        Parameters
        ----------
        path: str
            Path of the layer e.g. /parent_layer/sub_layer/sub_sub_layer.

        Returns
        -------
        Layer
            Layer that was found under the given path.
        """
        if path == "/":
            return self
        else:
            layer_names = path[1:].split("/")
            current_layer = self
            for layer_name in layer_names:
                try:
                    current_layer = current_layer.layers[layer_name]
                except KeyError:
                    raise LayerUnknownError(path)
            return current_layer

    def get_all_layer_paths(self) -> List[str]:
        """
        Get all layer paths of the sublayers.

        Returns
        -------
        List[str]
            List of all the layer paths of the sublayer.
        """
        layer_paths: List[str] = [self.layer_path]
        for layer in self.layers.values():
            layer_paths.extend(layer.get_all_layer_paths())
        return layer_paths

    def remove_all_layers(self) -> None:
        """
        Remove all sub layers from layer.
        """
        for layer in self.layers.values():
            self.layer_element.remove(layer.layer_element)
        self.layers.clear()

    def remove_all_objects_and_groups(self) -> None:
        """
        Remove all objects and groups from layer.
        """
        for object in self.objects.values():
            self.layer_element.remove(object.object_element)
        for group in self.groups.values():
            self.layer_element.remove(group.group_element)
        self.objects.clear()
        self.groups.clear()

    def remove_layers_if_path_not_matching(self, paths: List[str]) -> None:
        """
        Remove all sublayers if their path is not in the list of paths.

        Parameters
        ----------
        paths: List[str]
            List of paths that should not be removed

        """
        layers_to_remove: List["Layer"] = []
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

        if self.layer_path != "/" and self.layer_path not in paths:
            self.remove_all_objects_and_groups()

    def fill_all_objects(self, color: str, force=False, recursive=False) -> None:
        """
        Set the fill color of all objects and groups within the group to the given value.
        If recursive is activated, all objects on sublayers will be filled as well.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        recursive: bool
            Flag to enable recursive coloring.

        """
        super().fill_all_objects(color, force)

        if recursive:
            for layer in self.layers.values():
                layer.fill_all_objects(color, force=force, recursive=recursive)

    def stroke_paint_all_objects(self, color: str, force=False, recursive=False) -> None:
        """
        Set the stroke paint color of all objects and groups within the group to the given value.
        If recursive is activated, all objects on sublayers will be stroke painted as well.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment
        recursive: bool
            Flag to enable recursive coloring.

        """
        super().stroke_paint_all_objects(color, force=force)

        if recursive:
            for layer in self.layers.values():
                layer.stroke_paint_all_objects(color, force=force, recursive=recursive)


class Image(Layer):
    """
    Represents an Inkscape SVG image.

    Attributes
    ----------
    element_tree: ElementTree
        ElementTree that represents the image.

    """

    @classmethod
    def load_from_file(cls, file_path: PathLike) -> "Image":
        """
        Load a SVG image from file.

        Parameters
        ----------
        file_path: PathLike
            Path of file to load.

        Returns
        -------
        Image
            Loaded image.

        """
        return Image(ET.parse(file_path))

    @classmethod
    def load_from_string(cls, image_as_string: str) -> "Image":
        """
        Load SVG image from XML string.

        Parameters
        ----------
        image_as_string: str
            String representing the SVG image.

        Returns
        -------
        Image
            Loaded image.

        """
        return Image(ElementTree(ET.fromstring(image_as_string)))

    def __init__(self, element_tree: ElementTree) -> None:
        """
        Parameters
        ----------
        element_tree: ElementTree
            ElementTree that represents the SVG image.
        """
        super().__init__(element_tree.getroot(), None)
        self.element_tree: ElementTree = element_tree

    def extract_layer(self, path: str, preserve_layer_paths=True) -> "Image":
        """

        Parameters
        ----------
        path: str
            Layer path of the layer that will be extracted.
        preserve_layer_paths: bool=True
            When True, the complete layer path will be preserved in the output file.
            When False, the extracted layer will be a direct child of the root layer in the output file.

        Returns
        -------
        Image
            Output image that will contain only the requested layer.

        """
        if path == "/":
            return copy.deepcopy(self)
        else:
            return self.extract_layers([path], preserve_layer_paths)

    def extract_layers(self, paths: List[str], preserve_layer_paths=True) -> "Image":
        """
        Extract one or multiple layers.

        Parameters
        ----------
        paths: List[str]
            List of layer paths to extract.
        preserve_layer_paths: bool=True
            When True, the complete layer path will be preserved in the output file.
            When False, the extracted layer will be a direct child of the root layer in the output file.

        Returns
        -------
        Image
            Output image that will contain only the requested layers.

        """
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

    def extract_all_layers(self) -> dict[str, "Image"]:
        """
        Extract all layers of the image.

        Returns
        -------
        dict[str, Image]
            Dictionary with layers byt their path.

        """
        layer_path_list = self.get_all_layer_paths()
        return dict((layer_path, self.extract_layer(layer_path)) for layer_path in layer_path_list)

    def extract_all_layers_to_file(self, output_dir: PathLike, base_name: str) -> Dict[str, Path]:
        """
        Extract all layers to file by providing an output directory and a base name for
        the extracted layers output file names.

        Parameters
        ----------
        output_dir: PathLike
            Output directory to write files to.
        base_name: str
            Base name of the files that will be saved.
        Returns
        -------
        dict[str, Path]
            Dictionary with file paths by layer paths.
        """
        extracted_layer_file_paths_by_layer_path: Dict[str, Path] = {}
        extracted_images = self.extract_all_layers()
        for layer_path, extracted_image in extracted_images.items():
            if layer_path == "/":
                output_file_path = Path(output_dir) / f"{base_name}.svg"
            else:
                output_file_path = Path(output_dir) / f'{base_name}{layer_path.replace("/", "_")}.svg'
            extracted_image.save(output_file_path)
            extracted_layer_file_paths_by_layer_path[layer_path] = output_file_path
        return extracted_layer_file_paths_by_layer_path

    def save(self, path: PathLike) -> None:
        """
        Save image to file.

        Parameters
        ----------
        path: PathLike
            File location to write image to.
        """
        os.makedirs(Path(path).parent, exist_ok=True)
        self.element_tree.write(path)
