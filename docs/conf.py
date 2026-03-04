"""Sphinx configuration file for the News Capstone project.

This file is read by Sphinx when building the documentation. It configures
the Django environment so that autodoc can import the project's models,
views, and other modules without a running database connection.

To regenerate the docs locally::

    cd docs/
    make html

The generated HTML will appear in ``docs/_build/html/``.
"""

import os
import sys
import django

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# Insert the Django project root (the folder containing manage.py) into
# sys.path so that Sphinx can import the project's Python packages.
sys.path.insert(0, os.path.abspath("../news_project"))

# Tell Django which settings module to use.
os.environ["DJANGO_SETTINGS_MODULE"] = "news_project.settings"

# Initialise Django — required before importing any models or apps.
django.setup()

# ---------------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------------
project = "News Capstone"
copyright = "2025, HyperionDev Student"
author = "HyperionDev Student"
release = "1.0.0"

# ---------------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # Pull docstrings from source code automatically
    "sphinx.ext.viewcode",      # Add links to highlighted source code
    "sphinx.ext.napoleon",      # Support Google and NumPy docstring styles
    "sphinx.ext.intersphinx",   # Link to other project's documentation
]

# Napoleon settings — we use Google-style docstrings.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Intersphinx mapping for Django's own documentation.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/5.1/", None),
}

# autodoc settings.
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# HTML output options
# ---------------------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "News Capstone Documentation"
