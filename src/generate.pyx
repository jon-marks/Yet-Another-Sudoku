# # for optimization - need to eliminate these imports.
# from copy import copy, deepcopy
from random import randint, shuffle, seed
from sys import path
from ctypedefs cimport SOLN_T
from generate cimport *
from solve_utils cimport *

from globals import *
from solve import *
from trc import TRCX

TRC = True if path[len(path)-1] == ".trc_true" else False

cdef extern from "stdlib.h":
    void   srand (unsigned int)
    int    rand()

cdef extern from "time.h":
    long int time(int)

TRCX("SADFSDF")

if TRC:
#    import logging as log
    seed(0)
    srand(0)
else:
    seed()
    srand(time(0))

def check_puzzle(Grid):
    # Python wrapper to Cython/C check_puzzle_c
    cdef SOLN_T Soln,
    cdef SOLN_T *pSoln = &Soln
    cdef int G[9][9]
    cdef r, c

    Soln.Found = 0
    for r in range(9):
        for c in range(9):
            G[r][c] = Grid[r][c]
    check_puzzle_c(G, &Soln, 0)
    return Soln.Found, [[Soln.SlvdG[r][c] for c in range(9)] for r in range(9)]

cdef bint check_puzzle_c(int G[9][9], SOLN_T* pSoln, int cell):
    #  Recursive backtracking function to solve a Sudoku puzzle as a check.
    #  Returns True if only one solution is found, returns False if there is no
    #  solution or more than one solution.
    #  The information in G is not preserved.
    #  G:  In:  A sudoku puzzle to check
    #         Recursive call:  Partially tested
    #         Out:  Preserved G as passed if puzzle has a valid solution
    #  cell:  In: Optional: - must be 0 if not called recursively
    #         Recursive call: The current cell position
    #  Soln[S_FOUND]: In: Don't Care
    #                 Out: 1 - Puzzle is valid
    #                      else - Puzzle is invalid
    #  Soln[S_GRID]:  In:  None
    #                 Out: Solved puzzle grid if Soln[S_FOUND] == 1
    #                 Out: undefined.
    #  Returns:  Undefined.

    #  Find the next hole in the puzzle.
    cdef int r, c, v

    while cell < 81:
        r = cell//9
        c = cell%9
        if G[r][c] != 0:
            cell += 1
        else:
            break
    else:  # cell = 81:- All cells successfully filled
        pSoln[0].Found += 1
        if pSoln[0].Found == 1:  # This is the first solution
            for r in range(9):
                for c in range(9):
                    pSoln[0].SlvdG[r][c] = G[r][c]
            return False
        else:  # a second solution found - this is an invalid puzzle
            return True  # 2nd soln found pop back out of the stack.

    for v in range(1, 10):
        if cell_val_has_no_conflicts_c(v, G, r, c):
            G[r][c] = v
            if check_puzzle_c(G, pSoln, cell+1):
                G[r][c] = 0
                return True
    G[r][c] = 0
    return False

def gen_filled_grid():
    # Python wrapper for Cython gen_filled_grid
    cdef int G[9][9]
    cdef int r, c, cell = 0

   # TRC("Another trc test")
    for r in range(9):
        G[r][:] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    gen_filled_grid_c(G, cell)
    return [[G[r][c] for c in range(9)] for r in range(9)]

cdef bint gen_filled_grid_c(int G[9][9], int cell):
    #  Recursive backtracking function to generate a full Grid that obeys
    #  Sudoku rules
    #  Grid: In:  a complete zeroed out Grid, otherwise undefined results
    #        Recursive call:  A partially filled Grid with values between
    #                         1 and 9
    #        Out:  completed board
    #  cell: In: Optional: - must be 0 or omitted if not called recursively
    #        Recursive call: The current cell position
    #  Returns:  True always to the non-recursive caller

    if cell >= 81: return True
    cdef int r = cell//9
    cdef int c = cell%9
    cdef int v, l = 9
    cdef unsigned rrand, t
    cdef int[9] vals = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Fisher Yates shuffle
    while l:
        rrand = rand() % l
        l -= 1
        t = vals[l]
        vals[l] = vals[rrand]
        vals[rrand] = t
    # TRC("Testing trace\n")
    for v in vals:
        if cell_val_has_no_conflicts_c(v, G, r, c):
            G[r][c] = v
            if gen_filled_grid_c(G, cell+1):
                return True
    G[r][c] = 0
    return False

