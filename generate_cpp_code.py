#!/usr/bin/python3

import os
import random
import shutil
import string
import sys

primitive_types = ('char', 'int', 'short', 'unsigned', 'float', 'double')

class CppClassProperties():
    headers_to_use: list[str] = []
    headers_available = ('iostream', 'vector', 'map', 'unordered_map', 'array',
                         'list', 'stack', 'queue', 'deque', 'string',
                         'random', 'bitset', 'regex', 'thread')
    # adding 'memory' to the list above creates compilation problems
    max_num_public_functions = 20
    max_num_private_functions = 20
    max_num_members_per_internal_type = 2
    max_num_members_per_stl_type = 30
    classes_to_refer: list[str] = []

    def randomly_choose_headers(self) -> None:
        """ randomly selects a list of headers to use out of the ones supported (headers_available) """
        self.headers_to_use = random.sample(self.headers_available, k=random.randint(0, len(self.headers_available)))


def generate_member(member_base_name: str, header_to_use: str, available_headers: list[str],
                    num_members: int = 1, num_lines_comment: int = 0) -> str:
    header_code = ''
    for n in range(0, num_members):
        member_code = ''
        if header_to_use in ('vector', 'list', 'stack', 'queue', 'deque'):
            member_code += f'std::{header_to_use}<' + random.choice(primitive_types) + '>'
        elif header_to_use in ('map', 'unordered_map'):
            member_code += f'std::{header_to_use}<' + random.choice(primitive_types) + ', ' + random.choice(primitive_types) + '>'
        elif header_to_use == 'array':
            member_code += 'std::array<' + random.choice(primitive_types) + ', ' + str(random.randint(1, 5000)) + '>'
        elif header_to_use in ('string', 'regex', 'thread'):
            member_code += 'std::' + header_to_use
        elif header_to_use == 'memory':
            member_code += 'std::' + random.choice(('shared_ptr', 'weak_ptr', 'unique_ptr')) + f'<{random.choice(primitive_types)}>'
        elif header_to_use == 'bitset':
            member_code += 'std::bitset<' + str(random.randint(1,5000)) + '>'
        elif header_to_use.startswith('Class'):
            member_code += header_to_use

        if member_code:
            for k in range(0, num_lines_comment):
                header_code += f'    // some random doxygen docu {k}\n'
            header_code += f'    {member_code} {member_base_name}_{n}{{}};\n'
    return header_code


def generate_function_prototype(function_number: int, max_name_len: int = 20, max_num_arguments: int = 5) -> str:
    function_name = ''.join(random.choices(list(string.ascii_lowercase), k=random.randint(1, max_name_len)))
    function_prototype = f'{random.choice(primitive_types)} {function_name}{function_number}('
    function_arguments = []
    for argument_type in random.choices(primitive_types, k=random.randint(0,max_num_arguments)):
        function_arguments.append(argument_type)
    function_prototype += ', '.join(function_arguments) + ')'
    return function_prototype


def generate_cpp_class(class_name: str, properties: CppClassProperties):
    header_code = '#pragma once\n'

    for header in sorted(properties.headers_to_use):
        header_code += f'#include <{header}>\n'
    header_code += '\n'

    for class_to_refer in sorted(properties.classes_to_refer):
        header_code += f'#include "{class_to_refer}.h"\n'
    header_code += '\n'

    header_code += f"""class {class_name}
{{
public:
    {class_name}() = default;
    ~{class_name}() = default;

"""

    functions = []
    for n in range(0, random.randint(0, properties.max_num_public_functions)):
        function_prototype = generate_function_prototype(n)
        functions.append(function_prototype)
        header_code += '    ' + function_prototype + ';\n'

    header_code += '\nprivate:\n'

    for n in range(1, random.randint(0, properties.max_num_private_functions)):
        function_prototype = generate_function_prototype(n)
        functions.append(function_prototype)
        header_code += '    ' + function_prototype + ';\n'

    header_code += '\n'

    for class_index, class_to_refer in enumerate(properties.classes_to_refer):
        header_code += generate_member(f'm_member_internal{class_index}', class_to_refer, properties.headers_to_use,
                                       random.randint(1, properties.max_num_members_per_internal_type), random.randint(0, 3))

    for class_index, header in enumerate(properties.headers_to_use):
        header_code += generate_member(f'm_member_stl{class_index}', header, properties.headers_to_use,
                                       random.randint(1, properties.max_num_members_per_stl_type), random.randint(0, 3))

    header_code += '};\n'

    cpp_code = f'#include "{class_name}.h"\n\n'

    for function in functions:
        return_type, function_name_and_args = function.split(' ', 1)
        cpp_code += f'{return_type} {class_name}::{function_name_and_args}\n{{\n    return 0;\n}}\n\n'

    return header_code, cpp_code


def transform_cpp_code_to_module(cpp_code: str, class_name: str):
    cpp_code = cpp_code.replace(f'#include "{class_name}.h"', f'module {class_name.lower()};')
    cpp_code = cpp_code.replace('#include "C', 'import c')
    cpp_code = cpp_code.replace('.h"', ';')
    return cpp_code


def transform_header_code_to_module(header_code: str, class_name: str):
    header_code = header_code.replace(f'#pragma once', f'module;')
    header_code = header_code.replace('#include "C', 'import c')
    header_code = header_code.replace('.h"', ';')
    header_code = header_code.replace(f'class {class_name}', f'export module {class_name.lower()};\n\nexport class {class_name}')
    return header_code


