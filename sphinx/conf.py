import os
import sys
from build import toml_loads  # type: ignore

# -- Package Path for Autodoc ------------------------------------------------
# a bit of a hack to force sphinx-multiversion consume appropriate package
# versions for the docs
progname = sys.argv[0].replace("\\", "/")
if progname.endswith("site-packages/sphinx/__main__.py"):  # multiversion
    sys.path.insert(0, os.path.abspath(sys.argv[-2] + "/.."))
else:
    sys.path.insert(0, os.path.abspath(".."))  # current version only

import ndf_parse
_version = tuple(int(x) for x in ndf_parse.__version__.split(".")[:2])

# -- Ndf Highlighting Lexer --------------------------------------------------
if _version >= (0,2):
    from devutils import highlight
    from sphinx.highlighting import lexers

    lexers["ndf"] = highlight.NdfLexer()


# -- Project Information -----------------------------------------------------
with open("../pyproject.toml") as r:
    package_conf = toml_loads(r.read())
    projcfg = package_conf["project"]

author = projcfg["authors"][0]["name"]
project = projcfg["name"]
copyright = f"{author}, 2023-2024"
version = ndf_parse.__version__
release = version

# -- substitutions
rst_prolog=f"""
.. |copyright| replace:: {copyright}
.. |author| replace:: {author}
"""

rst_epilog=f"""
.. _homepage: {projcfg["urls"]["Homepage"]}
.. _releases: {projcfg["urls"]["Homepage"]}/releases
.. _docs: {projcfg["urls"]["Documentation"]}
"""

# -- General Configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx_multiversion",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

if _version >= (0,2):
    extensions.append("devutils.sphinx-inline")

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.rst"]
html_static_path = ["_static"]

autodoc_member_order = "bysource"
napoleon_numpy_docstring = True
add_module_names = False
html_show_sourcelink = False
html_copy_source = False
python_display_short_literal_types = True

intersphinx_mapping = {"python": ("https://docs.python.org/3.8", None)}

# -- Doctests ----------------------------------------------------------------
from doctest import (
    ELLIPSIS,
    IGNORE_EXCEPTION_DETAIL,
    DONT_ACCEPT_TRUE_FOR_1,
    NORMALIZE_WHITESPACE,
)

doctest_default_flags = (
    ELLIPSIS
    | IGNORE_EXCEPTION_DETAIL
    | DONT_ACCEPT_TRUE_FOR_1
    | NORMALIZE_WHITESPACE
)

# -- Furo Theme Setup --------------------------------------------------------
html_theme = "furo"

html_theme_options = {
    "light_logo": "ndf_parse_logo_blob.svg",
    "dark_logo": "ndf_parse_logo.svg",
}
html_favicon = "_static/favicon.png"

pygments_style = "solarized-light"
pygments_dark_style = "github-dark"

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        # "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
        "versions.html",
    ]
}

# -- multiversion config -----------------------------------------------------
publish_tags = r"v0\.1\.2|v0\.2\.0"  # doc only specific versions

smv_branch_whitelist = "^$"
smv_tag_whitelist = publish_tags
smv_released_pattern = f"refs/tags/({publish_tags})"
# `smv_latest_version` is fed via args and should not be set here!

# -- Custom Types Aliasing Workaround ----------------------------------------
TYPE_ALIASES = {"GR": "data", "CellValue": "data", "DictWrapped": "data"}


def resolve_type_aliases(app, env, node, contnode):  # type: ignore
    if node["refdomain"] == "py" and node["reftarget"] in TYPE_ALIASES:
        reftype = TYPE_ALIASES[node["reftarget"]]
        return app.env.get_domain("py").resolve_xref(  # type: ignore
            env,
            node["refdoc"],
            app.builder,  # type: ignore
            reftype,
            node["reftarget"],
            node,
            contnode,
        )


def setup(app):  # type: ignore
    app.connect("missing-reference", resolve_type_aliases)  # type: ignore
