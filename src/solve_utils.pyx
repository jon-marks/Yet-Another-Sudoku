
#  Collection of common enums, structures, classes, and functions used in the solving
#  of puzzles.

#  Note many of the functions operate optimally and seamlessly on group linked ccells
#  and scalar ccells.  This is achieved by using a the flag GrpLks to indicate when
#  pattern searches using group links is required and and passing all (r, c) parameters as
#  sets.  That is when GrpLKS is set, r and c are set objects, when GrpLks is False,
#  r and c are scalars.

# PyMem C_API functions are generally faster for small mem allocations than the native c
# functions, and this mem is accounted for within the Python environment.
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "string.h" nogil:
    void * memset(void *, int, size_t)

include "globals.pxi"
from ctypedefs cimport *
from globals import *
from trc cimport *
from trc import *
from solve_utils cimport *

# Link strength enumerations.
LK_NONE = 0x0000   # must be 0, code relies on this.
LK_WEAK = 0x0001
LK_STRG = 0x0002
LK_STWK = 0x0003   # a strong link is also a weak link.
LK_WKST = 0x0007   # strong link masquerading as a weak link

# Link orientation enumerations
LK_LINE = 0x0100
LK_ROW  = 0x0010 | LK_LINE
LK_COL  = 0x0020 | LK_LINE
LK_BOX  = 0x0040
LK_CELL = 0x0080
# LK_ANY_depreciated  = 0x0070


# The use of weak or strong ended AIC's to search for patterns where ccell's see
# each other, for example in covers seeing fins in finned fish or W wings, etc,
# adds the dimension of incremental difficulty in finding and solving a pattern
# based on the number of links in the chains used to solve a step.

class TNODE:
    # This is the tree node (branch) structure used in constructing AI chains.
    def __init__(self, r = -1, c = -1, Cand = -1, Lk = -1, Chain = None, Parent = None, Children = None):
        self.r = r              # row
        self.c = c              # col
        self.Cand = Cand        # Candidate
        self.Lk = Lk            # link to parent (LK_ enums)
        self.Chain = [] if Chain is None else Chain  # List of path from root to current Node. (NODE(r, c, Cand, Lk_type_to_next)
        self.Parent = Parent
        self.Children = [] if Children is None else Children

class STATUS:
    def __init__(self, Tech = T_UNDEF, Pattern = None, Outcome = None):
        self.Tech = Tech
        self.Pattern = Pattern if Pattern else []
        self.Outcome = Outcome if Outcome else []

# Python <==> Cython conversion functions, neccessary while port to Cython code, will
# eventually be depreciated with the the python structures when all the code is in Cython.

cdef CHAIN* pchain_2_cchain(list PChain):
    # pchain is a list of (r, c, Cand, Lk) tuples. cchain is a linked list of "Ctypedef struct CHAIN_NODE"s
    # with start and end in "ctypedef struct CHAIN"
    # implicitly mallocs the memory for the cchain.
    cdef CHAIN      *CChain = <CHAIN *>PyMem_Malloc(sizeof(CHAIN))
    cdef NODE *N
    cdef i
    # print("---- In pchain_2_cchain() ----", file=stderr)
    if not PChain or CChain == NULL: return NULL

    N = <NODE *>PyMem_Malloc(sizeof(NODE))
    if N == NULL: return NULL
    CChain.Start = N; N.Prev = NULL
    for i in range(len(PChain)-1):
        N.r, N.c, N.Cand, N.Lk = PChain[i]
        N.Next = <NODE *>PyMem_Malloc(sizeof(NODE))
        if N == NULL: return NULL
        N.Next.Prev = N
        # print(f"Loop: {i}, {PChain[i]}")
        # print(f"{N.r},{N.c},{N.Cand},{N.Lk},N: 0x{<long long>N:016x}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}")
        N = N.Next
    else:
        N.r, N.c, N.Cand, N.Lk = PChain[len(PChain)-1]
        N.Next = NULL; CChain.End = N
        # print(f"Loop: {len(PChain)-1}, {PChain[len(PChain)-1]}")
        # print(f"{N.r},{N.c},{N.Cand},{N.Lk},N: 0x{<long long>N:016x}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}")
    return CChain

cdef CHAIN* pchain_2_cchain_gl(list PChain):
    # for group links.
    # pchain is a list of (r, c, Cand, Lk) tuples, where r and c are sets of up to 3 .
    # cchain is a linked list of "Ctypedef struct CHAIN_NODE_GL"s
    # with start and end in "ctypedef struct CHAIN_GL"
    # implicitly mallocs the memory for the cchain.
    cdef CHAIN       *CChain = <CHAIN *>PyMem_Malloc(sizeof(CHAIN_GL))
    cdef NODE_GL *N
    cdef int i

    # if DEBUG: print("In pchain_2_cchain_gl()")
    if not PChain or CChain == NULL: return NULL
    N = <NODE_GL *>PyMem_Malloc(sizeof(NODE_GL))
    if N == NULL: return NULL
    CChain.StartGL = N; N.Prev = NULL
    for i in range(len(PChain)-1):
        r, c, N.Cand, N.Lk = PChain[i]
        # if DEBUG: print(f"  Pchain[{i}] upacked, r:{r}, c:{c}, N.Cand:{N.Cand}, N.Lk:{N.Lk}, len(r):{len(r)}, len(c):{len(c)}")
        for j, x in enumerate(r): N.r.v[j] = x
        for j in range(len(r),3): N.r.v[j] = 0
        N.r.l = len(r)
        for j, x in enumerate(c): N.c.v[j] = x
        for j in range(len(c),3): N.c.v[j] = 0
        N.c.l = len(c)
        N.Next = <NODE_GL *>PyMem_Malloc(sizeof(NODE_GL))
        if N == NULL: return NULL
        N.Next.Prev = N
        # print(f"Loop: {i}, {PChain[i]}")
        # print(f"{N.r},{N.c},{N.Cand},{N.Lk},N: 0x{<long long>N:016x}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}")
        N = N.Next
    else:
        r, c, N.Cand, N.Lk = PChain[len(PChain)-1]
        # if DEBUG: print(f"  Pchain[{len(PChain)-1}] upacked, r:{r}, c:{c}, N.Cand:{N.Cand}, N.Lk:{N.Lk}, len(r):{len(r)}, len(c):{len(c)}")
        for j, x in enumerate(r): N.r.v[j] = x
        for j in range(len(r),3): N.r.v[j] = 0
        N.r.l = len(r)
        for j, x in enumerate(c): N.c.v[j] = x
        for j in range(len(c),3): N.c.v[j] = 0
        N.c.l = len(c)
        N.Next = NULL; CChain.EndGL = N
        # print(f"Loop: {len(PChain)-1}, {PChain[len(PChain)-1]}")
        # print(f"{N.r},{N.c},{N.Cand},{N.Lk},N: 0x{<long long>N:016x}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}")
    return CChain

