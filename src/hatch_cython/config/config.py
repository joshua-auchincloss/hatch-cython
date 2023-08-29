from collections.abc import Generator
from dataclasses import asdict, dataclass, field
from importlib import import_module
from os import path
from typing import Optional

from hatch.utils.ci import running_in_ci
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_cython.config.autoimport import Autoimport, __packages__
from hatch_cython.config.defaults import get_default_compile, get_default_link
from hatch_cython.config.files import FileArgs
from hatch_cython.config.flags import EnvFlag, EnvFlags, parse_env_args
from hatch_cython.config.platform import ListedArgs, PlatformArgs, parse_platform_args
from hatch_cython.constants import DIRECTIVES, EXIST_TRIM, INCLUDE, LTPY311, MUST_UNIQUE
from hatch_cython.types import CallableT, ListStr

# fields tracked by this plugin
__known__ = (
    "src",
    "env",
    "files",
    "compile_py",
    "includes",
    "libraries",
    "library_dirs",
    "directives",
    "compile_args",
    "cythonize_kwargs",
    "extra_link_args",
    "retain_intermediate_artifacts",
)


def parse_from_dict(cls: BuildHookInterface):
    given = cls.config.get("options", {})
    passed = given.copy()
    kwargs = {}
    for kw, val in given.items():
        if kw in __known__:
            if kw == "files":
                val = FileArgs(**val)  # noqa: PLW2901
            kwargs[kw] = val
            passed.pop(kw)
            continue

    compile_args = parse_platform_args(kwargs, "compile_args", get_default_compile)
    link_args = parse_platform_args(kwargs, "extra_link_args", get_default_link)
    env = parse_env_args(kwargs)

    kw = {"custom": {}}
    for arg in env:
        arg: EnvFlag
        if arg.applies():
            if arg.env in EnvFlags.__known__:
                kw[arg.env] = arg
            else:
                kw["custom"][arg.env] = arg
    envflags = EnvFlags(**kw)
    cfg = Config(**kwargs, compile_args=compile_args, extra_link_args=link_args, envflags=envflags)
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

    if "parallel" in passed and passed.get("parallel"):
        passed.pop("parallel")
        comp = [
            PlatformArgs(arg="/openmp", platforms="windows"),
            PlatformArgs(arg="-fopenmp", platforms=["linux"]),
        ]
        link = [
            PlatformArgs(arg="/openmp", platforms="windows"),
            PlatformArgs(arg="-fopenmp", platforms="linux"),
            PlatformArgs(arg="-lomp", platforms="darwin", marker=LTPY311, apply_to_marker=running_in_ci),
        ]
        cma = ({*cfg.compile_args}).union({*comp})
        cfg.compile_args = list(cma)
        seb = ({*cfg.extra_link_args}).union({*link})
        cfg.extra_link_args = list(seb)

    cfg.compile_kwargs = passed
    return cfg


@dataclass
class Config:
    src: Optional[str] = field(default=None)  # noqa: UP007
    files: FileArgs = field(default_factory=FileArgs)
    includes: ListStr = field(default_factory=list)
    libraries: ListStr = field(default_factory=list)
    library_dirs: ListStr = field(default_factory=list)
    directives: dict = field(default_factory=lambda: DIRECTIVES)
    compile_args: ListedArgs = field(default_factory=get_default_compile)
    compile_kwargs: dict = field(default_factory=dict)
    cythonize_kwargs: dict = field(default_factory=dict)
    extra_link_args: ListedArgs = field(default_factory=get_default_link)
    retain_intermediate_artifacts: bool = field(default=False)
    envflags: EnvFlags = field(default_factory=EnvFlags)
    compile_py: bool = field(default=True)

    def __post_init__(self):
        self.directives = {**DIRECTIVES, **self.directives}

    @property
    def compile_args_for_platform(self):
        return self._arg_impl(self.compile_args)

    @property
    def compile_links_for_platform(self):
        return self._arg_impl(self.extra_link_args)

    def _post_import_attr(
        self,
        cls: BuildHookInterface,
        im: Autoimport,
        att: str,
        mod: any,
        extend: CallableT[[ListStr], None],
        append: CallableT[[str], None],
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

    def _arg_impl(self, target: ListedArgs):
        args = {"any": []}

        def with_argvalue(arg: str):
            # be careful with e.g. -Ox flags
            matched = list(filter(lambda s: arg.startswith(s), MUST_UNIQUE))
            if len(matched):
                m = matched[0]
                args[m] = arg.split(" ")
            else:
                args["any"].append(arg.split(" "))

        for arg in target:
            # if compile-arg format, check platform applies
            if isinstance(arg, PlatformArgs):
                if arg.applies() and arg.is_exist(EXIST_TRIM):
                    with_argvalue(arg.arg)
            # else assume string / user knows what theyre doing and add to the call params
            else:
                with_argvalue(arg)

        flat = []

        def flush(it):
            if isinstance(it, list):
                for v in it:
                    flush(v)
            else:
                flat.append(it)

        # side effect
        list(map(flush, args.values()))
        return flat

    def asdict(self):
        return asdict(self)

    def validate_include_opts(self):
        for opt in self.includes:
            if not path.exists(opt):
                msg = "%s does not exist" % opt
                raise ValueError(msg)
