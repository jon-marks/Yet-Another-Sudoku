... title:: Yet another Sudoku | Software | Algorithms

.. include:: ..\globals.inc

============
Algorithms
============

YAS Algorithms.

In YAS, they are used in the exhaustive construction of AI-Chains.
YAS does this by identifying the forest of all possible net starts and growing trees for all of these saplings.
The traversal from each tree trunk to every leaf in that tree forms an AI chain.  On average solutions are found faster by growing one strong and one weak branch level at a time and then checking if the chain finds eliminations or placements.  Rather that fully constructing the net and then scanning the net.  The former yields more complex code, but the effort is worth it in terms of average time reduction.
