# distutils: language=c++

cimport numpy as cnp

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

cnp.import_array()

ctypedef cnp.longlong_t dtype

cpdef str hello_world(str name):
    cdef str response
    response = f"hello, {name}"
    return response


cpdef dtype hello_numpy(cnp.ndarray[dtype, ndim=1] arr):
    cdef dtype tot
    tot = 0
    for k in arr:
        tot = tot + k
    return tot
