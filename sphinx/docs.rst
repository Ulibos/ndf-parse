#############
Documentation
#############


.. currentmodule:: ndf_parse

This documentation starts with a :ref:`quickstart <quick-start>` section with a
code showing main features of the library. The code gets explained below in 4
following secitons all tied up to the quickstart and showing alternative methods
to form an overall understanding of how this tool works:

#.  Setting up the mod.
#.  Searching and comparing things.
#.  Editing things.
#.  Creating/deleting things.

If you struggle to understand how ndf entities are represented in the model then
:ref:`read this primer on the model relations <model-representation>`.

.. _quick-start:

Quick Start
===========

Before We Begin
---------------

First thing we need to do is to set up a pristine copy of the mod sources. This
module works in the following way:

#.  Get a file from an unchanged mod (we'll refer to it as a *source mod*).
#.  Parse, convert to model representation.
#.  Apply our edits.
#.  Format back to ndf and write it to a directory with our final mod (we'll
    refer to it as a *destination mod*).

Generate a new source mod using ``CreateNewMod.bat`` provided by Eugen Systems
and place it to ``path/to/src/mod``.

Make The Script
---------------

We are going to make a mod that adds a :code:py:`'HE'` trait to all
autocannons, then we are going to add 2 new weapon types. Not the most useful
mod but it is enough to demonstrate the basic workflow.

Create a new python file, say, ``my_mod.py`` with the following code:

.. literalinclude:: code/quick_start.py
    :caption: quick_start.py
    :linenos:
    :lines: 3-

Run this script (but don't forget to substitute your mod paths first!) You
should see prints that correspond to operations from this sctipt. Now, if you
navigate to your newly generated mod and check ``Ammunition.ndf``, you should
find that every autocannon has the :code:py:`'HE'` trait and at the end of the
file there are 2 new ammo types.

Quick Start Explained
=====================

Setting Up
----------

Now let's go line by line and examine what this code does.

.. literalinclude:: code/quick_start.py
    :linenos:
    :lineno-start: 7
    :lines: 9-10

Here we initialize our :class:`Mod` object. It's nothing but a convenience
wrapper that saves you time from writing boilerplate code. Second line here
checks if your source mod was updated. Whenever the game gets an update - you
should delete your source mod and regenerate it anew. Next time when you run the
script, that second line detects it (by comparing modification date of source
and destination folders), nukes the destination mod and makes a new fresh copy
of it from the source.

.. warning::

    Never store anything important inside of source and destination folders! It
    will get nuked by such an update. Store it elsewhere or regenerate it with
    your script.

Edits
-----

.. literalinclude:: code/quick_start.py
    :linenos:
    :lineno-start: 10
    :lines: 12

:meth:`Mod.edit` loads the file, parses it, converts to a python representation
(based on :doc:`ndf-parse/model`), stores it internally as an :class:`Edit` and
returns a :class:`Mod` back. But since :class:`Mod` is implemented as a context
manager, within :code:py:`with` statement it returns a :class:`model.List`
that represents our ndf file and which we can alter. as soon as
:code:py:`with` statement's scope is closed (i.e. when all of the operations
defined in this block are completed), it will automatically format the
:class:`~model.List` back to ndf code and write the file out to the destination
mod.

.. note::

    If you are just tinkering with the code and don't want to write the file out on
    each test run, you can disable it by adding the following argument:

    .. code-block:: python
        :linenos:
        :lineno-start: 10

        with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf", False) as source:

You can also manually manage a bunch of edits at the same time. Suppose you want
to rework ammunition for specific decks only. For that you would need at least 4
files: ``Ammunition.ndf``, ``WeaponDescriptor.ndf``, ``UniteDescriptor.ndf`` and
``Decks.ndf`` of which you will edit only 3 (no edits for Decks). Then you would
do the following:

.. code-block:: python
    :caption: manual_write_control.py
    :linenos:

    import ndf_parse as ndf
    mod = ndf.Mod("path/to/src/mod", "path/to/dst/mod")
    # We don't want to write out decks because we only use them to query specific
    # units, so we set `save` argumet to ``False``
    decks_src = mod.edit(r"GameData\Generated\Gameplay\Decks\Decks.ndf", False).current_tree
    # others we will modify so we leave `save` at default (``True``)
    units_src = mod.edit(r"GameData\Generated\Gameplay\Gfx\UniteDescriptor.ndf").current_tree
    weap_src  = mod.edit(r"GameData\Generated\Gameplay\Gfx\WeaponDescriptor.ndf").current_tree
    ammo_src  = mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf").current_tree

    ...  # here we do all the work with 4 sources

    for edit in mod.edits:
        mod.write_edit(edit, False)  # ``False`` disables forced writing so it
                                     # respects `edit.save` attribute

.. _navigating-model-instances:

Navigating model Instances
--------------------------

Next section loops through the root declarations of the file (while matchig the
pattern):

.. literalinclude:: code/quick_start.py
    :linenos:
    :lineno-start: 12
    :lines: 14-16

All classes that are subclasses of :class:`model.abc.List` (I call them
"list-likes") are iterable as well as have length (``len(source)``). This means
that you can iterate through :class:`model.List`, :class:`model.Object` ,
:class:`model.Template` and :class:`model.Map`. Stray pairs (ones that are not
inside of a Map) are defined as a :class:`tuple`. Everything else is essentially
a string literal. This also means that :class:`~model.List`,
:class:`~model.Object` , :class:`~model.Template` and :class:`~model.Map` all
have a :attr:`~model.abc.List.parent` attribute while others don't. It's worth
noting that :class:`~model.Template` also has a :attr:`~model.Template.params`
attribute to store it's generic parameters.

Each returned ``obj_row`` is a subclass of a :class:`model.abc.Row` Here is
a correspondence table of all list-likes and their rows:

+-------------------------+-------------------------+--------------------------+
|    ndf Code Entities    |      Parent Class       |         Row Class        |
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

:ref:`Here is <model-representation>` a more detailed representation of how each
model row maps to a corresponding ndf expression.

.. note::

    Rows are built with no referencing in mind. You can reference them in
    arbitrary variables or python's builtin types but anytime you insert them
    into model's lists, they insert a copy instead of self (except for dangling
    rows, they insert themselves without doing a copy). This is done to prevent
    unexpected edits of the original rows. :ref:`More on that here, with
    examples. <no-referencing>`

.. _search-tools:

Search Tools
------------

Currently there are 4 main ways to search items of interest:

#.  :meth:`model.abc.List.match_pattern <List.match_pattern()>`. Good for
    matching items with some shared "trait" in a single list-like (as in the
    quickstart code, :ref:`lines 12-13
    <navigating-model-instances>`).
#.  A recursive :func:`walk`. Good for cases when one needs to walk an entire
    subtree (i.e. also search inside children of a list-like) and/or match on a
    complex parameter. If we were to reformulate our pattern search with a
    walker, it would look like this:

    .. code-block:: python
        :caption: quick_start_v2.py
        :linenos:
        :lineno-start: 10

        def is_autocannon(row):
            return (isinstance(row, ndf.model.ListRow)  # ensure it's a row,
                    # because `walk` is recursice and compares everything here,
                    # including source itself!
                and isinstance(row.v, ndf.model.Object)  # ensure there is an
                    # object in this row
                and row.v.type == "TAmmunitionDescriptor"  # ensure it's the
                    # type we need. `type` attr is specific to ObjectRow and
                    # it's subclasses!
                and row.v.by_member("Caliber").v == "'DYDXERZARY'"  # ensure it's a
                    # 30mm autocannon. Note embedded ^  single  ^ quotes!
                and not any(item.v == "'HE'" for item in row.v.by_member("TraitsToken").v)
                )

        with mod.edit(r"GameData\Generated\Gameplay\Gfx\Ammunition.ndf") as source:
            for row in ndf.walk(source, is_autocannon):
                # any row here is a 30mm autocannon with no 'HE', just ad one
                row.v.by_member("TraitsToken").v.add(value="'HE'")

    **Cons:** very verbose (all filtering is explicit), processes too many extra
    nodes, we call ``by_member`` a couple times which is a bit costly.

    **Pros:** allows for very complex filtering, walks entire tree which is
    necessary in some cases.

    To summarize: a very specific filter for very specific tasks that is good
    to have non the less.


