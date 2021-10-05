from random import sample
from copy import copy, deepcopy

from globals import *
from solve_utils import *
from solve_singles import *
from solve_subsets import *
from solve_fish import *
from solve_wings import *
from solve_chains import *




# Note that the order in which techniques are attempted influences the outcomes:
# * the holy grail is to solve the puzzle with the simplest techniques possible.
#     which is often not achieved because a more complex technique could
#     eliminate a candidate that makes the balance of the puzzle easier to solve
#     than a candidate to eliminate found by the the possible complex technique
# * from (perceived) simpler to more complex
# * order / size of of condition ascends
# * some, but not all techniques depend on a prior logic condition not being
#   satisfied.
# * exposed subsets of a particular order before the hidden subset of same order
# * With fish, order (2, 3, 4) before finned (2, 3, 4) before Kraken (2, 3, 4).
# * The reason there are less techniques than there are patterns (T_... enums)
#   is that some techniques are able to resolve more than one pattern.
# * _kraken_ refers to the technique using an AIC chain as a strong or weak link.
# * ..._gl refers to the technique using group links in its chains.


Techniques = [tech_exposed_singles,
              tech_hidden_singles,
              tech_locked_singles,
              tech_exposed_pairs,
              tech_hidden_pairs,
              tech_exposed_triples,
              tech_hidden_triples,
              tech_exposed_quads,
              tech_hidden_quads,
              tech_x_wings,
              tech_swordfish,
              tech_jellyfish,
              tech_y_wings,
              tech_three_link_x_chains,  # skyscrapers, 2 string kites and turbot fish
              tech_empty_rects,
              tech_w_wings,
              tech_xyz_wings,        # not before y-wings
              tech_finned_x_wings,   # finned fish never before ordinary fish
              tech_finned_swordfish,
              tech_finned_jellyfish,
              tech_wxyz_wings,
              tech_bent_exposed_quads,
              tech_other_x_chains,  # never before three link X-Chains
              tech_even_x_loops,         # never before X-Wings
              tech_strong_x_loops,
              # tech_xy_chains,
              tech_kraken_x_wings,  # kraken fish never before finned fish
              tech_kraken_swordfish,
              tech_kraken_jellyfish,
              tech_kraken_w_wings,  # never before W-Wings.
              tech_gl_w_wings,
              tech_gl_three_link_x_chains,
              tech_gl_other_x_chains,
              tech_gl_even_x_loops,
              tech_gl_strong_x_loops,
              # tech_gl_xy_chains,
              tech_gl_kraken_x_wings,
              tech_gl_kraken_swordfish,
              tech_gl_kraken_jellyfish,
              tech_gl_kraken_w_wings,
              ]


