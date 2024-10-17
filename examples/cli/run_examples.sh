#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
STDOUT_DIR=stdout

cd $SCRIPT_DIR

python -m venv venv
source venv/bin/activate
pip install $SCRIPT_DIR/../..

mkdir -p $STDOUT_DIR

#
# Help
#

inkscape_layer_utils --help > $STDOUT_DIR/help.output
inkscape_layer_utils list_layers --help > $STDOUT_DIR/help_list_layers.output
inkscape_layer_utils extract_layers --help > $STDOUT_DIR/help_extract_layers.output

#
# List layers
#

inkscape_layer_utils list_layers ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths.output
inkscape_layer_utils list_layers --json ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_json.output

inkscape_layer_utils list_layers --print ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_print.output
inkscape_layer_utils list_layers --print --json ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_print_json.output
inkscape_layer_utils --quiet list_layers --print --json ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_print_json_quiet.output

inkscape_layer_utils -vv list_layers ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_verbose.output
inkscape_layer_utils -vv list_layers --json ../../resources/test_images/* > $STDOUT_DIR/list_layer_paths_json_verbose.output


#
# Extract layers
#

inkscape_layer_utils -vv extract_layers -o output/ ../../resources/test_images/* > $STDOUT_DIR/extract_layers_verbose.output


echo -e "\nResults can be found in \"$STDOUT_DIR\""