cdef list cchain_2_pchain(CHAIN* CChain):
    # pchain is a list of (r, c, Cand, Lk) tuples. cchain is a linked list of "Ctypedef struct CHAIN_NODE"s
    # with start and end in "ctypedef struct CHAIN"
    # returns PChain
    # implicitly frees the allocated cchain memory
    cdef NODE *N
    # cdef NODE *N1
    cdef list PChain = []

    N = CChain.Start
    while N:
        PChain.append((N.r, N.c, N.Cand, N.Lk))
        # N1 = N
        N = N.Next
        PyMem_Free(N.Prev)
    PyMem_Free(CChain); CChain = NULL
    return PChain

cdef list cchain_2_pchain_gl(CHAIN* CChain):
    # for group_links
    # pchain is a list of (r, c, Cand, Lk) tuples. cchain is a linked list of "Ctypedef struct CHAIN_NODE"s
    # with start and end in "ctypedef struct CHAIN"
    # returns PChain
    # implicitly frees the allocated cchain memory
    cdef NODE_GL *N
    # cdef NODE_GL *N1
    cdef list PChain = []
    cdef int i

    N = CChain.StartGL
    while N:
        r = set(); c = set()
        for i in range(N.r.l): r.add(N.r.v[i])
        for i in range(N.c.l): c.add(N.c.v[i])
        PChain.append((r, c, N.Cand, N.Lk))
        # N1 = N
        N = N.Next
        PyMem_Free(N.Prev)
    PyMem_Free(CChain); CChain = NULL
    return PChain

cdef inline pGRIDC pgrid_2_cgrid(pG, int cG[9][9]):
    cdef int r, c

    for r in range(9):
        for c in range(9):
            cG[r][c] = pG[r][c]
    return cG


# cdef inline cgrid_2_pgrid(int cG[9][9], pG):
# just do the following list comprehension instead.
# pG = [[cG[r][c] for c in range(9)] for r in range(9)]

cdef inline pCANDSC pcands_2_ccands(list pCands, bint cCands[9][9][9]):
    cdef int r, c, d, Cand

    memset(<void *>cCands, False, SIZEOF_CANDS)
    for r in range(9):
        for c in range(9):
            # for d in range(9): cCands[r][c][d] = False
            for Cand in pCands[r][c]: cCands[r][c][Cand-1] = True
    return cCands

cdef inline list ccands_2_pcands(bint cCands[9][9][9]):  # , list pCands):
    cdef int r, c, d

    pCands = [[set() for c in range(9)] for r in range(9)]
    for r in range(9):
        for c in range(9):
            for d in range(9):
                if cCands[r][c][d]: pCands[r][c].add(d+1)
    return pCands

cdef inline SET3* pset_2_cset3(set SetP, SET3* pSetC):
    cdef int i, x

    for i, x in enumerate(SetP): pSetC[0].v[i] = x
    pSetC[0].l = len(pSet)
    for i in range(pSetC[0].l, 3): cSet[0].v[i] = 0
    return pSetC

cdef inline set cset3_2_pset(SET3* pSetC):
    cdef i

    SetP = set()
    for i in range(pSetC[0].l):
        SetP.add(pSetC[0].v[i])
    return SetP

def cell_val_has_no_conflicts(v, grid, r, c):
    # Cython wrapper function
    cdef int G[9][9]

    pgrid_2_cgrid(grid, G)
    return cell_val_has_no_conflicts_c(v, G, r, c)

