# SPDX-FileCopyrightText: 2023-present joshua-auchincloss <joshua.auchincloss@proton.me>
#
# SPDX-License-Identifier: MIT
import os
import sys

sep = "\\" if os.name == "nt" else "/"
src = sep.join(__file__.split(sep)[:-2])
sys.path.append(src)

from hatch_cython import (CythonBuildHook,  # noqa: F401, E402
                          hatch_register_build_hook)
