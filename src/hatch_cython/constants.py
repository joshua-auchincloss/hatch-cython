from hatch_cython.types import CorePlatforms, ListT

NORM_GLOB = r"([^\s]*)"
UAST = "${U_AST}"
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
POSIX_CORE: ListT[CorePlatforms] = ["darwin", "linux"]
