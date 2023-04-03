import os.path
import xml.etree.ElementTree as ET

from pathlib import Path



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


def set_fill_color(style: str, color: str) -> str:
    style_elements = style.split(';')
    for style_element in style_elements:
        if style_element.startswith('fill:'):
            style_elements[style_elements.index(style_element)] = f'fill:{color}'
    return ';'.join(style_elements)



if __name__ == '__main__':

    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
    ET.register_namespace("cc", "http://creativecommons.org/ns#")
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace("svg", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
    ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")

    # Parse XML tree
    filepath = Path(os.path.dirname(__file__)) / '../output/example_graphic_1_Layer 1.svg'
    input_image_tree = ET.parse(filepath)
    input_tree_root_node = input_image_tree.getroot()

    layers = input_tree_root_node.findall('{http://www.w3.org/2000/svg}g')

    for layer in layers:
        current_layer_name = layer.get('{http://www.inkscape.org/namespaces/inkscape}label')
        print(current_layer_name)
        for children in layer.iter():
            if not children.tag == '{http://www.w3.org/2000/svg}g':
                print(children.attrib['style'])
                children.attrib['style'] = set_fill_color(children.attrib['style'], '#FF0000')
                print(children.attrib['style'])

    print(layers)

    input_image_tree.write(filepath)
