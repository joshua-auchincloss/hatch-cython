# SPDX-FileCopyrightText: 2023-present joshua-auchincloss <joshua.auchincloss@proton.me>
#
# SPDX-License-Identifier: MIT
import os
import sys

src = os.sep.join(__file__.split(os.sep)[:-2])
sys.path.append(src)

from hatch_cython import CythonBuildHook  # noqa: E402, F401
