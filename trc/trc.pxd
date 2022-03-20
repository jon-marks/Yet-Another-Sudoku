
ctypedef struct COORD:
    int r, c

cdef void TRCX_grid(int G[9][9])
cdef void TRCX_cands(bint C[9][9][9])
cdef void TRCX_int_array(object sDesc, int *A, int lenA)
cdef void TRCX_coord_array(object sDesc, COORD *A, int lenA)
cdef void TRCX_memdump(void *Addr, int lenA)
cdef void *PyMem_TRCX_Malloc(size_t Bytes)
cdef void *PyMem_TRCX_Calloc(size_t Nr, size_t Bytes)
cdef void PyMem_TRCX_Free(void *Mem)
