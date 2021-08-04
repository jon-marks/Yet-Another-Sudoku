"""
board.py:  Man machine graphical front end, input and output

Description:
    Provides the Board class which provides the man machine interface
    for the puzzle.  The Board class draws the board, displays the values
    and manages all user input that is not menu related.

    Note:  wx.Window is favoured over wx.Panel.  This is because wx.Panel
    appears to block wx.EVT_CHAR events wx.Window does not filter these events.
    See:
    https://stackoverflow.com/questions/51977015/evt-char-never-calls-handler

Audit:
    2021-04-xx  jm  Initial Entry

"""

import wx
from copy import copy, deepcopy

from globals import *

# GC_FLAG bits
GCF_SEL    = 0x0001  # Cell selected
GCF_GRP_HL = 0x0002  # Part of transient group highlight

# grid cell attributes
GC_SHOW     = 0  # What is being displayed - assumes CVS_* enums from
                 # globals.py, which also is the index to the cell_fg_clr.
                 # through CVS_CLRS[]
GC_FRM_WIN  = 1  # Cell frame window object where the selected frame is indicated
GC_CELL_WIN = 2  # Cell window - the inside window of the selection frame
GC_FLAGS    = 3  # Cell is selected or not.
GC_VAL      = 4  # Cell value (0 = blank)
GC_BGI      = 5  # Index to the background colour in BG_CLRS[]
GC_STC      = 6  # Cell StaticText control
GC_CAND     = 7  # The 3x3 matrix of candidate attributes

# Candidate attributes
CD_SEL = 0  # Candidate selected when true
CD_BGI = 1  # Background colour index to BG_CLRS[]
CD_STC = 2  # Static text control

# Background colour selector for cell or candidate enum
BG_CELL = 0
BG_CAND = 1

