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
import os, sys
from copy import copy, deepcopy

import wx

from globals import *
from misc import open_puzzle, save_puzzle, ListSolnWindow, tkns_to_str

# Local imports
from generate import check_puzzle, gen_filled_grid, scramble_puzzle, minimalise_puzzle, create_puzzle
from solve_utils import determine_cands
from solve import *
from timer import *
from board import *
from puzzle import *

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
ST_CAND = 19  # show / clear candidates
ST_FSV  = 20  # Save puzzle to file when finished/Idle state.
ST_FKBD = 21  # Process keyboard entries in finished/Idle state
ST_NR   = 22  # number of states
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
GE[ST_CAND] = {SB: "Solve",       EMI: EMI_SOLVE}
GE[ST_FSV]  = {SB: "Idle",        EMI: EMI_IDLE}
GE[ST_FKBD] = {SB: "Idle",        EMI: EMI_IDLE}

# GE[ST_RSP]  = {SB: "Solve",       EMI: EMI_SOLVE}

# Sudoku Control State transit table (STT)
STT = [[] for ev in range(EV_SC_NR)]
#                  I   G   L   E   E   E   E   V   S   S   S   S   P   S   A   H   L   R   M   C   F   F
#                  D   E   D   N   S   M   K   A   L   S   M   K   S   C   U   N   S   S   I   A   S   K
#                  L   N       T   V   S   B   L   V   V   S   B   E   R   T   T   L   T   N   N   V   B
#                  E                       D                   D   D       O   S   N           D       D
#                  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
STT[EV_SC_GEN] = [1,  CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_LD]  = [2,  CH, CH,  2, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_ENT] = [3,  CH,  3,  3,  3,  3,  3,  3, CH, CH, CH, CH, CH,  3, CH, CH, CH, CH,  3, CH, CH, CH]
STT[EV_SC_SV]  = [20, CH, CH,  4, CH, CH, CH, CH,  9, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_MSE] = [IG, IG, IG,  5, IG, IG, IG, IG, 10, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG]
STT[EV_SC_KBD] = [21, IG, IG,  6, IG, IG, IG, IG, 11, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG, IG]
STT[EV_SC_VLD] = [CH,  7,  7,  7, CH, CH,  7, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_SLV] = [CH, CH, CH, CH, CH, CH, CH,  8,  8,  8,  8,  8, CH, CH,  8,  8,  8,  8, CH,  8, CH, CH]
STT[EV_SC_PSE] = [CH, CH, CH, CH, CH, CH, CH, CH, 12, CH, CH, CH,  8, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_SCR] = [CH, CH, CH, 13, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_ASL] = [CH, CH, CH, CH, CH, CH, CH, CH, 14, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_HNT] = [CH, CH, CH, CH, CH, CH, CH, CH, 15, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_LSN] = [16, CH, CH, CH, CH, CH, CH, CH, 16, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_RST] = [17, CH, CH, CH, CH, CH, CH, CH, 17, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_MIN] = [CH, CH, CH, 18, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_CND] = [CH, CH, CH, CH, CH, CH, CH, CH, 19, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]
STT[EV_SC_FIN] = [CH, CH,  0, CH,  3, CH, CH,  0,  0,  8, CH, CH, CH, CH, CH, CH,  8,  0, CH, CH,  0,  0]

# STT[EV_SC_RSP]  = [CH, CH, CH, CH, CH, CH, CH, CH, 19, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH]

