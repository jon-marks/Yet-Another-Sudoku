from git import Repo
from time import strftime, localtime
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

oRepo = Repo("..\\..")
project = 'Yet Another Sudoku'
author = 'Jonathan Marks'
version = "0.0.2"  # f'V{oRepo.tags[-1].tag.tag}'
release = ""  # f'{version}:{oRepo.head.commit.hexsha[:7]}{"*" if oRepo.is_dirty() else ""}, {strftime("%a, %d %b %Y, %H:%M:%S", localtime(oRepo.head.commit.committed_date))}'
copyright = '2022, Jonathan Marks, Commit Tag: 'f'V{oRepo.tags[-1].tag.tag}:{oRepo.head.commit.hexsha[:7]}{"*" if oRepo.is_dirty() else ""}, {strftime("%a, %d %b %Y, %H:%M:%S", localtime(oRepo.head.commit.committed_date))}'


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

rst_epilog = """
.. role:: raw-html(raw)
   :format: html
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ['_static']
html_title = ''
html_css_files = ['overrides.css']
html_logo = 'images/AIM.png'
html_favicon = 'images/AIM.ico'
html_use_index = True
extensions.append('cloud_sptheme.ext.table_styling')

html_theme = 'furo'

# Furo is not supporting sourcelinks https://github.com/pradyunsg/furo/issues/478
html_copy_source = False
html_show_sourcelink = False


