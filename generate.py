from copy import copy, deepcopy
from random import randint, sample, seed

from globals import *
from solve import *

seed()
if DEBUG:
    import logging as log

    seed(0)

def check_puzzle(Grid, Soln, cell = 0):
    #  Recursive backtracking function to check a Sudoku puzzle. Returns True
    #  if only one solution is found, returns False if there is no solution or
    #  more than one solution.
    #  The information in Grid is not preserved.
    #  Grid:  In:  A sudoku puzzle to test
    #         Recursive call:  Partially tested
    #         Out:  Preserved Grid as passed if puzzle has a valid solution
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
    while cell < 81:
        r = cell//9
        c = cell%9
        if Grid[r][c] != 0:
            cell += 1
        else:
            break
    else:  # cell = 81:- All cells successfully filled
        Soln[S_FOUND] += 1
        if Soln[S_FOUND] == 1:  # This is the first solution
            Soln[S_GRID] = [[Grid[r][c] for c in range(9)] for r in range(9)]
            return False  # Continue looking for a second solution
        else:  # a second solution found - this is an invalid puzzle
            return True  # 2nd soln found pop back out of the stack.

    for v in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        if cell_val_has_no_conflicts(v, Grid, r, c):
            Grid[r][c] = v
            if check_puzzle(Grid, Soln, cell+1):
                Grid[r][c] = 0
                return True
    Grid[r][c] = 0
    return False

def gen_filled_grid(Grid, cell = 0):
    #  Recursive backtracking function to generate a full Grid that obeys
    #  Sudoku rules
    #  Grid: In:  a complete zeroed out Grid, otherwise undefined results
    #        Recursive call:  A partially filled Grid with values between
    #                         1 and 9
    #        Out:  completed board
    #  cell: In: Optional: - must be 0 or omitted if not called recursively
    #        Recursive call: The current cell position
    #  Returns:  True always to the non-recursive caller

    if cell >= 81:
        return True
    r = cell//9
    c = cell%9
    vals = sample(range(1, 10), k = 9)
    #    vals = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    #    shuffle(vals)
    for v in vals:
        if cell_val_has_no_conflicts(v, Grid, r, c):
            Grid[r][c] = v
            if gen_filled_grid(Grid, cell+1):
                return True
    Grid[r][c] = 0
    return False

def scramble_puzzle(grid):
    # Creates a mathematically equivalent puzzle by shuffling the puzzle.
    # grid:  In: The Sudoku puzzle to scramble.
    #        Out: a partially scrambled puzzle.
    # Returns: The scrambled puzzle.

    grid1 = [[] for r in range(9)]
    # Shuffle the rows in bands of 3:   grid  ==> grid1, refs
    for bi in [0, 3, 6]:  # In each band
        for dri, sri in enumerate(sample([0, 1, 2], k = 3)):
            grid1[bi+dri] = grid[bi+sri]

    # Shuffle the bands:  grid1 ==> grid, refs
    for dbi, sbi in enumerate(sample([0, 3, 6], k = 3)):  # sbi | dbi source | dest band idx,
        dbi1 = dbi*3
        grid[dbi1] = grid1[sbi]
        grid[dbi1+1] = grid1[sbi+1]
        grid[dbi1+2] = grid1[sbi+2]

    # It is easier to transpose and shuffle rows than to shuffle cols
    # grid ==> grid1, vals
    grid1 = [[grid[c][r] for c in range(len(grid))] for r in range(len(grid[0]))]

    # shuffle transposed rows in bands of 3:   grid1 ==> grid, refs
    for bi in [0, 3, 6]:  # In each band
        for dri, sri in enumerate(sample([0, 1, 2], k = 3)):  # sri | dri: source | row idx,
            grid[bi+dri] = grid1[bi+sri]

    # Shuffle the bands:  grid  ==> grid1, refs
    for dbi, sbi in enumerate(sample([0, 3, 6], k = 3)):
        dbi1 = dbi*3
        grid1[dbi1] = grid[sbi]
        grid1[dbi1+1] = grid[sbi+1]
        grid1[dbi1+2] = grid[sbi+2]

    v = sample(range(1, 10), k = 9)  # randomize the 9 digits
    v.insert(0, 0)

    R = randint(0, 7)
    if R == 0:
        return [[v[grid1[r][c]] for c in range(9)] for r in range(9)]
    elif R == 1:
        return [[v[grid1[r][8-c]] for c in range(9)] for r in range(9)]
    elif R == 2:
        return [[v[grid1[8-r][c]] for c in range(9)] for r in range(9)]
    elif R == 3:
        return [[v[grid1[8-r][8-c]] for c in range(9)] for r in range(9)]
    elif R == 4:
        return [[v[grid1[c][r]] for c in range(9)] for r in range(9)]
    elif R == 5:
        return [[v[grid1[c][8-r]] for c in range(9)] for r in range(9)]
    elif R == 6:
        return [[v[grid1[8-c][r]] for c in range(9)] for r in range(9)]
    else:  # R == 7
        return [[v[grid1[8-c][8-r]] for c in range(9)] for r in range(9)]

