# hatch-cython

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CI/CD   | [![Build](https://github.com/joshua-auchincloss/hatch-cython/actions/workflows/build.yaml/badge.svg)](https://github.com/joshua-auchincloss/hatch-cython/actions) [![Tests](https://github.com/joshua-auchincloss/hatch-cython/actions/workflows/test.yaml/badge.svg)](https://github.com/joshua-auchincloss/hatch-cython/actions)[![codecov](https://codecov.io/gh/joshua-auchincloss/hatch-cython/graph/badge.svg?token=T12ACNLFWV)](https://codecov.io/gh/joshua-auchincloss/hatch-cython) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-cython.svg?logo=pypi&label=PyPI&logoColor=silver)](https://pypi.org/project/hatch-cython/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/hatch-cython.svg?color=blue&label=Downloads&logo=pypi&logoColor=silver)](https://pypi.org/project/hatch-cython/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-cython.svg?logo=python&label=Python&logoColor=silver)](https://pypi.org/project/hatch-cython/)  |
| Meta    | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)                                                                                                                                                                                                                    |

---

**Table of Contents**

- [Usage](#usage)
- [Installation](#installation)
  - [Build System Requirements for Library Includes](#build-system-requirements-for-library-includes)
- [Configuration Options](#configuration-options)
  - [Platform-Specific Arguments](#platform-specific-arguments)
  - [Files](#files)
  - [Explicit Build Targets](#explicit-build-targets)
- [Source Distributions](#source-distributions)
- [Templating](#templating)
- [Notes](#notes)
- [Development](#development)
- [License](#license)


## Usage

The build hook plugin name is `cython`. It can be configured either globally (applies to all build targets) or specifically for the wheel target.

## Installation

Add `hatch-cython` to your build dependencies in `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling", "hatch-cython", "Cython", "setuptools"]
build-backend = "hatchling.build"
```

> **Important**: `Cython` and `setuptools` must be included in `build-system.requires` because the build hook imports Cython modules at load time, before hook-specific dependencies are resolved.

### Build System Requirements for Library Includes

When using `include_numpy`, `include_pyarrow`, `include_pythran`, or custom `include_{package}` options, **those packages must also be added to `build-system.requires`**. This is because hatch-cython imports these packages at hook initialization to resolve their include paths.

| Option                  | Required in `build-system.requires` |
| ----------------------- | ----------------------------------- |
| `include_numpy = true`  | `"numpy"`                           |
| `include_pyarrow = true`| `"pyarrow"`                         |
| `include_pythran = true`| `"pythran"`                         |
| `include_{pkg} = {...}` | The package specified in `pkg`      |

**Example with NumPy:**

```toml
[build-system]
requires = ["hatchling", "hatch-cython", "Cython", "setuptools", "numpy"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[tool.hatch.build.targets.wheel.hooks.cython.options]
include_numpy = true
define_macros = [["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"]]
```

**Example with PyArrow:**

```toml
[build-system]
requires = ["hatchling", "hatch-cython", "Cython", "setuptools", "pyarrow"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[tool.hatch.build.targets.wheel.hooks.cython.options]
include_pyarrow = true
```


### Hook Configuration Locations

You can define the hook in several locations depending on your needs:

| Location                                        | Scope                | File           |
| ----------------------------------------------- | -------------------- | -------------- |
| `[tool.hatch.build.hooks.cython]`               | Global (all targets) | pyproject.toml |
| `[tool.hatch.build.targets.wheel.hooks.cython]` | Wheel only           | pyproject.toml |
| `[build.hooks.cython]`                          | Global (all targets) | hatch.toml     |
| `[build.targets.wheel.hooks.cython]`            | Wheel only           | hatch.toml     |


### Basic Example (pyproject.toml)

```toml
[build-system]
requires = ["hatchling", "hatch-cython", "Cython", "setuptools"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[tool.hatch.build.targets.wheel.hooks.cython.options]
# Include directories for .h or .cpp files
includes = []

# Include headers from common scientific packages
include_numpy = false
include_pyarrow = false

# Custom library integration (see "Custom Library Includes" section)
include_somelib = {
    pkg = "somelib",              # module name (must be in dependencies)
    include = "gets_include",      # somelib.gets_include() -> str | list[str]
    libraries = "gets_libraries",  # somelib.gets_libraries() -> list[str]
    library_dirs = "gets_library_dirs",  # somelib.gets_library_dirs() -> list[str]
    required_call = "some_setup_op"      # somelib.some_setup_op() called before build
}

# Cython compiler directives
directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }

# Additional keyword arguments passed to setuptools.Extension()
compile_kwargs = { }
```

### Basic Example (hatch.toml)

```toml
[build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[build.targets.wheel.hooks.cython.options]
directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }
compile_args = ["-O3"]
includes = []
include_numpy = false

# Example: equivalent to include_pyarrow = true
include_somelib = { pkg = "pyarrow", include = "get_include", libraries = "get_libraries", library_dirs = "get_library_dirs", required_call = "create_library_symlinks" }

define_macros = [
    ["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"],
]
```

## Configuration Options

All options are specified under `[tool.hatch.build.targets.wheel.hooks.cython.options]` (pyproject.toml) or `[build.targets.wheel.hooks.cython.options]` (hatch.toml).

| Field               | Type                       | Description                                                                                                                                                                                                                                                                                                                               |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src`               | `str \| None`              | The package directory name if it differs from the project name. For example, if your project is `package-a` but the source is in `src/package_a_lib/`, set `src = "package_a_lib"`.                                                                                                                                                       |
| `directives`        | `dict`                     | Cython compiler directives passed to `cythonize()`. See [compiler-directives] for available options.                                                                                                                                                                                                                                      |
| `compile_args`      | `list[str \| PlatformArg]` | Compiler arguments passed to the C/C++ compiler. Can be simple strings or platform-specific objects (see [Platform-Specific Arguments](#platform-specific-arguments)). See [extensions] for available arguments.                                                                                                                          |
| `extra_link_args`   | `list[str \| PlatformArg]` | Linker arguments. Same format as `compile_args`. See [extensions] for available arguments.                                                                                                                                                                                                                                                |
| `cythonize_kwargs`  | `dict`                     | Additional keyword arguments passed directly to Cython's `cythonize()` function. Example: `{ annotate = true, nthreads = 4 }`                                                                                                                                                                                                             |
| `env`               | `list[EnvArg]`             | Environment variables to set during compilation. Format: `{ env = "VAR", arg = "VALUE", platforms = [...], arch = [...] }`. For flags like `CFLAGS`, `LDFLAGS`, `CPPFLAGS`, `LDSHARED`, `CCSHARED`, `ARFLAGS`, values are merged with existing env vars (separated by space). Use `merges = true` to enable merging for custom variables. |
| `includes`          | `list[str]`                | List of directories to add to the include path for the C/C++ compiler.                                                                                                                                                                                                                                                                    |
| `include_{package}` | `dict`                     | Custom library integration. Format: `{ pkg = str, include = str, libraries = str \| None, library_dirs = str \| None, required_call = str \| None }`. Each field (except `pkg`) is an attribute name on the package that returns `str \| list[str]` or is a callable returning the same.                                                  |
| `include_numpy`     | `bool`                     | If `true`, automatically includes NumPy headers. NumPy must be in your build dependencies. Default: `false`                                                                                                                                                                                                                               |
| `include_pyarrow`   | `bool`                     | If `true`, automatically includes PyArrow headers and libraries. PyArrow must be in your build dependencies. Default: `false`                                                                                                                                                                                                             |
| `include_pythran`   | `bool`                     | If `true`, automatically includes Pythran headers. Pythran must be in your build dependencies. Default: `false`                                                                                                                                                                                                                           |
| `parallel`          | `bool`                     | If `true`, adds OpenMP headers and flags for parallel compilation. **macOS users**: Requires Homebrew's LLVM (`brew install llvm`) instead of Apple's LLVM to use `-fopenmp`. Default: `false`                                                                                                                                            |
| `compiler`          | `str`                      | Compiler identifier. If set to `"msvc"` (Microsoft Visual Studio), uses `/openmp` instead of `-fopenmp` when `parallel = true`.                                                                                                                                                                                                           |
| `compile_py`        | `bool`                     | If `true`, `.py` files are compiled to Cython extensions alongside `.pyx` files. This allows you to write standard Python that gets compiled. Use `files.exclude` to skip specific files. Default: `true`                                                                                                                                 |
| `define_macros`     | `list[list[str]]`          | C preprocessor macro definitions. Each entry is a list: `["KEY"]` for `#define KEY` or `["KEY", "VALUE"]` for `#define KEY VALUE`. Example: `[["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"]]`                                                                                                                                          |
| `**kwargs`          | `any`                      | Additional keyword arguments are passed directly to `setuptools.Extension()`. See [extensions] for available options.                                                                                                                                                                                                                     |

### Platform-Specific Arguments

The `compile_args` and `extra_link_args` fields support platform-specific configuration using objects with the following fields:

| Field          | Type               | Description                                                                                                                                                                                                              |
| -------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `arg`          | `str`              | The compiler/linker argument to add.                                                                                                                                                                                     |
| `platforms`    | `str \| list[str]` | Platform(s) where this arg applies. Values: `"darwin"`, `"linux"`, `"windows"`, `"freebsd"`, `"*"` (all). Default: `"*"`                                                                                                 |
| `arch`         | `str \| list[str]` | Architecture(s) where this arg applies. Values: `"x86_64"`, `"arm64"`, `"aarch64"`, `"anon"` (empty string), `"*"` (all). Default: `"*"`                                                                                 |
| `depends_path` | `bool`             | If `true`, the path specified in `arg` (after any flag prefix like `-I` or `-L`) must exist for this argument to be included. Useful for optional library paths that may not be present on all systems. Default: `false` |
| `marker`       | `str`              | A [PEP 508 environment marker](https://peps.python.org/pep-0508/#environment-markers) expression. The argument is only included if the marker evaluates to `true`.                                                       |

> **Note**: The `"anon"` architecture value matches systems that return an empty string for `platform.machine()`, which can occur in some containerized or emulated environments.

#### PEP 508 Markers

The `marker` field accepts standard PEP 508 environment markers for conditional compilation. Common variables include:

- `python_version` - Python version (e.g., `"3.10"`)
- `python_full_version` - Full Python version (e.g., `"3.10.12"`)
- `os_name` - OS name (`"posix"`, `"nt"`, `"java"`)
- `sys_platform` - System platform (`"linux"`, `"darwin"`, `"win32"`)
- `platform_machine` - Machine architecture (`"x86_64"`, `"arm64"`)
- `platform_system` - System name (`"Linux"`, `"Darwin"`, `"Windows"`)
- `implementation_name` - Python implementation (`"cpython"`, `"pypy"`)

**Examples:**

```toml
compile_args = [
  # Simple string argument (applies to all platforms)
  "-v",

  # Platform-specific
  { platforms = ["linux", "darwin"], arg = "-Wcpp" },

  # Platform and architecture specific
  { platforms = "darwin", arch = "x86_64", arg = "-arch x86_64" },
  { platforms = "darwin", arch = "arm64", arg = "-arch arm64" },

  # Only include if path exists (useful for optional dependencies)
  { platforms = "darwin", arg = "-I/opt/homebrew/include", depends_path = true },

  # Only for Python 3.10 and earlier
  { arg = "-I/legacy/include", marker = "python_version <= '3.10'" },

  # Only for CPython (not PyPy)
  { arg = "-DCPYTHON_ONLY", marker = "implementation_name == 'cpython'" },

  # Combine platform, arch, path check, and marker
  { platforms = "darwin", arch = "x86_64", arg = "-I/usr/local/opt/llvm/include", depends_path = true, marker = "python_version < '3.11'" },

  # Complex marker expressions
  { arg = "-DOLD_ABI", marker = "python_version < '3.9' or implementation_name == 'pypy'" },
]
```

### Files

The `files` section controls which files are included or excluded from compilation.

```toml
[build.targets.wheel.hooks.cython.options.files]
exclude = [
    # Anything matching this pattern is ignored by cython
    "*/no_compile/*",

    # Note: "*" in patterns is converted to "([^\s]*)" (non-whitespace regex)
    # For a literal regex asterisk, use the full regex syntax:
    "([^.]\\*).(pyd$|pytempl$)",

    # Platform-specific exclusions (exclude on all OTHER platforms)
    { matches = "*/windows", platforms = ["linux", "darwin", "freebsd"] },
    { matches = "*/darwin", platforms = ["linux", "freebsd", "windows"] },
    { matches = "*/linux", platforms = ["darwin", "freebsd", "windows"] },
    { matches = "*/freebsd", platforms = ["linux", "darwin", "windows"] },
]

# Rename modules in the final build
aliases = {"mylib._internal" = "mylib.public_name"}
```

### Explicit Build Targets

By default, `hatch-cython` compiles all `.pyx` files (and `.py` files if `compile_py = true`). To compile only specific files, use `options.files.targets`:

```toml
[build.targets.wheel.hooks.cython.options.files]
targets = [
  # String pattern
  "*/compile.py",

  # Platform-specific targets
  { matches = "*/windows", platforms = ["windows"] },
  { matches = "*/posix", platforms = ["darwin", "freebsd", "linux"] },
]
```

When `targets` is specified, only matching files are compiled. This also implicitly enables compilation of `.py`, `.c`, `.cpp`, and `.cc` files that match the patterns.

## Source Distributions

Source distributions (sdist) work normally with `hatch-cython`. When building an sdist:

1. Hatch automatically installs `hatch-cython` as specified in your build dependencies
2. Platform-specific compile arguments are evaluated but compilation is skipped
3. Template files (`.pyx.in`, `.pyi.in`, etc.) can be processed and included
4. Generated `.c` and `.cpp` files can optionally be included in the sdist

> **Note**: If `hatch-cython` runs during a non-wheel build target, the extension compilation is skipped. The generated intermediate files (`.c`, `.cpp`) may still be included if desired, though the compile arguments will differ per-platform at install time.

## Templating

`hatch-cython` supports [Cython Tempita](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#pxd-files) templates for generating code at build time. Any file with a `.in` suffix is processed as a template:

**Supported template extensions:**

- `.pyx.in` → `.pyx`
- `.pxd.in` → `.pxd`
- `.pyi.in` → `.pyi`
- `.py.in` → `.py`
- `.c.in` → `.c`
- `.cpp.in` → `.cpp`

### Template Example

**Source file (`templated.pyx.in`):**

```cython
{{for typ in supported}}

cpdef {{typ}} add_{{typ}}({{typ}} a, {{typ}} b):
    return a + b

{{endfor}}
```

**With configuration:**

```toml
[build.targets.wheel.hooks.cython.options.templates]
global = { supported = ["int", "float", "double"] }
```

**Generated output (`templated.pyx`):**

```cython
cpdef int add_int(int a, int b):
    return a + b

cpdef float add_float(float a, float b):
    return a + b

cpdef double add_double(double a, double b):
    return a + b
```

### Module Aliasing with Templates

Templates can be combined with aliases to rename modules:

```toml
[build.targets.wheel.hooks.cython.options.files]
aliases = {"mylib._templated" = "mylib.templated"}
```

Build process:

1. Source: `_templated.pyx.in`, `templated.pyi.in`
2. After template processing: `_templated.pyx`, `templated.pyi`
3. Final module: `mylib.templated`

### Template Arguments

Templates receive keyword arguments based on matching rules. Configure these in the `templates` section:

```toml
[build.targets.wheel.hooks.cython.options.templates]
# Index defines which keyword sets apply to which files
index = [
  { keyword = "global", matches = "*" },
  { keyword = "mac_types", matches = "templated.*.in", platforms = ["darwin"] },
  { keyword = "win_types", matches = "templated.*.in", platforms = ["windows"] },
  { keyword = "win_x64_types", matches = "templated.*.in", platforms = ["windows"], arch = ["x86_64"] },
  { keyword = "py38_compat", matches = "*.in", marker = "python_version == '3.8'" },
]

# Keyword argument sets
global = { supported = ["int"] }
mac_types = { supported = ["int", "float"] }
win_types = { supported = ["int", "float", "complex"] }
win_x64_types = { supported = ["int", "float", "double", "complex"] }
py38_compat = { use_legacy_api = true }
```

**Matching behavior:**

- `global` is always evaluated first and can be overridden by other matches
- Multiple matching keywords are merged in FIFO order (first defined takes precedence for conflicts)
- Each index entry supports `platforms`, `arch`, and `marker` for conditional matching

**Example merge:**

```python
# Given matches: global, mac_types
# global = { supported = ["int"], extra = "value" }
# mac_types = { supported = ["int", "float"] }
# Result: { supported = ["int", "float"], extra = "value" }
```

See the [test_libraries/src_structure](./test_libraries/src_structure/) directory for complete working examples.

## Notes

### macOS

- Users with Homebrew installed will automatically have `brew --prefix` library and include paths added during compilation
- GitHub Actions runners now use Apple Silicon (M1) for macOS. If using M1 runners, disable `macos-max-compat`:

  ```toml
  # hatch.toml
  [build.targets.wheel]
  macos-max-compat = false
  ```

### OpenMP on macOS

To use `parallel = true` on macOS, you need Homebrew's LLVM instead of Apple's Clang:

```bash
brew install llvm libomp
```

The plugin automatically detects Homebrew's LLVM and adds the appropriate include/library paths.

## Development

### Requirements

- C/C++ compiler (gcc, clang, or MSVC)
- Python 3.8 - 3.13
- [Mise](https://mise.jdx.dev)

### Development Scripts

| Command                 | Description                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------- |
| `mise install`         | Setup project environment                                                            |
| `hatch run cov`         | Run tests with coverage                                                            |
| `task example`          | Test with [src_structure example](./test_libraries/src_structure/hatch.toml)       |
| `task simple-structure` | Test with [simple_structure example](./test_libraries/simple_structure/hatch.toml) |
| `task precommit`        | Run pre-commit hooks                                                               |

## License

`hatch-cython` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

[extensions]: https://docs.python.org/3/distutils/apiref.html#distutils.core.Extension
[compiler-directives]: https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
[git-cliff]: https://git-cliff.org
[tasks]: https://taskfile.dev
