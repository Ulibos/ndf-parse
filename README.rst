ndf-parse
=========

This package allows to parse Eugen Systems ndf files, modify them and write back
modified versions as a valid ndf code. It was created to allow easier editing of
warno mods than what is currently available with game's own tools.

.. note::

   This package was created for and tested with Windows only! More on that in
   `caveats <#caveats>`__ section.

Prerequisites
-------------

-  `python <https://www.python.org/downloads/>`__ >= 3.8 (this package
   was developed on 3.8 and tested on 3.11)

Dependencies
~~~~~~~~~~~~

-  `py-tree-sitter <ts_>`__ - either gets installed automatically (will require
   a C compiler installed) or can be downloaded from a release bundle and
   installed manually (no compiler required).
-  `tree-sitter-ndf <ndf_>`__ - comes packaged in a release, can be overridden
   by a custom lib build (needed only for development purposes).

.. _ts: https://github.com/tree-sitter/py-tree-sitter/
.. _ndf: https://github.com/Ulibos/tree-sitter-ndf/

Installation
------------

Managing dependencies
~~~~~~~~~~~~~~~~~~~~~

One of package's dependencies requires a C compiler to be installed on your PC.
In case of Windows it's going to be a set of `Microsoft C++Build Tools
<msbt_>`__ that requires around 8Gb of space. If you already have it (basically
if you have Visual Studio installed) then you can proceed directly to the `last
step <inst_>`__. If you're feeling like downloading the thing then download and
install the Build Tools, then proceed to the `last step <inst_>`__. If you don't
want to waste your drive space then download one of prebuilt versions from a
`v0.1.0 release <pbts_>`__ (make sure to match it to your python version, that
being ``cp###``), say, ``tree_sitter-0.20.1-cp311-cp311-win_amd64.whl``, open
command prompt and execute the following:

.. _msbt: https://visualstudio.microsoft.com/visual-cpp-build-tools/
.. _inst: #installing-ndf-parse
.. _pbts: https://github.com/Ulibos/ndf-parse/releases/tag/v0.1.0

.. note::
   Note that if you didn't add python to the PATH variable during installation,
   you'll have to run it with full path to `pip`, for example
   ``C:\Users\User\AppData\Local\Python311-64\Scripts\pip.exe``

.. code:: bat
   
   pip install C:\path\to\tree_sitter-0.20.1-cp311-cp311-win_amd64.whl

Installing ndf-parse
~~~~~~~~~~~~~~~~~~~~

Download the `latest release <rls_>`__, say,
``ndf_parse-#.#.#-py3-none-any.whl``. Open command prompt and execute:

.. code:: bat

   pip install C:\path\to\ndf_parse-#.#.#-py3-none-any.whl

.. _rls: https://github.com/Ulibos/ndf-parse/releases

Using This Package
------------------

For usage please refer to the
`documentation <https://Ulibos.github.io/ndf-parse/pages/docs.html>`__.

Caveats
-------

This package gets shipped with an ``ndf.dll`` containing the tree-sitter
language parser. It's linkage is also hardcoded in module's ``__init__``. If
you're planning to use this on linux or MacOS (why?..), you will have to build
the lib yourself (`second dependency <ndf_>`__) and set an env variable
``NDF_LIB_PATH=path/to/your/lib``.

Development
-----------

In order to develop this module you will need to fork this repo, clone the fork
and run the following command:

.. code:: powershell

   pip install -e path\to\cloned\repo[dev]
   # note the [dev] part

It will load most dependencies automatically. Only thing you will have to
provide manually is an ``ndf.dll`` (`see below`__). You can build a release
package using ``scripts\build_package.bat`` script. It outputs the result to a
``build\package`` folder. By default the build sctipt uses a local library
(``ndf_parse\bin\ndf.dll``). If there is none, it copies one from tree-sitter's
default build path to local path. If there is also none then it refuses to
build.

.. __: #using-in-pair-with-custom-tree-sitter-ndf

`black <https://pypi.org/project/black/>`__ is used for code styling
with line length limit == 79. Code is (mostly) type hinted. ``.gitignore`` does
not store editor specific excludes, I store those in ``.git\info\exclude``.

Repo Structure
~~~~~~~~~~~~~~

-  ``build`` - temp folder to store build data, untracked
-  ``docs`` - compiled documentation
-  ``ndf_parse`` - package source code
-  ``sphinx`` - documentation sources
-  ``scripts`` - mostly scripts for building stuff
-  ``tests`` - what tests?..

Docs Development
~~~~~~~~~~~~~~~~

To build docs, use ``scripts\build_docs.bat``. If you're planning to test
scripts from this documentation (the ones in ``sphinx\pages\code``), you will
have to setup 2 env variables in your terminal:

.. code:: bat

   set MOD_SRC="path\to\source\mod"
   set MOD_DST="path\to\destination\mod"

Using in Pair With Custom tree-sitter-ndf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package looks for an ``ntf.dll`` in the following places (descending
priority):

1. ``NDF_LIB_PATH`` env variable
   (``"C:\custom\path\to\ndf.dll"``),
2. default tree-sitter's build path
   (``"%LocalAppData%\tree-sitter\lib\ndf.dll"``),
3. a copy bundled with the package (``ndf_parse\bin\ndf.dll``).

The repo itself does not hold a prebuilt copy of the library so you'll have to
either yank one from a release wleel (it's just a renamed zip) or build one
`from source <ndf_>`__.

Pull Requests and Issues
~~~~~~~~~~~~~~~~~~~~~~~~

I have no idea on how frequently I'll be able to respond to those, so
expect delays. You might find it easier catching me on WarYes discord in
case you have some blocking issue or a PR.

Credits
-------

Created by Ulibos, 2023.
