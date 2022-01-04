from copy import copy

from globals import *
# from misc import *
# from generate import *
from solve import Tech, LK_DIFF, GRP_LK_DIFF


class Puzzle:

    def __init__(self, oPzl):  # INSTR, *args, **kwds):
        # bare minimum initialisation is Grid, Givens, and Soln.

        self.Grid           = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
        self.InitGrid       = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
        if oPzl.Elims: self.Elims = [[copy(oPzl.Elims[r][c]) for c in range(9)] for r in range(9)]
        else: self.Elims    = [[set() for c in range(9)] for r in range(9)]
        self.InitElims      = [[copy(self.Elims[r][c]) for c in range(9)] for r in range(9)]
        self.Soln           = [[oPzl.Soln[r][c] for c in range(9)] for r in range(9)]
        self.Givens         = [[oPzl.Givens[r][c] for c in range(9)] for r in range(9)]
        if oPzl.Cands: self.Cands = [[copy(oPzl.Cands[r][c]) for c in range(9)] for r in range(9)]
        self.Cands          = [[set() for c in range(9)] for r in range(9)] # only used to track user selection of candidates when Sudoku.AssistCands is False.
        self.Steps          = oPzl.Steps
        self.NrGivens       = UNDEF
        self.NrEmpties      = UNDEF  # used to track remaining holes to fill when solving puzzles
        self.Lvl            = oPzl.Lvl
        self.Sym            = oPzl.Sym
        self.Try1st         = oPzl.Method
        self.Try1stPattern  = oPzl.Pattern
        self.Try1stOutcome  = oPzl.Outcome

        self.NrEmpties = self.NrGivens = 0
        for r in range(9):
            for c in range(9):
                if self.Givens[r][c]: self.NrGivens += 1
                if not self.Grid[r][c]: self.NrEmpties += 1
        # self.Rsteps    = UNDEF  # number of recursion steps (calls) taken to validate puzzle - relates to time

        # if INSTR == PZL_GEN:
        #     self.Sym = args[0]
        #     Pzl = PZL(Sym = self.Sym)
        #     # self.Soln = gen_filled_grid()
        #     # self.Givens = []
        #     create_puzzle(Pzl)
        #     self.Givens = Pzl.Givens
        #     self.Soln   = Pzl.Soln
        #     self.Lvl    = Pzl.Lvl
        #     self.Steps  = Pzl.Steps
        #
        #     self.NrGivens = self.NrEmpties = 0
        #     for r in range(9):
        #         for c in range(9):
        #             if self.Givens[r][c]:
        #                 self.InitGrid[r][c] = self.Grid[r][c] = self.Givens[r][c]
        #                 self.NrGivens += 1
        #             if not self.Grid[r][c]:
        #                 self.NrEmpties += 1
        # elif INSTR == PZL_VAL:
        #     oPzl = args[0]
        #     self.TryFirst  = oPzl[PZL_METH]
        #     self.NrEmpties = self.NrGivens = 0
        #     self.Givens    = [[0 for c in range(9)] for r in range(9)]
        #     for r in range(9):
        #         for c in range(9):
        #             self.InitGrid[r][c] = oPzl[PZL_GRID][r][c]
        #             if self.InitGrid[r][c] < 10:
        #                 self.Givens[r][c] = self.InitGrid[r][c]
        #                 if self.Givens[r][c]: self.NrGivens += 1
        #             self.Grid[r][c] = self.InitGrid[r][c] % 10
        #             if oPzl[PZL_ELIMS]:
        #                 self.InitElims[r][c] = copy(oPzl[PZL_ELIMS][r][c])
        #                 self.Elims[r][c] = copy(self.InitElims[r][c])
        #             if not self.Grid[r][c]: self.NrEmpties += 1


    def get_state(self):
        G = [[self.Grid[r][c] for c in range(9)] for r in range(9)]
        E = [[copy(self.Elims[r][c]) for c in range(9)] for r in range(9)]
        return G, E


    def set_state(self, S):
        (G, E) = S
        self.Grid  = G
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
                # self.Cands[r][c] = set()
                if not self.Grid[r][c]: self.NrEmpties += 1

    def get_props(self):
        StepsHisto = {Mthd: {HT_NR:    0,           # This is a 2d dict comprehension
                             HT_ADIFF: 0} for Mthd in Tech}
        Difficulty = 0
        for Step in self.Steps:
            Step.Difficulty                     = Tech[Step.Method].Difficulty + (Step.NrLks - Step.NrGrpLks) * LK_DIFF + Step.NrGrpLks * GRP_LK_DIFF
            Difficulty                        += Step.Difficulty
            StepsHisto[Step.Method][HT_NR]    += 1
            StepsHisto[Step.Method][HT_ADIFF] += Step.Difficulty

        GvnsHisto = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for r in range(9):
            for c in range(9):
                if self.Givens[r][c]:
                    GvnsHisto[self.Givens[r][c]-1] += 1
        Props = PZL_PROPS(Expertise   = self.Lvl,
                          NrGivens    = self.NrGivens,
                          GivensHisto = GvnsHisto,
                          Steps       = self.Steps,
                          StepsHisto  = StepsHisto,
                          Difficulty  = Difficulty
                          )
        return Props
