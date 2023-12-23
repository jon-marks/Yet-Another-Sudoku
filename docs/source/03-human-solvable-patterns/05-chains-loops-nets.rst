.. title:: Yet another Sudoku | Human Solvable Patterns | Chains, Loops and Nets

.. include:: ..\globals.inc


.. _human-solvable-chain-patterns:

======================
Chains, Loops and Nets
======================

This section builds on Link and Chain Basics
3.4.1.   X-Chains and -Loops
X chains and loops are a special case of AI-Chains where all the nodes have the same candidate value.  The X-Chain is a a SE-AIC creating a Robust link between its ends.  That is at least one of the Ends is True.  Therefore any Ccell that can see both the end nodes of the chain cannot be be True and can be eliminated.

An X Chain is validated by walking it, starting at one end with “not” the candidate value, to finish at the other end with the candidate value.  Then doing the same from the other end, i.e. starting at the other end with “not” the candidate to finish with the candidate value at the starting end.

Type 1 SE-AIC Eliminations (any ccell that sees both ends of the chain) are the only type available to X-Chains, as Type 2 and Type 3 apply to different chain end candidate values.

An X-Loop is an X-Chain that links back on itself.
https://www.sudokuwiki.org/X_Cycles
https://www.sudokuwiki.org/X_Cycles_Part_2
https://www.sudokuwiki.org/Grouped_X_Cycles
http://zitowolf.net/sudoku/strategy.html#chains

X Loops with an even number of alternating strong and weak links, and an even number of AIC chain nodes.  I term these Even X-Loops.  Type 3 SL Eliminations (any ccell that sees both an odd and even node).  Type 1 and Type 2 SL Eliminations rely on chains with multiple candidate values.

X-loops with an odd number of nodes will have either have:
    • Two adjacent strongly linked nodes.  This pattern is resolved by placing the candidate value of the ccell in the pivot of the two strong links.
    • Two adjacent weakly linked nodes.  This is exactly the same as a ccell in the pivot of the two weak links seeing the ends of a SE-AIC.

Strategies to find X-Chains:
    • Choose a candidate, identify all it’s conjugate pairs (strong links) and to link the strong links to each other.
    • Pick a start and end of a chain and build the alternating link chains simultaneously from both end seeing if they can connect.

3.4.1.1.   Skyscrapers (3 Link X-Chain)
A skyscraper has two parallel strong links connected by a weak link.  Any same value ccells that the two open ends of the skyscraper see, can be eliminated.
3.4.1.2.   Two String Kites (3 Link X-Chains)
A Two String Kite has a row strong link and a column strong link, weakly linked in a box.  Any same value ccells that the two open ends of the skyscraper see, can be eliminated.
3.4.1.3.   Turbot Fish (Other 3 Link X Chains)
All other 3 Link X Chain pattern.  That is those three link X-Chains that start or end with a strong link in a box.
3.4.1.4.   Longer X-Chains [Clean UP]
These are X-Chains with an odd number of links > 3.  As these X-Chains start and end with strong links, the ends are strongly linked, and therefore any same value candidate that both ends can see can be eliminated, even if it is an internal node/ccell of the chain.

If the chain ends are in the same house they form an Even X-Loop. If the chain ends are in different or same chute, then any candidate that can see both end candidates can be eliminated.

...+7..5.+9.32519...79+56...1..8.+9+65...+9.64371...+7.2+8+1.9..1...2.67..+917685...7..+4..+1|r2c1-=6;r4c1-=4;r7c1-=3|X-Chain|4r3c5=4r1c5-4r1c2=4r8c2-4r8c9=4r7c7|r3c7-=4

9.3....+75.467.....17.....+4+66..83.7.+1..71.64....1.79.+62.....+7.39.....562+77.....8.4|r1c5-=28;r2c1-=8;r2c5-=18;r2c6-=8;r2c8-=9;r3c4-=9;r3c5-=8;r5c1-=8;r5c2-=8;r6c1-=5;r7c5-=2;r8c5-=9;r9c5-=29|X-Chain|5r2c1=5r2c5-5r5c5=5r6c4-5r6c7=5r7c7|r7c1-=5



