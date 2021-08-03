#!/usr/bin/env python
"""
 Name:  main.pyw

Description:
    Yet another Soduko program to create and solve puzzles as well as teach
    logic techniques.
    Features include:
     *  Create puzzles
         - with specified type of symetry
         - to fall within specified difficulty grades
         - to only use selected logic techniques to solve.
     *  User entry of puzzles on screen
     *  Save and load puzzles - current state or list of values
     *  Check puzzles to ensure they only have one unique solution
     *  Grade puzzles identifying logic technques to solve and difficulty value
     *  Solving Assistant.
         -  Candidates (Pencil Marks)
              o  User add and erase.
              o  Automagic entry of candidates, per puzzle, cell, box, row
                 or column
              o  User highlighting of "can-be" and "must-be" candidates.
         -  Highlighting of cells, various colours and multiple cells
         -  Optionally highlight errors/conflicts.
         -  Hinting
              o  Correct value in selected cell.
              o  Next value and logic technique to solve.
    Future features
     *  In the background, create and cache a selection of puzzles.
     *  View, select or save-for-later puzzles from the cache.

Notes on programming style used here:
1.  The three major single instance classes are: TODO:  This para requires work.
    Sudoku:  This class manages the overall operation of the Sudoku program as
    a state machine, coordinating the activities of the other two major objects
    Board: This is the man machine Interface class responsible for drawing the
    grid, receiving user input and displaying puzzle information
    Puzzle: handles all the data associated with a puzzle and the the inputting / creation of puzzlesgeneration of An intent of the top level software design behind the code is to favour an
    egalitarian cluster of loosly coupled tightly contained objects rather than
    a hierachical structure of objects. Not to say that hierachy and inheritance
    are avoided when their use makes sense.

    Becuase this project has a relatively small number of objects, the necessity
    to abstract complexity by nesting objects is low. By design objects know
    their relationships and information flow with other objects.  Here it is
    not seen as advantagous to further constrain these relationships and flow by
    imposing hierachy.  As project size and number of objects increase, imposing
    hierachy by design becomes more advantagous/relevant.

2.  For speed, especially in the iterative and recursion algorithms, list
    comprehensions are favoured over deepcopy() for cloning/imaging lists.
    deepcopy() Is still used where it makes sense (ie less complex, more
    readable, and not nested in loops where the speed impact is multipied). In
    my speed testing I found list comprehensions to be about 8 times faster than
    the equivalent deepcopy()'s.

3.  By convention, use enumerated dicts to emulate the quivalaent of C-like
    typedef struct's rather rather than dataclasses.  Both afford similar
    readability albeit dataclass syntax being more familiar.  I suspect that the
    enumerated dicts are slightly more efficient in resources and speed, but
    this is yet to be confirmed.
    https://stackoverflow.com/questions/35988/c-like-structures-in-python

4.  Note a programming style that favours processing info in tables, rather than
    writing a long lists of if / elif / else type or other algorithmic flow.
    Not only does it take less (repetitive) code and produce simpler codec, with
    table driven software is much easier to debug and check for consistencies,
    ommissions, errors, etc.

4.  File organisation ref:
        https://stackoverflow.com/questions/6133348/confused-on-how-to-\
        structure-the-gui-wxpython/45555968#45555968

    Although this code no longer bares any resemblance to daniweb/Rev. Jim's
    code, I was inspired and cut my Python teeth on his code as I came up with
    my own incarnation.  To quote Rev. Jim:
            "None of us is as smart as all of us."


    Audit:
        2021-04-xx  jm  Initial entry

"""

import wx

# Local Imports
from globals import *
from menus import *
from sudoku import *

if DEBUG:
    import logging as log

    log.basicConfig(filename = 'sudoku.log',
                    filemode = 'w',
                    level = log.DEBUG,
                    format = '%(asctime)s: %(message)s')

class MainStatusBar(wx.StatusBar):
    def __init__(self, Parent):
        wx.StatusBar.__init__(self, Parent, id = wx.ID_ANY,
                              style = wx.BORDER_SUNKEN|wx.STB_DEFAULT_STYLE)
        self.SetFieldsCount(5)
        self.F1w = wx.Size.GetWidth(self.GetTextExtent(GE[ST_DEFAULT][SB]))
        self.F2w = wx.Size.GetWidth(self.GetTextExtent(AST_LVLS[AST_DEFAULT]))
        self.F3w = wx.Size.GetWidth(self.GetTextExtent(LVLS[LVL_NONE]))
        self.F4w = wx.Size.GetWidth(self.GetTextExtent("00:00:00"))-19
        self.SetStatusWidths([-1, self.F1w, self.F2w, self.F3w, self.F4w])
        self.SetStatusText(GE[ST_DEFAULT][SB], 1)
        self.SetStatusText(AST_LVLS[AST_DEFAULT], 2)
        self.SetStatusText(LVLS[LVL_NONE], 3)
        self.SetStatusText("00:00:00", 4)

    def update_0(self, Value):
        self.SetStatusText(Value, 0)

    def update_state(self, Value):
        self.F1w = wx.Size.GetWidth(self.GetTextExtent(Value))
        self.SetStatusWidths([-1, self.F1w, self.F2w, self.F3w, self.F4w])
        self.SetStatusText(Value, 1)

    def update_assist(self, Value):
        self.F2w = wx.Size.GetWidth(self.GetTextExtent(Value))
        self.SetStatusWidths([-1, self.F1w, self.F2w, self.F3w, self.F4w])
        self.SetStatusText(Value, 2)

    def update_level(self, Value):
        self.F3w = wx.Size.GetWidth(self.GetTextExtent(Value))
        self.SetStatusWidths([-1, self.F1w, self.F2w, self.F3w, self.F4w])
        self.SetStatusText(Value, 3)

    def update_time(self, Value):
        self.SetStatusText(Value, 4)


class MainWindow(wx.Frame):
    def __init__(self):  # , parent):
        # Create a default frame excluding border resizing
        wx.Frame.__init__(self, None,
                          id = wx.ID_ANY,
                          title = TITLE,
                          pos = wx.DefaultPosition,
                          size = wx.DefaultSize,
                          style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
        self.Hide()
        Icon = wx.Icon()
        Icon.CopyFromBitmap(wx.Bitmap("sudoku.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(Icon)
        self.SetMenuBar(MainMenubar(self))
        self.SetStatusBar(MainStatusBar(self))

#        self.Board = Board(self)  # Frontend man/machine interface
        self.Sudoku = Sudoku(self, self.MenuBar, self.StatusBar)  # Instantiate the single instance Sudoku class.

        self.Bind(wx.EVT_CLOSE, self.on_exit)



    def on_exit(self, e):
        self.Sudoku.on_close(e)
        e.Skip()
        del e
        self.Hide()
        wx.CallAfter(self.Destroy)

def main():
    #if __name__ == "__main__":
    App = wx.App(False)
    Frame = MainWindow()
    App.SetTopWindow(Frame)
    Frame.Show()
    App.MainLoop()

if __name__ == "__main__":
    main()
