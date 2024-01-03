# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = 'Yet Another Sudoku'
author = 'Jonathan Marks'
version = 'HEAD'
release = 'HEAD'
f = open('..\\build\\copyright', 'rt')
copyright = f.readline()
f.close()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.githubpages'] # creates .nojekyll empty file in html directory.
templates_path = ['_templates']
exclude_patterns = []

numfig = True
numfig_secnum = 1
numfig_format = {
                 'figure':     "Figure %s: ",
                 'table':      "Table %s: ",
                 'code-block': "Listing %s: ",
                 'section':    "Section %s: ",
                }

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_title = ''
html_css_files = ['overrides.css', 'table.css']
html_logo = 'images/AIM.png'
html_favicon = 'images/AIM.ico'
html_use_index = True

# Add my custom extension for tables stolen from from:cloud_sptheme (not maintained since 2020)
sys.path.append(os.path.abspath('./_ext'))
extensions.append('table')
html_css_files.append('table.css')


html_theme = 'furo'

# Furo is not supporting sourcelinks https://github.com/pradyunsg/furo/issues/478
html_copy_source = False
html_show_sourcelink = False
