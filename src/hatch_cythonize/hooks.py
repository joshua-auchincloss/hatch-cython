from hatchling.plugin import hookimpl

from hatch_cythonize.plugin import CythonBuildHook


@hookimpl
def hatch_register_build_hook():
    return CythonBuildHook