def scramble_puzzle(grid):
    # Creates a mathematically equivalent puzzle by shuffling the puzzle.
    # grid:  In: The Sudoku puzzle to scramble.
    #        Out: a partially scrambled puzzle.
    # Returns: The scrambled puzzle.

    # No need to optimize, compiled version executes in ~30uSec - plenty fast enough.

    grid1 = [[] for r in range(9)]
    # Shuffle the rows in bands of 3:   grid  ==> grid1, refs
    for bi in [0, 3, 6]:  # In each band
        RI = [0, 1, 2]; shuffle(RI)
        for dri, sri in enumerate(RI):
            grid1[bi+dri] = grid[bi+sri]

    # Shuffle the bands:  grid1 ==> grid, refs
    BI = [0, 3, 6]; shuffle(BI)
    for dbi, sbi in enumerate(BI):  # sbi | dbi source | dest band idx,
        dbi1 = dbi*3
        grid[dbi1] = grid1[sbi]
        grid[dbi1+1] = grid1[sbi+1]
        grid[dbi1+2] = grid1[sbi+2]

    # It is easier to transpose and shuffle rows than to shuffle cols
    # grid ==> grid1, vals
    grid1 = [[grid[c][r] for c in range(len(grid))] for r in range(len(grid[0]))]

    # shuffle transposed rows in bands of 3:   grid1 ==> grid, refs
    for bi in [0, 3, 6]:  # In each band
        RI = [0, 1, 2]; shuffle(RI)
        for dri, sri in enumerate(RI):  # sri | dri: source | row idx,
            grid[bi+dri] = grid1[bi+sri]

    # Shuffle the bands:  grid  ==> grid1, refs
    BI = [0, 3, 6]; shuffle(BI)
    for dbi, sbi in enumerate(BI):
        dbi1 = dbi*3
        grid1[dbi1] = grid[sbi]
        grid1[dbi1+1] = grid[sbi+1]
        grid1[dbi1+2] = grid[sbi+2]

    v = [1, 2, 3, 4, 5, 6, 7, 8, 9]; shuffle(v)  # randomize the 9 digits
    v.insert(0, 0)

    # one of 8 ways of transposition.
    R = randint(0, 7)
    if R == 0: return [[v[grid1[r][c]] for c in range(9)] for r in range(9)]
    elif R == 1: return [[v[grid1[r][8-c]] for c in range(9)] for r in range(9)]
    elif R == 2: return [[v[grid1[8-r][c]] for c in range(9)] for r in range(9)]
    elif R == 3: return [[v[grid1[8-r][8-c]] for c in range(9)] for r in range(9)]
    elif R == 4: return [[v[grid1[c][r]] for c in range(9)] for r in range(9)]
    elif R == 5: return [[v[grid1[c][8-r]] for c in range(9)] for r in range(9)]
    elif R == 6: return [[v[grid1[8-c][r]] for c in range(9)] for r in range(9)]
    else:  return [[v[grid1[8-c][8-r]] for c in range(9)] for r in range(9)]

def minimalise_puzzle(G, T_H = None):
    # sufficient optimisation using the python wrapper check_puzzle, no need to make this
    # code a wrapper for using check_puzzle.
    from misc import grid_to_grid_str

    H = []
    for r in range(9):
        for c in range(9):
            if G[r][c] != 0:
                H.append((r, c))

    shuffle(H)
    if T_H:  H = T_H
    G1 = [[G[r][c] for c in range(9)] for r in range(9)]
    for r, c in H:
        v = G1[r][c]
        G1[r][c] = 0
        NrFound, Soln = check_puzzle(G1)
        if NrFound == 1: G[r][c] = 0
        else: G1[r][c] = v
        # print(f"[{r}][{c}]: {grid_to_grid_str(G)}")
    return G

def create_puzzle(Pzl, T_H = None, T_G = None):
    # T_H and T_G used for benchmark and other testing to control randomisation.

    print("Testing Prefix: ")
    print(PREFIX())
# if DEBUG: DBG("This is a test!!!")
    # print("Create puzzle start")
    Pzl.Soln = gen_filled_grid()
    if T_G: Pzl.Soln = T_G
    CreatePuzzle[Pzl.Sym](Pzl, T_H)  # returns Pzl.Givens in the Pzl data class (struct)
#    else:
#        CreatePuzzle[Pzl.Sym](Pzl)  # returns Pzl.Givens in the Pzl data class (struct)
#  Moving this to sudoku.py       Pzl.Lvl, Pzl.Steps = logic_solve_puzzle(Pzl.Givens)

