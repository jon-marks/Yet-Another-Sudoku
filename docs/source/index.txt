.. title:: Yet Another Sudoku



##################
Yet Another Sudoku
##################

=================
Table of Contents
=================

.. toctree::
   :maxdepth: 6
   :numbered:

   01-introduction
   02-foundation/index
   03-human-solvable-patterns/index
   04-generating
   05-grading
   06-software/index
   07-glossary
   08-references

..
   :caption: Table of Contents
   :name: table-of-contents

===============
List of Figures
===============

|  :numref:`fig-truths-eg1` :ref:`fig-truths-eg1`
|  :numref:`fig-links-eg1` :ref:`fig-links-eg1`
|  :numref:`fig-locked-exposed-pair-cd1` :ref:`fig-locked-exposed-pair-cd1`
|  :numref:`fig-y-wing-cd1` :ref:`fig-y-wing-cd1`
|  :numref:`fig-locked-pointing-single-cd1` :ref:`fig-locked-pointing-single-cd1`
|  :numref:`fig-xyz-wing-cd1` :ref:`fig-xyz-wing-cd1`
|  :numref:`fig-locked-exposed-triple-cd1` :ref:`fig-locked-exposed-triple-cd1`
|  :numref:`fig-y-wing-cd2` :ref:`fig-y-wing-cd2`
|  :numref:`fig-xyz-wing-cd2` :ref:`fig-xyz-wing-cd2`
|  :numref:`fig-gbp-el-hb-cd1` :ref:`fig-gbp-el-hb-cd1`
|  :numref:`fig-gbp-hl-eb-cd1` :ref:`fig-gbp-hl-eb-cd1`
|  :numref:`fig-gbt-el-hb-cd1` :ref:`fig-gbt-el-hb-cd1`
|  :numref:`fig-gbt-hl-eb-cd1` :ref:`fig-gbt-hl-eb-cd1`
|  :numref:`fig-gbq-el-hb-cd1` :ref:`fig-gbq-el-hb-cd1`
|  :numref:`fig-gbq-hl-eb-cd1` :ref:`fig-gbq-hl-eb-cd1`
|  :numref:`fig-bht-cd1` :ref:`fig-bht-cd1`
|  :numref:`fig-base-cover-eg1` :ref:`fig-base-cover-eg1`
|  :numref:`fig-base-cover-eg2` :ref:`fig-base-cover-eg2`
|  :numref:`fig-hidden-pair-eg1` :ref:`fig-hidden-pair-eg1`
|  :numref:`fig-x-wing-eg1` :ref:`fig-x-wing-eg1`
|  :numref:`fig-finned-x-wing-eg1` :ref:`fig-finned-x-wing-eg1`
|  :numref:`fig-two-string-kite-eg1` :ref:`fig-two-string-kite-eg1`
|  :numref:`fig-uls-chain-cd1` :ref:`fig-uls-chain-cd1`
|  :numref:`fig-basic-fish-cd1` :ref:`fig-basic-fish-cd1`
|  :numref:`fig-two-string-kite-eg2` :ref:`fig-two-string-kite-eg2`
|  :numref:`fig-skyscraper-eg1` :ref:`fig-skyscraper-eg1`
|  :numref:`fig-chained-sln-t2-eg1` :ref:`fig-chained-sln-t2-eg1`
|  :numref:`fig-se-aic-diff-chute-cd1` :ref:`fig-se-aic-diff-chute-cd1`
|  :numref:`fig-se-aic-same-chute-cd1` :ref:`fig-se-aic-same-chute-cd1`
|  :numref:`fig-se-aic-same-house-cd1` :ref:`fig-se-aic-same-house-cd1`
|  :numref:`fig-se-aic-diff-ends-s1` :ref:`fig-se-aic-diff-ends-s1`
|  :numref:`fig-se-aic-diff-ends-s2` :ref:`fig-se-aic-diff-ends-s2`
|  :numref:`fig-se-aic-opp-exp-pair-ends-s1` :ref:`fig-se-aic-opp-exp-pair-ends-s1`
|  :numref:`fig-sln-t1-eg1` :ref:`fig-sln-t1-eg1`
|  :numref:`fig-sln-t2-eg1` :ref:`fig-sln-t2-eg1`
|  :numref:`fig-sln-t3-eg1` :ref:`fig-sln-t3-eg1`
|  :numref:`fig-cannib-ai-chain-eg1` :ref:`fig-cannib-ai-chain-eg1`
|  :numref:`fig-gl-cd1` :ref:`fig-gl-cd1`
|  :numref:`fig-gl-cd2` :ref:`fig-gl-cd2`
|  :numref:`fig-gl-cd3` :ref:`fig-gl-cd3`
|  :numref:`fig-gl-cd4` :ref:`fig-gl-cd4`
|  :numref:`fig-empty-rect-cd1` :ref:`fig-empty-rect-cd1`
|  :numref:`fig-y-wing-eg1` :ref:`fig-y-wing-eg1`
|  :numref:`fig-y-wing-eg2` :ref:`fig-y-wing-eg2`
|  :numref:`fig-xyz-wing-eg1` :ref:`fig-xyz-wing-eg1`
|  :numref:`fig-beq-eg1` :ref:`fig-beq-eg1`
|  :numref:`fig-beq-eg2` :ref:`fig-beq-eg2`
|  :numref:`fig-beq-eg3` :ref:`fig-beq-eg3`
|  :numref:`fig-bequint-eg1` :ref:`fig-bequint-eg1`
|  :numref:`fig-besext-eg1` :ref:`fig-besext-eg1`
|  :numref:`fig-gbp-er-hb-eg1` :ref:`fig-gbp-er-hb-eg1`
|  :numref:`fig-gbp-ec-hb-eg1` :ref:`fig-gbp-ec-hb-eg1`
|  :numref:`fig-gbp-hr-eb-eg1` :ref:`fig-gbp-hr-eb-eg1`
|  :numref:`fig-gbp-hc-eb-eg1` :ref:`fig-gbp-hc-eb-eg1`
|  :numref:`fig-gbt-er-hb-eg1` :ref:`fig-gbt-er-hb-eg1`
|  :numref:`fig-gbt-ec-hb-eg1` :ref:`fig-gbt-ec-hb-eg1`
|  :numref:`fig-gbt-hr-eb-eg1` :ref:`fig-gbt-hr-eb-eg1`
|  :numref:`fig-gbt-hc-eb-eg1` :ref:`fig-gbt-hc-eb-eg1`
|  :numref:`fig-gbq-er-hb-eg1` :ref:`fig-gbq-er-hb-eg1`
|  :numref:`fig-gbq-ec-hb-eg1` :ref:`fig-gbq-ec-hb-eg1`
|  :numref:`fig-gbq-hr-eb-eg1` :ref:`fig-gbq-hr-eb-eg1`
|  :numref:`fig-gbq-hc-eb-eg1` :ref:`fig-gbq-hc-eb-eg1`
|  :numref:`fig-bht-eg1` :ref:`fig-bht-eg1`

==============
List of Tables
==============

|  :numref:`tbl-weak-link-it` :ref:`tbl-weak-link-it`
|  :numref:`tbl-strong-link-it` :ref:`tbl-strong-link-it`
|  :numref:`tbl-robust-link-it` :ref:`tbl-robust-link-it`
|  :numref:`tbl-cand-diag-symbs` :ref:`tbl-cand-diag-symbs`
|  :numref:`tbl-cand-diag-expr` :ref:`tbl-cand-diag-expr`
|  :numref:`tbl-we-aic-it` :ref:`tbl-we-aic-it`
|  :numref:`tbl-se-aic-it` :ref:`tbl-se-aic-it`
|  :numref:`tbl-slc-it` :ref:`tbl-slc-it`
|  :numref:`tbl-se-aic-gl-it` :ref:`tbl-se-aic-gl-it`

..
   ==================
   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
