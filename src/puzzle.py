

from globals import *


class Puzzle:

    def __init__(self, Parent):

        self.Parent = Parent
        self.Grid = [[0 for c in range(9)] for r in range(9)]
        self.Givens = [[0 for c in range(9)] for r in range(9)]
        self.Cands = [[set() for c in range(9)] for r in range(9)]
        self.ElimCands = [[set() for c in range(9)] for r in range(9)]
        self.props = {}




        self.Grid = [[0 for c in range(9)] for r in range(9)]