def logic_solve_puzzle(Grid, Elims = None, Meth = T_UNDEF, Soln = None):

    # Solve the puzzle passed in grid, returning the ordered list of logic
    # solution steps.
    #
    # If the first method is not T_UNDEF and the first step cannot be solved
    # with the the specified method, then try to solve without the method
    # constraint
    #
    # Parms:
    #  Grid: In:   Contains the puzzle to grade, needs to be a valid puzzle.

    #  Steps: Out:   The ordered list of logic techniques solution path that the
    #  Cands: In Cands starting state.
    #  Meth:  Suggested starting method, will start from first technique if unsuccess.
    # Returns: The Maximum Expertise Level required to solve the puzzle

    NrEmpties = 0
    Steps = []
    G = [[Grid[r][c] for c in range(9)] for r in range(9)]
    C = [[set() for c in range(9)] for r in range(9)]
    for r in range(9):
        for c in range(9):
            if not G[r][c]:
                NrEmpties += 1
                for Cand in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    if cell_val_has_no_conflicts(Cand, G, r, c):
                        C[r][c].add(Cand)
                if Elims: C[r][c] -= Elims[r][c]

    MaxLvl = 0
    if Meth != T_UNDEF and NrEmpties > 0:
        Step = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0, P_GRID: deepcopy(G), P_CAND: deepcopy(C)}
        for tech in Techniques:
            NrSlvd = tech(G, Step, C, Method = Meth)
            if NrSlvd == -2: continue
            if NrSlvd >= 0:
                Steps.append(Step)
                if T[Step[P_TECH]][T_LVL] > MaxLvl: MaxLvl = T[Step[P_TECH]][T_LVL]
                NrEmpties -= NrSlvd
                if Soln:
                    for r in range(9):
                        for c in range(9):
                            if G[r][c] > 0:
                                if G[r][c] != Soln[r][c]:
                                    print (f"Invalid Assignment: r{r}c{c}:={Soln[r][c]}.")
                                    return UNDEF, Steps
                            else:
                                if Soln[r][c] not in C[r][c]:
                                    print (f"Invalid Elimination: r{r}c{c}-={Soln[r][c]}.")
                                    return UNDEF, Steps
            break

    while NrEmpties > 0:
        Step = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0, P_GRID: deepcopy(G), P_CAND: deepcopy(C)}
        for tech in Techniques:
            NrSlvd = tech(G, Step, C)
            if NrSlvd < 0: continue
            Steps.append(Step)
            if T[Step[P_TECH]][T_LVL] > MaxLvl: MaxLvl = T[Step[P_TECH]][T_LVL]
            NrEmpties -= NrSlvd
            if Soln:
                for r in range(9):
                    for c in range(9):
                        if G[r][c] > 0:
                            if G[r][c] != Soln[r][c]:
                                print(f"Invalid Assignment: r{r}c{c}:={Soln[r][c]}.")
                                return UNDEF, Steps
                        else:
                            if Soln[r][c] not in C[r][c]:
                                print(f"Invalid Elimination: r{r}c{c}-={Soln[r][c]}.")
                                return UNDEF, Steps
            break
        else:
            if not _tech_brute_force(G, Step, C):
                # An error occured - bug in program
                return UNDEF, Steps
            NrEmpties -= 1
            Steps.append(Step)
            MaxLvl = LVL_GURU
    return MaxLvl, Steps


def solve_next_step(Grid, Step, Elims, Method = T_UNDEF):
    # Find the solution for the next step, used in providing hints to users.
    # Hints cannot be taken from the solution list as the user more than likely
    # solved the puzzle to this point taking a different path to that of the
    # solution list, and the current puzzle state may be different to any state
    # in the solution list.  Also note that this function does not check if the
    # puzzle is correct if interactive error checking is disabled and will still
    # attempt to find a solution.
    #
    # Parms:
    #  Grid: In: The puzzle grid from which to find the next step.
    #  Step: Out: The next found step as a dict.
    #       P_TECH:  The enumeration of the logic technique, eg T_*
    #       P_DESC:  Text describing identification of logic technique
    #       P_SLVD:  list of solved cells in dict object:
    #           P_VAL:  Cell value
    #           P_ROW:  Row coord of cell
    #           P_COL:  Col coord of cell
    #       P_ELIM:  List of values a cell cannot assume - eliminated cands.
    #           P_VAL:  Candidate value to be eliminated
    #           P_ROW:  Row coord of cell where candidate is eliminated
    #           P_COL:  Col coord of cell where candidate is eliminated.
    #       P_SUBS:  Ordered list of sub-steps as a recursion of Steps.
    #  ElimCands: I/O: 9x9 array of sets containing eliminated candidates. It is
    #             necessary for the caller to maintain this structure for
    #             subsequent calls to this function to prevent the same hints
    #             being given.
    # Returns:  True:  A solution found.
    #           False: Can't solve next step - either invalid puzzle or bug in program.

    C = [[set() for c in range(9)] for r in range(9)]
    for r in range(9):
        for c in range(9):
            if not Grid[r][c]:
                for Cand in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    if cell_val_has_no_conflicts(Cand, Grid, r, c):
                        C[r][c].add(Cand)
                C[r][c] -= Elims[r][c]

    for tech in Techniques:
        if tech(Grid, Step, C, Method = Method) >= 0:
            return True

    if Method == T_UNDEF or Method == T_BRUTE_FORCE:
        return _tech_brute_force(Grid, Step, C)
    return False

