# C++20 Modules - Build Times Analysis

This is a repo aiming at profiling build times using C++20 modules using the Clang compiler.

To offer a generic profiling the C++ code is generated (some random code). The same code is implemented twice, with modules and with plain old headers. The time it takes to compile the two can then be compared.

## Usage

**Step 1** Generate the C++ code

```bash
./generate_cpp_code.py
```

The tested configurations can be found at the very bottom of this script. Customize it up to your desires.

This generates C++ code (incl. CMake presets and configuration) in the subfolders `generated_cpp_files_...`.

**Step 2** Build the C++ code

Using Ninja and Clang-17 and 18 the projects are compiled with the script

```bash
./build_projects.py generated_cpp_files*
```

(only a selection of folders can be chosen to be built with the command line arguments)

**Step 3** Build time analysis

The time it takes to build the projects is evaluated using

```bash
./eval_build_times.py generated_cpp_files_*
```

Essentially this scans all the folders for the `.ninja_log` and accumulates the build times for each intermediate file (`.o`, `.o.modmap`, `.ddi` files). Since each file shows up individually this works even if CMake distributed the compilation to a number of CPU cores.

The statistics are then printed on stdout.

## Visualization

To facilitate the visualization of the different projects, in each folder with the generated C++ code, there's a `dependencies.puml` file. That's a PlantUML file visualizing the dependencies between files (i.e. classes).
