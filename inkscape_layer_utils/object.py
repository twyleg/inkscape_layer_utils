from typing import List
from collections import OrderedDict
from xml.etree.ElementTree import Element


class Object:
    def __init__(self, object_element: Element) -> None:
        self.object_element = object_element
        self.tag = object_element.tag
        self.id = object_element.get('id')

    def __str__(self) -> str:
        return f'Object: tag={self.tag}, id={self.id}'

    def set_fill_color(self, color: str) -> str:
        style = self.object_element.attrib['style']
        style_dict = OrderedDict(item.split(':') for item in style.split(';'))
        style_dict['fill'] = color
        self.object_element.attrib['style'] = ';'.join([f'{key}:{value}' for key, value in style_dict.items()])



def parse_objects(parent_element: Element) -> OrderedDict[str, Object]:
    object_dict: OrderedDict[str, Object] = OrderedDict()

    for element in parent_element:
        if not element.tag == '{http://www.w3.org/2000/svg}g':
            object = Object(element)
            object_dict[object.id] = object

    return object_dict
