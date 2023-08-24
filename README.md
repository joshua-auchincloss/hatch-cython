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
<!-- optional, defaults below -->
language-level = 3
binding = true
compile-args = [
    "-O3",
]
```

- _hatch.toml_

```toml
[build.targets.wheel.hooks.cython]
dependencies = ["hatch-cython"]

[build.targets.wheel.hooks.cython.options]
<!-- optional, defaults below -->
language-level = 3
binding = true
compile-args = [
    "-O3",
]
```

## License

`hatch-cython` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