class BgClrPkrPopup(wx.PopupTransientWindow):
    # Background colour picker popup.  Used to select the background colour for
    # a selected cell or candidate.

    # def __init__(self, parent, creator, t, r, c):
    #     wx.PopupTransientWindow.__init__(self, parent, wx.BORDER_NONE)
    def __init__(self, FrmWin, Board, t, r, c):
        # t = type of popup, either for a cell or a cand. (BG_CELL or BG_CAND)

        wx.PopupTransientWindow.__init__(self, FrmWin, wx.BORDER_NONE)

        Szr0 = wx.BoxSizer(wx.VERTICAL)
        Pnl = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition,
                       wx.Size(BG_CLR_PKR_WIDTH, -1), wx.BORDER_SIMPLE)
        Pnl.SetBackgroundColour(BLACK)
        Szr0.Add(Pnl, 0, wx.ALL, 1)
        self.SetSizer(Szr0)
        Szr = wx.BoxSizer(wx.VERTICAL)
        Btn = [wx.Button(Pnl, wx.ID_ANY, "", wx.DefaultPosition,
                         wx.Size(BG_CLR_PKR_WIDTH, BG_CLR_PKR_BTN_HT),
                         wx.BORDER_NONE)
               for b in BG_CLRS]
        for i, Clr in enumerate(BG_CLRS):
            Szr.Add(Btn[i], 0, wx.ALL, 1)
            if t == BG_CELL:
                Btn[i].Bind(wx.EVT_LEFT_DOWN, lambda e, ci = i, Board = Board:
                            self.on_pick_cell_bg_clr(e, ci, Board))
            else:
                Btn[i].Bind(wx.EVT_LEFT_DOWN, lambda e, ci = i, Board = Board:
                            self.on_pick_cand_bg_clr(e, ci, Board, r, c))

            Btn[i].SetBackgroundColour(Clr)
            Pnl.SetSizer(Szr)

        Szr.Fit(Pnl)
        Szr0.Fit(self)
        self.Layout()

    def on_pick_cell_bg_clr(self, e, ci, Board):
        for r, c in Board.Sudoku.SelList:
            C = Board.Cell[r][c]
            C[GC_BGI] = ci  # VAL][VL_BG] = BG_CLRS[ci]
            C[GC_STC].SetBackgroundColour(BG_CLRS[ci])
            C[GC_STC].ClearBackground()
            C[GC_STC].SetLabel("")
            if C[GC_VAL]:
                C[GC_STC].SetLabel(str(C[GC_VAL]))
            i = 0
            for r1 in range(3):
                for c1 in range(3):
                    i += 1
                    D = C[GC_CAND][r1][c1]
                    if D[CD_BGI] == BG_CLR_DEFAULT:  # Cell BG colour shines through
                        if not (D[CD_SEL] or Board.UnselCandVisible):
                            D[CD_STC].SetForegroundColour(BG_CLRS[ci])
                        D[CD_STC].SetBackgroundColour(BG_CLRS[ci])
                        D[CD_STC].ClearBackground()
                        D[CD_STC].SetLabel("")
                        D[CD_STC].SetLabel(str(i))

            if C[GC_SHOW] != CVS_CANDS:
                for r1 in range(3):
                    for c1 in range(3):
                        C[GC_CAND][r1][c1][CD_STC].Hide()
                C[GC_STC].Show()
            else:
                C[GC_STC].Hide()
                for r1 in range(3):
                    for c1 in range(3):
                        C[GC_CAND][r1][c1][CD_STC].Show()
        wx.CallAfter(self.Destroy)

    def on_pick_cand_bg_clr(self, e, ci, cr, r, c):
        C = Board.Cell[r//3][c//3]
        D = C[GC_CAND][r%3][c%3]
        D[CD_BGI] = ci
        if ci == BG_CLR_DEFAULT:  # candidate inherits cell's bg clr.
            D[CD_STC].SetBackgroundColour(BG_CLRS[C[GC_BGI]])
        else:
            D[CD_STC].SetBackgroundColour(BG_CLRS[ci])
        D[CD_STC].ClearBackground()
        if D[CD_SEL] or Board.UnselCandVisible:
            lbl = D[CD_STC].GetLabelText()
            D[CD_STC].SetLabel("")
            D[CD_STC].SetLabel(lbl)
        wx.CallAfter(self.Destroy)

class Board:

    # TODO document this class.
    # Note:
    # 1.  Regarding mouse events:
    #   a.  Left mouse button ==> cell selection and operations
    #   b.  Right mouse button ==> candidate selection and operations

    def __init__(self, MainWindow, Sudoku, CellSz = DEFAULT_CELL_SZ):
#        self.Parent = parent
        self.MainWindow = MainWindow
        self.Sudoku     = Sudoku
        # Setup the main cell array structure
        self.Cell = [[{GC_SHOW:     CVS_EMPTY,
                       GC_FRM_WIN:  None,
                       GC_CELL_WIN: None,
                       GC_FLAGS:    0,  # No flags set
                       GC_VAL:      0,
                       GC_BGI:      BG_CLR_DEFAULT,
                       GC_STC:      None,
                       GC_CAND:     [[{CD_SEL: False,
                                       CD_BGI: BG_CLR_DEFAULT,
                                       CD_STC: None
                                       } for c1 in range(3)] for r1 in range(3)]
                       } for c in range(9)] for r in range(9)]
        self.BgClrPkr = None
        self.UnselCandVisible = False

        self.BrdSz = 2*(BOARD_BDR+BLOCK_BDR)+6*CELL_BDR+18*CELL_FRM_BDR+9*CellSz
        CellFontPt = CellSz*PT2PXR*V_FT_SCL
        CandSz = CellSz/3
        CandFontPt = CandSz*PT2PXR*C_FT_SCL

        self.HighlightGroup = False
        self.CellFont = wx.Font(CellFontPt, FONT_FAM, CELL_FONT_ST, CELL_FONT_WT, CELL_FONT_UL, FONT)
        self.CandFont = wx.Font(CandFontPt, FONT_FAM, CAND_FONT_ST, CAND_FONT_WT, CAND_FONT_UL, FONT)
        self.CandBold = wx.Font(CandFontPt, FONT_FAM, CAND_FONT_ST, wx.FONTWEIGHT_BOLD, CAND_FONT_UL, FONT)
        self.CellFont.SetFractionalPointSize(CellFontPt)
        self.CandFont.SetFractionalPointSize(CandFontPt)
        self.CandBold.SetFractionalPointSize(CandFontPt)
        # Draw the sudoku board
        # Frame sizer in the main window frame,into which the grid is stacked.
        FrmSzr = wx.GridSizer(1, 1, 0, 0)
        MainWindow.SetSizer(FrmSzr)

        # The purpose of this lowest frame panel in the stack is to force
        # the frame to the grid size and provide the outermost frame border
        # of the grid.
        self.FrmWin = wx.Window(MainWindow,
                                wx.ID_ANY,
                                wx.DefaultPosition,
                                wx.Size(self.BrdSz, self.BrdSz),
                                wx.BORDER_NONE)
        self.FrmWin.Hide()

        self.FrmWin.Bind(wx.EVT_CHAR, self.on_char_frm_win)
        self.FrmWin.SetBackgroundColour(BOARD_BDR_CLR)
        FrmSzr.Add(self.FrmWin, 0, wx.EXPAND, 0)

        self.PausedSTC = wx.StaticText(self.FrmWin,
                                       wx.ID_ANY,
                                       "",
                                       wx.Point(0, 0),
                                       wx.Size(self.BrdSz, self.BrdSz),
                                       wx.ALIGN_CENTRE_HORIZONTAL
                                       |wx.ST_NO_AUTORESIZE
                                       |wx.BORDER_NONE)
        self.PausedSTC.SetFont(wx.Font(100, FONT_FAM, CELL_FONT_ST,
                                       CELL_FONT_WT, CELL_FONT_UL, FONT))
        self.PausedSTC.SetForegroundColour(GREY)
        self.PausedSTC.SetBackgroundColour(LT_GREY)
        self.PausedSTC.SetLabel("\nPaused")
        self.PausedSTC.Hide()

        # The Base sizer is used to size the base panel on top of the frame
        # panel.
        BaseSzr = wx.GridSizer(1, 1, 0, 0)
        self.FrmWin.SetSizer(BaseSzr)

        # The base panel is stacked on the frame panel inset by GRID_BDR pixels
        # all around.
        self.BaseWin = wx.Window(self.FrmWin,
                                 wx.ID_ANY,
                                 wx.DefaultPosition,
                                 wx.DefaultSize,
                                 wx.BORDER_NONE)
        self.BaseWin.SetBackgroundColour(BOARD_BDR_CLR)
        BaseSzr.Add(self.BaseWin, 0, wx.ALL | wx.EXPAND, BOARD_BDR)

        # Into the base panel we place the block sizer - a 3x3 matrix of blocks
        # with BLOCK_BDR gaps between the blocks.
        BlkMatrixSzr = wx.GridSizer(3, 3, BLOCK_BDR, BLOCK_BDR)
        self.BaseWin.SetSizer(BlkMatrixSzr)

        # Each block panel in the 3 x 3 matrix of blocks provides the
        # backdrop onto which the Sudoku cells in that block are built
        self.BlkWin = [[wx.Window(self.BaseWin,
                                  wx.ID_ANY,
                                  wx.DefaultPosition,
                                  wx.DefaultSize,
                                  wx.BORDER_NONE) for bc in range(3)] for rc in range(3)]
        for br in range(3):
            for bc in range(3):
                B = self.BlkWin[br][bc]
                B.SetBackgroundColour(CELL_BDR_CLR)
                BlkMatrixSzr.Add(B, 0, wx.EXPAND, 0)

                # In each block panel a 3 x 3 matrix of cells are built, first
                # by defining the 3 x 3 GridSizer for the cells
                CellMatrixSzr = wx.GridSizer(3, 3, CELL_BDR, CELL_BDR)
                B.SetSizer(CellMatrixSzr)

                for cbr in range(3):
                    for cbc in range(3):
                        cr = br*3+cbr
                        cc = bc*3+cbc
                        C = self.Cell[cr][cc]

                        # Cells are designed to have a frame.  Create the frame
                        # panel and 'Add' it to the block panel sizer.
                        C[GC_FRM_WIN] = wx.Window(B,  # wx,Panel(B,
                                                  wx.ID_ANY,
                                                  wx.DefaultPosition,
                                                  wx.DefaultSize,
                                                  wx.BORDER_NONE)
                        C[GC_FRM_WIN].SetBackgroundColour(BG_CLRS[BG_CLR_DEFAULT])
                        CellMatrixSzr.Add(C[GC_FRM_WIN], 0, wx.EXPAND, 0)
                        C[GC_FRM_WIN].Bind(wx.EVT_LEFT_DOWN,
                                           lambda e, r = cr, c = cc:
                                           self.on_mse_left_down(e, r, c))
                        C[GC_FRM_WIN].Bind(wx.EVT_LEFT_UP,
                                           lambda e, r = cr, c = cc:
                                           self.on_mse_left_up(e, r, c))

                        # create a sizer in the 'cell frame panel' for the
                        # 'cell panel'
                        CellWinSzr = wx.GridSizer(1, 1, 0, 0)
                        C[GC_FRM_WIN].SetSizer(CellWinSzr)

                        # Create the Cell window that will either wrap the
                        # value or the 3 x 3 matrix of candidates.  The CellWin
                        # is a parent panel of the ValWin and CandsWin and
                        # children panels.
                        C[GC_CELL_WIN] = wx.Window(C[GC_FRM_WIN],  # wx.Window
                                                   wx.ID_ANY,
                                                   wx.DefaultPosition,
                                                   wx.DefaultSize,
                                                   wx.BORDER_NONE)
                        CellWinSzr.Add(C[GC_CELL_WIN], 0, wx.ALL | wx.EXPAND,
                                       CELL_FRM_BDR)

                        C[GC_STC] = wx.StaticText(C[GC_CELL_WIN],
                                                  wx.ID_ANY,
                                                  "",  # str(C[GC_VAL][VL_VAL]),
                                                  wx.Point(0, 0),
                                                  wx.Size(CellSz, CellSz),
                                                  wx.ALIGN_CENTRE_HORIZONTAL
                                                  |wx.ST_NO_AUTORESIZE
                                                  |wx.BORDER_NONE)
                        C[GC_STC].SetFont(self.CellFont)
                        C[GC_STC].SetForegroundColour(CVS_CLRS[C[GC_SHOW]])
                        C[GC_STC].SetBackgroundColour(BG_CLRS[C[GC_BGI]])
                        C[GC_STC].Bind(wx.EVT_LEFT_DOWN,
                                       lambda e, r = cr, c = cc:
                                       self.on_mse_left_down(e, r, c))
                        C[GC_STC].Bind(wx.EVT_LEFT_UP,
                                       lambda e, r = cr, c = cc:
                                       self.on_mse_left_up(e, r, c))

                        i = 0
                        for r in range(3):
                            for c in range(3):
                                D = C[GC_CAND][r][c]
                                #  Candidate values are not shown by default,
                                #  they only get toggled visible explicitly when
                                #  solving puzzles. The values are hidden by
                                #  setting the foreground colour to the back-
                                #  ground colour.
                                #  Also candidate cells inherit the underlying
                                #  value cell's background colour if its bg clr
                                #  is the default bg clr.                                #  mode.)
                                i += 1
                                D[CD_SEL] = False
                                D[CD_BGI] = BG_CLR_DEFAULT
                                D[CD_STC] = wx.StaticText(C[GC_CELL_WIN],  # CANDS_WIN),
                                                          wx.ID_ANY,
                                                          str(i),
                                                          wx.Point(c*CandSz, r*CandSz),
                                                          wx.Size(CandSz, CandSz),
                                                          wx.ALIGN_CENTRE_HORIZONTAL
                                                          |wx.ST_NO_AUTORESIZE
                                                          |wx.BORDER_NONE)
                                D[CD_STC].SetFont(self.CandFont)
                                D[CD_STC].SetForegroundColour(BG_CLRS[BG_CLR_DEFAULT])
                                D[CD_STC].SetBackgroundColour(BG_CLRS[BG_CLR_DEFAULT])
                                D[CD_STC].Bind(wx.EVT_LEFT_DOWN,
                                               lambda e, r = cr, c = cc:
                                               self.on_mse_left_down(e, r, c))
                                D[CD_STC].Bind(wx.EVT_LEFT_UP,
                                               lambda e, r = cr, c = cc:
                                               self.on_mse_left_up(e, r, c))
                                # For the mse_right_down event, candidate cells are located
                                # in a 27 x 27 array.
                                D[CD_STC].Bind(wx.EVT_RIGHT_DOWN,
                                               lambda e, r = cr*3+r, c = cc*3+c:
                                               self.on_mse_right_down(e, r, c))
                                D[CD_STC].Bind(wx.EVT_RIGHT_UP,
                                               lambda e, r = cr*3+r, c = cc*3+c:
                                               self.on_mse_right_up(e, r, c))
                                D[CD_STC].Hide()
        MainWindow.Layout()
        MainWindow.SetClientSize(self.BrdSz, self.BrdSz)
        MainWindow.Centre(wx.BOTH)
        self.FrmWin.Show()

    def resize(self, CellSz):
        self.BrdSz = 2*(BOARD_BDR+BLOCK_BDR)+6*CELL_BDR+18*CELL_FRM_BDR+9*CellSz
        self.FrmWin.Hide()

        self.FrmWin.SetSize(self.BrdSz, self.BrdSz)

        CellFontPt = CellSz*PT2PXR*V_FT_SCL
        CandSz = CellSz/3
        CandFontPt = CandSz*PT2PXR*C_FT_SCL
        self.CellFont.SetFractionalPointSize(CellFontPt)
        self.CandFont.SetFractionalPointSize(CandFontPt)
        self.CandBold.SetFractionalPointSize(CandFontPt)

        for cr in range(9):
            for cc in range(9):
                C = self.Cell[cr][cc]
                C[GC_STC].SetSize(CellSz, CellSz)
                C[GC_STC].SetFont(self.CellFont)
                for r in range(3):
                    for c in range(3):
                        D = C[GC_CAND][r][c]
                        D[CD_STC].SetPosition(wx.Point(c*CandSz, r*CandSz), )
                        D[CD_STC].SetSize(CandSz, CandSz)
                        D[CD_STC].SetFont(self.CandFont)
        self.MainWindow.Layout()
        self.MainWindow.SetClientSize(self.BrdSz, self.BrdSz)
        self.FrmWin.Show()

    def clear_board(self):
        # Clears the board and underlying structure.
        for cr in range(9):
            for cc in range(9):
                self.select_cell(cr, cc, False)
                C = self.Cell[cr][cc]
                C[GC_FLAGS] = 0  # no flags set.
                C[GC_SHOW] = CVS_EMPTY
                C[GC_VAL] = 0
                C[GC_BGI] = BG_CLR_DEFAULT
                C[GC_STC].SetLabelText("")
                C[GC_STC].SetBackgroundColour(BG_CLRS[BG_CLR_DEFAULT])
                C[GC_STC].ClearBackground()
                C[GC_STC].Show()
                i = 0
                for r in range(3):
                    for c in range(3):
                        i += 1
                        D = C[GC_CAND][r][c]
                        D[CD_SEL] = False
                        D[CD_BGI] = BG_CLR_DEFAULT
                        D[CD_STC].Hide()
                        if self.UnselCandVisible:
                            D[CD_STC].SetForegroundColour(CAND_UNSEL_CLR)
                        else:
                            D[CD_STC].SetForegroundColour(BG_CLRS[BG_CLR_DEFAULT])
                        D[CD_STC].SetBackgroundColour(BG_CLRS[BG_CLR_DEFAULT])
                        D[CD_STC].ClearBackground()
                        D[CD_STC].SetLabelText(str(i))

    def write_cell_value(self, v, r, c, st, cands = None):
        # If cands == None:  that means that Sudoku.ShowCands == False and
        # the cands STC's are shown but with no text..

        C = self.Cell[r][c]
        C[GC_VAL] = v  # Val will be 0 when st == CVS_EMPTY or CVS_CANDS
        if st != CVS_CANDS:
            C[GC_STC].SetForegroundColour(CVS_CLRS[st])
            C[GC_STC].SetLabel("")  # double write required with diff text as
                                    # wx widgets ignores same val writes.
            if v:
                C[GC_STC].SetLabel(str(v))
            else:
                C[GC_STC].SetLabel(" ")
            if C[GC_SHOW] == CVS_CANDS:
                # switch from show cands
                for rd in [0, 1, 2]:
                    for cd in [0, 1, 2]:
                        C[GC_CAND][rd][cd][CD_STC].Hide()
                C[GC_STC].Show()
        else:  # st == CVS_CANDS:
            if C[GC_SHOW] != CVS_CANDS:
                C[GC_STC].Hide()
                C[GC_STC].SetLabel("")

            for rd in [0, 1, 2]:
                for cd in [0, 1, 2]:
                    D = C[GC_CAND][rd][cd]
                    if cands is not None:
                        D[CD_SEL] = cands[rd][cd]
                    else:
                        D[CD_SEL] = False
                    if D[CD_SEL]:
                        D[CD_STC].SetForegroundColour(CAND_PNCL_CLR)
                    else:
                        if self.UnselCandVisible:
                            D[CD_STC].SetForegroundColour(CAND_UNSEL_CLR)
                        elif D[CD_BGI] == BG_CLR_DEFAULT:
                            D[CD_STC].SetForegroundColour(BG_CLRS[C[GC_BGI]])
                        else:
                            D[CD_STC].SetForegroundColour(BG_CLRS[D[CD_BGI]])
                    D[CD_STC].SetLabel("")  # double write with diff value required.
                    D[CD_STC].SetLabel(str(rd*3+cd+1))
                    D[CD_STC].Show()
        C[GC_SHOW] = st


    def select_cell(self, r, c, tf):
        if tf:
            self.Cell[r][c][GC_FLAGS] |= GCF_SEL
            self.Cell[r][c][GC_FRM_WIN].SetBackgroundColour(CELL_SEL_CLR)
        else:
            self.Cell[r][c][GC_FLAGS] &= ~GCF_SEL
            self.Cell[r][c][GC_FRM_WIN].SetBackgroundColour(WHITE)
        self.Cell[r][c][GC_FRM_WIN].ClearBackground()

    def popup_cell_bg_clr_selector(self, r, c):
        self.BgClrPkr = BgClrPkrPopup(self.FrmWin, self, BG_CELL, r, c)
        MseSt = wx.GetMouseState()
        self.BgClrPkr.SetPosition(wx.Point(MseSt.X, MseSt.Y))
        self.BgClrPkr.Popup()

    def popup_cand_bg_clr_selector(self, r, c):
        self.BgClrPkr = BgClrPkrPopup(self.FrmWin, self, BG_CAND, r, c)
        MseSt = wx.GetMouseState()
        self.BgClrPkr.SetPosition(wx.Point(MseSt.X, MseSt.Y))
        self.BgClrPkr.Popup()

    def unsel_cands_visibility(self, tf):
        self.UnselCandVisible = tf
        for r in range(9):
            for c in range(9):
                C = self.Cell[r][c]
                if C[GC_SHOW] == CVS_CANDS:  # Cands are shown, values are hidden
                    i = 0
                    if self.UnselCandVisible:  # Candidates are shown and visible unselected
                        for r1 in range(3):
                            for c1 in range(3):
                                D = C[GC_CAND][r1][c1]
                                i += 1
                                if not D[CD_SEL]:
                                    D[CD_STC].SetForegroundColour(CAND_UNSEL_CLR)
                                D[CD_STC].SetLabel("")
                                D[CD_STC].SetLabel(str(i))
                    else:  # Candidates are shown but no visible unselected
                        for r1 in range(3):
                            for c1 in range(3):
                                D = C[GC_CAND][r1][c1]
                                i += 1
                                if not D[CD_SEL]:
                                    if D[CD_BGI] == BG_CLR_DEFAULT:
                                        D[CD_STC].SetForegroundColour(BG_CLRS[C[GC_BGI]])
                                    else:
                                        D[CD_STC].SetForegroundColour(BG_CLRS[D[CD_BGI]])
                                D[CD_STC].SetLabel("")
                                D[CD_STC].SetLabel(str(i))

    def set_cand_value(self, rc, cc, rd, cd, tf, hl = False):
        if hl:
            FgClr = CVS_CLRS[CVS_SVSHL]
            Font = self.CandBold
        else:
            FgClr = CAND_PNCL_CLR
            Font = self.CandFont

        C = self.Cell[rc][cc]
        D = C[GC_CAND][rd][cd]
        D[CD_SEL] = tf
        if tf:  # candidate chosen.
            D[CD_STC].SetForegroundColour(FgClr)
            D[CD_STC].SetFont(Font)
        elif self.UnselCandVisible:
            D[CD_STC].SetForegroundColour(CAND_UNSEL_CLR)
        elif D[CD_BGI] == BG_CLR_DEFAULT:
            D[CD_STC].SetForegroundColour(BG_CLRS[C[GC_BGI]])
        else:
            D[CD_STC].SetForegroundColour(BG_CLRS[D[CD_BGI]])
        D[CD_STC].SetLabel("")
        D[CD_STC].SetLabel(str(rd*3+cd+1))

    def reset_cand_bg_clrs(self):
        for r in range(9):
            for c in range(9):
                C = self.Cell[r][c]
                for r1 in range(3):
                    for c1 in range(3):
                        D = C[GC_CAND][r1][c1]
                        D[CD_BGI] = BG_CLR_DEFAULT
                        D[CD_STC].SetBackgroundColour(BG_CLRS[C[GC_BGI]])
                        D[CD_STC].ClearBackground()
                        if not (D[CD_SEL] or self.UnselCandVisible):
                            D[CD_STC].SetForegroundColour(BG_CLRS[C[GC_BGI]])
                        lbl = D[CD_STC].GetLabel()
                        D[CD_STC].SetLabel("")
                        D[CD_STC].SetLabel(lbl)

    def hide_puzzle(self, tf):
        # When a game is paused the board needs to be hidden, and made visible again
        # when the game is resumed.
        if tf:  # hide the puzzle by painting the paused STC over it.
            for r in range(9):
                for c in range(9):
                    C = self.Cell[r][c]
                    if C[GC_SHOW] != CVS_CANDS:
                        C[GC_STC].Hide()
                    else:
                        for r1 in range(3):
                            for c1 in range(3):
                                C[GC_CAND][r1][c1][CD_STC].Hide()
            self.PausedSTC.Show()
            self.PausedSTC.Raise()
        else:  # Show the puzzle by hiding the paused STC
            self.PausedSTC.Hide()
            for r in range(9):
                for c in range(9):
                    C = self.Cell[r][c]
                    if C[GC_SHOW] != CVS_CANDS:
                        C[GC_STC].Show()
                    else:
                        for r1 in range(3):
                            for c1 in range(3):
                                C[GC_CAND][r1][c1][CD_STC].Show()

    def group_highlight(self, tf, r, c):
        rb = r//3
        cb = c//3
        if tf:
            for r1 in range(3):
                for c1 in range(3):
                    self.Cell[rb*3+r1][cb*3+c1][GC_FLAGS] |= GCF_GRP_HL
                    _highlight_cell(GRP_HL_TINT, self.Cell[rb*3+r1][cb*3+c1],
                                    self.UnselCandVisible)
            for r1 in range(9):
                if r1//3 != rb:
                    self.Cell[r1][c][GC_FLAGS] |= GCF_GRP_HL
                    _highlight_cell(GRP_HL_TINT, self.Cell[r1][c], self.UnselCandVisible)
            for c1 in range(9):
                if c1//3 != cb:
                    self.Cell[r][c1][GC_FLAGS] |= GCF_GRP_HL
                    _highlight_cell(GRP_HL_TINT, self.Cell[r][c1], self.UnselCandVisible)
        else:
            for r1 in range(9):
                for c1 in range(9):
                    if self.Cell[r1][c1][GC_FLAGS] & GCF_GRP_HL:
                        self.Cell[r1][c1][GC_FLAGS] &= ~GCF_GRP_HL
                        _highlight_cell(0, self.Cell[r1][c1], self.UnselCandVisible)

    # User input event handlers.  Pass them onto the Sudoku module where all the
    # processing takes place.

    def on_mse_left_down(self, e, r, c):
        self.FrmWin.SetFocus()  # Give keyboard focus back to FrmWin.
        KbdMods = e.GetModifiers() & (wx.MOD_ALT | wx.MOD_CONTROL  |wx.MOD_SHIFT)
        self.Sudoku.gen_event(EV_SC_MSE, wx.EVT_LEFT_DOWN, r, c, KbdMods)

    def on_mse_left_up(self, e, r, c):
        self.FrmWin.SetFocus()  # Give keyboard focus back to FrmWin.
        KbdMods = e.GetModifiers() & (wx.MOD_ALT | wx.MOD_CONTROL | wx.MOD_SHIFT)
        self.Sudoku.gen_event(EV_SC_MSE, wx.EVT_LEFT_UP, r, c, KbdMods)

    def on_mse_right_down(self, e, r, c):
        # note that r and c index a 27x27 matrix of candidates.
        self.FrmWin.SetFocus()  # Give keyboard focus back to FrmWin.
        KbdMods = e.GetModifiers() & (wx.MOD_ALT | wx.MOD_CONTROL | wx.MOD_SHIFT)
        self.Sudoku.gen_event(EV_SC_MSE, wx.EVT_RIGHT_DOWN, r, c, KbdMods)

    def on_mse_right_up(self, e, r, c):
        # note that r and c index a 27x27 matrix of candidates.
        self.FrmWin.SetFocus()  # Give keyboard focus back to FrmWin.
        KbdMods = e.GetModifiers() & (wx.MOD_ALT | wx.MOD_CONTROL | wx.MOD_SHIFT)
        self.Sudoku.gen_event(EV_SC_MSE, wx.EVT_RIGHT_UP, r, c, KbdMods)

    def on_char_frm_win(self, e):
        #  Process the wx.EVT_CHAR keypress event.
        Key = e.GetUnicodeKey()
        if Key == wx.WXK_NONE:
            Key = e.GetKeyCode()
        self.Sudoku.gen_event(EV_SC_KBD, Key)

def _highlight_cell(Tint, C, UnselCandVis):
    if C[GC_SHOW] != CVS_CANDS:
        C[GC_STC].SetBackgroundColour(BG_CLRS[C[GC_BGI]].ChangeLightness(100-Tint))
        C[GC_STC].ClearBackground()
        lbl = C[GC_STC].GetLabel()
        C[GC_STC].SetLabel("")
        C[GC_STC].SetLabel(lbl)
    else:  # working with candidate cells.
        for r2 in range(3):
            for c2 in range(3):
                D = C[GC_CAND][r2][c2]
                if D[CD_BGI] == BG_CLR_DEFAULT:
                    D[CD_STC].SetBackgroundColour(BG_CLRS[C[GC_BGI]].ChangeLightness(100-Tint))
                else:
                    D[CD_STC].SetBackgroundColour(BG_CLRS[D[CD_BGI]].ChangeLightness(100-Tint))
                D[CD_STC].ClearBackground()
                lbl = D[CD_STC].GetLabel()
                D[CD_STC].SetLabel("")
                if D[CD_SEL] or UnselCandVis:
                    D[CD_STC].SetLabel(lbl)
