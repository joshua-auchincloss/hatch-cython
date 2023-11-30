cdef class MyClass:
    def __cinit__(self):
        pass

    cpdef str do(self):
        return "abc"

cpdef MyClass fast_create():
    return MyClass.__new__(MyClass)
