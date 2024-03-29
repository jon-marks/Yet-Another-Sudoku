.. title:: Yet Another Sudoku | Glossary

.. include:: globals.inc

**************************
Glossary and Abbreviations
**************************

https://www.sudocue.net/glossary.php and http://sudopedia.enjoysudoku.com/Terminology.html 

.. glossary::

   **AI**
      Abbreviation for :term:`Alternating Inference`.

   **AIC**
      Abbreviation for :term:`Alternating Inference Chain`.

   **AIL**
      Abbreviation for :term:`Alternating Inference Loop`.

   **AIN**
      Abbreviation for :term:`Alternating Inference Net`.

   **Alternating Inference**
      A pattern where adjacent links between nodes alternate strong and weak.

   **Alternating Inference Chain**
      A :term:`Chain` linking :term:`Node`\s with alternating :term:`Strong Link`\s and
      :term:`Weak Link`\s.

   **Alternating Inference Loop**
      An :term:`Alternating Inference Chain` that loops back on itself.

   **Alternating Inference Net**
      A network of :term:`Node`\s where the Links at consecutive net levels alternate.

   **Band**
      See :term:`Chute`.

   **Base Set**
      A Base Set is a :term:`Set` of one or more :term:`Ccell`\s in a :term:`Chouse` forming a 
      :term:`Truth`.

   **BEQ**
      Abbreviation of :term:`Bent Exposed Quad`

   **Bent Exposed Quad**
      A pattern comprising four Candidates in four Cells spanning two Intersecting :term:`House`\s,
      where only one :term:`Unrestricted Candidate` exists.

   **Bi-value Cell**
      A cell on a Sudoku board containing only 2 candidate values.  A :term:`Strong Link` exists
      between these two candidates in that cell.

   **Block**
      See :term:`Box`.

   **Board**
      A solved, filled or completed puzzle.

   **Box**
      A 3x3 Grid.  A Sudoku :term:`Grid` is made up of 9 boxes, 3 accross, 3 down.
      Also known as a Block.

   **Buddy**
      See :term:`Peer`.

   **Candidate**
      A possible solved value for an unsolved cell.  This definition is only a reference to the
      candidate value, not to any :term:`Cell` location on the :term:`Grid`.

   **Ccell**
      A three-dimensional tuple uniquely identifying a candidate element by value, row,
      and column in a Sudoku Grid.

   **Cell**
      A location in a Sudoku grid which either contains a :term"`Given` or into which a 
      :term:`Solved Value` is placed.

   **Chain Patterns**
      The collective noun for Chain, Net and Loop patterns, typically referring
      to :term:`Alternating Inference` Chains

   **Chain**
      A shortening of the term :term:`Inference Chain`, a stream of inference links connecting Ccells
      to each other.
   
   **Chouse**
      Collective noun for :term:`House` and :term:`Cell`.

   **Chute**
      A grouping of three :term:`Box`\es in a row or a column.
      Three boxes in a row is a :term:`Floor`.  Three boxes in a column is a :term:`Tower`.
      Also known as a Band.

   **Column**
      A vertical line of 9 cells in a Sudoku :term:`Grid`.

   **Conditional Logic**
      The process of asserting a Premise and following a sequence of inferences to a
      possible logical outcome.  See :ref:`found_prem_inf`.

   **Conjugate Pair**
      The only two same value candidates in a house forming a :term:`Strong Link`.  This is a
      reference to the candidates not the links between them – a subtle distinction.

   **Cover Set**
      A Cover Set is a :term:`Set` of all the :term:`Ccell`\s that :term:`See` each other in the 
      :term:`Chouse` of a :term:`Link Set`.
      
   **Eliminations**
      Removing Ccells in puzzles that have been determined impossible to be True.

   **EMOP**
      Abbreviation of :term:`Equal Multi Order Pattern`.
      
   **End Node**
      In an AI-Chain of Nodes, the End Nodes mark the start and end of Chain.
      
   **Equal Multi Order Pattern**
      (abr: :term:`EMOP`\) A Pattern with 'n' :term:`Base Set`\s and 'n' or more :term:`Link Set`\s
      where one or more groupings of 'n' Link Sets intersects as all Base Set :term:`Ccell`\s.
      
   **Fin**
      Extra :term:`Ccell`\s in :term:`Base Set`\s of Fish patterns.
      
   **Floor**
      A row oriented :term:`Chute`.
      
   **GMOP**
      Abbreviation of :term:`Greater Multi Order Pattern`.
      
   **Greater Multi Order Pattern**
      (abr: :term:`GMOP`\) A pattern with 'n' :term:`Base Set`\s and needing 'n + r' :term:`Link Set`\s
      to :term:`Intersect <Intersection>` all the Base Set :term:`Ccell`\s. :term:`EMOP`\s are a 
      special case of GMOPs where 'r' = 0.  

   **Given**
      An initially placed value on a Sudoku Puzzle.  It is the Given placements that make the puzzle.

   **Grid**
      9x9 grid, subdivided into 9  – 3x3 :Term:`Box`\es  (Blocks) on to which Sudoku puzzles are
      spatially represented.

   **Group**
      See :term:`House`.

   **House**
      A specific 9 cell of a :term:`Row`, :term:`column` or :term:`Box`.  Also known as a Group, 
      Sector or Unit.

   **Inference Chain**
      A stream of inference links connecting Ccells to each other.
      
   **Interior Node**
      In an AI-Chain of Nodes, the Interior Nodes lie between the :term:`End Node`\s.

   **Intersection**
     The :term:`Ccell`\s common to two or more :term:`Set`\s where they :term:`Overlap`.

   **Line**
      Either a :term:`Row` or a :term:`Column`.

   **Link**
      A logical relationship between two Nodes (Ccells).  The logical relationship can be one of
      a :term:`Weak Link`, a :term:`Strong Link` or a :term:`Robust Link`.
      See :ref:`found_prem_inf`
      
   **Link Set**
      A :term:`Set` of one or more :term:`Ccell`\s in a non-:term:`Base Set` :term:`Chouse` that are
      in any Base Set.
      
   **MOP**
      Abreviation of :term:`Multi Order Pattern`.
      
   **Multi Order Pattern**
      Abr: :term:`MOP`.  A Pattern with multiple :term:`Base Set`\s :term:`Intersected <Intersection>`
      by multiple :term:`Link Set`\s.  There are Lesser, 
      :term:`Equal <Equal Multi Order Pattern>` and :term:`Greater <Greater Multi Order Pattern>`
      MOPS depending on the nature of Link Set intersections. See :ref:`Multi Order Patterns <found_blc_mop>`. 
      
   **Loop**
      An (:term:`AI`) :term:`Chain` that loops back on itself closing the chain.

   **Node**
      A :term:`Ccell` that is linked by :term:`Conditional Logic` to other nodes in a pattern.

   **Overlap**
      The :term:`Cell`\s where two or more :term:`Chouse`\s overlap.
      
   **Parity**
      The collective pronoun for the terms Odd and Even, which are the parity of the sequence
      numbers assigned to a :term:`SLN` or :term:`SLC`.

      In an SLC, applying the premise that one end is True, consecutive nodes will alternate
      True / False until the chain end is reached.  Similarly, applying the premise that that end is
      False, consecutive nodes will alternate False / True until the chain end is reached.

      In an SLN, applying the premise that the root is True, nodes at consecutive node
      levels will alternate True / False through to all the leaves.  Similarly, applying the premise
      that the root is False, nodes at consecutive node levels will alternate False / True through
      to all the leaves.

      Therefore, in either an SLC or SLN, adjacent Nodes alternate in :term:`State`. Although the
      State of a Node may not be known, its neighbours will always have opposing State.
      Consecutively numbering the Nodes in an SLC or Node levels in an SLN, the numbers, and hence
      the Nodes will either have Odd or Even parity.

      Parity (Odd or Even) is used to represent State where the actual State value (True or False)
      is not known.  All Nodes in an SLN with the same Parity will have the same State, even though
      the actual value of that State is yet to be determined.

   **Pattern**
      An arrangement of Ccells that have the potential of yielding eliminations or placements

   **Pattern Cell**
      Reference to a Cell containing Candidates belonging to a pattern

   **PE**
      A Abbreviation of :term:`Potential Elimination`, loosely synonymous with :term:`Ccell`.

   **Peer**
      A :term:`Ccell` that can :term:`See` other Ccells.  Peers are a set of Ccells that see
      each other.

   **Placement**
      Placing of a single solved value in a Cell.

   **Pincer**
      A :term:`Cell` containing :term:`Candidate`\s outside the :term:`Intersection` of two
      :term:`Line`\s, a :term:`Row`, and a :term:`Column`.  Referred to with :term:`Pivot`.

   **Pivot**
      A :term:`Cell` containing :term:`Candidate`\s in the :term:`Intersection` of two
      :term:`Line`\s, a :term:`Row`, and a :term:`Column`.  Reffered to with :term:`Pincer`.

   **Potential Elimination**
      A reference to a Candidate that is an element of the solution set of Candidates in that Cell.
      Through the application of :term:`Conditional Logic` Potential Eliminations are removed from
      this set until the last value remains as the solution for that Cell.

   **Puzzle**
      A partially completed Sudoku in a puzzle, it may only be populated with the givens or with
      givens and some solved values.

   **Restricted Candidate**
      In a Bent Exposed Subset, a Restricted Candidate is a Candidate that :term:`See`\s all
      instances of its value in the Bent Subset grouping.  This is a special case of a
      :term:`Restricted Candidate Set` (:ref:`found_tsf_nls`) with a single
      member.

   **Restricted Candidate Set**
      In :ref:`found_tsf_nls`, a Restricted Candidate Set is that set of Candidates that
      can :term:`See` all instances of its value in the Unlocked Sets pattern.

   **Robust Link**
      An inference between two Ccells at the ends of a Strongly Ended Alternating Inference Chain.
      Neither end can be simultaneously False, and at least one end is always True

   **Row**
       A horizontal line of 9 cells in a Sudoku :term:`Grid`.

   **SE-AIC**
      Strong Link Ended Alternating Inference Chain.  A chain pattern of even Node count where the
      end links are both Strong.  The ends of a SE-AIC form a :term:`Robust Link`.

   **Sector**
      See :term:`House`.

   **See**
      :term:`Ccell`\s that have an :term:`Link` between them are said to see each other.

   **Set**
      A collection of :term:`Ccell`\s that :term:`See` each other in a :term:`Chouse`.

   **SLC**
      Strongly Link Chain.  A Chain where all the links between Nodes are strong. An SLC is a special
      case of an AIC where every alternate link is masquerading as a Weak Link.

   **SLN**
      Strongly Link Net.  A Net where all the links between Nodes are strong.

   **Solved Value**
      A :term:`Ccell` that is part of the solution.   

   **State**
      Collective pronoun for the terms True and False, which are the conditions of a :term: `Ccell`
      in a :term: `Cell`.  A :term:`Ccell` can either be True or False in a Cell.  Only one Ccell
      can be True in a cell becoming the placed value.

   **Strong Link**
      An inference between two Ccells where neither can be simultaneously False, nor simultaneously
      True.  If one Ccell is True, the other is False and vice-versa.

   **Sudoku Rule**
         A Sudoku Puzzle has a unique solution where each :term:`Cell` in the 9 x 9 :term:`Grid`
         contains a number between 1 and 9 that only occurs once in each of the 9 :term:`Row`\s, 
         9 :term:`Column`\s, and 9 - 3 x 3 :term:`Box`\es.

   **Super-Node**
      The set of :ref:`'same parity/state nodes' in a Strong Linked Chain <hsp_cln_super-node>`, Net or
      Loop, that is strongly linked to the opposing Super-Nodes.

   **Tower**
      A Column oriented :term:`Chute`.

   **Truth**
      A Set of :term:`Ccell`\s that :term:`See` each other in a :term:`Chouse` where one of 
      the Ccells is True, that is the :term:`Solved Value`.

   **ULS**
      Ulocked Set, see :ref:`found_tsf_nls`.

   **Union**
      All the Cells of two intersecting :term:`House`\s.

   **Unit**
      See :term:`House`.

   **Unrestricted Candidate**
      In a Bent Exposed Subset, an Unrestricted Candidate is a Candidate that that cannot
      :term:`See` all instances of its value in the Bent Subset grouping.  This is a special
      case of an :term:`Unrestricted Candidate Set` (:ref:`found_tsf_nls`) with a single
      member.

   **Unrestricted Candidate Set**
      In :ref:`found_tsf_nls`, an Unrestricted Candidate Set is that set of Candidates that
      cannot :term:`See` all instances of its value in the Unlocked Sets pattern.

   **WE-AIC**
      Weak Link Ended Alternating Inference Chain.  A chain pattern of even Node count where the
      end links are both Strong.

   **Weak Link**
      An inference between two Ccells where neither can be simultaneously True, and at least one end
      is always False.  A Weak Link is formed by 3 or more same valued candidates in a
      house or three or more candidates in a cell.

   **YMMV**
      "Your milage may vary". Your opinion or experience may be different to mine.