class Sudoku:

    def __init__(self, MainWindow, MenuBar, StatusBar):

        # other class instances.
        self.MainWindow = MainWindow
        self.MenuBar    = MenuBar
        self.StatusBar  = StatusBar
        self.GameTimer  = GameTimer(StatusBar)
        self.Board      = Board(MainWindow, self)
        self.Puzzle     = None

        # instance data
        self.Grid        = [[0 for c in range(9)] for r in range(9)]
        self.Givens      = [[0 for c in range(9)] for r in range(9)]
        self.Cands       = [[set() for c in range(9)] for r in range(9)]  # only used when self.AssistCands = False.
        self.SelList     = []  # deque(())  # list of (r,c) tuples of selected cells
        self.History     = []         # History list (undo buffer) for Entry and Solve
        self.HL          = ()  # Highlighting
        # self.Lvl         = LVL_DEFAULT  # TODO: depreciated eliminate requested level (Menu/Options/Expertise Level selection
        self.Sym         = SYM_DEFAULT  # requested symmetry (Menu/Option/Symmetry selection
        self.Assist      = AST_DEFAULT
        self.AssistCands = AST_CANDS_DEFAULT
        self.ShowCands   = False
        self.Paused      = False
        self.ScState     = ST_IDLE
        self.VagueHints  = self.ClearerHints = self.ClearestHints = 0
        self.LSW         = None      # list solution window instance.
        self.OldGO       = False     # persistent variable used only in on_restart_state.
        self.Rsteps      = 0

        self.PzlDir = os.path.join(MainWindow.CWD, PUZZLES_DIR)  # where the puzzles are stored
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
                    self.on_candidates_state,
                    self.on_finish_save_state,
                    self.on_finish_keyboard_state]

    def on_close(self, e):
        self.GameTimer.on_close(e)
        if self.LSW:
            self.LSW.on_close(e)

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
        return

    # Sudoku control state machine actions follow

    def on_idle_state(self, e, Cleanup = False):

        self.StatusBar.update_0("")
        if Cleanup:
            self.GameTimer.stop()
            self.reset()
            # self.Board.clear_board()
            self.Puzzle = None
            self.PzlFn = ""
            self.MainWindow.SetTitle(TITLE)
            if self.LSW:
                self.LSW.on_close(0)
                self.LSW = None
        else:
            self.MenuBar.miPuzzleSave.Enable(True)
            self.MenuBar.miPuzzleListSoln.Enable(True)
            self.MenuBar.miPuzzleRestartGO.Enable(True)
            self.GameTimer.pause()  # ensure game timer is stopped
            self.update_status_histo(self.Grid)
        self.ShowCands = False
        self.MenuBar.miPuzzleCandsShow.Check(False)
        self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))

    def on_generate_state(self, e):
        # Creates a puzzle in self.Grid according to the difficulty level
        # self.Lvl and symmetry self.Sym options and returns with the logic step
        # to solve the puzzle in self.Steps.

        self.reset()
        self.Board.clear_board()
        if self.LSW:
            self.LSW.on_close(0)
            self.LSW = None
        self.StatusBar.update_0("Generating Puzzle, may take some time. . .")
        oPzl = PZL(Sym = self.Sym)
        create_puzzle(oPzl)  # returns with Soln and Givens fields filled
        oPzl.Grid    = [[oPzl.Givens[r][c] for c in range(9)] for r in range(9)]
        self.update_board(ST_ENT, oPzl)
        self.gen_event(EV_SC_VLD, oPzl)


    def on_load_state(self, e):
        # Can only (but not necessarily) transition to this state from the
        # Enter state if the UNSAVED_CHANGES flag is set.
        # if self.Flags & GF_UNSAVED_CHANGES:
        #     if wx.MessageBox("Discard unsaved changes?", "Confirmation",
        #                      wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         self.gen_event(EV_SC_ENT, False)
        #         return
        self.reset()
        self.Board.clear_board()
        # self.Flags &= ~GF_UNSAVED_CHANGES
        if self.LSW is not None:
            self.LSW.on_close(0)
            self.LSW = None
        self.Puzzle = None

        oPzl = PZL()  # {PZL_GRID: [], PZL_ELIMS: [], PZL_METH: T_UNDEF, PZL_PTRN: "", PZL_OUTC: ""}
        Fp, NrFlds = open_puzzle((self.PzlDir, self.PzlFn), oPzl)  # both grid and given records filled
        if Fp is None:
            self.gen_event(EV_SC_FIN, True)
            return
        (self.PzlDir, self.PzlFn) = Fp
        self.update_board(ST_ENT, oPzl)
        if NrFlds > 1:  # if only givens and placed values read, in enter mode, else transition to validation
            self.MainWindow.SetTitle(self.MainWindow.Title + " - "+Fp[1])
            self.MenuBar.miPuzzleEnter.Check(False)
            self.gen_event(EV_SC_VLD, oPzl)
        else:  # only givens and placed provided, only enter the givens and remain in enter mode.
            self.MainWindow.SetTitle(self.MainWindow.Title)
            self.MenuBar.miPuzzleEnter.Check()
            self.Grid   = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
            self.Givens = [[oPzl.Givens[r][c] for c in range(9)] for r in range(9)]
            self.gen_event(EV_SC_ENT, False)

        # # enter the givens and placed values on the board.  Givens are in entered state.
        # Cvs = 0
        # self.Givens = [[oPzl.Givens[r][c] if oPzl.Grid[r][c] < 10 else 0 for c in range(9)] for r in range(9)]
        # self.Grid   = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
        # # G           = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
        # # G1          = [[self.Grid[r][c]%10 for r in range(9)] for c in range(9)]
        # for r in range(9):
        #     for c in range(9):
        #         if self.Grid[r][c] == 0: Cvs = CVS_EMPTY
        #         else:
        #             Cvs = CVS_CNFLT if cell_val_has_conflicts(self.Grid, r, c) else 0
        #             if self.Givens[r][c]: Cvs |= CVS_ENTER
        #             else: Cvs |= CVS_PLACE
        #         self.Board.write_cell_value(self.Grid[r][c]%10, r, c, Cvs)
        # if not (Cvs & CVS_CNFLT) or Flds > 1:
        #     self.MainWindow.SetTitle(TITLE + " - " + Fp[1])
        #     self.MenuBar.miPuzzleEnter.Check(False)
        #     self.gen_event(EV_SC_VLD, oPzl)
        # else:  # only givens and placed provided, only enter the givens and remain in enter mode.
        #     self.MainWindow.SetTitle(TITLE)
        #     # G = oPzl[PZL_GRID]
        #     self.MenuBar.miPuzzleEnter.Check()
        #     self.gen_event(EV_SC_ENT, False)

    def on_entry_state(self, e, Cleanup = False):
        if Cleanup:
            self.reset()
            self.Board.clear_board()
            self.Grid = [[0 for c in range(9)] for r in range(9)]
            self.Givens = [[0 for c in range(9)] for r in range(9)]
        self.update_status_histo(self.Grid)
        self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))

    def on_entry_save_state(self, e):

        # oPzl = PZL(Grid = self.Grid, Givens = self.Givens)
        Fp = save_puzzle((self.PzlDir, self.PzlFn), PZL(Grid = self.Grid, Givens = self.Givens))
        if Fp is not None:
            self.PzlDir, self.PzlFn = Fp
            self.MainWindow.SetTitle(self.MainWindow.Title + " - " + self.PzlFn)
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
        elif Type == wx.EVT_RIGHT_DOWN:  # Right mouse button is a 27x27 array
            rc = r//3; cc = c//3
            rd = r%3; cd = c%3; v = (rd*3) + cd + 1
            self.Grid[rc][cc] = v
            if KbdMods != wx.MOD_SHIFT: self.Givens[rc][cc] = v
            self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))
        self.gen_event(EV_SC_ENT, False)

    def on_entry_keyboard_state(self, e, Key):
        if Key == wx.WXK_DELETE or Key == wx.WXK_CONTROL_H:  # ^H: Backspace
            for r, c in self.SelList:
                self.Grid[r][c] = self.Givens[r][c] = 0
            # oPzl = PZL(Grid = self.Grid, Givens = self.Givens)
            self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))
            self.gen_event(EV_SC_ENT, False)
            return
            # self.Board.write_cell_value(0, r, c, CVS_EMPTY)
            # Cvs = 0
            # G = [[self.Grid[r][c]%10 for c in range(9)] for r in range(9)]
            # for r in range(9):
            #     for c in range(9):
            #         if self.Grid[r][c] == 0: Cvs = CVS_EMPTY
            #         else:
            #             Cvs = CVS_CNFLT if cell_val_has_conflicts(G, r, c) else 0
            #             if self.Grid[r][c] < 10: Cvs |= CVS_ENTER
            #             else: Cvs |= CVS_PLACE
            #         self.Board.write_cell_value(G[r][c]%10, r, c, Cvs)
            # self.gen_event(EV_SC_ENT, False)
            # return

        if Key == wx.WXK_CONTROL_V:  # paste a puzzle spec from the clipboard
            # overwrites existing entries, and treated as if the spec was loaded from a file.
            oPzl = PZL()
            NrFlds = copy_clipboard_to_pzl(oPzl)
            if NrFlds: self.update_board(ST_ENT, oPzl)
            if NrFlds > 1:  # if only givens and placed values read, in enter mode, else transition to validation
                # self.MainWindow.SetTitle(TITLE+" - "+Fp[1])
                self.MenuBar.miPuzzleEnter.Check(False)
                self.gen_event(EV_SC_VLD, oPzl)
            else:  # only givens and placed provided, only enter the givens and remain in enter mode.
                # self.MainWindow.SetTitle(TITLE)
                self.MenuBar.miPuzzleEnter.Check()
                self.Grid = oPzl.Grid
                self.Givens = oPzl.Givens
                self.gen_event(EV_SC_ENT, False)
            return
            #
            # TDO = wx.TextDataObject()
            # if wx.TheClipboard.Open():
            #     wx.TheClipboard.GetData(TDO)
            #     sG = TDO.GetText()
            #     oPzl = PZL()  # {PZL_GRID: [], PZL_ELIMS: [], PZL_METH: T_UNDEF, PZL_PTRN: "", PZL_OUTC: ""}
            #     NrFlds = parse_pzl_str_depreciated(sG, oPzl)
            #     if NrFlds:
            #         oPzl.Givens = [[oPzl.Grid[r][c] if oPzl.Grid[r][c] < 10 else 0 for c in range(9)] for r in range(9)]
            #         self.Grid = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
            #         # G           = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
            #         G1 = [[self.Grid[r][c]%10 for r in range(9)] for c in range(9)]
            #         Cvs = 0
            #         for r in range(9):
            #             for c in range(9):
            #                 if self.Grid[r][c] == 0: Cvs = CVS_EMPTY
            #                 else:
            #                     Cvs = CVS_CNFLT if cell_val_has_conflicts(G1, r, c) else 0
            #                     if self.Grid[r][c] < 10: Cvs |= CVS_ENTER
            #                     else: Cvs |= CVS_PLACE
            #                 self.Board.write_cell_value(G1[r][c], r, c, Cvs)
            #         self.MainWindow.SetTitle(TITLE)
            #         if not (Cvs & CVS_CNFLT or Flds == 1):  # Continue to edit placed and givens.
            #             self.MenuBar.miPuzzleEnter.Check(False)
            #             self.gen_event(EV_SC_VLD, oPzl)
            #             return
            # self.gen_event(EV_SC_ENT, False)
            # return

        if Key == wx.WXK_CONTROL_C:
            # oPzl = PZL(Grid = self.Grid, Givens = self.Givens)
            copy_puzzle_to_clipboard(PZL(Grid = self.Grid, Givens = self.Givens))
            self.gen_event(EV_SC_ENT, False)
            return

        # else:  # Key in range(0x31, 0x3a):  # UTF-8 "1" through "9"
        Shift, Val = key_to_val(Key)  # [Shift] Key adds 10 to key's value.
        if Val != 0:
            Cvs = CVS_PLACE if Shift else CVS_ENTER
            for r, c in self.SelList:
                self.Grid[r][c] = Val
                if not Shift: self.Givens[r][c] = Val
            # oPzl = PZL(Grid = self.Grid, Givens = self.Givens)
            self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))
            self.gen_event(EV_SC_ENT, False)
        # if Val != 0:
        #     for r, c in self.SelList:
        #         self.Grid[r][c] = Val
        #     Cvs = 0
        #     G = [[self.Grid[r][c]%10 for c in range(9)] for r in range(9)]
        #     for r in range(9):
        #         for c in range(9):
        #             if self.Grid[r][c] == 0: Cvs = CVS_EMPTY
        #             else:
        #                 Cvs = CVS_CNFLT if cell_val_has_conflicts(G, r, c) else 0
        #                 if self.Grid[r][c] < 10: Cvs |= CVS_ENTER
        #                 else: Cvs |= CVS_PLACE
        #             self.Board.write_cell_value(G[r][c]%10, r, c, Cvs)
        # self.gen_event(EV_SC_ENT, False)

    def on_scramble_state(self, e):
        #  Only given/entered values are scrambled, placed values will be lost.
        self.Grid = scramble_puzzle(self.Givens)
        self.Givens = [[self.Grid[r][c] for c in range(9)] for r in range(9)]
        self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))
        while self.SelList:
            r, c = self.SelList.pop()
            self.Board.select_cell(r, c, False)
        self.gen_event(EV_SC_ENT, False)
        # for r in range(9):
        #     for c in range(9):
        #         if G[r][c]: Cvs = CVS_ENTER
        #         else: Cvs = CVS_EMPTY
        #         self.Board.write_cell_value(G[r][c], r, c, Cvs)
        # self.SelList.clear()
        # self.gen_event(EV_SC_ENT, False)

    def on_minimalise_state(self, e):
        #  Minimalises the combination of givens and placed.
        self.StatusBar.update_0("Minimalising Puzzle, may take some time. . .")
        self.Givens = minimalise_puzzle(self.Grid)
        self.Grid = [[self.Givens[r][c] for c in range(9)] for r in range(9)]
        while self.SelList:
            r, c = self.SelList.pop()
            self.Board.select_cell(r, c, False)
        self.update_board(ST_ENT, PZL(Grid = self.Grid, Givens = self.Givens))
        self.gen_event(EV_SC_ENT, False)
        # G = [[self.Grid[r][c] if self.Grid[r][c] < 10 else 0 for c in range(9)] for r in range(9)]
        # self.Grid = minimalise_puzzle(G)
        # # self.NrConflicts = self.NrGivens = 0
        # for r in range(9):
        #     for c in range(9):
        #         if G[r][c]: Cvs = CVS_ENTER
        #         else: Cvs = CVS_EMPTY
        #         self.Board.write_cell_value(G[r][c], r, c, Cvs)
        # self.SelList.clear()
        # self.gen_event(EV_SC_ENT, False)

    def on_validate_state(self, e, oPzl):
        # From Generate with Givens, Grid, and Soln. (no need to validate)
        # From Enter Menu being unchecked oPzl == None but self.Grid and self.Givens are valid.
        # From Load or [Ctrl]V with Givens and Grid, optionally Elims, Method, Pattern and Outcome
        #    With Elims specified, Elims are taken from Cands before grading puzzle.
        #    With Method specified, that method is tried as first step, if it fails proceeds as if no method specified.

        if not oPzl: oPzl = PZL(Grid = self.Grid, Givens = self.Givens)
        if not oPzl.Soln:  # validate puzzle by finding a solution
            # Some pre-checks first
            Gvns = 0
            for r in range(9):
                for c in range(9):
                    if cell_val_has_conflicts(oPzl.Grid, r, c):
                        wx.MessageBox(f"Puzzle has conflicts.\n", "Warning", wx.OK | wx.ICON_WARNING)
                        self.MenuBar.miPuzzleEnter.Check()
                        self.gen_event(EV_SC_ENT, False)
                        return
                    if oPzl.Givens[r][c]: Gvns += 1
            if Gvns < 17:
                if wx.MessageBox(f"Puzzle has {Gvns} givens, valid puzzle requires "
                                 "at least 17 givens.\n"
                                 "Do you want to go back and correct instead of starting over?",
                                 "Warning", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                    self.MenuBar.miPuzzleEnter.Check()
                    self.gen_event(EV_SC_ENT, False)
                else:
                    self.reset()
                    self.Board.clear_board()
                    self.gen_event(EV_SC_FIN)
                return
            self.StatusBar.update_0("Validating Puzzle, may take some time. . .")
            NrFound, oPzl.Soln = check_puzzle(oPzl.Grid)
            if NrFound != 1:
                self.StatusBar.update_0("")
                St = "Invalid Puzzle!  "
                St += "No Solution.\n" if NrFound == 0 else "Multiple Solutions.\n"
                St += "Do you want to correct instead of starting over"
                if wx.MessageBox(St, "Warning", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                    self.MenuBar.miPuzzleEnter.Check()
                    self.gen_event(EV_SC_ENT, False)
                else:
                    self.reset()
                    self.Board.clear_board()
                    self.Puzzle = None
                    self.gen_event(EV_SC_FIN)
                return
            # else: NrFound == 1:
        # else: We now have a solution and a validated or generated puzzle.
        #   Pzl structure contains a minimimum of Givens, Grid, Soln, with optional Elims, Method, Pattern and Outcome.

        self.StatusBar.update_0("Grading Puzzle, may take some time. . .")
        self.update_board(ST_SLV, oPzl)  # Change board colouring from Enter mode to Solve mode
        oPzl.Lvl, oPzl.Steps = logic_solve_puzzle(oPzl.Grid, oPzl.Elims, oPzl.Method, oPzl.Soln)
        if oPzl.Lvl < 0:
            wx.MessageBox("Cannot solve puzzle\n"
                          "Please save puzzle and send to developers",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)
            # Go to solve state so it is possible to get the incorrect elim or assignment and save puzzle.
            # self.gen_event(EV_SC_SLV)
            # return
        # Clear any selected cells
        while self.SelList:
            r, c = self.SelList.pop()
            self.Board.select_cell(r, c, False)
        #  Ditch the history
        self.History.clear()
        #  Create instance of Puzzle for solving.
        self.Puzzle = Puzzle(oPzl)
        #  Ready to transition to solve state
        self.GameTimer.start()
        self.StatusBar.update_level(LVLS[self.Puzzle.Lvl])
        self.reset()
        self.gen_event(EV_SC_SLV)
        #
        # NrEmpties, oPzl.Cands = determine_cands(oPzl.Grid, oPzl.Elims)
        #
        # for r in range(9):
        #     for c in range(9):
        #         if oPzl.Grid[r][c]:
        #             Cvs = CVS_GIVEN if oPzl.Givens[r][c] else CVS_PLACE Cvs = CVS_GIVEN else
        #             if oPzl.Givens[r][c]: Cvs = CVS_GIVEN
        #             else: Cvs = CVS_PLACE
        #             self.Board.write_cell_value(oPzl.Grid[r][c]%10, r, c, Cvs)
        #         else:
        #             if oPzl.Elims is not None and oPzl.Soln[r][c] in oPzl.Elims[r][c]:
        #                 wx.MessageBox(f"Invalid Candidate Elimination: r{r+1}c{c+1}-={self.Puzzle.Soln[r][c]}.",
        #                               "Information",
        #                               wx.ICON_INFORMATION | wx.OK)
        #                 oPzl = None
        #                 self.gen_event(EV_SC_ENT, False)
        #                 return
        #             if self.ShowCands:
        #                 Cands = set()
        #                 G1 = [[self.Grid[r][c]%10 for r in range(9)] for c in range(9)]
        #                 for Cand in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        #                     if cell_val_has_no_conflicts(Cand, G1, r, c):
        #                         Cands.add(Cand)
        #                 self.Board.write_cell_value(0, r, c, CVS_CANDS, Cands)
        #             else: self.Board.write_cell_value(0, r, c, CVS_CANDS)
        #
        #     self.StatusBar.update_0("Grading Puzzle, may take some time. . .")
        #     oPzl.Lvl, oPzl.Steps = logic_solve_puzzle(self.Puzzle.Grid, self.Puzzle.Elims, self.Puzzle.TryFirst, self.Puzzle.Soln)
        #     if self.Puzzle.Lvl < 0:
        #         wx.MessageBox("Cannot solve puzzle\n"
        #                       "Please save puzzle and send to developers",
        #                       "Information",
        #                       wx.ICON_INFORMATION | wx.OK)
        #         self.gen_event(EV_SC_SLV)
        #         return
        #
        #     # Clear any selected cells
        #     while len(self.SelList):
        #         r, c = self.SelList.popleft()
        #         self.Board.select_cell(r, c, False)
        #     #  Ditch the history
        #     self.History.clear()
        #     #  Ready to transition to solve state
        #     self.GameTimer.start()
        #     self.StatusBar.update_level(LVLS[self.Puzzle.Lvl])
        #     self.reset()
        #     self.gen_event(EV_SC_SLV)
        # else:  # puzzle validation error:
        #     # self.StatusBar.update_0("")
        #     # St = "Invalid Puzzle!  "
        #     # St += "No Solution.\n" if NrFound == 0 else "Multiple Solutions.\n"
        #     # St += "Do you want to correct instead of starting over"
        #     # if wx.MessageBox(St, "Warning", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
        #     #     self.MenuBar.miPuzzleEnter.Check()
        #     #     self.gen_event(EV_SC_ENT, False)
        #     # else:
        #     #     self.reset()
        #     #     self.Board.clear_board()
        #     #     del self.Puzzle; self.Puzzle = None
        #     #     self.gen_event(EV_SC_FIN)
        # return

    def on_solve_state(self, e):
        # Entering Pause state (can only occur from Solve state) will hide the
        # puzzle and pause the timer.  On re-entry ensure that the puzzle is
        # shown and the timer is resumed.

        if self.Paused:
            self.Board.hide_puzzle(False)
            self.GameTimer.resume()
            self.Paused = False

        self.update_status_histo(self.Puzzle.Grid)

        if self.Puzzle.NrEmpties == 0:  # and not self.Flags & GF_CORR:  # Puzzle is complete.
            Ans = 0
            # if self.Assist == AST_FIN_CHECK \
            #         or self.Assist == AST_FIN_CNFLTS \
            #         or self.Assist == AST_FIN_ERRORS:
                # grid = [[self.Grid[r][c][C_VAL] for c in range(9)] for r in range(9)]
            for r in range(9):
                for c in range(9):
                    if self.Puzzle.Givens[r][c]: continue
                    if self.Assist in [AST_CNFLTS, AST_FIN_CNFLTS]:
                        if cell_val_has_conflicts(self.Puzzle.Grid, r, c):
                            Ans = wx.MessageBox(f"There is at least one conflict in R{r+1}C{c+1}.\n"
                                                "Continue to Solve instead of starting over, "
                                                "or Cancel to Start New",
                                                "What would you like to do?",
                                                wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                    elif self.Assist in [AST_ERRORS, AST_FIN_ERRORS]:
                        if self.Puzzle.Grid[r][c] != self.Puzzle.Soln[r][c]:
                            Ans = wx.MessageBox(f"There is at least one error in R{r+1}C{c+1}.\n"
                                                "Continue to Solve instead of starting over, "
                                                "or Cancel to Start New",
                                                "What would you like to do?",
                                                wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                    else:  # self.Assist == AST_CHECK:
                        if self.Puzzle.Grid[r][c] != self.Puzzle.Soln[r][c]:
                            Ans = wx.MessageBox("There is at least one mistake\n"
                                                "Continue to Solve instead of starting over, "
                                                "or Cancel to Start New",
                                                "What would you like to do?",
                                                wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)
                    if Ans: break
                if Ans: break
            if not Ans:
                self.GameTimer.pause()
                while self.SelList:
                    r, c = self.SelList.pop()
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
            else:  # Ans = wx.YES
                self.Puzzle.Grid[r][c] = 0
                self.Puzzle.NrEmpties -= 1

    def on_solve_save_state(self, e):

        G = [[self.Puzzle.Grid[r][c] for c in range(9)] for r in range(9)]
        E = [[copy(self.Puzzle.Elims[r][c]) for c in range(9)] for r in range(9)]
        # TODO: change Step to Class from Dict.
        Step = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: []}
        Res = solve_next_step(G, Step, E)
        Fp = save_puzzle((self.PzlDir, self.PzlFn), PZL(
                Grid    = self.Puzzle.Grid,
                Givens  = self.Puzzle.Givens,
                Elims   = self.Puzzle.Elims,
                Method  = Step[P_TECH],
                Pattern = Step[P_PTRN],
                Outcome = Step[P_OUTC]))
        if Res < 0:
            wx.MessageBox("Bug in program!  Cannot solve next step\n"
                          "Please send saved puzzle to developers",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)
        if Fp is not None:
            self.PzlDir, self.PzlFn = Fp
            self.MainWindow.SetTitle(self.MainWindow.Title+" - "+self.PzlFn)
        self.gen_event(EV_SC_SLV)
        # self.gen_event(EV_SC_SLV)
        # G1 = [[self.Puzzle.Grid[r][c] for c in range(9)] for r in range(9)]
        # G  = [[G1[r][c] if (not G1[r][c]) or self.Puzzle.Givens[r][c] else G1[r][c]+10 for c in range(9)] for r in range(9)]
        # E1 = [[copy(self.Puzzle.Elims[r][c]) for c in range(9)] for r in range(9)]
        # E  = deepcopy(E1)
        # Step = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0}
        # if solve_next_step(G1, Step, E1) >= 0:
        #     Fp = save_puzzle((self.PzlDir, self.PzlFn), G, E, Step)
        # else:
        #     Fp = save_puzzle((self.PzlDir, self.PzlFn), G, E)
        #     wx.MessageBox("Bug in program!  Cannot solve next step\n"
        #                   "Please send saved puzzle to developers",
        #                   "Information",
        #                   wx.ICON_INFORMATION | wx.OK)
        #
        # if Fp is not None:
        #     self.PzlDir, self.PzlFn = Fp
        #     self.MainWindow.SetTitle(TITLE + " - " + self.PzlFn)
        # self.gen_event(EV_SC_SLV)

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
                # self.Flags |= GF_SAME_VAL_HL
                v = self.Puzzle.Grid[r][c]
                self.HL = (r, c, v)
                if v:
                    for r1 in range(9):
                        for c1 in range(9):
                            if v == self.Puzzle.Grid[r1][c1]:
                                if self.Puzzle.Givens[r1][c1]:
                                    self.Board.write_cell_value(v, r1, c1, CVS_SVGHL)
                                else:
                                    self.Board.write_cell_value(v, r1, c1, CVS_SVSHL)
                            # If candidates are shown and candidate assistance enabled
                            # then highlight that candidate value by changing candidate
                            # sub-cell background.
                            elif (not self.Puzzle.Grid[r1][c1]) and self.ShowCands:  # and self.AssistCands:
                                if self.AssistCands and cell_val_has_no_conflicts(v, self.Puzzle.Grid, r1, c1) and v not in self.Puzzle.Elims[r1][c1]:
                                    self.Board.set_cand_value(r1, c1, (v-1)//3, (v-1)%3, True, True)
                                elif v in self.Puzzle.Cands[r1][c1]:
                                    self.Board.set_cand_value(r1, c1, (v-1)//3, (v-1)%3, True, True)

            elif KbdMods == wx.MOD_ALT:
                # Popup the bg_clr selector to choose the cell's background
                # colour
                self.Board.popup_cell_bg_clr_selector(r, c)
            elif KbdMods == (wx.MOD_ALT | wx.MOD_CONTROL):
                self.HL = (r, c, 0)
                self.Board.group_highlight(True, r, c)

        elif Type == wx.EVT_LEFT_UP:
            # Releases the same cells value highlight push button, if it was
            # pressed.
            if self.HL:
                (r, c, v) = self.HL
                self.HL = ()
                if v:
                    for r1 in range(9):
                        for c1 in range(9):
                            if self.Puzzle.Givens[r1][c1] == v:
                                self.Board.write_cell_value(v, r1, c1, CVS_GIVEN)
                            elif self.Puzzle.Grid[r1][c1] == v:
                                self.Board.write_cell_value(v, r1, c1, CVS_PLACE)
                            elif (not self.Puzzle.Grid[r1][c1]) and self.ShowCands:  # and self.AssistCands:
                                if self.AssistCands and cell_val_has_no_conflicts(v, self.Puzzle.Grid, r1, c1) and v not in self.Puzzle.Elims[r1][c1]:
                                    self.Board.set_cand_value(r1, c1, (v-1)//3, (v-1)%3, True, False)
                                elif v in self.Puzzle.Cands[r1][c1]:
                                    self.Board.set_cand_value(r1, c1, (v-1)//3, (v-1)%3, True, False)
                else:  # if v == 0 must be a group highlight.
                    self.Board.group_highlight(False, r, c)

        elif Type == wx.EVT_RIGHT_DOWN:  # Work with candidates
            rc = r//3; cc = c//3
            rd = r%3; cd = c%3; Cand = (rd*3) + cd + 1
            if not KbdMods:  # Toggle the cands
                self.History.append((self.Puzzle.get_state()))

                if cell_val_has_no_conflicts(Cand, self.Puzzle.Grid, rc, cc) and Cand not in self.Puzzle.Elims[rc][cc]:
                    self.Puzzle.Elims[rc][cc].add(Cand)
                    if not self.AssistCands: self.Puzzle.Cands.discard(Cand)
                    self.Board.set_cand_value(rc, cc, rd, cd, False)
                elif Cand in self.Puzzle.Elims[rc][cc]:
                    self.Puzzle.Elims[rc][cc].discard(Cand)
                    if not self.AssistCands: self.Puzzle.Cands.add(Cand)
                    self.Board.set_cand_value(rc, cc, rd, cd, True)
                        # This is not a bug, we are purposefully silent about
                        # eliminating the candidate which is the solved value
                        # for that cell - So as not to give the game away.
                        # The candidate is not shown on the screen but is not
                        # added to the eliminated values that the hinter uses.
                        # The hinter needs to be true.
            elif KbdMods == wx.MOD_ALT:
                # Pop up the background selector to choose the candidate's
                # background colour.  Note that if white is selected, it is
                # treated as transparent.  That is the same background colour
                # as the underlying cell is used.
                if self.ShowCands:
                    self.Board.popup_cand_bg_clr_selector(r, c)
            elif KbdMods == wx.MOD_SHIFT:  # Convert candidate under cursor to value - overwrites existing cell value.
                if not self.Puzzle.Givens[rc][cc]:  # can only change placed vals not givens.
                    self.History.append((self.Puzzle.get_state()))  # deepcopy(self.Grid))
                    self.Puzzle.Grid[rc][cc] = Cand
                    self.Puzzle.NrEmpties = self.update_board(ST_SLV, PZL(
                            Grid = self.Puzzle.Grid,
                            Givens = self.Puzzle.Givens,
                            Elims = self.Puzzle.Elims,
                            Cands = self.Puzzle.Cands,
                            Soln = self.Puzzle.Soln))

            elif KbdMods == (wx.MOD_CONTROL | wx.MOD_ALT):
                # Reset all candidate background colours
                # Cursor can be over any cell to reset bg colours
                if self.ShowCands:
                    self.Board.reset_cand_bg_clrs()
        self.gen_event(EV_SC_SLV)

    def on_solve_keyboard_state(self, e, Key):
        # Ignore key presses if highlighting same values (Ctrl pressed while
        # left mouse button pressed)
        if self.HL:
            self_gen_event(EV_SC_SLV)
            return

        if Key == wx.WXK_DELETE or Key == wx.WXK_CONTROL_H:  # ^H: Backspace
            self.History.append((self.Puzzle.get_state()))
            for r, c in self.SelList:
                if not self.Puzzle.Givens[r][c]:
                    self.Puzzle.Grid[r][c] = 0
        elif Key == wx.WXK_CONTROL_Z:  # ^Z:  Undo
            if len(self.History):
                self.Puzzle.set_state(self.History.pop())
                if self.LSW:
                    if self.LSW.FromStep > 0:
                        self.LSW.FromStep -= 1
        elif Key == wx.WXK_CONTROL_C:  # copy to clipboard
            copy_puzzle_to_clipboard(PZL(
                    Grid = self.Puzzle.Grid,
                    Givens = self.Puzzle.Givens,
                    Elims = self.puzzle.Elims,
                    Method = self.Puzzle.Try1st,
                    Pattern = self.Puzzle.Try1stPattern,
                    Outcome = self.Puzzle.Try1stOutcome))
        elif Key in range(0x31, 0x3a):  # UTF-8 "1" through "9"
            self.History.append((self.Puzzle.get_state()))
            v = Key - 0x30
            for r, c in self.SelList:
                if not self.Puzzle.Givens[r][c]:
                    self.Puzzle.Grid[r][c] = v
                    # Do not update Elims and Cands rather fall back to their state if val placed in cell is deleted.
        # oPzl = PZL(Grid = self.Puzzle.Grid, Givens = self.Puzzle.Givens, Elims = self.Puzzle.Elims, Cands = self.Puzzle.Cands, Soln = self.Puzzle.Soln)
        self.Puzzle.NrEmpties = self.update_board(ST_SLV, PZL(
                Grid = self.Puzzle.Grid,
                Givens = self.Puzzle.Givens,
                Elims = self.Puzzle.Elims,
                Cands = self.Puzzle.Cands,
                Soln = self.Puzzle.Soln))
        self.gen_event(EV_SC_SLV)

    def on_paused_state(self, e, Pause):
        if Pause:
            self.Board.hide_puzzle(tf)
            self.GameTimer.pause()
            self.Paused = True

    def on_hints_state(self, e, h):
        for r in range(9):
            for c in range(9):
                if ((self.Puzzle.Grid[r][c] and self.Puzzle.Grid[r][c] != self.Puzzle.Soln[r][c])
                        or (self.Puzzle.Elims and self.Puzzle.Elims[r][c] and self.Puzzle.Soln[r][c] in self.Puzzle.Elims[r][c])):
                    wx.MessageBox("Fix errors in cell value or candidates first. . .", "Hint", wx.ICON_INFORMATION | wx.OK)
                    self.gen_event(EV_SC_SLV)
                    return

        G = [[self.Puzzle.Grid[r][c] for c in range(9)] for r in range(9)]
        E = [[copy(self.Puzzle.Elims[r][c]) for c in range(9)] for r in range(9)]
        Step = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: []}
        if solve_next_step(G, Step, E):
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
                                    f"Condition:  {tkns_to_str(Step[P_PTRN])}\n"
                                    f"\nThis hint will repeat until accepted.\n"
                                    f"\nAccept hint?",
                                    "Clearer Hint",
                                    wx.ICON_INFORMATION | wx.YES_NO)
                self.ClearerHints += 1
            else:  # H_CLEAREST
                Ans = wx.MessageBox(f"Clearest Hint:\n"
                                    f"Technique:  {T[Step[P_TECH]][T_TXT]}.\n"
                                    f"Condition:  {tkns_to_str(Step[P_PTRN])}\n"
                                    f"Outcome:    {tkns_to_str(Step[P_OUTC])}\n"
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
            self.process_step_outcome(self.Puzzle.Steps[i][P_OUTC])
        self.gen_event(EV_SC_SLV)


    def on_list_soln_state(self, e):
        if self.LSW:
            self.LSW.SetFocus()
        else:
            self.LSW = ListSolnWindow(self)
            self.LSW.Show()
        if self.Puzzle.NrEmpties: self.gen_event(EV_SC_SLV)
        else: self.gen_event(EV_SC_FIN)

    def on_restart_solve_state(self, e, GO):
        # GO -> givens only.
        self.reset()
        self.Puzzle.restart(GO)
        if self.LSW:
            self.LSW.on_close(0)
            self.LSW = None


        if GO:
            self.Puzzle.Grid = [[self.Puzzle.Givens[r][c] for c in range(9)] for r in range(9)]
            self.Puzzle.Elims = [[set() for c in range(9)] for r in range(9)]
        else:
            self.Puzzle.Grid = [[self.Puzzle.InitGrid[r][c] for c in range(9)] for r in range(9)]
            self.Puzzle.Elims = [[copy(self.Puzzle.InitElims[r][c]) for c in range(9)] for r in range(9)]
        if GO and (self.OldGO != GO):
            self.StatusBar.update_0("Re-validating Puzzle, may take some time. . .")
            self.Puzzle.NrEmpties = self.update_board(ST_ENT, PZL(Grid = self.Puzzle.Grid, Givens = self.Puzzle.Givens))

            NrFound, Soln, = check_puzzle(self.Puzzle.Grid)
            if NrFound != 1 and not grid_compare(Soln, self.Puzzle.Soln):
                wx.MessageBox("Givens do not form a valid puzzle\n"
                              "Information", wx.ICON_INFORMATION | wx.OK)
                # self.reset()
                # self.Board.clear_board()
                self.Puzzle = None
                self.gen_event(EV_SC_FIN, True)
                return

            self.StatusBar.update_0("Regrading Puzzle, may take some time. . .")
            self.update_board(ST_SLV, PZL(Grid = self.Puzzle.Grid, Givens = self.Puzzle.Givens))
            self.Puzzle.Lvl, self.Puzzle.Steps = logic_solve_puzzle(self.Puzzle.Grid, Soln = Soln)
            if self.Puzzle.Lvl < 0:
                wx.MessageBox("Cannot solve puzzle\n"
                              "Please save puzzle and send to developers",
                              "Information",
                              wx.ICON_INFORMATION | wx.OK)
                # Go to solve state so it is possible to get the incorrect elim or assignment and save puzzle.
                # self.gen_event(EV_SC_SLV)
                # return
            #  Ready to transition to solve state
        else:
            self.Puzzle.NrEmpties = self.update_board(ST_SLV, PZL(Grid = self.Puzzle.Grid, Givens = self.Puzzle.Givens))
        self.GameTimer.start()
        self.StatusBar.update_level(LVLS[self.Puzzle.Lvl])
        self.reset()
        self.OldGO = GO
        self.gen_event(EV_SC_SLV)

    def on_candidates_state(self, e, tf):
        self.ShowCands = tf
        if self.ShowCands and not self.AssistCands:
            NrEmpties, self.Puzzle.Cands = determine_cands(self.Puzzle.Grid)
        NrEmpties = self.update_board(ST_SLV, PZL(
                Grid = self.Puzzle.Grid,
                Givens = self.Puzzle.Givens,
                Elims = self.Puzzle.Elims,
                Cands = self.Puzzle.Cands,
                Soln = self.Puzzle.Soln))
        self.gen_event(EV_SC_SLV)


    def on_finish_save_state(self, e):
        # Fp = save_puzzle((self.PzlDir, self.PzlFn), PZL(
        save_puzzle((self.PzlDir, self.PzlFn), PZL(
                Grid    = self.Puzzle.Grid,
                Givens  = self.Puzzle.Givens))
        self.gen_event(EV_SC_FIN)


    def on_finish_keyboard_state(self, e, Key):
        if Key == wx.WXK_CONTROL_C:
            copy_puzzle_to_clipboard(PZL(
                    Grid = self.Puzzle.Grid,
                    Givens = self.Puzzle.Givens))
        self.gen_event(EV_SC_FIN)


    # Below are supporting functions for the Sudoku Control state machine actions
    def update_status_histo(self, Grid):
        H = [0, 0, 0, 0, 0, 0, 0, 0, 0]; G = 0
        for r in range(9):
            for c in range(9):
                if Grid[r][c]: H[Grid[r][c]-1] += 1; G += 1
        self.StatusBar.update_0(f"1►{H[0]}, 2►{H[1]}, 3►{H[2]}, 4►{H[3]}, 5►{H[4]}, "
                                f"6►{H[5]}, 7►{H[6]}, 8►{H[7]}, 9►{H[8]}, |{G}|")


    # def update_cands(self, v, r, c, Grid, Cands):
    #     # v > 0: update cands after adding a value v from cell
    #     # v < 0: update cands after removing value v from cell
    #     if v > 0:
    #         for i in range(9):
    #             Cands[r][i].discard(v)  # remember discard is silent if v not present.
    #             Cands[i][c].discard(v)
    #         br = (r//3)*3; bc = (c//3)*3
    #         for r1 in range(br, br+3):
    #             for c1 in range(bc, bc+3):
    #                 Cands[r1][c1].discard(v)
    #     else: #v < 0
    #         Peers = set()  # use set to automagically remove duplicates.
    #         for i in range(9): Peers |= {(r, i), (i, c)}
    #         br = (r//3)*3; bc = (c//3)*3
    #         for r1 in range(br, br+3):
    #             for c1 in range(bc, bc+3):
    #                 Peers |= {(r1, c1)}
    #         for r1, c1 in Peers:
    #             if cell_val_has_no_conficts(-v, Grid, r, c): Cands[r][c].add(-v)


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
                    self.History.append((self.Puzzle.get_state()))
                    self.Puzzle.Grid[r][c] = v
                    self.Puzzle.NrEmpties = self.update_board(ST_SLV, PZL(
                            Grid = self.Puzzle.Grid,
                            Givens = self.Puzzle.Givens,
                            Elims = self.Puzzle.Elims,
                            Cands = self.Puzzle.Cands,
                            Soln = self.Puzzle.Soln))
                    self.update_status_histo(self.Puzzle.Grid)
                elif op == OP_ELIM:
                    self.History.append((self.Puzzle.get_state()))
                    self.Puzzle.Elims[r][c].add(v)
                    r1 = (v-1)//3; c1 = (v-1)%3
                    self.Board.set_cand_value(r, c, r1, c1, False)
                # else: #  silently ignore other operations

    def reset(self):

        self.Grid = [[0 for c in range(9)] for r in range(9)]
        self.Givens = [[0 for c in range(9)] for r in range(9)]
        while self.SelList:
            r, c = self.SelList.pop()
            self.Board.select_cell(r, c, False)
        self.History.clear()   # History list (undo buffer) for Entry and Solve
        self.VagueHints = self.ClearerHints = self.ClearestHints = 0
        self.ShowCands = False
        self.MenuBar.miPuzzleCandsShow.Check(False)

    def update_board(self, Mode, oPzl):
        # returns the number of empties in the grid.
        # only relies on oPzl.Grid, oPzl.Givens, oPzl.Cands and oPzl.Elims and
        # Regarding candidates - only updates board with new state of candidates if ShowCands is set
        #    any computing of what the candidates are takes place prior to calling this function only
        #    if AssistCands is set.

        NrEmpties = 0
        if Mode == ST_ENT:
            for r in range(9):
                for c in range(9):
                    Cvs = 0
                    if oPzl.Grid[r][c]:
                        Cvs = CVS_ENTER if oPzl.Givens[r][c] else CVS_PLACE
                        if cell_val_has_conflicts(oPzl.Grid, r, c): Cvs |= CVS_CNFLT
                        self.Board.write_cell_value(oPzl.Grid[r][c], r, c, Cvs)
                    else:
                        NrEmpties += 1
                        self.Board.write_cell_value(0, r, c, CVS_CANDS, None)
        else:  # mode = ST_SLV
            for r in range(9):
                for c in range(9):
                    if oPzl.Grid[r][c]:
                        if oPzl.Givens[r][c]:  # A given cell/value
                            self.Board.write_cell_value(oPzl.Grid[r][c], r, c, CVS_GIVEN)
                        else:  # A placed cell value
                            Cvs = 0
                            if self.Assist == AST_CNFLTS and cell_val_has_conflicts(oPzl.Grid, r, c): Cvs = CVS_CNFLT
                            if self.Assist == AST_ERRORS and oPzl.Soln and oPzl.Grid[r][c] != oPzl.Soln[r][c]: Cvs = CVS_ERROR
                            self.Board.write_cell_value(oPzl.Grid[r][c], r, c, CVS_PLACE | Cvs)
                    else:  # empty cell - oPzl.Grid[r][c] == 0
                        NrEmpties += 1
                        if self.ShowCands:
                            if self.AssistCands:
                                Cands0 = set(range(1, 10))
                                if oPzl.Elims: Cands0 -= oPzl.Elims[r][c]
                                C = set()
                                for Cand in Cands0:
                                    if cell_val_has_no_conflicts(Cand, oPzl.Grid, r, c): C.add(Cand)
                            else: C = oPzl.Cands[r][c]
                        else: C = set()
                        self.Board.write_cell_value(0, r, c, CVS_CANDS, C)
        return NrEmpties
        #                 if oPzl.Grid[r][c]:
        #                     Cvs = 0
        #                     if self.Assist == AST_CNFLTS and cell_val_has_conflicts(oPzl.Grid, r, c): Cvs = CVS_CNFLT
        #                     if self.Assist == AST_ERRORS if oPzl.Soln and oPzl.Grid[r][c] != oPzl.Soln.Soln[r][c]: Cvs = CVS_ERROR
        #                     self.Board.write_cell_value(self.Puzzle.Grid[r][c], r, c, CVS_PLACE | Cvs)
        #                     if self.AssistCands and Cvs == 0:
        #                         self.Puzzle.Elims[r][c] = set()
        #                         self.update_board_peer_cands(r, c)
        #             else:  # self.Puzzle.Grid[r][c] == 0
        #
        #     Cvs0 = CVS_ENTER
        # else:
        #
        #
        #
        #     Cvs0 = CVS_GIVEN
        # #     pass
        # # else:  # mode == ST_SLV
        # NrEmpties = 0
        # for r in range(9):
        #     for c in range(9):
        #         if oPzl.Grid[r][c]:
        #             if oPzl.Givens[r][c]:
        #                 self.Board.write_cell_value(oPzl.Grid[r][c], r, c, Cvs0)
        #             elif oPzl.Grid[r][c]:
        #                 Cvs = 0
        #                 if self.Assist == AST_CNFLTS and cell_val_has_conflicts(oPzl.Grid, r, c): Cvs = CVS_CNFLT
        #                 if self.Assist == AST_ERRORS if oPzl.Soln and oPzl.Grid[r][c] != oPzl.Soln.Soln[r][c]: Cvs = CVS_ERROR
        #                 self.Board.write_cell_value(self.Puzzle.Grid[r][c], r, c, CVS_PLACE | Cvs)
        #                 if self.AssistCands and Cvs == 0:
        #                     self.Puzzle.Elims[r][c] = set()
        #                     self.update_board_peer_cands(r, c)
        #         else:  # self.Puzzle.Grid[r][c] == 0
        #             self.Puzzle.NrEmpties += 1
        #             if self.AssistCands and self.ShowCands:
        #                 self.Puzzle.Cands[r][c] = set()
        #                 for Cand in range(1, 10):
        #                     if cell_val_has_no_conflicts(Cand, self.Puzzle.Grid, r, c):
        #                         self.Puzzle.Cands[r][c].add(Cand)
        #                 self.Puzzle.Cands[r][c] -= self.Puzzle.Elims[r][c]
        #             self.Board.write_cell_value(0, r, c, CVS_CANDS, self.Puzzle.Cands[r][c])

    # def update_board_peer_cands(self, r, c):
    #     # Hide shown candidates in peer cells of values placed in selected
    #     # cells that are in CVS_PLACE state.
    #     v = self.Puzzle.Grid[r][c]
    #     if v:
    #         vr = (v-1)//3; vc = (v-1)%3
    #         # First the row.
    #         for r1 in range(9):
    #             if v in self.Puzzle.Cands[r1][c]:
    #                 self.Puzzle.Cands[r1][c].discard(v)
    #                 self.Board.set_cand_value(r1, c, vr, vc, False)
    #         # then the col.
    #         for c1 in range(9):
    #             if v in self.Puzzle.Cands[r][c1]:
    #                 self.Puzzle.Cands[r][c1].discard(v)
    #                 self.Board.set_cand_value(r, c1, vr, vc, False)
    #         # then the block.
    #         br = (r//3)*3
    #         bc = (c//3)*3
    #         for r1 in range(br, br+3):
    #             for c1 in range(bc, bc+3):
    #                 if self.Puzzle.Cands[r1][c1]:
    #                     self.Puzzle.Cands[r1][c1].discard(v)
    #                     self.Board.set_cand_value(r1, c1, vr, vc, False)

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
                self.Board.select_cell(r, c, True)
            elif dl == 1:  # Only one value in the list.
                # Clear previously selection, and select this one if not same
                r1, c1 = self.SelList.pop()
                self.Board.select_cell(r1, c1, False)
                if r1 != r or c1 != c:
                    self.SelList.append((r, c))
                    self.Board.select_cell(r, c, True)
            else:  # deque length > 1
                # Clear all selected cells and just select this one.
                while len(self.SelList):
                    r1, c1 = self.SelList.pop()
                    self.Board.select_cell(r1, c1, False)
                self.SelList.append((r, c))
                self.Board.select_cell(r, c, True)

        if KbdMods == wx.MOD_SHIFT:  # only Shift key is pressed.
            # Select multiple cells, if the cell is already  selected, just
            # toggle it to unselected, keeping the remaining selected cells.
            if self.Board.is_cell_selected(r, c):
                if (r, c) in self.SelList:
                    self.SelList.remove((r, c))
                self.Board.select_cell(r, c, False)
            else:
                self.SelList.append((r, c))
                self.Board.select_cell(r, c, True)

    def set_symmetry(self, sym):
        self.Sym = sym

    def set_assistance(self, ast):
        self.StatusBar.update_assist(AST_LVLS[ast])
        self.Assist = ast

    def set_assist_cands(self, tf):
        # can discard NrEmpties here as nothing has happened to change its value
        self.AssistCands = tf
        if tf:
            NrEmpties = self.update_board(ST_SLV, PZL(
                    Grid = self.Puzzle.Grid,
                    Givens = self.Puzzle.Givens,
                    Cands = self.Puzzle.Elims))
        else:    # Just seed cands with unconflicted vals
            NrEmpties, self.Puzzle.Cands = determine_cands(self.Puzzle.Grid)
            NrEmpties = self.update_board(ST_SLV, PZL(
                    Grid   = self.Puzzle.Grid,
                    Givens = self.Puzzle.Givens,
                    Cands  = self.Puzzle.Cands))


def key_to_val(Key):
    # Returns T/F, Val.  True if Shift key pressed, else false.
    if Key in range(0x31, 0x3a): return False, Key-0x30
    ShK = [312, 317, 367, 314, 305, 316, 313, 315, 366]  # Num pad vals
    if Key in ShK: return True, ShK.index(Key)+1
    ShK = ["!", "@", "#", "$", "%", "^", "&", "*", "("]
    if chr(Key) in ShK: return True, ShK.index(chr(Key))+1
    return False, 0

def grid_compare(g0, g1):
    for r in range(9):
        for c in range(9):
            if g0[r][c] != g1[r][c]: return False
    return True


