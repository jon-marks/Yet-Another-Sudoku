"""
A brown bag of small classes and functions that do not fit in the functional
context of other files.  Includes functions that handle files, some dialogs and
some non modal windows eg:eg list solution and user guide.

"""
import os
import wx
import wx.html
import wx.lib.mixins.listctrl as lcmi  # list control mix in
from wx.lib.embeddedimage import PyEmbeddedImage


from globals import *
from solve_utils import *

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

#import images
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
        if Parent.PzlFn != "":
            T = "Yet Another Sudoku Solution" + " - " + Parent.PzlFn
        else:
            T = "Yet Another Sudoku Solution"
        wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = T,
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
        self.BtnClose = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnSlvTo.Bind(wx.EVT_BUTTON, self.on_solve_to)
        self.BtnSaveStep.Bind(wx.EVT_BUTTON, self.on_save_step)
        self.BtnClose.Bind(wx.EVT_BUTTON, self.on_close)

        self.BtnSlvTo.Disable()
        self.BtnSaveStep.Disable()

        SzrBtns.Add(self.BtnSlvTo, 0, wx.ALIGN_CENTRE, 0)
        SzrBtns.Add(self.BtnSaveStep, 0, wx.ALIGN_CENTRE, 0)
        SzrBtns.Add(self.BtnClose, 0, wx.ALIGN_CENTRE, 0)
        SzrDlg.Add((0, 7), 0, 0, 0)  # Add a 7 pixel vertical spacer

        Props = self.Creator.Props
        #  Write the summary.
        G = Props[PR_GVN_HISTO]
        self.SumLC.InsertColumn(0, "Attribute", wx.LIST_FORMAT_LEFT, -1)
        self.SumLC.InsertColumn(1, "Value", wx.LIST_FORMAT_RIGHT, -1)
        self.SumLC.InsertColumn(2, "Comment", wx.LIST_FORMAT_LEFT, -1)
        self.SumLC.Append(["Expertise Level:", LVLS[Props[PR_ACT_LVL]], "Highest expertise level required to solve"])
        self.SumLC.Append(["Difficulty:", str(Props[PR_DIFF]), "Accumulated difficulty of all steps"])
        self.SumLC.Append(["Givens:", str(81-Props[PR_NR_HOLES]),
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
        H = sorted(Props[PR_HISTO], key=lambda a: a[3])
        for i, HT in enumerate(H):
            Row = [f"{i+1:3d}",
                   f"{HT[HT_NR]:3d}",
                   HT[HT_TXT],
                   LVLS[HT[HT_LVL]],
                   f"{HT[HT_DIFF]:6d}",
                   f"{HT[HT_ADIFF]:6d}"]
            DM[i] = Row
            # self.StatLC.Append(Row)
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
        #self.SolnLC.InsertColumn(1, "Level", wx.LIST_FORMAT_LEFT, -1)
        self.SolnLC.InsertColumn(1, "Technique", wx.LIST_FORMAT_LEFT, -1)
        self.SolnLC.InsertColumn(2, "Diff.", wx.LIST_FORMAT_RIGHT, -1)
        self.SolnLC.InsertColumn(3, "Condition", wx.LIST_FORMAT_LEFT, -1)
        self.SolnLC.InsertColumn(4, "Outcome", wx.LIST_FORMAT_LEFT, -1)

        for j, Step in enumerate(Props[PR_STEPS]):
            self.SolnLC.Append([f"{(j+1):d}",
                                # LVLS[Props[PR_HISTO][Step[P_TECH]][HT_LVL]],
                                Props[PR_HISTO][Step[P_TECH]][HT_TXT],
                                f"{Step[P_DIFF]:d}",
                                tkns_to_str(Step[P_COND]),
                                tkns_to_str(Step[P_OUTC])])
            if len(Step[P_SUBS]):
                for k, SubStep in enumerate(Step[P_SUBS]):
                    self.SolnLC.Append([f"{j+1:d}.{k+1:d}",
                                        # LVLS[Props[PR_HISTO][SubStep[P_TECH]][HT_LVL]],
                                        Props[PR_HISTO][SubStep[P_TECH]][HT_TXT],
                                        f"{SubStep[P_DIFF]:d}",
                                        tkns_to_str(SubStep[P_COND]),
                                        tkns_to_str(SubStep[P_OUTC])])

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
            self.ToStep = -1

    def on_item_selected(self, e):
        self.ToStep = e.Index
        self.BtnSaveStep.Enable()
        self.BtnSlvTo.Enable()

    def on_save_step(self, e):
        Step = self.Creator.Props[PR_STEPS][self.ToStep]
        Grid = Step[P_GRID]
        Gvns = self.Creator.Props[PR_GIVENS]
        G = [[Grid[r][c] + 10 if not Gvns[r][c] and Grid[r][c] else Grid[r][c] for c in range(9)] for r in range(9)]
        if not save_puzzle((self.Creator.PzlDir, self.Creator.PzlFn), G, Step[P_ELIM], Step):
            wx.MessageBox("Could not save puzzle, do not know why . . .\n"
                          "Please send saved puzzle to developers",
                          "Warning",
                          wx.ICON_WARNING | wx.OK)

    def on_solve_to(self, e):
        if self.ToStep > self.FromStep:
            self.Creator.gen_event(EV_SC_ASL, self.FromStep, self.ToStep)
            self.FromStep = self.ToStep
        elif self.ToStep < self.FromStep:
            wx.MessageBox("Can't follow the Solution Path backwards",
                          "Information",
                          wx.ICON_INFORMATION | wx.OK)

    # ColumnSorterMixin callbacks.
    # noinspection PyPep8Naming

    def GetListCtrl(self):
        return self.StatLC

    def GetSortImages(self):
        return self.SmlDnIdx, self.SmlUpIdx

class UserGuide(wx.Dialog):

    # Simple class to display the user guide written in simple html when created
    # and destroy itself when close is selected.  User guide pops up as a
    # non modal window.

    def __init__(self, parent):
        wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = "User Guide",
                           pos = wx.DefaultPosition,
                           size = USER_GUIDE_DLG_SZ,
                           style = wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT | wx.RESIZE_BORDER)
        szr = wx.BoxSizer(wx.VERTICAL)
        self.htc = wx.html.HtmlWindow(self)
        szr.Add(self.htc, 1, wx.ALL | wx.EXPAND, 5)

        self.BtnClose = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.DefaultSize, 0)
        self.BtnClose.Bind(wx.EVT_BUTTON, self.on_close)
        szr.Add(self.BtnClose, 0, wx.ALIGN_CENTER | wx.TOP, 2)
        szr.Add((0, 7), 0, 0, 0)  #  Add a 7 pixel spacer.
        self.htc.LoadFile(os.path.join(os.path.dirname(__file__), "../doc/user_guide.html"))
        self.SetSizer(szr)
        self.Layout()
        self.Centre(wx.BOTH)

    def on_close(self, e):
        wx.CallAfter(self.Destroy)

