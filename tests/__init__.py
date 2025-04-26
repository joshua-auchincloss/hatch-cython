# SPDX-FileCopyrightText: 2023-present elonzh <elonzh@outlook.com>
#
# SPDX-License-Identifier: MIT
from os import getcwd, name
from sys import path

if name == "nt":
    from pathlib import WindowsPath

    p = WindowsPath(getcwd()) / "src"
else:
    from pathlib import PosixPath

    p = PosixPath(getcwd()) / "src"

path.append(str(p))

from hatch_cythonize.__about__ import __version__  # noqa: E402
from hatch_cythonize.devel import CythonBuildHook, src  # noqa: E402
