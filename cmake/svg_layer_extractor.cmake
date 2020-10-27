set(script ${CMAKE_CURRENT_LIST_DIR}/../app/extract_svg_layers.py)

function(EXTRACT_SVG_LAYERS)
	
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
			python ${script} -o ${output_dir} ${input_file} --qrc svg_multilayer_extracted.qrc
		)

		execute_process(
			COMMAND python ${script} -o ${output_dir} ${input_file} --qrc svg_multilayer_extracted.qrc
		)
	endforeach()

endfunction()
