===
abc
===

.. currentmodule:: ndf_parse.model.abc

.. automodule:: ndf_parse.model.abc


Classes
-------

.. autoclass:: Row

    .. autoproperty:: index

    .. autoproperty:: parent

    .. automethod:: from_ndf

    .. automethod:: copy

    .. automethod:: compare

    .. automethod:: edit

    .. automethod:: edit_ndf

    .. automethod:: as_dict

.. autoclass:: List
    :show-inheritance:

    .. autoproperty:: parent

    .. autoproperty:: parent_row

    .. add()

    .. method:: add(input: str) -> GR | list[GR]

        Add a row/rows to the list. `input` is an ndf code snippet. If the
        snippet contains one item then the method will return one created row.
        Else it will return a list of created rows.

        >>> lst.add("Value is 12, Second is 24")
        [ListRow[2](value='12', visibility=None, namespace='Value'),
        ListRow[3](value='24', visibility=None, namespace='Second')]
        >>> lst.add("Extra is 42")
        ListRow[4](value='42', visibility=None, namespace='Extra')

        :return: An added row/rows.

    .. method:: add(input: DictWrapped | GR) -> GR
        :noindex:

        Add a row to the list. `input` is an existing row or a dict
        representation of a row. If existing row is dangling then it is parented
        directly. If it has a parent - it's copy is added.

        >>> lst.add({"namespace": "Value", "value": "12"})
        ListRow[5](value='12', visibility=None, namespace='Value')

        :return: An added row.

    .. method:: add(input: Iterable[DictWrapped | GR | str]) -> list[GR]
        :noindex:

        Add rows to the list. `input` is a single iterable containing a set of
        row representations. Multiple iterables and nested iterables are not
        supported due to severe ambiguity (and lack of meaningful usecases).

        >>> lst.add(
        ...     [ListRow(v="12", n="Value"), {"n":"Other", "value": "24"}, "Extra is 42" ]
        ... )
        [ListRow[6](value='12', visibility=None, namespace='Value'),
        ListRow[7](value='24', visibility=None, namespace='Other'),
        ListRow[8](value='42', visibility=None, namespace='Extra')]
        >>> # but examples below will fail
        >>> lst.add(
        ...     [ "This is 'a fail'", "or is it" ],
        ...     [ "WellNowIt is '2 iterables won't work'", ListRow(v="no, seriously") ],
        ...     ListRow(v="I mean it")
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list
        >>> lst.add(
        ...     "Value is 12",
        ...     [ "This is 'where it fails'", "TrustMeThis is 'a nested iterable'" ],
        ...     "Extra is 42"
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list

        :return: Added rows.

    .. method:: add(*input: DictWrapped | GR | str) -> list[GR]
        :noindex:

        Same as previous override but in a decomposed form.

        >>> lst.add(
        ...     ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42"
        ... )
        [ListRow[9](value='12', visibility=None, namespace='Value'),
        ListRow[10](value='24', visibility=None, namespace='Other'),
        ListRow[11](value='42', visibility=None, namespace='Extra')]

        :return: Added rows.

    .. insert()

    .. method:: insert(key: int, input: str) -> GR | list[GR]

        Insert a row/rows into the list. `key` is an index at which to insert a
        new row/rows. `input` is an ndf code snippet. If the snippet contains
        one item then the method will return one created row. Else it will
        return a list of created rows.

        >>> lst.insert(5, "Value is 12, Second is 24")
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Second')]
        >>> lst.insert(5, "Extra is 42")
        ListRow[5](value='42', visibility=None, namespace='Extra')

        :return: An inserted row/rows.

    .. method:: insert(key: int, input: DictWrapped | GR) -> GR
        :noindex:

        Insert a row into the list. `key` is an index at which to insert a new
        row. `input` is an existing row or a dict representation of a row.
        If existing row is dangling then it is parented directly. If it has a
        parent - it's copy is added.

        >>> lst.insert( 5, {"namespace": "FromDict", "value": "69"})
        ListRow[5](value='69', visibility=None, namespace='FromDict')

        :return: An inserted row.

    .. method:: insert(key: int, input: Iterable[DictWrapped | GR | str]) -> list[GR]
        :noindex:

        Insert rows into the list. `key` is an index at which to insert new
        rows. `input` is a single iterable containing a set of row
        representations. Multiple iterables and nested iterables are not
        supported due to severe ambiguity (and lack of meaningful usecases).

        >>> lst.insert( 5,
        ...     [ ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42" ]
        ... )
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Other'),
        ListRow[7](value='42', visibility=None, namespace='Extra')]
        >>> # but examples below will fail
        >>> lst.insert( 5,
        ...     [ "This is 'a fail'", "or is it" ],
        ...     [ "WellNowIt is '2 iterables won't work'", ListRow(v="no, seriously") ],
        ...     ListRow(v="I mean it")
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list
        >>> lst.insert( 5,
        ...     "Value is 12",
        ...     [ "This is 'where it fails'", "TrustMeThis is 'a nested iterable'" ],
        ...     "Extra is 42"
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list

        :return: Inserted rows.

    .. method:: insert(key: int, *input: DictWrapped | GR | str) -> list[GR]
        :noindex:

        Same as previous override but in a decomposed form.

        >>> lst.insert( 5,
        ...     ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42"
        ... )
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Other'),
        ListRow[7](value='42', visibility=None, namespace='Extra')]

        :return: Inserted rows.

    .. replace()

    .. method:: replace(key: int | slice, input: str) -> GR | list[GR]

        Replace a row/rows in the list. `key` is an index or slice marking which
        row/rows to replace. `input` is an ndf code snippet. If the snippet
        contains one item then the method will return one created row. Else it
        will return a list of created rows.

        >>> # replace one with one
        >>> lst.replace(5, "Value is 12")
        ListRow[5](value='12', visibility=None, namespace='Value')
        >>> # if you want to replace 1 item with multiple then make it explicit with a slice
        >>> lst.replace(5, "Value is 12, Second is 24") # this will fail
        Traceback (most recent call last):
        ValueError: Cannot replace single item List[5] with multiple ones.
        >>> # replace index 5, note non-inclusive upper bound 6
        >>> lst.replace(slice(5, 6), "Value is 12, Second is 24")
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Second')]
        >>> # replace many with one
        >>> lst.replace(slice(1, 8), "Value is 12")
        ListRow[1](value='12', visibility=None, namespace='Value')

        :return: An inserted row/rows.

    .. method:: replace(key: int | slice, input: DictWrapped | GR) -> GR
        :noindex:

        Replace row/rows in the list. `key` is an index or slice marking which
        row to replace. `input` is an existing row or a dict representation
        of a row. If existing row is dangling then it is parented directly. If
        it has a parent - it's copy is added.

        >>> # replace one with one
        >>> lst.replace( 5, {"namespace": "Value", "value": "12"})
        ListRow[5](value='12', visibility=None, namespace='Value')
        >>> # replace many with one
        >>> lst.replace( slice(1, 8), {"namespace": "Value", "value": "12"})
        ListRow[1](value='12', visibility=None, namespace='Value')

        :return: An inserted row.

    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | GR | str]) -> list[GR]
        :noindex:

        Replace row/rows in the list. `key` is an index at which to insert new
        rows. `input` is a single iterable containing a set of row
        representations. Multiple iterables and nested iterables are not
        supported due to severe ambiguity (and lack of meaningful usecases).

        >>> # replace one with many
        >>> lst.replace( slice(5, 6),
        ...     [ ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42" ]
        ... )
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Other'),
        ListRow[7](value='42', visibility=None, namespace='Extra')]
        >>> # replace many with many (`len(added)` vs `len(removed)` don't have to match)
        >>> lst.replace( slice(1, 8),
        ...     [ ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42" ]
        ... )
        [ListRow[1](value='12', visibility=None, namespace='Value'),
        ListRow[2](value='24', visibility=None, namespace='Other'),
        ListRow[3](value='42', visibility=None, namespace='Extra')]
        >>> # but examples below will fail
        >>> lst.replace( slice(1, 8),
        ...     [ "This is 'a fail'", "or is it" ],
        ...     [ "WellNowIt is '2 iterables won't work'", ListRow(v="no, seriously") ],
        ...     ListRow(v="I mean it")
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list
        >>> lst.replace( slice(1, 8),
        ...     "Value is 12", [ "This is 'where it fails'",
        ...     "TrustMeThis is 'a nested iterable'" ], "Extra is 42"
        ... )
        Traceback (most recent call last):
        TypeError: Got unsupported type of row: list

        :return: Inserted rows.

    .. method:: replace(key: int | slice, *input: DictWrapped | GR | str) -> list[GR]
        :noindex:

        Same as previous override but in a decomposed form.

        >>> # replace one with many
        >>> lst.replace( slice(5, 6),
        ...     ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42"
        ... )
        [ListRow[5](value='12', visibility=None, namespace='Value'),
        ListRow[6](value='24', visibility=None, namespace='Other'),
        ListRow[7](value='42', visibility=None, namespace='Extra')]
        >>> # replace many with many (`len(added)` vs `len(removed)` don't have to match)
        >>> lst.replace( slice(1, 8),
        ...     ListRow(v="12", n="Value"),
        ...     {"n":"Other", "value": "24"},
        ...     "Extra is 42"
        ... )
        [ListRow[1](value='12', visibility=None, namespace='Value'),
        ListRow[2](value='24', visibility=None, namespace='Other'),
        ListRow[3](value='42', visibility=None, namespace='Extra')]

        :return: Inserted rows.

    .. remove()

    .. method:: remove(self, key: int) -> GR

        Remove a row. `key` is an indexable value that controls which rows to
        remove. Contrary to ``del row[int]`` this method returns back a removed
        dangling row.

        >>> lst.remove(5)
        ListRow[DANGLING](value='24', visibility=None, namespace='Other')

        :return: Removed row.

    .. method:: remove(self, key: slice) -> list[GR]
        :noindex:

        Remove rows. `key` is a slice that controls which rows to remove.
        Contrary to ``del row[slice]`` this method returns back removed
        dangling rows.

        >>> lst.remove(slice(1, 8))
        [ListRow[DANGLING](value='12', visibility=None, namespace='Value'),
        ListRow[DANGLING](value='24', visibility=None, namespace='Other'),
        ListRow[DANGLING](value='42', visibility=None, namespace='Extra'),
        ListRow[DANGLING](value='12', visibility=None, namespace='Value'),
        ListRow[DANGLING](value='42', visibility=None, namespace='Extra')]
        >>> # note that it does not fail if list-like doesn't have enough values
        >>> # for the slice, it returns as much as it can find.
        >>> lst.remove(slice(3, 3))
        []

        :return: Removed rows.

    .. -other methods

    .. automethod:: match_pattern

    .. I don't like copy-pasting an entire function dosctring one fucking bit but no better option for now.

    .. method:: find_by_cond(condition: callable[[GR], bool], strict: bool = True) -> GR | None

        Find a row by a condition. The condition is a function that returns
        ``True`` if a row satisfies all requirements. Always returns the first
        row that matches. Examples:

        >>> import ndf_parse as ndf
        >>> scene = ndf.convert("A is 12\nB is 24\nC is 24\nC is 42")  # note 2 values `24`
        >>> scene.find_by_cond(lambda x: x.v == '24')
        ListRow[1](value='24', visibility=None, namespace='B')
        >>> # first row matching the condition was returned

        This example is intentionally simple, but this method has it's use like
        catching a descriptor of specific type in a list of descriptors with no
        namespaces (Unit's module descriptors are a good example).

        :param callable[[GR], bool] condition: A function or a lambda that
            checks each row.
        :param bool, default=True strict: If strict and now row found then
            raises an error. Else returns ``None``.
        :raises TypeError: Errors out if in strict mode and no matching row as
            found.

    .. automethod:: compare

    .. automethod:: copy

    .. automethod:: inner


Utilities
---------

.. autofunction:: is_pair

Typing
------

.. data:: Pair
    :type: type alias

    A tuple with 2 values inside: :class:`tuple`\[:data:`CellValue`\, :data:`CellValue`\]

.. data:: CellValue
    :type: type alias

    :class:`model.List <ndf_parse.model.List>` |
    :class:`model.Object <ndf_parse.model.Object>` |
    :class:`model.Template <ndf_parse.model.Template>` |
    :class:`model.Map <ndf_parse.model.Map>` |
    :class:`str` | :data:`Pair`

.. data:: GR
    :type: type alias

    A Generic Row (a subclass of :class:`Row`).

.. data:: DictWrapped
    :type: type alias

    A dictionary representation of a row: :class:`dict`\[:class:`str`\, :data:`CellValue`\]