cdef bint cell_val_has_no_conflicts_c(int v, int grid[9][9], int r, int c):
    #  Checks that value v obeys sudoku rules in grid[r][c], the 9x9 matrix
    #  v:     IN:  value to test in the grid
    #  grid:  IN:  grid to test value
    #  r, c   IN:  row and column in grid for test.
    # Check that val not in row
    cdef int br, bc, r1, c1, i

    for i in range(9):
        if v == grid[r][i]: return False
        if v == grid[i][c]: return False
    br = (r//3)*3; bc = (c//3)*3
    for r1 in range(br, br+3):
        for c1 in range(bc, bc+3):
            if v == grid[r1][c1]: return False
    return True

def cell_val_has_conflicts(grid, r, c):
    # Cython wrapper function
    cdef int G[9][9]

    pgrid_2_cgrid(grid, G)
    return cell_val_has_conflicts_c(G, r, c)

cdef bint cell_val_has_conflicts_c(int G[9][9], int r, int c):
    cdef int br, bc, v, i

    if G[r][c]:
        v = G[r][c]; G[r][c] = 0
        for i in range(9):
            if v == G[r][i]: G[r][c] = v; return True
            if v == G[i][c]: G[r][c] = v; return True
        br = (r//3)*3; bc = (c//3)*3
        for r1 in range(br, br+3):
            for c1 in range(bc, bc+3):
                if v == G[r1][c1]: G[r][c] = v; return True
        G[r][c] = v
    return False

def determine_cands(Grid, Elims = None):
    # Cython wrapper function
    cdef int cGrid[9][9]
    cdef bint cElims[9][9][9]
    cdef bint cCands[9][9][9]
    cdef int NrEmpties, r, c, d, Cand

    if Elims:
        for r in range(9):
            for c in range(9):
                cGrid[r][c] = Grid[r][c]
                for d in range(9):
                    cElims[r][c][d] = cCands[r][c][d] = False
                for Cand in Elims[r][c]:
                    cElims[r][c][Cand-1] = True
        NrEmpties = determine_cands_c(cGrid, cElims, cCands)
    else:
        NrEmpties = determine_cands_c(cGrid, <pCANDSC>NULL, cCands)
    return NrEmpties, ccands_2_pcands(cCands)

cdef int determine_cands_c(int Grid[9][9], bint Elims[9][9][9], bint Cands[9][9][9]):
    # No Elims if set to NULL.
    cdef int r, c, d, NrEmpties = 0

    memset(<void *>Cands, False, SIZEOF_CANDS)
    if Elims:
        for r in range(9):
            for c in range(9):
                if not Grid[r][c]:
                    NrEmpties += 1
                    for d in range(9):
                        if not Elims[r][c][d] and cell_val_has_no_conflicts_c(d+1, Grid, r, c):
                            Cands[r][c][d] = True
    else:
        for r in range(9):
            for c in range(9):
                if not Grid[r][c]:
                    NrEmpties += 1
                    for d in range(9):
                        if cell_val_has_no_conflicts_c(d+1, Grid, r, c):
                            Cands[r][c][d] = True
    return NrEmpties

# def link_house(r0, c0, r1, c1, GrpLks = False):
#     # wrapper for Cython C functions.
#     # ccells must be linked else erroneous LK_BOX cand be returned.
#     cdef SET3 r0s, c0s, r1s, c1s
#
#     if GrpLks:
#         pset_2_cset3(r0, &r0s); pset_2_cset3(c0, &c0s)
#         pset_2_cset3(r1, &r1s); pset_2_cset3(c1, &c1s)
#         return link_house_gl_c(r0s, c0s, r1s, c1s)
#     else:
#         return link_house_c(r0, c0, r1, c1)

cdef int link_house_gl_c(SET3 r0, SET3 c0, SET3 r1, SET3 c1):
    # cells must be linked, else erroneous LK_BOX_C is returned.
    if r0.l == r1.l == 1 and r0.v[0] == r1.v[0]: return LK_ROW_C
    if c0.l == c1.l == 1 and c0.v[0] == c1.v[0]: return LK_COL_C
    return LK_BOX_C

cdef int link_house_c(int r0, int c0, int r1, int c1):
    # cells must be linked, else erroneous LK_BOX_C is returned.
    if r0 == r1 and c0 == c1: return LK_CELL_C
    if r0 == r1: return LK_ROW_C
    if c0 == c1: return LK_COL_C
    return LK_BOX_C

# def token_link(Lk):
#     #wrapper for token_link_c
#     return token_link_c(Lk)

cdef int token_link_c(int Lk):
    Lk &= 0x000f
    if Lk == LK_WEAK_C: return OP_WLK_C
    if Lk == LK_STRG_C or Lk == LK_STWK_C: return OP_SLK_C
    if Lk == LK_WKST_C: return OP_WSLK_C
    if Lk == LK_NONE_C: return OP_NONE_C
    return -1

# def discard_cand_from_peers(Cand, r, c, Cands):
#     #wrapper for discard_cand_from_peers_c.
#     cdef bint Cands_c[9][9][9]
#     cdef int r1, c1, d1
#
#     pcands_2_ccands(Cands, Cands_c)
#     # for r1 in range(9):
#     #     for c1 in range(9):
#     #         for d1 in range(9): Cands_c[r1][c1][d1] = False
#     #         for Cand1 in Cands[r1][c1]: Cands_c[r1][c1][Cand1-1] = True
#     discard_cand_from_peers_c(Cand, r, c, Cands_c)
#     # python objects are passed by assignment, so assigning something else to cands will not be
#     # passed to the caller.  However changes to to the values in the cands object do not alter
#     # the cands assignment.
#     for r1 in range(9):
#         for c1 in range(9):
#             if Cands[r1][c1]:
#                 for d1 in range(9):
#                     if not Cands_c[r1][c1][d1]: Cands[r1][c1].discard(d1+1)


cdef void discard_cand_from_peers_c(int Cand, int r, int c, bint Cands[9][9][9]):
    cdef int i, j, br, bc

    for i in range(9):
        Cands[i][c][Cand-1] = False
        Cands[r][i][Cand-1] = False
    br = (r//3)*3; bc = (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            Cands[i][j][Cand-1] = False

# def is_in_chain(r, c, Cand, PChain, GrpLks):
#     # wrapper for is_in_chain_c() and is_in_chain_gl_c()
#     cdef SET3 r_gl, c_gl
#     # cdef int i, x, res
#     cdef int res
#     cdef CHAIN *Chain
#     cdef CHAIN_GL *Chain_gl
#     cdef NODE_GL *N
#
#     if GrpLks:
#         if DEBUG: print(f"is_in_chain(): GrpLks, r:{r}, c:{c}, Cand:{Cand}, PChain:{PChain}")
#         pset_2_cset3(r, &r_gl); pset_2_cset3(c, &c_gl)
#         # for i, x in enumerate(r): r_gl.v[i] = x
#         # for i in range(len(r),3): r_gl.v[i] = 0
#         # r_gl.l = len(r)
#         # for i, x in enumerate(c): c_gl.v[i] = x
#         # for i in range(len(c),3): c_gl.v[i] = 0
#         # c_gl.l = len(c)
#         # if DEBUG: print(f"Is this group node in the chain?  r_gl:{r_gl}, c_gl:{c_gl}")
#         Chain_gl = pchain_2_cchain_gl(PChain)
#         ####
#         # if DEBUG: print(f"B4 is_in_chain_gl_c(), Chain_gl.Start: 0x{<long long>Chain_gl.Start:016x}, CChain.End: 0x{<long long>Chain_gl.End:016x}")
#         # N = Chain_gl.Start
#         # while N:
#         #     if DEBUG: print(f"N.r:{N.r}, N.c:{N.c}, N.Cand:{N.Cand}, N.Lk:{N.Lk}, N: 0x{<long long> N:016x}, N.Prev: 0x{<long long> N.Prev:016x}, N.Next: 0x{<long long> N.Next:016x}")
#         #     N = N.Next
#         res = is_in_chain_gl_c(r_gl, c_gl, Cand, Chain_gl)
#         # if DEBUG: print(f"After is_in_chain_gl_c(), Chain_gl.Start: 0x{<long long>Chain_gl.Start:016x}, CChain.End: 0x{<long long>Chain_gl.End:016x}")
#         # N = Chain_gl.Start
#         # while N:
#         #     if DEBUG: print(f"N.r:{N.r}, N.c:{N.c}, N.Cand:{N.Cand}, N.Lk:{N.Lk}, N: 0x{<long long>N:016x}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}")
#         #     N = N.Next
#         ####
#         cchain_2_pchain_gl(Chain_gl)  # lazy way to free all allocated memory
#         # PC = cchain_2_pchain_gl(Chain_gl)  # lazy way to free all allocated memory
#         # if DEBUG: print(f"res:{res}, Reconst PChain:{PC}")
#     else:
#         Chain = pchain_2_cchain(PChain)
#         res = is_in_chain_c(r, c, Cand, Chain)
#         cchain_2_pchain(Chain) # lazy way to free all allocated memory
#     return res

# cdef int is_in_chain_c(int r, int c, int Cand, CHAIN *Chain):
#     cdef NODE *N
#     cdef int i = 0
#
#     N = Chain.Start
#     while N:
#         # For scalars (non group links, intersecting is the same as ==
#         if r == N.r and c == N.c and Cand == N.Cand: return i
#         i += 1
#         N = N.Next
#     return -1
#
# cdef int is_in_chain_gl_c(SET3 r, SET3 c, int Cand, CHAIN_GL *Chain_gl):
#     cdef NODE_GL *N
#     cdef int i = 0
#
#     N = Chain_gl.Start
#     while N:
#         if set3_intersect(r, N.r) and set3_intersect(c, N.c) and Cand == N.Cand: return i
#         i += 1
#         N = N.Next
#     return -1

cdef inline bint set3_intersect(SET3 a, SET3 b):

    for i in range(a.l):
        for j in range(b.l):
            if a.v[i] == b.v[j]: return True
    return False

cdef NODE* list_ccells_linked_to_c(int r, int c, bint Cands[9][9][9], int Type):
    # returns a singly linked list of ccell nodes
    return <NODE *>void

cdef NODE_GL *list_ccells_linked_to_gl_c(SET3 r, SET3 c, bint Cands[9][9][9], int Type):
    # returns a singly linked list of ccell nodes
    return <NODE_GL *>void

def list_ccells_linked_to(r, c, Cand, Cands, Type = LK_STWK, GrpLks = False):
    # this now becomes a wrapper function for Cython functions list_ccells_linked_to_c()
    # and list_ccells_linked_to_c()
    # Returns a list of (r, c, Cand, LkType, LkHouse) tuples that ccell(r, c, Cand) can see.
    # LkType is one of LK_STWK or LK_WEAK, LkHouse is one of LK_ROW, LK_COL, LK_BOX, or LK_CELL
    # If Type == LK_STRG, only strong links will be returned.
    # if GrpLks is True r and c are passed and returned as sets, else r, c are passed and
    # returned as scalars.

    # Note when working with non-group links, if the link is in the intersection of two
    # houses (a line and a box), it may be strong in one house and weak in the other.
    # This is an opportunity to for pointing or claiming locked singles eliminations (which
    # BTW should have been cleared by earlier steps than when these higher level of
    # complexity functions are used.

    LCL = []
    if GrpLks:
        if len(r) == 1:  # scan the row
            r0 = list(r)[0]
            ct = list(c)[0]//3
            C1 = set()
            Twr = [set(), set(), set()]
            for c1 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - c):
                if Cand in Cands[r0][c1]:
                    C1.add(c1)
                    Twr[c1//3].add(c1)
            if len(C1) == 1:
                LCL.append((r, C1, Cand, LK_STWK, LK_ROW))
            elif Type & LK_WEAK:
                for c1 in sorted(C1):
                    LCL.append((r, {c1}, Cand, LK_WEAK, LK_ROW))
            lenTwr0 = len(Twr[0]); lenTwr1 = len(Twr[1]); lenTwr2 = len(Twr[2])
            if ct == 0:
                if lenTwr0 == 0:
                    if lenTwr1 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK, LK_ROW))
                    elif lenTwr1 > 1 and lenTwr2 == 0: LCL.append((r, Twr[1], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr1 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[1], Cand, LK_WEAK, LK_ROW), (r, Twr[2], Cand, LK_WEAK, LK_ROW)])
            if ct == 1:
                if lenTwr1 == 0:
                    if lenTwr0 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK, LK_ROW))
                    elif lenTwr0 > 1 and lenTwr2 == 0: LCL.append((r, Twr[0], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK, LK_ROW), (r, Twr[2], Cand, LK_WEAK, LK_ROW)])
            if ct == 2:
                if lenTwr2 == 0:
                    if lenTwr0 == 0 and lenTwr1 > 1: LCL.append((r, Twr[1], Cand, LK_STWK, LK_ROW))
                    elif lenTwr0 > 1 and lenTwr1 == 0: LCL.append((r, Twr[0], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr1 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK, LK_ROW), (r, Twr[1], Cand, LK_WEAK, LK_ROW)])
        if len(c) == 1:  # scan the col
            c0 = list(c)[0]
            rf = list(r)[0]//3
            R1 = set()
            Flr = [set(), set(), set()]
            for r1 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - r):
                if Cand in Cands[r1][c0]:
                    R1.add(r1)
                    Flr[r1//3].add(r1)
            if len(R1) == 1:
                LCL.append((R1, c, Cand, LK_STWK, LK_COL))
            elif Type & LK_WEAK:
                for r1 in sorted(R1):
                    LCL.append(({r1}, c, Cand, LK_WEAK, LK_COL))
            lenFlr0 = len(Flr[0]); lenFlr1 = len(Flr[1]); lenFlr2 = len(Flr[2])
            if rf == 0:
                if lenFlr0 == 0:
                    if lenFlr1 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr1 > 1 and lenFlr2 == 0: LCL.append((Flr[1], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr1 > 1 and lenFlr2 > 1: LCL.extend([(Flr[1], c, Cand, LK_WEAK, LK_COL), (Flr[2], c, Cand, LK_WEAK, LK_COL)])
            if rf == 1:
                if lenFlr1 == 0:
                    if lenFlr0 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr0 > 1 and lenFlr2 == 0: LCL.append((Flr[0], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr2 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK, LK_COL), (Flr[2], c, Cand, LK_WEAK, LK_COL)])
            if rf == 2:
                if lenFlr2 == 0:
                    if lenFlr0 == 0 and lenFlr1 > 1: LCL.append((Flr[1], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr0 > 1 and lenFlr1 == 0: LCL.append((Flr[0], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr1 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK, LK_COL), (Flr[1], c, Cand, LK_WEAK, LK_COL)])
        # scan the box.  (Grouped) Node is always contained in a box
        rb = (list(r)[0]//3)*3; cb = (list(c)[0]//3)*3; rb1 = rb+1; rb2 = rb+2; cb1 = cb+1; cb2 = cb+2
        B1 = []
        RB = [set(), set(), set()]; CB = [set(), set(), set()]
        for i, r0 in enumerate([rb, rb1, rb2]):
            for j, c0 in enumerate([cb, cb1, cb2]):
                if r0 in r and c0 in c: continue
                if Cand in Cands[r0][c0]: B1.append((r0, c0)); RB[i].add(c0); CB[j].add(r0)
        if len(B1) == 1:
            r1, c1 = B1[0]; LCL.append(({r1}, {c1}, Cand, LK_STWK, LK_BOX))
        elif Type & LK_WEAK:
            for r1, c1 in B1: LCL.append(({r1}, {c1}, Cand, LK_WEAK, LK_BOX))
        BX = []
        B1 = sorted(B1)
        for i in [0, 1, 2]:
            if RB[i]: BX.append(({rb+i}, RB[i]))
            if CB[i]: BX.append((CB[i], {cb+i}))
        for r2, c2 in BX:
            B2 = []; lr2 = len(r2); lc2 = len(c2)
            if lr2 == lc2 == 1: B2.append((list(r2)[0], list(c2)[0]))
            elif lc2 == 1:
                for rx in r2: B2.append((rx, list(c2)[0]))
            elif lr2 == 1:
                for cx in c2: B2.append((list(r2)[0], cx))
            if B1 == sorted(B2): LCL.append((r2, c2, Cand, LK_STWK, LK_BOX))
            elif Type & LK_WEAK: LCL.append((r2, c2, Cand, LK_WEAK, LK_BOX))
    else:  # no GrpLks
        # Scan the row.
        n = 0; LCL0 = []
        Lk = LK_NONE
        for c0 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - {c}):
            if Cand in Cands[r][c0]:
                n +=1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r, c0, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_ROW) for r, c, Cand in LCL0])
        # Scan the col
        n = 0; LCL0 = []
        for r0 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - {r}):
            if Cand in Cands[r0][c]:
                n += 1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r0, c, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_COL) for r, c, Cand in LCL0])
        # Scan the box
        rb = (r//3)*3; cb = (c//3)*3; rb1 = rb+1; rb2 = rb+2; cb1 = cb+1; cb2 = cb+2
        n = 0; LCL0 = []
        for r0, c0 in sorted({(rb, cb), (rb, cb1), (rb, cb2), (rb1, cb), (rb1, cb1), (rb1, cb2), (rb2, cb), (rb2, cb1), (rb2, cb2)} - {(r, c)}):
            if Cand in Cands[r0][c0]:
                n += 1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r0, c0, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_BOX) for r, c, Cand in LCL0])
        # Check in the cell - cell will always have two or more candidates
        # try:
        if len(Cands[r][c]) == 2: LCL.append((r, c, list(Cands[r][c] - {Cand})[0], LK_STWK, LK_CELL))
        elif Type & LK_WEAK:
            for Cand0 in sorted(Cands[r][c] - {Cand}):
                LCL.append((r, c, Cand0, LK_WEAK, LK_CELL))
        # except:
        #     print("ABC")
    return LCL