def minimalise_puzzle(G):

    H = []
    for r in range(9):
        for c in range(9):
            if G[r][c] != 0:
                H.append(r*9 + c)

    G1 = [[G[r][c] for c in range(9)] for r in range(9)]
    for hdx in sample(H, k = len(H)):
        r = hdx//9
        c = hdx%9
        v = G1[r][c]
        G1[r][c] = 0
        Soln = {S_FOUND: 0, S_GRID: None}
        check_puzzle(G1, Soln)
        if Soln[S_FOUND] == 1:
            G[r][c] = 0
        else:
            G1[r][c] = v

def _create_random_puzzle(Grid, Props):
    #  Creates a puzzle with up to nh randomly placed holes that can be solved
    #  using the techniques passed in ltl.
    #  Grid:    In:  A fully populated Grid (board) that obeys Sudoku rules
    #           Out: A valid puzzle with up to nh holes dug
    #  Props    Out: Ordered lists of the the specific logic steps to solve
    #                each hole.
    #  returns: True with a valid puzzle.
    #           False with an invalid puzzle. (To be implemented)

    h = sample(range(81), k = 81)
    Props[PR_NR_HOLES] = 0
    for hdx in h:
        Grid1 = [[Grid[r][c] for c in range(9)] for r in range(9)]
        r = hdx//9
        c = hdx%9
        # v = Grid1[r][c]
        Grid1[r][c] = 0
        Soln = {S_FOUND: 0, S_GRID: None}
        check_puzzle(Grid1, Soln)  # check_puzzle() returns with unsolved puzzle preserved in Grid1
        if Soln[S_FOUND] == 1:
            grade_puzzle(Grid1, Props)  # grade_puzzle returns with solved puzzle in Grid1
            if Props[PR_REQ_LVL] >= Props[PR_ACT_LVL]:
                Grid[r][c] = 0
                Props[PR_NR_HOLES] += 1

def _create_dihedral_puzzle(grid, nh, ltl, props):
    # TODO _create_dihedral_puzzle(grid, nh, ltl, props):
    pass

def _create_square_quad_rotated_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging _create_square_quad_rotated_puzzle(grid, nh, ltl, props):

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

    h = sample(range(25), k = 25)
    #    h = [x for x in range(25)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx//5
        c = hdx%5
        hcnt = 0
        if (r == 4) & (c == 4):
            if thcnt+1 > nh:
                break
            grid1[r][c] = 0  # rotational pivot
        elif r < 4:
            if thcnt+4 > nh:
                break
            grid1[r][c] = 0  # Q1
            grid1[c][8-r] = 0  # Q2
            grid1[8-r][8-c] = 0  # Q3
            grid1[8-r][c] = 0  # Q4
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Solns) & solve_puzzle(grid2, ltl, props = []):
            # put the holes in kept grid
            if r == 4 & c == 4:
                grid[r][c] = 0
                hcnt += 1
            elif r < 4:
                grid[r][c] = 0  # Q1
                grid[c][8-r] = 0  # Q2
                grid[8-r][8-c] = 0  # Q3
                grid[8-r][c] = 0  # Q4
                hcnt += 4
            thcnt += hcnt
    return True