#.  :meth:`~model.List.by_namespace`, :meth:`~model.Object.by_member`,
    :meth:`~model.Params.by_param`, :meth:`~model.Map.by_key` and similar
    methods for finding a single unique element. Strict by default (i.e. will
    raise an error and terminate execution if item is not found) which is good
    for not getting surprising silent bugs if Eugen removes some field one was
    relying on.

#.  Manually :meth:`~model.abc.List.compare` list-likes and
    :meth:`~model.abc.Row.compare` rows. In fact this is what is used under the
    hood for :meth:`abc.List.match_pattern() <model.abc.List.match_pattern>`.

Get and Set Values
------------------

Get and Set Values for Rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting and setting values in rows is pretty straightforward:

.. doctest::

    >>> import ndf_parse as ndf
    >>> row = ndf.model.ListRow.from_ndf("Namespace is 12")
    >>> row.namespace  # get namespace
    'Namespace'
    >>> row.n  # same but with an alias
    'Namespace'
    >>> row.value  # get value (also has an alias, `v`)
    '12'
    >>> # get row's visibility (has an alias `vis`, stores values like
    >>> # 'unnamed', 'export' etc.)
    >>> row.visibility
    >>> # ^ will not print anything because it's `None`
    >>> #
    >>> # set a value
    >>> row.v = 24
    >>> row.namespace = "NewName"
    >>> row.vis = 'export'
    >>> ndf.printer.print(row)
    export NewName is 24

All possible values and methods for rows are documented in :mod:`.model` plus
shared methods are described in :class:`model.abc.Row`.

Get and Set Values for List-Likes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List-likes can be queried for items as any other pythonic list. Above that they
have methods for searching (and removing) rows by specific attributes (as was
demonstrated in :ref:`search tools <search-tools>`). They also share a bunch of
methods like :meth:`~model.abc.List.add` (used in quickstart to add a ``'HE'``
trait), :meth:`~model.abc.List.insert`, :meth:`~model.abc.List.replace` and
:meth:`~model.abc.List.remove`. Their API is well documented in their
:class:`parent class <model.abc.List>`.

A couple things worth mentioning:

#.  :class:`~model.Map` differs from others in that it also accepts pairs as
    row representations:

    .. doctest::

        >>> import ndf_parse as ndf
        >>> mymap = ndf.model.Map()
        >>> mymap.add(("'key1'", "'value1'"), ("'key2'", "24"))
        [MapRow[0](key="'key1'", value="'value1'"),
        MapRow[1](key="'key2'", value='24')]
        >>> ndf.printer.print(mymap)
        MAP[('key1', 'value1'), ('key2', 24)]

#.  :class:`model.List`, :class:`model.Object` and :class:`model.Template` all
    store their type inside of their own :attr:`~model.Object.type` attribute
    instead of row's one. This issue is covered in detail in :ref:`typing
    ambiguity <typing-ambiguity>` section.

#.  :class:`model.List` differs in how it :ref:`parses ndf code snippets
    <source-is-a-list-but-its-not>`.

#.  All row types are convertable into an integer. They return their index within
    a parent list-like. This allows us to do the following:

    .. testsetup:: indexing

        import ndf_parse as ndf
        mymap = ndf.model.Map()
        mymap.add(ndf.model.MapRow(k=f"Key{i}", v=f"{i}") for i in range(8))
        row_from = mymap[3]
        row_to = mymap[6]

    .. doctest:: indexing

        >>> row_from, row_to  # two rows from a list
        (MapRow[3](key='Key3', value='3'),
        MapRow[6](key='Key6', value='6'))
        >>> mymap  # the list
        Map[MapRow[0](key='Key0', value='0'),
        MapRow[1](key='Key1', value='1'),
        MapRow[2](key='Key2', value='2'),
        MapRow[3](key='Key3', value='3'),
        MapRow[4](key='Key4', value='4'),
        MapRow[5](key='Key5', value='5'),
        MapRow[6](key='Key6', value='6'),
        MapRow[7](key='Key7', value='7')]
        >>> del mymap[row_from : row_to]
        >>> mymap  # list has now lost 3 rows including the `row_from`
        Map[MapRow[0](key='Key0', value='0'),
        MapRow[1](key='Key1', value='1'),
        MapRow[2](key='Key2', value='2'),
        MapRow[3](key='Key6', value='6'),
        MapRow[4](key='Key7', value='7')]
        >>> row_from  # it is now dangling
        MapRow[DANGLING](key='Key3', value='3')
        >>> row_to  # this row is tracking it's position accordingly
        MapRow[3](key='Key6', value='6')
        >>> mymap.remove(row_to) # remove the second too
        MapRow[DANGLING](key='Key6', value='6')

    .. caution::

        Just don't try using a dangling pointer as an index, it will crash.

Create New Values
-----------------

Create New List-Likes
~~~~~~~~~~~~~~~~~~~~~

Lists are all mostly created via a direct constructor call. The logic is "make
a new list and add stuff after". Examples:

.. doctest::

    >>> import ndf_parse as ndf
    >>> md = ndf.model  # an alias for brevity
    >>> ndf_print = ndf.printer.print  # also an alias
    >>> # a new map
    >>> md.Map()
    Map[]
    >>> # a new template
    >>> tpl = md.Template()
    >>> tpl
    Template[]
    >>> tpl.params  # we can also query it's md.Params section if we want
    Params[]
    >>> md.Params()  # or make a new one
    Params[]
    >>> # a new list
    >>> lst = md.List()
    >>> ndf_print(lst)
    []
    >>> lst.type = "RGB"  # make it typed
    >>> ndf_print(lst)
    RGB[]
    >>> ndf_print(md.List(type="RGB"))  # or create it already typed
    RGB[]
    >>> # a new source
    >>> md.List(is_root=True)
    List[]
    >>> # yes, source is just a List with a flag on. And you can convert
    >>> # one into the other just by altering `lst.is_root` parameter.
    >>> # this also affects the type of snippets it accepts, more on that
    >>> # in "Source Is a List But It's Not" section.`

