
cdef int tech_exposed_singles_c(int Grid[9][9], object Step, bint Cands[9][9][9], object Methods)
cdef int tech_hidden_singles_c(int Grid[9][9], object Step, bint Cands[9][9][9], object Methods)
cdef int tech_locked_singles_c(int Grid[9][9], object Step, bint Cands[9][9][9], object Methods)
cdef int tech_empty_rects_c(int Grid[9][9], object Step, bint Cands[9][9][9], object Methods)
cdef int tech_brute_force_c(int Grid[9][9], object Step, bint Cands[9][9][9], object Methods)
