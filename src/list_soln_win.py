
# import os

import wx.html
import wx.lib.mixins.listctrl as lcmi  # list control mix in
from wx.lib.embeddedimage import PyEmbeddedImage

from globals import *
from solve import Tech
from misc import *
from solve_utils import determine_cands

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
            Pattern = tkns_to_str(Step.Pattern)
            if len(Pattern) > 220: Pattern = Pattern[:220] + "..."
            Outcome = tkns_to_str(Step.Outcome)
            if len(Outcome) > 220: Outcome = Outcome[:220] + "..."
            self.SolnLC.Append([f"{(j+1):d}",
                                Tech[Step.Method].Text,
                                f"{Step.Difficulty:6d}",
                                Pattern,
                                Outcome
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
                                                                   Outcome = Step.Outcome,
                                                                   Soln    = self.Creator.Puzzle.Soln
                                                                   ))

    def on_copy_step(self, e):
        Step = self.Creator.Puzzle.Steps[self.ToStep]
        NrEmpties, Elims = determine_cands(Step.Grid, Step.Cands)
        copy_puzzle_to_clipboard(PZL(Grid    = Step.Grid,
                                     Givens  = self.Creator.Puzzle.Givens,
                                     Elims   = Elims,
                                     Method  = Step.Method,
                                     Pattern = Step.Pattern,
                                     Outcome = Step.Outcome,
                                     Soln    = self.Creator.Puzzle.Soln
                                     )
                                 )

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

