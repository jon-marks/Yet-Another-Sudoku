# from git import Repo
from time import strftime, localtime
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# oRepo = Repo("..\\..")
project = 'Yet Another Sudoku'
author = 'Jonathan Marks'
version = "0.0.2"  # f'V{oRepo.tags[-1].tag.tag}'
release = ""  # f'{version}:{oRepo.head.commit.hexsha[:7]}{"*" if oRepo.is_dirty() else ""}, {strftime("%a, %d %b %Y, %H:%M:%S", localtime(oRepo.head.commit.committed_date))}'
copyright = '2022, Jonathan Marks, Build Tag: 'f'V{version}'  # oRepo.tags[-1].tag.tag}:{oRepo.head.commit.hexsha[:7]}{"*" if oRepo.is_dirty() else ""}, {strftime("%a, %d %b %Y, %H:%M:%S", localtime(oRepo.head.commit.committed_date))}'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []
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


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ['_static']
html_title = ''
html_ccss_files = ['overrides.css']
html_logo = 'AIM.png'

# https://sphinxjpthemesbasicstrap.readthedocs.io/en/latest/options.html

#extensions.append('sphinx_copybutton')
html_theme = 'furo'


# -- HTML theme options for `basicstrap` style -------

# html_theme_options = {
#

#     # Set the lang attribute of the html tag. Defaults to 'en'
#     'lang': 'en',
#     # Disable showing the sidebar. Defaults to 'false'
#     'nosidebar': False,
#     # Show header searchbox. Defaults to false. works only "nosidber=True",
#     'header_searchbox': False,
#
#     # Put the sidebar on the right side. Defaults to false.
#     'rightsidebar': False,
#     # Set the width of the sidebar. Defaults to 3 blocks out of a grid of 12.
#     'sidebar_span': 3,
#
#     # Fix navbar to top of screen. Defaults to true
#     'nav_fixed_top': True,
#     # Fix the width of the sidebar. Defaults to false
#     'nav_fixed': False,
#     # Set the width of the sidebar. Defaults to '900px'
#     'nav_width': '900px',
#     # Fix the width of the content area. Defaults to false
#
#     'content_fixed': True,  # False,
#     # Set the width of the content area. Defaults to '900px'
#     'content_width': '950px',
#     # Fix the width of the row. Defaults to false
#     'row_fixed': False,
#
#     # Disable the responsive design. Defaults to false
#     'noresponsive': False,
#     # Disable the responsive footer relbar. Defaults to false
#     'noresponsiverelbar': False,
#     # Disable flat design. Defaults to false.
#     # Works only "bootstrap_version = 3"
#     'noflatdesign': False,
#
#     # Enable Google Web Font. Defaults to false
#     'googlewebfont': False,
#     # Set the URL of Google Web Font's CSS.
#     # Defaults to 'http://fonts.googleapis.com/css?family=Text+Me+One'
#     'googlewebfont_url': 'http://fonts.googleapis.com/css?family=Lily+Script+One',  # NOQA
#     # Set the Style of Google Web Font's CSS.
#     # Defaults to "font-family: 'Text Me One', sans-serif;"
#     'googlewebfont_style': u"font-family: 'Lily Script One' cursive;",
#
#     # Set 'navbar-inverse' attribute to header navbar. Defaults to false.
#     'header_inverse': False,
#     # Set 'navbar-inverse' attribute to relbar navbar. Defaults to false.
#     'relbar_inverse': False,
#
#     # Enable inner theme by Bootswatch. Defaults to false
#     'inner_theme': False,
#     # Set the name of innner theme. Defaults to 'bootswatch-simplex'
#     'inner_theme_name': 'bootswatch-simplex',
#
#     # Select Twitter bootstrap version 2 or 3. Defaults to '3'
#     'bootstrap_version': '3',
#
#     # Show "theme preview" button in header navbar. Defaults to false.
#     'theme_preview': True,
#
#     # Set the Size of Heading text. Defaults to None
#     # 'h1_size': '3.0em',
#     # 'h2_size': '2.6em',
#     # 'h3_size': '2.2em',
#     # 'h4_size': '1.8em',
#     # 'h5_size': '1.4em',
#     # 'h6_size': '1.1em',
# }
