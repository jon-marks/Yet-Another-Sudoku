.. title:: Yet Another Sudoku | Foundation | Base Sets (Truths) and Cover Sets (Links)

.. include:: ..\globals.inc

..  _found_blc_sets:

*************************
Base, Link and Cover Sets
*************************

This section owes much credit to:
   |  https://www.stolaf.edu/people/hansonr/sudoku/12rules.htm, and
   |  http://sudoku.allanbarker.com/sweb/general.htm
   
.. _found_blc_intro:

Introduction
============

Some Definitions
----------------

**Cell**
   A location in a Sudoku grid which either contains a :term:`Given` or into which a 
   :term:`Solved Value` is placed.

**Ccell**
   A three-dimensional tuple uniquely identifying a candidate element by value, row,
   and column in a Sudoku Grid.

**House**
   A specific 9 cell of a :term:`Row`, :term:`column` or :term:`Box`.  Also known as a Group, 
   Sector or Unit.

**Chouse**
   Collective noun for :term:`House` and :term:`Cell`.

**See**
   :term:`Ccell`\s that have an :term:`Link` between them are said to see each other.

**Set**
   A collection of :term:`Ccell`\s that :term:`See` each other in a :term:`Chouse`.
   
**Truth**
   A collection of :term:`Ccell`\s that :term:`See` each other in a :term:`Chouse` where one of 
   the Ccells is True, that is the :term:`Solved Value`.

**Base Set**
   A Base Set is a :term:`Set` of one or more :term:`Ccell`\s in a :term:`Chouse` forming a 
   :term:`Truth`.  Base Sets may :term:`Overlap` each other, but cannot :term:`Intersect <Intersection>`.

**Link Set**
   A :term:`Set` of one or more :term:`Ccell`\s in a non-:term:`Base Set` :term:`Chouse` that are 
   in any Base Set.

**Cover Set**
   A Cover Set is a :term:`Set` of all the :term:`Ccell`\s that :term:`See` each other in the 
   :term:`Chouse` of a :term:`Link Set`.
   
A Viable Pattern is one where all the Base Set Ccells in the union of Base Sets are also present
in the union of Link Set Ccells.  That is All Link Set Ccells Intersect Base Set Ccells, thus locking
all the Link Sets as Truths.  Any Cover Set Ccell that is not part of a Link Set cannot be True and
is eliminated. 

.. figure:: images/base-cover-eg1.png
   :name: fig-base-cover-eg1
   :scale: 65%
   :alt: Sudoku X-Wing Example
   :align: right
   :figwidth: 359px

   Base, Link and Cover Set Example

   :raw-html:`<mong>+17+6.2958.94...+6...+8+3.....6.4+816.....+7239.+4+8.+65+6+9..24..+2+9+7.6814.+6+1+4.+9...+835+8+24+1+6+97||X-Wing||3r17c49|r2c4-=3;r2c9-=3;r4c9-=3;r6c4-=3;r6c9-=3;r8c4-=3|+17+6+42958+394+5+8+3+6+7+1+2+8+3+2+1+7+5+96+44+816+5+3+2+7+9+7239+1+4+8+5+65+6+9+7+824+3+1+2+9+7+36814+5+6+1+4+5+9+7+3+2+835+8+24+1+6+97</mong>`

In Fig :numref:`fig-base-cover-eg1`

*  Row 1 is a :term:`Base Set` containing the :term:`Truth` ``3r1c49``.
*  Row 7 is also a :term:`Base Set` containing the  :term:`Truth` ``3r7c49``.
*  Column 4 is a :term:`Link Set` connecting ``3r1c4`` and ``3r7c4`` from the Base Sets.
*  Column 9 is also a :term:`Link Set` connecting ``3r1c9`` and ``3r7c9`` from the Base Sets.
*  Column 4 is also a :term:`Cover Set` including all :term:`Ccell`\s that see the Link Set, that is ``3r12678c4``.
*  Column 9 is also a :term:`Cover set` including all :term:`Ccell`\s that see its Link Set  that is ``3r12467c9``
*  Because all the Base Ccells are covered by Cover Ccells, the intersecting Ccells are confirmed as 
   a Truth in the Cover Sets.  Thus, resulting in the elimination on non-intersecting Ccells in the 
   Cover Sets, ``(r268c4,r246c9) -= 3``

.. _found_blc_sop:

Single Order Patterns
=====================

A single order patterns has a single :term:`Base Set`, with a single :term:`Ccell` :term:`Truth`.  Ccells in
:term:`Intersecting <Intersection>` :term:`Cover Set`\s outside the intersection are eliminated.

:ref:`Exposed Singles <found_sing_exposed>`, :ref:`Hidden Singles <found_sing_hidden>`, and 
:ref:`Locked Singles <found_sing_locked>` are examples of Single Order Patterns.

