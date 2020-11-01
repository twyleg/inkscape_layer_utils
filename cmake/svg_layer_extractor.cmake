set(script ${CMAKE_CURRENT_LIST_DIR}/../app/extract_svg_layers.py)

function(extract_svg_layers)

	find_package(Python3 REQUIRED COMPONENTS Interpreter)

	if (NOT DEFINED Python3_FOUND)
		message(FATAL_ERROR "Python3 not found. Please check your installation and PATH variable.")
	endif()
	
	set(oneValueArgs OUTPUT_DIR)
	set(multiValueArgs INPUT_FILES)
	cmake_parse_arguments(EXTRACT_SVG_LAYERS "" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

	set(output_dir ${EXTRACT_SVG_LAYERS_OUTPUT_DIR})
	file(MAKE_DIRECTORY ${output_dir})

	foreach(input_file IN LISTS EXTRACT_SVG_LAYERS_INPUT_FILES)

		set(input_file_path ${CMAKE_SOURCE_DIR}/${input_file})
		get_filename_component(input_filename ${input_file} NAME_WE)

		message(STATUS ${input_file})

		add_custom_target(
			${input_filename}
			ALL 
			${Python3_EXECUTABLE} ${script} -o ${output_dir} ${input_file} --qrc svg_multilayer_extracted.qrc
		)

		execute_process(
			COMMAND ${Python3_EXECUTABLE} ${script} -o ${output_dir} ${input_file} --qrc svg_multilayer_extracted.qrc
		)
	endforeach()

endfunction()
