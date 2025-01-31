"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup ----------------------------------------------------------------
from datetime import datetime

# -- Project information -------------------------------------------------------
project = "pytest-copie"
author = "Pierrick Rambaud"
copyright = f"2023-{datetime.now().year}, {author}"
release = "0.2.1"

# -- General configuration -----------------------------------------------------
extensions = [
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_immaterial",
    "autoapi.extension",
    "sphinxemoji.sphinxemoji",
]
exclude_patterns = ["**.ipynb_checkpoints"]
templates_path = ["_template"]

# -- Options for HTML output ---------------------------------------------------
html_theme = "sphinx_immaterial"
html_title = "pytest-copie"
html_static_path = ["_static"]
html_theme_options = {
    "toc_title_is_page_title": True,
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
    },
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/12rambau/pytest-copie",
            "name": "Source on github.com",
        },
        {
            "icon": "fontawesome/brands/python",
            "link": "https://pypi.org/project/pytest-copie/",
        },
    ],
    "site_url": "https://pytest-copie.readthedocs.io/",
    "repo_url": "https://github.com/12rambau/pytest-copie/",
    "edit_uri": "blob/main/docs",
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "deep-orange",
            "accent": "amber",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "amber",
            "accent": "orange",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to light mode",
            },
        },
    ],
    "globaltoc_collapse": False,
}
html_css_files = ["custom.css"]

# -- Options for autosummary/autodoc output ------------------------------------
autodoc_typehints = "description"
autoapi_dirs = ["../pytest_copie"]
autoapi_python_class_content = "init"
autoapi_member_order = "groupwise"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
