#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

python -m venv venv
source venv/bin/activate
pip install $SCRIPT_DIR/../..

inkscape_layer_utils -vv extract_layers -o output/ ../../resources/test_images/*