It would be nice to have an option to directly initialize them with code
snippets, like :code:py:`md.List("A is 12, B is 24")` but there are 2 issues:
:ref:`List is a special case <source-is-a-list-but-its-not>` that makes parsing
snippets context-dependent and a risk of type collisions for list-like args vs
row args. This is resolvable in the future, it just requires time. For now if
one is really determined in creating lists via snippets, there is a workaround:

.. doctest::

    >>> import ndf_parse as ndf
    >>> md = ndf.model
    >>> ndf_print = ndf.printer.print
    >>> # a new source from a snippet
    >>> source = ndf.convert("A is 12\nB is 24\nC is Obj(memb = 12)")  # \n denotes a newline
    >>> ndf_print(source)
    A is 12
    B is 24
    C is Obj
    (
        memb = 12
    )
    >>> source = ndf.convert("""
    ... A is 12
    ... B is 24
    ... C is Obj(memb = 12)
    ... """) # snippet with multiline string, a bit easier to read
    >>> ndf_print(source)
    A is 12
    B is 24
    C is Obj
    (
        memb = 12
    )
    >>> # any Map/List/Object/Template (Param is a bit tricky, but doable)
    >>> # snippet below will return a dict with row's arguments mapped as keys
    >>> # (it's this way because of how internal converter works, just accept it as is)
    >>> dict_wrapped = ndf.expression("MAP[('A', 1), ('B', 2)]")
    >>> dict_wrapped
    {'value': Map[MapRow[0](key="'A'", value='1'), MapRow[1](key="'B'", value='2')]}
    >>> dict_wrapped['value']  # fetch the row itself
    Map[MapRow[0](key="'A'", value='1'), MapRow[1](key="'B'", value='2')]
    >>> ndf.expression("MAP[('A', 1), ('B', 2)]")['value']  # same, just a oneliner
    Map[MapRow[0](key="'A'", value='1'), MapRow[1](key="'B'", value='2')]
    >>> # you can make a helper function if ypu use it alot
    >>> def mk_listlike(snippet):
    ...     return ndf.expression(snippet)['value']
    ...
    >>> mk_listlike("[1, 2, 3]")
    List[ListRow[0](value='1', visibility=None, namespace=None),
    ListRow[1](value='2', visibility=None, namespace=None),
    ListRow[2](value='3', visibility=None, namespace=None)]
    >>> mk_listlike("MAP[('A', 1), ('B', 2)]")
    Map[MapRow[0](key="'A'", value='1'), MapRow[1](key="'B'", value='2')]
    >>> mk_listlike("Obj(memb1 = 12\nmemb2 = 24)")
    Object[MemberRow[0](value='12', member='memb1', type=None,
    visibility=None, namespace=None),
    MemberRow[1](value='24', member='memb2', type=None,
    visibility=None, namespace=None)]
    >>> mk_listlike("template Templ[parm1, parm2 = 12] is Obj(memb1 = <parm1>\nmemb2 = <parm2>)")
    Template[MemberRow[0](value='<parm1>', member='memb1', type=None, visibility=None, namespace=None),
    MemberRow[1](value='<parm2>', member='memb2', type=None, visibility=None, namespace=None)]
    >>> # or grab just params of a template
    >>> mk_listlike("template T[parm1, parm2 = 12] is Obj()").params
    Params[ParamRow[0](param='parm1', type=None, value=None),
    ParamRow[1](param='parm2', type=None, value='12')]
    >>> # and here is a demonstration of how `expression` works since we're at it
    >>> ndf.expression("template T[parm1, parm2 = 12] is Obj()")
    {'value': Template[], 'namespace': 'T'}
    >>> ndf.expression("export Name is Obj()")
    {'value': Object[], 'namespace': 'Name', 'visibility': 'export'}

