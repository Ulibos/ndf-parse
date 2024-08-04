=====
model
=====

.. toctree::
   :maxdepth: 1
   :caption: Submodules:

   model/abc

.. currentmodule:: ndf_parse.model

.. automodule:: ndf_parse.model

Row Classes
^^^^^^^^^^^

.. autoclass:: ListRow
    :show-inheritance:

    .. autoproperty:: index

    .. autoproperty:: parent

    .. property:: value() -> CellValue

        Value of this row.

        .. property:: v()

        An alias for :attr:`value`.

    .. property:: visibility() -> str | None

        Visibility modifier of the assignment. Should be one of these:
        ``'unnamed'`` | ``'export'`` | ``'private'`` | ``'public'``
        Keep in mind that it won't protect from ``'unnamed'`` actually having a
        name or appearing multiple times the List, see :ref:`notes on checking
        strictness <checking-strictness>`.

        .. property:: vis()

        An alias for :attr:`visibility`.

    .. property:: namespace() -> str | None

        Namespace name of the assignment.

        .. property:: n()

        An alias for :attr:`namespace`.

    .. -methods

    .. classmethod:: from_ndf(code) -> ListRow

        Create a row from an ndf code snippet. More details:
        :meth:`abc.Row.from_ndf`.

    .. method:: copy() -> ListRow

        Performs a deep copy of a row. More details: :meth:`abc.Row.copy`.

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Compares this row with a given row or a row representation.
        `existing_only` affects comparison mode (pattern matching if ``True``,
        strict comparison if ``False``) More details with examples:
        :meth:`abc.Row.compare`.

    .. method:: edit(_strict: bool = True, **kwargs) -> self

        Edit several parameters at a time. Supports parameter aliases. More
        details: :meth:`abc.Row.edit`.

    .. method:: edit_ndf(code) -> self

        Edit row with an ndf code snippet. More details with an example:
        :meth:`abc.Row.edit_ndf`.

    .. automethod:: as_dict

.. autoclass:: MapRow
    :show-inheritance:

    .. autoproperty:: parent

    .. autoproperty:: index

    .. property:: key() -> CellValue | None

        First value of a pair.

        .. property:: k()

        An alias for :attr:`key`.

    .. property:: value() -> CellValue | None

        Second value of a pair.

        .. property:: v()

        An alias for :attr:`value`.

    .. -methods

    .. classmethod:: from_ndf(code) -> MapRow

        Create a row from an ndf code snippet. More details:
        :meth:`abc.Row.from_ndf`.

    .. method:: copy() -> MapRow

        Performs a deep copy of a row. More details: :meth:`abc.Row.copy`.

    .. automethod:: compare

    .. automethod:: edit(_strict: bool = True, **kwargs) -> self

    .. method:: edit_ndf(code) -> self

        Edit row with an ndf code snippet. More details with an example:
        :meth:`abc.Row.edit_ndf`.

    .. automethod:: as_dict

.. autoclass:: MemberRow
    :show-inheritance:

    .. autoproperty:: parent

    .. autoproperty:: index

    .. property:: value() -> CellValue

        Value of this row.

    .. property:: v()

        An alias for :attr:`value`.

    .. property:: member() -> str | None

        Member name of the object.

    .. property:: m()

        An alias for :attr:`member`.

    .. property:: type() -> str | None

        Typing data for this object. Keep in mind,
        :ref:`not all types are stored here. <typing-ambiguity>`

    .. property:: t()

        An alias for :attr:`type`.

    .. property:: visibility() -> str | None

        Visibility modifier of the assignment. Should be one of these:
        ``'export'`` | ``'private'`` | ``'public'``

    .. property:: vis()

        An alias for :attr:`visibility`.

    .. property:: namespace() -> str | None

        Namespace name of the assignment.

    .. property:: n()

        An alias for :attr:`namespace`.

    .. classmethod:: from_ndf(code) -> MemberRow

        Create a row from an ndf code snippet. More details:
        :meth:`abc.Row.from_ndf`.

    .. method:: copy() -> MemberRow

        Performs a deep copy of a row. More details: :meth:`abc.Row.copy`.

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Compares this row with a given row or a row representation.
        `existing_only` affects comparison mode (pattern matching if ``True``,
        strict comparison if ``False``) More details with examples:
        :meth:`abc.Row.compare`.

    .. method:: edit(_strict: bool = True, **kwargs) -> self

        Edit several parameters at a time. Supports parameter aliases. More
        details: :meth:`abc.Row.edit`.

    .. method:: edit_ndf(code) -> self

        Edit row with an ndf code snippet. More details with an example:
        :meth:`abc.Row.edit_ndf`.

    .. automethod:: as_dict