def open_puzzle(Fp, Pzl):
    # Selects a puzzle with the FileDialog opening in Cwd, and returns a loaded
    # puzzle in grid G.  Note that the parent of the FileDialog is set to None.
    #   Grid = [[0 for c in range(9)] for r in range(9)]
    #   Elim = [[set() for c in range(9)] for r in range(9)]
    #   Meth = -1
    #   Pzl = [Grid, Elm, Meth]
    # Parms:
    #   Fp:  In:  a tuple containing the default directory and filename                  strings.
    #   G:   In:  Empty grid.
    #        Out: Populated grid if returns true, else undefined
    #             Empty cell is 0
    #             Given values are 1 to 9
    #             Placed values are 11 thru 19.  (offset by 10)
    #  E:    In:  Empty cell grid of cands to eliminate
    #        Out: Cell grid of cands to eliminate.
    #  M:    Out:  will return T_UNDEF if method in file is not recognised.
    # Returns:  None:  Could not load file properly
    #           (Dir, Fn) Tuple of successfully loaded file.

    dlg = wx.FileDialog(None, message = "Open A Puzzle",
                        defaultDir = Fp[0],
                        defaultFile = Fp[1],
                        wildcard = FILE_WILDCARDS,
                        style = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)

    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None

    Fs = dlg.GetPath()
    dlg.Destroy()
    try:
        with open(Fs, "rt") as f:
            sG = f.readline(MAX_SVL_FILE_SIZE)
    except (OSError, IOError):
        return None

    lG = sG.replace("\n", "").split("|")
    if lG[0] and grid_str_to_grid(lG[0], Pzl[0]):
        if len(lG) >= 2 and lG[1]:
            for sElim in lG[1].split(";"):
                r, c, op, Cands = parse_ccell_phrase(sElim)
                if r < 0 or op != OP_ELIM: break
                Pzl[1][r][c] = Cands
        if len(lG) >= 3 and lG[2]:
            for m in range(T_NR_TECHS):
                if T[m][T_TXT] == lG[2]:
                    break
            else:
                m = T_UNDEF
            Pzl[2] = m
        return os.path.split(Fs)
        #     else:
        #         if len(lG) >= 3 and lG[2]:
        #             for m in range(T_NR_TECHS):
        #                 if T[m][T_TXT] == lG[2]:
        #                     break
        #             else: m = T_UNDEF
        #             Pzl[2] = m
        #         return os.path.split(Fs)
        # else: return os.path.split(Fs)

    wx.MessageBox("Invalid Sudoku value file format",
                  "Warning",
                  wx.ICON_WARNING | wx.OK)
    return None