Create New Rows
~~~~~~~~~~~~~~~

New rows can be created in a multitude of ways:

#.  Create rows directly inside of a list:

    .. doctest::

        >>> import ndf_parse as ndf
        >>> lst = ndf.model.List()
        >>> lst.add("A is 12")  # create via snippet
        ListRow[0](value='12', visibility=None, namespace='A')
        >>> lst.add({'value': "24", 'namespace': "B"})  # create as a dict
        ListRow[1](value='24', visibility=None, namespace='B')
        >>> lst.add(value="42", namespace="C")  # create directly via args
        ListRow[2](value='42', visibility=None, namespace='C')

    .. note::

        List-likes also support methods like :meth:`~model.abc.List.insert`,
        :meth:`~model.abc.List.replace`, :meth:`~model.abc.List.remove` as well
        as pythonic getters/setters (`lst[0] = ...`). Please read :class:`the
        reference <model.abc.List>`, it's extensively documented there plus
        some additional info (like ability to add rows via lists and iterables).

    .. note::

        :class:`~model.Map` has additional ability to accept rows as plain
        python tuples:

        .. doctest::

            >>> mymap = ndf.model.Map()
            >>> mymap.add(("A", "1"))
            MapRow[0](key='A', value='1')
            >>> # pythonic way with a caveat
            >>> mymap[0] = ("B", "2"),  # >>> NOTE THE COMMA AT THE END <<<
            >>> mymap
            Map[MapRow[0](key='B', value='2')]

        You can find out :class:`here <model.Map>` why there is an extra comma
        in a pythonic setter.

#. Create dangling rows with snippets:

    .. doctest::

        >>> import ndf_parse as ndf
        >>> md = ndf.model
        >>> md.ListRow.from_ndf("private Namespace is Value")
        ListRow[DANGLING](value='Value', visibility='private', namespace='Namespace')
        >>> md.MemberRow.from_ndf("member_name : member_type = Value")
        MemberRow[DANGLING](value='Value', member='member_name',
        type='member_type', visibility=None, namespace=None)
        >>> md.ParamRow.from_ndf("param_name: param_type = Value")
        ParamRow[DANGLING](param='param_name', type='param_type', value='Value')
        >>> md.MapRow.from_ndf("('key', Value)")  # note there are parenthesies!
        MapRow[DANGLING](key="'key'", value='Value')

#. Create dangling rows manually:

    .. doctest::

        >>> # from dict decomposition (supports aliases)
        >>> md.ListRow(**{'value':'Value', 'vis':'private', 'n':'Namespace'})
        ListRow[DANGLING](value='Value', visibility='private', namespace='Namespace')
        >>> # from args (supports aliases)
        >>> md.MemberRow(v='Value', m='member_name', t='member_type', vis=None, n=None)
        MemberRow[DANGLING](value='Value', member='member_name',
        type='member_type', visibility=None, namespace=None)
        >>> # special case for Map - pair tuple
        >>> md.MapRow(('key', 'Value'))
        MapRow[DANGLING](key='key', value='Value')

Delete Items
------------

To delete a value from a row simply replace it with :code:py:`None` (for
optionals) or a new value (for mandatory parameters, like :attr:`ListRow.value
<model.ListRow.value>`):