Expressing the :term:`Sudoku Rule` as a Formula for Single Order Patterns using Set Algebra:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Base Set  <b>B</b>  = {P}    # P is the only Ccell Truth in the Base Set <b>B</b>
Cover Set <b>C<sub>j</sub></b> = {S, T, V, ...}    # S, T, U, ... are the Ccells that see P in Cover Set<sub>j</sub>.
Cover Set <b>C</b> = U(<b>C<sub>0</sub></b>, <b>C<sub>1</sub></b>, ...)    # C is the union of Cover Sets C<sub>0</sub>, C<sub>1</sub>, ...
&nbsp;
IF (<b>B</b> & <b>C</b> == <b>B</b>):    # if <u>all</u> the Cover Set Ccells intersect Base Set Ccells
&nbsp;  THEN <b>Elims</b> = <b>C</b> - <b>B</b>    # Then Eliminate all Cover Ccells not in Base Sets  
</pre></div></div>
<p><span>`

.. figure:: images/hid-sing-eg1.png
   :name: fig-hid-sing-eg1
   :scale: 65%
   :alt: Sudoku Single Base Set Hidden Single Example
   :align: right
   :figwidth: 359px

   Single Base Set - Hidden Single Example

   :raw-html:`<mong>.6...1..4.48....9+1....+4...+2+4..2.87+5+658+2967+143..65.4+9+2+8+6.....+4+1.+85+4+1..26.1..4.+6+38.|r1c3-=9;r1c5-=3;r2c5-=3;r3c2-=9;r3c3-=9;r7c5-=3;r8c5-=3|Hidden Pair||29#2r1c15|r1c1-=37;r1c5-=578|+96+3+8+21+5+74+248+3+7+5+69+1+7+1+5+6+4+9+8+3+2+4+9+12+387+5+658+2967+143+3+765+14+9+2+8+6+3+9+7+8+2+4+1+5+85+4+1+9+326+71+2+74+5+6+38+9</mong>`

In :numref:`fig-hid-sing-eg1` Candidate 3 occurs once in Row 8 in location ``r8c6``. From Theorem 1, as ``3r8c6`` is the only 
occurrence of 3 in row 8, it is also the only occurrence in:

*  Column 6 resulting in the eliminations ``r236c6-=3``.
*  Box 8 resulting in the eliminations ``r7c46-=3``.
*  Cell ``r8c6`` resulting in the elimination ``r8c6-=9``, and placement of only remaining candidate
   ``r8c6:= 3``.

Normally the following logic bypassed by recognising that the only occurrence of a candidate in a
House is the solved value. ``r8c6:= 3``, which automagically eliminates all ccells with
candidate 3 that can see this placed value.  However, this Logic is easier understood with a simple
example before progressing to more complex patterns.

|
|

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Base Set: <b>B<sub>3r8</sub></b> = {3r8c6}   # The only 3 in Row 8
&nbsp;
Column Cover Set: <b>C<sub>3c6</sub></b> = {3r2c6, 3r3c6, 3r7c6, 3r8c6}    # Intersecting Column
Box Cover Set: <b>C<sub>3b8</sub></b> = {3r7c4, 3r7c6, 3r8c6}    # Intersecting Box
Cell Cover Set:<b>C<sub>r8c6</sub></b> = {3r8c6, 9r8c6}    # Intersecting Cell
&nbsp;
Cover Set Union <b>C<sub>U</sub></b> = {3r2c6, 3r3c6, 3r7c4, 3r7c6, 3r8c6, 9r8c6}
</pre></div></div>
<p><span>`

Evaluating the IF condition:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre><b>B<sub>3r8</sub></b> & <b>C<sub>U</sub></b> == <b>B<sub>3r8</sub></b>
{3r8c6} & {<del>3r2c6</del>, <del>3r7c4</del>, <del>3r3c6</del>, <del>3r7c6</del>, 3r8c6, <del>9r8c6</del>}
True</pre>
</div></div>
<p><span>`

Because the IF condition is True, the Eliminations are evaluated as:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Elims = <b>C<sub>U</sub></b> - <b>B<sub>3r8</sub></b>
&nbsp;       {3r2c6, 3r3c6, 3r7c4, 3r7c6, <del>3r8c6</del>, 9r8c6} - {3r8c6}
&nbsp;       {3r2c6, 3r3c6, 3r7c4, 3r7c6, 9r8c6}</pre>
</div></div>
<p><span>`

All same value Ccells in intersecting houses that can see 3r8c6 in the intersection are eliminated,
leaving ``3r8c6`` as the only Ccell in the intersection, permitting its placement.

.. _found_blc_mop:

Multi Order Patterns
====================

:term:`Multi Order Pattern`\s, abr: :term:`MOP`, have multiple :term:`Base Set`\s  :term:`intersected <Intersection>` by
multiple :term:`Link Set`\s.  Depending on how the Link Sets intersect the Base Sets, additional
Truths may be found, which in turn, may lead to eliminations.

MOPs can be one of:

*  **Lesser Multi Order Patterns** with fewer Link Sets present than Base 
   Sets.  It is impossible for fewer Link Sets to intersect all the Base Set CCells.  Therefore, 
   without additional crieria, it is impossible to lock further Truths.  Look to 
   `Allan Barker's General Logic of Sudoku <https://sudoku.allanbarker.com/sweb/general.htm>`_'s
   section on Illegal Logic for more information.
*  **Equal Multi Order Patterns**, (abr: EMOP) All :term:`Ccell`\s in 'n' :term:`Base Set`\s are 
   :term:`Intersected <Intersection>` by at least 'n' :term:`Link Set`\s.  Any :term:`Cover Set` 
   :term:`Ccell` that is not in a Base Set cannot be True and is eliminated.
*  **Greater Multi Order Patterns**, (abr: GMOP) need 'n + r' :term:`Link Set`\s to 
   :term:`Intersect <Intersection>` all the Base Set Ccells. Any non Base Set Ccell in 'r + 1' 
   Cover Sets cannot be True and is eliminated.  EMOPs are a special case of GMOPs where 'r' = 0.  

.. _found_blc_emop:

Equal Multi Order Patterns
--------------------------

A 'n<sup>th</sup>' order :term:`EMOP` has 'n' Link Sets intersecting all the Ccells of 'n' Base Sets, 
exposing the Link Set's as Truths.  Any Ccell that can see a Link Set Truth cannot be True and is
eliminated.  A EMOP pattern is one where the union of Base Sets is equal to the union of Link Sets.

