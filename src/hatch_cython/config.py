import platform
from collections.abc import Callable, Generator, Hashable
from dataclasses import asdict, dataclass, field
from importlib import import_module
from os import environ, path
from typing import ClassVar, Optional

from hatch.utils.ci import running_in_ci
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.markers import Marker

from hatch_cython.types import ListStr, list_t, union_t
from hatch_cython.utils import memo

EXIST_TRIM = 2

ANON = "anon"
INCLUDE = "include_"
OPTIMIZE = "-O2"
DIRECTIVES = {
    "binding": True,
    "language_level": 3,
}
LTPY311 = "python_version < '3.11'"
MUST_UNIQUE = ["-O", "-arch", "-march"]


@memo
def plat():
    return platform.system().lower()


@memo
def aarch():
    return platform.machine().lower()


# fields tracked by this plugin
__known__ = (
    "src",
    "env",
    "includes",
    "libraries",
    "library_dirs",
    "directives",
    "compile_args",
    "cythonize_kwargs",
    "extra_link_args",
    "retain_intermediate_artifacts",
)


@dataclass
class Autoimport:
    pkg: str

    include: str
    libraries: str = field(default=None)
    library_dirs: str = field(default=None)
    required_call: str = field(default=None)


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


@dataclass
class PlatformBase(Hashable):
    platforms: union_t[ListStr, str] = "*"
    arch: union_t[ListStr, str] = "*"
    depends_path: bool = False
    marker: str = None
    apply_to_marker: Callable[[], bool] = None

    def __post_init__(self):
        self.do_rewrite("platforms")
        self.do_rewrite("arch")

    def do_rewrite(self, attr: str):
        att = getattr(self, attr)
        if isinstance(att, list):
            setattr(self, attr, [p.lower() for p in att])
        elif isinstance(att, str):
            setattr(self, attr, att.lower())

    def check_marker(self):
        do = True
        if self.apply_to_marker:
            do = self.apply_to_marker()
        if do:
            marker = Marker(self.marker)
            return marker.evaluate()
        return False

    def _applies_impl(self, attr: str, defn: str):
        if self.marker:
            ok = self.check_marker()
            if not ok:
                return False

        att = getattr(self, attr)
        if isinstance(att, list):
            # https://docs.python.org/3/library/platform.html#platform.machine
            # "" is a possible value so we have to add conditions for anon
            _anon = ANON in att and defn == ""
            return defn in att or "*" in att or _anon
        _anon = ANON == att and defn == ""
        return (att in (defn, "*")) or _anon

    def applies(self):
        _isplatform = self._applies_impl("platforms", plat())
        _isarch = self._applies_impl("arch", aarch())
        return _isplatform and _isarch

    def is_exist(self, trim: int = 0):
        if self.depends_path:
            return path.exists(self.arg[trim:])
        return True


@dataclass
class PlatformArgs(PlatformBase):
    arg: str = None

    def __hash__(self) -> int:
        return hash(self.arg)


@dataclass
class EnvFlag(PlatformArgs):
    env: str = field(default="")
    merges: bool = field(default=False)

    def __hash__(self) -> int:
        return hash(self.field)


__flags__ = (
    EnvFlag(env="CC", merges=False),
    EnvFlag(env="CPP", merges=False),
    EnvFlag(env="CXX", merges=False),
    EnvFlag(env="CFLAGS", merges=True),
    EnvFlag(env="CCSHARED", merges=True),
    EnvFlag(env="CPPFLAGS", merges=True),
    EnvFlag(env="LDFLAGS", merges=True),
    EnvFlag(env="LDSHARED", merges=True),
    EnvFlag(env="SHLIB_SUFFIX", merges=False),
    EnvFlag(env="AR", merges=False),
    EnvFlag(env="ARFLAGS", merges=True),
)


@dataclass
class EnvFlags:
    CC: PlatformArgs = None
    CPP: PlatformArgs = None
    CXX: PlatformArgs = None

    CFLAGS: PlatformArgs = None
    CCSHARED: PlatformArgs = None

    CPPFLAGS: PlatformArgs = None

    LDFLAGS: PlatformArgs = None
    LDSHARED: PlatformArgs = None

    SHLIB_SUFFIX: PlatformArgs = None

    AR: PlatformArgs = None
    ARFLAGS: PlatformArgs = None

    custom: dict[str, PlatformArgs] = field(default_factory=dict)
    env: dict = field(default_factory=environ.copy)

    __known__: ClassVar[dict[str, EnvFlag]] = {e.env: e for e in __flags__}

    def __post_init__(self):
        for flag in __flags__:
            self.merge_to_env(flag, self.get_from_self)
        for flag in self.custom.values():
            self.merge_to_env(flag, self.get_from_custom)

    def merge_to_env(self, flag: EnvFlag, get: Callable[[str], EnvFlag]):
        var = environ.get(flag.env)
        override: EnvFlag = get(flag.env)
        if override and flag.merges:
            add = var + " " if var else ""
            self.env[flag.env] = add + override.arg
        elif override:
            self.env[flag.env] = override.arg

    def get_from_self(self, attr):
        return getattr(self, attr)

    def get_from_custom(self, attr):
        return self.custom.get(attr)


ListedArgs = list_t[union_t[PlatformArgs, str]]
"""
List[str | PlatformArgs]
"""


def get_default_link():
    return [
        PlatformArgs(arg="-L/opt/homebrew/lib", platforms="darwin", depends_path=True),
        PlatformArgs(arg="-L/usr/local/lib", platforms="darwin", depends_path=True),
        PlatformArgs(arg="-L/usr/local/opt", platforms="darwin", depends_path=True),
    ]


def get_default_compile():
    args = [
        PlatformArgs(arg="-O2"),
        PlatformArgs(arg="-I/opt/homebrew/include", platforms="darwin", depends_path=True),
        PlatformArgs(arg="-I/usr/local/include", platforms="darwin", depends_path=True),
    ]
    return args


def parse_to_plat(cls, arg, args: union_t[list, dict], key: union_t[int, str], require_argform: bool, **kwargs):
    if isinstance(arg, dict):
        args[key] = cls(**arg, **kwargs)
    elif require_argform:
        msg = f"arg {key} is invalid. must be of type ({{ flag = ... , platform = '*' }}) given {arg} ({type(arg)})"
        raise ValueError(msg)


def parse_platform_args(
    kwargs: dict,
    name: str,
    default: Callable,
) -> list_t[union_t[str, PlatformArgs]]:
    try:
        args = [*default(), *kwargs.pop(name)]
        for i, arg in enumerate(args):
            parse_to_plat(PlatformArgs, arg, args, i, require_argform=False)
    except KeyError:
        args = default()
    return args


def parse_env_args(
    kwargs: dict,
):
    try:
        args: list = kwargs.pop("env")
        for i, arg in enumerate(args):
            parse_to_plat(EnvFlag, arg, args, i, require_argform=True)
    except KeyError:
        args = []
    return args


def parse_from_dict(cls: BuildHookInterface):
    given = cls.config.get("options", {})
    passed = given.copy()
    kwargs = {}
    for kw, val in given.items():
        if kw in __known__:
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