def write_code_to_files(output_directory: str, class_name: str, cpp_code: str, header_code: str,
                        cpp_code_module: str, module_interface_code: str):
    header_file_path = os.path.join(output_directory, f"{class_name}.h")
    cpp_file_path = os.path.join(output_directory, f"{class_name}.cpp")

    with open(header_file_path, 'w') as header_file:
        header_file.write(header_code)

    with open(cpp_file_path, 'w') as cpp_file:
        cpp_file.write(cpp_code)

    module_interface_file_path = os.path.join(output_directory, f"{class_name}.cppm")
    cpp_module_file_path = os.path.join(output_directory, f"{class_name}_module.cpp")

    with open(module_interface_file_path, 'w') as module_interface_file:
        module_interface_file.write(module_interface_code)

    with open(cpp_module_file_path, 'w') as cpp_module_file:
        cpp_module_file.write(cpp_code_module)


def generate_cpp_files(output_directory: str, num_classes: int, layer: int=0,
                       dependable_classes: list[str] = [], dependency_type: str='unknown') -> list[str]:
    """Generate C++ files with classes that use standard containers."""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    generated_classes = []

    for i in range(num_classes):
        class_name = f"Class{layer}_{i}"
        properties = CppClassProperties()
        properties.randomly_choose_headers()

        if len(dependable_classes) > 0:
            if dependency_type == 'rand':
                properties.classes_to_refer = random.sample(dependable_classes, random.randint(1, len(dependable_classes)))
            elif dependency_type == 'all':
                properties.classes_to_refer = dependable_classes
            else:
                print(f'Unknown dependency type "{dependency_type}"')
                sys.exit(1)

            if isinstance(properties.classes_to_refer, str):
                properties.classes_to_refer = [properties.classes_to_refer]

        # generate header and implementation of class "class_name"
        header_code, cpp_code = generate_cpp_class(class_name, properties)

        # transform the code into a module-compliant variant
        cpp_code_module = transform_cpp_code_to_module(cpp_code, class_name)
        module_interface_code = transform_header_code_to_module(header_code, class_name)

        write_code_to_files(output_directory, class_name, cpp_code, header_code, cpp_code_module, module_interface_code)

        generated_classes.append(class_name)

    return generated_classes


def generate_main_files(output_directory: str, *generated_classes):
    main_code_headers = ''
    main_code_modules = ''

    for list_of_classes in generated_classes:
        for generated_class in list_of_classes:
            main_code_headers += f'#include "{generated_class}.h"\n'
            main_code_modules += f'import {generated_class.lower()};\n'

    main_code_headers += '\n\nint main()\n{\n'
    main_code_modules += '\n\nint main()\n{\n'

    n = 0
    for list_of_classes in generated_classes:
        for generated_class in list_of_classes:
            main_code_headers += f'    {generated_class} c{n}{{}};\n'
            main_code_modules += f'    {generated_class} c{n}{{}};\n'
            n += 1

    main_code_headers += '\n    return 0;\n}\n'
    main_code_modules += '\n    return 0;\n}\n'

    main_file_headers_path = os.path.join(output_directory, 'main_headers.cpp')
    main_file_modules_path = os.path.join(output_directory, 'main_modules.cpp')

    with open(main_file_headers_path, 'w') as f:
        f.write(main_code_headers)

    with open(main_file_modules_path, 'w') as f:
        f.write(main_code_modules)


if __name__ == "__main__":
    output_directory = "generated_cpp_files_n_n"
    shutil.rmtree(output_directory)
    classes1 = generate_cpp_files(output_directory, 10, 0)
    classes2 = generate_cpp_files(output_directory, 10, 1, classes1, 'all')
    shutil.copy('CMakeLists.txt.prototype', f'{output_directory}/CMakeLists.txt')
    shutil.copy('CMakePresets.json.prototype', f'{output_directory}/CMakePresets.json')
    generate_main_files(output_directory, classes1, classes2)
    print(f"C++ files generated in '{output_directory}'.")

    output_directory = "generated_cpp_files_1_n"
    shutil.rmtree(output_directory)
    classes1 = generate_cpp_files(output_directory, 10, 0)
    classes2 = generate_cpp_files(output_directory, 1, 1, classes1, 'all')
    shutil.copy('CMakeLists.txt.prototype', f'{output_directory}/CMakeLists.txt')
    shutil.copy('CMakePresets.json.prototype', f'{output_directory}/CMakePresets.json')
    generate_main_files(output_directory, classes1, classes2)
    print(f"C++ files generated in '{output_directory}'.")

    output_directory = "generated_cpp_files_n_1"
    shutil.rmtree(output_directory)
    classes1 = generate_cpp_files(output_directory, 10, 0)
    classes2 = generate_cpp_files(output_directory, 1, 1, random.choice(classes1), 'all')
    shutil.copy('CMakeLists.txt.prototype', f'{output_directory}/CMakeLists.txt')
    shutil.copy('CMakePresets.json.prototype', f'{output_directory}/CMakePresets.json')
    generate_main_files(output_directory, classes1, classes2)
    print(f"C++ files generated in '{output_directory}'.")

    output_directory = "generated_cpp_files_n_n_rand"
    shutil.rmtree(output_directory)
    classes1 = generate_cpp_files(output_directory, 10, 0)
    classes2 = generate_cpp_files(output_directory, 10, 1, classes1, 'rand')
    shutil.copy('CMakeLists.txt.prototype', f'{output_directory}/CMakeLists.txt')
    shutil.copy('CMakePresets.json.prototype', f'{output_directory}/CMakePresets.json')
    generate_main_files(output_directory, classes1, classes2)
    print(f"C++ files generated in '{output_directory}'.")
