# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Ray and Stephanie Lane Cluster'
copyright = '2025, Ray and Stephanie Lane Computational Biology Department'
author = 'Ivan E. Cao-Berg'

version = '0.1'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",                 # Markdown support
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",         # Google/NumPy docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    # Optional (uncomment if using):
    # "sphinxcontrib.bibtex",
    # "sphinxext.opengraph",
]

myst_enable_extensions = [
    "deflist",
    "colon_fence",
    "linkify",
    "replacements",
]

# -- HTML -------------------------------------------------------------
html_theme = "furo"
html_theme = 'sphinx_rtd_theme'
html_title = "Ray and Stephanie Lane cluster documentation"

# -- Autodoc / Napoleon ----------------------------------------------
autodoc_typehints = "description"

# Optional: AutoAPI instead of sphinx-apidoc
# extensions.append("autoapi.extension")
# autoapi_type = "python"
# autoapi_dirs = ["../src"]   # adjust to your package pat

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
