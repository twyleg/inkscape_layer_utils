cmake_minimum_required(VERSION 3.17)

include(../cmake/inkscape_svg_layer_extractor.cmake)

EXTRACT_INKSCAPE_SVG_LAYERS(
	INPUT_FILES
        example_graphic_1.svg
        example_graphic_2.svg
	OUTPUT_DIR
	    extracted_layers
)
