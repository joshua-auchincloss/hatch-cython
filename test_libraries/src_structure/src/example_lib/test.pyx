# distutils: language=c++

cimport numpy as cnp

from cython.parallel import parallel, prange

cnp.import_array()

ctypedef cnp.longlong_t dtype

cpdef str hello_world(str name):
    cdef str response
    response = f"hello, {name}"
    return response


cpdef dtype hello_numpy(cnp.ndarray[dtype, ndim=1] arr):
    cdef dtype tot
    cdef Py_ssize_t cap
    cdef int i
    tot = 0
    cap = arr.size
    with nogil, parallel():
        for i in prange(cap):
            with gil:
                tot += arr[i]
    return tot
