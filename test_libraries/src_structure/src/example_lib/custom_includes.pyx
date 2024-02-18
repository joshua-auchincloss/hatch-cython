ctypedef long long int64_t

cdef extern from "something.h" namespace "pyutil":
    cdef int64_t bwf(int64_t *b)

cpdef int64_t bwfpy(int64_t b):
    return bwf(&b)