same chute












Need to find an X-chain with ends in same house.


https://www.sudopedia.org/wiki/X-Chain
3.4.1.5.   Even Number of Links X-Loops (Even X-Loops)
[TODO – this explanation is partially incorrect about base / cover set logic, true about weak links becoming strong links – fix.]
Even length X-Loops have the same number of strong and weak links.  Note that a strong link can masquerade as a weak link.  From Base/Cover Set Logic, and solving fish below, we are dealing with Rank Zero logic where the strong links form the base sets and the weak links form the cover sets.  Here, the same value candidates in the houses of the weak links that are not part of the chain can be eliminated.  This is because when the chain is closed becoming the loop, it forces either of the two connected candidates in the house of the weak links to be true.  Because only one of those candidates is true, all other candidates in that weak link house can be eliminated.

Minimal fish are a type of X-Loops.  A Minimal fish is is a fish where each cover only intersects the bases twice.  X-loops, unlike minimal fish are not limited to rows and columns, and can include boxes/blocks when forming loops.

The following example identifies the following Even X-Loop of 6 links:
   8(r3c2=r7c2-r8c3=r8c9-r9c7=r3c7-r3c2).

The weak link in r3 results in the eliminations r3c39-=8,
The weak link in b7 results in the elimination of r7c3-=8, and
The weak link in b9 results in the elimination of r7c9-=8.

By the way with the puzzle in it’s current state, it is also possible to identify other patterns.  There are two – two string kites. 8(r1c7=r1c9-r3c7=r9,c7) resulting in r9c6-=8, and
8(r8c3=r8c9-r9c7=r3c7) resulting in r3c3-=8.  There is also a Swordfish 8r128c369, resulting in the same eliminations as the 6 link X-Loop.




3.4.1.6.   Odd Number of Links X-Loops (Strong and Weak X-Loops) [Clean Up]
There are two types of odd number of links X-loops:

    • Weak X-Loop:.  This is an X-Loop with two adjacent weak links.  This is equivalent to an X-Chain where the two strongly linked ends both “see” the same same value candidate which can be eliminated.  As a Weak X-Loops is simply an X-Chains, and in YAS, is resolved as such.
    • Strong X-Loop.  This is an X-Loop with two adjacent strong links.  In this pattern, the cell connecting the two strong links can be assigned the candidate value.

The following example illustrates and explains the logic behind Strong X-Loops.


The pattern 6(r2c2=r4c2-r4c6=r1c6=r2c4-r2c2) is found, where ccell 6r1c6 joins two strong links.
    • If ccell 6r1c6 is False, then both ccells 6r2c4 and 6r4c6 must be True.  But the strong link 6(r2c2=r4c2) that sees both 6r2c4 and 6r4c6 restricts them from both being simultaneously True.  Therefore it is not possible for 6r1c6 to be False.
    • If ccell 6r1c6 is True, then both ccells 6r2c4 and 6r4c6 must be False.  The strong link 6(r2c2=r4c2) that sees both 6r2c4 and 6r4c6 does not constrain them from both being simultaneously False.  Therefore it is possible for 6r1c6 to be True.
    • As 6r1c6 may be True and can’t be False.  And 6r1c6 can only assume a value of True or False, 6r1c6 must be True:  r1c6:= 6.


Another Stong X-Loop example, courtesy of: http://www.taupierbw.be/SudokuCoach/SC_XCycle.shtml

This example results in the r1c3:=2 assignment.

3.4.1.7.   Grouped Linked X-Chains and Loops [Clean Up]
It is very possible to find group linked x-chains, including Two-String Kites and Turbot Fish. Because a box and line intersection is required to make a group link, by definition a Skyscraper (which is two strong links along parallel lines weakly connected with a perpendicular line) which does not have a box cannot have a group linked variant.

