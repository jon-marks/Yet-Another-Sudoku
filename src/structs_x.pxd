# Project wide Cython structs

ctypedef struct soln_t:
    int Found
    int SlvdG[9][9]

