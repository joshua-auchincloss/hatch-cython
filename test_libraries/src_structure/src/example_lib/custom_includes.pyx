# distutils: language=c++

cdef extern from "something.cc" namespace "pyutil":
    cdef long long bwf(long long *b)

cpdef long long bwfpy(long long b):
    return bwf(&b)