def _create_square_quad_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging _create_square_quad_mirrored_puzzle

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

    h = sample(range(25), k = 25)
    #    h = [x for x in range(25)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx//5
        c = hdx%5
        #  Q1
        grid1[r][c] = 0
        hcnt = 1
        #  Q2
        if c < 4:
            grid1[r][8-c] = 0
            hcnt += 1
        #  Q3
        if (r < 4) & (c < 4):
            grid1[8-r][8-c] = 0
            hcnt += 1
        #  Q4
        if r < 4:
            grid1[8-r][c] = 0
            hcnt += 1
        if thcnt+hcnt > nh:
            break  # we're done!
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Solns) & solve_puzzle(grid2, ltl, props = []):
            # dig the holes in kept grid
            grid[r][c] = 0
            #  Q2
            if c < 4:
                grid[r][8-c] = 0
            #  Q3
            if (r < 4) & (c < 4):
                grid[8-r][8-c] = 0
            #  Q4
            if r < 4:
                grid[8-r][c] = 0

            thcnt += hcnt
    return True

def _create_diag_quad_rotated_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_quad_rotated_puzzle
    pass

def _create_diag_quad_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_quad_mirrored_puzzle
    pass

def _create_vert_rotated_puzzle(grid, nh, ltl, steps):
    # TODO: Needs debugging _create_vert_rotated_puzzle

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

    h = sample(range(25), k = 25)
    #    h = [x for x in range(41)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx%9
        c = hdx//9
        grid1[r][c] = 0
        hcnt = 1
        if (r != 4) & (c != 4):  # cell is not the centre pivot.
            grid1[8-r][8-c] = 0
            hcnt += 1
        if thcnt+hct > nh:
            break  # we're done!
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
            grid[r][c] = 0
            if (r != 4) & (c != 4):  # cell is not the centre pivot.
                grid1[8-r][8-c] = 0
            thcnt += hcnt
    return True

def _create_vert_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging _create_vert_mirrored_puzzle

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

    h = sample(range(45), k = 45)
    #    h = [x for x in range(45)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx%9
        c = hdx//9
        grid1[r][c] = 0
        hcnt = 1
        if c < 4:
            grid1[r][8-c] = 0
            hcnt += 1
        if thcnt+hct > nh:
            break  # we're done!
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
            grid[r][c] = 0
            if c < 4:
                grid1[r][8-c] = 0
            thcnt += hcnt
    return True

def _create_horz_rotated_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging _create_horz_rotated_puzzle

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

    h = sample(range(41), k = 41)
    #    h = [x for x in range(41)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx//9
        c = hdx%9
        grid1[r][c] = 0
        hcnt = 1
        if (r != 4) & (c != 4):  # cell is not the centre pivot.
            grid1[8-r][8-c] = 0
            hcnt += 1
        if thcnt+hct > nh:
            break  # we're done!
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
            grid[r][c] = 0
            if (r != 4) & (c != 4):  # cell is not the centre pivot.
                grid1[8-r][8-c] = 0
            thcnt += hcnt
    return True

def _create_horz_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: Needs debugging _create_horz_mirrored_puzzle

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

    h = sample(range(45), k = 45)
    #    h = [x for x in range(45)]
    #    shuffle(h)
    thcnt = 0
    for hdx in h:
        grid1 = deepcopy(grid)
        r = hdx//9
        c = hdx%9
        grid1[r][c] = 0
        hcnt = 1
        if r < 4:
            grid1[8-r][c] = 0
            hcnt += 1
        if thcnt+hct > nh:
            break  # we're done!
        grid2 = deepcopy(grid1)
        if _check_puzzle(grid1, Soln) & solve_puzzle(grid2, ltl, props = []):
            grid[r][c] = 0
            if r < 4:
                grid1[8-r][c] = 0
            thcnt += hcnt
    return True

