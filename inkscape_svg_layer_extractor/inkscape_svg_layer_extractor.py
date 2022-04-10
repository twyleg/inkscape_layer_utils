#! /usr/bin/python3

# Inspired by
# https://github.com/james-bird/layer-to-svg/blob/master/layer2svg.py

import xml.etree.ElementTree as ET
import copy
import os
import argparse
from shutil import copyfile
from pathlib import Path

force = False
verbose = False
qrc_path = None


def is_input_file_dirty(input_file_path, output_file_path):
    try:
        input_file_timestamp = os.path.getmtime(input_file_path)
        output_file_timestamp = os.path.getmtime(output_file_path)
    except OSError:
        # Output file doesn't exist yet therefore return true
        return True

    if output_file_timestamp > input_file_timestamp:
        return False
    else:
        return True


def write_qrc_file(svg_output_directory, qrc_filename):

    qrc_file = open(os.path.join(svg_output_directory, qrc_filename), 'w')

    qrc_file.write('<RCC>\n')
    qrc_file.write('\t<qresource prefix = "/svg-multilayer-extracted">\n')

    svg_output_files_search_results = sorted(Path(svg_output_directory).glob('**/*.svg'))
    for svg_output_file in svg_output_files_search_results:
        qrc_file.write('\t\t<file>{}</file>\n'.format(os.path.basename(svg_output_file)))

    qrc_file.write('\t</qresource>\n')
    qrc_file.write('</RCC>\n')


def find_layers(current_layer_node):

    new_layer_paths_list = []

    for sublayer_node in current_layer_node.findall('{http://www.w3.org/2000/svg}g'):
        # Call function recursively to extract sublayer if available
        new_layer_paths_list.extend(find_layers(sublayer_node))

    current_layer_name = current_layer_node.get('{http://www.inkscape.org/namespaces/inkscape}label')

    if current_layer_name is not None:

        for layer_path_list in new_layer_paths_list:
            layer_path_list.insert(0, current_layer_name)

        new_layer_paths_list.append([current_layer_name])

    return new_layer_paths_list


def print_layers(layer_paths_list):

    print('Layers:')
    for layer_path in layer_paths_list:
        layer_path_string = '/'.join(layer_path)
        print('\t' + layer_path_string)


def extract_layers(output_directory, input_file_filename_without_extension, layer_paths_list, input_image_tree):

    for layer_path in layer_paths_list:

        output_image_tree = copy.deepcopy(input_image_tree)
        output_image_tree_root_node = output_image_tree.getroot()

        number_of_layers = len(layer_path)

        #
        # Get first layer from root node
        #
        desired_layer_name = layer_path[0]

        for layer_element in output_image_tree_root_node.findall('{http://www.w3.org/2000/svg}g'):
            layer_name = layer_element.get('{http://www.inkscape.org/namespaces/inkscape}label')
            if layer_name != desired_layer_name:
                output_image_tree_root_node.remove(layer_element)
            else:
                # Found the desired layer, save it to next_layer_node and make it visible
                next_layer_node = layer_element
                next_layer_node.attrib['style'] = 'display:inline'

        #
        # Handle sublayers between root and last layer
        #
        for i in range(1, number_of_layers):

            desired_layer_name = layer_path[i]

            current_layer_node = next_layer_node
            for element in list(current_layer_node):

                # Remove every element (layers and graphical stuff) that isn't the next layer we're loopking for
                element_name = element.get('{http://www.inkscape.org/namespaces/inkscape}label')

                if element_name != desired_layer_name:
                    current_layer_node.remove(element)
                else:
                    # Found the desired layer, save it to next_layer_node and make it visible
                    next_layer_node = element
                    next_layer_node.attrib['style'] = 'display:inline'

        #
        # Handle last layer
        #
        current_layer_node = next_layer_node
