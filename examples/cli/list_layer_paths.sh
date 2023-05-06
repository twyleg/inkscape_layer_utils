#!/usr/bin/env bash

python -m venv venv
source venv/bin/activate
pip install inkscape_layer_utils

inkscape_layer_utils list_layers ../../resources/test_images/*
inkscape_layer_utils list_layers --json ../../resources/test_images/*
