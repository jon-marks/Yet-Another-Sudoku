"""
sudoku.py:  Backend processing for puzzle entry and solving

Description:
    Provides the Sudoku class and supporting functionality for managing,
    entering and solving sudoku puzzles.

    Background colours are not part of the backend puzzle solving.
    Only used in the front end mmi as a visual aid to assist with
    hand solving puzzles.

Audit:
    2021-04-xx  jm  Initial Entry

"""
import os
from copy import copy, deepcopy

from collections import deque
import wx

# Local imports

from globals import *
from misc import open_puzzle, save_puzzle, ListSolnWindow, construct_str
from generate import *
from solve import *
from timer import *
from board import *

# Grid Flags
GF_UNSAVED_CHANGES = 0x00000001  # Unsaved edits in entry mode.
GF_CORR            = 0x00000002  # Correct an incorrectly completed puzzle
GF_SAME_VAL_HL     = 0x00000004  # Transient same values highlight (^+MSE_LT_DN)
GF_GROUP_HL        = 0x00000008  # Transient group highlight (^+alt+MSE_LT_DN)
GF_FLAG5           = 0x00000010  # example flag

# Grid cell attributes
C_VAL  = 0  # Working cell value  (int)
C_ST   = 1  # Cell value state                                                                       , see CVS_*
C_SEL  = 2  # True if cell is selected (bool)
C_SLVD = 3  # Correct cell value int in range 1 - 9
C_CAND = 4  # Candidate selected or not 3x3 bool array.  User tool does not impact programming logic
C_ELIM = 5  # Set of eliminated candidates - only used by program for hinting

# Sudoku Control State Machine states
ST_IDLE = 0   # idle state
ST_GEN  = 1   # program is generating a puzzle
ST_LD   = 2   # selecting and loading a puzzle from a file
ST_ENT  = 3   # hand entry of a puzzle
ST_ESV  = 4   # save in entry state
ST_EMS  = 5   # Mouse cmd in entry state
ST_EKBD = 6   # Keyboard cmd in entry state
ST_VLD  = 7   # validate entered puzzle
ST_SLV  = 8   # hand solving of a puzzle
ST_SSV  = 9   # Save to file in solve state
ST_SMS  = 10  # Mouse cmd in solve state
ST_SKBD = 11  # Keyboard cmd in solve state
ST_PSED = 12  # paused the hand solving of the puzzle
ST_SCR  = 13  # Scramble (Creating mathematically equivalent puzzles)
ST_AUTO = 14  # program is solving the puzzle
ST_HNTS = 15  # hint state
ST_LSLN = 16  # list solution state
ST_RST  = 17  # restart game with givens
ST_MIN  = 18  # Minimise an entered puzzle
# ST_RSP  = 19   spare   # restore set point
ST_CAND = 20  # show / clear candidates
ST_NR   = 21  # number of states
ST_DEFAULT = ST_IDLE


# lookup table for changing statusbar state status and selecting
# menu items to enable on transition to new states in self.gen_event
SB = 0
EMI = 1
GE = [{} for i in range(ST_NR)]
GE[ST_IDLE] = {SB: "Idle",        EMI: EMI_IDLE}
GE[ST_GEN]  = {SB: "Generate",    EMI: EMI_IDLE}
GE[ST_LD]   = {SB: "Load",        EMI: EMI_IDLE}
GE[ST_ENT]  = {SB: "Enter",       EMI: EMI_ENTER}
GE[ST_ESV]  = {SB: "Save",        EMI: EMI_ENTER}
GE[ST_EMS]  = {SB: "Enter",       EMI: EMI_ENTER}
GE[ST_EKBD] = {SB: "Enter",       EMI: EMI_ENTER}
GE[ST_VLD]  = {SB: "Validate",    EMI: EMI_ENTER}
GE[ST_SLV]  = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_SSV]  = {SB: "Save",        EMI: EMI_SOLVE}
GE[ST_SMS]  = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_SKBD] = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_PSED] = {SB: "Paused",      EMI: EMI_PAUSE}
GE[ST_SCR]  = {SB: "Scramble",    EMI: EMI_ENTER}
GE[ST_AUTO] = {SB: "Auto-Solve",  EMI: EMI_SOLVE}
GE[ST_HNTS] = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_LSLN] = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_RST]  = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_MIN]  = {SB: "Minimalise",  EMI: EMI_ENTER}
# GE[ST_RSP]  = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_CAND] = {SB: "Solve",       EMI: EMI_SOLVE}