Intersection/Overlap:	Where 2 Groups/Houses share one or more cells.  The shared cell(s) where a row and column cross, or when a row or column crosses a block.
Conflict/Contradiction/Error:	Two or more cells with the same value in a Group/House.
Minimal Puzzle:	A minimal puzzle is that where no more holes can be dug without the puzzle becoming invalid, that is having multiple solutions. 
Slink:	Strong link in a chain or a loop
Wink	Weak link in a chain or a loop 
Ccell	Refers to a candidate value in a cell as a unique identifier comprising the candidate, row and column coordinates as a tuple.  For example 3r2c8 candidate 3 in row 2, column 8.
This reference is useful when referring to specific candidates in specific cells, and is used extensively in the explanation of many logic techniques and their algorithms.   In solving puzzles Ccells are whittled away (eliminated) using logic techniques until only one Ccell remains as the solution for that cell.
Sudoku Rules	The collective term for: 
* The numbers 1 through 9 only occur once in each row, column and block. 
* Only one unique solution. 
Conjugate Pair.	The two same value candidates in a house forming a strong link. 
Bi-Value Cell (BVC)	A cell containing only two candidates. 
AIC	Alternating Inference Chain.  A chain comprising alternating Weak and Strong links. 
Linebox	The intersection of a line (row or column) and a box comprising only three cells. 
Rowbox	The intersection of row and box comprising only three cells 
Colbox	The intersection of a column and box comprising only three cells.