Group Linked Even X-Loop, from http://www.taupierbw.be/SudokuCoach/SC_XCycle.shtml resulting in the elimination of the highlighted 1’s.  Note the group link of 1’s in box 7.

Group Linked X-Chains, from http://www.taupierbw.be/SudokuCoach/SC_XCycle.shtml resulting in the elimination:  r1c2 -= 5.  This Group Linked X-Chain pattern is described by:
	5r46c2=5r45c1~5r9c1=5r9c8-5r2c8=5r1c9

At this stage of the puzzle, YAS finds a different Group Linked X-Chain pattern:
   5r7c7=5r7c3-5r3c3=5r3c46~5r2c6=5r2c8,

which yields the elimination r9c8-=5.

Source http://forum.enjoysudoku.com/grouped-x-cycle-or-grouped-er-t34307.html







3.4.2.   XY-Chains, -Loops and -Nets
XY-Chains and loops are a special case of AI-Chains where the chain is made up of only bi-value cells and rely on and only use the strong links between the two Candidates in the Bi-Value cells.  Therefore a chain is formed by entering the cell with one ccell of the conjugate pair and leaving the cell on the other ccell.  All the links connecting cells can be weak.  A Y-Wing is the shortest XY Chain that can exist made up of 6 Ccell nodes and 5 links over 3 cells. Minimal Bent Exposed Subsets (comprising only bi-value cells (conjugate pairs) are also XY-chains.

The strategy to finding XY-chains is to identify all bi-value cells and try linking them together in various possible permutations in the attempt to build a chain that starts and ends with same value.

An XY-Loop is a XY-Chain that loops back on itself.  That is the end ccells can see each other.  As with all loops, the weak links are strengthened creating a Strong Linked (SL) structure.


.. _hsp_xy-chains:

3.4.2.1.   XY-Chains [Clean Up]

All three types of chain eliminations are available to XY Chains:
    • Type 1:  Same value chain ends
    • Type 2:  Different value chain ends that see each other (either cell or house)
    • Type 3:  Different value chain ends, in different cells of an Exposed Pair.

Because of the way XY-Chains are formed, it is never possible to form group links of any kind.  Recall, group links are strong links formed with three or more ccell.  In XY-Chains, all strong links are the bi-value cells.

Aside:  Need to search for different candidate value ends in same house examples.  I do believe they exist, just have not found any yet.













In the above example, courtesy of Hodoku, the following XY-Chain is constructed:
	(3=9)r7c4-(9=8)r5c4-(8=2)r5c6-(2=3)r2c6.

Here the chain starts and ends ccells of value 3.  Walking the chain from one end with the premise that 3 is False, infers a True 3 at the other end.

If 3r7c4 is False, 9r7c4 is True, 9r5c4 is False, 8r5c4 is True, 8r5c6 is False, 2r5c6 is True, 2r2c6 is False making 3r2c6 True.  Similarly if 3r2c6 is False, 3r7c4 is True.  The chain strongly links 3r2c6 and 3r7c4.  Therefore any 3 ccell that sees both 3r7c4 and 3r2c6 can be eliminated as highlighted in red.

Because YAS’s pattern search algorithm has a different order, it finds a different XY-Chain solution at this step.

3+6+1+74+952858+4...+7+9.+7+92.....+4+9+2+3+574.+8.+41+6...35+7+85+76+3+1+24+9+678...+4+121+4+52+8+7+9..+239+4+168+7+5||XY-Chain|(2=3)r2c6~(3=5)r7c6~(5=9)r7c5~(9=2)r5c5|r2c5-=2;r5c6-=2

3.4.2.2.   XY Loops
If both the starting and ending ccell of an XY Chain fall in the same house, they form an Even Loop.  It is only possible to make even node XY-Loops, because all the strong links are in bi-value cells.  There can never be a Strong XY-Loop.

As with all Even Loops, all the weak links are strengthened. Thus any ccell that sees both ccells of a weak link, and is not part of the chain can be eliminated.

Because the chain is only made up of bi-value cells, it is not possible to create a loop with two same parity nodes in a cell necessary for Type 1 SL Eliminations.  Therefore only Type 2 (all cell candidates see same parity nodes) and Type 3 (any ccell sees both an odd and an even parity node) Eliminations can be made.

An example, courtesy of Sudokuwiki:

:raw-html:`<mong>.92...376.1..3.5..+3.....+19.9+3.85.+7.1...3.4...2...97..3+68+9..+3+4+1.+5+23.4..6.147...2+3.|r2c3-=4;r2c8-=4;r3c3-=4;r3c4-=5;r3c6-=5;r5c9-=5|XY-Loop|(6=8)r2c3~(8=2)r2c8~(2=4)r4c8~(4=6)r4c3-|r2c1-=8;r2c6-=8;r2c9-=8;r5c8-=2;r3c3-=6;r5c3-=6;r6c3-=6|</mong>`

The XY-Loop pattern is identified as:
	(6=8)r2c3-(8=2)r2c8-(2=4)r4c8-(4=6)r4c3

Because chain has closed on itself – ie formed a loop, all other same value candidates in the house of the weak links can be eliminated.

If 8r2c3 is False, 6r2c3 is True, 6r4c3 is False, 4r4c3 is True, 4r4c8 is False, 2r4c8 is True, 2r2c8 is False, making 8r2c8 True.  Similarly in the reverse direction if 8r2c8 is False, 8r2c3 is True.  Therefore the chain strongly links 8r2c3 to 8r2c8 eliminating all other 8 candidates in r2.

The same can be said for 6r2c3 and 6r4c3 in c3, 4r4c3 in r4, and 2r4c8 and 2r2c8 in c8.

+75.+39..4+64..+5+7...3...16+4.....8+2+476..2.+5+6+8+1+4.9..4+9+532...+4.8.5...8..+7.+6..451.+43+9.6.|r7c8-=23;r8c8-=3|XY-Loop|(1=2)r1c3~(2=7)r9c3~(7=8)r9c7~(8=1)r1c7~|r2c3-=2;r3c3-=2;r7c3-=2;r8c3-=2;r9c9-=7;r2c7-=8;r3c7-=8
3.4.2.3.   Remote Pairs
Remote pairs are a special case of XY-Chains, where there is a collection of bi-value cell with exactly the same 2 candidates. That is a collection of resolved (exposed or hidden) pairs that can be connected together.  A resolved pair in one house can only connect to a resolved pair in one or both of the other two houses.  Because bi-value cell can connect to two other cells, it make sense to build the chain as a net/tree rather than a simple chain.

Any traversal of 4 or more linked cells in the net forms a Remote Pair chain.  Any Ccell that can see the same valued Candidate Ccell at both ends of this Remote Pair Chain that is not part of the overall net/tree can be eliminated.

The reason for the minimum number of cells needing to be four is shown as follows:
[TODO Fixup with concept Diag syntax.]

Considering 3 linked nodes/cells. If green “a” is True, then red “a” is False and if green “a” is False then red “a” is True.  Any other candidate “a” outside of this chain that can see both a green “a” and a red “a” can be eliminated.  With only three cells there is no location on a Sudoku grid that can see both a red and a green “a”.  Add a fourth bi-value cell linked to the chain as follows:


With for bi-value cells in a chain, eliminations are possible.  The yellow highlighted cells can see both a green “a” and a red “a”, and candidates “a” and “b” can be eliminated from those cells.

However, observe the following pattern with also four cells:


Here it is not possible for any other cell outside the pattern to see both a red and green “a” or a red or green “b”.  Note:  ab==r2c3,r3c2 is the exposed pair in box 1.  The reason this does not work, is that this four cell pattern is a net and does not form a four cell simple chain.  In building a net, branch levels will alternate “ab” and “ab” (AKA odd and even parity nodes).  A productive Remote Pair chain must traverse 4 or more consecutive linked nodes in the net.  This traversal can go up one branch and down another, but cannot attempt traverse down two branches.

Therefore any productive Remote Pair in the net needs to include two odd level nodes and two even level nodes.
A remote Pair net can be seen as the linking together of Exposed Pairs.  All Exposed pairs have two Strong links, connecting the two ccell of each candidate value as well as the two strong links between each the two ccells in each cell.  There are only strong links in a Remote Pair structure, therefore it’s elimination follow Strong Link Types.  However only Type 3 SL Eliminations (ccells that see both an odd and even parity link) are applicable to Remote pairs Type 1 (cell contains two same parity nodes) and Type 2: (all cands in a cell see same parity nodes) are made impossible with the exlusive use of bi-value cells., for the same reasons as XY Chains.

 Therefore in any Remote Pair net that has at least 2 odd and 2 even nodes, any Ccell that is not part of the net that can see both an odd and even Ccell in the net can be eliminated.

The reason this works is that there is an implied strong link between the cells containing the exposed pair in a house.  Since the remote pair net (strongly, as it has no other option) links the exposed pairs, there is an implied strong link between any odd level and even level node in the net.  It is easy to show this empirically by connecting the nodes that a candidate to be eliminated see with a strongly ended AIC using only ccells in the net.

Another   Hodoku example:

1+78+6.+9.5.+9+34+1+5.6.72+5+6+7.3.+1.+7+9+35+6..4+16+4+1.+3+7+59.+8+2+591+47+3+6+5+673.+1...+4+1..75.6.38.4.6+1+75||Remote Pair||(2=8)(r2c6{~r2c8~r7c8,~r4c6~r4c7~r5c9~r5c4~r8c4})|r1c7-=2;r3c7-=8;r7c5-=28;r7c9-=28;r8c7-=28;r8c9-=28

Here Hodoku finds the chain pattern as a simple chain:
	(2=8)(r7c8-r2c8-r2c6-r4c6-r4c7-r5c9-r5c4-r8c4)

YAS finds the pattern as a net:
	(2=8)(r2c6{~r2c8~r7c8,~r4c6~r4c7~r5c9~r5c4~r8c4})

The net found in YAS is exactly the same pattern as the simple chain Hoduku finds.  It is described differently because it starts at the third node that Hoduku finds, therefore starts with two nodes.  To illustrate this example odd nodes are green, even nodes are blue.  Any value in the pair (2 or 8) that can see both a blue and a green highlight can be eliminated.
3.4.3.   AI-Chains and -Loops and -Nets
AI- (Alternating Inference) Chains and loops is the most generalized linking of which X-Chains/Loops and XY-Chains/Loops are subsets.  AIC’s are formed by linking any ccell nodes by alternating strong and weak links (keeping in mind that a strong link can masquerade as a weak link, but a weak link cannot masquerade as a strong link.  See Links and Chains Logic above.

3.4.3.1.   W-Wings (AIC with 6 nodes)
A W-Wing pattern is a type of AIC with a specific pattern defined as: Two identical bi-value cells in different houses that can see a strong link with one of their candidates.  The outcome is: Any candidate of the other value that can see both bi-value cells can be eliminated as shown by the highlights in the two diagrams below.


Recognize that W-Wings are also AIC’s of the form (using the second diagram as an example):
	‘a’r2c7=’b’r2c7-’b’r2c2=’b’r8c2-’b’r8c9=a’r8c9 ==> ‘a’r2c7=’a’r8c9.

The AIC forms a strong link between ‘a’r2c7 and ‘a’r8c9, therefore any other candidate ‘a’ that sees the ends can be eliminated as shown by the highlights.

Note that the strong link between the two ‘b’ candidates can also be an AIC, thereby extending the length of the minimal W-Wing AIC of 6 nodes.  It can have any even number of nodes greater than 6.  As an AIC of greater than 6 nodes is a variation of the original definition, which the YAS implementation identifies as a “Kraken W-Wing”.

As with all AIC’s cannibalism is permitted, that is: an elimination in the chain does not break the chain.
3.4.3.2.   AI Chains
Productive AIC chains have an odd number of links (an even number of nodes) and start and end with strong links.  An AIC ends in the same house with same candidate values form an Even AI-Loop. If the ends are the same value but are in different houses, eliminations can still be made.  If the chain ends are different values but fall in the same house, eliminations can also be made. If the AI chain starts and ends with the same ccell, that is, both links to that ccell are strong links, then the  Chain form a Strong Loop.  In a strong loop, the node with the two strong links can be placed.



3.4.3.2.1.   Same Candidate Ccell Ends [Clean Up]

Different Chutes, same chute examples

8+2+7+3...+95+4+1..7..3+2+63.2...4+7+5+41+7+39+2+86+378.2.45+99+6+25..7+1+3+25+6+4.3+97.+79+4.5+2+3+6.1+8+3..+7+5+24||Same End Candidate AI-Chain||1r1c7=1r3c7~8r3c7=8r2c7-8r2c4=8r8c4~8r7c5=1r7c5|r1c5-=1|

SudokuSwami finds this solution:
..736..9..6....4....59...+637..+68....+5.81.36..+6..+75..+821....69....6....2..5..978+1+6|r1c6-=2;r2c1-=28;r2c3-=12;r3c5-=2;r3c6-=2;r4c2-=1;r4c3-=3;r6c2-=1;r6c3-=3;r7c2-=234;r7c3-=3;r7c5-=4;r8c1-=34;r8c2-=34;r8c5-=4;r8c6-=4|Same End Candidate AI-Chain||2r1c7=2r3c7-7r3c7=7r3c5-4r3c5=4r5c5~2r5c5=2r5c2|r1c2-=2

Yas  finds a shorter chain for the same puzzle state, also in diffent chutes.

..736..9..6....4....59...+637..+68....+5.81.36..+6..+75..+821....69....6....2..5..978+1+6|r1c6-=2;r2c1-=28;r2c3-=12;r3c5-=2;r3c6-=2;r4c2-=1;r4c3-=3;r6c2-=1;r6c3-=3;r7c2-=234;r7c3-=3;r7c5-=4;r8c1-=34;r8c2-=34;r8c5-=4;r8c6-=4|Same End Candidate AI-Chain||7r2c5=7r3c5-4r3c5=4r5c5-4r5c8=7r5c8|r2c8-=7

Same chute examples


SudokuSwami finds the same chute solution in tower 2.with 4 eliminations..
	5r6c6=5r6c1~7r6c1=7r6c8~4r6c8=4r3c8-9r3c8=9r3c5-9r7c5=5r7c5|r5c5-=5;r7c7-=5;r7c8-=5;r7c9-=5

YAS finds a different chute shorter chain solution.

.+4......135....62.821..6.......24+96.4+6+29.7+1.3.9.16...+2.+3.8..714.84+6...399......
.+6|r1c4-=7;r1c5-=79;r1c6-=9;r1c8-=58;r2c5-=8;r3c4-=4;r3c5-=45;r3c8-=5;r4c3-=57;r6c3-=57;r6c8-=58;r7c1-=5;r8c1-=5|Same End Candidate AI-Chain||3r3c7=3r1c7-8r1c7=8r2c9~8r4c9=8r4c3~3r4c3=3r4c4|r3c4-=3|

Another SudokuSwami Same End Candidate AI-Chain example:


SudokuSwami resolves this pattern, as shown above.  However YAS finds three different Same End Candidate AI chain in a row with this puzzle state as shown below.

+1+57.3+8..6+329.+6187.4+8+6..+7.1...+4875..+1..5...4....+1642....4+3..+6..8+5127+8.69.6.+8.2.1..|r5c1-=9;r5c2-=39;r5c8-=3;r5c9-=39;r6c2-=7;r7c4-=9;r9c4-=4;r9c9-=5|Same End Candidate AI-Chain||2r5c9=7r5c9-7r9c9=7r7c7-2r7c7=2r7c8|r4c8-=2;r5c8-=2


+1+57.3+8..6+329.+6187.4+8+6..+7.1...+4875..+1..5...4....+1642....4+3..+6..8+5127+8.69.6.+8.2.1..|r4c8-=2;r5c1-=9;r5c2-=39;r5c8-=23;r5c9-=39;r6c2-=7;r7c4-=9;r9c4-=4;r9c9-=5|Same End Candidate AI-Chain||3r3c7=3r3c9-9r3c9=9r6c9-9r6c2=3r6c2|r6c7-=3


+1+57.3+8..6+329.+6187.4+8+6..+7.1...+4875..+1..5...4....+1642....4+3..+6..8+5127+8.69.6.+8.2.1..|r4c8-=2;r5c1-=9;r5c2-=39;r5c8-=23;r5c9-=39;r6c2-=7;r6c7-=3;r7c4-=9;r9c4-=4;r9c9-=5|Same End Candidate AI-Chain||4r1c8=4r9c8-5r9c8=5r9c4-5r2c4=4r2c4|r1c4-=4;r2c9-=4




Same chute with canibalism

Canibalistic same chute.\


3.4.3.2.2.   Different Candidate Ccell Ends, Same House [Clean Up]

Show one elim, two elims


























3.4.3.2.3.   Different Candidate Ccell Ends, Same House, Identical Bi-Value Pairs [Clean Up]






























3.4.3.2.4.   Different Ccell Ends – Same  House – Non Identical Bi-Value Pairs
In different Candidate Ccell Ends in Same house where cells do not contain identical bivalue pairs, the non end candidate in both end cells needs to be the same to yield eliminations.  And if it is the same, then an Even AI Chain is formed, so this situation is not considered further.

3.4.3.3.   Even AI Loops [Clean Up]

Like Even X-Loops, the weak links are strengthened, forcing these eliminations:
   • If the Weak Link is two same value ccells in a house, then all other same value ccells in that house can be eliminated.
   • If the Weak Link is two different valued ccells in a cell, then all other ccells (candidates) can be eliminated from that cell.


83.+2.......2..8...79634+1.....7..4.295+2..9...694.6.+27..+3...25164...1..9.....+4...73|r1c7-=5;r1c8-=15;r1c9-=5;r2c7-=5;r2c8-=15;r2c9-=5;r5c8-=8;r6c8-=58;r6c9-=1|Even AI-Loop T3||1r4c5=1r6c5-1r6c8=3r6c8-3r4c7=3r4c5-,1r4c5-5r4c5-3r4c5,1r4c5-8r4c5-3r4c5,3r4c7-3r5c7-3r6c8,3r4c7-3r5c8-3r6c8,1r6c8-1r6c3-1r6c5|r4c5-=58;r5c7-=3;r5c8-=3;r6c3-=1|83+5+2+7+6+4+9+1+4+12+9+58+6+3+779634+1+5+8+2+6+87+5+14+3295+2+1+79+3+8+4694+36+8+27+1+5+3+7+9+825164+2+6+41+3+79+5+8+1+5+8+4+6+9+273





















3.4.3.4.   Strong AI Loops
Like Strong X-Loops, The ccell node that joins the two strong links can be assigned that candidate value, as it is the only possibility that forms a truth.




















3.4.3.5.   Group linked AI-Chains and -Loops



More chains:
From Craking the crypic, many chains.