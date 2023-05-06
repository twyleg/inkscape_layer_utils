#!/usr/bin/env bash

python -m venv venv
source venv/bin/activate
pip install inkscape_layer_utils

inkscape_layer_utils extract_layers -o output/ ../../resources/test_images/*