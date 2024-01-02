.. title:: Yet Another Sudoku | Foundation | Spatial Representation

.. include:: ..\globals.inc

.. _found_spatial-reps:

***********************
Spatial Representation
***********************

See Denis Berthier’s Hidden Logic of Sudoku. https://github.com/denis-berthier.

A Sudoku solution is a unique selection and ordering of 81 ccells (value,
row, column tuples) out of an exhaustive set of 729 ccells – where values, rows and columns can
assume any value between 1 and 9, and Sudoku rules apply.  Sudoku is a Finite Constraint Satisfaction
problem, and the recognition of patterns and their resolutions in solving the puzzle are the
constraint propagation techniques.

Sudoku puzzles are spatially represented as values on a 9 row by 9 column grid of
cells.  However, this is not the only possible spacial representation for Sudoku.  The same
puzzle can be represented as row numbers on a value x column number or any of the other 6 spatial
domains:

*  values on a row x column grid (default)
*  row numbers on a value x column grid
*  column numbers on a value x row grid
*  values on a cell x box grid
*  box numbers on a value x cell grid
*  cell numbers on a value x box grid

The underlying puzzle logic is the same, it is only the perspective, that differs in each spatial
representation.

However, each perspective, exposes patterns that are hidden in other perspectives.  For example, a
hidden single or hidden subset patten will be transformed into an exposed pattern in one of the
five perspectives.

Viewing puzzles from different perspectiv0516es, come into its own with more complex patterns
such as chains, loops, nets, bent hidden subsets, etc. Transforming to another domain may make it
easier to spot exposed patterns that are hidden in the former domain.
