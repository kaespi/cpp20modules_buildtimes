#!/usr/bin/python3

import os
import re
import subprocess
import sys


script_path = os.path.dirname(os.path.abspath(__file__))


def build_project(folder: str):
    os.chdir(folder)
    presets = list_presets()

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


if __name__ == "__main__":
    for folder in sys.argv[1:]:
        abs_folder = os.path.abspath(os.path.join(script_path, folder))
        for foldername, subfolders, filenames in os.walk(abs_folder):
            if 'CMakeLists.txt' in filenames:
                build_project(foldername)
