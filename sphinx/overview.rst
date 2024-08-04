Overview
========

.. include-from-here

Prerequisites
-------------

-  `python <https://www.python.org/downloads/>`__ >= 3.8 (this package
   was developed on 3.8 and tested on minor versions from 3.8 to 3.12).

Installation
------------

.. code:: bat

   pip install ndf-parse

.. note::
   Note that if you didn't add python to the ``PATH`` variable during
   installation, you'll have to run it with full path to **pip**, for example
   :code:bat:`"C:\\Users\\User\\AppData\\Local\\Python311-64\\Scripts\\pip.exe"
   install ndf_parse`

As an alternative, you can download and install this package from
`github releases <releases_>`__.

Using This Package
------------------

For usage please refer to the `documentation <docs_>`__.

.. _caveats:

Caveats
-------

This package gets shipped with an :code:bat:`ndf.dll` containing the tree-sitter
language parser. It's linkage is also hardcoded in module's ``__init__``. If
you're planning to use this on linux or MacOS (why?..), you will have to `build
the lib yourself <ndf_>`__ and set an env variable
:code:shell:`NDF_LIB_PATH=path/to/your/lib`.

.. _ndf: https://github.com/Ulibos/tree-sitter-ndf

Developing
----------

In order to develop this module you will need to fork this repo, clone the fork
and run the following command:

.. code:: powershell

   pip install -e "path\to\cloned\repo[dev]"

It will load most dependencies automatically. Only thing you will have to
provide manually is an :code:bat:`ndf.dll` (`see below <custom-ndf_>`__). You
can then build a release package using :code:bat:`scripts\\build_package.bat`
script. It outputs the result to a :code:bat:`build\\package` folder. By default
the build sctipt uses a local library (:code:bat:`ndf_parse\\bin\\ndf.dll`). If
there is none, it copies one from tree-sitter's default build path to local
path. If there is also none then it refuses to build.

.. _custom-ndf: #using-in-pair-with-custom-tree-sitter-ndf

`black <https://pypi.org/project/black/>`__ is used for code styling
with line length limit == 79. Code is (mostly) type hinted.

:code:bat:`.gitignore` does not store editor specific excludes, I store those in
:code:bat:`.git\\info\\exclude`.

Repo Structure
~~~~~~~~~~~~~~

-  ``build``     - temp folder to store build data, untracked
-  ``ndf_parse`` - package source code
-  ``sphinx``    - documentation sources
-  ``scripts``   - mostly scripts for building stuff
-  ``tests``     - basic testing scripts

Docs Development
~~~~~~~~~~~~~~~~

Current Version Build
"""""""""""""""""""""

To build docs for current commit use :code:bat:`scripts\\build_docs.bat`. Your
docs will be in :code:bat:`build\\docs`.

Multiversion Build
""""""""""""""""""

To build docs for all releases follow these steps:

#. Make sure to bump release version and commit all changes related to the
   latest release (and stash what is left).
#. Tag the release with semver (example: ``v1.0.5``, ``v`` is mandatory).
#. Add new tag to :code:python:`publish_tags` variable in
   :code:bat:`sphinx\\conf.py`.
#. Remove :code:bat:`build\\multiver` to ensure clean build.
#. Run :code:bat:`python scripts\\build_multidocs.py`. Result will be in
   :code:bat:`build\\multiver`.
#. Checkout ``docs`` branch.
#. Remove old docs dirs (named by their releases), move new ones, including
   :code:bat:`build\\multiver\\index.html` (but excluding :code:bat:`.doctree`
   dirs in each version build, they are not needed for serving), to the root
   of the repo.
#. Add new stuff to git (be careful not to include junk, there is no
   :code:bat:`.gitignore`) and commit.

.. note::

   Things to keep in mind: sphinx-multiversion arranges releases based on commit
   date, not semver number. So be careful when rebasing/amending older releases.

Tests
~~~~~

If you're planning to test scripts from the documentation (the ones in
:code:bat:`sphinx\\code`), you will have to setup 2 env variables in your
terminal:

.. code:: bat

   set MOD_SRC="path\to\source_mod"
   set MOD_DST="path\to\destination_mod"

Currently there are only tests for :mod:`ndf_parse.model` and docs' code
snippets and examples. Docstrings code is tested with sphinx via
:code:bat:`tests\\docs_tests.bat`, py script with the same name has examples
tests and a deprecated version of doctests.

Using in Pair With Custom tree-sitter-ndf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package looks for an :code:bat:`ntf.dll` in the following places
(descending priority):

#. ``NDF_LIB_PATH`` env variable
   (:code:bat:`"C:\\custom\\path\\to\\ndf.dll"`),
#. default tree-sitter's build path
   (:code:bat:`"%LocalAppData%\\tree-sitter\\lib\\ndf.dll"`),
#. a copy bundled with the package (:code:bat:`"ndf_parse\\bin\\ndf.dll"`).

The repo itself does not hold a prebuilt copy of the library so you'll have to
either yank one from a release wheel (it's just a renamed zip) or build one
`from source <ndf_>`__.

Pull Requests and Issues
~~~~~~~~~~~~~~~~~~~~~~~~

I have no idea on how frequently I'll be able to respond to those, so expect
delays. You might find it easier catching me on `WarYes discord <waryes_>`__ or
`Eugen discord <eugen_>`__ in case you have some blocking issue or a PR.

.. _waryes: https://discord.gg/gqBgvgGj8H
.. _eugen:  https://discord.gg/sheyBRnqKP

Credits
-------

Created by |copyright|.
