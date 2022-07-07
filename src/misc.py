"""
A brown bag of utility and general functions that do not fit the context of other
files.  Includes functions that handle files, some dialogs and
some non-modal windows eg: list solution and user guide.
"""
import os
import wx

from globals import *

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

    NrFlds, sErr = pzl_str_to_pzl(sPzl, Pzl)
    if NrFlds: return os.path.split(Fs), NrFlds
    else:
        wx.MessageBox(sErr,
                      "Warning",
                      wx.ICON_WARNING | wx.OK)
        return None, 0

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

    sG = pzl_to_pzl_str(oPzl) + "\n"

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
        return 0, "Invalid Sudoku value puzzle spec format - grid."
    if lenlG >= 2 and lG[1]:
        Pzl.Elims = [[set() for c in range(9)] for r in range(9)]
        for sE in lG[1].split(";"):
            r, c, op, Cands = parse_ccell_phrase(sE)
            if r < 0 or op != OP_ELIM:
                return 0, "Invalid Sudoku puzzle string - malformed elims."

            Pzl.Elims[r][c] |= Cands
    if lenlG >= 3 and lG[2]:
        for Meth, TInfo in Tech.items():  # m in range(len(T):
            if TInfo.Text == lG[2]:
                Pzl.Method = Meth
                break
        else: Pzl.Method = T_UNDEF
    else: Pzl.Method = T_UNDEF
    if lenlG >= 4 and lG[3]:
        for Oride in lG[3].split(";"):
            if "=" in Oride: Key, Val = Oride.split("=")
            else: return 0, "Invalid Sudoku puzzle string - malformed overrides."
            Pzl.Overrides[Key] = Val
    if lenlG >= 6:
        Pzl.Pattern = lG[4]
        Pzl.Outcome = lG[5]
    if lenlG >=7:
        Pzl.Soln = [[0 for c in range(9)] for r in range(9)]
        if not grid_str_to_grid(lG[6],  Pzl.Soln, None):
            Pzl.Soln = None
    return lenlG, ""

def pzl_to_pzl_str(oPzl, sOverrides = None, sSoln = None):  #, CR = True):

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
        sG += f"|{Tech[oPzl.Method].Text}|"
        if sOverrides: sG += sOverrides
        sG += f"|{tkns_to_str(oPzl.Pattern)}|{tkns_to_str(oPzl.Outcome)}".replace(" ", "").replace(".", "")
    else: sG += "||||"
    if oPzl.Soln:
        sG += f"|{grid_to_grid_str(oPzl.Soln, oPzl.Givens)}"
    elif sSoln: sG += f"|{sSoln}"
    else: sG += "|"
#    if CR: sG += "\n"
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
            else: sG += "."
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

def pgm_msg(Type, Msg, Flags = wx.OK):  # wx.OK = 4 if not provided.
    # Wrapper that will put up a MessageBox if running under wx or
    # prints the message to console.  Only necessary to wrap messages
    # in modules/functions that run in both environments.

    try:
        return wx.MessageBox(Type, Msg, Flags)
    except:
        print(f"{Type}: {Msg}"); return Flags
    # if 'wx' in sys.modulesfrom importlib.util import find_spec
    # if find_spec("wx"): return wx.MessageBox(Type, Msg, Flags)
    # else: print(f"{Type}: {Msg}"); return Flags


# def flist(hl):
#     fl = []  # list()
#     for i in hl:
#         if isinstance(i, list):
#             fl.extend(flist(i))
#         else:
#             fl.append(i)
#     return fl