def create_random_puzzle(Pzl, T_H = None):
    cdef int G[9][9]
    cdef int H[81]
    cdef SOLN_T Soln
    cdef int r, c, v, Hr, Hlen = 81
    # print("Create random puzzle start")
    # Give G the solution from which to dig holes..
    for r in range(9):
        for c in range(9):
            G[r][c] = Pzl.Soln[r][c]
    for r in range(81): H[r] = r
    # Fisher Yates shuffle
    while Hlen:
        Hr = rand() % Hlen
        Hlen -= 1
        r = H[Hlen]
        H[Hlen] = H[Hr]
        H[Hr] = r

    if T_H:
       for h in range(81): H[h] = T_H[h]
    # Incrementally dig a random hole and check the puzzle.  Cover hole if an invalid soln
    for Hr in H:
        r = Hr//9; c = Hr%9
        v = G[r][c]
        Soln.Found = 0
        G[r][c] = 0
        check_puzzle_c(G, &Soln, 0)
        if Soln.Found != 1: G[r][c] = v
    Pzl.Givens = [[G[r][c] for c in range(9)] for r in range(9)]

def create_dihedral_puzzle(grid, nh, ltl, props):
    # TODO create_dihedral_puzzle(grid, nh, ltl, props):
    pass

def create_square_quad_rotated_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging create_square_quad_rotated_puzzle(grid, nh, ltl, props):
    pass
    #  Creates a puzzle with holes where each hole in Q1 is found in the
    #  following consecutive quadrants symmetrically rotated by 90 degs
    #  Q1, Q2
    #  Q3, Q4
    #  Puzzle is solvable using the logic techniques in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug.
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to use (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle to be implemented with ltl.

#    h = sample(range(25), k = 25)
#    #    h = [x for x in range(25)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx//5
#        c = hdx%5
#        hcnt = 0
#        if (r == 4) & (c == 4):
#            if thcnt+1 > nh:
#                break
#            grid1[r][c] = 0  # rotational pivot
#        elif r < 4:
#            if thcnt+4 > nh:
#                break
#            grid1[r][c] = 0  # Q1
#            grid1[c][8-r] = 0  # Q2
#            grid1[8-r][8-c] = 0  # Q3
#            grid1[8-r][c] = 0  # Q4
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Solns) & solve_puzzle(grid2, ltl, props = []):
#            # put the holes in kept grid
#            if r == 4 & c == 4:
#                grid[r][c] = 0
#                hcnt += 1
#            elif r < 4:
#                grid[r][c] = 0  # Q1
#                grid[c][8-r] = 0  # Q2
#                grid[8-r][8-c] = 0  # Q3
#                grid[8-r][c] = 0  # Q4
#                hcnt += 4
#            thcnt += hcnt
#    return True

def create_square_quad_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging create_square_quad_mirrored_puzzle
    pass
    #  Creates a puzzle with holes in Q1 mirrored in other quadrants.
    #  Q2 is a horizontal fold  mirror of Q1, Q3 is a vertical fold mirror
    #  of Q1 and Q4 is a diagonal fold mirror of Q1
    #  Q1, Q2
    #  Q3, Q4
    #  Puzzle is solvable using the logic steps in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug.
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to be used (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

#    h = sample(range(25), k = 25)
#    #    h = [x for x in range(25)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx//5
#        c = hdx%5
#        #  Q1
#        grid1[r][c] = 0
#        hcnt = 1
#        #  Q2
#        if c < 4:
#            grid1[r][8-c] = 0
#            hcnt += 1
#        #  Q3
#        if (r < 4) & (c < 4):
#            grid1[8-r][8-c] = 0
#            hcnt += 1
#        #  Q4
#        if r < 4:
#            grid1[8-r][c] = 0
#            hcnt += 1
#        if thcnt+hcnt > nh:
#            break  # we're done!
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Solns) & solve_puzzle(grid2, ltl, props = []):
#            # dig the holes in kept grid
#            grid[r][c] = 0
#            #  Q2
#            if c < 4:
#                grid[r][8-c] = 0
#            #  Q3
#            if (r < 4) & (c < 4):
#                grid[8-r][8-c] = 0
#            #  Q4
#            if r < 4:
#                grid[8-r][c] = 0
#
#            thcnt += hcnt
#    return True

def create_diag_quad_rotated_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_quad_rotated_puzzle
    pass

def create_diag_quad_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_quad_mirrored_puzzle
    pass

