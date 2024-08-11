from typing import Any

from hatchling.plugin import hookimpl

from hatch_cython.plugin import CythonBuildHook


@hookimpl
def hatch_register_build_hook():
    return CythonBuildHook


@hookimpl
def hatch_register_builder():
    from hatchling.builders import wheel as wheel
    print("test1")

    wheel.DefaultWheelBuilder = wheel.WheelBuilder

    class WheelBuilder(wheel.WheelBuilder):
        # TODO allow any custom modifications
        # TODO overwrite get_default_build_data(), set_build_data_defaults(), config.set_build_data()=WheelBuilderConfig
        def __init__(
                self,
                root: str,
                plugin_manager = None,
                config = None,
                metadata = None,
                app = None,
        ) -> None:
            super().__init__(root, plugin_manager, config, metadata, app)
            print("test2")

        def build_standard(self, directory: str, **build_data: Any) -> str:
            print("test3")
            return super().build_standard(directory, **build_data)

    wheel.WheelBuilder = WheelBuilder
    return WheelBuilder