def _tech_brute_force(Grid, Step, Cands):
    # first randomly pick the empty to hint on.
    r = c = 0
    for s in sample(range(81), k = 81):
        r = s//9
        c = s%9
        if not Grid[r][c]:
            break
        # least one empty cell
    G = [[Grid[r1][c1] for c1 in range(9)] for r1 in range(9)]
    if _solve_puzzle_backtrack(G):
        Step[P_TECH] = T_BRUTE_FORCE
        Grid[r][c] = G[r][c]
        Step[P_PTRN] = [[P_ROW, r], [P_COL, c], [P_OP, OP_EQ], [P_VAL, Grid[r][c]], [P_END, ]]
        Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
        Cands[r][c].clear()
        discard_cand_from_peers(Grid[r][c], r, c, Cands)
        return True
    else:
        return False

def _solve_puzzle_backtrack(Grid, Cell = 0):
    #  Recursive backtracking function to find a Sudoku puzzle. If the
    #  puzzle is not a valid sudoku either the first solution found will be
    #  in grid, or returns False if no solution found.
    #  Grid: In:  A Sudoku puzzle (can process invalid puzzles too)
    #        Recursive call:  Partially solved puzzle
    #        Out:  The solved puzzle.
    #  cell: In: Optional: - must be 0 if not called recursively
    #        Recursive call: The current cell position
    #  Returns:  True: a solution found - does not imply a valid puzzle
    #            False: no solution found - implies invalid puzzle

    #  Find the next hole in the puzzle.
    while Cell < 81:
        r = Cell//9
        c = Cell%9
        if Grid[r][c] != 0:
            Cell += 1
        else:
            break
    else:
        #        Soln[0] = [[Grid[r1][c1] for c1 in range(9)] for r1 in range(9)]
        return True  # All cells successfully filled

    for v in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        if cell_val_has_no_conflicts(v, Grid, r, c):
            Grid[r][c] = v
            if _solve_puzzle_backtrack(Grid, Cell+1):
                return True
    Grid[r][c] = 0
    return False





