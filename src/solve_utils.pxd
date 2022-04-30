
DEF SEARCHING       = 0  # Still looking for a chain.
DEF FOUND           = 1  # Chain has been found
DEF NOT_FOUND       = 2  # No more nodes to create chain
DEF BOTTOMED_OUT    = 4  # recursion limit reached before finding chain or running out of nodes.

ctypedef int  (*pGRIDC)[9]
ctypedef bint (*pCANDSC)[9][9]

ctypedef struct COORD:
    int r, c

ctypedef struct SET3:
    int l
    int v[3]

ctypedef struct OUTCOME:
    int     r, c, Op, Cand
    OUTCOME *Prev
    OUTCOME *Next

ctypedef struct NODE:
    int     r, c
    SET3    rgl, cgl
    int     Cand, Lk
    NODE    *Prev
    NODE    *Next

ctypedef struct CHAIN:
    NODE    *Start
    NODE    *End
    CHAIN   *Prev
    CHAIN   *Next

# Tree structs are used to construct chains in pursuit of patterns that can result in eliminations
# Each pattern type has its own species of trees.

#  For TREE_FFISH, if chains from each fin all reach the cover, then cover can be eliminated
ctypedef struct TREE_FFISH:  # FFISH ==> finned fish trees, one for each cover in a linked list
    int             r, c, Cand     # Tree is identified by its cover,
    int             nFins
    NODE            *FinChain[8]  # Points to the fin chains (cvr first to fin last) when a valid pattern (chain from each fin to cover) is found
    TNODE_FFISH     *FinBranch[8]  # Tree has a first level branch for each fin..
    TREE_FFISH      *Prev
    TREE_FFISH      *Next

ctypedef struct TNODE_FFISH:
    NODE            *ChainN
    TNODE_FFISH     *Parent
    TNODE_FFISH     *SibPrev
    TNODE_FFISH     *SibNext
    TNODE_FFISH     *ChildStart
    TNODE_FFISH     *ChildEnd

# Creating Python wrappers to Cython code on second blush is not as effective as simply
# rewriting chunks of code to optimise in cython and debugging. For the time being commenting
# out all code to transform objects to structs and back again, as well as all wrapper functions
# An implication of this decision is that all solve_* code will ultimately end up being cython
# code, in development and production builds, and only that code that is translated to cython
# can be used in solve_* files. Which:
# * Firstly, it is what I want.
# * Secondly, it keeps things code and implementation simpler
# * Thirdly, eliminates extra make work and maintenance for the wrapper functionality which is
#   turning out not to be trivial.
# That said, I am not going to waste time converting wrappers back to their python function
# and will continue to use them.  But unless a there is no alternative, no more wrappers.

cdef bint is_in_int_array(int v, int *A, int lenA)

cdef CHAIN* pchain_2_cchain(list PChain)
cdef list cchain_2_pchain(CHAIN* CChain)
cdef CHAIN* pchain_2_cchain_gl(list PChain)
cdef list cchain_2_pchain_gl(CHAIN* CChain)
#
cdef pGRIDC  pgrid_2_cgrid(pG, int cG[9][9])
# cdef list   cgrid_2_pgrid(int cG[9][9], pG) # just use a list comprehension
cdef pCANDSC pcands_2_ccands(list pCands, bint cCands[9][9][9])
cdef list    ccands_2_pcands(bint cCands[9][9][9])
cdef SET3*   pset_2_cset3(set SetP, SET3* pSetC)
cdef set     cset3_2_pset(SET3* pSetC)

cdef bint cell_val_has_no_conflicts_c(int v, int grid[9][9], int r, int c)
cdef bint cell_val_has_conflicts_c(int G[9][9], int r, int c)
cdef int determine_cands_c(int Grid[9][9], bint Elims[9][9][9], bint Cands[9][9][9])
cdef int link_house_gl_c(SET3 r0, SET3 c0, SET3 r1, SET3 c1)
cdef int link_house_c(int r0, int c0, int r1, int c1)
cdef void discard_cand_from_peers_c(int cand, int r, int c, bint Cands[9][9][9])
cdef int how_ccells_linked_c(int r0, int c0, int Cand0, int r1, int c1, int Cand1, bint Cands[9][9][9])
cdef int how_ccells_linked_gl_c(SET3 r0, SET3 c0, int Cand0, SET3 r1, SET3 c1, int Cand1, bint Cands[9][9][9])

# cdef int is_in_chain_c(int r, int c, int Cand, CHAIN *Chain)
# cdef int is_in_chain_gl_c(SET3 r, SET3 c, int Cand, CHAIN_GL *Chain)

cdef bint ccells_intersect_c(int r0, int c0, int Cand0, int r1, int c1, int Cand1)
cdef bint ccells_intersect_gl_c(SET3 r0, SET3 c0, int Cand0, SET3 r1, SET3 c1, int Cand1)

cdef NODE* list_ccells_linked_to_c(int r, int c, int Cand, bint Cands[9][9][9], int Type)
cdef NODE* list_ccells_linked_to_gl_c(SET3 r, SET3 c, int Cand, bint Cands[9][9][9], int Type)

cdef bint set3_intersect(SET3 a, SET3 b)
cdef void qd_inplace_sort_c(int *pA, int lenA)
# cdef inline int cands_in_row_c(int r, int Cand, bint Cands[9][9][9])
# cdef inline int cands_in_col_c(int c, int Cand, bint Cands[9][9][9])
# cdef inline int cands_in_box_c(int b, int Cand, bint Cands[9][9][9])

