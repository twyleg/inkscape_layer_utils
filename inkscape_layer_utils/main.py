# Copyright (C) 2024 twyleg
import json
import os
import argparse
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from typing import List

from simple_python_app.subcommand_application import SubcommandApplication

from inkscape_layer_utils import __version__
from inkscape_layer_utils.image import Image


FILE_DIR = Path(__file__).parent


class InkscapeLayerUtils(SubcommandApplication):
    def __init__(self):
        super().__init__(
            application_name="inkscape_layer_utils",
            version=__version__,
            application_config_init_enabled=False,
            logging_init_custom_logging_enabled=False,
            logging_logfile_output_dir=FILE_DIR / "logs/",
        )

    def add_arguments(self, argparser: argparse.ArgumentParser) -> None:
        # fmt: off
        extract_layers_command = self.add_subcommand(
            command="extract_layers",
            help="",
            description="Counter going upwards with multiple parameters.",
            handler=self._handle_extract_layers
        )

        extract_layers_command.parser.add_argument(
            "-o",
            "--output",
            dest="output",
            default=os.path.join(os.getcwd(), "output"),
            help='Output directory for extracted layers. Default="./"',
        )

        list_layers_command = self.add_subcommand(
            command="list_layers",
            help="Counter going downwards",
            description="Counter going downwards with multiple parameters.",
            handler=self._handle_list_layers
        )

        list_layers_command.parser.add_argument(
            "-j",
            "--json",
            action="store_true"
        )
        # fmt: on

        for command in [extract_layers_command, list_layers_command]:
            command.parser.add_argument(
                "svg_files",
                metavar="svg_files",
                type=str,
                nargs="+",
                help="SVG image file(s) to extract the layers from.",
            )

    def _handle_extract_layers(self, args: argparse.Namespace) -> int:

        for svg_file_path in args.svg_files:
            svg_file_element_tree = ET.parse(svg_file_path)
            svg_image = Image(svg_file_element_tree)
            svg_image.extract_all_layers_to_file(args.output, Path(svg_file_path).stem)

        return 0

    def _handle_list_layers(self, args: argparse.Namespace) -> int:

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

        return 0


def main() -> None:
    inkscape_layer_utils = InkscapeLayerUtils()
    inkscape_layer_utils.start()


if __name__ == "__main__":
    main()