def parse_ccell_phrase(St):
    # only knows how to parse rycx-=digits, and rycx:=digit

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


def grid_str_to_grid(sG, G, Placed = True, GivensOnly = False):
    # Placed = True - differentiate between placed and givens, else all as givens
    # GivensOnly = True - only fill givens and ignore placed (digits prefixed by '+'
    i = rc = 0
    while i < len(sG):
        if rc >= 81:
            return False
        G[rc//9][rc%9] = 0; v = sG[i]
        if v in ["0", ".", "-"]: i += 1; rc += 1; continue
        if v == " ": i += 1; continue
        if v == "+":
            if GivensOnly: i += 2; rc += 2; continue
            if Placed: G[rc//9][rc%9] = 10;
            i += 1; v = sG[i]
        if v.isdigit(): G[rc//9][rc%9] += int(v); i +=1; rc += 1; continue
        return False  # error parsing the grid string.
    return True if rc == 81 else False

def grid_to_grid_str(G, sG = None):

    if sG == None: sG = ""
    for r in range(9):
        for c in range(9):
            if G[r][c] > 10: sG += "+"; G[r][c] %= 10
            sG += f"{G[r][c]}"
    return sG


def save_puzzle(Fp, G, ElimCands = None, Step = None):
    # Selects a puzzle filename with the save FileDialog in Cwd, and returns
    # after saving the sudoku values in the grid G.  Note that the parent of
    # the FileDialog is set to None.
    #
    # Parms:
    #   Fp:  In:  Tuple containing default directory and filename                  strings.
    #   G:   In:  Grid containing values to save.
    #        Out: Populated grid if returns true, else undefined
    # Returns:  None: Could not save selected file.
    #           Tuple containing directory and filename of saved file.

    sG = ""
    sG = grid_to_grid_str(G, sG)
    sE = ""
    if ElimCands:
        for r in range(9):
            for c in range(9):
                if ElimCands[r][c]:
                    if sE: sE += ";"
                    sE += f"r{r+1}c{c+1}-="
                    for v in sorted(ElimCands[r][c]):
                        sE += f"{v}"
        sG += f"|{sE}"
    if Step:
        sG += f"|{T[Step[P_TECH]][T_TXT]}"
        sG += f"|{tkns_to_str(Step[P_COND])}|{tkns_to_str(Step[P_OUTC])}\n".replace(" ","").replace(".", "")
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

# def flist(hl):
#     fl = []  # list()
#     for i in hl:
#         if isinstance(i, list):
#             fl.extend(flist(i))
#         else:
#             fl.append(i)
#     return fl

