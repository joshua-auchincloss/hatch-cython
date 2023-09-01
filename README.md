# hatch-cython

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-cython.svg)](https://pypi.org/project/hatch-cython)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-cython.svg)](https://pypi.org/project/hatch-cython)
![PyPI - Downloads](https://img.shields.io/pypi/dw/hatch-cython)
[![Build](https://github.com/joshua-auchincloss/hatch-cython/actions/workflows/build.yaml/badge.svg)](https://github.com/joshua-auchincloss/hatch-cython/actions)
[![Tests](https://github.com/joshua-auchincloss/hatch-cython/actions/workflows/test.yml/badge.svg)](https://github.com/joshua-auchincloss/hatch-cython/actions)
[![codecov](https://codecov.io/gh/joshua-auchincloss/hatch-cython/graph/badge.svg?token=T12ACNLFWV)](https://codecov.io/gh/joshua-auchincloss/hatch-cython)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

**Table of Contents**

- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [Notes](#notes)
  - [Templating (Tempita)](#templating-tempita)
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
directives = { boundscheck = false, nonecheck = false, language_level = 3, binding = true }
compile_args = [
    "-O3",
]
includes = []
include_numpy = false
<!-- equivalent to include_pyarrow = true -->
include_somelib = { pkg = "pyarrow", include="get_include", libraries="get_libraries", library_dirs="get_library_dirs", required_call="create_library_symlinks" }
define_macros = [
    ["NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"],
]
```

## Configuration Options

| Field                                                  | Type                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| src                                                    | `str \| None` <br/> directory within `src` dir or `.`  which aliases the package being built. e.g. `package_a` -> `src/package_a_lib` <br/> `src = "package_a"`                                                                                                                                                                                                                                     |
| directives                                             | directives to cython (see [compiler-directives])                                                                                                                                                                                                                                                                                                                                                    |
| compile_args                                           | str or `{ platforms = ["*"] \| "*", arg = str }`. see [extensions] for what args may be relevant                                                                                                                                                                                                                                                                                                    |
| extra_link_args                                        | str or `{ platforms = ["*"] \| "*", arg = str }`. see [extensions] for what args may be relevant                                                                                                                                                                                                                                                                                                    |
| env                                                    | `{ env = "VAR1", arg = "VALUE", platforms = ["*"], arch = ["*"] }`<br/> if flag is one of:<br/> - ARFLAGS<br/> - LDSHARED <br/> - LDFLAGS<br/> - CPPFLAGS <br/> - CFLAGS <br/> - CCSHARED<br/>the current env vars will be merged with the value (provided platform & arch applies), separated by a space. This can be enabled by adding `{ env = "MYVAR" ... , merges = true }` to the definition. |
| includes                                               | list str                                                                                                                                                                                                                                                                                                                                                                                            |
| includes\_{package}                                    | `{ pkg = str, include = str, libraries = str\| None, library_dirs = str \| None , required_call = str \| None }` <br/>where all fields, but `pkg`, are attributes of `pkg` in the type of `callable() -> list[str] \| str` \| `list[str] \| str`. `pkg` is a module, or loadable module object, which may be imported through `import x.y.z`.                                                       |
| includes_numpy \| includes_pyarrow \| includes_pythran | bool<br/>3rd party named imports. must have the respective opt in `dependencies`                                                                                                                                                                                                                                                                                                                    |
| retain_intermediate_artifacts                          | bool = False <br/>whether to keep `.c` \| `.cpp` files                                                                                                                                                                                                                                                                                                                                              |
| parallel                                               | bool = False <br/>if parallel, add openmp headers<br/>important: if using macos, you need the *homebrew* llvm vs _apple's_ llvm in order to pass `-fopenmp` to clang compiler                                                                                                                                                                                                                       |
| compiler                                               | compiler used at build-time. if `msvc` (Microsoft Visual Studio), `/openmp` is used as argument to compile instead of `-fopenmp`  when `parallel = true`. `default = false`                                                                                                                                                                                                                         |
| compile_py                                             | whether to include `.py` files when building cython exts. note, this can be enabled & you can do per file / matched file ignores as below. `default = true`                                                                                                                                                                                                                                         |
| define_macros                                          | list of list str (of len 1 or 2). len 1 == [KEY] == `#define KEY FOO` . len 2 == [KEY, VALUE] == `#define KEY VALUE`. see [extensions]                                                                                                                                                                                                                                                              |
| \*\* kwargs                                            | keyword = value pair arguments to pass to the extension module when building. see [extensions]                                                                                                                                                                                                                                                                                                      |

### Files

```toml
[build.targets.wheel.hooks.cython.options.files]
exclude = [
    # anything matching no_compile is ignored by cython
    "*/no_compile/*",
    # note - anything "*" is escaped to "([^\s]*)" (non whitespace).
    # if you need an actual * for python regex, use as below:
    # this excludes all pyd or pytempl extensions
    "([^.]\\*).(pyd$|pytempl$)"
]
aliases = {"abclib._filewithoutsuffix" = "abclib.importalias"}
```

## Templating

Cython tempita is supported for any files suffixed with `.in`, where the extension output is:

- `.pyx.in`
- `.pyd.in`
- `.pyi.in`
  For these files, you may expect the output `.pyx.in` -> `.pyx`. Thus, with aliasing this would look like:

```toml
[build.targets.wheel.hooks.cython.options.files]
aliases = {"abclib._somemod" = "abclib.somemod"}
```

- 1. Source files `somemod.pyi.in`, `_somemod.pyx.in`
- 2. Processed templates `somemod.pyi`, `_somemod.pyx`
- 3. Compiled module `abclib.somemod{.pyi,.pyx}`

An example of this is included in:

- [pyi stub file](./example/src/example_lib/templated.pyi.in)
- [pyx cython source file](./example/src/example_lib/templated.pyx.in)
- [pyi stub (rendered)](./example/src/example_lib/templated_maxosx_sample.pyi)
- [pyx cython source (rendered)](./example/src/example_lib/templated_maxosx_sample.pyi)

### Template Arguments

You may also supply arguments for per-file matched namespaces. This follows the above `platforms`, `arch`, & `marker` formats, where if supplied & passing the condition the argument is passed to the template as a named series of keyword arguments.

You supply an `index` value, and all other kwargs to templates are `keywords` for each index value. Follows FIFO priority for all keys except global, which is evaluated first and overriden if there are other matching index directives. The engine will attempt to merge the items of the keywords, roughly following:

```py
args = {
    "index": [
        {"keyword": "global", ...},
        {"keyword": "thisenv", ...},
    ],
    "global": {"abc": 1, "other": 2},
    "thisenv": {"other": 3},
}

merge(args) -> {"abc": 1, "other": 3}
```

In hatch.toml:

```toml
[build.targets.wheel.hooks.cython.options.templates]
index = [
  {keyword = "global", matches = "*" },
  {keyword = "templated_mac", matches = "templated.*.in",  platforms = ["darwin"] },
  {keyword = "templated_mac_py38", matches = "templated.*.in",  platforms = ["darwin"], marker = "python == '3.8'" },
  {keyword = "templated_win", matches = "templated.*.in",  platforms = ["windows"] },
  {keyword = "templated_win_x86_64", matches = "templated.*.in",  platforms = ["windows"], arch = ["x86_64"] },

]

<!-- these are passed as arguments for templating -->

<!-- 'global' is a special directive reserved & overriden by all other matched values -->
global = { supported = ["int"] }

templated_mac = { supported = ["int", "float"] }
templated_mac_py38 = { supported = ["int", "float"] }

templated_win = { supported = ["int", "float", "complex"] }

<!-- assuming numpy is cimported in the template -->
templated_win_x86_64 = { supported = ["int", "float", "np.double"]}
```

## License

`hatch-cython` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

[extensions]: (https://docs.python.org/3/distutils/apiref.html#distutils.core.Extension)
[compiler-directives]: (https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives)
