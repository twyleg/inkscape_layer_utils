# Copyright (C) 2023 twyleg
import json
import os
import sys
import argparse
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from typing import List

from inkscape_layer_utils import __version__
from inkscape_layer_utils.image import Image


def extract_layers() -> None:
    parser = argparse.ArgumentParser(prog="inkscape_layer_utils extract_layers")
    parser.add_argument(
        "svg_files",
        metavar="svg_files",
        type=str,
        nargs="+",
        help="SVG image file(s) to extract the layers from.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=os.path.join(os.getcwd(), "output"),
        help='Output directory for extracted layers. Default="./"',
    )

    args = parser.parse_args(sys.argv[2:])

    for svg_file_path in args.svg_files:
        svg_file_element_tree = ET.parse(svg_file_path)
        svg_image = Image(svg_file_element_tree)
        svg_image.extract_all_layers_to_file(args.output, Path(svg_file_path).stem)


def list_layers() -> None:
    parser = argparse.ArgumentParser(prog="inkscape_layer_utils list_layers")
    parser.add_argument(
        "svg_files",
        metavar="svg_files",
        type=str,
        nargs="+",
        help="SVG image file(s) to extract the layers from.",
    )
    parser.add_argument("-j", "--json", action="store_true")
    args = parser.parse_args(sys.argv[2:])

    layers_by_svg_file_path: OrderedDict[str, List[str]] = OrderedDict()
    for svg_file_path in args.svg_files:
        svg_file_element_tree = ET.parse(svg_file_path)
        svg_image = Image(svg_file_element_tree)
        layers_by_svg_file_path[svg_file_path] = svg_image.get_all_layer_paths()

    if args.json:
        print(json.dumps(layers_by_svg_file_path, indent=4))
    else:
        for svg_file_path, layer_paths in layers_by_svg_file_path.items():
            print(f"File: {svg_file_path}")
            for layer_path in layer_paths:
                print(f"  {layer_path}")


def main() -> None:
    parser = argparse.ArgumentParser(usage="inkscape_layer_utils <command> [<args>] <track_file>")
    parser.add_argument("command", help="track_generator commands")
    parser.add_argument(
        "-v",
        "--version",
        help="show version and exit",
        action="version",
        version=__version__,
    )
    args = parser.parse_args(sys.argv[1:2])

    match args.command:
        case "extract_layers":
            extract_layers()
        case "list_layers":
            list_layers()


if __name__ == "__main__":
    main()
