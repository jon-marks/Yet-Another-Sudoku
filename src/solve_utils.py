
#  Collection of common enums, structures, classes, and functions used in the solving
#  of puzzles.

#  Note many of the functions operate optimally and seamlessly on group linked ccells
#  and scalar ccells.  This is achieved by using a the flag GrpLks to indicate when
#  pattern searches using group links is required and and passing all (r, c) parameters as
#  sets.  That is when GrpLKS is set, r and c are set objects, when GrpLks is False,
#  r and c are scalars.

#  This module does not import any lower level project modules, it is a lowest level module.

from collections import namedtuple
from globals import *

# Link strength enumerations.
# LK_ERR  = 0x1000
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

# The use of weak or strong ended AIC's to search for patterns where ccell's see
# each other, for example in covers seeing fins in finned fish or W wings, etc,
# adds the dimension of incremental difficulty in finding and solving a pattern
# based on the number of links in the chains used to solve a step.

NL = namedtuple('NL', ['r', 'c', 'Cand', 'Lk'])  # Node in a chain with lk to partner
CCELL = namedtuple('CCELL', ['r', 'c', 'Cand'])

class TNODE:
    def __init__(self, r = -1, c = -1, Cand = -1, Lk = -1, Chain = None, Parent = None, Children = None):  # , Subnet = None):  #, SubnetBackRefs = None):  # Chain = None,
        self.r = r; self.c = c; self.Cand = Cand; self.Lk = Lk
        self.Chain = Chain if Chain else []  # List of path from root to current Node. (NODE(r, c, Cand, Lk_type_to_next)
        self.Parent = Parent
        self.Children = Children if Children else []

class ANODE:
    def __init__(self, Hash = -1, Lk = LK_NONE, DeadEnd = False, Children = None):
        self.Hash = Hash
        self.Lk = Lk
        self.Children = Children if Children else []

class STATE:
    def __init__(self, SLNodes = None, Tech = T_UNDEF, Pattern = None, Pattern1 = None, Elims = None, Plcmts = None):
        self.SLNodes = SLNodes if SLNodes else []
        self.Tech = Tech
        self.Pattern = Pattern if Pattern else []
        self.Pattern1 = Pattern1 if Pattern1 else []
        self.Elims = Elims if Elims else {}
        self.Plcmts = Plcmts if Plcmts else []

