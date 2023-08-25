cimport cython


@cython.final
cdef class ValueDefn:
    cdef public int value
    cpdef bint set(self, int value)
