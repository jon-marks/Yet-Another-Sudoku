.. title:: Yet Another Sudoku::Glossary

Glossary
========

1.4.   Glossary
https://www.sudocue.net/glossary.php and http://sudopedia.enjoysudoku.com/Terminology.html


Grid:	9x9 grid, subdivided into 9 – 3x3 grids (Blocks) on to which Sudoku puzzles are spatially represented. I generally call an empty grid a grid, a partially filled grid a puzzle and a filled grid, a board.
Board:	Filled/solved puzzle.  Analogous to a finished game of chess. (Except for Sudoko a completed game is when all the locations have numbers according to the rules, rather than a few chess remaining in check or stale mate).
Puzzle:	A Patrially completed Sudoku in a puzzle, it may only be populated with the givens or with givens and some solved values.
Box / Block:	One of the 9 3x3 sub grids making up the 9 x 9 Sudoku grid.
Chute/Band:	3 Boxes in a row or column.  A horizontal chute is known as a Floor, a vertical chute is known as a Tower.
Location or Cell:	A position in the 9x9 Grid.  Located as a 2 dimensional array. For example Grid[7,2] is the cell in the 7th row, and 2nd column.  A cell can also be referenced by r7c2.  A cell state can be:

    • Given:  Populated with a fixed value that defines the puzzle.
    • Solved:  Entered, possibly correct value
    • Empty: No values.  Often empty cells are annotated with candidate pencil marks.

Group/House/Sector/Unit:	A collection of 9 locations that can hold the 1 to 9 unique solved values in a Sudoku grid.  A House can refer to a Row, Column or Box, where each house contains a unique value between 1 and 9 that obeys Sudoku rules.  .  A group can be referenced by r7 for the 7th row, c2 for the 2nd column.  Blocks can be referenced by NW for the NW block, or r123c456 for the N block.  Blocks/Boxes, Rows and Columns are Groups/Houses.
Peers/Buddies:	The Peers/Buddies of a cell are the other cells in the combined row, column and block groups.  By Sudoku rules all Peers are have unique numbers, Peers cannot have the same values..  Peers/Buddies are said to “see” each other.
Lines:	A line is either a row or a column.
Row:	Horizontal House/Group or line.
Column:	Vertical House/Group or line.
Intersection/Overlap:	Where 2 Groups/Houses share one or more cells.  The shared cell(s) where a row and column cross, or when a row or column crosses a block.
Conflict/Contradiction/Error:	Where there are two or more cells with the same value in a Group/House.
Minimal Puzzle:	A minimal puzzle is that where no more holes can be dug without the puzzle becoming invalid, that is having multiple solutions.
Candidate:	A possible solved value for an unsolved cell.  This definition has a finer disctinction in that is only a reference to the candidate value, irrespective of the Cell it is found in.  A Ccell defines a potential solved value for a cell by its value and celll coordinates. In solving puzzles candidates are whittled away (eliminated) using logic techniques until only one candidate remains, which is the Solved value.
Slink:	Strong link in a chain or a loop
Wink	Weak link in a chain or a loop
Ccell	Refers to a candidate value in a cell as a unique identifier comprising the candidate, row and column coordinates as a tuple.  For example 3r2c8 candidate 3 in row 2, column 8..  This reference is useful when referring to specific candidates in specific cells, and is used extensively in the explanation of many logic techniques and their algorithms.   In solving puzzles Ccells are whittled away (eliminated) using logic techniques until only one Ccell remains as the solution for that cell.
Sudoku Rules	The collective term for:
* The numbers 1 through 9 only occur once in each row, column and block.
* Only one unique solution.
Conjugate Pair.	The two same value candidates in a house forming a strong link.
Bi-Value Cell (BVC)	A cell containing only two candidates.
AIC	Alternating Inference Chain.  A chain comprising alternating Weak and Strong links.
Linebox	The intersection of a line (row or column) and a box comprising only three cells.
Rowbox	The intersection of row and box comprising only three cells
Colbox	The intersection of a column and box comprising only three cells.