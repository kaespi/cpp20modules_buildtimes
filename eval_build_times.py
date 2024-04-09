#!/usr/bin/python3

import os
import re
import sys

def eval_folder(folder: str):
    for foldername, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            if filename == ".ninja_log":
                file_path = os.path.join(foldername, filename)
                build_times_ms = parse_ninja_log_file(file_path)
                print(file_path)
                for k,v in build_times_ms.items():
                    print(f'{k}: {v}ms')


def parse_ninja_log_file(file_path: str) -> dict:
    total_build_time_ms = { 'headers': 0, 'modules': 0 }
    with open(file_path, 'r') as file:
        regex_pattern = r'(\d+)\s+(\d+)\s+\d+\s+CMakeFiles/libclasses_(headers|modules)\.dir.*'
        for line in file.readlines():
            match = re.match(regex_pattern, line)
            if match:
                time_ms = int(match.group(2)) - int(match.group(1))
                total_build_time_ms[match.group(3)] += time_ms

    return total_build_time_ms


if __name__ == "__main__":
    for folder in sys.argv[1:]:
        eval_folder(folder)
