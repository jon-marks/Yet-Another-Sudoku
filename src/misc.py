"""
A brown bag of small classes and functions that do not fit in the functional
context of other files.  Includes functions that handle files, some dialogs and
some non-modal windows eg: list solution and user guide.
"""
import os

import wx.html
import wx.lib.mixins.listctrl as lcmi  # list control mix in
from wx.lib.embeddedimage import PyEmbeddedImage

from globals import *
from solve import Tech
from solve_utils import determine_cands

OP = ["" for i in range(OP_NR_OPS)]
OP[OP_POS]  = "?-"  # Possibility, perhaps something to try
OP[OP_PRES] = "--"  # Presence of candidate / value in cell
OP[OP_ABS]  = "!-"  # Absence of candidate in cell.
OP[OP_EQ]   = "=="  # Presence of only value in cell
OP[OP_NEQ]  = "!="  # Cell cannot assume that value
OP[OP_ASNV] = ":="   # Assign value to cell.
OP[OP_ASNC] = "+="  # Add candidate to cell.
OP[OP_ELIM] = "-="  # Eliminate candidate from cell.
OP[OP_WLK]  = "-"   # Chain weak link.
OP[OP_SLK]  = "="   # Chain strong link.
OP[OP_WSLK] = '~'   # Chain strong masquerading as weak link.
OP[OP_CNT]  = "#"   # Count / number of occurrences
OP[OP_PARO] = "("   # Opening parenthesis
OP[OP_PARC] = ")"   # Closing parenthesis
OP[OP_SETO] = "{"   # Opening set
OP[OP_SETC] = "}"   # Closing set

# import images
SmallUpArrow = PyEmbeddedImage(
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAADxJ"
        "REFUOI1jZGRiZqAEMFGke2gY8P/f3/9kGwDTjM8QnAaga8JlCG3CAJdt2MQxDCAUaOjyjKMp"
        "cRAYAABS2CPsss3BWQAAAABJRU5ErkJggg==")

SmallDnArrow = PyEmbeddedImage(
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAEhJ"
        "REFUOI1jZGRiZqAEMFGke9QABgYGBgYWdIH///7+J6SJkYmZEacLkCUJacZqAD5DsInTLhDR"
        "bcPlKrwugGnCFy6Mo3mBAQChDgRlP4RC7wAAAABJRU5ErkJggg==")