.. doctest::

    >>> import ndf_parse as ndf
    >>> row = ndf.model.ListRow.from_ndf("A is Obj(memb = 12)")
    >>> val = row.value
    >>> val.parent_row  # inner list-like has the row as it's parent
    ListRow[DANGLING](value=Object[MemberRow[0](value='12', member='memb',
    type=None, visibility=None, namespace=None)], visibility=None, namespace='A')
    >>> row.value = "12"
    >>> # note that on replacing the value the row automatically unparents the
    >>> # inner list-like
    >>> val.parent_row is None
    True

To delete a row from a list simply use:

.. doctest::

    >>> source = ndf.convert("A is 12\nB is 24\nC is 42")
    >>> del source[1]
    >>> source
    List[ListRow[0](value='12', visibility=None, namespace='A'),
    ListRow[1](value='42', visibility=None, namespace='C')]
    >>> # we can also use the row itself as an index if needed
    >>> row = source[0]
    >>> row
    ListRow[0](value='12', visibility=None, namespace='A')
    >>> del source[row]
    >>> # note that on deleting the row the list automatically unparents it
    >>> row
    ListRow[DANGLING](value='12', visibility=None, namespace='A')

Printing an NDF Code Out
========================

If you want to print data out (for debugging purposes or whatever), you can do
the following:

.. literalinclude:: code/print.py
    :linenos:

This code should print out the following:

.. code-block:: ndf
    :caption: Ndf Output

    // Complete assignment statement (printing the whole row):
    Obj1 is Type1
    (
        member1 = Obj2 is Type1
        (
            member1 = nil
        )
    )
    // Object declaration only (row's value only):
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

Avoid using :code:py:`try` clause or any other silently failing operations. If
Eugen renames or moves objects or members that you're editing - it's in your
best interest to let the script fail instead of silently ignoring missing member
or namespace. That way you will know 100% something has changed in the source
code and needs fixing instead of bashing your head over a compiled mod that
doesn't do what you expect from it.

For that reason some functions use ``strict`` argument with :code:py:`True` by
default `(more on that here) <strict-attributes_>`__ that forces them to fail if
anything is off. Don't turn those off unless you really know that it won't hurt
you in the long run.

Nested Edits
------------

Avoid nesting :code:py:`with mod.edit(...)` inside of another :code:py:`with
mod.edit(...)` if they both access the same source file. First clause will build
an independent tree from pristine source mode. Second one will build another
independent tree from pristine source mode. When second clause ends, your file
gets written out with all the changes you made in the second clause. But your
first tree still holds data from original unedited tree. As soon as it gets
written out, it will overwrite anything you did in the second clause.

.. _checking-strictness:

Syntax Checking Strictness
--------------------------

`tree-sitter-ndf <ndf_>`__ parser is not a language server so it will allow for
some not-quite-correct expressions. It will only catch the most bogus syntax
errors while will let through things like excessive commas, multiple ``unnamed``
definitions, clashing namespaces and ``member`` definitions at the root level.
You can read more on this in `tree-sitter-ndf's README.md <ndf_>`__.

.. _ndf: https://github.com/Ulibos/tree-sitter-ndf

.. _source-is-a-list-but-its-not:

Source Is a List But It's Not
-----------------------------

Ndf syntax is inconsistent with respect to usage of commas. If you have an ndf
list then you have to separate entries with commas:

.. code-block:: ndf
    :caption: Ndf Code

    [var1 is 12, var2 is 24, var3 is 42, SomeObject is Type(member1 = 12)]

On the other hand, the root level declarations always use newlines and never
commas:

.. code-block:: ndf
    :caption: Ndf Code

    var1 is 12
    var2 is 24
    var3 is 42
    SomeObject is Type(member1 = 12)

Both declarations operate virtually the same way so :mod:`ndf_parse` uses the
same class (:class:`model.List`) to implement both, the only thing that makes
the difference is the :attr:`model.List.is_root` attribute. If it's
:code:py:`True` then it will act like a source root. It will print with
newlines instead of commas and will expect ndf code arguments to
:meth:`~model.abc.List.insert` and :meth:`~model.abc.List.add` with newlines as
statements separators. If :attr:`~model.List.is_root` is :code:py:`False` then
it will act like a simple list and will expect ndf code arguments to have commas
as separators. Examples:

