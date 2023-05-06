# Copyright (C) 2023 twyleg
import xml.etree.ElementTree as ET

from . import _version

ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ET.register_namespace("cc", "http://creativecommons.org/ns#")
ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")


__version__ = _version.get_versions()["version"]
