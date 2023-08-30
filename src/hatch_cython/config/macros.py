from hatch_cython.types import ListT, TupleT, UnionT

DefineMacros = ListT[TupleT[str, UnionT[str, None]]]


def parse_macros(define: ListT[ListT[str]]) -> DefineMacros:
    """Parses define_macros from list[list[str, ...]] -> list[tuple[str, str|None]]

    Args:
        define (ListT[ListT[str]]): list of listed strings of len 1 or 2. raises error if len > 2

    Raises:
        ValueError: length > 2 or types are not valid

    Returns:
        DefineMacros: list[tuple[str,str|None]]
    """
    for i, inst in enumerate(define):
        size = len(inst)
        if not (isinstance(inst, list) and size in (1, 2) and all(isinstance(v, str) or v is None for v in inst)):
            msg = "".join(
                f"define_macros[{i}]: macros must be defined as [name, <value>], "
                "where None value denotes #define FOO"
            )
            raise ValueError(msg, inst)
        inst: list
        if size == 1:
            define[i] = (inst[0], None)
        else:
            define[i] = (inst[0], inst[1])
    return define