.. code-block:: python

    >>> import ndf_parse as ndf
    >>> md = ndf.model
    >>> lst = md.List(is_root=False)  # initialize as a simple list
    >>> lst.add("1, 2, 3")
    [List[0](value='1', visibility=None, namespace=None),
    List[1](value='2', visibility=None, namespace=None),
    List[2](value='3', visibility=None, namespace=None)]
    >>> ndf.printer.print(lst)
    [1, 2, 3]
    >>> lst.is_root = True  # switch it to behave like a source root
    >>> lst.add("""
    ... 4
    ... Obj is 5
    ... Obj is Type()
    ... """)
    [List[3](value='4', visibility=None, namespace=None),
    List[4](value='5', visibility=None, namespace='Obj'),
    List[5](value=Object[], visibility=None, namespace='Obj')]
    >>> ndf.printer.print(lst)
    1
    2
    3
    4
    Obj is 5
    Obj is Type()

.. _path-relativeness:

Path Relativeness
-----------------

By default python interprets relative paths relative to where the program was
started. If for example you have your script in ``C:\Users\User\Scripts\mod.py``
but run your terminal from ``C:\``, your script will interpret all relative paths
relative to ``C:\``. If you want your script to always interpert paths relative
to itself, you can add these 2 lines at the beginning of your srcipt:

.. code-block:: python

   import os
   os.chdir(os.path.dirname(__file__))

This rule however is not applicable to :meth:`Mod.edit`, :meth:`Mod.parse_src`
and :meth:`Mod.parse_dst`. These methods operate relative to :attr:`Mod.mod_src`
(for :meth:`Mod.edit` and :meth:`Mod.parse_src`) and :attr:`Mod.mod_dst` (for
:meth:`Mod.parse_dst` and :meth:`Mod.write_edit`, just make sure you generated
some data there before trying to access it).

.. _typing-ambiguity:

Typing Ambiguity
----------------

Ndf manual is not very clear on it's typing annotation rules. Consider the following
example:

.. code-block:: ndf
    :caption: Ndf Code

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
:class:`model.abc.List`, :class:`model.abc.Row` and their subclasses are
implemented with no copy by reference in mind. This is done to prevent
unexpected side effects when editing data (accidentally mutating the row you
wanted to copy). An example to illustrate the issue:

.. code-block:: python

    >>> # this is not an ``ndf_parse`` code, these are builtin python types
    >>> data_source = {'name': 'my_variable', 'value': '12'}
    >>> scene = []
    >>> scene.append(data_source)  # we want to copy our data
    >>> scene.append(data_source)  # we want to make another copy and edit it
    >>> scene[1]['value'] = '24'  # edit the second item in the list
    >>> scene[1]  # check the edit
    {'name': 'my_variable', 'value': '24'}
    >>> # all good, value is edited
    >>> scene[0]  # check that the first item is still 12
    {'name': 'my_variable', 'value': '24'}
    >>> # what?.. both values have changed
    >>> data_source  # check the original dict just in case
    {'name': 'my_variable', 'value': '24'}
    >>> # !!! all 3 have changed !!!

