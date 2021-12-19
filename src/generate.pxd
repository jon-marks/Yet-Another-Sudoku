from ctypedefs_x cimport *

cdef bint check_puzzle_c(int G[9][9], SOLN_T* pSoln, int cell)
cdef bint gen_filled_grid_c(int G[9][9], int cell)