:term:`Cover Set`\s assist in the visibility of locating :term:`Ccell`\s to eliminate.  A Cover Set 
is a :term:`Set` of all the Ccells that See each other in the :term:`Chouse` of a :term:`Link Set`.
Any Cover Set Ccell that is not part of a Base Set is Eliminated.  Subtracting the union of Base Sets
from the union of Cover Set's yields the Eliminations.

.. figure:: images/exp-quad-cd1.png
   :name: fig-exp-quad-cd1
   :scale: 65%
   :alt: Exposed Quad
   :align: right
   :figwidth: image

   Exposed Quad Pattern

In the Exposed Quad :numref:`fig-exp-quad-cd1`, B1, B2, B3, B4 are Base Sets, each containing two or
more instances of values W, X, Y, and Z; such that each of the 4 Link Sets see two or more instances of 
each value W, X, Y, Z. That is, L1 sees all the W's present in B1, B2, B3, B4; L2 sees all the X's, L3
all the Y's and L4 all the Z's.  Therefore, by virtue of L1, L2, L3 and L4, each intersecting all the Base Sets,
they hold the Truths for W, X, Y and Z respectively in that house.  W, X, Y, and Z cannot be True anywhere else in 
this House and are Eliminated.

.. figure:: images/not-exp-quad-cd1.png
   :name: fig-not-exp-quad-cd1
   :scale: 65%
   :alt: Not A Exposed Quad
   :align: right
   :figwidth: image

   Not Quite an Exposed Quad Pattern
   
:numref:`fig-not-exp-quad-cd1` has a V instead of a Z in B3.  Here candidate V remains uncovered
after the Link Sets have been applied.  Either the remaining Exposed Quad is True, or V is True.  
But which it is, is undetermined.  Therefore, without additional criteria, it is impossible to draw 
any elimination conclusions.

Base Sets may be any combination of distinct :term:`Chouse`\s.  That is, they can :term:`Overlap`,
but do not :term:`Intersect <intersection>`.  Base Sets do not share :term:`Ccell`\s.  

Extending the :term:`Sudoku Rule` formula to include Equal Multi Order Patterns:

.. _n-base-n-link-sud-rule:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Base Set  <b>B<sub>i</sub></b>  = {P, Q, R, ...}    # P, Q, R, ... are the Ccells making up the Truth in the Base Set <b>B<sub>i</sub></b>
Base Set <b>B<sub>U</sub></b> = U(<b>B<sub>0</sub></b>, <b>B<sub>1</sub></b>, ...,<b>B<sub>n</sub></b>)    # The union of Base Sets <b>B<sub>1</sub></b>, <b>B<sub>2</sub></b>, ..., <b>B<sub>n</sub></b>
Link Set <b>L<sub>i</sub></b> = {K, M, N, ...}    # K, M, N, ... Links Ccells from the Base Set Union that see each other in a non-Base Set Chouse
Link Set <b>L<sub>U</sub></b> = U(<b>L<sub>0</sub></b>, <b>L<sub>1</sub></b>, ..., <b>L<sub>n</sub></b>)    # The union of Link Sets <b>L<sub>1</sub></b>, <b>L<sub>2</sub></b>, ..., <b>L<sub>n</sub></b>
Cover Set <b>C<sub>i</sub></b> = {K, M, N, S, T, ...}    # Contains all the Ccells that See each other in the Link Set House <b>L<sub>i</sub></b>
Cover Set <b>C<sub>U</sub></b> = U(<b>C<sub>0</sub></b>, <b>C<sub>1</sub></b>, ..., <b>C<sub>n</sub></b>)    # The union of Cover Sets <b>C<sub>1</sub></b>, <b>C<sub>2</sub></b>, ..., <b>C<sub>n</sub></b>
&nbsp;
IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # if <u>all</u> the Base Set Ccells are Linked
&nbsp;  THEN <b>Elims</b> = <b>C<sub>U</sub></b> - <b>B<sub>U</sub></b>    # Then Any Cover Sets Ccells that is not in a Base Set is eliminated.
</pre></div></div>
<p><span>`

The :term:`Base Set`\s are non-intersecting :term:`Chouse`\s, each containing a :term:`Truth`.  :term:`Link Set`\s connect the :term:`Ccell`\s of the truths in 
other non-Base Set Chouses.  If all the Base Set Ccells are :term:`Linked <Link>` (union of Base Sets == Union of 
Link Sets), then the :term:`Cover Set` Ccells that are not in this union (union of Cover Sets - Union of Base 
Sets) cannot be True and are eliminated. 

.. _found_emop_exp_ssets:

Cell Base Sets and House Link Sets – Exposed Subsets
+++++++++++++++++++++++++++++++++++++++++++++++++++++

The :term:`Base Set`\s are the :term:`CCell`\s, each containing a :term:`Truth`.  :term:`Link Set`\s are all confined to a :term:`House` in
which all the Base Sets are contained. 

.. figure:: images/locked-exp-trip-eg1.png
   :name: fig-locked-exp-trip-eg1
   :scale: 65%
   :alt: Sudoku Exposed Triple Example
   :align: right
   :figwidth: 359px

   Locked Exposed Triple

   :raw-html:`<mong>..+5.1+2+7+6+8..+2.6.+1+5916..5.4+23.1...6.9.2+538+9+1+6749.+6...8.....2.758.52................||Locked Exposed Triple||34==r7c5,348==r8c5,348==r9c5|r8c4-=34;r9c4-=34;r8c6-=348;r9c6-=348;r4c5-=34;r6c5-=34|+3+4+5+91+2+7+6+8+7+8+2+46+3+1+5916+9+75+84+23+81+4+3+76+29+52+538+9+1+6749+7+6+5+2+48+3+1+4+9+12+3758+652+8+6+4+9+3+1+7+6+3+7+1+8+5+9+4+2</mong>`

The Locked Exposed Triple in :numref:`fig-locked-exp-trip-eg1` has the following :term:`Base Set`\s:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>r7c5</sub></b> = {3r7c5, 4r7c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>r8c5</sub></b> = {3r8c5, 4r8c5, 8r8c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>r9c5</sub></b> = {3r9c5, 4r9c5, 8r9c5}</span></code>.</p></li>
</ul>
<p><span>`