def _create_diag_top_left_rotated_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_top_left_rotated_puzzle
    pass

def _create_diag_top_left_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_top_left_mirrored_puzzle
    pass

def _create_diag_bot_left_rotated_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_bot_left_rotated_puzzle
    pass

def _create_horz_bot_left_mirrored_puzzle(grid, nh, ltl, props):
    # TODO: _create_diag_bot_left_mirrored_puzzle
    pass

# Pointer to function array for generating puzzles with symmetry types
CreatePuzzle = [_create_random_puzzle,
                _create_dihedral_puzzle,
                _create_square_quad_rotated_puzzle,
                _create_square_quad_mirrored_puzzle,
                _create_diag_quad_rotated_puzzle,
                _create_diag_quad_mirrored_puzzle,
                _create_vert_rotated_puzzle,
                _create_vert_mirrored_puzzle,
                _create_horz_rotated_puzzle,
                _create_horz_mirrored_puzzle,
                _create_diag_top_left_rotated_puzzle,
                _create_diag_top_left_mirrored_puzzle,
                _create_diag_bot_left_rotated_puzzle,
                _create_horz_bot_left_mirrored_puzzle]

"""
Not so sure we don't need these functions so I'll hang on to them for the time
being . . .

@staticmethod
def solve_puzzle_backtrack(grid, cell = 0):
    #  Recursive backtracking function to find a Sudoku puzzle. If the
    #  puzzle is not a valid sudoku either the first solution found will be
    #  in grid, or returns False if no solution found.
    #  grid: In:  A sudoku puzzle (can process invalid puzzles too)
    #        Recursive call:  Partially solved puzzle
    #        Out:  completed puzzle if function returns True
    #  cell: In: Optional: - must be 0 if not called recursively
    #        Recursive call: The current cell position
    #  Returns:  True: a solution found - does not imply a valid puzzle
    #            False: no solution found - implies invalid puzzle

    #  Find the next hole in the puzzle.
    while cell < 81:
        r = cell // 9
        c = cell % 9
        if grid[r][c] != 0:
            cell += 1
        else:
            break
    else:
        return True  # All cells successfully filled

    vals = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for v in vals:
        if _cell_val_has_no_conflicts(v, grid, r, c):
            grid[r][c] = v
            if solve_puzzle_backtrack(grid, cell + 1):
                return True
    grid[r][c] = 0
    return False

@staticmethod
def test_puzzle_givens(grid):
    #  Ensures that the givens obey Sudoku rules.
    #  grid:     In:  Puzzle to test, populated with givens.
    #  Returns:  True:  if a valid puzzle
    #            False: if an invalid puzzle

    #  Check that the givens obey Sudoku rules.
    for bi in range(0, 9):
        br = (bi // 3) * 3
        bc = (bi % 3) * 3
        row = [[grid[bi][0:8]]]
        row = [x for x in row if x != 0]  # remove 0 from list
        if len(row) != len(set(row)):
            return False
        col = [[grid[0][bi], grid[1][bi], grid[2][bi], grid[3][bi], grid[4][bi],
                grid[5][bi], grid[6][bi], grid[7][bi], grid[8][bi]]]
        col = [x for x in col if x != 0]  # remove 0 from list
        if len(col) != len(set(col)):
            return False
        box = [[grid[br][bc:bc + 3] + grid[br + 1][bc:bc + 3]
                + grid[br + 2][bc:bc + 3]]]
        box = [x for x in box if x != 0]  # remove 0 from list
        if len(box) != len(set(box)):
            return False
    return True

@staticmethod
def test_puzzle(grid):
    #  Checks that the givens obey Sudoku rules and that there is only one
    #  unique solution.
    #  grid:    In:  The puzzle to test, grid is preserved on return.
    #  Returns:  True:  a valid puzzle
    #            False: an invalid puzzle

    if test_puzzle_givens(grid):
        grid1 = deepcopy(grid)  # preserve puzzle
        return _check_puzzle(grid1, Soln)
    return False

"""
