# SPDX-FileCopyrightText: 2023-present joshua-auchincloss <joshua.auchincloss@proton.me>
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

from hatch_cython.__about__ import __version__  # noqa: E402
from hatch_cython.devel import CythonBuildHook, src  # noqa: E402
