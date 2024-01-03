.. title:: Yet Another Sudoku | Foundation | Premises, Inferences and Searching

.. include:: ..\globals.inc

.. _found_premises_and_inferences:

**********************************
Premises, Inferences and Searching
**********************************

.. _found_prem_inf:

Premises and Inferences
=======================

Source: http://sudopedia.enjoysudoku.com/Inference.html

Solving Sudoku puzzles involves asserting a premise, and deducing what conclusions can be
inferred.  

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

Searching is the process of cascading inferences to find a solution.  Often referred to as Forcing 
Chains in the Sudoku literature, it is a type of Trial and Error technique, not a guessing.  It is 
the application of logic to test a premise.

However, exhaustive searching becomes a mechanical process, replacing skill with brute force to find
a solution.  Searching finds it own place in conjunction with other criteria, logic and/or pattern 
solving techniques that have isolated a few conditions to search.  

A Verity is where two search different paths from the same condition, find another candidate to be 
True in both cases.  A Contradiction where two different search paths from the same condition find
another candidate to be False in both cases.  A verity / contradiction could also be the testing for
a :ref:`strong <found_lc_strong_links>` or :ref:`robust link <found_lc_robust_link_patterns>`.
