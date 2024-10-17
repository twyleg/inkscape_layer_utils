# Copyright (C) 2024 twyleg
import copy
import os
import logging
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional, Dict
from xml.etree.ElementTree import Element, ElementTree


class LayerUnknownError(Exception):
    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return f"Layer with path '{self.path}' is unknown!"


class HirarchicalElement:
    def __init__(self, level: int):
        self.level = level

    def log_hirarchical(self, logm: logging.Logger, fmt: str, *args):
        logm.debug(f"{'  '*self.level}{fmt}", *args)


class Object(HirarchicalElement):
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
    objects: OrderedDict[str, Object]
        An ordered dict with all the sub objects by their id

    """

    logm = logging.getLogger(f"{__name__}.obj")

    def __init__(self, object_element: Element, level=0) -> None:
        """
        Parameters
        ----------
        object_element: Element
           ElementTree Element that represents the object.
        """
        super().__init__(level)
        self.object_element = object_element

        self.tag: str = object_element.tag
        self.id: str = object_element.attrib["id"]
        self.objects: OrderedDict[str, Object] = self.__parse_objects()

    def __str__(self) -> str:
        return f"Object: tag={self.tag}, id={self.id}"

    def __parse_objects(self) -> OrderedDict[str, "Object"]:
        object_dict: OrderedDict[str, Object] = OrderedDict()

        self.log_hirarchical(self.logm, 'Parse object "%s" for sub-objects', self.id)
        for element in self.object_element:
            if "id" in element.attrib:
                self.log_hirarchical(self.logm, '- Found object: tag="%s", id="%s"', element.tag, element.attrib["id"])
                object = Object(element, self.level + 1)
                object_dict[object.id] = object

        if len(object_dict) == 0:
            self.log_hirarchical(self.logm, "- None")

        return object_dict

    def _set_style_attribute(self, key: str, value: str | float | int, force=False):
        if "style" in self.object_element.attrib:
            style = self.object_element.attrib["style"]
            style_dict = OrderedDict(item.split(":") for item in style.split(";"))
            if force:
                style_dict[key] = str(value)
            else:
                if key in style_dict and style_dict[key] != "none":
                    style_dict[key] = str(value)
            self.object_element.attrib["style"] = ";".join([f"{key}:{value}" for key, value in style_dict.items()])

    def set_fill_color(self, color: str, force=False) -> None:
        """
        Set the fill color of an object to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment.
        """
        self.logm.debug("Set fill color: object-id=%s, color=%s, force=%s", self.id, color, force)
        for object in self.objects.values():
            object.set_fill_color(color, force)

        self._set_style_attribute("fill", color, force)

    def set_stroke_paint_color(self, color: str, force=False) -> None:
        """
        Set the stroke paint color of an object to the given value.

        Parameters
        ----------
        color: str
            The color string in Hex RGB format. E.g. '#FF0000' for red.
        force: bool
            Force to colorize even if not colorized at the moment.
        """
        self.logm.debug("Set stroke paint color: object-id=%s, color=%s, force=%s", self.id, color, force)
        for object in self.objects.values():
            object.set_stroke_paint_color(color, force)

        self._set_style_attribute("stroke", color, force)

    def set_fill_opacity(self, opacity: float, force=False) -> None:
        """
        Set the fill opacity of an object to the given value.

        Parameters
        ----------
        opacity: float
            The the objects opacity from 0.0 - 1.0 (0% - 100%).
        force: bool
            Force to set the opacity attribute even if it is not present at the moment.
        """
        self.logm.debug("Set fill opacity: object-id=%s, opacity=%f, force=%s", self.id, opacity, force)
        for object in self.objects.values():
            object.set_fill_opacity(opacity)

        self._set_style_attribute("fill-opacity", opacity, force)

    def set_stroke_opacity(self, opacity: float, force=False) -> None:
        """
        Set the stroke opacity of an object to the given value.

        Parameters
        ----------
        opacity: float
            The the objects opacity from 0.0 - 1.0 (0% - 100%).
        force: bool
            Force to set the opacity attribute even if it is not present at the moment.
        """
        for object in self.objects.values():
            object.set_fill_opacity(opacity)

        self._set_style_attribute("stroke-opacity", opacity, force)


class Group(HirarchicalElement):
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

    logm = logging.getLogger(f"{__name__}.grp")

    def __init__(self, group_element: Element, level=0):
        """
        Parameters
        ----------
        group_element: Element
           ElementTree Element that represents the group.
        """
        super().__init__(level)
        self.group_element: Element = group_element

        self.id = group_element.attrib["id"]
        self.objects: OrderedDict[str, Object] = self.__parse_objects()
        self.groups: OrderedDict[str, Group] = self.__parse_groups()

    def __parse_objects(self) -> OrderedDict[str, Object]:
        object_dict: OrderedDict[str, Object] = OrderedDict()

        self.log_hirarchical(self.logm, 'Parse group "%s" for sub-objects:', self.id)
        for element in self.group_element:
            if not element.tag == "{http://www.w3.org/2000/svg}g" and "id" in element.attrib:
                self.log_hirarchical(self.logm, '- Found object: tag="%s", id="%s"', element.tag, element.attrib["id"])
                object = Object(element, self.level + 1)
                object_dict[object.id] = object

        if len(object_dict) == 0:
            self.log_hirarchical(self.logm, "- None")

        return object_dict

    def __parse_groups(self) -> OrderedDict[str, "Group"]:
        group_dict: OrderedDict[str, "Group"] = OrderedDict()

        self.log_hirarchical(self.logm, 'Parse group "%s" for sub-groups:', self.id)
        for group_element in self.group_element.findall("{http://www.w3.org/2000/svg}g"):
            groupmode = group_element.get("{http://www.inkscape.org/namespaces/inkscape}groupmode")
            if not groupmode or groupmode != "layer" and "id" in group_element.attrib:
                self.log_hirarchical(self.logm, '- Found group: id="%s"', group_element.attrib["id"])
                group = Group(group_element, self.level + 1)
                group_dict[group.id] = group

        if len(group_dict) == 0:
            self.log_hirarchical(self.logm, "- None")

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

    def set_fill_opacity_of_all_objects(self, opacity: float, force=False) -> None:
        """
        Set the fill opacity of all objects within the group to the given value.

        Parameters
        ----------
        opacity: float
            The the objects opacity from 0.0 - 1.0 (0% - 100%).
        force: bool
            Force to set the opacity attribute even if it is not present at the moment.
        """
        for group in self.groups.values():
            group.set_fill_opacity_of_all_objects(opacity, force)

        for object in self.objects.values():
            object.set_fill_opacity(opacity, force)

    def set_stroke_opacity_of_all_objects(self, opacity: float, force=False) -> None:
        """
        Set the stroke opacity of all objects within the group to the given value.

        Parameters
        ----------
        opacity: float
            The the objects opacity from 0.0 - 1.0 (0% - 100%).
        force: bool
            Force to set the opacity attribute even if it is not present at the moment.
        """
        for group in self.groups.values():
            group.set_stroke_opacity_of_all_objects(opacity, force)

        for object in self.objects.values():
            object.set_stroke_opacity(opacity, force)


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

    logm = logging.getLogger(f"{__name__}.lay")

    def __init__(self, layer_element: Element, parent_layer_path: Optional[str], level=0):
        """
        Parameters
        ----------
        layer_element: Element
           ElementTree Element that represents the layer
        parent_layer_path: Optional[str]
            Path of the parent layer to build up the path of this layer. If not provided, the layer is treated as the
            root layer, which results in a layer path equal to '/'.
        """
        super().__init__(layer_element, level)
        self.layer_element: Element = layer_element
        if parent_layer_path:
            self.layer_name = layer_element.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
            self.layer_path = f"/{self.layer_name}" if parent_layer_path == "/" else "/".join([parent_layer_path, self.layer_name])
        else:
            self.layer_name = "/"
            self.layer_path = "/"
        self.layers: OrderedDict[str, Layer] = self.__parse_layers()

    def __str__(self):
        return f"Layer: name={self.layer_name}"

    def __parse_layers(self) -> OrderedDict[str, "Layer"]:
        layer_dict: OrderedDict[str, Layer] = OrderedDict()

        self.log_hirarchical(self.logm, 'Parse layer "%s" for sub-layers:', self.layer_path)
        for group_element in self.layer_element.findall("{http://www.w3.org/2000/svg}g"):
            groupmode = group_element.get("{http://www.inkscape.org/namespaces/inkscape}groupmode")
            if groupmode and groupmode == "layer":
                self.log_hirarchical(
                    self.logm,
                    '- Found layer: name="%s", id="%s"',
                    group_element.attrib["{http://www.inkscape.org/namespaces/inkscape}label"],
                    group_element.attrib["id"],
                )
                layer = Layer(group_element, self.layer_path, self.level + 1)
                layer_dict[layer.layer_name] = layer

        if len(layer_dict) == 0:
            self.log_hirarchical(self.logm, "- None")

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

    def get_all_layer_paths(self, _recursive_call=False) -> List[str]:
        """
        Get all layer paths of the sublayers.

        Returns
        -------
        List[str]
            List of all the layer paths of the sublayer.
        """
        if not _recursive_call:
            self.logm.debug('Get all layer paths of layer "%s"', self.layer_path)

        layer_paths: List[str] = [self.layer_path]
        for layer in self.layers.values():
            layer_paths.extend(layer.get_all_layer_paths(_recursive_call=True))

        if not _recursive_call:
            self.logm.debug("Layer paths: %s", layer_paths)
        return layer_paths

    def remove_all_layers(self) -> None:
        """
        Remove all sub layers from layer.
        """
        self.logm.debug("Remove all sub-layers of layer: %s", self.layer_path)
        for layer in self.layers.values():
            self.logm.debug(" - Remove layer: %s", layer.layer_name)
            self.layer_element.remove(layer.layer_element)
        self.layers.clear()

    def remove_all_objects_and_groups(self) -> None:
        """
        Remove all objects and groups from layer.
        """
        self.logm.debug("Remove all objects and groups of layer: %s", self.layer_path)

        if len(self.objects) == 0 and len(self.groups) == 0:
            self.logm.debug(" - None")

        for object in self.objects.values():
            self.logm.debug(" - Removing object: %s", object.id)
            self.layer_element.remove(object.object_element)
        for group in self.groups.values():
            self.logm.debug(" - Removing group: %s", group.id)
            self.layer_element.remove(group.group_element)
        self.objects.clear()
        self.groups.clear()

    def remove_layers_if_path_not_matching(self, whitelist_paths: List[str], _recursive_call=False) -> None:
        """
        Remove layers recursively (the layer itself and all sublayers)
        if their path is not in the list of paths.

        Parameters
        ----------
        whitelist_paths: List[str]
            List of paths that should not be removed

        """
        if not _recursive_call:
            self.logm.debug("Remove layers recursively if path not in whitelist: path=%s, whitelist=%s", self.layer_path, whitelist_paths)

        layers_to_remove: List["Layer"] = []
        for layer in self.layers.values():
            remove_layer = True
            for whitelist_path in whitelist_paths:
                if whitelist_path.startswith(layer.layer_path):
                    remove_layer = False
                    break

            if remove_layer:
                layers_to_remove.append(layer)

            layer.remove_layers_if_path_not_matching(whitelist_paths, _recursive_call=True)

        for layer_to_remove in layers_to_remove:
            self.layer_element.remove(layer_to_remove.layer_element)
            del self.layers[layer_to_remove.layer_name]

        if self.layer_path != "/" and self.layer_path not in whitelist_paths:
            self.logm.debug("Remove layer: %s", self.layer_path)
            self.remove_all_objects_and_groups()

    def fill_all_objects(self, color: str, force=False, recursive=False, _recursive_call=False) -> None:
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
        if not _recursive_call:
            self.logm.debug('Fill all objects: layer="%s", color="%s", force=%s, recursive=%s', self.layer_path, color, force, recursive)

        super().fill_all_objects(color, force)

        if recursive:
            for layer in self.layers.values():
                layer.fill_all_objects(color, force=force, recursive=recursive, _recursive_call=True)

    def stroke_paint_all_objects(self, color: str, force=False, recursive=False, _recursive_call=False) -> None:
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
        if not _recursive_call:
            self.logm.debug('Stroke paint all objects: layer="%s", color="%s", force=%s, recursive=%s', self.layer_path, color, force, recursive)
        super().stroke_paint_all_objects(color, force=force)

        if recursive:
            for layer in self.layers.values():
                layer.stroke_paint_all_objects(color, force=force, recursive=recursive, _recursive_call=True)

    def set_visibility(self, visibility: bool, recursive=False, _recursive_call=False) -> None:
        """
        Set the visibility of a specific layer and its children (when recursive flag is set)

        Parameters
        ----------
        visibility: bool
            Visibility to set for layer.
        recursive: bool
            Flag to enable recursive modification of visibility.

        """
        if not _recursive_call:
            self.logm.debug('Set visibility: layer="%s", visibility=%s, recursive=%s', self.layer_path, visibility, recursive)

        if recursive:
            for layer in self.layers.values():
                layer.set_visibility(visibility, recursive, _recursive_call=True)

        if "style" in self.layer_element.attrib:
            self.logm.debug('"style" attribute detected. Preserving other style parameters.')
            style = self.layer_element.attrib["style"]
            style_dict = OrderedDict(item.split(":") for item in style.split(";"))

            style_dict["display"] = "inline" if visibility else "none"
            self.layer_element.attrib["style"] = ";".join([f"{key}:{value}" for key, value in style_dict.items()])


class Image(Layer):
    """
    Represents an Inkscape SVG image.

    Attributes
    ----------
    element_tree: ElementTree
        ElementTree that represents the image.

    """

    logm = logging.getLogger(f"{__name__}.img")

    @classmethod
    def load_from_file(cls, file_path: Path) -> "Image":
        """
        Load a SVG image from file.

        Parameters
        ----------
        file_path: Path
            Path of file to load.

        Returns
        -------
        Image
            Loaded image.

        """
        cls.logm.debug("Load image from file: %s", file_path)
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
        cls.logm.debug("Load image from string")
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
        self.logm.debug('Extract layer: path="%s", preserve_layer_path=%s', path, preserve_layer_paths)
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
        self.logm.debug('Extract layers: paths="%s", preserve_layer_path=%s', paths, preserve_layer_paths)

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
        self.logm.debug("Extract all layers")
        layer_path_list = self.get_all_layer_paths()
        return dict((layer_path, self.extract_layer(layer_path)) for layer_path in layer_path_list)

    def extract_all_layers_to_file(self, output_dir: Path, base_name: str) -> Dict[str, Path]:
        """
        Extract all layers to file by providing an output directory and a base name for
        the extracted layers output file names.

        Parameters
        ----------
        output_dir: Path
            Output directory to write files to.
        base_name: str
            Base name of the files that will be saved.
        Returns
        -------
        dict[str, Path]
            Dictionary with file paths by layer paths.
        """
        self.logm.debug("Extract all layers to file")
        extracted_layer_file_paths_by_layer_path: Dict[str, Path] = {}
        extracted_images = self.extract_all_layers()
        for layer_path, extracted_image in extracted_images.items():
            if layer_path == "/":
                output_file_path = Path(output_dir) / f"{base_name}.svg"
            else:
                output_file_path = Path(output_dir) / f'{base_name}{layer_path.replace("/", "_")}.svg'
            self.logm.debug('Saving layer "%s" to file "%s"', layer_path, output_file_path)
            extracted_image.save(output_file_path)
            extracted_layer_file_paths_by_layer_path[layer_path] = output_file_path
        return extracted_layer_file_paths_by_layer_path

    def extract_all_layers_to_file_lazy(self, output_dir: Path, base_name: str, input_file_path: Path) -> Dict[str, Path]:
        """
        Extract all layers to file by providing an output directory and a base name for
        the extracted layers output file names.
        Only write output to file when either the output file is not yet existing or the input files modification
        timestamp is more recent than the output file timestamp (comparable with GNU makes timestamp check).

        Parameters
        ----------
        output_dir: Path
            Output directory to write files to.
        base_name: str
            Base name of the files that will be saved.
        input_file_path: Path
            The input file path to determine the change timestamp.
        Returns
        -------
        dict[str, Path]
            Dictionary with file paths by layer paths.
        """
        self.logm.debug("Extract all layers to file (lazy)")
        extracted_layer_file_paths_by_layer_path: Dict[str, Path] = {}
        extracted_images = self.extract_all_layers()
        for layer_path, extracted_image in extracted_images.items():

            if layer_path == "/":
                output_file_path = Path(output_dir) / f"{base_name}.svg"
            else:
                output_file_path = Path(output_dir) / f'{base_name}{layer_path.replace("/", "_")}.svg'
            if output_file_path.exists() is False:
                self.logm.debug("Output file not yet existing. Save file!")
                extracted_image.save(output_file_path)
            elif os.path.getmtime(input_file_path) > os.path.getmtime(output_file_path):
                self.logm.debug("Input file modification timestamp more recent than output file modification timestamp. Save file!")
                extracted_image.save(output_file_path)
            else:
                self.logm.debug("Output file up-to-date. Skip!")
            extracted_layer_file_paths_by_layer_path[layer_path] = output_file_path
        return extracted_layer_file_paths_by_layer_path

    def save(self, path: Path) -> None:
        """
        Save image to file.

        Parameters
        ----------
        path: Path
            File location to write image to.
        """
        self.logm.debug("Save image to file: %s", path)
        path.parent.mkdir(exist_ok=True)
        self.element_tree.write(path)