.. autoclass:: ParamRow
    :show-inheritance:

    .. autoproperty:: parent

    .. autoproperty:: index

    .. property:: param() -> str

        Template parameter name.

    .. property:: p()

        An alias for :attr:`param`.

    .. property:: type() -> str | None

        Typing data for this template parameter.

    .. property:: t()

        An alias for :attr:`type`.

    .. property:: value() -> CellValue | None

        Value of this template parameter.

    .. property:: v()

       An alias for :attr:`value`.

    .. classmethod:: from_ndf(code) -> ParamRow

        Create a row from an ndf code snippet. More details:
        :meth:`abc.Row.from_ndf`.

    .. method:: copy() -> ParamRow

        Performs a deep copy of a row. More details: :meth:`abc.Row.copy`.

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Compares this row with a given row or a row representation.
        `existing_only` affects comparison mode (pattern matching if ``True``,
        strict comparison if ``False``) More details with examples:
        :meth:`abc.Row.compare`.

    .. method:: edit(_strict: bool = True, **kwargs) -> self

        Edit several parameters at a time. Supports parameter aliases. More
        details: :meth:`abc.Row.edit`.

    .. method:: edit_ndf(code) -> self

        Edit row with an ndf code snippet. More details with an example:
        :meth:`abc.Row.edit_ndf`.

    .. automethod:: as_dict

List-like Classes
^^^^^^^^^^^^^^^^^

