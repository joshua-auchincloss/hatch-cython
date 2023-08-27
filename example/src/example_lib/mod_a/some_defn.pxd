# distutils: language=c++
cimport cython


@cython.final
cdef class ValueDefn:
    cdef public int value
    cpdef bint set(self, int value)


cdef inline int vmul(ValueDefn v1, ValueDefn v2):
    cdef int result
    result = v1.value ** v2.value
    return result