def cells_in_same_house(r1, c1, r2, c2):
    # Cells see each other in same house
    return r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3)
    #     return True
    # return False

def cells_that_see_all_of(Cells, GrpLks = False):
    # Cells = list of two to four (r,c) tuples.  Returns another list of (r, c) tuples that
    # can see all the passed cells.

    # For three or more cells to be seen by
    # any other cell, the cells to be seen, and the cell that is doing the seeing
    # all need to be in the same chute.

    Cells0 = []
    if GrpLks:
        for r, c in Cells:
            for r0 in r:
                for c0 in c:
                    Cells0.append((r0, c0))
        Cells = Cells0

    Cells1 = []
    for r0 in range(9):
        for c0 in range(9):
            for r1, c1 in Cells:
                if (r0, c0) == (r1, c1): break
                if not (r0 == r1 or c0 == c1 or (r0//3 == r1//3 and c0//3 == c1//3)): break
            else:
                Cells1.append((r0, c0))
    return Cells1

def ccells_match(r0, c0, Cand0, r1, c1, Cand1, GrpLks = False):
    # ccells (grouped or not must match to return True, else False.
    return r0 == r1 and c0 == c1 and Cand0 == Cand1


def ccells_intersect(r0, c0, Cand0, r1, c1, Cand1, GrpLks = False):
    # Not going to create a wrapper as this function is currently only being used local to this module.
    # if not group links: return True if ccells match, else False.
    # for group links, if the cells intersect each other return True, else Fasle

    if GrpLks:
        return bool(len(r0 & r1) and len(c0 & c1)) and Cand0 == Cand1
    else:
        return r0 == r1 and c0 == c1 and Cand0 == Cand1

cdef bint ccells_intersect_gl_c(SET3 r0, SET3 c0, int Cand0, SET3 r1, SET3 c1, int Cand1):
    pass

cdef bint ccells_intersect_c(int r0, int c0, int Cand0, int r1, int c1, int Cand1):
    return r0
    pass


def how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands, GrpLks = False):
    # returns LkType, LkHouse
    #    Where: LkType is one of: LK_NONE, LK_WEAK, or LK_STWK
    #           LkHouse is one of: LK_NONE, LK_ROW, LK_COL, LK_BOX, LK_ROW | LK_BOX, LK_ROW | LK_BOX
    # Two ccells are directly linked if:
    #   * they are two different candidates in the same cell, or
    #     +  strongly if they are the only two candidates in that cell.
    #     +  weakly if there are other candidates in that cell
    #   * they are same value candidates in different cells in a common house.
    #     +  strongly if they are the only occurrences of that candidate value
    #        in the house.
    #     +  weakly if there other candidate values in that cell.
    # Note that a strong link can masquerade as a weak link, but a weak link
    # cannot masquerade as a strong link.

    if GrpLks:
        lenr0 = len(r0); lenc0 = len(c0); lenr1 = len(r1); lenc1 = len(c1)
        r00 = list(r0)[0]; c00 = list(c0)[0]; r10 = list(r1)[0]; c10 = list(c1)[0]
        if lenr0 == lenr1 == lenc0 == lenc1 == 1:  # no grouped ccells
            if not (r0 ^ r1 or c0 ^ c1):  # same cell.
                if Cand0 == Cand1: return LK_NONE, LK_NONE  # cells cannot link on themselves
                if len(Cands[r00][c00]) == 2: return LK_STWK, LK_CELL
                else: return LK_WEAK, LK_CELL
        # different cells, grouped or ungrouped
        if Cand0 != Cand1: return LK_NONE, LK_NONE
        if lenr0 == lenr1 == 1 and r00 == r10:  # house is a row
            for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (c0 | c1):
                if Cand0 in Cands[r00][c]: return LK_WEAK, LK_ROW
            return LK_STRG, LK_ROW
        if lenc0 == lenc1 == 1 and c00 == c10:  # house is a column
            for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (r0 | r1):
                if Cand0 in Cands[r][c00]: return LK_WEAK, LK_COL
            return LK_STRG, LK_COL
        F = set(); T = set()
        for r in r0 | r1: F.add(r//3)
        for c in c0 | c1: T.add(c//3)
        if len(F) == len(T) == 1:  # house is a box.
            rb0 = list(F)[0]; rb1 = rb0+1; rb2 = rb0+2; cb0 = list(T)[0]; cb1 = cb0+1; cb2 = cb0+2
            for rb, cb in [(rb0, cb0), (rb0, cb1), (rb0, cb2), (rb1, cb0), (rb1, cb1), (rb1, cb2), (rb2, cb0), (rb2, cb1), (rb2, cb2)]:
                if (rb in r0 | r1) and (cb in c0 | c1): continue
                if Cand0 in Cands[rb][cb]: return LK_WEAK, LK_BOX
            return LK_STWK, LK_BOX
        return LK_NONE, LK_NONE
    else:
        if r0 == r1 and c0 == c1:
            if Cand0 == Cand1: return LK_NONE, LK_NONE  # ccells cannot link on themselves
            if len(Cands[r0][c0]) == 2: return LK_STWK, LK_CELL
            return LK_WEAK, CELL
        # different cells, therefore linked by same candidate
        if Cand0 != Cand1: return LK_NONE, LK_NONE
        if r0 == r1:  # house is a row
            LkHse = LK_ROW
            if c0//3 == c1//3: LkHse |= LK_BOX
            for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {c0, c1}:
                if Cand0 in Cands[r0][c]: return LK_WEAK, LkHse
            return LK_STWK, LkHse
        if c0 == c1:  # house is a column
            LkHse = LK_COL
            if r0//3 == r1//3: LkHse |= LK_BOX
            for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {r0, r1}:
                if Cand0 in Cands[r][c0]: return LK_WEAK, LkHse
            return LK_STWK, LkHse
        rb0 = (r0//3)*3; cb0 = (c0//3)*3; rb1 = (r1//3)*3; cb1 = (c1//3)*3
        if rb0 == rb1 and cb0 == cb1:  # house is a box
            for rb in [rb0, rb0+1, rb0+2]:
                for cb in [cb0, cb0+1, cb0+2]:
                    if (rb, cb) in {(r0, c0), (r1, c1)}: continue
                    if Cand0 in Cands[rb][cb]: return LK_WEAK, LK_BOX
            return LK_STWK, LK_BOX
        return LK_NONE, LK_NONE

# cdef inline int cands_in_row_c(int r, int Cand, bint Cands[9][9][9]):
#     cdef int c, n = 0
#
#     for c in range(9):
#         if Cands[r][c][Cand-1]: n += 1
#     return n
#
# cdef inline int cands_in_col_c(int c, int Cand, bint Cands[9][9][9]):
#     cdef int r, n = 0
#
#     for r in range(9):
#         if Cands[r][c][Cand-1]: n += 1
#     return n
#
# cdef inline int cands_in_box_c(int b, int Cand, bint Cands[9][9][9]):
#     cdef int br, bc, r, c, n = 0
#
#     br = (b//3)*3; bc = (b%3)*3
#     for r in range(br, br+3):
#         for c in range(bc, bc+3):
#             if Cands[r][c][Cand-1]: n += 1
#     return n

cdef int how_ccells_linked_c(int r0, int c0, int Cand0, int r1, int c1, int Cand1, bint Cands[9][9][9]):
    cdef int LkH, r, c, rb0, cb0, rb1, cb1

    if r0 == r1 and c0 == c1:
        if Cand0 == Cand1: return LK_NONE_C  # ccells cannot link on themselves
        #### FIX BUG #### Need to count # Nr Cands = True in Cands[][][].
        if len(Cands[r0][c0]) == 2: return LK_STWK_C | LK_CELL_C
        return LK_WEAK_C | LK_CELL_C
    # different cells, therefore linked by same candidate
    if Cand0 != Cand1: return LK_NONE
    if r0 == r1:  # house is a row
        LkH = LK_ROW_C
        if c0//3 == c1//3: LkH |= LK_BOX_C
        for c in range(9):
            if c == c0 or c == c1: continue
            # TRCX(f"{Cand0+1}r{r0+1}c{c+1}=={Cands[r0][c][Cand0]}")
            if Cands[r0][c][Cand0]: return LK_WEAK_C | LkH
        return LK_STWK_C | LkH
    if c0 == c1:  # house is a col
        LkH = LK_COL_C
        if r0//3 == r1//3: LkH |= LK_BOX_C
        for r in range(9):
            if r == r0 or r == r1: continue
            # TRCX(f"{Cand0+1}r{r+1}c{c0+1}=={Cands[r][c0][Cand0]}")
            if Cands[r][c0][Cand0]: return LK_WEAK_C | LkH
        return LK_STWK_C | LkH
    rb0 = (r0//3)*3; cb0 = (c0//3)*3; rb1 = (r1//3)*3; cb1 = (c1//3)*3
    if rb0 == rb1 and cb0 == cb1:  # house is a box
        for r in range(rb0, rb0+3):
            for c in range(cb0, cb0+3):
                if (r == r0 and c == c0) or (r == r1 and c == c1): continue
                # TRCX(f"{Cand0+1}r{r+1}c{c+1}=={Cands[r][c][Cand0]}")
                if Cands[r][c][Cand0]: return LK_WEAK_C | LK_BOX_C
        return LK_STRG_C | LK_BOX_C
    return LK_NONE_C | LK_NONE_C

cdef int how_ccells_linked_gl_c(SET3 r0, SET3 c0, int Cand0, SET3 r1, SET3 c1, int Cand1,bint Cands[9][9][9]):

    TRCX("TODO: Stubbed out")
    return LK_NONE_C


def find_all_strong_cand_links(Cand, Cands, GrpLks = False):
    # Finds all the strong links for a candidate and enters makes two entries
    # in the list for same cand links in house, one from each side.  Returns
    # a list of (r, c, Cand) tuples not CCELLS as tuples are compared literally
    # but comparision of classes will compare the pointers to the instance and
    # not the contents of the class.

    SLks = find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks)

    for r in range(9):
        for c in range(9):
            if len(Cands[r][c])== 2 and Cand in Cands[r][c]:
                if GrpLks: SLks.append((({r}, {c}, Cand), ({r}, {c}, list(Cands[r][c] ^ {Cand})[0])))
                else: SLks.append(((r, c, Cand), (r, c, list(Cands[r][c] ^ {Cand})[0])))
    return SLks

def find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks = False):
    # only finds strong links for the passed cand between cells.
    # returns Lks[((r0, c0), (r1, c1)), . . .] without the cand.
    # Note that ((r0, c0), (r1, c1)) and ((r1, c1), (r0, c0)) are seen as distinct
    # and both tuples are returned in the list for the same candidate.

    # Note that if GrpLks is True, then all coords are returned as sets.  If GrpLks are
    # False, all coords are scalars.

    Lks = []
    if GrpLks:
        # look in rows
        for r in range(9):
            C = []; Twr = [set(), set(), set()]
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c); Twr[c//3].add(c)
            if len(C) == 2:  # and (((r, C[0]), (r, C[1])) not in Lks and ((r, C[1]), (r, C[0])) not in Lks):
                Lks.extend([((r, C[0], Cand), (r, C[1], Cand)), ((r, C[1], Cand), (r, C[0], Cand))])
            else:
                if Twr[0] and Twr[1] and Twr[2]: continue
                if Twr[0] and Twr[1]:   Lks.extend([((r, Twr[0], Cand), (r, Twr[1], Cand)), ((r, Twr[1], Cand), (r, Twr[0], Cand))])
                elif Twr[0] and Twr[2]: Lks.extend([((r, Twr[0], Cand), (r, Twr[2], Cand)), ((r, Twr[2], Cand), (r, Twr[0], Cand))])
                elif Twr[1] and Twr[2]: Lks.extend([((r, Twr[1], Cand), (r, Twr[2], Cand)), ((r, Twr[2], Cand), (r, Twr[1], Cand))])
        # look in cols
        for c in range(9):
            R = []; Flr = [set(), set(), set()]
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r); Flr[r//3].add(r)
            if len(R) == 2 and (((R[0], c), (R[1], c)) not in Lks and ((R[1], c), (R[0], c)) not in Lks):
                Lks.extend([((R[0], c, Cand), (R[1], c, Cand)), ((R[1], c, Cand), (R[0], c, Cand))])
            else:
                if Flr[0] and Flr[1] and Flr[2]: continue
                if Flr[0] and Flr[1]:   Lks.extend([((Flr[0], c, Cand), (Flr[1], c, Cand)), ((Flr[1], c, Cand), (Flr[0], c, Cand))])
                elif Flr[0] and Flr[2]: Lks.extend([((Flr[0], c, Cand), (Flr[2], c, Cand)), ((Flr[2], c, Cand), (Flr[0], c, Cand))])
                elif Flr[1] and Flr[2]: Lks.extend([((Flr[1], c, Cand), (Flr[2], c, Cand)), ((Flr[2], c, Cand), (Flr[1], c, Cand))])
        # #look in boxes
        for br, bc in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
            # 1.  Examine the ccells in the box
            B1 = []
            RB = [set(), set(), set()]; CB = [set(), set(), set()]
            br1 = br+1; br2 = br+2; bc1 = bc+1; bc2 = bc+2
            for i, j, r, c in [(0, 0, br, bc), (0, 1, br, bc1), (0, 2, br, bc2),
                               (1, 0, br1, bc), (1, 1, br1, bc1), (1, 2, br1, bc2),
                               (2, 0, br2, bc), (2, 1, br2, bc1), (2, 2, br2, bc2)]:
                if Cand in Cands[r][c]:
                    B1.append((r, c))
                    RB[i].add(c); CB[j].add(r)
            lenRB0 = len(RB[0]); lenRB1 = len(RB[1]); lenRB2 = len(RB[2])
            lenCB0 = len(CB[0]); lenCB1 = len(CB[1]); lenCB2 = len(CB[2])
            # 2. Check out rows patterns
            if lenRB0 > 0 and lenRB1 > 0 and lenRB2 == 0:   Lks.extend([((br, RB[0], Cand), (br1, RB[1], Cand)), ((br1, RB[1], Cand), (br, RB[0], Cand))])
            elif lenRB0 > 0 and lenRB1 == 0 and lenRB2 > 0: Lks.extend([((br, RB[0], Cand), (br2, RB[2], Cand)), ((br2, RB[2], Cand), (br, RB[0], Cand))])
            elif lenRB0 == 0 and lenRB1 > 0 and lenRB2 > 0: Lks.extend([((br1, RB[1], Cand), (br2, RB[2], Cand)), ((br2, RB[2], Cand), (br1, RB[1], Cand))])
            # 3. Check out col patterns
            if lenCB0 > 0 and lenCB1 > 0 and lenCB2 == 0:   Lks.extend([((CB[0], bc, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (CB[0], bc, Cand))])
            elif lenCB0 > 0 and lenCB1 == 0 and lenCB2 > 0: Lks.extend([((CB[0], bc, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (CB[0], bc, Cand))])
            elif lenCB0 == 0 and lenCB1 > 0 and lenCB2 > 0: Lks.extend([((CB[1], bc1, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (CB[1], bc1, Cand))])
            # 4. Check out row/col patterns
            RP = sorted([lenRB0, lenRB1, lenRB2]); CP = sorted([lenCB0, lenCB1, lenCB2])
            if RP == CP == [1, 1, 2]:
                # |** |   |* *| Family
                # |  *|   | * |
                # |  *|   | * |
                # filter out invalid [1,1,2] patterns eg /**./ /..*/ /.*./, ie all cands must be covered by a row and a col only.
                # an invalid pattern is when a cand is not part of a row or a col, ie it is the only candidate in the row and the col.
                for k in [0, 1, 2]:
                    if len(RB[k]) == 1 and len(CB[list(RB[k])[0]%3]) == 1: break
                else:
                    if lenRB0 == 2:
                        if lenCB0 == 2:   Lks.extend([((br, RB[0], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br, RB[0], Cand))])
                        elif lenCB1 == 2: Lks.extend([((br, RB[0], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br, RB[0], Cand))])
                        elif lenCB2 == 2: Lks.extend([((br, RB[0], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2:
                        if lenCB0 == 2:   Lks.extend([((br1, RB[1], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br1, RB[1], Cand))])
                        elif lenCB1 == 2: Lks.extend([((br1, RB[1], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br1, RB[1], Cand))])
                        elif lenCB2 == 2: Lks.extend([((br1, RB[1], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2:
                        if lenCB0 == 2:   Lks.extend([((br2, RB[2], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br2, RB[2], Cand))])
                        elif lenCB1 == 2: Lks.extend([((br2, RB[2], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br2, RB[2], Cand))])
                        elif lenCB2 == 2: Lks.extend([((br2, RB[2], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br2, RB[2], Cand))])
            elif RP == [0, 1, 3] and CP == [1, 1, 2]:
                # |   |  |  +| Family
                # |  +|  |   |
                # |**+|  |**+|
                if lenRB0 == 3:  # and lenRB1 == 1:
                    if lenCB0 == 2:   Lks.extend([((br, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br, {bc, bc1}, Cand))])
                elif lenRB1 == 3:
                    if lenCB0 == 2:   Lks.extend([((br1, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br1, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br1, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br1, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br1, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br1, {bc, bc1}, Cand))])
                elif lenRB2 == 3:
                    if lenCB0 == 2:   Lks.extend([((br2, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br2, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br2, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br2, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br2, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br2, {bc, bc1}, Cand))])
            elif RP == [1, 1, 2] and CP == [0, 1, 3]:
                # above patterns rotated by 90degs
                if lenCB0 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc, Cand)), (({br1, br2}, bc, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc, Cand)), (({br, br2}, bc, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc, Cand)), (({br, br1}, bc, Cand), (br2, RB[2], Cand))])
                elif lenCB1 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc1, Cand)), (({br1, br2}, bc1, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc1, Cand)), (({br, br2}, bc1, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc1, Cand)), (({br, br1}, bc1, Cand), (br2, RB[2], Cand))])
                elif lenCB2 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc2, Cand)), (({br1, br2}, bc2, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc2, Cand)), (({br, br2}, bc2, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc2, Cand)), (({br, br1}, bc2, Cand), (br2, RB[2], Cand))])
            elif RP == CP == [1, 1, 3]:
                # |  +|  |  +| Family
                # |  +|  |  +|
                # |**+|  |***|
                if lenRB0 == 3:
                    if lenCB0 == 3:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc, Cand)),  ((CB[0], bc, Cand), (br, {bc1, bc2}, Cand)), (({br1, br2}, bc, Cand), (br, RB[0], Cand)),  ((br, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc1, Cand)), ((CB[1], bc1, Cand), (br, {bc, bc2}, Cand)), (({br1, br2}, bc1, Cand), (br, RB[0], Cand)), ((br, {bc, bc2}, Cand), (CB[1], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc2, Cand)), ((CB[2], bc2, Cand), (br, {bc, bc1}, Cand)), (({br1, br2}, bc2, Cand), (br, RB[0], Cand)), ((br, {bc, bc1}, Cand), (CB[2], bc2, Cand))])
                elif lenRB1 == 3:
                    if lenCB0 == 3:   Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc, Cand)),  ((CB[0], bc, Cand), (br1, {bc1, bc2}, Cand)), (({br, br2}, bc, Cand), (br1, RB[1], Cand)),  ((br1, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc1, Cand)), ((CB[1], bc1, Cand), (br1, {bc, bc2}, Cand)), (({br, br2}, bc1, Cand), (br1, RB[1], Cand)), ((br1, {bc, bc2}, Cand), (CB[1], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc2, Cand)), ((CB[2], bc2, Cand), (br1, {bc, bc1}, Cand)), (({br, br2}, bc2, Cand), (br1, RB[1], Cand)), ((br1, {bc, bc1}, Cand), (CB[2], bc2, Cand))])
                elif lenRB2 == 3:
                    if lenCB0 == 3:   Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc, Cand)),  ((CB[0], bc, Cand), (br2, {bc1, bc2}, Cand)), (({br, br1}, bc, Cand), (br2, RB[2], Cand)),  ((br2, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc1, Cand)), ((CB[1], bc1, Cand), (br2, {bc, bc2}, Cand)), (({br, br1}, bc1, Cand), (br2, RB[2], Cand)), ((br2, {bc, bc2}, Cand), (CB[1], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc2, Cand)), ((CB[2], bc2, Cand), (br2, {bc, bc1}, Cand)), (({br, br1}, bc2, Cand), (br2, RB[2], Cand)), ((br2, {bc, bc1}, Cand), (CB[2], bc2, Cand))])
        # cleanup, convert all cell coords to sets and remove duplicates.
        Lks1 = []
        for ((r0, c0, Cand0), (r1, c1, Cand1)) in Lks:
            R0 = {r0} if isinstance(r0, int) else r0
            C0 = {c0} if isinstance(c0, int) else c0
            R1 = {r1} if isinstance(r1, int) else r1
            C1 = {c1} if isinstance(c1, int) else c1

            for ((Ra, Ca, Canda), (Rb, Cb, Candb)) in Lks1:
                if ccells_match(Ra, Ca, Canda, R0, C0, Cand0, GrpLks) and ccells_match(Rb, Cb, Candb, R1, C1, Cand1, GrpLks): continue
            else: Lks1.append(((R0, C0, Cand0), (R1, C1, Cand1)))
    else:  # No group links
        # look in rows
        for r in range(9):
            C = []
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c)
            if len(C) == 2:  # and (((r, C[0]), (r, C[1])) not in Lks and ((r, C[1]), (r, C[0])) not in Lks):
                Lks.extend([((r, C[0], Cand), (r, C[1], Cand)), ((r, C[1], Cand), (r, C[0], Cand))])
        # look in cols
        for c in range(9):
            R = []
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r)
            if len(R) == 2:  # and (((R[0], c), (R[1], c)) not in Lks and ((R[1], c), (R[0], c)) not in Lks):
                Lks.extend([((R[0], c, Cand), (R[1], c, Cand)), ((R[1], c, Cand), (R[0], c, Cand))])
        # look in boxes
        for b in range(9):
            rb = (b//3)*3; cb = (b%3)*3
            B = []
            for r in [rb, rb+1, rb+2]:
                for c in [cb, cb+1, cb+2]:
                    if Cand in Cands[r][c]: B.append((r, c, Cand))
            if len(B) == 2:
                if (B[0], B[1]) not in Lks: Lks.extend([(B[0], B[1]), (B[1], B[0])])
        # cleanup, convert single candidate sets and remove duplicates.
        Lks1 = []
        for ((ra, ca, Canda), (rb, cb, Candb)) in Lks:
            if ((ra, ca, Canda), (rb, cb, Candb)) in Lks1: continue
            # if ((ra, ca), (rb, cb)) in Lks1 or ((rb, cb), (ra, ca)) in Lks: continue
            Lks1.append(((ra, ca, Candb), (rb, cb, Candb)))
    return Lks1

# general functions used while solving.

cdef void qd_inplace_sort_c(int* pA, int lenA):
    # A quick and dirty inplace sort.  Efficient for small sized (<64) arrays of ints.  Uses a bubble sort variation
    cdef int i, j, k

    for i in range(lenA-1):
        for j in range(lenA-i):
            if pA[j] > pA[j+1]:
                k = pA[j]; pA[j] = pA[j+1]; pA[j+1] = k



# diagnostic code for walking tree nodes - not used for a while, may have bitrot.

def walk_ai_trees(Orchards, path):
    # Walks an orchard of AI trees printing out the nodes and their branches.
    # Trees is list of orchards, one per candidate.  The next level up is the list of trees in the
    # orchard for that candidate.  The following level up is the first level of branches per tree
    # which is the start of chains.
    Lvl = 0
    with open(path, "wt") as f:
        for i, Trees in enumerate(Orchards):
            f.write(f"Candidate {i+1} Orchard\n")
            for Tree in Trees: traverse_branch(Tree, Lvl, f)

def traverse_branch(B, Lvl, f):
    sLk = ""
    sL = ""
    for i in range(Lvl): sL += "| "
    sL += f"+{ascii_lk(B.Lk)}{B.Cand}r{B.r+1}c{B.c+1}"
    if B.Chain:
        sL += f", Chain: "
        for r, c, Cand, Lk in B.Chain:
            sL += f"{Cand}r{r+1}c{c+1}{ascii_lk(Lk)}"
    if B.Parent: sL += f", Parent: {B.Parent.Cand}r{B.Parent.r+1}c{B.Parent.c+1}"
    f.write(sL + "\n")
    for SB in B.Children: traverse_branch(SB, Lvl+1, f)

def ascii_lk(Lk):
    if Lk == LK_WEAK: return "-"
    elif Lk == LK_STRG or Lk == LK_STWK: return "="
    elif Lk == LK_WKST: return "~"
    else: return "*"

