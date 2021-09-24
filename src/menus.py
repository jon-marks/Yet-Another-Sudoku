"""
    Name:  menus.py

    Contains the MainMenubar and other contextual menus used in the program.
    The wx.EVT_MENU callbacks make calls to other classes out of this file.
    No program functionality other than the menu structure and the wx.EVT_MENU
    events are handled in this file / these classes.

    The User Guide class bound to the Help/User Guide menu item is also included
    here.

    Audit:
        2021-04-xx  jm  Initial entry

"""

import wx
import wx.html

from globals import *
from misc import UserGuide

class MainMenubar(wx.MenuBar):

    def __init__(self, parent):
        wx.MenuBar.__init__(self)

        # Puzzle Menu
        self.mPuzzle = wx.Menu()
        self.Append(self.mPuzzle, "&Puzzle")

        self.miPuzzleGenerate = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "&Generate",
                                            "Generate a puzzle according to set options",
                                            wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleGenerate)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_generate, self.miPuzzleGenerate)

        self.miPuzzleEnter = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "&Enter",
                                         "Manual puzzle entry toggle "
                                         "- Manually enter a puzzle",
                                         wx.ITEM_CHECK)

        self.mPuzzle.Append(self.miPuzzleEnter)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_enter, self.miPuzzleEnter)
        self.miPuzzleEnter.Check(False)

        self.miPuzzleOpen = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                        "&Open...",
                                        "Opens a sudoku puzzle file",
                                        wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleOpen)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_open, self.miPuzzleOpen)

        self.miPuzzleScramble = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                            "Sc&ramble",
                                            "Create a mathematically equivalent puzzle",
                                            wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleScramble)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_scramble, self.miPuzzleScramble)

        self.miPuzzleMinimalise = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                              "&Minimalise",
                                              "Make existing puzzle minimal",
                                              wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleMinimalise)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_minimalise, self.miPuzzleMinimalise)

        self.miPuzzleSave = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                        "&Save...",
                                        "Save puzzle values",
                                        wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleSave)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_save, self.miPuzzleSave)

        self.mPuzzle.AppendSeparator()

        self.miPuzzleCandsShow = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                             "Show &Possible Candidates",
                                             "Show possible candidates in unfilled cells.",
                                             wx.ITEM_CHECK)
        self.mPuzzle.Append(self.miPuzzleCandsShow)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_cands_show, self.miPuzzleCandsShow)
        self.miPuzzleCandsShow.Check(False)

        self.mPuzzle.AppendSeparator()

        self.miPuzzlePause = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "&Pause",
                                         "Pause toggle - "
                                         "Pauses and resumes the current puzzle",
                                         wx.ITEM_CHECK)
        self.mPuzzle.Append(self.miPuzzlePause)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_pause, self.miPuzzlePause)
        self.miPuzzlePause.Check(False)

        self.mPuzzle.AppendSeparator()

        self.smPuzzleHint = wx.Menu()
        self.mPuzzle.AppendSubMenu(self.smPuzzleHint, "&Hint")

        self.miPuzzleHintVague = wx.MenuItem(self.smPuzzleHint, wx.ID_ANY, "&Vague",
                                             "Logic technique", wx.ITEM_NORMAL)
        self.smPuzzleHint.Append(self.miPuzzleHintVague)
        parent.Bind(wx.EVT_MENU, lambda e, hint = H_VAGUE: self.on_puzzle_hint(e, hint),
                    self.miPuzzleHintVague)

        self.miPuzzleHintClearer = wx.MenuItem(self.smPuzzleHint, wx.ID_ANY, "&Clear",
                                               "Logic technique details",
                                               wx.ITEM_NORMAL)
        self.smPuzzleHint.Append(self.miPuzzleHintClearer)
        parent.Bind(wx.EVT_MENU, lambda e, hint = H_CLEARER: self.on_puzzle_hint(e, hint),
                    self.miPuzzleHintClearer)

        self.miPuzzleHintClearest = wx.MenuItem(self.smPuzzleHint, wx.ID_ANY, "C&learest",
                                                "Logic technique details and outcomes",
                                                wx.ITEM_NORMAL)
        self.smPuzzleHint.Append(self.miPuzzleHintClearest)
        parent.Bind(wx.EVT_MENU, lambda e, hint = H_CLEAREST: self.on_puzzle_hint(e, hint),
                    self.miPuzzleHintClearest)

        self.miPuzzleListSoln = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "L&ist Solution",
                                            "List the steps to solve the current puzzle",
                                            wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleListSoln)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_list_solution, self.miPuzzleListSoln)

        self.mPuzzle.AppendSeparator()

        self.miPuzzleRestart = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "Start Ov&er",
                                           "Restart the current puzzle", wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleRestart)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_restart, self.miPuzzleRestart)

        self.miPuzzleRestartGO = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "Start Over (&Givens Only)",
                                             "Restart the current puzzle", wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleRestartGO)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_restart_go, self.miPuzzleRestartGO)

        self.miPuzzleGiveUp = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "Start &New",
                                          "Give up current puzzle", wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleGiveUp)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_give_up, self.miPuzzleGiveUp)

        self.mPuzzle.AppendSeparator()

        self.miPuzzleExit = wx.MenuItem(self.mPuzzle, wx.ID_ANY, "&Exit",
                                        "Good bye.", wx.ITEM_NORMAL)
        self.mPuzzle.Append(self.miPuzzleExit)
        parent.Bind(wx.EVT_MENU, self.on_puzzle_exit, self.miPuzzleExit)

        # View Menu
        self.mView = wx.Menu()
        self.Append(self.mView, "&View")

        self.smViewZoom = wx.Menu()
        self.mView.AppendSubMenu(self.smViewZoom, "&Zoom")

        self.miViewZoomTiny = wx.MenuItem(self.smViewZoom, wx.ID_ANY, "&Tiny",
                                          "Ridiculously Small size",
                                          wx.ITEM_RADIO)
        self.smViewZoom.Append(self.miViewZoomTiny)
        parent.Bind(wx.EVT_MENU, lambda e, CellSz = TNY_CELL_SZ: self.on_view_zoom(e, CellSz),
                    self.miViewZoomTiny)
        if DEFAULT_CELL_SZ == TNY_CELL_SZ:
            self.miViewZoomTiny.Check(True)

        self.miViewZoomSmall = wx.MenuItem(self.smViewZoom, wx.ID_ANY, "&Small", "Small size",
                                           wx.ITEM_RADIO)
        self.smViewZoom.Append(self.miViewZoomSmall)
        parent.Bind(wx.EVT_MENU, lambda e, CellSz = SML_CELL_SZ: self.on_view_zoom(e, CellSz),
                    self.miViewZoomSmall)
        if DEFAULT_CELL_SZ == SML_CELL_SZ:
            self.miViewZoomSmall.Check(True)

        self.miViewZoomNormal = wx.MenuItem(self.smViewZoom, wx.ID_ANY, "&Normal", "Normal",
                                            wx.ITEM_RADIO)
        self.smViewZoom.Append(self.miViewZoomNormal)
        parent.Bind(wx.EVT_MENU, lambda e, CellSz = NRM_CELL_SZ: self.on_view_zoom(e, CellSz),
                    self.miViewZoomNormal)
        if DEFAULT_CELL_SZ == NRM_CELL_SZ:
            self.miViewZoomNormal.Check(True)

        self.miViewZoomLarge = wx.MenuItem(self.smViewZoom, wx.ID_ANY, "&Large", "Large",
                                           wx.ITEM_RADIO)
        self.smViewZoom.Append(self.miViewZoomLarge)
        parent.Bind(wx.EVT_MENU, lambda e, CellSz = LRG_CELL_SZ: self.on_view_zoom(e, CellSz),
                    self.miViewZoomLarge)
        if DEFAULT_CELL_SZ == LRG_CELL_SZ:
            self.miViewZoomLarge.Check(True)

        self.miViewZoomXLarge = wx.MenuItem(self.smViewZoom, wx.ID_ANY, "E&xtra Large",
                                            "Ridiculously Large",
                                            wx.ITEM_RADIO)
        self.smViewZoom.Append(self.miViewZoomXLarge)
        parent.Bind(wx.EVT_MENU, lambda e, CellSz = XLG_CELL_SZ: self.on_view_zoom(e, CellSz),
                    self.miViewZoomXLarge)
        if DEFAULT_CELL_SZ == XLG_CELL_SZ:
            self.miViewZoomXLarge.Check(True)

        self.mView.AppendSeparator()

        self.miViewCandsUnselVis = wx.MenuItem(self.mPuzzle, wx.ID_ANY,
                                               "Unselected Candidates Visible",
                                               "Show unselected Candidates in unfilled cells",
                                               wx.ITEM_CHECK)
        self.mView.Append(self.miViewCandsUnselVis)
        parent.Bind(wx.EVT_MENU, self.on_view_cands_unsel_vis, self.miViewCandsUnselVis)
        self.miViewCandsUnselVis.Check(False)

        # Options Menu
        self.mOptions = wx.Menu()
        self.Append(self.mOptions, "&Options")

        self.smOptionLvl = wx.Menu()
        self.mOptions.AppendSubMenu(self.smOptionLvl, "Generate Expertise &Level Request")

        self.miOptionLvlBeginner = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Beginner",
                                               "Beginner level of expertise", wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlBeginner)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_BEGINNER: self.on_option_level(e, lvl),
                    self.miOptionLvlBeginner)
        if LVL_DEFAULT == LVL_BEGINNER:
            self.miOptionLvlBeginner.Check(True)

        self.miOptionLvlNovice = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Novice",
                                             "Novice level of expertise", wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlNovice)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_NOVICE: self.on_option_level(e, lvl),
                    self.miOptionLvlNovice)
        if LVL_DEFAULT == LVL_NOVICE:
            self.miOptionLvlNovice.Check(True)

        self.miOptionLvlIntermediate = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Intermediate",
                                                   "Intermediate level of expertise",
                                                   wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlIntermediate)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_INTERMEDIATE: self.on_option_level(e, lvl),
                    self.miOptionLvlIntermediate)
        if LVL_DEFAULT == LVL_INTERMEDIATE:
            self.miOptionLvlIntemediate.Check(True)

        self.miOptionLvlProficient = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Proficient",
                                                 "Proficient level of expertise",
                                                 wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlProficient)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_PROFICIENT: self.on_option_level(e, lvl),
                    self.miOptionLvlProficient)
        if LVL_DEFAULT == LVL_PROFICIENT:
            self.miOptionLvlProficient.Check(True)

        self.miOptionLvlAccomplished = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Accomplished",
                                                   "Accomplished level of expertise",
                                                   wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlAccomplished)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_ACCOMPLISHED: self.on_option_level(e, lvl),
                    self.miOptionLvlAccomplished)
        if LVL_DEFAULT == LVL_ACCOMPLISHED:
            self.miOptionLvlAccomplished.Check(True)

        self.miOptionLvlExpert = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Expert",
                                             "Expert level of expertise",
                                             wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlExpert)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_EXPERT: self.on_option_level(e, lvl),
                    self.miOptionLvlExpert)
        if LVL_DEFAULT == LVL_EXPERT:
            self.miOptionLvlExpert.Check(True)

        self.miOptionLvlGuru = wx.MenuItem(self.smOptionLvl, wx.ID_ANY, "&Guru",
                                           "Guru level of expertise", wx.ITEM_RADIO)
        self.smOptionLvl.Append(self.miOptionLvlGuru)
        parent.Bind(wx.EVT_MENU, lambda e, lvl = LVL_GURU: self.on_option_level(e, lvl),
                    self.miOptionLvlGuru)
        if LVL_DEFAULT == LVL_GURU:
            self.miOptionLvlGuru.Check(True)

        self.smOptionSym = wx.Menu()
        self.mOptions.AppendSubMenu(self.smOptionSym, "Grid &Symmetry")

        self.miOptionSymRand = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "&Random",
                                           "Generate puzzle with random symmetry",
                                           wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymRand)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_RAND: self.on_option_symmetry(e, sym),
                    self.miOptionSymRand)
        if SYM_DEFAULT == SYM_RAND:
            self.miOptionSymRand.Check(True)

        self.miOptionSymDihedral = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "&Dihedral",
                                               "Generate puzzle with dihedral (8 point) symmetry",
                                               wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDihedral)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_DIHEDRAL: self.on_option_symmetry(e, sym),
                    self.miOptionSymDihedral)
        if SYM_DEFAULT == SYM_DIHEDRAL:
            self.miOptionSymDihedral.Check(True)

        self.miOptionSymSqQuadRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY,
                                                "&Square Quadrant Rotated",
                                                "Generate puzzle with square quadrants "
                                                "rotated by 90 degrees (4 point) symmetry",
                                                wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymSqQuadRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_SQ_QUAD_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymSqQuadRot)
        if SYM_DEFAULT == SYM_SQ_QUAD_ROT:
            self.miOptionsSymSqQuadRot.Check(True)

        self.miOptionSymSqQuadMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY,
                                                "S&quare Quadrant Mirrored",
                                                "Generate puzzle with mirrored quadrants "
                                                "(4 point) symmetry",
                                                wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymSqQuadMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_SQ_QUAD_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymSqQuadMrd)
        if SYM_DEFAULT == SYM_SQ_QUAD_MRD:
            self.miOptionsSymSqQuadMrd.Check(True)

        self.miOptionSymDgQuadRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY,
                                                "&Diagonal Quadrant Rotated",
                                                "Generate puzzle with diagonal quadrants "
                                                "rotated by 90 degrees (4 point) symmetry",
                                                wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgQuadRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_DG_QUAD_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgQuadRot)
        if SYM_DEFAULT == SYM_DG_QUAD_ROT:
            self.miOptionsSymDgQuadRot.Check(True)

        self.miOptionSymDgQuadMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY,
                                                "D&iagonal Quadrant Mirrored",
                                                "Generate puzzle with diagonal "
                                                "mirrored quadrants (4 point) symmetry",
                                                wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgQuadMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_DG_QUAD_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgQuadMrd)
        if SYM_DEFAULT == SYM_DG_QUAD_MRD:
            self.miOptionsSymDgQuadMrd.Check(True)

        self.miOptionSymVertRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "&Vertical Rotated",
                                              "Generate puzzle with vertical halves rotated "
                                              "by 180 degrees",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymVertRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_VERT_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymVertRot)
        if SYM_DEFAULT == SYM_VERT_ROT:
            self.miOptionSymVertRot.Check(True)

        self.miOptionSymVertMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "V&ertical Mirrored",
                                              "Generate puzzle with vertical halves mirrored",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymVertMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_VERT_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymVertMrd)
        if SYM_DEFAULT == SYM_VERT_MRD:
            self.miOptionSysVertMrd.Check(True)

        self.miOptionSymHorzRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "&Horizontal Rotated",
                                              "Generate puzzle with horizontal halves rotated "
                                              "by 180 degrees",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymHorzRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_HORZ_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymHorzRot)
        if SYM_DEFAULT == SYM_HORZ_ROT:
            self.miOptionHorzRot.Check(True)

        self.miOptionSymHorzMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "H&orizontal Mirrored",
                                              "Generate puzzle with horizontal halves mirrored",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymHorzMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_HORZ_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymHorzMrd)
        if SYM_DEFAULT == SYM_HORZ_MRD:
            self.miOptionSymHorzMrd.Check(True)

        self.miOptionSymDgTlRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "&Diagonal Top Left Rotated",
                                              "Generate puzzle with diagonal top left halves rotated "
                                              "by 180 degrees (2 point) symmetry",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgTlRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_VERT_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgTlRot)
        if SYM_DEFAULT == SYM_DGTL_ROT:
            self.miOptionSymDgTlRot.Check(True)

        self.miOptionSymDgTlMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "Di&agonal Top Left Mirrored",
                                              "Generate puzzle with diagonal top left halves mirrored "
                                              "(2 point) symmetry",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgTlMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_VERT_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgTlMrd)
        if SYM_DEFAULT == SYM_DGTL_MRD:
            self.miOptionSysDgTlMrd.Check(True)

        self.miOptionSymDgBlRot = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "Dia&gonal Bottom Left Rotated",
                                              "Generate puzzle with diagonal bottom left halves rotated "
                                              "by 180 degrees (2 point) symmetry",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgBlRot)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_HORZ_ROT: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgBlRot)
        if SYM_DEFAULT == SYM_DGBL_ROT:
            self.miOptionDgBlRot.Check(True)

        self.miOptionSymDgBlMrd = wx.MenuItem(self.smOptionSym, wx.ID_ANY, "Diag&onal Bottom Left Mirrored",
                                              "Generate puzzle with diagonal bottom left halves mirrored "
                                              "(2 point) symmetry",
                                              wx.ITEM_RADIO)
        self.smOptionSym.Append(self.miOptionSymDgBlMrd)
        parent.Bind(wx.EVT_MENU, lambda e, sym = SYM_HORZ_MRD: self.on_option_symmetry(e, sym),
                    self.miOptionSymDgBlMrd)
        if SYM_DEFAULT == SYM_HORZ_MRD:
            self.miOptionSymDgBlMrd.Check(True)

        self.smOptionAssist = wx.Menu()
        self.mOptions.AppendSubMenu(self.smOptionAssist, "&Value Assistance")

        self.miOptionAssistFinCheck = wx.MenuItem(self.smOptionAssist, wx.ID_ANY,
                                                  "&Check On Finish",
                                                  "On completion, advise correct or not, "
                                                  "No cell value conflicts or errors shown.",
                                                  wx.ITEM_RADIO)
        self.smOptionAssist.Append(self.miOptionAssistFinCheck)
        parent.Bind(wx.EVT_MENU, lambda e, ast = AST_FIN_CHECK: self.on_option_assist(e, ast),
                    self.miOptionAssistFinCheck)
        if AST_DEFAULT == AST_FIN_CHECK:
            self.miOptionAssistFinCheck.Check(True)

        self.miOptionAssistFinCnflts = wx.MenuItem(self.smOptionAssist, wx.ID_ANY,
                                                   "&Show Conflicts On Finish",
                                                   "Only show cell value conficts on completion.",
                                                   wx.ITEM_RADIO)
        self.smOptionAssist.Append(self.miOptionAssistFinCnflts)
        parent.Bind(wx.EVT_MENU, lambda e, ast = AST_FIN_CNFLTS: self.on_option_assist(e, ast),
                    self.miOptionAssistFinCnflts)
        if AST_DEFAULT == AST_FIN_CNFLTS:
            self.miOptionAssistFinCnflts.Check(True)

        self.miOptionAssistFinErrs = wx.MenuItem(self.smOptionAssist, wx.ID_ANY,
                                                 "&Show Errors On Finish",
                                                 "Only show cell value errors on completion.",
                                                 wx.ITEM_RADIO)
        self.smOptionAssist.Append(self.miOptionAssistFinErrs)
        parent.Bind(wx.EVT_MENU, lambda e, ast = AST_FIN_ERRORS: self.on_option_assist(e, ast),
                    self.miOptionAssistFinErrs)
        if AST_DEFAULT == AST_FIN_ERRORS:
            self.miOptionAssistFinErrs.Check(True)

        self.miOptionAssistCnflts = wx.MenuItem(self.smOptionAssist, wx.ID_ANY,
                                                "S&how Conflicts",
                                                "Interactactively show cell value conflicts.",
                                                wx.ITEM_RADIO)
        self.smOptionAssist.Append(self.miOptionAssistCnflts)
        parent.Bind(wx.EVT_MENU, lambda e, ast = AST_CNFLTS: self.on_option_assist(e, ast),
                    self.miOptionAssistCnflts)
        if AST_DEFAULT == AST_CNFLTS:
            self.miOptionAssistCnflts.Check(True)

        self.miOptionAssistErrors = wx.MenuItem(self.smOptionAssist, wx.ID_ANY,
                                                "&Show Errors",
                                                "Interactively show cell value errors.",
                                                wx.ITEM_RADIO)
        self.smOptionAssist.Append(self.miOptionAssistErrors)
        parent.Bind(wx.EVT_MENU, lambda e, ast = AST_ERRORS: self.on_option_assist(e, ast),
                    self.miOptionAssistErrors)
        if AST_DEFAULT == AST_ERRORS:
            self.miOptionAssistErrors.Check(True)

        self.miOptionAssistCands = wx.MenuItem(self.mOptions, wx.ID_ANY,
                                               "&Candidate Assistance",
                                               "Hides shown peer candidates when values "
                                               "are entered.",
                                               wx.ITEM_CHECK)
        self.mOptions.Append(self.miOptionAssistCands)
        parent.Bind(wx.EVT_MENU, self.on_option_assist_cands, self.miOptionAssistCands)
        self.miOptionAssistCands.Check(AST_CANDS_DEFAULT)

        # Help Menu
        self.mHelp = wx.Menu()
        self.Append(self.mHelp, "&Help")

        self.miHelpAbout = wx.MenuItem(self.mHelp, wx.ID_ANY, "&About",
                                       "About %s"%TITLE, wx.ITEM_NORMAL)
        self.mHelp.Append(self.miHelpAbout)
        parent.Bind(wx.EVT_MENU, self.on_help_about, self.miHelpAbout)

        self.miHelpGuide = wx.MenuItem(self.mHelp, wx.ID_ANY, "&User Guide",
                                       "About %s"%TITLE, wx.ITEM_NORMAL)
        self.mHelp.Append(self.miHelpGuide)
        parent.Bind(wx.EVT_MENU, self.on_help_guide, self.miHelpGuide)

        # Which menu items are enabled in which non-interim (async) states
        #                                           IDLE,  ENTER, SOLVE, PAUSE
        self.MIS = {self.miPuzzleGenerate:        [True,  False, False, False],
                    self.miPuzzleEnter:           [True,  True,  False, False],
                    self.miPuzzleOpen:            [True,  False, False, False],
                    self.miPuzzleScramble:        [False, True,  False, False],
                    self.miPuzzleMinimalise:      [False, True,  False, False],
                    self.miPuzzleSave:            [False, True,  True,  False],
                    self.miPuzzleCandsShow:       [False, False, True,  False],
                    self.miPuzzlePause:           [False, False, True,  True],
                    self.miPuzzleHintVague:       [False, False, True,  False],
                    self.miPuzzleHintClearer:     [False, False, True,  False],
                    self.miPuzzleHintClearest:    [False, False, True,  False],
                    self.miPuzzleListSoln:        [False, False, True,  False],
                    self.miPuzzleRestart:         [False, False, True,  False],
                    self.miPuzzleRestartGO:       [False, False, True,  False],
                    self.miPuzzleGiveUp:          [False, False, True,  False],
                    self.miPuzzleExit:            [True,  True,  True,  False],
                    self.miViewZoomTiny:          [True,  True,  True,  False],
                    self.miViewZoomSmall:         [True,  True,  True,  False],
                    self.miViewZoomNormal:        [True,  True,  True,  False],
                    self.miViewZoomLarge:         [True,  True,  True,  False],
                    self.miViewZoomXLarge:        [True,  True,  True,  False],
                    self.miViewCandsUnselVis:     [False, False, True,  False],
                    self.miOptionLvlBeginner:     [True,  False, False, False],
                    self.miOptionLvlNovice:       [True,  False, False, False],
                    self.miOptionLvlIntermediate: [True,  False, False, False],
                    self.miOptionLvlProficient:   [True,  False, False, False],
                    self.miOptionLvlAccomplished: [True,  False, False, False],
                    self.miOptionLvlExpert:       [True,  False, False, False],
                    self.miOptionLvlGuru:         [True,  False, False, False],
                    self.miOptionSymRand:         [True,  False, False, False],
                    self.miOptionSymDihedral:     [True,  False, False, False],
                    self.miOptionSymSqQuadRot:    [True,  False, False, False],
                    self.miOptionSymSqQuadMrd:    [True,  False, False, False],
                    self.miOptionSymDgQuadRot:    [True,  False, False, False],
                    self.miOptionSymDgQuadMrd:    [True,  False, False, False],
                    self.miOptionSymVertRot:      [True,  False, False, False],
                    self.miOptionSymVertMrd:      [True,  False, False, False],
                    self.miOptionSymHorzRot:      [True,  False, False, False],
                    self.miOptionSymHorzMrd:      [True,  False, False, False],
                    self.miOptionSymDgTlRot:      [True,  False, False, False],
                    self.miOptionSymDgTlMrd:      [True,  False, False, False],
                    self.miOptionSymDgBlRot:      [True,  False, False, False],
                    self.miOptionSymDgBlMrd:      [True,  False, False, False],
                    self.miOptionAssistFinCheck:  [True,  True,  True,  False],
                    self.miOptionAssistFinCnflts: [True,  True,  True,  False],
                    self.miOptionAssistFinErrs:   [True,  True,  True,  False],
                    self.miOptionAssistCnflts:    [True,  True,  True,  False],
                    self.miOptionAssistErrors:    [True,  True,  True,  False],
                    self.miOptionAssistCands:     [True,  True,  True,  False],
                    self.miHelpAbout:             [True,  True,  True,  True],
                    self.miHelpGuide:             [True,  True,  True,  True]}

    def enable_menuitems(self, e):
        for mi, en in self.MIS.items():
            mi.Enable(en[e])

    def on_puzzle_generate(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_GEN)

    def on_puzzle_enter(self, e):
        if self.miPuzzleEnter.IsChecked():
            self.Parent.Sudoku.gen_event(EV_SC_ENT, True)
        else:
            self.Parent.Sudoku.gen_event(EV_SC_VLD)

    def on_puzzle_open(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_LD)

    def on_puzzle_scramble(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_SCR)

    def on_puzzle_minimalise(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_MIN)

    def on_puzzle_save(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_SV)

    def on_puzzle_cands_show(self, e):
        if self.miPuzzleCandsShow.IsChecked():
            self.Parent.Sudoku.gen_event(EV_SC_CND, True)
        else:
            self.Parent.Sudoku.gen_event(EV_SC_CND, False)

    def on_puzzle_pause(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_PSE, self.miPuzzlePause.IsChecked())

    def on_puzzle_hint(self, e, hint):
        self.Parent.Sudoku.gen_event(EV_SC_HNT, hint)

    def on_puzzle_list_solution(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_LSN)

    def on_puzzle_restart(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_RST, GO = False)

    def on_puzzle_restart_go(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_RST, GO = True)

    def on_puzzle_give_up(self, e):
        self.Parent.Sudoku.gen_event(EV_SC_FIN, True)  # cleanup is true

    def on_puzzle_exit(self, e):
        self.Parent.on_exit(e)

    def on_view_zoom(self, e, sz):
        self.Parent.Board.resize(sz)

    def on_view_cands_unsel_vis(self, e):
        self.Parent.Board.unsel_cands_visibility(self.miViewCandsUnselVis.IsChecked())

    def on_option_level(self, e, lvl):
        self.Parent.Sudoku.set_expertise_req_lvl(lvl)

    def on_option_symmetry(self, e, sym):
        self.Parent.Sudoku.set_symmetry(sym)

    def on_option_assist(self, e, ast):
        self.Parent.Sudoku.set_assistance(ast)

    def on_option_assist_cands(self, e):
        self.Parent.Sudoku.set_assist_cands(self.miOptionAssistCands.IsChecked())

    @staticmethod
    def on_help_about(e):
        wx.MessageBox(TITLE+"\n\n"+ BLURB + "\n\n" + VERSION, " Help About", wx.OK)

    def on_help_guide(self, e):
        dlgUserGuide = UserGuide(self)
        dlgUserGuide.Show()
