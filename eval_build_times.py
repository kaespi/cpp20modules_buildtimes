#!/usr/bin/python3

import os
import re
import sys

def eval_folder(folder: str):
    for foldername, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            if filename == ".ninja_log":
                ninja_log_path = os.path.join(foldername, filename)
                build_times_ms = parse_ninja_log_file(ninja_log_path)
                print(ninja_log_path)
                for k,v in build_times_ms.items():
                    print(f'{k}: {v}ms')


def parse_ninja_log_file(file_path: str) -> dict:
    total_build_time_ms = { 'headers': 0, 'modules': 0 }
    with open(file_path, 'r') as file:
        parsed_hashes = {}
        regex_pattern_lib = r'(\d+)\s+(\d+)\s+\d+\s+CMakeFiles/libclasses_(headers|modules)\.dir.*\s+([0-9a-f]+)$'
        regex_pattern_main = r'(\d+)\s+(\d+)\s+\d+\s+CMakeFiles/main_(headers|modules).*\s+([0-9a-f]+)$'
        for line in file.readlines():
            match = re.match(regex_pattern_lib, line)
            if not match:
                # try the other regex (main files)
                match = re.match(regex_pattern_main, line)
            if match:
                build_action_hash = match.group(4)
                if build_action_hash not in parsed_hashes:
                    time_ms = int(match.group(2)) - int(match.group(1))
                    total_build_time_ms[match.group(3)] += time_ms
                    parsed_hashes[build_action_hash] = 1

    return total_build_time_ms


if __name__ == "__main__":
    for folder in sys.argv[1:]:
        eval_folder(folder)
