

from globals import *
from misc import *
from generate import *
from solve import *


class Puzzle:

    def __init__(self, INSTR, *args, **kwds):
        # self.Grid, self.Cands and self.ElimCands track user activity in solving the puzzle, which
        # may or may not be correct.  The logic_solve_puzzle() and solve_next_step

        self.Grid      = [[0 for c in range(9)] for r in range(9)]
        self.Elims     = [[set() for c in range(9)] for r in range(9)]
        self.Soln      = []  # [[0 for c in range(9)] for r in range(9)]
        # self.Givens    = [[0 for c in range(9)] for r in range(9)]
        self.InitGrid  = [[0 for c in range(9)] for r in range(9)]  # placed = val + 10
        self.InitElims = [[set() for c in range(9)] for r in range(9)]
        self.Cands     = [[set() for c in range(9)] for r in range(9)]
        self.Steps     = []
        self.TryFirst  = UNDEF
        self.NrGivens  = UNDEF
        self.NrEmpties = UNDEF  # used to track remaining holes to fill when solving puzzles
        self.Lvl       = UNDEF
        self.Sym       = UNDEF
        self.Rsteps    = UNDEF  # number of recursion steps (calls) taken to validate puzzle - relates to time

        if INSTR == PZL_GEN:
            Lvl = args[0]; self.Sym = args[1]
            self.Soln = [[0 for c in range(9)] for r in range(9)]
            gen_filled_grid(self.Soln)
            self.Givens = []
            create_puzzle(Lvl, self)
            self.NrGivens = self.NrEmpties = 0
            for r in range(9):
                for c in range(9):
                    if self.Givens[r][c]:
                        self.InitGrid[r][c] = self.Grid[r][c] = self.Givens[r][c]
                        self.NrGivens += 1
                    if not self.Grid[r][c]:
                        self.NrEmpties += 1
        elif INSTR == PZL_LOAD:
            oPzl = args[0]
            self.TryFirst  = oPzl[PZL_METH]
            self.NrEmpties = self.NrGivens = 0
            self.Givens    = [[0 for c in range(9)] for r in range(9)]
            for r in range(9):
                for c in range(9):
                    self.InitGrid[r][c] = oPzl[PZL_GRID][r][c]
                    if self.InitGrid[r][c] < 10:
                        self.Givens[r][c] = self.InitGrid[r][c]
                        if self.Givens[r][c]: self.NrGivens += 1
                    self.Grid[r][c] = self.InitGrid[r][c] % 10
                    if oPzl[PZL_ELIMS]:
                        self.InitElims[r][c] = copy(oPzl[PZL_ELIMS][r][c])
                        self.Elims[r][c] = copy(self.InitElims[r][c])
                    if not self.Grid[r][c]: self.NrEmpties += 1


    def get_state(self):
        G = [[self.Grid[r][c] for c in range(9)] for r in range(9)]
        C = [[copy(self.Cands[r][c]) for c in range(9)] for r in range(9)]
        E = [[copy(self.Elims[r][c]) for c in range(9)] for r in range(9)]
        return G, C, E


    def set_state(self, S):
        (G, C, E) = S
        self.Grid  = G
        self.Cands = C
        self.Elims = E


    def restart(self, GQ):
        self.NrEmpties = 0
        for r in range(9):
            for c in range(9):
                if GQ:
                    self.Grid[r][c] = self.Givens[r][c]
                    self.Elims[r][c] = set()
                else:
                    self.Grid[r][c] = self.InitGrid[r][c] % 10
                    self.Elims[r][c] = copy(self.InitElims[r][c])
                self.Cands[r][c] = set()
                if not self.Grid[r][c]: self.NrEmpties += 1

    def get_props(self):
        StepsHisto = {Tx: {HT_NR:    0,
                           HT_TXT:   T[Tx][T_TXT],
                           HT_LVL:   T[Tx][T_LVL],
                           HT_DIFF:  T[Tx][T_DIFF],
                           HT_ADIFF: 0} for Tx in T}
        Diff = 0
        for S in self.Steps:
            if not S[P_DIFF]: S[P_DIFF] = T[S[P_TECH]][T_DIFF]
            Diff += S[P_DIFF]
            H = StepsHisto[S[P_TECH]]
            H[HT_NR] += 1
            H[HT_ADIFF]  += S[P_DIFF]

        GvnsHisto = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for r in range(9):
            for c in range(9):
                if self.Givens[r][c]:
                    GvnsHisto[self.Givens[r][c]-1] += 1

        Props = {PR_LVL:         self.Lvl,
                 PR_NR_GVNS:     self.NrGivens,
                 PR_GVNS_HISTO:  GvnsHisto,
                 PR_STEPS:       self.Steps,
                 PR_STEPS_HISTO: StepsHisto,
                 PR_DIFF:        Diff}
        return Props