class AWListCtrl(wx.ListCtrl, lcmi.ListCtrlAutoWidthMixin):

    # ListCtrl Class with mixin that automagically adjusts the last column to
    # fit the window width in which it exists.
    def __init__(self, parent, ID, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        lcmi.ListCtrlAutoWidthMixin.__init__(self)

class ListSolnWindow(wx.Dialog, lcmi.ColumnSorterMixin):
    # This class uses the wx.lib.mixin Column Sorter for the sorting of the
    # Statistics List Control

    def __init__(self, Parent):
        sT = Parent.MainWindow.Title + ": Solution"
        wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = sT,
                           pos = wx.DefaultPosition,
                           size = LIST_SOLN_DLG_SZ,
                           style = wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT | wx.RESIZE_BORDER)

        self.Creator = Parent
        self.SetSizeHints(LIST_SOLN_DLG_MIN_SZ, wx.DefaultSize)
        SzrDlg = wx.BoxSizer(wx.VERTICAL)

        # Small up and down arrow images to indicate column sort order in
        # Statistics list control.
        self.ImgList = wx.ImageList(16, 16)
        self.SmlUpIdx = self.ImgList.Add(SmallUpArrow.GetBitmap())
        self.SmlDnIdx = self.ImgList.Add(SmallDnArrow.GetBitmap())

        self.NB = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP)

        self.NBSum = wx.Window(self.NB, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
        SzrNBSum = wx.BoxSizer(wx.VERTICAL)
        self.SumST = wx.StaticText(self.NBSum, wx.ID_ANY, "Summary", wx.DefaultPosition, wx.DefaultSize, 0)
        self.SumLC = AWListCtrl(self.NBSum, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.BORDER_NONE)  # | wx.LC_NO_HEADER)
        self.StatST = wx.StaticText(self.NBSum, wx.ID_ANY, "Statistics", wx.DefaultPosition, wx.DefaultSize, 0)
        self.StatLC = AWListCtrl(self.NBSum, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                 wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.BORDER_NONE)
        SzrNBSum.Add(self.SumST, 0, wx.ALL | wx.EXPAND, 10)
        SzrNBSum.Add(self.SumLC, 1, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        SzrNBSum.Add(self.StatST, 0, wx.ALL | wx.EXPAND, 5)
        SzrNBSum.Add(self.StatLC, 1, wx.ALL | wx.EXPAND, 5)
        self.NBSum.SetSizer(SzrNBSum)

        self.StatLC.SetImageList(self.ImgList, wx.IMAGE_LIST_SMALL)

        self.NB.AddPage(self.NBSum, "Summary Statistics", False)

        self.NBSoln = wx.Window(self.NB, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
        SzrNBSoln = wx.BoxSizer(wx.VERTICAL)
        self.SolnLC = AWListCtrl(self.NBSoln, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                 wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.BORDER_NONE)
        SzrNBSoln.Add(self.SolnLC, 1, wx.ALL | wx.EXPAND, 5)
        self.NBSoln.SetSizer(SzrNBSoln)
        self.NB.AddPage(self.NBSoln, "Solution Path", False)
        self.NB.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_nb_page_change)

        SzrDlg.Add(self.NB, 1, wx.ALL | wx.EXPAND, 5)

        SzrBtns = wx.BoxSizer(wx.HORIZONTAL)
        SzrDlg.Add(SzrBtns, 0, wx.ALIGN_CENTRE, 0)

        self.BtnSlvTo = wx.Button(self, wx.ID_ANY, "Solve to Selected Step", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnSaveStep = wx.Button(self, wx.ID_ANY, "Save Selected Step", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnCopyStep = wx.Button(self, wx.ID_ANY, "Copy Selected Step", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnClose = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnSlvTo.Bind(wx.EVT_BUTTON, self.on_solve_to)
        self.BtnSaveStep.Bind(wx.EVT_BUTTON, self.on_save_step)
        self.BtnCopyStep.Bind(wx.EVT_BUTTON, self.on_copy_step)
        self.BtnClose.Bind(wx.EVT_BUTTON, self.on_close)

        self.BtnSlvTo.Disable()
        self.BtnSaveStep.Disable()
        self.BtnCopyStep.Disable()

        SzrBtns.Add(self.BtnSlvTo, 0, wx.ALIGN_CENTRE, 0)
        SzrBtns.Add(self.BtnSaveStep, 0, wx.ALIGN_CENTRE, 0)
        SzrBtns.Add(self.BtnCopyStep, 0, wx.ALIGN_CENTRE, 0)
        SzrBtns.Add(self.BtnClose, 0, wx.ALIGN_CENTRE, 0)
        SzrDlg.Add((0, 7), 0, 0, 0)  # Add a 7 pixel vertical spacer

        Props = self.Creator.Puzzle.get_props()
        #  Write the summary.
        G = Props.GivensHisto  # [PR_GVNS_HISTO]
        self.SumLC.InsertColumn(0, "Attribute", wx.LIST_FORMAT_LEFT, -1)
        self.SumLC.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, -1)
        self.SumLC.InsertColumn(2, "Comment", wx.LIST_FORMAT_LEFT, -1)
        self.SumLC.Append(["Expertise Level:", EXPS[Props.Expertise], "Highest expertise level required to solve"])
        self.SumLC.Append(["Difficulty:", str(Props.Difficulty), "Accumulated difficulty of all steps"])
        self.SumLC.Append(["Givens:", str(Props.NrGivens),
                           f"[1]={G[0]}, [2]={G[1]}, [3]={G[2]}, [4]={G[3]}, [5]={G[4]},"
                           f"[6]={G[5]}, [7]={G[6]}, [8]={G[7]}, [9]={G[8]}"])
        self.SumLC.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SumLC.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SumLC.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SumLC.SetBackgroundColour(VLT_BLUE)

        x1, y1, x2, y2 = self.SumLC.GetViewRect()
        self.SumLC.SetMinSize(wx.Size(-1, y2-y1))
        self.SumLC.SetMaxSize(wx.Size(-1, y2-y1))

        # Write the stats
        self.StatLC.InsertColumn(0, " ", wx.LIST_FORMAT_RIGHT, -1)
        self.StatLC.InsertColumn(1, "Count", wx.LIST_FORMAT_RIGHT, -1)
        self.StatLC.InsertColumn(2, "Technique", wx.LIST_FORMAT_LEFT, -1)
        self.StatLC.InsertColumn(3, "Level", wx.LIST_FORMAT_LEFT, -1)
        self.StatLC.InsertColumn(4, "Difficulty", wx.LIST_FORMAT_RIGHT, -1)
        self.StatLC.InsertColumn(5, "Score", wx.LIST_FORMAT_RIGHT, -1)
        DM = self.itemDataMap = {}  # self.itemDataMap dict rqd by column sorter mixin

        for i, (Method, HistoStep) in enumerate(Props.StepsHisto.items()):
            Row = [f"{i+1:3d}",
                   f"{HistoStep[HT_NR]:3d}",
                   Tech[Method].Text,
                   EXPS[Tech[Method].Expertise],
                   f"{Tech[Method].Difficulty:6d}",  # HistoStep[HT_DIFF]:6d}",
                   f"{HistoStep[HT_ADIFF]:6d}"
                   ]
            DM[i] = Row
            self.StatLC.InsertItem(i, Row[0], -1)
            self.StatLC.SetItem(i, 1, Row[1])
            self.StatLC.SetItem(i, 2, Row[2])
            self.StatLC.SetItem(i, 3, Row[3])
            self.StatLC.SetItem(i, 4, Row[4])
            self.StatLC.SetItem(i, 5, Row[5])
            self.StatLC.SetItemData(i, i)

        SysFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        DC = wx.ClientDC(self)
        w, h, d, e = DC.GetFullTextExtent("0000000", SysFont)
        self.StatLC.SetColumnWidth(0, w)
        w, h, d, e = DC.GetFullTextExtent("Count0000000", SysFont)
        self.StatLC.SetColumnWidth(1, w)
        self.StatLC.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.StatLC.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        w, h, d, e = DC.GetFullTextExtent("Difficulty0000000", SysFont)
        self.StatLC.SetColumnWidth(4, w)
        w, h, d, e = DC.GetFullTextExtent("Score0000000", SysFont)
        self.StatLC.SetColumnWidth(5, w)
        self.StatLC.SetBackgroundColour(VLT_BLUE)
        lcmi.ColumnSorterMixin.__init__(self, 6)

        # Write the solution path.
        w, h, d, e = DC.GetFullTextExtent("Step000", SysFont)
        self.SolnLC.InsertColumn(0, "Step", wx.LIST_FORMAT_RIGHT, w)
        self.SolnLC.InsertColumn(1, "Technique", wx.LIST_FORMAT_LEFT, -1)
        self.SolnLC.InsertColumn(2, "Diff.", wx.LIST_FORMAT_RIGHT, -1)
        self.SolnLC.InsertColumn(3, "Pattern", wx.LIST_FORMAT_LEFT, -1)
        self.SolnLC.InsertColumn(4, "Outcome", wx.LIST_FORMAT_LEFT, -1)

        for j, Step in enumerate(Props.Steps):  # [PR_STEPS]):
            self.SolnLC.Append([f"{(j+1):d}",
                                Tech[Step.Method].Text,
                                f"{Step.Difficulty:6d}",
                                tkns_to_str(Step.Pattern),
                                tkns_to_str(Step.Outcome),
                                ])

        self.SolnLC.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.SolnLC.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SolnLC.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.SolnLC.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.SolnLC.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        self.SolnLC.SetBackgroundColour(VLT_BLUE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected, self.SolnLC)
        self.ToStep = self.FromStep = 0
        self.SetSizer(SzrDlg)
        self.Layout()
        self.Centre(wx.BOTH)

    def on_close(self, e):
        self.Creator.LSW = None
        wx.CallAfter(self.Destroy)

    def on_nb_page_change(self, e):
        if self.NB.GetSelection() != 1:
            self.BtnSlvTo.Disable()
            self.BtnSaveStep.Disable()
            self.BtnCopyStep.Disable()
        else:
            if self.ToStep != 0:
                self.BtnSlvTo.Enable()
                self.BtnSaveStep.Enable()
                self.BtnCopyStep.Enable()

    def on_item_selected(self, e):
        self.ToStep = e.Index
        self.BtnSlvTo.Enable()
        self.BtnSaveStep.Enable()
        self.BtnCopyStep.Enable()

    def on_save_step(self, e):
        Step = self.Creator.Puzzle.Steps[self.ToStep]
        NrEmpties, Elims = determine_cands(Step.Grid, Step.Cands)
        save_puzzle((self.Creator.PzlDir, self.Creator.PzlFn), PZL(Grid    = Step.Grid,
                                                                   Givens  = self.Creator.Puzzle.Givens,
                                                                   Elims   = Elims,
                                                                   Method  = Step.Method,
                                                                   Pattern = Step.Pattern,
                                                                   Outcome = Step.Outcome
                                                                   ))

    def on_copy_step(self, e):
        Step = self.Creator.Puzzle.Steps[self.ToStep]
        NrEmpties, Elims = determine_cands(Step.Grid, Step.Cands)
        copy_puzzle_to_clipboard(PZL(Grid    = Step.Grid,
                                     Givens  = self.Creator.Puzzle.Givens,
                                     Elims   = Elims,
                                     Method  = Step.Method,
                                     Pattern = Step.Pattern,
                                     Outcome = Step.Outcome
                                     ))

    def on_solve_to(self, e):
        if self.ToStep > self.FromStep:
            self.Creator.gen_event(EV_SC_ASL, self.FromStep, self.ToStep)
            self.FromStep = self.ToStep
        elif self.ToStep < self.FromStep:
            wx.MessageBox("Can't follow the Solution Path backwards",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)

    def GetListCtrl(self):
        return self.StatLC

    def GetSortImages(self):
        return self.SmlDnIdx, self.SmlUpIdx

class UserGuide(wx.Dialog):
    # Simple class to display the user guide written in simple html when created
    # and destroy itself when close is selected.  User guide pops up as a
    # non-modal window.

    def __init__(self, Title):  # , parent):
        wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = Title + ": User Guide",
                           pos = wx.DefaultPosition,
                           size = USER_GUIDE_DLG_SZ,
                           style = wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT | wx.RESIZE_BORDER)
        szr = wx.BoxSizer(wx.VERTICAL)
        self.htc = wx.html.HtmlWindow(self)
        szr.Add(self.htc, 1, wx.ALL | wx.EXPAND, 5)

        self.BtnClose = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnClose.Bind(wx.EVT_BUTTON, self.on_close)
        szr.Add(self.BtnClose, 0, wx.ALIGN_CENTER | wx.TOP, 2)
        szr.Add((0, 7), 0, 0, 0)  # Add a 7 pixel spacer.
        self.htc.LoadFile(os.path.join(os.path.dirname(__file__), "../doc/user_guide.html"))
        self.SetSizer(szr)
        self.Layout()
        self.Centre(wx.BOTH)

    def on_close(self, e):
        wx.CallAfter(self.Destroy)

def open_puzzle(Fp, Pzl):

    dlg = wx.FileDialog(None, message = "Open A Puzzle",
                        defaultDir = Fp[0],
                        defaultFile = Fp[1],
                        wildcard = FILE_WILDCARDS,
                        style = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)

    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None, 0

    Fs = dlg.GetPath()
    dlg.Destroy()
    try:
        with open(Fs, "rt") as f:
            sPzl = f.readline(MAX_SVL_FILE_SIZE)
    except (OSError, IOError):
        return None, 0

    NrFlds = pzl_str_to_pzl(sPzl, Pzl)
    if NrFlds: return os.path.split(Fs), NrFlds
    else: return None, 0

def save_puzzle(Fp, oPzl):

    sG = pzl_to_pzl_str(oPzl)

    dlg = wx.FileDialog(None, message = "Save A Puzzle",
                        defaultDir = Fp[0],
                        defaultFile = Fp[1],
                        wildcard = FILE_WILDCARDS,
                        style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None

    Fs = dlg.GetPath()
    dlg.Destroy()

    try:
        with open(Fs, "wt") as f:
            f.write(sG)
    except (IOError, OSError):
        wx.MessageBox("Error writing file",
                      "Warning",
                      wx.ICON_WARNING | wx.OK)
        return None
    return os.path.split(Fs)

def copy_puzzle_to_clipboard(oPzl):

    sG = pzl_to_pzl_str(oPzl)

    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(wx.TextDataObject(sG))
        wx.TheClipboard.Close()
        return True
    return False

def copy_clipboard_to_pzl(oPzl):

    TDO = wx.TextDataObject()
    if wx.TheClipboard.Open():
        wx.TheClipboard.GetData(TDO)
        wx.TheClipboard.Close()
        sG = TDO.GetText()
        return pzl_str_to_pzl(TDO.GetText(), oPzl)
    return 0

def pzl_str_to_pzl(sPzl, Pzl):

    lG = sPzl.replace("\n", "").split("|")
    lenlG = len(lG)
    Pzl.Grid   = [[0 for c in range(9)] for r in range(9)]
    Pzl.Givens = [[0 for c in range(9)] for r in range(9)]
    if not grid_str_to_grid(lG[0], Pzl.Grid, Pzl.Givens):
        PgmMsg("Invalid Sudoku value puzzle spec format - grid.",
               "Warning",
               wx.ICON_WARNING | wx.OK)
        return 0
    if lenlG >= 2 and lG[1]:
        Pzl.Elims = [[set() for c in range(9)] for r in range(9)]
        for sE in lG[1].split(";"):
            r, c, op, Cands = parse_ccell_phrase(sE)
            if r < 0 or op != OP_ELIM:
                PgmMsg("Invalid Sudoku value puzzle spec format - elims.",
                       "Warning",
                       wx.ICON_WARNING | wx.OK)
                return 0
            Pzl.Elims[r][c] |= Cands
    if lenlG >= 3 and lG[2]:
        for Meth, TInfo in Tech.items():  # m in range(len(T):
            if TInfo.Text == lG[2]:  # Tech[Tx][T_TXT] == lG[2]:
                Pzl.Method = Meth
                break
        # else:
        #     PgmMsg(f"Invalid Sudoku value puzzle spec format - unrecognised method \"{lG[2]}.",
        #            "Warning",
        #            wx.ICON_WARNING | wx.OK)
        #     Pzl.Method = T_UNDEF
    else: Pzl.Method = T_UNDEF
    if lenlG == 5:
        Pzl.Pattern = lG[3]
        Pzl.Outcome = lG[4]
    return lenlG

def pzl_to_pzl_str(oPzl):

    sG = grid_to_grid_str(oPzl.Grid, oPzl.Givens)
    if oPzl.Elims:
        sE = ""
        for r in range(9):
            for c in range(9):
                if oPzl.Elims[r][c]:
                    if sE: sE += ";"
                    sE += f"r{r+1}c{c+1}-="
                    for v in sorted(oPzl.Elims[r][c]):
                        sE += f"{v}"
        sG += f"|{sE}"
    if oPzl.Method != T_UNDEF:
        sG += f"|{Tech[oPzl.Method].Text}"
        sG += f"|{tkns_to_str(oPzl.Pattern)}|{tkns_to_str(oPzl.Outcome)}\n".replace(" ", "").replace(".", "")
    return sG

def parse_ccell_phrase(St):
    # only knows how to parse rycx-=digits, and rycx:=digit
    # note that cands is always returned as a set.

    if St[0] != "r" or St[2] != "c": return -1, -1, -1, -1
    r = int(St[1])-1
    if not 0 <= r <= 8: return -1, -1, -1, -1
    c = int(St[3])-1
    if not 0 <= c <= 8: return -1, -1, -1, -1
    if St[4:6] == "-=":
        op = OP_ELIM
    elif St[4:6] == ":=":
        op = OP_ASNV
    else: return -1, -1, -1, -1
    Cands = set(int(z) for z in St[6:])
    if not Cands: return -1, -1, -1, -1
    if len(Cands) > 1 and op == OP_ASNV: return -1, -1, -1, -1
    return r, c, op, Cands

def grid_str_to_grid(sG, Grid, Givens = None):
    # String is unpacked and values placed in passed empty grid array.  If an empty Givens
    # array is passed, the Givens are placed in that.

    i = rc = 0
    while i < len(sG):
        if rc >= 81: return False
        r = rc//9; c = rc%9
        if sG[i] in ["0", ".", "-"]:
            Grid[r][c] = 0
            if Givens: Givens[r][c] = 0
            i += 1; rc += 1
        elif sG[i] == " ": i += 1
        elif sG[i] == "+":
            if Givens: Givens[r][c] = 0
            Grid[r][c] = int(sG[i+1])
            i += 2; rc += 1
        elif (sG[i]).isdigit():
            if Givens: Givens[r][c] = Grid[r][c] = int(sG[i])
            else: Grid[r][c] = int(sG[i])
            i += 1; rc += 1
        else:
            return False
    return True if rc == 81 else False

def grid_to_grid_str(Grid, Givens = None):

    sG = ""
    for r in range(9):
        for c in range(9):
            if Grid[r][c]:
                if Givens is None: sG += f"{Grid[r][c]}"
                elif Givens[r][c]: sG += f"{Grid[r][c]}"
                else: sG += f"+{Grid[r][c]}"
            else: sG += "0"
    return sG

def tkns_to_str(Tkns):

    St = ""
    for Tkn in Tkns:
        # try:
        if Tkn[0] == P_ROW:
            St += "r"
            for i in range(1, len(Tkn)):
                if isinstance(Tkn[i], int):
                    St += f"{Tkn[i]+1}"
                else:
                    for r in sorted(Tkn[i]):
                        St += f"{r+1}"
        elif Tkn[0] == P_COL:
            St += "c"
            for i in range(1, len(Tkn)):
                if isinstance(Tkn[i], int):
                    St += f"{Tkn[i]+1}"
                else:
                    for c in sorted(Tkn[i]):
                        St += f"{c+1}"
        elif Tkn[0] == P_BOX:
            St += f"b{Tkn[1]+1}"
        elif Tkn[0] == P_OP:
            if Tkn[1] == OP_CNT:
                St += f"{OP[OP_CNT]}{Tkn[2]}"
            else:
                St += f"{OP[Tkn[1]]}"
        elif Tkn[0] == P_VAL:
            for i in range(1, len(Tkn)):
                if isinstance(Tkn[i], int):
                    St += f"{Tkn[i]}"
                else:
                    for v in sorted(Tkn[i]):
                        St += f"{v}"
        elif Tkn[0] == P_SEP:
            St += "; "
        elif Tkn[0] == P_CON:
            St += ","
        elif Tkn[0] == P_END:
            St += "."
    return St

def PgmMsg(Type, Msg, Flags = 4):  # wx.OK = 4 if not provided.
    # Wrapper that will put up a MessageBox if running under wx or
    # prints the message to console.  Only necessary to wrap messages
    # in modules/functions that run in both environments.

    from importlib.util import find_spec
    if find_spec("wx"): return wx.MessageBox(Type, Msg, Flags)
    else: print(f"{Type}: {Msg}"); return 4


# def flist(hl):
#     fl = []  # list()
#     for i in hl:
#         if isinstance(i, list):
#             fl.extend(flist(i))
#         else:
#             fl.append(i)
#     return fl
