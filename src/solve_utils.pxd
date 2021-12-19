from ctypedefs_x cimport *

cdef CHAIN* pchain_2_cchain(list PChain)
cdef list cchain_2_pchain(CHAIN* CChain)
cdef CHAIN_GL* pchain_2_cchain_gl(list PChain)
cdef list cchain_2_pchain_gl(CHAIN_GL* CChain)

cdef void pgrid_2_cgrid(list pG, int cG[9][9])
cdef void cgrid_2_pgrid(int cG[9][9], list pG)
cdef void pcands_2_ccands(list pCands, bint cCands[9][9][9])
cdef void ccands_2_pcands(bint cCands[9][9][9], list pCands)
cdef void pset_2_cset3(set pSet, SET3 cCset)
cdef set cset3_2_pset(SET3 cSet)

cdef bint cell_val_has_no_conflicts_c(int v, int grid[9][9], int r, int c)
cdef bint cell_val_has_conflicts_c(int G[9][9], int r, int c)
cdef int determine_cands_c(int Grid[9][9], bint Elims[9][9][9], bint Cands[9][9][9])
cdef int link_house_gl_c(SET3 r0, SET3 c0, SET3 r1, SET3 c1)
cdef int link_house_c(int r0, int c0, int r1, int c1)
cdef int token_link_c(int Lk)
cdef void discard_cand_from_peers_c(int cand, int r, int c, bint Cands[9][9][9])

cdef int is_in_chain_c(int r, int c, int Cand, CHAIN *Chain)
cdef int is_in_chain_gl_c(SET3 r, SET3 c, int Cand, CHAIN_GL *Chain)

cdef bint ccells_intersect_c(int r0, int c0, int Cand0, int r1, int c1, int Cand1)
cdef bint ccells_intersect_gl_c(SET3 r0, SET3 c0, int Cand0, SET3 r1, SET3 c1, int Cand1)

cdef NODEC* list_ccells_linked_to_c(int r, int c, bint Cands[9][9][9], LK_STR Type)
cdef NODE_GL *list_ccells_linked_to_gl_c(SET3 r, SET3 c, bint Cands[9][9][9], LK_STR Type)



cdef bint set3_intersect(SET3 a, SET3 b)
