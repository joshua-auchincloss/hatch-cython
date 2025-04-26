# SPDX-FileCopyrightText: 2023-present elonzh <elonzh@outlook.com>
#
# SPDX-License-Identifier: MIT
import os
import sys

src = os.sep.join(__file__.split(os.sep)[:-2])
sys.path.append(src)

from hatch_cythonize import CythonBuildHook  # noqa: E402, F401