def cell_val_has_no_conflicts(v, grid, r, c):
    #  Checks that value v obeys sudoku rules in grid[r][c], the 9x9 matrix
    #  v:     IN:  value to test in the grid
    #  grid:  IN:  grid to test value
    #  r, c   IN:  row and column in grid for test.
    # Check that val not in row
    if not (v in grid[r]):
        # Check that not in col
        if not (v in [grid[0][c], grid[1][c], grid[2][c],
                      grid[3][c], grid[4][c], grid[5][c],
                      grid[6][c], grid[7][c], grid[8][c]]):
            # Check that not in block/box
            br = (r//3)*3
            bc = (c//3)*3
            if not (v in (grid[br][bc:bc+3]
                          +grid[br+1][bc:bc+3]
                          +grid[br+2][bc:bc+3])):
                return True
    return False

def cell_val_has_conflicts(grid, r, c, val = 0):
    # if val != 0 then grid[r][c] is zero, else caller made a mistake.
    # and unpredictable results.
    #  Checks that value v obeys sudoku rules in grid[r][c], the 9x9 matrix

    if val == grid[r][c] == 0: return False  # empty cell cannot be conflicted.

    if val: v = val
    else: v = grid[r][c]; grid[r][c] = 0

    if not (v in grid[r]):
        # Check that not in col
        if not (v in [grid[0][c], grid[1][c], grid[2][c],
                      grid[3][c], grid[4][c], grid[5][c],
                      grid[6][c], grid[7][c], grid[8][c]]):
            # Check that not in block/box
            br = (r//3)*3
            bc = (c//3)*3
            if not (v in (grid[br][bc:bc+3]
                          +grid[br+1][bc:bc+3]
                          +grid[br+2][bc:bc+3])):
                if not val: grid[r][c] = v
                return False
    if not val: grid[r][c] = v
    return True

def determine_cands(Grid, Elims = None):
    # Returns 9x9 matrix of of non-conflicted candidates less the Elims.
    # non conflicted cands found by scanning grid.
    # Can also be used to determine Elims by passing puzzle being solved cands in place of elims.
    NrEmpties = 0
    Cands = [[set() for c in range(9)] for r in range(9)]
    for r in range(9):
        for c in range(9):
            if not Grid[r][c]:
                NrEmpties += 1
                Cands0 = set(range(1, 10))
                if Elims:  Cands0 -= Elims[r][c]
                for Cand in Cands0:
                    if cell_val_has_no_conflicts(Cand, Grid, r, c):
                        Cands[r][c].add(Cand)
    return NrEmpties, Cands

def token_link(Lk):
    if Lk == LK_WEAK: return OP_WLK
    if Lk == LK_STRG or Lk == LK_STWK: return OP_SLK
    if Lk == LK_WKST: return OP_WSLK
    if Lk == LK_NONE: return OP_NONE
    return -1

def discard_cand_from_peers(Cand, r, c, Cands):
    for i in range(9):
        Cands[i][c].discard(Cand)
        Cands[r][i].discard(Cand)
    br = (r//3)*3; bc = (c//3)*3
    for r1 in range(br, br+3):
        for c1 in range(bc, bc+3):
            Cands[r1][c1].discard(Cand)

def list_ccells_linked_to(r, c, Cand, Cands, Type = LK_STWK, GrpLks = False, InclCell = True):
    # Returns a list of (r, c, Cand, LkType, LkHouse) tuples that the ccell(r, c, Cand) can see.
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
            for c1 in range(9):
                if c1 in c: continue  # sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - c):
                if Cand in Cands[r0][c1]:
                    C1.add(c1)
                    Twr[c1//3].add(c1)
            if len(C1) == 1:
                LCL.append((r, C1, Cand, LK_STWK | LK_ROW))
            elif Type & LK_WEAK:
                for c1 in sorted(C1):
                    LCL.append((r, {c1}, Cand, LK_WEAK | LK_ROW))
            lenTwr0 = len(Twr[0]); lenTwr1 = len(Twr[1]); lenTwr2 = len(Twr[2])
            if ct == 0:
                if lenTwr0 == 0:
                    if lenTwr1 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK | LK_ROW))
                    elif lenTwr1 > 1 and lenTwr2 == 0: LCL.append((r, Twr[1], Cand, LK_STWK | LK_ROW))
                elif Type & LK_WEAK and lenTwr1 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[1], Cand, LK_WEAK | LK_ROW), (r, Twr[2], Cand, LK_WEAK | LK_ROW)])
            if ct == 1:
                if lenTwr1 == 0:
                    if lenTwr0 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK | LK_ROW))
                    elif lenTwr0 > 1 and lenTwr2 == 0: LCL.append((r, Twr[0], Cand, LK_STWK | LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK | LK_ROW), (r, Twr[2], Cand, LK_WEAK | LK_ROW)])
            if ct == 2:
                if lenTwr2 == 0:
                    if lenTwr0 == 0 and lenTwr1 > 1: LCL.append((r, Twr[1], Cand, LK_STWK | LK_ROW))
                    elif lenTwr0 > 1 and lenTwr1 == 0: LCL.append((r, Twr[0], Cand, LK_STWK | LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr1 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK | LK_ROW), (r, Twr[1], Cand, LK_WEAK | LK_ROW)])
        if len(c) == 1:  # scan the col
            c0 = list(c)[0]
            rf = list(r)[0]//3
            R1 = set()
            Flr = [set(), set(), set()]
            for r1 in range(9):  # sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - r):
                if r1 in r: continue
                if Cand in Cands[r1][c0]:
                    R1.add(r1)
                    Flr[r1//3].add(r1)
            if len(R1) == 1:
                LCL.append((R1, c, Cand, LK_STWK | LK_COL))
            elif Type & LK_WEAK:
                for r1 in sorted(R1):
                    LCL.append(({r1}, c, Cand, LK_WEAK | LK_COL))
            lenFlr0 = len(Flr[0]); lenFlr1 = len(Flr[1]); lenFlr2 = len(Flr[2])
            if rf == 0:
                if lenFlr0 == 0:
                    if lenFlr1 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK | LK_COL))
                    elif lenFlr1 > 1 and lenFlr2 == 0: LCL.append((Flr[1], c, Cand, LK_STWK | LK_COL))
                elif Type & LK_WEAK and lenFlr1 > 1 and lenFlr2 > 1: LCL.extend([(Flr[1], c, Cand, LK_WEAK | LK_COL), (Flr[2], c, Cand, LK_WEAK | LK_COL)])
            if rf == 1:
                if lenFlr1 == 0:
                    if lenFlr0 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK | LK_COL))
                    elif lenFlr0 > 1 and lenFlr2 == 0: LCL.append((Flr[0], c, Cand, LK_STWK | LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr2 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK | LK_COL), (Flr[2], c, Cand, LK_WEAK | LK_COL)])
            if rf == 2:
                if lenFlr2 == 0:
                    if lenFlr0 == 0 and lenFlr1 > 1: LCL.append((Flr[1], c, Cand, LK_STWK | LK_COL))
                    elif lenFlr0 > 1 and lenFlr1 == 0: LCL.append((Flr[0], c, Cand, LK_STWK | LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr1 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK | LK_COL), (Flr[1], c, Cand, LK_WEAK | LK_COL)])
        # scan the box.  (Grouped) Node is always contained in a box
        rb = (list(r)[0]//3)*3; cb = (list(c)[0]//3)*3  # ; rb1 = rb+1; rb2 = rb+2; cb1 = cb+1; cb2 = cb+2
        B1 = []; RB = [set(), set(), set()]; CB = [set(), set(), set()]
        Lks = []
        lr = len(r); lc = len(c)
        if lr == lc == 1:
            rx = list(r)[0]; ix = rx - rb; cx = list(c)[0]; jx = cx - cb
            i0 = (ix + 1) % 3; i1 = (ix + 2) % 3; j0 = (jx + 1) % 3; j1 = (jx + 2) % 3
            r0 = i0 + rb; r1 = i1 + rb; c0 = j0 + cb; c1 = j1 + cb
            # rows in the box.
            Grp = set()
            if Cand in Cands[r0][cx]: Grp.add(cx)
            if Cand in Cands[r0][c0]: Grp.add(c0); Lks.append(({r0}, {c0}))
            if Cand in Cands[r0][c1]: Grp.add(c1); Lks.append(({r0}, {c1}))
            if len(Grp) > 1: Lks.append(({r0}, Grp))
            Grp = set()
            if Cand in Cands[r1][cx]: Grp.add(cx)
            if Cand in Cands[r1][c0]: Grp.add(c0); Lks.append(({r1}, {c0}))
            if Cand in Cands[r1][c1]: Grp.add(c1); Lks.append(({r1}, {c1}))
            if len(Grp) > 1: Lks.append(({r1}, Grp))
            # cols in the box.
            Grp = set()
            if Cand in Cands[rx][c0]: Grp.add(rx)
            if Cand in Cands[r0][c0]: Grp.add(r0)
            if Cand in Cands[r1][c0]: Grp.add(r1)
            if len(Grp) > 1: Lks.append((Grp, {c0}))
            Grp = set()
            if Cand in Cands[rx][c1]: Grp.add(rx)
            if Cand in Cands[r0][c1]: Grp.add(r0)
            if Cand in Cands[r1][c1]: Grp.add(r1)
            if len(Grp) > 1: Lks.append((Grp, {c1}))
        elif lr == 1:
            ix = list(r)[0]; i0 = (ix + 1) % 3; i1 = (ix + 2) % 3
            r0 = i0 + rb; r1 = i1 + rb
            Grp = set()
            if Cand in Cands[r0][cb]: Grp.add(cb); Lks.append(({r0}, {cb}))
            if Cand in Cands[r0][cb+1]: Grp.add(cb+1); Lks.append(({r0}, {cb+1}))
            if Cand in Cands[r0][cb+2]: Grp.add(cb+2); Lks.append(({r0}, {cb+2}))
            if len(Grp) > 1: Lks.append(({r0}, Grp))
            Grp = set()
            if Cand in Cands[r1][cb]: Grp.add(cb); Lks.append(({r1}, {cb}))
            if Cand in Cands[r1][cb+1]: Grp.add(cb+1); Lks.append(({r1}, {cb+1}))
            if Cand in Cands[r1][cb+2]: Grp.add(cb+2); Lks.append(({r1}, {cb+2}))
            if len(Grp) > 1: Lks.append(({r1}, Grp))
        elif lc == 1:
            jx = list(c)[0] - cb; j0 = (jx + 1) % 3; j1 = (jx + 2) % 3
            c0 = j0 + cb; c1 = j1 + cb
            Grp = set()
            if Cand in Cands[rb][c0]: Grp.add(rb); Lks.append(({rb}, {c0}))
            if Cand in Cands[rb+1][c0]: Grp.add(rb+1); Lks.append(({rb+1}, {c0}))
            if Cand in Cands[rb+2][c0]: Grp.add(rb+2); Lks.append(({rb+2}, {c0}))
            if len(Grp) > 1: Lks.append((Grp, {c0}))
            Grp = set()
            if Cand in Cands[rb][c1]: Grp.add(rb); Lks.append(({rb}, {c1}))
            if Cand in Cands[rb+1][c1]: Grp.add(rb+1); Lks.append(({rb+1}, {c1}))
            if Cand in Cands[rb+2][c1]: Grp.add(rb+2); Lks.append(({rb+2}, {c1}))
            if len(Grp) > 1: Lks.append((Grp, {c1}))

        for r0, c0 in sorted(Lks):
            for b in range(9):
                r1 = rb + b//3; c1 = cb + b%3
                if ccells_intersect({r1}, {c1}, Cand, r, c, Cand, GrpLks) or ccells_intersect({r1}, {c1}, Cand, r0, c0, Cand, GrpLks): continue
                Lk = LK_WEAK; break
            else:
                Lk = LK_STWK
            if Type == LK_STRG:
                if Lk == LK_STWK: LCL.append((r0, c0, Cand, LK_STWK))
            else: LCL.append((r0, c0, Cand, Lk | LK_BOX))
        # Scan the cell.
        if InclCell and len(r) == len(c) == 1:
            if len(Cands[list(r)[0]][list(c)[0]]) == 2: LCL.append((r, c, list(Cands[list(r)[0]][list(c)[0]]-{Cand})[0], LK_STWK | LK_CELL))
            elif Type != LK_STRG:
                for Cand0 in sorted(Cands[list(r)[0]][list(c)[0]]-{Cand}):
                    LCL.append((r, c, Cand0, LK_WEAK | LK_CELL))

    else:  # no GrpLks
        # Scan the row.
        n = 0; L = []
        # Lk = LK_NONE
        for c0 in range(9):
            if c == c0 or Cand not in Cands[r][c0]: continue
            n += 1
            if n > 1 and Type == LK_STRG: n = 0; break
            L.append(c0)
        if n:
            Lk = LK_STRG if n == 1 else LK_WEAK
            for c0 in L: LCL.append((r, c0, Cand, Lk | LK_ROW))
        # Scan the col.
        n = 0; L = []
        for r0 in range(9):
            if r == r0 or Cand not in Cands[r0][c]: continue
            n += 1
            if n > 1 and Type == LK_STRG: n = 0; break
            L.append(r0)
        if n:
            Lk = LK_STRG if n == 1 else LK_WEAK
            for r0 in L: LCL.append((r0, c, Cand, Lk | LK_COL))
        # Scan the box.
        br = (r//3)*3; bc = (c//3)*3
        n = m = 0; L = []  # m counts all cands in box to deterimine strong or weak link.  n counts on only cands not overlapping with lines.
        for h in range(9):
            r0 = br+h//3; c0 = bc+h%3
            if (r0 == r and c0 == c) or not (Cand in Cands[r0][c0]): continue
            if m > 0 and Type == LK_STRG: n = 0; break
            m += 1
            if r0 != r and c0 != c: L.append((r0, c0)); n += 1
        else:
            # if n:
            Lk = LK_STRG if m == 1 else LK_WEAK
            for r0, c0 in L: LCL.append((r0, c0, Cand, Lk | LK_BOX))
        # Scan the cell.
        if InclCell:
            if len(Cands[r][c]) == 2: LCL.append((r, c, list(Cands[r][c]-{Cand})[0], LK_STWK | LK_CELL))
            elif Type != LK_STRG:
                for Cand0 in sorted(Cands[r][c]-{Cand}):
                    LCL.append((r, c, Cand0, LK_WEAK | LK_CELL))
    return LCL

def list_bv_cells_linked_to(r, c, Cand, Cands):

    LCL = []
    # scan row
    L = []; n = 0
    for c0 in range(9):
        if c != c0 and Cand in Cands[r][c0]:
            n += 1
            if len(Cands[r][c0]) == 2: L.append((c0, [Cand, list(Cands[r][c0] ^ {Cand})[0]]))
    Lk0 = (LK_WEAK if n > 1 else LK_WKST) | LK_ROW
    for c0, Candsl0 in L: LCL.append((r, c0, Candsl0, Lk0))
    # scan col
    L = []; n = 0
    for r0 in range(9):
        if r != r0 and Cand in Cands[r0][c]:
            n += 1
            if len(Cands[r0][c]) == 2: L.append((r0, [Cand, list(Cands[r0][c] ^ {Cand})[0]]))
    Lk0 = (LK_WEAK if n > 1 else LK_WKST) | LK_COL
    for r0, Candsl0 in L: LCL.append((r0, c, Candsl0, Lk0))
    # scan box.
    L = []; n = 0
    rb = (r//3)*3; cb = (c//3)*3
    for b0 in range(9):
        r0 = rb + b0//3; c0 = cb + b0%3
        if Cand in Cands[r0][c0]:
            if r != r0 and c != c0: n += 1
            if (r != r0 or c != c0) and len(Cands[r0][c0]) == 2: L.append((r0, c0, [Cand, list(Cands[r0][c0] ^ {Cand})[0]]))
        # if not(r == r0 or c == c0) and len(Cands[r0][c0]) == 2 and Cand in Cands[r0][c0]: L.append((r0, c0, [Cand, list(Cands[r0][c0] ^ {Cand})[0]]))
        # if not(r == r0 and c == c0) and Cand in Cands[r0][c0]: n += 1
    Lk0 = (LK_WEAK if n > 1 else LK_WKST) | LK_BOX
    #     if r == r0 or c == c0 or len(Cands[r0][c0]) != 2 or Cand not in Cands[r0][c0]: continue
    #     L.append((r0, c0, [Cand, list(Cands[r0][c0] ^ {Cand})[0]]))
    # Lk0 = Lk0 = (LK_WEAK if len(L) > 1 else LK_WKST) | LK_BOX
    for r0, c0, Candsl0 in L: LCL.append((r0, c0, Candsl0, Lk0))
    return LCL

def link_elims(r0, c0, Cand0, r1, c1, Cand1, Cands, GrpLks = False):

    Elims = []
    if GrpLks:
        if Cand0 == Cand1:
            if len(r0) == len(r1) == 1 and r0 == r1:  # house is a row
                r = list(r0)[0]
                for c in range(9):
                    if c in c0 | c1: continue
                    if Cand0 in Cands[r][c]: Elims.append((r, c, Cand0))
            if len(c0) == len(c1) == 1 and c0 == c1:  # house is a col
                c = list(c0)[0]
                for r in range(9):
                    if r in r0 | r1: continue
                    if Cand0 in Cands[r][c]: Elims.append((r, c, Cand0))
            rb0 = list(r0)[0]//3; cb0 = list(c0)[0]//3; rb1 = list(r1)[0]//3; cb1 = list(c1)[0]//3
            if rb0 == rb1 and cb0 == cb1:  # house is box.
                rb = rb0 * 3; cb = cb0 * 3
                for b in range(9):
                    r = rb + b//3; c = cb + b%3
                    if (r in r0 and c in c0) or (r in r1 and c in c1): continue
                    if Cand0 in Cands[r][c] and not (r, c, Cand0) in Elims: Elims.append((r, c, Cand0))
        elif r0 == r1 and c0 == c1 and len(r0) == len(c0) == 1:  # different candidates in the same cell
            Candsx = Cands[list(r0)[0]][list(c0)[0]] - {Cand0, Cand1}
            for Cand in Candsx: Elims.append((list(r0)[0], list(c0)[0], Cand))
    else:  # not GrpLks:
        if Cand0 == Cand1:
            if r0 == r1:  # house is a row
                for c in range(9):
                    if c == c0 or c == c1: continue
                    if Cand0 in Cands[r0][c]: Elims.append((r0, c, Cand0))
            if c0 == c1:  # house is a col
                for r in range(9):
                    if r == r0 or r == r1: continue
                    if Cand0 in Cands[r][c0]: Elims.append((r, c0, Cand0))
            rb0 = r0//3; cb0 = c0//3; rb1 = r1//3; cb1 = c1//3
            if rb0 == rb1 and cb0 == cb1:  # house is a box
                rb = rb0 * 3; cb = cb0 * 3
                for b in range(9):
                    r = rb + b//3; c = cb + b%3
                    if (r, c) == (r0, c0) or (r, c) == (r1, c1): continue
                    if Cand0 in Cands[r][c] and not (r, c, Cand0) in Elims: Elims.append((r, c, Cand0))
        elif r0 == r1 and c0 == c1:  # different candidates in the same cell
            Candsx = Cands[r0][c0] - {Cand0, Cand1}
            for Cand in Candsx: Elims.append((r0, c0, Cand))
    return Elims

def cells_in_same_house(r1, c1, r2, c2, GrpLks = False):
    # Cells see each other in same house
    if GrpLks: return r1 == r2 or c1 == c2 or (list(r1)[0]//3 == list(r2)[0]//3 and list(c1)[0]//3 == list(c2)[0]//3)
    else: return r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3)

def cells_that_see_all_of(Cells, GrpLks = False):
    # Cells = list of two or more (r,c) tuples.  Returns another list of (r, c) tuples that
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
    # if not group links: return True if ccells match, else False.
    # for group links, if the cells intersect each other return True, else Fasle

    if GrpLks:
        return bool(len(r0 & r1) and len(c0 & c1)) and Cand0 == Cand1
    else:
        return r0 == r1 and c0 == c1 and Cand0 == Cand1

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
        if len(r0 & r1) and len(c0 & c1) and Cand0 == Cand1: return LK_NONE  # ccells intersect
        lenr0 = len(r0); lenc0 = len(c0); lenr1 = len(r1); lenc1 = len(c1)
        r00 = list(r0)[0]; c00 = list(c0)[0]; r10 = list(r1)[0]; c10 = list(c1)[0]
        if lenr0 == lenr1 == lenc0 == lenc1 == 1:  # no grouped ccells
            if not (r0 ^ r1 or c0 ^ c1):  # same cell.
                if Cand0 == Cand1: return LK_NONE  # cells cannot link on themselves
                if len(Cands[r00][c00]) == 2: return LK_STWK | LK_CELL
                else: return LK_WEAK | LK_CELL
        # different cells, grouped or ungrouped
        if Cand0 != Cand1: return LK_NONE
        if lenr0 == lenr1 == 1 and r00 == r10:  # house is a row
            cc = set()
            for c in c0 | c1: cc.add(c//3)
            Lk = LK_BOX if len(cc) == 1 else LK_NONE
            for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (c0 | c1):
                if Cand0 in Cands[r00][c]: return LK_WEAK | LK_ROW | Lk
            return LK_STRG | LK_ROW | Lk
        if lenc0 == lenc1 == 1 and c00 == c10:  # house is a column
            rr = set()
            for r in r0 | r1: rr.add(r//3)
            Lk = LK_BOX if len(rr) == 1 else LK_NONE
            for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (r0 | r1):
                if Cand0 in Cands[r][c00]: return LK_WEAK | LK_COL | Lk
            return LK_STRG | LK_COL | Lk
        F = set(); T = set()
        for r in r0 | r1: F.add(r//3)
        for c in c0 | c1: T.add(c//3)
        if len(F) == len(T) == 1:  # house is a box.
            rb0 = list(F)[0]; cb0 = list(T)[0]
            for b0 in range(9):
                rb = rb0 + b0//3; cb = cb0 + b0%3
                if (rb in r0 | r1) and (cb in c0 | c1): continue
                if Cand0 in Cands[rb][cb]: return LK_WEAK | LK_BOX
            return LK_STWK | LK_BOX
        return LK_NONE
    else:
        if r0 == r1 and c0 == c1:
            if Cand0 == Cand1: return LK_NONE  # ccells cannot link on themselves
            if len(Cands[r0][c0]) == 2: return LK_STWK | LK_CELL
            return LK_WEAK | LK_CELL
        # different cells, therefore linked by same candidate
        if Cand0 != Cand1: return LK_NONE
        if r0 == r1:  # house is a row
            LkHse = LK_ROW
            if c0//3 == c1//3: LkHse |= LK_BOX
            for c in range(9):
                if c == c0 or c == c1: continue
            # for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {c0, c1}:
                if Cand0 in Cands[r0][c]: return LK_WEAK | LkHse
            return LK_STWK | LkHse
        if c0 == c1:  # house is a column
            LkHse = LK_COL
            if r0//3 == r1//3: LkHse |= LK_BOX
            for r in range(9):
                if r == r0 or r == r1: continue
            # for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {r0, r1}:
                if Cand0 in Cands[r][c0]: return LK_WEAK | LkHse
            return LK_STWK | LkHse
        rb0 = r0//3; cb0 = c0//3; rb1 = r1//3; cb1 = c1//3
        if rb0 == rb1 and cb0 == cb1:  # house is a box
            rb0 *= 3; cb0 *= 3
            for b0 in range(9):
                rb = rb0 + b0//3; cb = cb0 + b0%3
                if (rb, cb) in {(r0, c0), (r1, c1)}: continue
                if Cand0 in Cands[rb][cb]: return LK_WEAK | LK_BOX
            return LK_STWK | LK_BOX
        return LK_NONE

def ccells_see_each_other(r0, c0, Cand0, r1, c1, Cand1, GrpLks = False):
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
    #     +  weakly if other candidate values exist in that cell.
    # Note that a strong link can masquerade as a weak link, but a weak link
    # cannot masquerade as a strong link.

    if GrpLks:
        if len(r0 & r1) and len(c0 & c1) and Cand0 == Cand1: return False  # ccells intersect
        lenr0 = len(r0); lenc0 = len(c0); lenr1 = len(r1); lenc1 = len(c1)
        r00 = list(r0)[0]; c00 = list(c0)[0]; r10 = list(r1)[0]; c10 = list(c1)[0]
        if lenr0 == lenr1 == lenc0 == lenc1 == 1:  # no grouped ccells
            if not (r0 ^ r1 or c0 ^ c1):  # same cell.
                if Cand0 == Cand1: return False
                else: return True
        # different cells, grouped or ungrouped
        if Cand0 != Cand1: return False
        if lenr0 == lenr1 == 1 and r00 == r10: return True  # house is a row
        if lenc0 == lenc1 == 1 and c00 == c10: return True  # house is a column
        F = set(); T = set()
        for r in r0 | r1: F.add(r//3)
        for c in c0 | c1: T.add(c//3)
        if len(F) == len(T) == 1: return True  # house is a box.
    else:
        if r0 == r1 and c0 == c1:
            if Cand0 == Cand1: return False  # ccells cannot link on themselves
            else: return True
        # different cells, therefore linked by same candidate
        if Cand0 != Cand1: return False
        if r0 == r1: return True  # house is a row
        if c0 == c1: return True  # house is a column
        rb0 = r0//3; cb0 = c0//3; rb1 = r1//3; cb1 = c1//3
        if rb0 == rb1 and cb0 == cb1: return True  # house is a box
    return False

def list_all_cand_strong_links(Cand, Cands, GrpLks = False, InclCell = True):
    # Finds all the strong links for a candidate and enters makes two entries
    # in the list for same cand links in house, one from each side.  Returns
    # a list of (r, c, Cand) tuples not CCELLS as tuples are compared literally
    # but comparision of classes will compare the pointers to the instance and
    # not the contents of the class.

    Lks1 = []
    if GrpLks:
        Lks = []
        # look in rows
        for r in range(9):
            C = []; Twr = [set(), set(), set()]
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c); Twr[c//3].add(c)
            if len(C) == 2:  # and (((r, C[0]), (r, C[1])) not in Lks and ((r, C[1]), (r, C[0])) not in Lks):
                Lks.extend([((r, C[0], Cand, LK_NONE), (r, C[1], Cand, LK_STRG | LK_ROW)), ((r, C[1], Cand, LK_NONE), (r, C[0], Cand, LK_STRG | LK_ROW))])
            else:
                if Twr[0] and Twr[1] and Twr[2]: continue
                if Twr[0] and Twr[1]:   Lks.extend([((r, Twr[0], Cand, LK_NONE), (r, Twr[1], Cand, LK_STRG | LK_ROW)), ((r, Twr[1], Cand, LK_NONE), (r, Twr[0], Cand, LK_STRG | LK_ROW))])
                elif Twr[0] and Twr[2]: Lks.extend([((r, Twr[0], Cand, LK_NONE), (r, Twr[2], Cand, LK_STRG | LK_ROW)), ((r, Twr[2], Cand, LK_NONE), (r, Twr[0], Cand, LK_STRG | LK_ROW))])
                elif Twr[1] and Twr[2]: Lks.extend([((r, Twr[1], Cand, LK_NONE), (r, Twr[2], Cand, LK_STRG | LK_ROW)), ((r, Twr[2], Cand, LK_NONE), (r, Twr[1], Cand, LK_STRG | LK_ROW))])
        # look in cols
        for c in range(9):
            R = []; Flr = [set(), set(), set()]
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r); Flr[r//3].add(r)
            if len(R) == 2 and (((R[0], c), (R[1], c)) not in Lks and ((R[1], c), (R[0], c)) not in Lks):
                Lks.extend([((R[0], c, Cand, LK_NONE), (R[1], c, Cand, LK_STRG | LK_COL)), ((R[1], c, Cand, LK_NONE), (R[0], c, Cand, LK_STRG | LK_COL))])
            else:
                if Flr[0] and Flr[1] and Flr[2]: continue
                if Flr[0] and Flr[1]:   Lks.extend([((Flr[0], c, Cand, LK_NONE), (Flr[1], c, Cand, LK_STRG | LK_COL)), ((Flr[1], c, Cand, LK_NONE), (Flr[0], c, Cand, LK_STRG | LK_COL))])
                elif Flr[0] and Flr[2]: Lks.extend([((Flr[0], c, Cand, LK_NONE), (Flr[2], c, Cand, LK_STRG | LK_COL)), ((Flr[2], c, Cand, LK_NONE), (Flr[0], c, Cand, LK_STRG | LK_COL))])
                elif Flr[1] and Flr[2]: Lks.extend([((Flr[1], c, Cand, LK_NONE), (Flr[2], c, Cand, LK_STRG | LK_COL)), ((Flr[2], c, Cand, LK_NONE), (Flr[1], c, Cand, LK_STRG | LK_COL))])
        # #look in boxes
        for br, bc in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
            # Compute box params
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
            RP = sorted([lenRB0, lenRB1, lenRB2]); CP = sorted([lenCB0, lenCB1, lenCB2])
            # 1 Check for 2 two scalars in box.
            if RP == CP == [0, 1, 1]:
                # |*  |   |  *| Family
                # |  +|   |   |
                # |   |   | + |
                if lenRB0 > 0 and lenRB1 > 0 and lenRB2 == 0:   Lks.extend([((br, RB[0], Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX)), ((br1, RB[1], Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                elif lenRB0 > 0 and lenRB1 == 0 and lenRB2 > 0: Lks.extend([((br, RB[0], Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, RB[2], Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                elif lenRB0 == 0 and lenRB1 > 0 and lenRB2 > 0: Lks.extend([((br1, RB[1], Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, RB[2], Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
            else:
            # 2.  Check out Row/Row Patterns: RP == [0, n, m] where n and m are 1, 2, or 3
            # |   |   |   |   |   |   |   |   |   |   |   | Family
            # |*  |   |  *|   |  *|   | **|   | **|   |* *|
            # | ++|   | ++|   |+++|   |++ |   |+++|   |+++|
                if lenRB0 > 0 and lenRB1 > 0 and lenRB2 == 0:   Lks.extend([((br, RB[0], Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX)), ((br1, RB[1], Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                elif lenRB0 > 0 and lenRB1 == 0 and lenRB2 > 0: Lks.extend([((br, RB[0], Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, RB[2], Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                elif lenRB0 == 0 and lenRB1 > 0 and lenRB2 > 0: Lks.extend([((br1, RB[1], Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, RB[2], Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
            # 3. Check out Col/Col patterns  CP == [0, n, m] where n and m are 1, 2, or 3
            # Above rotated by 90degs
                if lenCB0 > 0 and lenCB1 > 0 and lenCB2 == 0:   Lks.extend([((CB[0], bc, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX))])
                elif lenCB0 > 0 and lenCB1 == 0 and lenCB2 > 0: Lks.extend([((CB[0], bc, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX))])
                elif lenCB0 == 0 and lenCB1 > 0 and lenCB2 > 0: Lks.extend([((CB[1], bc1, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX))])
            # 4.  Check out Row/Col Patterns - not mutually exclusive with Row/Row or Col/Col patterns
            if RP == CP == [1, 1, 2]:
                # |** |   |* *| Family
                # |  +|   | + |
                # |  +|   | + |
                # filter out invalid [1,1,2] patterns eg /**./ /..*/ /.*./, ie all cands must be covered by a row and a col only.
                # an invalid pattern is when a cand is not part of a row or a col, ie it is the only candidate in the row and the col.
                for k in [0, 1, 2]:
                    if len(RB[k]) == 1 and len(CB[list(RB[k])[0]%3]) == 1: break
                else:
                    if lenRB0 == 2:
                        if lenCB0 == 2:   Lks.extend([((br, RB[0], Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                        elif lenCB1 == 2: Lks.extend([((br, RB[0], Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                        elif lenCB2 == 2: Lks.extend([((br, RB[0], Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                    elif lenRB1 == 2:
                        if lenCB0 == 2:   Lks.extend([((br1, RB[1], Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                        elif lenCB1 == 2: Lks.extend([((br1, RB[1], Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                        elif lenCB2 == 2: Lks.extend([((br1, RB[1], Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                    elif lenRB2 == 2:
                        if lenCB0 == 2:   Lks.extend([((br2, RB[2], Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
                        elif lenCB1 == 2: Lks.extend([((br2, RB[2], Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
                        elif lenCB2 == 2: Lks.extend([((br2, RB[2], Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
            elif RP == [0, 1, 3] and CP == [1, 1, 2]:
                # |   |  |  +| Family
                # |  +|  |   |
                # |**+|  |**+|
                if lenRB0 == 3:  # and lenRB1 == 1:
                    if lenCB0 == 2:   Lks.extend([((br, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br, {bc1, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 2: Lks.extend([((br, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br, {bc, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 2: Lks.extend([((br, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br, {bc, bc1}, Cand, LK_STRG | LK_BOX))])
                elif lenRB1 == 3:
                    if lenCB0 == 2:   Lks.extend([((br1, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br1, {bc1, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 2: Lks.extend([((br1, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br1, {bc, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 2: Lks.extend([((br1, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br1, {bc, bc1}, Cand, LK_STRG | LK_BOX))])
                elif lenRB2 == 3:
                    if lenCB0 == 2:   Lks.extend([((br2, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX)), ((CB[0], bc, Cand, LK_NONE), (br2, {bc1, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 2: Lks.extend([((br2, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br2, {bc, bc2}, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 2: Lks.extend([((br2, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br2, {bc, bc1}, Cand, LK_STRG | LK_BOX))])
            elif RP == [1, 1, 2] and CP == [0, 1, 3]:
                # above patterns rotated by 90degs
                if lenCB0 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
                elif lenCB1 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc1, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc1, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc1, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc1, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc1, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc1, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
                elif lenCB2 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc2, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc2, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc2, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc2, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc2, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc2, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX))])
            elif RP == CP == [1, 1, 3]:
                # |  +|  |  +| Family
                # |  +|  |  +|
                # |**+|  |***|
                if lenRB0 == 3:
                    if lenCB0 == 3:   Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc, Cand, LK_STRG | LK_BOX)),  ((CB[0], bc, Cand, LK_NONE), (br, {bc1, bc2}, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX)),  ((br, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 3: Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br, {bc, bc2}, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc1, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX)), ((br, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 3: Lks.extend([((br, RB[0], Cand, LK_NONE), ({br1, br2}, bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br, {bc, bc1}, Cand, LK_STRG | LK_BOX)), (({br1, br2}, bc2, Cand, LK_NONE), (br, RB[0], Cand, LK_STRG | LK_BOX)), ((br, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX))])
                elif lenRB1 == 3:
                    if lenCB0 == 3:   Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc, Cand, LK_STRG | LK_BOX)),  ((CB[0], bc, Cand, LK_NONE), (br1, {bc1, bc2}, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX)),  ((br1, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 3: Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br1, {bc, bc2}, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc1, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX)), ((br1, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 3: Lks.extend([((br1, RB[1], Cand, LK_NONE), ({br, br2}, bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br1, {bc, bc1}, Cand, LK_STRG | LK_BOX)), (({br, br2}, bc2, Cand, LK_NONE), (br1, RB[1], Cand, LK_STRG | LK_BOX)), ((br1, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX))])
                elif lenRB2 == 3:
                    if lenCB0 == 3:   Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc, Cand, LK_STRG | LK_BOX)),  ((CB[0], bc, Cand, LK_NONE), (br2, {bc1, bc2}, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)),  ((br2, {bc1, bc2}, Cand, LK_NONE), (CB[0], bc, Cand, LK_STRG | LK_BOX))])
                    elif lenCB1 == 3: Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc1, Cand, LK_STRG | LK_BOX)), ((CB[1], bc1, Cand, LK_NONE), (br2, {bc, bc2}, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc1, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, {bc, bc2}, Cand, LK_NONE), (CB[1], bc1, Cand, LK_STRG | LK_BOX))])
                    elif lenCB2 == 3: Lks.extend([((br2, RB[2], Cand, LK_NONE), ({br, br1}, bc2, Cand, LK_STRG | LK_BOX)), ((CB[2], bc2, Cand, LK_NONE), (br2, {bc, bc1}, Cand, LK_STRG | LK_BOX)), (({br, br1}, bc2, Cand, LK_NONE), (br2, RB[2], Cand, LK_STRG | LK_BOX)), ((br2, {bc, bc1}, Cand, LK_NONE), (CB[2], bc2, Cand, LK_STRG | LK_BOX))])
        # look in cell
        if InclCell:
            for r in range(9):
                for c in range(9):
                    if len(Cands[r][c])==2 and Cand in Cands[r][c]:
                        Lks.extend([((r, c, Cand, LK_NONE), (r, c, list(Cands[r][c] - {Cand})[0], LK_STRG | LK_CELL))])
        # cleanup, convert all cell coords to sets.
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in Lks:
            R0 = {r0} if isinstance(r0, int) else r0
            C0 = {c0} if isinstance(c0, int) else c0
            R1 = {r1} if isinstance(r1, int) else r1
            C1 = {c1} if isinstance(c1, int) else c1
            Lks1.append((NL(R0, C0, Cand0, Lk0), NL(R1, C1, Cand1, Lk1)))
    else:  # No group link
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]:
                    c2 = -1
                    for c1 in range(9):
                        if Cand in Cands[r][c1]:
                            if c1 == c: continue
                            if c2 >= 0: break
                            else: c2 = c1
                    else:
                        if c2 >= 0:
                            LkHse = LK_ROW | LK_BOX if c//3 == c2//3 else LK_ROW
                            Lks1.append((NL(r, c, Cand, LK_NONE), NL(r, c2, Cand, LK_STRG | LkHse)))
                    r2 = -1
                    for r1 in range(9):
                        if Cand in Cands[r1][c]:
                            if r1 == r: continue
                            if r2 >= 0: break
                            else: r2 = r1
                    else:
                        if r2 >= 0:
                            LkHse = LK_COL | LK_BOX if r//3 == r2//3 else LK_COL
                            Lks1.append((NL(r, c, Cand, LK_NONE), NL(r2, c, Cand, LK_STRG | LkHse)))
                    r2 = c2 = -1
                    rb = r//3; cb = c//3
                    for b1 in range(9):
                        r1 = (rb*3) + b1//3; c1 = (cb*3) + b1%3
                        if Cand in Cands[r1][c1]:
                            if r1 == r and c1 == c: continue
                            if r1 == r or c1 == c: break
                            if r2 >= 0: break
                            else: r2 = r1; c2 = c1
                    else:
                        if r2 >= 0: Lks1.append((NL(r, c, Cand, LK_NONE), NL(r2, c2, Cand, LK_STRG | LK_BOX)))
                    if InclCell:
                        if len(Cands[r][c])==2:
                            Lks1.extend([(NL(r, c, Cand, LK_NONE), NL(r, c, list(Cands[r][c] - {Cand})[0], LK_STRG | LK_CELL))])
    return Lks1
