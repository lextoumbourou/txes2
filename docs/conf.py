# -*- coding: utf-8 -*-

import sys
import os
import sphinx_rtd_theme
sys.path.insert(0, os.path.join(os.path.abspath('.'), '..'))
import txes2  # noqa

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
]
autoclass_content = 'both'
templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
project = u'txes2'
copyright = u'2014, Multiple authors'

# The short X.Y version.
version = '0.0.1'
# The full version, including alpha/beta/rc tags.
release = '0.0.1'

exclude_patterns = ['_build']
pygments_style = 'sphinx'

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
htmlhelp_basename = 'txes2doc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}
latex_documents = [
    ('index', 'txes2.tex', u'txes2 Documentation',
     u'Multiple authors', 'manual'),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    ('index', 'txes2', u'txes2 Documentation',
     [u'Multiple authors'], 1)
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    ('index', 'txes2', u'txes2 Documentation',
     u'Multiple authors', 'txes2', 'One line description of project.',
     'Miscellaneous'),
]
