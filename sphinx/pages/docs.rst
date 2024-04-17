#############
Documentation
#############

.. contents:: Table of Contents
    :local:
    :depth: 3

Quick Start
===========

.. currentmodule:: ndf_parse

Prepare The files
-----------------

First thing we need to do is to set up a pristine copy of the mod sources. This
module works in the following way:

- Get a file from an unchanged mod (we'll refer to it as *source mod*).
- Parse, convert, apply edits.
- Format back to ndf and write it to a directory with our final mod (we'll refer
  to it as a *destination mod*).

Generate a new source mod using ``CreateNewMod.bat`` provided by Eugen Systems
and place it to ``path/to/src/mod``.

Make The Script
---------------

Create a new python file, say, ``my_mod.py`` with the following code:

.. literalinclude:: ../pages/code/quick_start.py
    :lines: 3-36

Run this script (but don't forget to substitute your mod paths first!) You
should see prints that correspond to operations from this sctipt. Now, if you
navigate to your newly generated mod and check ``Ammunition.ndf``, you should
find that some items have their *"Weapon_Cursor_MachineGun"* replaced with
*"Weapon_Replaced_MachineGun"*.

Step-by-step Explanation
------------------------

Now let's go line by line and examine what this code does.

.. literalinclude:: ../pages/code/quick_start.py
    :lines: 9-10

Here we initialize our :class:`Mod` object. It's nothing but a convenience
wrapper that saves you time from writing boilerplate code. Second line here
checks if your source mod was updated. Whenever the game gets an update - you
should delete your source mod and regenerate it anew. When next time you run the
script, that second line detects it (by comparing modification date of source
and destination folders), nukes destination mod and makes a new fresh copy of it
from the source.

.. warning::

    Never store anything important inside of source and destination folders! It
    will get nuked by such an update. Store it elsewhere or regenerate it with a
    script.

Edits
~~~~~

.. literalinclude:: ../pages/code/quick_start.py
    :lines: 11

This line starts an edit of a file. It loads the file, parses it, converts to a
python representation (based on :mod:`model`) and returns a :class:`model.List`
instance to the user to work with. Since :class:`Mod` is implemented as a
context manager, as soon as ``with`` statement's scope is closed (i.e. when all
of the operations defined in this block are completed), it will automatically
format the source back to ndf code and write the file out to the destination
mod.
If you are just tinkering with the code and don't want to write data out on each
test run, you can disable it by adding the following argument:

.. code-block:: python

    with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf", False) as source:

Navigating model Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~

Next operation loops through the root declarations of the file:

.. literalinclude:: ../pages/code/quick_start.py
    :lines: 12

All classes that are subclasses of :class:`model.DeclarationsList` are iterable
as well as have length (``len(source)``). This means that you can iterate
through :class:`model.List`, :class:`model.Object` , :class:`model.Template` and
:class:`model.Map`. Stray pairs (ones that are not inside of a Map) are defined
as a :class:`tuple`. Everything else is essentially a string literal. This also
means that List, Object, Template and Map all have a
:attr:`model.DeclarationsList.parent` attribute while others don't. It's worth
noting that :class:`model.Template` also has a :attr:`model.Template.params`
attribute to store it's generic parameters.

Each returned ``obj_row`` is a subclass of a :class:`model.DeclListRow` Here is
a correspondence table of all list-likes and their rows:

+-------------------------+-------------------------+--------------------------+
|          Notes          |      Parent Class       |         Row Class        |
+=========================+=========================+==========================+
| root/lists/vector types | :class:`model.List`     | :class:`model.ListRow`   |
+-------------------------+-------------------------+--------------------------+
| template parameters     | :class:`model.Params`   | :class:`model.ParamRow`  |
+-------------------------+-------------------------+--------------------------+
| templates               | :class:`model.Template` | :class:`model.MemberRow` |
+-------------------------+-------------------------+--------------------------+
| objects                 | :class:`model.Object`   | :class:`model.MemberRow` |
+-------------------------+-------------------------+--------------------------+
| maps                    | :class:`model.Map`      | :class:`model.MapRow`    |
+-------------------------+-------------------------+--------------------------+

.. warning::

    Don't try copying model objects from row to row! :ref:`More on that here
    <no-referencing>`.

Get and Set Values
~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../pages/code/quick_start.py
    :lines: 13-21

This code skips anything but object with specified caliber. 2 things to note
here:

1.  :class:`model.List`, :class:`model.Object` and :class:`model.Template` all
    store their type inside of their own :attr:`model.Object.type` attribute
    instead of row's one. This issue is covered in detail in :ref:`typing
    ambiguity <typing-ambiguity>` section.

2.  Literal on the right side of the last comparison has 2 sets of quotes. Since
    ndf-parse stores any trivial types and expressions as strings, we somehow
    need to keep actual ndf strings distinguishable from say a float value
    stored as a string literal. For that reason we ebmed actual string quotation
    within the string.

.. _finding-items:

Finding Items
=============

There is a :func:`walk` function that is designed to help you find stuff around
trees. It is recursive so it allows to search through nested objects. Here is an
example of how to use it:

.. literalinclude:: ../pages/code/walk.py
    :lines: 3-17
   
This example prints out all items that have an expression including a ``Metre``
word. Note that it uses a custom function to check for matches. It is your
responsibility to write one that fits your case and to make sure you typecheck.

Generating New NDF items
========================

To ease the process of making new items there is a convenience function
:func:`expression`. It takes a string with an ndf statement and returns a
:class:`dict` with the desired object and additional arguments (if the
expression was a member/visibility/assignment statement).
Example:

.. literalinclude:: ../pages/code/expression.py
    :lines: 3-32

You should get an output that is an unformatted equivalent to this statement:

.. code-block:: python

    {
        'value': [  # DeclarationsList type objects are printed as a python list
            Object[0](
                member='Radius',
                type=None,
                visibility=None,
                namespace=None,
                value='12 * Metre'
            ),
            Object[1](
                member='SomeParam',
                type=None,
                visibility=None,
                namespace=None,
                value="'A string'"
            )
        ],
        'namespace': 'NewNS'
    }

Now also check your generated ``Ammunition.ndf``, it should have objects of type
``SomeType`` instead of ``'XUTVWWNOTF'``. It also has it's ``Radius``
modified after replacement. Things worth noting in this example:

1. We regenerate the expression instead of making it once and pasting for each
   match. That is necessary because of :ref:`referencing restriction
   <no-referencing>`.
2. We have multiple new declarations with the same new namespace (`"NewNS"`).
   This most likely would not compile but this tool :ref:`does not enforce
   <checking-strictness>` language restrictions.

Printing an ndf Code Out
========================

If you want to print data out (for debugging purposes or whatever), you can do
the following:

.. literalinclude:: ../pages/code/print.py

This code should print out the following:

.. code-block:: none

    Complete assignment statement (printing the whole row):
    Obj1 is Type1
    (
        member1 = Obj2 is Type1
        (
            member1 = nil
        )
    )
    Object declaration only (row's value only):
    Type1
    (
        member1 = Obj2 is Type1
        (
            member1 = nil
        )
    )

There are 2 other functions you might find useful:

- :func:`printer.string`, returns ndf code as a string instead of dumping it to
  stdout.
- :func:`printer.format`, wtires ndf code out to an IO handle.
  :func:`printer.print` used above is actually a wrapper around this function.

General Recommendations and Caveats
===================================

Errors Suppression
------------------

Avoid using ``try`` clause or any other silently failing operations. If Eugen
renames or moves objects or members that you're editing - it's in your best
interest to let the script fail instead of silently ignoring missing member or
namespace. That way you will know 100% something has changed in the source code
and needs fixing instead of bashing your head over a compiled mod that doesn't
do what you expect from it.

For that reason some functions use ``strict`` argument with ``True`` by default
that forces them to fail if anything is off. Don't turn those off unless you
really know that it won't hurt you in the long run.

Nested Edits
------------

Avoid nesting ``with mod.edit(...)`` inside of another ``with mod.edit(...)`` if
they both access the same source file. First clause will build an independent
tree from pristine source mode. Second one will build another independent tree
from pristine source mode. When second clause ends, your file gets written out
with all the changes you made in the second clause. But your first tree still
holds data from original unedited tree. As soon as it gets written out, it will
overwrite anything you did in the second clause.

.. _checking-strictness:

Syntax Checking Strictness
--------------------------

`tree-sitter-ndf <ndf_>`__ parser is not a
language server so it will allow for some not-quite-correct expressions. It will
only catch the most bogus syntax errors while will let through things like
excessive commas, multiple ``unnamed`` definitions, clashing namespaces and
``member`` definitions at the root level. You can read more on this in
`tree-sitter-ndf's README.md <ndf_>`__.

.. _ndf: https://github.com/Ulibos/tree-sitter-ndf

.. _path-relativeness:

Path Relativeness
-----------------

By default python interprets relative paths relative to where the program was
started. If for example you have your script in ``C:\Users\User\Scripts\mod.py``
but run your terminal from ``C:\``, your script will interpret all relative paths
relative to ``C:\``. If you want your script to always internert paths relative
to itself, you can add these 2 lines at the beginning of your srcipt:

.. code:: python
   
   import os
   os.chdir(os.path.dirname(__file__))

This rule however is not applicable to :meth:`Mod.edit`, :meth:`Mod.parse_src` and
:meth:`Mod.parse_dst`. These methods operate relative to :attr:`Mod.mod_src` (for
:meth:`Mod.edit` and :meth:`Mod.parse_src`) and :attr:`Mod.mod_dst` (for
:meth:`Mod.parse_dst`, just make sure you generated some data there before trying
to access it).

.. _typing-ambiguity:

Typing Ambiguity
----------------

Ndf manual is not very clear on it's typing annotation rules. Consider the following
example:

.. code-block:: C

   MemberTyping is TObject(  // object is of type TObject
      // member is of type string
      StringMember : string = "Some text"  
      
      // case similar to one in the manual, we have both member and namespace names
      ObjectMember = InnerNamespace is TObject( ... )  

      // syntax allows for this in theory
      WtfMember : MType = CanWeDoThis is TObject( ... )
      AnotherOne : RGBA = RGBA[0, 0, 0, 1]
   )

Since there are no clear instructions on wheter this is possible and syntax
rules don't seem to prohibit such declaration, I had to opt for a cursed
solution - :class:`model.Template`, :class:`model.Object` and
:class:`model.List` have a ``type`` parameter that stores their mandatory type
declaration (``TObject`` in this example). So for these specific objects don't
rely on row's ``type`` parameter. For everything else Row's ``type`` is the way
to go.

.. _no-referencing:

No Referencing
--------------
:class:`model.DeclarationsList`, :class:`model.DeclListRow` and their subclasses
don't implement copying. If you get a value from one row (or a row itself) and
put it into another row then they both will refer to the same object in memory.
This will lead to unexpected edits at best (when modifying one item, other will
sync with it) and infinite recursions on printing at worst (if some object
happens to become a child of itself, irrespective of depth of such hierarchy).
This can be fixed in future by implementing deep copying on assignment.

.. _strict-attributes:

Strict Attributes in Edits
--------------------------

By default methods like :func:`model.DeclListRow.edit`,
:func:`model.DeclarationsList.add` and :func:`model.DeclarationsList.insert`
operate in a strict mode. This means that they don't allow to pass in parameters
that aren't supported by the Row/List type. This limitation is purely "cosmetic"
and servers one purpose: to help one catch errors early. If one deconstructs
an incompatible dict into an :func:`model.DeclarationsList.add` function, it
will raise and exception to warn about the error. By setting `_strict` attribute
to ``False`` one can put any attributes in the call, they will be simply ignored
by the function. An example of how it works and when one might want to override
the default behaviour:

.. code-block:: python

    >>> import ndf_parse as ndf
    >>> source = ndf.convert("export SomeObj is Object(a = 12)")
    >>> source
    [List[0](visibility='export', namespace='SomeObj', value=[Object[0](member='a', type=None, visibility=None, namespace=None, value='12')])]
    >>> source.add(n="PI", v="12", test="42")
    TypeError: Cannot set ListRow.test, attribute does not exist.
    >>> source.add(n="PI", v="12", test="42", _strict=False)  # disable strict
    List[1](visibility=None, namespace='PI', value='12')  # note there is no "test" attribute, it was dropped
    >>> my_param = {"n": "MyValue", "vis": "export", "v": "12", "description": "Something to use in script's debug output."}
    >>> source.add(**my_param, _strict=False)  # disabling strict mode because we are sure we won't break the list with our description
    List[2](visibility='export', namespace='MyValue', value='12')