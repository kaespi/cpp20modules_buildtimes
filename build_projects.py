#!/usr/bin/python3

import argparse
import os
import re
import subprocess


script_path = os.path.dirname(os.path.abspath(__file__))


def build_project(folder: str, preset: str='all'):
    os.chdir(folder)
    if preset=='all':
        presets = list_presets()
    else:
        presets = [preset]

    for preset in presets:
        print(f'Building {folder}, preset {preset}...')
        execute_shell_command(f'kcmake --preset {preset}')
        execute_shell_command(f'kcmake --build --preset {preset}')


def list_presets() -> list[str]:
    presets = []
    regex_pattern = r'\s+"([^"]+)"\s+-\s+.*'
    presets_cmd_out = execute_shell_command('kcmake --list-presets')
    for line in presets_cmd_out:
        match = re.match(regex_pattern, line)
        if match:
            presets.append(match.group(1))

    return presets


def execute_shell_command(command: str) -> list[str]:
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().splitlines()
        else:
            print(f"Error executing command: {result.stdout.strip()} {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser(description='Build the generated C++20 modules code using CMake.')
    parser.add_argument('--preset', type=str, default='all',
                        help='CMake preset to build (default: "all", meaning all presets are built)')
    parser.add_argument('folders', nargs='+', help='List of folders to scan for CMake projects')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    for folder in args.folders:
        abs_folder = os.path.abspath(os.path.join(script_path, folder))
        for foldername, subfolders, filenames in os.walk(abs_folder):
            if 'CMakeLists.txt' in filenames:
                build_project(foldername, args.preset)
