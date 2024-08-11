from typing import Any

from hatchling.plugin import hookimpl

from hatch_cython.plugin import CythonBuildHook


@hookimpl
def hatch_register_build_hook():
    return CythonBuildHook


@hookimpl
def hatch_register_builder():
    from hatchling.builders import wheel as wheel

    wheel.DefaultWheelBuilder = wheel.WheelBuilder

    class WheelBuilder(wheel.WheelBuilder):
        PLUGIN_NAME = "hatch_cython"
        # TODO allow any custom modifications
        # TODO overwrite get_default_build_data(), set_build_data_defaults(), config.set_build_data()=WheelBuilderConfig

        def build_standard(self, directory: str, **build_data: Any) -> str:
            print("WHEEL BUILDER OVERRIDE")
            return super().build_standard(directory, **build_data)

    wheel.WheelBuilder = WheelBuilder
    return WheelBuilder
