# hatch-cython

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-cython.svg)](https://pypi.org/project/hatch-cython)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-cython.svg)](https://pypi.org/project/hatch-cython)
![PyPI - Downloads](https://img.shields.io/pypi/dw/hatch-cython)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Usage

The build hook name is `cython`.

- _pyproject.toml_

```toml
[tool.hatch.build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[tool.hatch.build.targets.wheel.hooks.cython.options]
<!-- include .h or .cpp directories -->
includes = []
<!-- include numpy headers -->
include_numpy = false
include_pyarrow = false

include_somelib = {
    pkg = "somelib",
    <!-- somelib.gets_include() -> str -->
    include = "gets_include",
    <!-- somelib.gets_libraries() -> list[str] -->
    libraries = "gets_libraries",
    <!-- somelib.gets_library_dirs() -> list[str] -->
    library_dirs = "gets_library_dirs",
    <!-- somelib.some_setup_op() before build -->
    required_call = "some_setup_op"
}

compile_args = [
    <!-- single string -->
    "-std=c++17",
    <!-- list of platforms + arg -->
    { platforms = ["nt"], arg = "-std=c++17" },
    <!-- single platform + arg -->
    { platforms = "posix", arg = "-I/abc/def" },
]

directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }

compile_kwargs = { }
```

- _hatch.toml_

```toml
[build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[build.targets.wheel.hooks.cython.options]
<!-- optional, defaults below -->
directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }
compile_args = [
    "-O3",
]
includes = []
include_numpy = false
<!-- equivalent to include_pyarrow = true -->
include_somelib = { pkg = "pyarrow", include="get_include", libraries="get_libraries", library_dirs="get_library_dirs", required_call="create_library_symlinks" }
```

## Configuration Options

| Field                              | Type                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| src                                | `str \| None` <br/> directory within `src` dir or `.`  which aliases the package being built. e.g. `package_a` -> `src/package_a_lib` <br/> `src = "package_a"`                                                                                                                                                                                                                                     |
| directives                         | directives to cython (see cython docs)                                                                                                                                                                                                                                                                                                                                                              |
| compile_args                       | str or `{ platforms = ["*"] \| "*", arg = str }`                                                                                                                                                                                                                                                                                                                                                    |
| extra_link_args                    | str or `{ platforms = ["*"] \| "*", arg = str }`                                                                                                                                                                                                                                                                                                                                                    |
| env                                | `{ env = "VAR1", arg = "VALUE", platforms = ["*"], arch = ["*"] }`<br/> if flag is one of:<br/> - ARFLAGS<br/> - LDSHARED <br/> - LDFLAGS<br/> - CPPFLAGS <br/> - CFLAGS <br/> - CCSHARED<br/>the current env vars will be merged with the value (provided platform & arch applies), separated by a space. This can be enabled by adding `{ env = "MYVAR" ... , merges = true }` to the definition. |
| includes                           | list str                                                                                                                                                                                                                                                                                                                                                                                            |
| includes\_{package}                | `{ pkg = str, include = str, libraries = str\| None, library_dirs = str \| None , required_call = str \| None }` <br/> where all fields, but `pkg`, are attributes in the type of `callable() -> list[str] \| str` \| `list[str] \| str`                                                                                                                                                            |
| includes_numpy \| includes_pyarrow | bool<br/> 3rd party named imports. must have the respective opt in `dependencies`                                                                                                                                                                                                                                                                                                                   |
| retain_intermediate_artifacts      | bool = False <br/> whether to keep `.c` \| `.cpp` files                                                                                                                                                                                                                                                                                                                                             |
| parallel                           | bool = False <br/>if parallel, add openmp headers<br/> important: if using macos, you need the *homebrew* llvm vs _apple's_ llvm in order to pass `-fopenmp` to clang compiler                                                                                                                                                                                                                      |
| compiler                           | compiler used at build-time. if `msvc` (Microsoft Visual Studio), `/openmp` is used as argument to compile instead of `-fopenmp`  when `parallel = true`                                                                                                                                                                                                                                            |
| \*\* kwargs                        | keyword = value pair arguments to pass to the extension module when building                                                                                                                                                                                                                                                                                                                        |

## License

`hatch-cython` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
