.. title:: Yet Another Sudoku | Foundation | Premises and Inferences

.. include:: ..\globals.inc

.. _found_premises_and_inferences:

***********************
Premises and Inferences
***********************

Source: http://sudopedia.enjoysudoku.com/Inference.html

Solving Sudoku puzzles involves asserting a premise, and deducing what conclusions can be
inferred.  Applying a premise is different to guessing.  A premise is used to infer logical
conclusions, whereas guessing is taking a chance on arbitrarily selecting what might be the correct
cell value and testing it.

The most basic assertion of a premise is on the state of a Ccell. For example:

| ``3r7c2`` - Asserts 3 in r7c2 to be True, similarly.
| ``3!-r7c2`` - Asserts 3 in r7c2 to be False

When a cell state is inferred, other cell states may be inferred:

| ``3r7c2 => 3r7c8 => 5r7c8``

Asserting 3r7c2 True, infers 3r7c8, which in turn infers 5r7c8.  An inference string may lead to
the placement or elimination of a candidate.

| ``5!-r2c7 => 5r2c2 => 5!-r6c2 => 5r6c7 => r34c7-=5``

Asserting 5r2c7 False infers 5r2c2 is True, 5r6c2 is False, leading to the elimination of candidate
5 from Cells r3c7 and r4c7.


Searching
=========
