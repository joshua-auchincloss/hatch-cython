# DO NOT EDIT.
# Autoformatted by hatch-cython.
# Version: 0.3.0
# Cython: 3.0.2
# Platform: darwin
# Architecture: x86_64
# Keywords: {'supported': ['int', 'float']}

# int C adder (int)
cpdef int ciadd(int a, int b):
    return a + b

# int C mul (int)
cpdef int cimul(int a, int b):
    return a * b

# int C pow (int)
cpdef int cipow(int a, int b):
    return a ** b

# float C adder (float)
cpdef float cfadd(float a, float b):
    return a + b

# float C mul (float)
cpdef float cfmul(float a, float b):
    return a * b

# float C pow (float)
cpdef float cfpow(float a, float b):
    return a ** b
