#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

python -m venv venv
source venv/bin/activate
pip install $SCRIPT_DIR/../..

inkscape_layer_utils -vv list_layers ../../resources/test_images/*
inkscape_layer_utils -vv list_layers --json ../../resources/test_images/*