This happens because by default mutable objects (which are the vast majority in
python) are passed by reference. So ``data_source`` and both ``scene`` entries
reference the same place in memory. We can easily fix it by importing the
``copy`` module and appending like
:code:py:`scene.append(copy.deepcopy(data_source))` but that would become very
verbose very fast. So :mod:`ndf_parse` is implemented with deep copying on
assignment (to it's lists) by default. Whenever a :class:`model.abc.Row` is
inserted into a :class:`~model.abc.List`, it always makes a deep copy of itself
(only exception is if it was a dangling row, i.e. it had no parent list
previously). An example to illustrate the implementation:

.. code-block:: python

    >>> # this is an ``ndf_parse`` code with it's types
    >>> import ndf_parse as ndf
    >>> md = ndf.model  # a simple alias to save on typing
    >>> scene = md.List(is_root=True)  # make a scene
    >>> row = md.ListRow(value='12', namespace='Var1')  # create a dangling row
    >>> row  # check it
    ListRow[DANGLING](value='12', visibility=None, namespace='Var1')
    >>> scene.add(row)  # add 1st row, will get attached because is dangling
    List[0](value='12', visibility=None, namespace='Var1')
    >>> row is scene[0]  # our row is now attached to the scene
    True
    >>> scene.add(row)  # add 2nd row, will copy because already has a parent
    List[1](value='12', visibility=None, namespace='Var1')
    >>> row is scene[1]  # make sure second insert is a new object
    False
    >>> scene[1].v = '24'  # edit the second row
    >>> scene[1]  # check the edit
    List[1](value='24', visibility=None, namespace='Var1')
    >>> scene[0]  # check the original
    List[0](value='12', visibility=None, namespace='Var1')
    >>> # all good, value is still 12
    >>> # if you want your ``row`` variable to point to the last inserted row
    >>> # for ease of editing, then do this:
    >>> row = scene.add(row)  # ``add()`` will return the inserted row
    >>> row is scene[2]  # row now refers to the last insertion
    True
    >>> row is scene[0]  # and no longer refers to the first insertion
    False


.. _strict-attributes:

Strict Attributes in Edits
--------------------------

By default methods like :func:`~model.abc.Row.edit`, :func:`~model.abc.List.add`
and :func:`~model.abc.List.insert` operate in a strict mode. This means that
they don't allow to pass in parameters that aren't supported by the Row/List
type. This limitation is purely "cosmetic" and servers one purpose: to help one
catch errors early. If one deconstructs an incompatible dict into an
:func:`~model.abc.List.add` function, it will raise and exception to warn about
the error. By setting `_strict` attribute to :code:py:`False` one can put any
attributes in the call, they will be simply ignored by the function. An example
of how it works and when one might want to override the default behaviour:

.. code-block:: python

    >>> import ndf_parse as ndf
    >>> source = ndf.convert("export SomeObj is Obj(a = 12)")
    >>> source
    List[List[0](value=Object[Object[0](value='12', member='a', type=None,
    visibility=None, namespace=None)], visibility='export', namespace='SomeObj')]
    >>> source.add(n="PI", v="12", test="42")
    Traceback (most recent call last):
        ...
    TypeError: Cannot set ListRow.test, attribute does not exist.
    >>> source.add(n="PI", v="12", test="42", _strict=False)  # disable strict
    List[1](value='12', visibility=None, namespace='PI')
    >>> # note there is no "test" attribute, it was dropped
    >>> my_param = {"n": "MyValue", "vis": "export", "v": "12",
    ... "description": "Something to use in script's debug output."}
    >>> source.add(**my_param, _strict=False)  # disabling strict mode because
    >>> # we are sure we won't break the list with our description
    List[2](value='12', visibility='export', namespace='MyValue')

.. _comparing-strings:

Comparing Strings
-----------------

This tool cuts corners by representing anything that is not a fundamental
structural element (any list-like) as a string. That includes ref paths (even
though the underlying parser knows how to parse those), expressions, ints floats
and strings too. To distinguish, say, an int :code:ndf:`12` from a string
:code:ndf:`"12"` we embed quotes themselves into python's strings. So if we
have an ndf code that looks like this:

.. code-block:: ndf
    :caption: Ndf Code

    SomeInt is 12 // This is an int
    SomeString is "12" // this is a string, not an int
    IllMakeYouSuffer is '12' // string again but with single quotes

We would get the following items in python:

.. code-block:: python

    ListRow(value='12', visibility=None, namespace='SomeInt')
    #              v  v note embedded quotes in `value`
    ListRow(value='"12"', visibility=None, namespace='SomeString')
    #              v  v note embedded quotes but inverted (python adapts to the content)
    ListRow(value="'12'", visibility=None, namespace='IllMakeYouSuffer')

The caveat is that even though `SomeString` and `IllMakeYouSuffer` are logically
the same thing, in python :code:py:`'"12"' != "'12'"` ! It would be nice to
account for that in :meth:`Row.compare() <ndf_parse.model.abc.Row.compare>`
method but for now it's not there because 1) time 2) edge cases. So you should
be careful when comparing such stuff. Since you know the context when working
with specific data, you can either keep track of which quotes you are using or
strip them before comparing stuff. First method is preferrable because you can't
embed stripping inside existing methods like aforementioned :meth:`Row.compare()
<ndf_parse.model.abc.Row.compare>`.