The :term:`Link Set`\s are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>3c5</sub></b> = {3r7c5, 3r8c5, 3r9c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>4c5</sub></b> = {4r7c5, 4r8c5, 4r9c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>8c5</sub></b> = {8r8c5, 8r9c5}</span></code>.</p></li>
</ul>
<p><span>`

And the :term:`Cover Set`\s in Column 4 are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3c5</sub></b> = {3r4c5, 3r6c5, 3r7c5, 3r8c5, 3r9c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>4c5</sub></b> = {4r4c5, 4r6c5, 4r7c5, 4r8c5, 4r9c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>8c5</sub></b> = {8r4c5, 8r6c5, 8r8c5, 8r9c5}</span></code>.</p></li>
</ul>
<p><span>`

And notice that this pattern is also locked to Box 8
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3b8</sub></b> = {3r7c5, 3r8c4, 3r8c5, 3r8c6, 3r9c4, 3r9c5, 3r9c6}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>4b8</sub></b> = {4r7c5, 4r8c4, 4r8c5, 4r8c6, 4r9c4, 4r9c5, 4r9c6}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>8b8</sub></b> = {8r9c5, 8r9c6}</span></code>.</p></li>
</ul>
<p><span>`

The set unions are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>u</sub></b> = {3r7c5, 4r7c5, 3r8c5, 4r8c5, 8r8c5, 3r9c5, 4r9c5, 8r9c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>u</sub></b> = {3r7c5, 3r8c5, 3r9c5, 4r7c5, 4r8c5, 4r9c5, 8r8c5, 8r9c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>U</sub></b> = {3r4c5, 3r6c5, 3r7c5, 3r8c4, 3r8c5, 3r8c6, 3r9c4, 3r9c5, 3r9c6, 4r4c5, 4r6c5, 4r7c5, 4r8c4, 4r8c5, 4r8c6, 4r9c4, 4r9c5 4r9c6, 8r4c5, 8r6c5, 8r8c5, 8r8c6, 8r9c5, 8r9c6}</span></code>.</p></li>
</ul>
<p><span>`

Applying the Sudoku Rule: 
:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # Evaluates True
&nbsp;  THEN <b>Elims</b> = <b>C<sub>U</sub></b> - <b>B<sub>U</sub></b>  # Compute Eliminations
&nbsp;            = {3r4c5, 3r6c5, <del>3r7c5</del>, 3r8c4, <del>3r8c5</del>, 3r8c6, 3r9c4, <del>3r9c5</del>, 3r9c6, 4r4c5, 4r6c5, <del>4r7c5</del>, 4r8c4, <del>4r8c5</del>, 4r8c6, 4r9c4, <del>4r9c5</del>, 4r9c6, 8r4c5, 8r6c5, <del>8r8c5</del>, 8r8c6, <del>8r9c5</del>, 8r9c6} - {3r7c5, 3r8c5, 3r9c5, 4r7c5, 4r8c5, 4r9c5, 8r8c5, 8r9c5}
&nbsp;            = {3r4c5, 3r6c5, 3r8c4, 3r8c6, 3r9c4, 3r9c6, 4r4c5, 4r6c5, 4r8c4, 4r8c6, 4r9c4, 4r9c6, 8r8c6, 8r9c6}
</pre></div></div>
<p><span>`

An unusually productive 14 Ccell Elimination.

.. _found_emop_hid_ssets1:

House Base Sets and Cell Link Sets – Hidden Subsets
++++++++++++++++++++++++++++++++++++++++++++++++++++

:term:`Base Set`\s are :term:`Set`\s of :term:`Ccell`\s, each a :term:`Truth`, all in the same 
:term:`House`.  :term:`Link Set`\s connect Base Set Ccells in :term:`Cell`\s.

.. figure:: images/hid-pair-eg1.png
   :name: fig-hid-pair-eg1
   :scale: 65%
   :alt: Sudoku Hidden Pair Example
   :align: right
   :figwidth: 359px

   Hidden Pair

   :raw-html:`<mong>.6...1..4.48....9+1....+4...+2+4..2.87+5+658+2967+143..65.4+9+2+8+6.....+4+1.+85+4+1.+326.1..4.+6+38.|r1c3-=9;r1c5-=3;r2c5-=3;r3c2-=9;r3c3-=9|Hidden Pair||29#2r1c15|r1c1-=37;r1c5-=578|+96+3+8+21+5+74+248+3+7+5+69+1+7+1+5+6+4+9+8+3+2+4+9+12+387+5+658+2967+143+3+765+14+9+2+8+6+3+9+7+8+2+4+1+5+85+4+1+9+326+71+2+74+5+6+38+9</mong>`

The Hidden Pair in :numref:`fig-hid-pair-eg1` has the following :term:`Base Set`\s:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>2r1</sub></b> = {2r1c1, 2r1c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>9r1</sub></b> = {9r1c1, 9r1c5}</span></code>.</p></li>
</ul>
<p><span>`

The :term:`Link Set`\s are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>r1c1</sub></b> = {2r1c1, 9r1c1}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>r1c5</sub></b> = {2r1c5, 9r1c5}</span></code>.</p></li>
</ul>
<p><span>`

And the :term:`Cover Set`\s in Column 4 are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>r1c1</sub></b> = {2r1c1, 3r1c1, 7r1c1, 9r1c1}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>r1c5</sub></b> = {2r1c5, 5r1c5, 7r1c5, 8r1c5, 9r1c5}</span></code>.</p></li>
</ul>
<p><span>`

The set unions are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>u</sub></b> = {2r1c1, 2r1c5, 9r1c1, 9r1c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>u</sub></b> = {2r1c1, 9r1c1, 2r1c5, 9r1c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>U</sub></b> = {2r1c1, 3r1c1, 7r1c1, 9r1c1, 2r1c5, 5r1c5, 7r1c5, 8r1c5, 9r1c5}</span></code>.</p></li>
</ul>
<p><span>`

Applying the Sudoku Rule: 
:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # Evaluates True
&nbsp;  THEN <b>Elims</b> = <b>C<sub>U</sub></b> - <b>B<sub>U</sub></b>  # Compute Eliminations
&nbsp;            = {<del>2r1c1</del>, 3r1c1, 7r1c1, <del>9r1c1</del>, <del>2r1c5</del>, 5r1c5, 7r1c5, 8r1c5, <del>9r1c5</del>} - {2r1c1, 9r1c1, 2r1c5, 9r1c5}
&nbsp;            = {3r1c1, 7r1c1, 5r1c5, 7r1c5, 8r1c5}
</pre></div></div>
<p><span>`

.. _found_emop_fish:

House Base Sets and House Link Sets – Fish
+++++++++++++++++++++++++++++++++++++++++++

Fish are single Candidate value patterns.  Base Sets are Sets of same value Ccell Truths
each in their own House.  Link Sets connect Ccells from the Base Sets in non-Base Set Houses.

.. figure:: images/swordfish-eg1.png
   :name: fig-swordfish-eg1
   :scale: 65%
   :alt: Sudoku Swordfish Example
   :align: right
   :figwidth: 359px

   Swordfish

   :raw-html:`<mong>+2..197.+4..4.+2.+3+17+9+1+79.+4.3+2.8+9.+43+1+7.27.+19.2.+343+2+4+76.+9.1..2.+1+94.+7+41..+7.+29.+9.+7524.+1.|r1c2-=6;r1c3-=6;r3c9-=6|Swordfish||6r159c279|r7c2-=6;r8c9-=6|+2+3+8197+5+4+6+54+6+2+8+3+17+9+1+79+6+4+53+2+88+9+5+43+1+7+627+6+19+52+8+343+2+4+76+8+9+51+6+52+3+1+94+8+7+41+3+8+7+6+29+5+9+8+7524+6+1+3</mong>`

The Candidate 6 Swordfish in :numref:`fig-swordfish-eg1`, Base Set Houses are highlighted beigé, Link Set Houses highlighted cyan, and intersections 
highlighted light purple.  The Base Sets are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>6r1</sub></b> = {6r1c7, 6r1c9}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>6r5</sub></b> = {6r5c2, 6r5c7}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>6r9</sub></b> = {6r9c2, 6r9c7, 6r9c9}</span></code>.</p></li>
</ul>
<p><span>`

The :term:`Link Set`\s are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>6c2</sub></b> = {6r5c2, 6r9c2}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>6c7</sub></b> = {6r1c7, 6r5c7, 6r9c7}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>6c9</sub></b> = {6r1c9, 6r9c9}</span></code>.</p></li>
</ul>
<p><span>`

And the :term:`Cover Set`\s in Column 4 are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3c5</sub></b> = {6r5c2, 6r7c2, 6r9c2}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>4c5</sub></b> = {6r1c7, 6r5c7, 6r9c7}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>8c5</sub></b> = {6r1c9, 6r8c9, 6r9c9}</span></code>.</p></li>
</ul>
<p><span>`

The set unions are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>u</sub></b> = {6r1c7, 6r1c9, 6r5c2, 6r5c7, 6r9c2, 6r9c7, 6r9c9}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>u</sub></b> = {6r5c2, 6r9c2, 6r1c7, 6r5c7, 6r9c7, 6r1c9, 6r9c9}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>U</sub></b> = {6r5c2, 6r7c2, 6r9c2, 6r1c7, 6r5c7, 6r9c7, 6r1c9, 6r8c9, 6r9c9}</span></code>.</p></li>
</ul>
<p><span>`

Applying the Sudoku Rule: 
:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # Evaluates True
&nbsp;  THEN <b>Elims</b> = <b>C<sub>U</sub></b> - <b>B<sub>U</sub></b>  # Compute Eliminations
&nbsp;            = {<del>6r5c2</del>, 6r7c2, <del>6r9c2</del>, <del>6r1c7</del>, <del>6r5c7</del>, <del>6r9c7</del>, <del>6r1c9</del>, 6r8c9, <del>6r9c9</del>} - {6r5c2, 6r9c2, 6r2c7, 6r5c7, 6r9c7, 6r2c9, 6r9c9}
&nbsp;            = {6r7c2, 6r8c9}
</pre></div></div>
<p><span>`

.. _found_blc_gmop:

Greater Multi Order Patterns
============================

.. topic:: Definition

   Pattern Rank = number of Cover Sets – Number of Base Sets
   
The number of additional Cover Sets needed to intersect all Base Sets determines the order of Rank. 

Rank 0 Patterns
---------------

Rank 0 Patterns have 'n' :term:`Link Set`\s :term:`intersecting <Intersection>` all the 
:term:`Ccell`\s of 'n' :term:`Base Set`\s.  That is,Rank 0 pattern has the same number of Base and 
Cover Sets.  

.. topic:: Rank 0 Rule

   Any non-Base Set Ccell in any Cover Set cannot be True and is eliminated.

The algebra for Rank Zero patterns is documented :ref:`above <found_blc_emop>`.

Rank 0 patterns include Singles, Subsets, Fish and Even Loops.

Rank 1 Patterns
---------------

Rank 1 :term:`GMOP` Patterns need an extra Link Set to Intersect all Base Sets.  This ensures that 
the union of any two Link Sets see a complete Base Set Truth.  Therefore,  where ever two Link Sets overlap, any 
non-Base Set Ccells in their intersecting Cover Sets cannot be True and are eliminated.

Many “Human Solvable” patterns are Rank 1 patterns.  These include Bent Subsets,  Finned Fish in all
their forms, AI Chains in many of their forms, and Unlocked Sets.

.. topic:: Rank 1 Rule

   Any non-Base Set Ccell in the intersection of any two Cover Sets cannot be True and is eliminated.
   
The Sudoku Rule as a Formula for Rank 1 :term:`GMOP`\s:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Base Set  <b>B<sub>i</sub></b>  = {P, Q, R, ...}    # P, Q, R, ... are the Ccells making up the Truth in the Base Set <b>B<sub>i</sub></b>
Base Set <b>B<sub>U</sub></b> = U(<b>B<sub>1</sub></b>, <b>B<sub>1</sub></b>, ...,<b>B<sub>n</sub></b>)    # The union of Base Sets <b>B<sub>1</sub></b>, <b>B<sub>2</sub></b>, ..., <b>B<sub>n</sub></b>
Link Set <b>L<sub>i</sub></b> = {K, M, N, ...}    # K, M, N, ... Links Ccells from the Base Set Union that see each other in a non-Base Set Chouse
Link Set <b>L<sub>U</sub></b> = U(<b>L<sub>1</sub></b>, <b>L<sub>1</sub></b>, ..., <b>L<sub>n+1</sub></b>)    # The union of Link Sets <b>L<sub>1</sub></b>, <b>L<sub>2</sub></b>, ..., <b>L<sub>n+1</sub></b>
Cover Set <b>C<sub>i</sub></b> = {K, M, N, S, T, ...}    # Contains all the Ccells that See each other in the Link Set House <b>L<sub>i</sub></b>
Cover Set <b>C<sub>U</sub></b> = U(<b>C<sub>1</sub></b>, <b>C<sub>1</sub></b>, ..., <b>C<sub>n+1</sub></b>)    # The union of Cover Sets <b>C<sub>1</sub></b>, <b>C<sub>2</sub></b>, ..., <b>C<sub>n+1</sub></b>
&nbsp;
IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # if <u>all</u> the Base Set Ccells are Linked
&nbsp;  THEN <b>Elims</b> = (Union of (Intersections of all Combinations of 2 Cover Sets)) - <b>B<sub>U</sub></b>   
</pre></div></div>
<p><span>`

Any Ccell in the occupied Intersected Cover Pair that is not of the Union of Link Sets cannot 
be True and is eliminated.

Rank R Patterns
---------------

Rank 'r' :term:`GMOP` patterns need 'n + r' :term:`Link Set`\s to :term:`intersect <Intersection>` 
all the :term:`Ccell`\s of 'n' :term:`Base Set`\s.  This ensures the union of any r + 1 Link Sets 
will always see a complete Base Set truth.  Therefore, where ever r + 1 Link Sets overlap, any 
non-Base Set Ccels in their intersecting Cover Sets cannot be True and are eliminated.

Many of the most difficult puzzles have patterns that can be found and resolved as Rank 2 and higher
freeform Base / Cover Set patterns.  A deeper understanding of Sudoku logic comes from appreciating 
rank 'r' logic.

.. topic:: Rank 'r' Rule

   Any non-Base Set Ccell in the intersection of any 'r + 1'two Cover Sets cannot be True and is eliminated.

The Sudoku Rule as a Formula for Rank r :term:`GMOP`\s:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Base Set  <b>B<sub>i</sub></b>  = {P, Q, R, ...}    # P, Q, R, ... are the Ccells making up the Truth in the Base Set <b>B<sub>i</sub></b>
Base Set <b>B<sub>U</sub></b> = U(<b>B<sub>1</sub></b>, <b>B<sub>1</sub></b>, ...,<b>B<sub>n</sub></b>)    # The union of Base Sets <b>B<sub>1</sub></b>, <b>B<sub>2</sub></b>, ..., <b>B<sub>n</sub></b>
Link Set <b>L<sub>i</sub></b> = {K, M, N, ...}    # K, M, N, ... Links Ccells from the Base Set Union that see each other in a non-Base Set Chouse
Link Set <b>L<sub>U</sub></b> = U(<b>L<sub>1</sub></b>, <b>L<sub>1</sub></b>, ..., <b>L<sub>n+r</sub></b>)    # The union of Link Sets <b>L<sub>1</sub></b>, <b>L<sub>2</sub></b>, ..., <b>L<sub>n+1</sub></b>
Cover Set <b>C<sub>i</sub></b> = {K, M, N, S, T, ...}    # Contains all the Ccells that See each other in the Link Set House <b>L<sub>i</sub></b>
Cover Set <b>C<sub>U</sub></b> = U(<b>C<sub>1</sub></b>, <b>C<sub>1</sub></b>, ..., <b>C<sub>n+r</sub></b>)    # The union of Cover Sets <b>C<sub>1</sub></b>, <b>C<sub>2</sub></b>, ..., <b>C<sub>n+1</sub></b>
&nbsp;
IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # if <u>all</u> the Base Set Ccells are Linked
&nbsp;  THEN <b>Elims</b> = (Union of (Intersections of all Combinations of 'r + 1' Cover Sets)) - <b>B<sub>U</sub></b>   
</pre></div></div>
<p><span>`

If the 'n + r' :term:`Link Set`\s intersect the all the Ccells of all 'n' non-intersecting :term:`Base Set`\s then any Ccell
found in the intersection of any 'r + 1' Cover Sets cannot be True and is Eliminated.

Some More Examples
==================

.. figure:: images/finned-x-wing-eg1.png
   :name: fig-finned-x-wing-eg1
   :scale: 65%
   :alt: Sudoku Finned-X-Wing Example
   :align: right
   :figwidth: 359px

   Finned X-Wing

   :raw-html:`<mong>+156+87+49+3+2.4+762.+18+528....+4+7+6....8.+5+9.73....618+8.5...+32.........+3.7.5...49....487.1||Finned X-Wing||3c35r38,r9c3;3r8c1-3r9c3|r8c1-=3|+156+87+49+3+2+34+762+9+18+528+9+1+5+3+4+7+6+4+6+1+38+2+5+9+773+2+4+9+5618+8+95+7+1+6+32+4+9+1+4+2+6+7+8+5+3+67+85+3+1+249+5+2+3+9487+61</mong>`

The Rank 1 puzzle pattern on the right is a Finned X-Wing ``3c35r38,r9c3``.
The Base Sets are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>3c3</sub></b> = {3r3c3, 3r8c3, 3r9c3}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>B<sub>3c5</sub></b> = {3r3c5, 3r8c5}</span></code>.</p></li>
</ul>
<p><span>`

The Link Sets are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>3r3</sub></b> = {3r3c3, 3r3c5}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>3r8</sub></b> = {3r8c3, 3r8c5}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>L<sub>3b7</sub></b> = {3r8r3, 3r9c3}</span></code>.</p></li>
</ul>
<p><span>`

And the Cover Sets are:
:raw-html:`</span></p>
<ul class="simple">
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3r3</sub></b> = {3r3c3, 3r3c4, 3r3c5, 3r3c6}</span></code>,</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3r8</sub></b> = {3r8c1, 3r8c3, 3r8c5, 3r8c6}</span></code>, and</p></li>
<li><p><code class="docutils literal notranslate"><span class="pre"><b>C<sub>3b7</sub></b> = {3r8c1, 3r8r3, 3r9c1, 3r9c3}</span></code>.</p></li>
</ul>
<p><span>`

Applying the Sudoku Rule: 
:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>IF (<b>B<sub>U</sub></b> == <b>L<sub>U</sub></b>):    # Evaluates True
&nbsp;  THEN <b>Elims</b> = (<b>C<sub>3r8</sub></b> & <b>C<sub>3b7</sub></b>) - <b>B<sub>U</sub></b>  # Compute Eliminations
&nbsp;            = {3r8c1, 3r8r3} - {3r3c3, 3r8c3, 3r9c3, 3r3c5, 3r8c5}
&nbsp;            = {3r8c1}
</pre></div></div>
<p><span>`


The intersection of :raw-html:`<code class="docutils literal notranslate"><span class="pre"><b>C<sub>3r8</sub></b> & <b>C<sub>3b7</sub></b></span></code>`
is the only intersection of pairs of Link Sets that yields a not empty result.

Double-checking this result intuitively, either the Fish pattern will be True or the Fin will be
True.  Therefore, any Ccell that is any Cover Set Ccell outside the
intersections that can also see the Fin cannot be True and can be eliminated.

|

.. figure:: images/two-string-kite-eg1.png
   :name: fig-two-string-kite-eg1
   :scale: 65%
   :alt: Sudoku Two String Kite Example
   :align: right
   :figwidth: 359px

   Two String Kite

   :raw-html:`<mong>+3617..+2+95842+395+6+7+1.5.+26+14+8+3+1.+8+5+2+6.3+4+625....+1+8.+341..+526+4..+6+1.+8+5+2+58...+2+1672+1+6+8+5+7349||Two String Kite||9r6c6=9r6c1~9r4c2=9r7c2,9r6c6-9r7c6-9r7c2|r7c6-=9|+3617+8+4+2+95842+395+6+7+1+75+9+26+14+8+3+1+7+8+5+2+6+93+4+625+4+3+9+7+1+8+9+341+7+8+526+4+9+7+6+1+3+8+5+2+58+3+9+4+2+1672+1+6+8+5+7349</mong>`

The Rank 1 puzzle pattern on the right is a Two String Kite
``9(r6c6=r6c1-r4c2=r7c2)``.  This pattern is also an example of two base sets
crossing over each other without intersecting.  The two Base Sets for Candidate 9 are:

*  ``BS9r7 = {9r6c1, 9r6c6}``, and
*  ``BS9c2 = {9r4c2, 9r7c2}``.

The intersecting Cover Sets are:

*  :raw-html:`<mong>CS9b4 = {9r4c2, 9r6c1}</mong>`,
*  :raw-html:`<mong>CS9r7 = {9r7c2, 9r7c6}</mong>`, and
*  :raw-html:`<mong>CS9c6 = {9r6c6, 9r7c6}</mong>`

|
|

Applying the Sudoku Rule for Rank 1 Patterns::

   IF (BS9r7 | BS9c2) & (CS9b4 | CS9r7 | CS9c6) == (BS9r7 | BS9c2)
      THEN Elims = ((CS9b4 & CS9r7) | CS9r4 & CS9c6) | (CS9r7 & CS9c6)) – (BS9r7 | BS9c2)

Evaluating the IF condition:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>(BS9r7 | BS9c2) & (CS9b4 | CS9r7 | CS9c6) == (BS9r7 | BS9c2)
{9r6c1, 9r6c6, 9r4c2, 9r7c2} & {9r4c2, 9r6c1, 9r7c2, <del>9r7c6</del>, 9r6c6}{9r6c1, 9r6c6, 9r4c2, 9r7c2}
{9r6c1, 9r6c6, 9r4c2, 9r7c2} == {9r6c1, 9r6c6, 9r4c2, 9r7c2}
True</pre>
</div></div>
<p><span>`

Because the IF condition evaluates True, the Elims are computed:

:raw-html:`</span></p>
<div class="highlight-none notranslate"><div class="highlight">
<pre>Elims = ((CS9b4 & CS9r7) | CS9r4 & CS9c6) | (CS9r7 & CS9c6)) – (BS9r7 | BS9c2)
Elims = ({9r4c2, 9r6c1} & {9r7c2, 9r7c6}) | ({9r4c2, 9r6c1} & {9r6c6, 9r7c6}) | ({9r7c2, 9r7c6} & {9r6c6, 9r7c6}) – {9r6c1, 9r6c6, 9r4c2, 9r7c2}
Elims = ({}) | ({}) | ({9r7c6}) - {9r6c1, 9r6c6, 9r4c2, 9r7c2}
Elims = {9r7c6}</pre>
</div></div>
<p><span>`


As a Two String Kite, if ``9r6c6`` is False, ``9r6c2`` is True, ``9r4c2`` is False, and ``9r2c7``
is True.  Similarly walking the links in the opposite direction, if ``9r2c7`` is False, then
``9r6c6`` is True.  This pattern identifies a :ref:`Robust link <found_cc_robust_links>`
``9r6c6|~|9r7c2``. Recall that at least one end of a Robust Link must be True, therefore any Ccell
that can see both ends cannot be True and can be eliminated.  ``9r7c6`` is such a Ccell which can
be eliminated.

|

.. figure:: images/uls-chain-cd1.png
   :name: fig-uls-chain-cd1
   :scale: 65%
   :alt: Sudoku Unlocked Set Chain Candidate Diagram Example
   :align: right
   :figwidth: 359px

   Unlocked Set Chain Candidate Diagram

The Rank 1 Puzzle pattern on the right, is both an XY-Chain:
``(Z=Y)r1c4~(Y=X)r5c4~(X=W)r5c7~(W=Z)r6c8``, and a 2 Node Unlocked Set Chain:
``Z(YZr1c4,XYr5c4)X(WXr5c7,WZr6c8)Z``.

As a Rank 1 Base Set / Cover Set Pattern, the 4 Base Sets are the Cells:

*  ``BSr1c4 = {Yr1c4, Zr1c4}``
*  ``BSr5c4 = {Xr5c4, Yr5c4}``
*  ``BSr5c7 = {Wr5c7, Xr5c7}``
*  ``BSr6c8 = {Wr6c8, Zr6c8}``

3 of the 5 Cover Set connecting the 4 Base Sets are:

*  ``CSc4 = {Yr1c4, Yr5c4}``
*  ``CSr5 = {Xr5c4, Xr5c7}``
*  ``CSb6 = {Wr5c7, Wr6c8}``

Two equally valid possibilities for the remaining two cover sets exist, the one pair being:

*  ``CSc4 = {Zr1c4, Zr6c4}``
*  ``CSr6 = {Zr6c4, Zr6c8}``

Evaluating the Sudoku Rules Algebraic expression for these Base Sets and Cover Sets yields the
elimination of Zr6c4.

The other pair of equally valid Cover Sets are:

*  ``CSc8 = {Zr1c8, Zr6c8}``
*  ``CSr1 = {Zr1c4, Zr1c8}``

Evaluating the Sudoku Rules Algebraic expression for these Base Sets and Cover Sets yields the
elimination of Zr1c8.

As an XY Chain the Ccells in the Bi Value cells are the Strong links of the AI Chain.  They are
weakly linked by a common value Ccell connecting two Bi Value Ccells.  The Chain ends are ``Zr1c4``
and ``Zr6c8`` and the Chain ensures that neither end is simultaneously False, at least one end is True,
which it is yet to be determined.  Therefore, any Ccell that can see both ends of the chain
cannot be True, and can be eliminated.

As the 2 Node Unlocked Set Chain, X is the only member in the RCS connecting the two ULS’s.  The
other common candidate is “Z”.  If X is True in the first ULS, then Z is True in ULS2, and if X is
True in the second ULS, then Z is True in the first ULS.  This locks  ``Zr1c4`` and ``Zr6c8`` are locked
into “A Truth”.  Therefore, any same valued (Z) Ccell that can see all the elements of this
'A Truth' cannot be True and can be eliminated.

So as either an XY-Chain or a ULS-Chain, ``Zr1c8`` and ``Zr6c4`` can be eliminated, and Base/Cover Set
logic can be used to verify the pattern resolution.

Parting Comment
===============

The skill in Sudoku still remains finding Patterns.  Having found probable patterns, the 
Sudoku Formula developed here can be used to verify patterns and calculate eliminations.
