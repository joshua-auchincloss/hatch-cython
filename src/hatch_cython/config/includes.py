from hatch_cython.config.autoimport import Autoimport, __packages__
from hatch_cython.constants import INCLUDE


def parse_includes(kw: str, val: str):
    alias = kw.replace(INCLUDE, "")
    import_p = __packages__.get(alias)
    if import_p is None:
        if isinstance(val, str):
            import_p = Autoimport(pkg=alias, include=val)
        elif isinstance(val, dict):
            if "pkg" not in val:
                val["pkg"] = alias
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
    return import_p