.. autoclass:: List
    :show-inheritance:

    .. attribute:: is_root
        :type: bool
        :value: False

        Indicates whether this is a source root or any other nested item. Needed
        for :mod:`.printer` format them differently.

    .. attribute:: type
        :type: str | None
        :value: None

        Stores type for vector types (like :code:ndf:`RGBA[0, 0, 0, 1]`). See
        :ref:`Typing Ambiguity <typing-ambiguity>` in main documentation for
        more info.

    .. method:: by_n(namespace : str) -> ListRow
                by_n(namespace : str, strict : bool) -> Optional[ListRow]
                by_name(namespace : str) -> ListRow
                by_name(namespace : str, strict : bool) -> Optional[ListRow]
    .. automethod:: by_namespace

    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace

    .. rubric:: Inherited Methods

    .. method:: add(input: str) -> ListRow | list[ListRow]
    .. method:: add(input: DictWrapped | ListRow) -> ListRow
        :noindex:
    .. method:: add(input: Iterable[DictWrapped | ListRow | str]) -> list[ListRow]
        :noindex:
    .. method:: add(*input: DictWrapped | ListRow | str) -> list[ListRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.add`

    .. method:: insert(key: int, input: str) -> ListRow | list[ListRow]
    .. method:: insert(key: int, input: DictWrapped | ListRow) -> ListRow
        :noindex:
    .. method:: insert(key: int, input: Iterable[DictWrapped | ListRow | str]) -> list[ListRow]
        :noindex:
    .. method:: insert(key: int, *input: DictWrapped | ListRow | str) -> list[ListRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.insert`

    .. method:: replace(key: int | slice, input: str) -> ListRow | list[ListRow]
    .. method:: replace(key: int | slice, input: DictWrapped | ListRow) -> ListRow
        :noindex:
    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | ListRow | str]) -> list[ListRow]
        :noindex:
    .. method:: replace(key: int | slice, *input: DictWrapped | ListRow | str) -> list[ListRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.replace`

    .. method:: remove(self, key: int) -> ListRow
    .. method:: remove(self, key: slice) -> list[ListRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.remove`

    .. method:: match_pattern(row: str | ListRow | DictWrapped) -> Iterable[ListRow]

        Detailed description and examples: :meth:`abc.List.match_pattern`

    .. method:: find_by_cond(condition: callable[[ListRow], bool], strict: bool = True) -> ListRow | None

        Detailed description and examples: :meth:`abc.List.find_by_cond`

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Detailed description and examples: :meth:`abc.List.compare`

    .. automethod:: copy

    .. automethod:: inner

.. autoclass:: Object
    :show-inheritance:

    .. attribute:: type
        :type: str | None
        :value: None

        Stores object's type (for :code:ndf:`TObject( /*...*/ )` it's `type`
        will be equal to ``TObject``). See :ref:`Typing Ambiguity
        <typing-ambiguity>` in main documentation for more info.

    .. method:: by_n(namespace : str) -> MemberRow
                by_n(namespace : str, strict : bool) -> Optional[MemberRow]
                by_name(namespace : str) -> MemberRow
                by_name(namespace : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_namespace

    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace

    .. method:: by_m(member : str) -> MemberRow
                by_m(member : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_member

    .. method:: rm_m(member : str)
    .. automethod:: remove_by_member

    .. rubric:: Inherited Methods

    .. method:: add(input: str) -> MemberRow | list[MemberRow]
    .. method:: add(input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: add(input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: add(*input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.add`

    .. method:: insert(key: int, input: str) -> MemberRow | list[MemberRow]
    .. method:: insert(key: int, input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: insert(key: int, input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: insert(key: int, *input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.insert`

    .. method:: replace(key: int | slice, input: str) -> MemberRow | list[MemberRow]
    .. method:: replace(key: int | slice, input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: replace(key: int | slice, *input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.replace`

    .. method:: remove(self, key: int) -> MemberRow
    .. method:: remove(self, key: slice) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.remove`

    .. method:: match_pattern(row: str | MemberRow | DictWrapped) -> Iterable[MemberRow]

        Detailed description and examples: :meth:`abc.List.match_pattern`

    .. method:: find_by_cond(condition: callable[[MemberRow], bool], strict: bool = True) -> MemberRow | None

        Detailed description and examples: :meth:`abc.List.find_by_cond`

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Detailed description and examples: :meth:`abc.List.compare`

    .. automethod:: copy

    .. automethod:: inner

.. autoclass:: Template
    :show-inheritance:

    .. method:: by_n(namespace : str) -> MemberRow
                by_n(namespace : str, strict : bool) -> Optional[MemberRow]
                by_name(namespace : str) -> MemberRow
                by_name(namespace : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_namespace

    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace

    .. method:: by_m(member : str) -> MemberRow
                by_m(member : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_member

    .. method:: rm_m(member : str)
    .. automethod:: remove_by_member

    .. rubric:: Inherited Methods

    .. method:: add(input: str) -> MemberRow | list[MemberRow]
    .. method:: add(input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: add(input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: add(*input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.add`

    .. method:: insert(key: int, input: str) -> MemberRow | list[MemberRow]
    .. method:: insert(key: int, input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: insert(key: int, input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: insert(key: int, *input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.insert`

    .. method:: replace(key: int | slice, input: str) -> MemberRow | list[MemberRow]
    .. method:: replace(key: int | slice, input: DictWrapped | MemberRow) -> MemberRow
        :noindex:
    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | MemberRow | str]) -> list[MemberRow]
        :noindex:
    .. method:: replace(key: int | slice, *input: DictWrapped | MemberRow | str) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.replace`

    .. method:: remove(self, key: int) -> MemberRow
    .. method:: remove(self, key: slice) -> list[MemberRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.remove`

    .. method:: match_pattern(row: str | MemberRow | DictWrapped) -> Iterable[MemberRow]

        Detailed description and examples: :meth:`abc.List.match_pattern`

    .. method:: find_by_cond(condition: callable[[MemberRow], bool], strict: bool = True) -> MemberRow | None

        Detailed description and examples: :meth:`abc.List.find_by_cond`

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Detailed description and examples: :meth:`abc.List.compare`

    .. automethod:: copy

    .. automethod:: inner

.. autoclass:: Params
    :show-inheritance:

    .. attribute:: type
        :type: str | None
        :value: None

        Stores object's type (for :code:ndf:`TObject( /*...*/ )` it's `type`
        will be equal to ``TObject``). See :ref:`Typing Ambiguity
        <typing-ambiguity>` in main documentation for more info.

    .. attribute:: params
        :type: Params
        :value: Params()

        Attribute that holds template parameters.

    .. method:: by_p(self, param: str) -> ParamRow
                by_p(self, param: str, strict : bool) -> Optional[ParamRow]
    .. automethod:: by_param

    .. method:: rm_p(param : str)
    .. automethod:: remove_by_param

    .. rubric:: Inherited Methods

    .. method:: add(input: str) -> ParamRow | list[ParamRow]
    .. method:: add(input: DictWrapped | ParamRow) -> ParamRow
        :noindex:
    .. method:: add(input: Iterable[DictWrapped | ParamRow | str]) -> list[ParamRow]
        :noindex:
    .. method:: add(*input: DictWrapped | ParamRow | str) -> list[ParamRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.add`

    .. method:: insert(key: int, input: str) -> ParamRow | list[ParamRow]
    .. method:: insert(key: int, input: DictWrapped | ParamRow) -> ParamRow
        :noindex:
    .. method:: insert(key: int, input: Iterable[DictWrapped | ParamRow | str]) -> list[ParamRow]
        :noindex:
    .. method:: insert(key: int, *input: DictWrapped | ParamRow | str) -> list[ParamRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.insert`

    .. method:: replace(key: int | slice, input: str) -> ParamRow | list[ParamRow]
    .. method:: replace(key: int | slice, input: DictWrapped | ParamRow) -> ParamRow
        :noindex:
    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | ParamRow | str]) -> list[ParamRow]
        :noindex:
    .. method:: replace(key: int | slice, *input: DictWrapped | ParamRow | str) -> list[ParamRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.replace`

    .. method:: remove(self, key: int) -> ParamRow
    .. method:: remove(self, key: slice) -> list[ParamRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.remove`

    .. method:: match_pattern(row: str | ParamRow | DictWrapped) -> Iterable[ParamRow]

        Detailed description and examples: :meth:`abc.List.match_pattern`

    .. method:: find_by_cond(condition: callable[[ParamRow], bool], strict: bool = True) -> ParamRow | None

        Detailed description and examples: :meth:`abc.List.find_by_cond`

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Detailed description and examples: :meth:`abc.List.compare`

    .. automethod:: copy

    .. automethod:: inner

.. autoclass:: Map
    :show-inheritance:

    .. method:: by_k(self, key: str) -> MapRow
                by_k(self, key: str, strict : bool) -> Optional[MapRow]
    .. automethod:: by_key

    .. method:: rm_k(key : str)
    .. automethod:: remove_by_key

    .. rubric:: Inherited Methods

    .. method:: add(input: str) -> MapRow | list[MapRow]
    .. method:: add(input: DictWrapped | MapRow | Pair) -> MapRow
        :noindex:
    .. method:: add(input: Iterable[DictWrapped | MapRow | str | Pair]) -> list[MapRow]
        :noindex:
    .. method:: add(*input: DictWrapped | MapRow | str | Pair) -> list[MapRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.add`

        .. note:: Also accepts :data:`~abc.Pair` as an input.

    .. method:: insert(key: int, input: str) -> MapRow | list[MapRow]
    .. method:: insert(key: int, input: DictWrapped | MapRow | Pair) -> MapRow
        :noindex:
    .. method:: insert(key: int, input: Iterable[DictWrapped | MapRow | str | Pair]) -> list[MapRow]
        :noindex:
    .. method:: insert(key: int, *input: DictWrapped | MapRow | str | Pair) -> list[MapRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.insert`

        .. note:: Also accepts :data:`~abc.Pair` as an input.

    .. method:: replace(key: int | slice, input: str) -> MapRow | list[MapRow]
    .. method:: replace(key: int | slice, input: DictWrapped | MapRow | Pair) -> MapRow
        :noindex:
    .. method:: replace(key: int | slice, input: Iterable[DictWrapped | MapRow | str | Pair]) -> list[MapRow]
        :noindex:
    .. method:: replace(key: int | slice, *input: DictWrapped | MapRow | str | Pair) -> list[MapRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.replace`

        .. note:: Also accepts :data:`~abc.Pair` as an input.

    .. method:: remove(self, key: int) -> MapRow
    .. method:: remove(self, key: slice) -> list[MapRow]
        :noindex:

        Detailed description and examples: :meth:`abc.List.remove`

    .. method:: match_pattern(row: str | MapRow | DictWrapped) -> Iterable[MapRow]

        Detailed description and examples: :meth:`abc.List.match_pattern`

    .. method:: find_by_cond(condition: callable[[MapRow], bool], strict: bool = True) -> MapRow | None

        Detailed description and examples: :meth:`abc.List.find_by_cond`

    .. method:: compare(other: object, existing_only: bool = True) -> bool

        Detailed description and examples: :meth:`abc.List.compare`

    .. automethod:: copy

    .. automethod:: inner