"""
Info in these functions may come in handy later on


def _tech_hidden_single_no_cands(Grid, Step, Cands):
    # Pencil marks (Cands array) not used in the finding of hidden singles
    r1 = c1 = 0  # Open scope of local vars r & c to whole function.
    # 1. Scan Rows
    for r in range(9):
        for Cand in range(1, 10):
            if Cand not in Grid[r]:
                Occ = 0
                for c, v in enumerate(Grid[r]):
                    if not v and cell_val_has_no_conflicts(Cand, Grid, r, c):
                        Occ += 1
                        c1 = c
                        if Occ > 1:
                            break
                if Occ == 1:  # Found a hidden single
                    Step[P_TECH] = T_HIDDEN_SINGLE
                    Step[P_VAL] = Cand
                    Step[P_ROW] = r
                    Step[P_COL] = c1
                    return True
    # 2. Scan Cols
    for c in range(9):
        for Cand in range(1, 10):
            if Cand not in [Grid[0][c], Grid[1][c], Grid[2][c],
                            Grid[3][c], Grid[4][c], Grid[5][c],
                            Grid[6][c], Grid[7][c], Grid[8][c]]:
                Occ = 0
                for r, v in enumerate([Grid[0][c], Grid[1][c], Grid[2][c],
                                       Grid[3][c], Grid[4][c], Grid[5][c],
                                       Grid[6][c], Grid[7][c], Grid[8][c]]):
                    if not v and cell_val_has_no_conflicts(Cand, Grid, r, c):
                        Occ += 1
                        r1 = r
                        if Occ > 1:
                            break
                if Occ == 1:  # Found a hidden single
                    Step[P_TECH] = T_HIDDEN_SINGLE
                    Step[P_VAL] = Cand
                    Step[P_ROW] = r1
                    Step[P_COL] = c
                    return True
    # 3. Scan Blks
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for Cand in range(1, 10):
                if Cand not in (Grid[br][bc:bc + 3]
                                + Grid[br + 1][bc:bc + 3]
                                + Grid[br + 2][bc:bc + 3]):
                    Occ = 0
                    for r in range(br, br + 3):
                        for c in range(bc, bc + 3):
                            if not Grid[r][c] and cell_val_has_no_conflicts(Cand, Grid, r, c):
                                Occ += 1
                                r1 = r
                                c1 = c
                                if Occ > 1:
                                    break
                        if Occ > 1:
                            break
                    if Occ == 1:  # Found a hidden single
                        Step[P_TECH] = T_HIDDEN_SINGLE
                        Step[P_VAL] = Cand
                        Step[P_ROW] = r1
                        Step[P_COL] = c1
                        return True
    return False  # No hidden singles found.

def _tech_exposed_single_no_cands(Grid, Step, Cands):
    # Pencil marks (Cands array) not used in the finding of hidden singles

    Cand1  = 0  # Open scope of local vars to whole function.
    # 1. Scan Rows
    for r in range(9):
        for c, v, in enumerate(Grid[r]):
            if not v:  # cell[r][c] is empty
                Occ = 0
                for Cand in range(1, 10):
                    if cell_val_has_no_conflicts(Cand, Grid, r, c):
                        Occ += 1
                        Cand1 = Cand
                        if Occ > 1:
                            break
                if Occ == 1:  # found an exposed single
                    Step[P_TECH] = T_EXPOSED_SINGLE
                    Step[P_VAL] = Cand1
                    Step[P_ROW] = r
                    Step[P_COL] = c
                    return True
    # 2. Scan Cols
    for c in range(9):
        for r, v in enumerate([Grid[0][c], Grid[1][c], Grid[2][c],
                              Grid[3][c], Grid[4][c], Grid[5][c],
                              Grid[6][c], Grid[7][c], Grid[8][c]]):
            if not v:  # Grid[r][c] is empty
                Occ = 0
                for Cand in range(1, 10):
                    if cell_val_has_no_conflicts(Cand, Grid, r, c):
                        Occ += 1
                        Cand1 = Cand
                        if Occ > 1:
                            break
                if Occ == 1:  # found an exposed single
                    Step[P_TECH] = T_EXPOSED_SINGLE
                    Step[P_VAL] = Cand1
                    Step[P_ROW] = r
                    Step[P_COL] = c
                    return True
    # 3. Scan Blks
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):

            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    if not Grid[r][c]:  # is empty
                        Occ = 0
                        for Cand in range(1, 10):
                            if cell_val_has_no_conflicts(Cand, Grid, r, c):
                                Occ += 1
                                Cand1 = Cand
                                if Occ > 1:
                                    break
                        if Occ == 1:  # found an exposed single
                            Step[P_TECH] = T_EXPOSED_SINGLE
                            Step[P_VAL] = Cand1
                            Step[P_ROW] = r
                            Step[P_COL] = c
                            return True
    return False  # No hidden singles found.

                        # for r2 in range(br, br + 3):
                            #     for c2 in range(bc, bc + 3):
                            #         if (r2 != r1 or c2 != c1) and (r2 != r or c2 != c):
                            #             for Cand in Cands[r][c]:
                            #                 if Cand in Cands[r2][c2]:
                            #                     Cands[r2][c2].discard(Cand)
                            #                     if ElimCands is not None:
                            #                         ElimCands[r2][c2].add(Cand)
                            #                     Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c2})

    # Step[P_TECH] = T_UNDEF
    # for r in range(9):
    #     for c in range(9):
    #         # Scan for cells with only 2 candidates
    #         if len(Cands[r][c]) == 2:
    #             # Do any peers have only the same two candidates?
    #             for c1 in set(range(9)) - {c}:
    #                 if Cands[r][c] == Cands[r][c1]:
    #                     # Found an exposed pair in the row. Could it perhaps
    #                     # be a locked pair too?
    #                     if (c // 3) == (c1 // 3):  # both cells in same blk
    #                         # Yes, it is a locked pair too.
    #                         br = (r // 3) * 3
    #                         bc = (c // 3) * 3
    #                         Step[P_TECH] = T_LOCKED_EXPOSED_PAIR
    #                         for r2 in range(br, br + 3):
    #                             for c2 in range(bc, bc + 3):
    #                                 if (r2 != r or c2 != c) and (r2 != r or c2 != c1):
    #                                     for Cand in Cands[r][c]:
    #                                         if Cand in Cands[r2][c2]:
    #                                             Cands[r2][c2].discard(Cand)
    #                                             if ElimCands is not None:
    #                                                 ElimCands[r2][c2].add(Cand)
    #                                             Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c2})
    #                     if Step[P_TECH] == T_UNDEF:
    #                         Step[P_TECH] = T_EXPOSED_PAIR
    #                     for c2 in range(9):
    #                         if (c2 != c1) and (c2 != c):
    #                             for Cand in Cands[r][c]:
    #                                 if Cand in Cands[r][c2]:
    #                                     Cands[r][c2].discard(Cand)
    #                                     if ElimCands is not None:
    #                                         ElimCands[r][c2].add(Cand)
    #                                     Step[P_ELIM].append({P_VAL: Cand, P_ROW: r, P_COL: c2})
    #                     if len(Step[P_ELIM]):  # Candidates were eliminated
    #                         return True
    #                     # else we continue looking because nothing changed
    #             for r1 in set(range(9)) - {r}:
    #                 if Cands[r][c] == Cands[r1][c]:
    #                     # Found an exposed pair in the col. Could it perhaps
    #                     # be a locked pair too?
    #                     if (r // 3) == (r1 // 3):  # both cells in same blk
    #                         # Yes, it is a locked pair too.
    #                         br = (r // 3) * 3
    #                         bc = (c // 3) * 3
    #                         Step[P_TECH] = T_LOCKED_EXPOSED_PAIR
    #                         for r2 in range(br, br + 3):
    #                             for c2 in range(bc, bc + 3):
    #                                 if (r2 != r or c2 != c) and (r2 != r1 or c2 != c):
    #                                     for Cand in Cands[r][c]:
    #                                         if Cand in Cands[r2][c2]:
    #                                             Cands[r2][c2].discard(Cand)
    #                                             if ElimCands is not None:
    #                                                 ElimCands[r2][c2].add(Cand)
    #                                             Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c2})
    #                     if Step[P_TECH] == T_UNDEF:
    #                         Step[P_TECH] = T_EXPOSED_PAIR
    #                     for r2 in range(9):
    #                         if (r2 != r1) and (r2 != r):
    #                             for Cand in Cands[r][c]:
    #                                 if Cand in Cands[r2][c]:
    #                                     Cands[r2][c].discard(Cand)
    #                                     if ElimCands is not None:
    #                                         ElimCands[r2][c].add(Cand)
    #                                     Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c})
    #                     if len(Step[P_ELIM]):  # Candidates were eliminated
    #                         return True
    #                     # else we continue looking, because nothing changed
    #             br = (r // 3) * 3  # scan the box.
    #             bc = (c // 3) * 3
    #             for r1 in range(br, br + 3):
    #                 for c1 in range(bc, bc + 3):
    #                     if (r1 != r) and (c1 != c):
    #                         if Cands[r][c] == Cands[r1][c1]:
    #                             # Found an exposed pair in a box, discard
    #                             # matching candidates from remaining cells in
    #                             # the box.
    #                             Step[P_TECH] = T_EXPOSED_PAIR
    #                             br1 = (r // 3) * 3  # scan the box.
    #                             bc1 = (c // 3) * 3
    #                             for r2 in range(br1, br1 + 3):
    #                                 for c2 in range(bc1, bc1 + 3):
    #                                     if (r2 != r1 or c2 != c1) and (r2 != r or c2 != c):
    #                                         for Cand in Cands[r][c]:
    #                                             if Cand in Cands[r2][c2]:
    #                                                 Cands[r2][c2].discard(Cand)
    #                                                 if ElimCands is not None:
    #                                                     ElimCands[r2][c2].add(Cand)
    #                                                 Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c2})
    #                             if len(Step[P_ELIM]):
    #                                 return True
    # return False


Original X-Wing code, incase it is needed.

    # Inspect rows first.
    for r1 in range(8):
        for Cand in sorted(Cands[r1][0] | Cands[r1][1] | Cands[r1][2] | Cands[r1][3]
                           | Cands[r1][4] | Cands[r1][5] | Cands[r1][6] | Cands[r1][7]
                           | Cands[r1][8]):
            f = 0
            c1 = c2 = -1
            for c in range(9):
                if Cand in Cands[r1][c]:
                    f += 1
                    if f == 1:
                        c1 = c
                    elif f == 2:
                        c2 = c
                    else:
                        break
            else:
                if f == 2:  # only 2 instances of candidate in r1
                    for r2 in range(r1+1, 9):
                        if Cand in Cands[r2][c1] and Cand in Cands[r2][c2]:
                            # Cand exists in corresp columns in r2, make sure
                            # that Cand does not exist in other cells in r2
                            for c in set(range(9)) - {c1, c2}:
                                if Cand in Cands[r2][c]:
                                    break  # not an x wing.
                            else:  # found an x-wing, remove cands from c1 and c2
                                for r3 in set(range(9)) - {r1, r2}:
                                    if Cand in Cands[r3][c1]:
                                        Cands[r3][c1].discard(Cand)
                                        Step[P_ELIM].append({P_VAL: Cand, P_ROW: r3, P_COL: c1})
                                        if ElimCands is not None:
                                            ElimCands[r3][c1].add(Cand)
                                    if Cand in Cands[r3][c2]:
                                        Cands[r3][c2].discard(Cand)
                                        Step[P_ELIM].append({P_VAL: Cand, P_ROW: r3, P_COL: c2})
                                        if ElimCands is not None:
                                            ElimCands[r3][c2].add(Cand)
                                if len(Step[P_ELIM]):
                                    Step[P_TECH] = T_X_WING
                                    Step[P_DESC] = f"r{r1+1:d}{r2+1:d}c{c1+1:d}{c2+1:d} == {Cand:d}."
                                    return True
    # the inspect columns
    for c1 in range(8):
        for Cand in sorted(Cands[0][c1] | Cands[1][c1] | Cands[2][c1] | Cands[3][c1]
                           | Cands[4][c1] | Cands[5][c1] | Cands[6][c1] | Cands[7][c1]
                           | Cands[8][c1]):
            f = 0
            r1 = r2 = -1
            for r in range(9):
                if Cand in Cands[r][c1]:
                    f += 1
                    if f == 1:
                        r1 = r
                    elif f == 2:
                        r2 = r
                    else:
                        break
            else:
                if f == 2:  # only two instances of Cand in c1
                    for c2 in range(c1+1, 9):
                        if Cand in Cands[r1][c2] and Cand in Cands[r2][c2]:
                            # Cand exists in corresp rows in c2, make sure
                            # that Cand does not exist in other cells in c2
                            for r in set(range(9)) - {r1, r2}:
                                if Cand in Cands[r][c2]:
                                    break  # not an x wing.
                            else:  # found an x-wing, remove cands from c1 and c2
                                for c3 in set(range(9)) - {c1, c2}:
                                    if Cand in Cands[r1][c3]:
                                        Cands[r1][c3].discard(Cand)
                                        Step[P_ELIM].append({P_VAL: Cand, P_ROW: r1, P_COL: c3})
                                        if ElimCands is not None:
                                            ElimCands[r2][c3].add(Cand)
                                    if Cand in Cands[r2][c3]:
                                        Cands[r2][c3].discard(Cand)
                                        Step[P_ELIM].append({P_VAL: Cand, P_ROW: r2, P_COL: c3})
                                        if ElimCands is not None:
                                            ElimCands[r2][c3].add(Cand)
                                if len(Step[P_ELIM]):
                                    Step[P_TECH] = T_X_WING
                                    Step[P_DESC] = f"r{r1+1:d}{r2+1:d}c{c1+1:d}{c2+1:d} == {Cand:d}."
                                    return True
    return False


"""