def create_vert_rotated_puzzle(grid, nh, ltl, steps):
    # TODO: Needs debugging create_vert_rotated_puzzle
    pass
    #  Creates a puzzle where holes in the first 4.5 columns are also found in
    #  symmetric 180 degs vertically rotated positions.  Puzzle is solvable
    #  using the logic techniques in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug.
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to be used (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

#    h = sample(range(25), k = 25)
#    #    h = [x for x in range(41)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx%9
#        c = hdx//9
#        grid1[r][c] = 0
#        hcnt = 1
#        if (r != 4) & (c != 4):  # cell is not the centre pivot.
#            grid1[8-r][8-c] = 0
#            hcnt += 1
#        if thcnt+hct > nh:
#            break  # we're done!
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
#            grid[r][c] = 0
#            if (r != 4) & (c != 4):  # cell is not the centre pivot.
#                grid1[8-r][8-c] = 0
#            thcnt += hcnt
#    return True

def create_vert_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging create_vert_mirrored_puzzle
    pass
    #  Creates a puzzle where holes in the first 4 columns are mirrored in the
    #  last 4 four columns, with up to nh holes dug.  Puzzle is solvable using
    #  the logic techniques in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug..
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to be used (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

#    h = sample(range(45), k = 45)
#    #    h = [x for x in range(45)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx%9
#        c = hdx//9
#        grid1[r][c] = 0
#        hcnt = 1
#        if c < 4:
#            grid1[r][8-c] = 0
#            hcnt += 1
#        if thcnt+hct > nh:
#            break  # we're done!
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
#            grid[r][c] = 0
#            if c < 4:
#                grid1[r][8-c] = 0
#            thcnt += hcnt
#    return True

def create_horz_rotated_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging create_horz_rotated_puzzle
    pass
    #  Creates a puzzle where holes in the first 4.5 rows are also found in
    #  symmetric 108 degs horizontally rotated positions.  Puzzle is solvable
    #  using the logic techniques in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with between nh-2 and nh holes dug.
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to be used (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

#    h = sample(range(41), k = 41)
#    #    h = [x for x in range(41)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx//9
#        c = hdx%9
#        grid1[r][c] = 0
#        hcnt = 1
#        if (r != 4) & (c != 4):  # cell is not the centre pivot.
#            grid1[8-r][8-c] = 0
#            hcnt += 1
#        if thcnt+hct > nh:
#            break  # we're done!
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
#            grid[r][c] = 0
#            if (r != 4) & (c != 4):  # cell is not the centre pivot.
#                grid1[8-r][8-c] = 0
#            thcnt += hcnt
#    return True

def create_horz_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging create_horz_mirrored_puzzle
    pass
    #  Creates a puzzle where holes in the first 4 rows are mirrored in the
    #  last 4 four rows.  Puzzle is solvable using the logic techniques in ltl.
    #  grid:    In:  A fully populated grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug
    #  nh       In:  Number of holes to dig.
    #  ltl      In:  List of logic techniques to be used (To be implemented)
    #  steps    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

#    h = sample(range(45), k = 45)
#    #    h = [x for x in range(45)]
#    #    shuffle(h)
#    thcnt = 0
#    for hdx in h:
#        grid1 = deepcopy(grid)
#        r = hdx//9
#        c = hdx%9
#        grid1[r][c] = 0
#        hcnt = 1
#        if r < 4:
#            grid1[8-r][c] = 0
#            hcnt += 1
#        if thcnt+hct > nh:
#            break  # we're done!
#        grid2 = deepcopy(grid1)
#        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
#            grid[r][c] = 0
#            if r < 4:
#                grid1[8-r][c] = 0
#            thcnt += hcnt
#    return True

def create_diag_top_left_rotated_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_top_left_rotated_puzzle
    pass

def create_diag_top_left_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_top_left_mirrored_puzzle
    pass

def create_diag_bot_left_rotated_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_bot_left_rotated_puzzle
    pass

def create_horz_bot_left_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: create_diag_bot_left_mirrored_puzzle
    pass

# Pointer to function array for generating puzzles with symmetry types
CreatePuzzle = [create_random_puzzle,
                create_dihedral_puzzle,
                create_square_quad_rotated_puzzle,
                create_square_quad_mirrored_puzzle,
                create_diag_quad_rotated_puzzle,
                create_diag_quad_mirrored_puzzle,
                create_vert_rotated_puzzle,
                create_vert_mirrored_puzzle,
                create_horz_rotated_puzzle,
                create_horz_mirrored_puzzle,
                create_diag_top_left_rotated_puzzle,
                create_diag_top_left_mirrored_puzzle,
                create_diag_bot_left_rotated_puzzle,
                create_horz_bot_left_mirrored_puzzle]

