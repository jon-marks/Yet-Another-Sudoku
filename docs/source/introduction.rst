
Introduction
============

    “If you steal from one author it's plagiarism; if you steal from many it's research.”
     --- Wilson Mizner

History
-------

Source: http://sudopedia.enjoysudoku.com/Introduction.html

A game called "Number Place" was designed by Howard Garns, and first published by Dell Magazines
in 1979. The puzzle was introduced in Japan by Nikoli in 1984, who gave it the name "Sudoku", which
is an abbreviation for the original Japanese name meaning "The Numbers must be Unique". The whole
world adopted this new name, but in Japan, Nikoli owns the trademark, so other publishers in Japan
call it Nanpure, the Japanese translation of Number Place. By the end of 2004, Sudoku appeared in
The Times in Britain, brought to Europe by Wayne Gould, the founder of Pappocom.

What is Sudoku
--------------

Sudoku is a puzzle laid out on a 9x9 grid of cells, where each cell is empty or contains a number
between 1 and 9.  The puzzle is solved by filling the empty cells with digits 1 to 9 such each digit only
occurs once in each row, column and 3x3 box.

Sudoku Rules
------------

   1. A completed Sudoku Puzzle is one where each cell on a 9x9 grid contains a digit between 1 and 9
      such that each digit only occurs once in each row, column and 3x3 box, and
   2. The puzzle has a unique solution.

.. _sudoku:

Sudoku Facts
------------

Source: <http://sudopedia.enjoysudoku.com/Mathematics_of_Sudoku.html

Sudoku is a finite constraint satisfaction problem (fCSP).

`Fraser Jarvis, et al <http://www.afjarvis.staff.shef.ac.uk/sudoku/>`_ has determined there are 6670903752021072936960 (6.6709e+21) Sudoku grids of
which 5472730538 (5.4727e+9) are mathematical unique.  That is they cannot be computed by transforming
one grid to another. Also termed non-isomorphic; they are not canonical forms of each other.

Denis Berthier has estimated to within a 0,065% error the average number of minimal puzzles that can be
formed from a Sudoku grid is 4.6655e+15.  Therefore the number of of minimal Sudoku puzzles possible is 6.6709e+21 x 4.6655e+15 = 3,1123e+37, of which 2.5533e+25 are mathematically unique.

It is often useful to give perspective to such astronomical large numbers.  Say it is possible to solve a puzzle every second, only 31 557 600 (3,1557e+7) puzzles can be solved in a year.  Solving a puzzle every second since the beginning of time (estimated 14 billion years ago), only 4,4180e+15 puzzles will be solved.  There are approximately 8 billion people on earth (2022).  If everyone on earth has been solving unique Sudoku puzzles since the beginning of time, only 3.5345e+27 puzzles will be solved.  This number is an infinitesimally small one 8.8 billionth (8.8055e-9) of all possible puzzles.

There is no known theoretical minimum number of givens a puzzle can have and still be unique.  To date no unique puzzles have been found with less than 17 givens, and only 49158 puzzles have been found with 17 givens.  The list can be found in this archive.

All puzzles with 40 or more givens have one unique solution. Most unique minimal puzzles have between 23 and 26 givens.

In a valid puzzle at least 8 of the 9 digits must occur one or more times as givens.  However, meeting this criteria does not presume a puzzle is valid.


1.3.   Intended Audience
This treatise is intended for people who have mastered the basics of Sudoku, and are seeking to improve their Sudoku skills.  There are many very good sources on the internet that teach the basics, so it is not necessary to repeat it here.
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
1.5.   Acknowledgements
In my journey of understanding Sudoku logic which is documented here,  I owe credit to the whole sudoku community, the many reports, web-pages, and videos found on the Internet. This tomb is a bringing together of related bits information.  If anything is original here it is the insights and conclusions drawn from the collective works before me.  Following is a list of website links read and watched.  Additionally, the text is peppered with specific web page links where the specific reference is applied.

Researching, I found the following refs for the basis of this work.
    1. Sudopedia: http://sudopedia.enjoysudoku.com/  Most useful for its solving techniques reference.  Not everything listed is explained or explained in sufficient detail but reference to search elsewhere.
    2. Hodoku:  Bernhard Hobiger website.  Bernhard passed away (last updates are 2013 on his website).  Site and program contain a very comprehensive list of solving techniques, training and learning, a very good start for me to base my program on.

http://hodoku.sourceforge.net/en/index.php
    3. Pseudofish: This is a branch of the Hoduko code base and maintained up to 2020 releasing v2.3.0.

https://github.com/PseudoFish/Hodoku
    4. Systematic Sudoku:  Methods for solving Sudoku puzzles in a systematic way.

https://sySudoku.com/
    5. https://www.stolaf.edu/people/hansonr/Sudoku/index.htm:  Online solver:  Techniques are explained in https://www.stolaf.edu/people/hansonr/Sudoku/explain.htm and https://www.stolaf.edu/people/hansonr/Sudoku/12rules.htm

The following links present solutions to solve less than evil/extreme puzzles without backtracking
    6. https://Sudokusolver.com/play/:  look at the simple techniques and advanced techniques for explanations.
    7. https://www.kristanix.com/Sudokuepic/Sudoku-solving-techniques.php
    8. Simple soduko  includes a program and many sample puzzles to work with. http://www.angusj.com/Sudoku/index.php.  Techniques used explained here: www.angusj.com/Sudoku/hints.php

Puzzle Generation
    9. https://stackoverflow.com/questions/6924216/how-to-generate-Sudoku-boards-with-unique-solutions/7280517
    10. https://www.101computing.net/Sudoku-generator-algorithm/.  Algorithm in python.

Backtracking algorithms
    11. https://hackernoon.com/Sudoku-and-backtracking-6613d33229af.  High level explanation
    12. https://stackoverflow.com/questions/1518346/optimizing-the-backtracking-algorithm-solving-Sudoku
    13. https://www.101computing.net/backtracking-algorithm-Sudoku-solver/.  Algorithm in Python.  Explanation of code: https://medium.com/swlh/simple-Sudoku-with-backtracking-bb4813ddabb1

Sudoku swami,
enjoySudoku.com – Sudoku forum.
pauls pages
allanbarker.com
Sudokuwiki. Very good
http://www.taupierbw.be/SudokuCoach/  very good but appears to be a scrape of Sudowiki with scrambled examples from Sudokuwiki..
http://www.philsfolly.net.au/
https://sudoku.ironmonger.com/howto/basicRules/docs.tpl?setreferrertoself=true
Test Cases
http://forum.enjoysudoku.com/let-s-build-a-zoo-t4424.html
http://forum.enjoysudoku.com/the-effortless-extremes-thread-t3740.html

http://sudopedia.enjoysudoku.com/Mathematics_of_Sudoku.html

This is what the console output looks like for building this page:

.. code-block:: console

    (venv) C:\Users\jm\Dropbox\Work\Sudoku\Yet Another Sudoku>docs\make html
    Running Sphinx v5.1.1
    Initializing Basicstrap theme directives
    loading pickled environment... done
    building [mo]: targets for 0 po files that are out of date
    building [html]: targets for 2 source files that are out of date
    updating environment: 0 added, 0 changed, 0 removed
    looking for now-outdated files... none found
    preparing documents... done
    writing output... [100%] introduction
    generating indices... genindex done
    writing additional pages... search done
    copying static files... done
    copying extra files... done
    dumping search index in English (code: en)... done
    dumping object inventory... done
    build succeeded.

    The HTML pages are in build\html.