# Sudoku Control State transit table (STT)
STT = [[] for ev in range(EV_SC_NR)]
#                  I   G   L   E   E   E   E   V   S   S   S   S   P   S   A   H   L   R   M   R   C
#                  D   E   D   N   S   M   K   A   L   S   M   K   S   C   U   N   S   S   I   S   A
#                  L   N       T   V   S   B   L   V   V   S   B   E   R   T   T   L   T   N   P   N
#                  E                       D                   D   D       O   S   N               D
#                  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
STT[EV_SC_GEN] = [1,  CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_LD]  = [2,  CH, CH,  2, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_ENT] = [3,  CH,  3,  3,  3,  3,  3,  3, CH, CH, CH, CH, CH,  3, CH, CH, CH, CH,  3, CH, CH]
STT[EV_SC_SV]  = [CH, CH, CH,  4, CH, CH, CH, CH,  9, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_MSE] = [IG, IG, IG,  5, IG, IG, IG, IG, 10, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG]
STT[EV_SC_KBD] = [IG, IG, IG,  6, IG, IG, IG, IG, 11, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG]
STT[EV_SC_VLD] = [CH, CH,  7,  7, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_SLV] = [CH,  8, CH, CH, CH, CH, CH,  8,  8,  8,  8,  8, CH, CH,  8,  8,  8,  8, CH, CH,  8]
STT[EV_SC_PSE] = [CH, CH, CH, CH, CH, CH, CH, CH, 12, CH, CH, CH,  8, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_SCR] = [CH, CH, CH, 13, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_ASL] = [CH, CH, CH, CH, CH, CH, CH, CH, 14, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_HNT] = [CH, CH, CH, CH, CH, CH, CH, CH, 15, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_LSN] = [CH, CH, CH, CH, CH, CH, CH, CH, 16, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_RST] = [17, CH, CH, CH, CH, CH, CH, CH, 17, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_MIN] = [CH, CH, CH, 18, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
#STT[EV_SC_RSP]  = [CH, CH, CH, CH, CH, CH, CH, CH, 19, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_CND] = [CH, CH, CH, CH, CH, CH, CH, CH, 20, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_FIN] = [CH, CH,  0, CH,  3, CH, CH,  0,  0,  8, CH, CH, CH, CH, CH, CH, CH,  0, CH, CH, CH]

class Sudoku:

    def __init__(self, MainWindow, MenuBar, StatusBar):
        # self.Parent = MainWindow

        self.MainWindow = MainWindow
        self.MenuBar    = MenuBar
        self.StatusBar  = StatusBar
        self.GameTimer  = GameTimer(StatusBar)
        self.Board      = Board(MainWindow, self)

        self.Grid = [[{C_VAL:  0,
                       C_ST:   CVS_EMPTY,
                       C_SEL:  False,
                       C_SLVD: 0,
                       C_CAND: [[False for cc in range(3)] for cr in range(3)],
                       C_ELIM: set()
                       } for c in range(9)] for r in range(9)]

        self.Props       = {}         # Puzzle properties including steps to solve, etc.
        self.NrConflicts = 0          # A count of conflicted cells in the grid
        self.NrErrors    = 0          # Tracking of value errors
        self.NrGivens    = 0          # A count of the givens.
        self.FilledVals  = []         # histogram of givens and solved values.
        self.NrEmpties   = 81         # All cells are empty
        self.SelList     = deque(())  # list of (r,c) tuples of selected cells
        self.History     = []         # History list (undo buffer) for Entry and Solve
        self.Flags       = 0
        self.Lvl         = LVL_DEFAULT
        self.Sym         = SYM_DEFAULT
        self.Assist      = AST_DEFAULT
        self.AssistCands = AST_CANDS_DEFAULT
        self.ShowCands   = False
        self.ScState     = ST_IDLE
        self.VagueHints  = self.ClearerHints = self.ClearestHints = 0
        self.LSW         = None      # list solution window instance.

        self.Dir    = os.getcwd()
        self.PzlDir = os.path.join(self.Dir, PUZZLES_DIR)  # where the puzzles are stored
        self.PzlFn  = ""

        self.MenuBar.enable_menuitems(EMI_IDLE)

        # Sudoku Control State action table.
        self.SAT = [self.on_idle_state,
                    self.on_generate_state,
                    self.on_load_state,
                    self.on_entry_state,
                    self.on_entry_save_state,
                    self.on_entry_mouse_state,
                    self.on_entry_keyboard_state,
                    self.on_validate_state,
                    self.on_solve_state,
                    self.on_solve_save_state,
                    self.on_solve_mouse_state,
                    self.on_solve_keyboard_state,
                    self.on_paused_state,
                    self.on_scramble_state,
                    self.on_auto_solve_state,
                    self.on_hints_state,
                    self.on_list_soln_state,
                    self.on_restart_solve_state,
                    self.on_minimalise_state,
                    None,  # self.on_restore_savepoint_state,
                    self.on_candidates_state]

    def on_close(self, e):
        self.GameTimer.on_close(e)

    def gen_event(self, e, *args, **kwds):
        # Moore model state machines: An event arriving at a state machine
        # causes a state transition to same or new state (based on the state
        # transition table (STT)) which causes the action associated with that
        # state (per the state action table (SAT)).  This function is used to
        # generate events for the Sudoku control state machine.  In addition to
        # affecting the state transistion, the status bar state field and the
        # enabling of menubar items is driven using the information in the GE
        # table.
        #
        # Parms:
        #   e:        The enumeration of the event arriving at the state machine
        #             to affect the transition
        #   *args:    event/action specific args list
        #   **kwds:   event/action specific kwd: value dict list.

        s = STT[e][self.ScState]
        if s == CH:  # Can't happen
            raise RuntimeError(f"Event {e:d} can't happen in state {self.ScState:d}")  # this event cannot happen in this state
        elif s == IG:  # Ignore
            pass  # ignore this event in this state
        else:
            if GE[s][SB] != GE[self.ScState][SB]:
                self.StatusBar.update_state(GE[s][SB])
            if GE[s][EMI] != GE[self.ScState][EMI]:
                self.MenuBar.enable_menuitems(GE[s][EMI])
            self.ScState = s
            self.SAT[self.ScState](e, *args, **kwds)

    # Sudoku control state machine actions follow
    def on_idle_state(self, e, Cleanup = False):
        self.Flags &= ~GF_UNSAVED_CHANGES
        self.StatusBar.update_0("")
        if Cleanup:
            self.GameTimer.stop()
            self.clear_grid()
            self.Board.clear_board()
            self.PzlFn = ""
            self.MainWindow.SetTitle(TITLE)
            if self.LSW is not None:
                self.LSW.on_close(0)
                self.LSW = None
        else:
            self.GameTimer.pause()  # ensure game timer is stopped
        self.ShowCands = False
        self.MenuBar.miPuzzleCandsShow.Check(False)

    def on_generate_state(self, e):
        # Creates a puzzle in self.Grid according to the difficulty level
        # self.Lvl and symmetry self.Sym options and returns with the logic step
        # to solve the puzzle in self.Steps.

        self.clear_grid()
        self.Board.clear_board()
        self.Flags &= ~GF_UNSAVED_CHANGES
        if self.LSW is not None:
            self.LSW.on_close(0)
            self.LSW = None

        self.StatusBar.update_0("Generating Puzzle, may take some time. . .")

        g = [[0 for c in range(9)] for r in range(9)]
        gen_filled_grid(g)
        for c in range(9):
            for r in range(9):
                self.Grid[r][c][C_SLVD] = g[r][c]

        self.Props[PR_REQ_LVL] = self.Lvl
        CreatePuzzle[self.Sym](g, self.Props)

        self.StatusBar.update_level(LVLS[self.Props[PR_ACT_LVL]])
        self.NrGivens = 0
        self.Props[PR_GIVENS] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for r in range(9):
            for c in range(9):
                self.Grid[r][c][C_VAL] = g[r][c]
                if g[r][c]:
                    self.Grid[r][c][C_ST] = CVS_GIVEN
                    self.Board.write_cell_value(g[r][c], r, c, CVS_GIVEN)
                    self.NrGivens += 1
                    self.Props[PR_GIVENS][g[r][c] - 1] += 1
                else:
                    self.Grid[r][c][C_ST] = CVS_CANDS
                    self.Board.write_cell_value(0, r, c, CVS_CANDS, self.Grid[r][c][C_CAND])
        self.NrEmpties = 81-self.NrGivens
        self.GameTimer.start()
        self.gen_event(EV_SC_SLV)

    def on_load_state(self, e):
        # Can only (but not necessarily) transition to this state from the
        # Enter state if the UNSAVED_CHANGES flag is set.
        if self.Flags & GF_UNSAVED_CHANGES:
            if wx.MessageBox("Discard unsaved changes?", "Confirmation",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                self.gen_event(EV_SC_ENT, False)
                return
        self.clear_grid()
        self.Board.clear_board()
        self.Flags &= ~GF_UNSAVED_CHANGES
        if self.LSW is not None:
            self.LSW.on_close(0)
            self.LSW = None

        G = [[0 for c in range(9)] for r in range(9)]
        # Following uses tuple as a hack to pass PzlDir and PzlFn by ref.
        Fp = open_puzzle((self.PzlDir, self.PzlFn), G)
        if Fp is None:
            self.gen_event(EV_SC_FIN)
            return

        # load the parsed grid into self.Grid and update the board.
        self.NrConflicts = self.NrGivens = 0
        for r in range(9):
            for c in range(9):
                v = G[r][c]
                if v:
                    G[r][c] = 0
                    if cell_val_has_no_conflicts(v, G, r, c):
                        self.Grid[r][c][C_ST] = CVS_ENTER
                    else:
                        self.NrConflicts += 1
                        self.Grid[r][c][C_ST] = CVS_CNFLT
                    G[r][c] = v
                    self.NrGivens += 1
                else:
                    self.Grid[r][c][C_ST] = CVS_EMPTY
                self.Grid[r][c][C_VAL] = v
                self.Board.write_cell_value(v, r, c,
                                                   self.Grid[r][c][C_ST])
        if wx.MessageBox("Sudoku value file successfully loaded\n"
                         "Would you like to edit values before validating?",
                         "Question",
                         wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
            self.MenuBar.miPuzzleEnter.Check()
            self.gen_event(EV_SC_ENT, False)  # Cleanup is False
        else:
            self.PzlDir, self.PzlFn = Fp
            self.MainWindow.SetTitle(TITLE + " - " + Fp[1])
            self.gen_event(EV_SC_VLD)

    def on_entry_state(self, e, Cleanup = False):
        if Cleanup:
            self.clear_grid()
            self.Board.clear_board()

    def on_entry_save_state(self, e):
        G = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        Fp = save_puzzle((self.PzlDir, self.PzlFn), G)
        if Fp is not None:
            self.PzlDir, self.PzlFn = Fp
            self.MainWindow.SetTitle(TITLE + " - " + self.PzlFn)
        self.gen_event(EV_SC_ENT, False)

    def on_entry_mouse_state(self, e, Type, r, c, KbdMods):
        if Type == wx.EVT_LEFT_DOWN:
            # Cell selection is a toggle and multiple cells can be selected.
            # Deselecting a selected cell when multiple cells are selected,
            # clears all the cells in the selection, except if the cursor is on
            # a selected cell, that cell is not deleted (unless it is the only
            # cell).  SHIFT with left mouse button is used to select multiple
            # cells.
            self.process_cell_selection(r, c, KbdMods)
        # All other mouse events ignored in entry state
        self.gen_event(EV_SC_ENT, False)

    def on_entry_keyboard_state(self, e, Key):
        if Key == wx.WXK_DELETE or Key == wx.WXK_CONTROL_H:  # ^H: Backspace
            self.History.append(deepcopy(self.Grid))
            for r, c in self.SelList:
                if self.Grid[r][c][C_VAL]:
                    self.Grid[r][c][C_VAL] = 0
                    self.Grid[r][c][C_ST] = CVS_EMPTY
                    self.Board.write_cell_value(0, r, c, CVS_EMPTY)

            self.Flags |= GF_UNSAVED_CHANGES
            # check for conflicts (in an imaged grid) and update board.
            grid = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
            self.NrConflicts = self.NrGivens = 0
            for r in range(9):
                for c in range(9):
                    v = grid[r][c]
                    if v:
                        self.NrGivens += 1
                        grid[r][c] = 0
                        if cell_val_has_no_conflicts(v, grid, r, c):
                            self.Grid[r][c][C_ST] = CVS_ENTER
                        else:
                            self.NrConflicts += 1
                            self.Grid[r][c][C_ST] = CVS_CNFLT
                        grid[r][c] = v
                        self.Board.write_cell_value(v, r, c, self.Grid[r][c][C_ST])

        elif Key == wx.WXK_CONTROL_Z:  # ^Z:  Undo
            if len(self.History):
                g = self.History.pop()
                self.Grid = deepcopy(g)
                for r in range(9):
                    for c in range(9):
                        self.Board.write_cell_value(g[r][c][C_VAL], r, c,
                                                           g[r][c][C_ST])
        elif Key in range(0x31, 0x3a):  # UTF-8 "1" through "9"
            # In Entry state, place the value in the selected cells and check
            # for conflicts
            self.History.append(deepcopy(self.Grid))
            for r, c in self.SelList:
                self.Grid[r][c][C_VAL] = Key-0x30

            self.Flags |= GF_UNSAVED_CHANGES
            # check for conflicts (in an imaged grid) and update board.
            grid = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
            self.NrConflicts = self.NrGivens = 0
            for r in range(9):
                for c in range(9):
                    v = grid[r][c]
                    if v:
                        self.NrGivens += 1
                        grid[r][c] = 0
                        if cell_val_has_no_conflicts(v, grid, r, c):
                            self.Grid[r][c][C_ST] = CVS_ENTER
                        else:
                            self.NrConflicts += 1
                            self.Grid[r][c][C_ST] = CVS_CNFLT
                        grid[r][c] = v
                        self.Board.write_cell_value(v, r, c, self.Grid[r][c][C_ST])
        self.gen_event(EV_SC_ENT, False)

    def on_scramble_state(self, e):
        self.History.append(deepcopy(self.Grid))
        G = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        G = scramble_puzzle(G)
        self.NrConflicts = self.NrGivens = 0
        for r in range(9):
            for c in range(9):
                v = G[r][c]
                if v:
                    self.NrGivens += 1
                    self.Grid[r][c][C_ST] = CVS_ENTER
                else:
                    self.Grid[r][c][C_ST] = CVS_EMPTY
                self.Grid[r][c][C_VAL] = G[r][c]
                self.Grid[r][c][C_SEL] = False
                self.Board.select_cell(r, c, False)
                self.Board.write_cell_value(G[r][c], r, c, self.Grid[r][c][C_ST])
        self.SelList.clear()
        self.gen_event(EV_SC_ENT, False)

    def on_minimalise_state(self, e):
        self.History.append(deepcopy(self.Grid))
        G = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        minimalise_puzzle(G)
        self.NrConflicts = self.NrGivens = 0
        for r in range(9):
            for c in range(9):
                if G[r][c]:
                    self.NrGivens += 1
                    self.Grid[r][c][C_ST] = CVS_ENTER
                else:
                    self.Grid[r][c][C_ST] = CVS_EMPTY
                self.Grid[r][c][C_VAL] = G[r][c]
                self.Grid[r][c][C_SEL] = False
                self.Board.select_cell(r, c, False)
                self.Board.write_cell_value(G[r][c], r, c, self.Grid[r][c][C_ST])
        self.SelList.clear()
        self.gen_event(EV_SC_ENT, False)

    def on_validate_state(self, e):
        if self.NrConflicts:
            if wx.MessageBox(f"Puzzle has {self.NrConflicts:d} conflicts.\n"
                             "Do you want to go back and correct instead of starting over?",
                             "Warning", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                self.MenuBar.miPuzzleEnter.Check()
                self.gen_event(EV_SC_ENT, False)
            else:
                self.clear_grid()
                self.Board.clear_board()
                self.gen_event(EV_SC_FIN)
            return
        if self.NrGivens < 17:
            if wx.MessageBox(f"Puzzle has {self.NrGivens:d} givens, valid puzzle requires "
                             "at least 17 givens.\n"
                             "Do you want to go back and correct instead of starting over?",
                             "Warning", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                self.MenuBar.miPuzzleEnter.Check()
                self.gen_event(EV_SC_ENT, False)
            else:
                self.clear_grid()
                self.Board.clear_board()
                self.gen_event(EV_SC_FIN)
            return

        self.StatusBar.update_0("Validating Puzzle, may take some time. . .")
        #  Image the grid
        G = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        Soln = {S_FOUND: 0, S_GRID: None}
        check_puzzle(G, Soln)
        if Soln[S_FOUND] == 1:  # The puzzle is valid
            # 0.  Copy the solved grid into self.Grid[][][C_SLVD], convert entered
            #     values to Givens and update board.
            self.NrGivens = 0
            self.Props[PR_GIVENS] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            for r in range(9):
                for c in range(9):
                    self.Grid[r][c][C_SLVD] = Soln[S_GRID][r][c]
                    if self.Grid[r][c][C_VAL]:
                        self.Grid[r][c][C_ST] = CVS_GIVEN
                        self.Board.write_cell_value(G[r][c], r, c, CVS_GIVEN)
                        self.Props[PR_GIVENS][G[r][c]-1] += 1
                        self.NrGivens += 1
                    else:
                        self.Grid[r][c][C_ST] = CVS_CANDS
                        self.Board.write_cell_value(0, r, c, CVS_CANDS, self.Grid[r][c][C_CAND])
            # 1.  Grade the puzzle
            # The grid g should still be good.
            self.Props[PR_REQ_LVL] = self.Lvl
            self.Props[PR_NR_HOLES] = 81-self.NrGivens
            if grade_puzzle(G, self.Props):
                self.StatusBar.update_level(LVLS[self.Props[PR_ACT_LVL]])
                # 2.  Clear any selected cells
                while len(self.SelList):
                    r, c = self.SelList.popleft()
                    self.Grid[r][c][C_SEL] = False
                    self.Board.select_cell(r, c, False)
                # 3.  Ditch the history
                self.History.clear()
                # 4.  Ready to transition to solve state
                self.GameTimer.start()
                self.NrEmpties = 81-self.NrGivens
                self.gen_event(EV_SC_SLV)
                return
            else:
                wx.MessageBox("Bug in program!\nPlease submit puzzle to developers",
                                 "Warning",
                                 wx.OK | wx.ICON_WARNING)
                self.gen_event(EV_SC_SLV)
                return
        self.StatusBar.update_0("")
        St = "Invalid Puzzle!  "
        St += "No Solution.\n" if Soln[S_FOUND] == 0 else "Multiple Solutions.\n"
        St += "Do you want to correct instead of starting over"
        if wx.MessageBox(St,
                         "Warning",
                         wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            self.MenuBar.miPuzzleEnter.Check()
            self.gen_event(EV_SC_ENT, False)
        else:
            self.clear_grid()
            self.Board.clear_board()
            self.gen_event(EV_SC_FIN)

    def on_solve_state(self, e, tf = True):
        # Entering Pause state (can only occur from Solve state) will hide the
        # puzzle and pause the timer.  On re-entry ensure that the puzzle is
        # shown and the timer is resumed.
        self.Board.hide_puzzle(False)
        self.GameTimer.resume()

        # update value histogram in status bar.
        G = self.FilledVals = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for r in range(9):
            for c in range(9):
                C = self.Grid[r][c]
                if C[C_ST] == CVS_GIVEN or C[C_ST] == CVS_SOLVE:
                    G[C[C_VAL]-1] += 1
        self.StatusBar.update_0(f"[1]={G[0]}, [2]={G[1]}, [3]={G[2]}, [4]={G[3]}, "
                                f"[5]={G[4]}, [6]={G[5]}, [7]={G[6]}, [8]={G[7]}, "
                                f"[9]={G[8]}")
        if self.NrEmpties == 0 and not self.Flags & GF_CORR:  # Puzzle is complete.
            if self.Assist == AST_FIN_CHECK \
                    or self.Assist == AST_FIN_CNFLTS \
                    or self.Assist == AST_FIN_ERRORS:
                Ans = 0
                grid = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
                for r in range(9):
                    for c in range(9):
                        v = grid[r][c]
                        if v:
                            if self.Grid[r][c][C_ST] != CVS_GIVEN:
                                if self.Assist == AST_FIN_CNFLTS:
                                    grid[r][c] = 0
                                    if not cell_val_has_no_conflicts(v, grid, r, c):
                                        Ans = wx.MessageBox(f"There is at least one conflict in R{r+1}C{c+1}.\n"
                                                            "Continue to Solve instead of starting over, "
                                                            "or Cancel to Start New",
                                                            "What would you like to do?",
                                                            wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                                    grid[r][c] = v
                                else:
                                    if v != self.Grid[r][c][C_SLVD]:
                                        if self.Assist == AST_FIN_ERRORS:
                                            Ans = wx.MessageBox(f"There is at least one error in R{r+1}C{c+1}.\n"
                                                                "Continue to Solve instead of starting over, "
                                                                "or Cancel to Start New",
                                                                "What would you like to do?",
                                                                wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                                        else:  # self.Assist == AST_CHECK:
                                            Ans = wx.MessageBox("There is at least one mistake\n"
                                                                "Continue to Solve instead of starting over, "
                                                                "or Cancel to Start New",
                                                                "What would you like to do?",
                                                                wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                        if Ans:
                            break
                    if Ans:
                        break
            else:
                Ans = 0
                if self.NrConflicts:
                    Ans = wx.MessageBox("There are conflicts to resolve\n"
                                        "Continue to Solve instead of starting "
                                        "over, or Cancel to Start New",
                                        "What would you like to do?",
                                        wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                elif self.NrErrors:
                    Ans = wx.MessageBox("There are errors to resolve\n"
                                        "Continue to Solve instead of starting "
                                        "over, or Cancel to Start New",
                                        "What would you like to do?",
                                        wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
            if not Ans:
                self.GameTimer.pause()
                while len(self.SelList):
                    r, c = self.SelList.pop()
                    self.Grid[r][c][C_SEL] = False
                    self.Board.select_cell(r, c, False)
                St = "Correct Solution!\n"
                if self.VagueHints:
                    St += f"    {self.VagueHints} vague hints.\n"
                if self.ClearerHints:
                    St += f"    {self.ClearerHints} clearer hints.\n"
                if self.ClearestHints:
                    St += f"    {self.ClearestHints} clearest hints."
                Ans = wx.MessageBox(St,
                                    "Information",
                                    wx.ICON_INFORMATION | wx.OK)
                self.gen_event(EV_SC_FIN)
            elif Ans == wx.NO:
                self.gen_event(EV_SC_RST)
            elif Ans == wx.CANCEL:
                self.gen_event(EV_SC_FIN, True)  # True to clear existing puzzle
            else:
                self.Flags |= GF_CORR

    def on_solve_save_state(self, e):
        G = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        Fp = save_puzzle((self.PzlDir, self.PzlFn), G)
        if Fp is not None:
            self.PzlDir, self.PzlFn = Fp
            self.MainWindow.SetTitle(TITLE + " - " + self.PzlFn)
        self.gen_event(EV_SC_SLV)

    def on_solve_mouse_state(self, e, Type, r, c, KbdMods):
        if Type == wx.EVT_LEFT_DOWN:
            if not KbdMods or KbdMods == wx.MOD_SHIFT:
                # Cell selection is a toggle, and multiple cells can be
                # (un)selected if the shift key is pressed
                # Deselecting a selected cell when multiple cells are selected,
                # clears all the cells in the selection, except if the cursor is
                # on a selected cell, that cell is not deleted (unless it is the
                # only cell).  SHIFT with left mouse button is used to select
                # multiple cells.
                self.process_cell_selection(r, c, KbdMods)
            elif KbdMods == wx.MOD_CONTROL:
                # Same cells value highlight pushbutton.  Highlights cells of
                # same value while the left mouse button is down.  This
                # highlighting only changes pen colours.  See CVS_CLR table in
                # globals.py  Only cells in GIVEN or SOLVE state are highlighted
                # in this manner.
                self.Flags |= GF_SAME_VAL_HL
                v = self.Grid[r][c][C_VAL]
                if v:
                    for r1 in range(9):
                        for c1 in range(9):
                            if self.Grid[r][c][C_VAL] == self.Grid[r1][c1][C_VAL]:
                                if self.Grid[r1][c1][C_ST] == CVS_GIVEN:
                                    self.Grid[r1][c1][C_ST] = CVS_SVGHL
                                    self.Board.write_cell_value(self.Grid[r1][c1][C_VAL],
                                                                       r1, c1, CVS_SVGHL)
                                elif self.Grid[r1][c1][C_ST] == CVS_SOLVE:
                                    self.Grid[r1][c1][C_ST] = CVS_SVSHL
                                    self.Board.write_cell_value(self.Grid[r1][c1][C_VAL],
                                                                       r1, c1, CVS_SVSHL)

                            # If candidates are shown and candidate assistance enabled
                            # then highlight that candidate value by changing candidate
                            # sub-cell background.
                            elif self.ShowCands and self.AssistCands:
                                rd = (v - 1) // 3
                                cd = (v - 1) % 3
                                self.Board.set_cand_value(r1, c1, rd, cd,
                                                                 self.Grid[r1][c1][C_CAND][rd][cd], True)

            elif KbdMods == wx.MOD_ALT:
                # Popup the bg_clr selector to choose the cell's background
                # colour
                self.Board.popup_cell_bg_clr_selector(r, c)
            elif KbdMods == (wx.MOD_ALT | wx.MOD_CONTROL):
                self.Flags |= GF_GROUP_HL
                self.Board.group_highlight(True, r, c)

        elif Type == wx.EVT_LEFT_UP:
            # Releases the same cells value highlight push button, if it was
            # pressed.
            if self.Flags & GF_SAME_VAL_HL:
                self.Flags &= ~GF_SAME_VAL_HL
                for r1 in range(9):
                    for c1 in range(9):
                        if self.Grid[r1][c1][C_ST] == CVS_SVGHL:
                            self.Grid[r1][c1][C_ST] = CVS_GIVEN
                            self.Board.write_cell_value(self.Grid[r1][c1][C_VAL],
                                                               r1, c1, CVS_GIVEN)
                        elif self.Grid[r1][c1][C_ST] == CVS_SVSHL:
                            self.Grid[r1][c1][C_ST] = CVS_SOLVE
                            self.Board.write_cell_value(self.Grid[r1][c1][C_VAL],
                                                               r1, c1, CVS_SOLVE)
                        elif self.ShowCands and self.AssistCands:
                            for rd in [0, 1, 2]:
                                for cd in [0, 1, 2]:
                                    self.Board.set_cand_value(r1, c1, rd, cd,
                                                                     self.Grid[r1][c1][C_CAND][rd][cd])
            elif self.Flags & GF_GROUP_HL:
                self.Flags &= ~GF_GROUP_HL
                self.Board.group_highlight(False, r, c)

        elif Type == wx.EVT_RIGHT_DOWN:
            # Note: r and c here are in the range 0 - 26 candidate cells,
            # not 0 - 9 as for value cells with LEFT_DOWN.
            rc = r//3
            cc = c//3
            if self.Grid[rc][cc][C_ST] == CVS_CANDS:
                # Only if Cands are being displayed, ie the cell is empty.
                rd = r%3
                cd = c%3
                if not KbdMods:
                    d = not(self.Grid[rc][cc][C_CAND][rd][cd])
                    self.Grid[rc][cc][C_CAND][rd][cd] = d
                    self.Board.set_cand_value(rc, cc, rd, cd, d)
                    if self.AssistCands and not d:
                        v = (rd * 3) + cd + 1
                        # This is not a bug, we are purposefully silent about
                        # eliminating the candidate which is the solved value
                        # for that cell - So as not to give the game away.
                        # The candidate is not shown on the screen but is not
                        # added to the eliminated values that the hinter uses.
                        # The hinter needs to be true.
                        if v != self.Grid[rc][cc][C_SLVD]:
                            self.Grid[rc][cc][C_ELIM].add(v)
                elif KbdMods == wx.MOD_ALT:
                    # Pop up the background selector to choose the candidate's
                    # background colour.  Note that if white is selected, it is
                    # treated as transparent.  That is the same background colour
                    # as the underlying cell is used.
                    self.Board.popup_cand_bg_clr_selector(r, c)
                elif KbdMods == wx.MOD_SHIFT:
                    self.History.append(deepcopy(self.Grid))
                    self.Grid[rc][cc][C_VAL] = (rd * 3) + cd + 1
                    self.Grid[rc][cc][C_ST] = CVS_SOLVE
                    self.Flags &= ~GF_CORR
                    self.process_grid()
                    if self.AssistCands:
                        self.update_peer_cands(rc, cc)
                elif KbdMods == wx.MOD_CONTROL:
                    if self.ShowCands:
                        for r1 in range(9):
                            for c1 in range(9):
                                self.Board.set_cand_value(r1, c1, rd, cd,
                                                                 self.Grid[r1][c1][C_CAND][rd][cd], True)

            if KbdMods == (wx.MOD_CONTROL | wx.MOD_ALT):
                # Reset all candidate background colours
                # Cursor can be over any cell to reset bg colours
                self.Board.reset_cand_bg_clrs()
        elif Type == wx.EVT_RIGHT_UP:
            if self.ShowCands:
                rd = r%3
                cd = c%3
                for r1 in range(9):
                    for c1 in range(9):
                        self.Board.set_cand_value(r1, c1, rd, cd,
                                                         self.Grid[r1][c1][C_CAND][rd][cd])
        self.gen_event(EV_SC_SLV)

    def on_solve_keyboard_state(self, e, Key):
        # Ignore key presses if highlighting same values (Ctrl pressed while
        # left mouse button pressed)
        if self.Flags & GF_SAME_VAL_HL:
            self_gen_event(EV_SC_SLV)
            return

        if Key == wx.WXK_DELETE or Key == wx.WXK_CONTROL_H:  # ^H: Backspace
            self.History.append(deepcopy(self.Grid))
            for r, c in self.SelList:
                if self.Grid[r][c][C_VAL] and not self.Grid[r][c][C_ST] == CVS_GIVEN:
                    self.Grid[r][c][C_VAL] = 0
                    self.Grid[r][c][C_ST] = CVS_CANDS
                    self.Flags &= ~GF_CORR
        elif Key == wx.WXK_CONTROL_Z:  # ^Z:  Undo
            if len(self.History):
                self.Grid = deepcopy(self.History.pop())
                if self.LSW is not None:
                    if self.LSW.FromStep > 0:
                        self.LSW.FromStep -= 1
                self.Flags &= ~GF_CORR
        elif Key in range(0x31, 0x3a):  # UTF-8 "1" through "9"
            self.History.append(deepcopy(self.Grid))
            for r, c in self.SelList:
                if self.Grid[r][c][C_ST] != CVS_GIVEN:
                    self.Grid[r][c][C_VAL] = Key-0x30
                    self.Grid[r][c][C_ST] = CVS_SOLVE
                    self.Flags &= ~GF_CORR
        self.process_grid()
        if self.AssistCands:
            for r, c in self.SelList:
                self.update_peer_cands(r, c)
        self.gen_event(EV_SC_SLV)

    def on_paused_state(self, e, tf):
        if tf:
            self.Board.hide_puzzle(tf)
            self.GameTimer.pause()

    def on_hints_state(self, e, h):
        if not self.NrEmpties:

            wx.MessageBox("Should never get here\n"
                          "There needs to be at least one empty cell to hint.",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)
            self.gen_event(EV_SC_SLV)
            return

        if self.AssistCands and self.ShowCands:
            for r in range(9):
                for c in range(9):
                    if self.Grid[r][c][C_ST] == CVS_CANDS:
                        for rc in range(3):
                            for cc in range(3):
                                v = (rc * 3) + cc + 1
                                if (not self.Grid[r][c][C_CAND][rc][cc]) and v == self.Grid[r][c][C_SLVD]:
                                    if h == H_VAGUE:
                                        wx.MessageBox("Fix incorrectly eliminated candidate(s).",
                                                      "Hint",
                                                      wx.ICON_INFORMATION | wx.OK)
                                    else:
                                        wx.MessageBox(f"Fix incorrectly eliminated candidate value {v:d}.",
                                                      "Hint",
                                                      wx.ICON_INFORMATION | wx.OK)
                                    self.gen_event(EV_SC_SLV)
                                    return

        g = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        Step = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
        e = [[copy(self.Grid[r][c][C_ELIM]) for c in range(9)] for r in range(9)]
        if solve_next_step(g, Step, e):
            if h == H_VAGUE:
                Ans = wx.MessageBox(f"Vague Hint:\n"
                                    f"Technique: {T[Step[P_TECH]][T_TXT]}.\n"
                                    f"\nThis hint will repeat until accepted.\n"
                                    f"\nAccept hint?",
                                    "Vague Hint",
                                    wx.ICON_INFORMATION | wx.YES_NO)
                self.VagueHints += 1
            elif h == H_CLEARER:

                Ans = wx.MessageBox(f"Clearer Hint:\n"
                                    f"Technique: {T[Step[P_TECH]][T_TXT]}.\n"
                                    f"Condition:  {construct_str(Step[P_COND])}\n"
                                    f"\nThis hint will repeat until accepted.\n"
                                    f"\nAccept hint?",
                                    "Clearer Hint",
                                    wx.ICON_INFORMATION | wx.YES_NO)
                self.ClearerHints += 1
            else:  #  H_CLEAREST
                Ans = wx.MessageBox(f"Clearest Hint:\n"
                                    f"Technique:  {T[Step[P_TECH]][T_TXT]}.\n"
                                    f"Condition:  {construct_str(Step[P_COND])}\n"
                                    f"Outcome:    {construct_str(Step[P_OUTC])}\n"
                                    f"\nThis hint will repeat until accepted.\n"
                                    f"\nAccept hint?",
                                    "Clearest Hint",
                                    wx.ICON_INFORMATION | wx.YES_NO)
                self.ClearestHints += 1
            if Ans == wx.YES:
                self.process_step_outcome(Step[P_OUTC])
        else:
            wx.MessageBox("Bug in program!  Cannot solve next step\n"
                          "Please save puzzle and send to developers",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)
        self.gen_event(EV_SC_SLV)

    def on_auto_solve_state(self, e, FromStep, ToStep):

        for i in range(FromStep, ToStep):
            self.process_step_outcome(self.Props[PR_STEPS][i][P_OUTC])
        self.gen_event(EV_SC_SLV)


    def on_list_soln_state(self, e):
        self.LSW = ListSolnWindow(self)
        self.LSW.Show()
        self.gen_event(EV_SC_SLV)

    def on_restart_solve_state(self, e):
        if self.NrGivens:   # the grid is populated with a puzzle
            self.Board.clear_board()
            self.NrConflicts = 0  # A count of conflicted cells in the grid
            self.NrEmpties = 81-self.NrGivens  # All cells are empty
            self.FilledVals = copy(self.Props[PR_GIVENS])
            self.SelList.clear()  # list of (r,c) tuples of selected cells
            self.History.clear()  # History list (undo buffer) for Entry and Solve
            self.Flags = 0
            self.VagueHints = self.ClearerHints = self.ClearestHints = 0
            self.ShowCands = False
            self.MenuBar.miPuzzleCandsShow.Check(False)
            if self.LSW is not None:
                self.LSW.on_close(0)
                self.LSW = None

            for r in range(9):
                for c in range(9):
                    C = self.Grid[r][c]
                    if C[C_ST] != CVS_GIVEN:
                        C[C_ST] = CVS_CANDS
                        C[C_VAL] = 0
                        C[C_CAND] = [[False for cc in range(3)] for cr in range(3)]
                        C[C_ELIM] = set()
                    self.Board.write_cell_value(C[C_VAL], r, c, C[C_ST], C[C_CAND])
            self.gen_event(EV_SC_SLV)
        else:
            self.gen_event(EV_SC_FIN)

    # def on_set_savepoint_state(self, e):
    #     # TODO:  on_set_savepoint_state(self, e):
    #     pass
    #
    # def on_restore_savepoint_state(self, e):
    #     # TODO:  on_restore_savepoint_state(self, e):
    #     pass

    def on_candidates_state(self, e, tf):
        self.ShowCands = tf
        g = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        if tf:  # Show Candidates
            for r in range(9):
                for c in range(9):
                    if not g[r][c]:  # Cell is empty (can show candidates)
                        i = 0
                        for r1 in range(3):
                            for c1 in range(3):
                                i += 1
                                if cell_val_has_no_conflicts(i, g, r, c) \
                                        and i not in self.Grid[r][c][C_ELIM]:
                                    self.Grid[r][c][C_CAND][r1][c1] = True
                                    self.Board.set_cand_value(r, c, r1, c1, True)
                                else:
                                    self.Grid[r][c][C_CAND][r1][c1] = False
                                    self.Board.set_cand_value(r, c, r1, c1, False)
        else:
            for r in range(9):
                for c in range(9):
                    if not g[r][c]:  # Cell is empty
                        for r1 in range(3):
                            for c1 in range(3):
                                self.Grid[r][c][C_CAND][r1][c1] = False
                                self.Board.set_cand_value(r, c, r1, c1, False)
        self.gen_event(EV_SC_SLV)

    # Below are supporting functions for the Sudoku Control state machine actions

    def process_step_outcome(self, S):
        # Assumes cell outcome phrases between separators are of the
        # form:  r<n>c<n><op><val>
        r = c = op = v = -1
        for Tkn in S:
            if Tkn[0] == P_ROW:
                r = Tkn[1]
            elif Tkn[0] == P_COL:
                c = Tkn[1]
            elif Tkn[0] == P_OP:
                op = Tkn[1]
            elif Tkn[0] == P_VAL:
                v = Tkn[1]
            elif Tkn[0] == P_SEP or Tkn[0] == P_END:
                if op == OP_ASNV:
                    self.History.append(deepcopy(self.Grid))
                    self.Grid[r][c][C_VAL] = v
                    self.Grid[r][c][C_ST] = CVS_SOLVE
                    self.process_grid()
                    if self.AssistCands:
                        self.update_peer_cands(r, c)
                elif op == OP_ELIM:
                    self.History.append(deepcopy(self.Grid))
                    self.Grid[r][c][C_ELIM].add(v)
                    r1 = (v - 1) // 3
                    c1 = (v - 1) % 3
                    self.Grid[r][c][C_CAND][r1][c1] = False
                    self.Board.set_cand_value(r, c, r1, c1, False)
                # else: #  silently ignore other operations

    def clear_grid(self):
        # initialise / reset the main grid structure.

        self.Grid = [[{C_VAL:  0,
                       C_ST:   CVS_EMPTY,
                       C_SEL:  False,
                       C_SLVD: 0,
                       C_CAND: [[False for pc in range(3)] for pr in range(3)],
                       C_ELIM: set()
                       } for c in range(9)] for r in range(9)]

        self.Props       = {}  # Puzzle properties including steps to solve, etc.
        self.NrConflicts = 0   # A count of conflicted cells in the grid
        self.NrGivens    = 0   # A count of the givens.
        self.FilledVals  = []  # Histogram of givens and solved values
        self.NrEmpties   = 81  # All cells are empty
        self.SelList.clear()   # list of (r,c) tuples of selected cells
        self.History.clear()   # History list (undo buffer) for Entry and Solve
        self.Flags       = 0
        self.VagueHints = self.ClearerHints = self.ClearestHints = 0

    #        self.ElimCands      = [[set() for c in range(9)] for r in range(9)]

    def process_grid(self):

        self.NrConflicts = self.NrErrors = 0
        self.NrEmpties = 81-self.NrGivens
        grid = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
        if self.Assist == AST_CNFLTS or self.Assist == AST_ERRORS:
            # check for conflicts (in an imaged grid) and update board.
            for r in range(9):
                for c in range(9):
                    v = grid[r][c]
                    if v:
                        if self.Grid[r][c][C_ST] != CVS_GIVEN:
                            self.NrEmpties -= 1
                            if self.Assist == AST_CNFLTS:
                                grid[r][c] = 0
                                if cell_val_has_no_conflicts(v, grid, r, c):
                                    self.Grid[r][c][C_ST] = CVS_SOLVE
                                else:
                                    self.Grid[r][c][C_ST] = CVS_CNFLT
                                    self.NrConflicts += 1
                                grid[r][c] = v
                            elif self.Assist == AST_ERRORS:
                                if v == self.Grid[r][c][C_SLVD]:
                                    self.Grid[r][c][C_ST] = CVS_SOLVE
                                else:
                                    self.Grid[r][c][C_ST] = CVS_ERROR
                                    self.NrErrors += 1
                    else:
                        self.Grid[r][c][C_ST] = CVS_CANDS
                    self.Board.write_cell_value(v, r, c, self.Grid[r][c][C_ST],
                                                       self.Grid[r][c][C_CAND])
        else:
            for r in range(9):
                for c in range(9):
                    v = grid[r][c]
                    if v:
                        if self.Grid[r][c][C_ST] != CVS_GIVEN:
                            self.Grid[r][c][C_ST] = CVS_SOLVE
                            self.NrEmpties -= 1
                    else:
                        self.Grid[r][c][C_ST] = CVS_CANDS
                    self.Board.write_cell_value(v, r, c, self.Grid[r][c][C_ST],
                                                       self.Grid[r][c][C_CAND])


    def update_peer_cands(self, r, c):
        # Hide shown candidates in peer cells of values placed in selected
        # cells that are in CVS_SOLVE state.
        if self.Grid[r][c][C_ST] == CVS_SOLVE:
            v = self.Grid[r][c][C_VAL]-1
            vr = v//3
            vc = v%3
            # First the row.
            for r1 in set(range(9))-{r}:
                if self.Grid[r1][c][C_CAND][vr][vc]:
                    self.Grid[r1][c][C_CAND][vr][vc] = False
                    self.Board.set_cand_value(r1, c, vr, vc, False)
            # then the col.
            for c1 in set(range(9))-{c}:
                if self.Grid[r][c1][C_CAND][vr][vc]:
                    self.Grid[r][c1][C_CAND][vr][vc] = False
                    self.Board.set_cand_value(r, c1, vr, vc, False)
            # then the block.
            br = (r//3)*3
            bc = (c//3)*3
            for r1 in range(br, br+3):
                for c1 in range(bc, bc+3):
                    if self.Grid[r1][c1][C_CAND][vr][vc]:
                        self.Grid[r1][c1][C_CAND][vr][vc] = False
                        self.Board.set_cand_value(r1, c1, vr, vc, False)

    def process_cell_selection(self, r, c, KbdMods):
        # Cell selection on left mouse down is exactly the same irrespective of
        # entry or solve states, so the shared functionality is here.  Cell
        # selection behaviour depends on whether only the SHIFT key is pressed
        # or not.  The shift key is used to select multiple cells.
        #
        # Parms:
        #   r, c:    In:  The row and column of the cell under the cursor
        #   KbdMods: In:  The state of the Ctrl, Alt, and Shift keys.

        if not KbdMods:  # No modifiers pressed.
            # Just toggle the selection of the current cell, after erasing the
            # selection of all other cells that may have been selected.

            dl = len(self.SelList)
            if dl == 0:  # Selection list is empty
                # Simply select the cell
                self.SelList.append((r, c))
                self.Grid[r][c][C_SEL] = True
                self.Board.select_cell(r, c, True)
            elif dl == 1:  # Only one value in the list.
                # Clear previously selection, and select this one if not same
                r1, c1 = self.SelList.popleft()
                self.Grid[r1][c1][C_SEL] = False
                self.Board.select_cell(r1, c1, False)
                if r1 != r or c1 != c:
                    self.SelList.append((r, c))
                    self.Grid[r][c][C_SEL] = True
                    self.Board.select_cell(r, c, True)
            else:  # deque length > 1
                # Clear all selected cells and just select this one.
                while len(self.SelList):
                    r1, c1 = self.SelList.popleft()
                    self.Grid[r1][c1][C_SEL] = False
                    self.Board.select_cell(r1, c1, False)
                self.SelList.append((r, c))
                self.Grid[r][c][C_SEL] = True
                self.Board.select_cell(r, c, True)

        if KbdMods == wx.MOD_SHIFT:  # only Shift key is pressed.
            # Select multiple cells, if the cell is already  selected, just
            # toggle it to unselected, keeping the remaining selected cells.
            if self.Grid[r][c][C_SEL]:
                if (r, c) in self.SelList:
                    self.SelList.remove((r, c))
                self.Grid[r][c][C_SEL] = False
                self.Board.select_cell(r, c, False)
            else:
                self.SelList.append((r, c))
                self.Grid[r][c][C_SEL] = True
                self.Board.select_cell(r, c, True)

    def get_sel_list(self):
        # returns the selection list
        return self.SelList

    def set_expertise_req_lvl(self, lvl):
        # Setting the expertise level is a menu selection to request the puzzle
        # generator to create a puzzle to that expertise level.  This is the
        # requested or desired level of a puzzle to be generated.  This is not
        # to be confused with the actual difficulty level shown in the status
        # bar.  For example a generated puzzle may not be able to achieve the
        # desired expertise before becoming minimal or a loaded or hand entered
        # puzzle that has a difficulty different to that in the menu option.
        # the difficulty level of the puzzle in play.
        self.Lvl = lvl

    def set_symmetry(self, sym):
        self.Sym = sym

    def set_assistance(self, ast):
        self.StatusBar.update_assist(AST_LVLS[ast])
        self.Assist = ast

    def set_assist_cands(self, tf):
        self.AssistCands = tf
