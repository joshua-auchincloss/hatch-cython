from hatch_cython.types import CallableT, DictT, ListT, P, TupleT, UnionT


# basic test to assert we can use subscriptable generics
def test_type_compat():
    TupleT[int, str]
    DictT[str, str]
    ListT[str]
    CallableT[P, str]
    UnionT[str, None]