#         current_layer_node.attrib['style'] = 'display:inline'
        for layer_element in current_layer_node.findall('{http://www.w3.org/2000/svg}g'):
            layer_name = layer_element.get('{http://www.inkscape.org/namespaces/inkscape}label')
            if layer_name is not None:
                current_layer_node.remove(layer_element)

        otuput_file_filename = input_file_filename_without_extension + '_' + '_'.join(layer_path) + '.svg'
        output_file_path = os.path.join(output_directory, otuput_file_filename)

        # Write new tree
        output_image_tree.write(output_file_path)


def extract_svg_image(input_file_filepath, output_directory):

    # First of all check if input file exists and skip it if not
    if os.path.exists(input_file_filepath) is False:
        print('Warning: input file ' + input_file_filepath + ' doesn\'t exist!')
        return

    # Extract the filename from filepath
    input_file_filename = os.path.basename(input_file_filepath)
    input_file_filename_without_extension = os.path.splitext(input_file_filename)[0]

    # Check if the image was modified since last extraction
    complete_image_output_file_filename = input_file_filename
    complete_image_output_file_filepath = os.path.join(output_directory,complete_image_output_file_filename)

    if force is False and is_input_file_dirty(input_file_filepath, complete_image_output_file_filepath) is False:
        return

    # Create a copy of the complete file in the output directory
    copyfile(input_file_filepath, complete_image_output_file_filepath)

    if verbose:
        print("Extracting file: " + input_file_filepath)

    # Parse XML tree
    input_image_tree = ET.parse(input_file_filepath)
    input_tree_root_node = input_image_tree.getroot()

    #
    # Get a list of all image layers
    #

    layer_paths_list = find_layers(input_tree_root_node)

    if verbose:
        print_layers(layer_paths_list)

    extract_layers(output_directory, input_file_filename_without_extension, layer_paths_list, input_image_tree)

def main():
    global verbose
    global force
    global qrc_path

    if verbose:
        print('SVG Extractor - Started!')
        print('')

        #
        # Register namespace for inkscape
        #
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
    ET.register_namespace("cc", "http://creativecommons.org/ns#")
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace("svg", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
    ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

    #
    # Scan for cli arguments
    #
    parser = argparse.ArgumentParser(description='Extract layers from SVG files.')

    parser.add_argument('paths', metavar='filepath.svg', type=str, nargs='*', default=None,
                        help='Path to SVG file to process.')
    parser.add_argument('-s', '--searchpath', dest='searchpath', default=None,
                        help='Path to search for *.svg files.')
    parser.add_argument('-o', '--output', dest='output', default=os.getcwd(),
                        help='Output directory for generated SVG layer files.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force extraction even if output files are newer than input files.')
    parser.add_argument('--qrc', type=str, dest='qrc_path', nargs='?',
                        help='Output qrc-file path.')

    args = parser.parse_args()

    # Save settings
    verbose = args.verbose
    qrc_path = args.qrc_path
    force = args.force

    #
    # Collect input files
    #
    svg_input_files = []

    # Add explicitly added files
    if args.paths is not None:
        # print('Added files explicitly:')
        for svg_input_file in args.paths:
            print('Extracting SVG: ' + svg_input_file)
            svg_input_files.append(svg_input_file)
    # print('')

    # Search searchpath and add files
    if args.searchpath is not None:
        # print('Added files found in searchpath [' + args.searchpath + "]:")
        svg_input_files_search_results = Path(args.searchpath).glob('**/*.svg')
        for svg_input_file in svg_input_files_search_results:
            print('Extracting SVG files in: ' + str(svg_input_file))
            svg_input_files.append(str(svg_input_file))

    # Print output directory
    svg_output_directory = args.output

    if verbose:
        print('')
        print('Output directory:')
        print('\t' + svg_output_directory)
        print('')

    #
    # Process input files
    #
    for svg_input_file in svg_input_files:
        extract_svg_image(svg_input_file, svg_output_directory)

    #
    # Print .qrc-file entries
    #
    if qrc_path is not None:
        write_qrc_file(svg_output_directory, qrc_path)

if __name__ == "__main__":
    main()
