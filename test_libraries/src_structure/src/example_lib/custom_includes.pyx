# distutils: language=c++

ctypedef long long int wide_int

cdef extern from "something.cc" namespace "pyutil":
    cdef wide_int bwf(wide_int *b)

cpdef wide_int bwfpy(wide_int b):
    return bwf(&b)
