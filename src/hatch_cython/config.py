from collections.abc import Callable, Generator
from dataclasses import asdict, dataclass, field
from importlib import import_module
from os import name, path
from typing import Optional

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_cython.types import ListStr, list_t, union_t

__known__ = (
    "src",
    "includes",
    "libraries",
    "library_dirs",
    "directives",
    "compile_args",
    "retain_intermediate_artifacts",
)

INCLUDE = "include_"
DIRECTIVES = {
    "binding": True,
    "language_level": 3,
}


@dataclass
class Autoimport:
    pkg: str

    include: str
    libraries: str = field(default=None)
    library_dirs: str = field(default=None)
    required_call: str = field(default=None)


@dataclass
class CompileArgs:
    arg: str
    platforms: union_t(ListStr, str) = "*"


__packages__ = {
    a.pkg: a
    for a in (
        Autoimport("numpy", "get_include"),
        Autoimport(
            "pyarrow",
            include="get_include",
            libraries="get_libraries",
            library_dirs="get_library_dirs",
            required_call="create_library_symlinks",
        ),
    )
}

COMPILE_ARGS = [CompileArgs(arg="-O2")]


def parse_from_dict(cls: BuildHookInterface):
    given = cls.config.get("options", {})
    passed = given.copy()
    kwargs = {}
    for kw, val in given.items():
        if kw in __known__:
            kwargs[kw] = val
            passed.pop(kw)
            continue

    try:
        args = kwargs.pop("compile_args")
        for i, arg in enumerate(args):
            if isinstance(arg, dict):
                args[i] = CompileArgs(**arg)

    except KeyError:
        args = []

    cfg = Config(**kwargs, compile_args=args)
    for kw, val in passed.copy().items():
        is_include = kw.startswith(INCLUDE)
        if is_include and val:
            import_p = __packages__.get(kw.replace(INCLUDE, ""))
            if import_p is None:
                if isinstance(val, str):
                    import_p = Autoimport(pkg=kw, include=val)
                elif isinstance(val, dict):
                    if "pkg" not in val:
                        val["pkg"] = kw
                    import_p = Autoimport(**val)
                else:
                    msg = " ".join(
                        (
                            "%s (%s) is invalid, either provide a known package or",
                            "a path in the format of module.get_xxx where get_xxx is",
                            "the directory to be included",
                        )
                    ).format(val, type(val))
                    raise ValueError(msg)

            cfg.resolve_pkg(
                cls,
                import_p,
            )
            passed.pop(kw)
        elif is_include:
            passed.pop(kw)

    cfg.compile_kwargs = passed
    return cfg


@dataclass
class Config:
    src: Optional[str] = field(default=None)  # noqa: UP007
    includes: ListStr = field(default_factory=list)
    libraries: ListStr = field(default_factory=list)
    library_dirs: ListStr = field(default_factory=list)
    directives: dict = field(default_factory=lambda: DIRECTIVES)
    compile_args: list_t(union_t(CompileArgs, str)) = field(default_factory=lambda: COMPILE_ARGS)
    compile_kwargs: dict = field(default_factory=dict)
    retain_intermediate_artifacts: bool = field(default=False)

    def __post_init__(self):
        self.directives = {**DIRECTIVES, **self.directives}

    def _post_import_attr(
        self,
        cls: BuildHookInterface,
        im: Autoimport,
        att: str,
        mod: any,
        extend: Callable[[ListStr], None],
        append: Callable[[str], None],
    ):
        attr = getattr(im, att)
        if attr is not None:
            try:
                libraries = getattr(mod, attr)
                if callable(libraries):
                    libraries = libraries()

                if isinstance(libraries, str):
                    append(libraries)
                elif isinstance(libraries, (list, Generator)):  # noqa: UP038
                    extend(libraries)
                elif isinstance(libraries, dict):
                    extend(libraries.values())
                else:
                    cls.app.display_warning(f"{im.pkg}.{attr} has an invalid type ({type(libraries)})")

            except AttributeError:
                cls.app.display_warning(f"{im.pkg}.{attr}")

    def resolve_pkg(
        self,
        cls: BuildHookInterface,
        im: Autoimport,
    ):
        mod = import_module(im.pkg)
        calls = getattr(mod, im.include)
        if not callable(calls):
            msg = f"{im.pkg}.{im.include} is invalid"
            raise ValueError(msg)
        self.includes.append(calls())
        self._post_import_attr(
            cls,
            im,
            "libraries",
            mod,
            self.libraries.extend,
            self.libraries.append,
        )
        self._post_import_attr(
            cls,
            im,
            "library_dirs",
            mod,
            self.library_dirs.extend,
            self.library_dirs.append,
        )
        if im.required_call is not None:
            if hasattr(mod, im.required_call):
                call = getattr(mod, im.required_call)
                call()
            else:
                cls.app.display_warning(f"{im.pkg}.{im.required_call} is invalid")

    @property
    def compile_args_for_platform(self):
        args = []
        for arg in self.compile_args:
            if isinstance(arg, CompileArgs):
                if (isinstance(arg.platforms, list) and name in arg.platforms or "*" in arg.platforms) or (
                    isinstance(arg.platforms, str) and (arg.platforms in (name, "*"))
                ):
                    args.append(arg.arg)
            else:
                args.append(arg)
        return args

    def asdict(self):
        return asdict(self)

    def validate_include_opts(self):
        for opt in self.includes:
            if not path.exists(opt):
                msg = "%s does not exist" % opt
                raise ValueError(msg)
