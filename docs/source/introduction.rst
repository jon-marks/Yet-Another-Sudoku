.. title:: Yet another Sudoku | Introduction

************
Introduction
************

    “If you steal from one author it's plagiarism; if you steal from many it's research.”
     --- Wilson Mizner

History
=======

Sources:
   |  http://sudopedia.enjoysudoku.com/Introduction.html
   |  https://en.wikipedia.org/wiki/Sudoku

In July 1895 in France, the Newspaper La France, refined a numbers game puzzle appearing in a rival
newspaper Le Siècle.  La France called these puzzles *Carré Magique Diabolique*.  These puzzles were
the precursor to modern Sudoku.  La France published its puzzles until about the time of the First World War.

Modern Sudoku started out published in Dell Magazines from about 1979 called *Number Place*.  It is thought
that they were designed by Howard Garns, a retired 74-year old Architect.  In 1984 the Nikoli Puzzle Company
in Japan introduced *Number Place* puzzles as *Sūji wa dokushin ni kagiru* which was later abreviated (in Kanji)
to *Sudoku*, despite it being unbiquitously called *Nanpure* in Japan.

In 1997, Wayne Gould,  a retired Hong Kong Judge, developed the first computer program to produce unique puzzles
rapidly, and introduced Sudoku to the Times newspaper in Britain.  The publicity gained from its exposure in the Times
secured the puzzle's world wide popularity.

What is Sudoku
==============

Sudoku is a puzzle laid out on a 9x9 grid of cells, where each cell is either empty or contains a number
between 1 and 9.  The puzzle is solved by filling the empty cells with digits 1 to 9 such each digit only
occurs once in each row, column and 3x3 box.

.. _sudoku_rules:

Sudoku Rules
============

   1. A completed Sudoku Puzzle is one where each cell on a 9x9 grid contains a digit between 1 and 9
      such that each digit only occurs once in each row, column and 3x3 box, and
   2. The puzzle has a unique solution.

Sudoku Facts
============

Source: http://sudopedia.enjoysudoku.com/Mathematics_of_Sudoku.html
   https://en.wikipedia.org/wiki/Sudoku

Sudoku is a finite constraint satisfaction problem (fCSP).  A Sudoku grid comprises 9 rows by 9 columns
making 81 cells, and each cell can assume one of 9 values.  Therefore the out of a Domain set of 729
(9 rows x 9 columns x 9 Values) elements, any Solution set comprises 81 elements (9 rows x 9 columns x 1 value)
that are constrianed by Sudoku Rules and further constraint propagation.

`Fraser Jarvis, et al <http://www.afjarvis.staff.shef.ac.uk/sudoku/>`_ has determined there are
6670903752021072936960 (6.6709e+21) Sudoku grids of
which 5472730538 (5.4727e+9) are mathematical unique.  That is they cannot be computed by transforming
one grid to another. Also termed non-isomorphic; they are not canonical forms of each other.

`Denis Berthier <http://www.carva.org/denis.berthier>`_ has estimated to within a 0,065% error the average number of minimal puzzles that can be
formed from a Sudoku grid is 4.6655e+15.  Therefore the number of of minimal Sudoku puzzles possible is
6.6709e+21 x 4.6655e+15 = 3,1123e+37, of which 2.5533e+25 are mathematically unique.

It is often useful to give perspective to such astronomical large numbers.  Say it is possible to solve
a puzzle every second, only 31 557 600 (3,1557e+7) puzzles can be solved in a year.  Solving a puzzle
every second since the beginning of time (estimated 14 billion years ago), only 4,4180e+15 puzzles will
be solved.  There are approximately 8 billion people on earth (2022).  If everyone on earth has been
solving unique Sudoku puzzles since the beginning of time, only 3.5345e+27 puzzles will be solved.
This number is an infinitesimally small one 8.8 billionth (8.8055e-9) of all possible puzzles.

There is no known theoretical minimum number of givens a puzzle can have and still be unique.  To date
no unique puzzles have been found with less than 17 givens, and only 49158 puzzles have been found with
17 givens.  The list can be found in this archive.

All puzzles with 40 or more givens have one unique solution. Most unique minimal puzzles have between 23
and 26 givens.

In a valid puzzle at least 8 of the 9 digits must occur one or more times as givens.  However, meeting this
criteria does not presume a puzzle is valid.

Intended Audience
=================

This treatise is intended for people who have at least mastered the basics of Sudoku, and are seeking to improve
their Sudoku skills.  `There are many very good sources on the internet that do a better job than I in covering the
basics <https://www.google.com/search?client=firefox-b-d&q=Sudoku+basics>`_.  I defer to them.

Acknowledgements
=================

I owe credit to the whole sudoku community, the many reports, web-pages, and videos found on the Internet.
This tomb brings together many, many related bits information.  If anything is original here, it is
the insights and conclusions gained from the collective works before me.

A complete list acknowledging all the media that has contributed to my understanding would be so vast and so
incomplete distracting from it's intent.  I owe all the contributors in the Sudoku community a big debt of
gratitude.

I have taken the effort to acknowledge sources of information and puzzles throughout the text and have included
a :ref:`list of references <references>`.  I fear that with the passage of time, linked references will disappear,
frustrating readers seeking sources, I apologise in advance for this.
