cimport numpy as cnp

cnp.import_array()

ctypedef cnp.int64_t dtype

cpdef str hello_world(str name):
    cdef str response
    response = f"hello, {name}"
    return response


cpdef dtype hello_numpy(cnp.ndarray[dtype, ndim=1] arr):
    cdef dtype tot
    for k in arr:
        tot = tot + k
    return tot
