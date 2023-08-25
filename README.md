# hatch-cython

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-cython.svg)](https://pypi.org/project/hatch-cython)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-cython.svg)](https://pypi.org/project/hatch-cython)

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
compile-args = [
    "-O3",
]
includes = []
include_numpy = false
<!-- equivalent to include_numpy = true -->
include_somelib = { pkg = "pyarrow", include="get_include", libraries="get_libraries", library_dirs="get_library_dirs", required_call="create_library_symlinks" }
```

## License

`hatch-cython` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
