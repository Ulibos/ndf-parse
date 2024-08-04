"""This module contains abstract classes used as a foundation for (almost) all
ndf-related structures. Main building blocks are :class:`List` and :class:`Row`.
List is a list-like structure (but does not inherit directly from :class:`list`
for ease of distinguishing one from the other in checks) that holds Rows of an
appropriate subtype. Actual concrete classes perform only minor overrides and
add aliases for convenience and brevity.
"""

import sys
import copy
import tree_sitter as ts
import typing as t
import pprint

from .. import converter

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def is_pair(arg: t.Any) -> bool:
    """is_pair(arg) -> bool
    Checks if given item is a tulpe with 2 items inside.

    >>> from ndf_parse.model.abc import is_pair
    >>> is_pair(("key", 12))
    True
    >>> is_pair(("key", 12, 'EXTRA'))
    False
    >>> is_pair(["key", 12])
    False

    """
    return isinstance(arg, tuple) and len(arg) == 2  # type: ignore


# ============================== TYPES =================================
ArgsNamesFlat = t.Tuple[str, ...]
ArgsNames = t.Tuple[t.Tuple[str, ...], ...]
ItemKey = t.Union[slice, t.SupportsIndex, t.Iterable[t.SupportsIndex]]

#: Generic Row
GR = t.TypeVar("GR", bound="Row", covariant=True)
# Pair = t.Tuple["CellValue", "CellValue"]
CellValue = t.Union["List[Row]", str]  # , Pair]
OptCellValue = t.Optional[CellValue]
DictWrapped = t.Mapping[str, OptCellValue]
RowInput = t.Union[str, DictWrapped, GR]
AllRowInputs = t.Union[RowInput[GR], t.Iterable[RowInput[GR]]]


# ============================= CLASSES ================================


class Row:
    """Row(*args, **kwargs, _strict: bool = True)
    An abstract class for rows of data in list-like structures of the model.

    It serves as a foundation for any classes that are meant to store assigned
    items along with any related metadata (variable names, visibility modifiers,
    mapping keys etc.)

    When printing out (via standard :func:`print`, not
    :func:`ndf_parse.printer.print`), a row gets printed as it's class name
    followed by it's index in the parent object. If row is not parented then
    it will have ``[DANGLING]`` instead of an index. Examples:

    >>> from ndf_parse.model import Map, MapRow
    >>> row = MapRow("'key'", "12")
    >>> row
    MapRow[DANGLING](key="'key'", value='12')
    >>> m = Map()
    >>> m.add(row)
    MapRow[0](key="'key'", value='12')

    """

    # Ordering of `_args_names` is important! It must correspond to what we
    # expect to get in `__init__()`, starting from mandatory arguments.
    _args_names: ArgsNames
    _args_names_flat: ArgsNamesFlat
    _args_required: ArgsNamesFlat
    _parent: t.Optional["List[Self]"]
    _entries_parser: t.Callable[[str], t.List[ts.Node]]

    def __init__(self, *args: OptCellValue, **kwargs: OptCellValue) -> None:
        self._parent = None
        for aliases in self._args_names:
            object.__setattr__(self, aliases[0], None)
        self.__edit("()", "initialized", args, kwargs)

    @property
    def index(self) -> t.Optional[int]:
        """*(readonly)* – Returns an index of this row in it's parent or
        ``None`` if dangling.

        Raises
        ------
        LookupError
            Errors out if has a parent but was not found in it (this should
            never happen unless there is a serious bug in parent/unparent
            routines or it was manually deleted from ``List.__inner``).
        """
        if self.parent is not None:
            for i, other in enumerate(self.parent):
                if id(self) == id(other):
                    return i
            raise LookupError(
                f"{self.__class__.__name__} is marked as parented to a list "
                "but is not found in the list."
            )

    @property
    def parent(self) -> t.Optional["List[Self]"]:
        """*(readonly)* – A List-like object to which this row belongs."""
        return self._parent

    def copy(self) -> Self:
        """Performs a deep copy of a row. It's an alias to a
        :meth:`__deepcopy__` method (shallow copying :ref:`is disabled
        intentionally <no-referencing>`).
        """
        return self.__deepcopy__({})

    def edit(self, *args: OptCellValue, **kwargs: OptCellValue) -> Self:
        """edit(_strict = True, **kwargs) -> self
        Edit current row with multiple values (except `parent` and `index`).

        This method allows to edit a bunch of values in the row at once. It also
        accepts properties' aliases or a dict of keys corresponding to Row's
        properties/aliases (such as an output of :func:`ndf_parse.expression`).

        Note
        ----
        You cannot pass mutually exclusive keys at once, for example, you cannot
        pass ``namespace=...`` along with ``n=...`` to a :meth:`ListRow.edit()
        <ndf_parse.model.ListRow.edit>`, it will raise an error.

        Parameters
        ----------
        kwargs : :data:`CellValue` | None
            Properties to edit.
        _strict : bool, default=True
            If set to ``True`` and kwargs contain a key that doesn't match any
            properties of this row then it will fail. If ``False`` then it will
            silently skip it.
            :ref:`More on why this exists <strict-attributes>`.

        Returns
        -------
        self

        Raises
        ------
        TypeError
            Errors out if gets repeating/clashing arguments/aliases or if in
            strict mode and got unrecognized arguments.
        """
        return self.__edit(".edit()", "edited", args, kwargs)

    def edit_ndf(self, code: str) -> Self:
        """edit_ndf(code) -> self
        Edit a row using ndf code. The code should contain an expression
        representing a single object of the same type as the row is, i.e. for
        :class:`ListRow <ndf_parse.model.ListRow>` it would look like this:

        .. doctest::

            >>> from ndf_parse.model import ListRow
            >>> row = ListRow(value="12")
            >>> row.edit_ndf("export NewName is 24")
            ListRow[DANGLING](value='24', visibility='export', namespace='NewName')
            >>> # If a value can be skipped it will remain unedited.
            >>> # Main drawback is you can't ignore mandatory values for a
            >>> # specific sublass of Row.
            >>> row.edit_ndf("NewValue is 12")
            ListRow[DANGLING](value='12', visibility='export', namespace='NewValue')
            >>> # note that 'export' didn't change

        Parameters
        ----------
        code : str
            Ndf code.

        Returns
        -------
        self

        Raises
        ------
        ValueError
            Errors out in case the ndf code contains more than one object.
        """
        entries = self.__class__._entries_parser(code)
        if len(entries) != 1:
            raise ValueError(
                "edit(code) expects exactly one statement to be present in the "
                f"ndf code, got {len(entries)}."
            )
        return self.__edit_dict(**converter.find_converter(entries[0]))

    @classmethod
    def from_ndf(cls, code: str) -> Self:
        """from_ndf(code) -> Self
        Create a row from an ndf code. The code must contain only one item
        corresponding to this row's class. Example:

        >>> from ndf_parse.model import ListRow
        >>> ListRow.from_ndf("export Value is 12")
        ListRow[DANGLING](value='12', visibility='export', namespace='Value')

        Parameters
        ----------
        code : str
            An ndf code representing a single row.

        Returns
        -------
        Self
            A new row.

        Raises
        ------
        ValueError
            Errors out in case ndf code contains more than one object.
        """
        result = cls.__new__(cls)
        result._parent = None
        for attr in (a[0] for a in cls._args_names):
            setattr(result, attr, None)
        result.edit_ndf(code)
        result.__ensure_requried("cannot be initialized to None.")
        return result

    def as_dict(self) -> t.Dict[str, CellValue]:
        """as_dict() -> dict
        Outputs given row in a form of a dict.

        Note
        ----
        It does not perform copy for it's `value`. If you edit `value` key in
        the dict, it will be also edited in the original row (they literally
        point to the same object in memory). Creating a new row from such dict
        via decomposition (:code:py:`new_row = model.ListRow(
        **old_row.as_dict() )`) is fine as long as source is parented to
        something. If it is a dangling row then you WILL get 2 rows referencing
        the same data in memory (because of specific optimizations aimed at
        avoiding excessive data copying on row moves) and will have unexpected
        side effects! Copying using :meth:`Row.copy` is recommended in most
        cases. It's easier and guarantees no such side effects.

        :ref:`See notes on copying here. <no-referencing>`

        Returns
        -------
        dict[str, CellValue]
        """
        return {k: getattr(self, k) for k in self.full_args_names()}

    def full_args_names(self) -> t.Iterable[str]:
        return (x[0] for x in self._args_names)

    def compare(self, other: object, existing_only: bool = True) -> bool:
        r"""Compares 2 items. If `existing_only` is ``True`` (the default) then
        it acts as a pattern matcher, i.e. it compares only with existing rows
        in the second object, allowing to filter out objects with specific
        values. If `existing_only` is ``False`` then acts as `__eq__()`.
        Examples:

        >>> from ndf_parse.model import ListRow
        >>> original_row = ListRow.from_ndf("NewMember is Obj(inner_member = 12\n extra=5)")
        >>> strict_match = ListRow.from_ndf("NewMember is Obj(inner_member = 12\n extra=5)")
        >>> will_fail_01 = ListRow.from_ndf("Renamed is Obj(inner_member = 12\n extra=5)")
        >>> will_fail_02 = ListRow.from_ndf("NewMember is Obj(inner_member = 44\n extra=5)")
        >>> #                                                       44 != 12 ^^
        >>> pattern_01 = ListRow.from_ndf("NewMember is Obj()")
        >>> pattern_02 = ListRow.from_ndf("NewMember is Obj(inner_member = 12)")
        >>> # strict compare example (`existing_only` is ``False``)
        >>> original_row.compare(strict_match, existing_only=False)
        True
        >>> original_row.compare(will_fail_01, existing_only=False)
        False
        >>> original_row.compare(will_fail_02, existing_only=False)
        False
        >>> # pattern compare(`existing_only` is ``True``)
        >>> original_row.compare(pattern_01)
        True
        >>> original_row.compare(pattern_02)
        True

        Note
        ----
        Be careful when :ref:`comparing strings <comparing-strings>`
        from ndf code. Embedded quotes must match.

        Parameters
        ----------
        other : Self | dict
            object to compare against or to use as a pattern.
        existing_only : bool, default=True
            Controls comparison mode between full comparison and pattern
            matching (default mode).

        Returns
        -------
        bool
            If items match or not.
        """
        getter: t.Callable[[t.Any], t.Any]
        attrs_list: t.Dict[str, str]
        # prep iterators to compare cells
        if isinstance(other, Row):
            _all_attrs = set(self.full_args_names())
            _all_attrs |= set(other.full_args_names())
            attrs_list = {a: a for a in _all_attrs}
            getter = lambda k: getattr(other, k, None)
        else:
            if isinstance(other, t.Mapping):
                other = t.cast(t.Mapping[str, t.Any], other)
                pass
            elif hasattr(other, "__dict__"):
                other = other.__dict__
            else:
                return False
            attrs_list = self._map_args(other.keys())
            getter = lambda k: other.get(k, None)
        # compare cells
        if existing_only:
            for ks, ko in attrs_list.items():
                vs = getattr(self, ks, None)
                vo = getter(ko)
                if vo is None:
                    # partial compare, skip non-existant fields from template
                    continue
                elif isinstance(vs, List):
                    if not vs._compare(vo):  # type: ignore
                        # compare template against original because original most
                        # likely has more rows, this way will be more optimal
                        return False
                elif isinstance(vo, List):
                    if not vo._compare(vs):  # type: ignore
                        return False
                elif vs != vo:
                    return False
        else:
            for ks, ko in attrs_list.items():
                if getattr(self, ks, None) != getter(ko):
                    return False
        return True

    # ================ DUNDER METHODS
    def __index__(self) -> int:
        """Method for ``int(Self)``."""
        result = self.index
        if result is None:
            raise ValueError(
                f"Attempt to index a dangling row: {self.__class__.__name__}"
            )
        return result

    def __repr__(self) -> str:
        args = (
            f"{k}={repr(getattr(self, k))}" for k in self.full_args_names()
        )
        parent = f"{self.index}" if self.parent is not None else "DANGLING"
        return f"{self.__class__.__name__}[{parent}]({', '.join(args)})"

    def __copy__(self) -> Self:
        return self.__deepcopy__({})

    def __deepcopy__(self, memo: t.Dict[int, t.Any]) -> Self:
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        new._parent = None
        args = {k: copy.deepcopy(v, memo) for k, v in self.as_dict().items()}
        new.__init__(**args)
        return new

    def __eq__(self, other: object) -> bool:
        return self.compare(other, False)

    def __setattr__(self, name: str, value: object):
        """Auto parenting and alias remepping to actual properties are
        implemented here.
        """
        if name not in self._args_names_flat:
            object.__setattr__(self, name, value)
            return
        for aliases in self._args_names:
            if name in aliases:
                # deal with parenting incoming
                if isinstance(value, List):
                    value = t.cast(List[Row], value)
                    if value.parent is not None and value._parent != self:  # type: ignore
                        value = value.copy()
                    value._parent = self  # type: ignore
                # deal with parenting outgoing
                old_value = getattr(self, aliases[0], None)
                if isinstance(old_value, List):
                    old_value._parent = None  # type: ignore
                # set the attribute
                object.__setattr__(self, aliases[0], value)
                return

    def __getattribute__(self, name: str) -> t.Any:
        """Getters for aliases are based on this dunder method."""
        for aliases in object.__getattribute__(self, "_args_names"):
            if name in aliases:
                return object.__getattribute__(self, aliases[0])
        return object.__getattribute__(self, name)

    # ================ UTILS

    def __edit(
        self,
        fn_name: str,
        op_name: str,
        args: t.Tuple[OptCellValue, ...],
        kwargs: t.Dict[str, OptCellValue],
    ) -> Self:
        """Main editing method. Accepts preprocessed arguments along with info
        about a method from which it was called and performs an edit of the row.

        Parameters
        ----------
        fn_name : str
            Which method it was called from. Used in error messages formatting.
        op_name : str
            Human-readable name of the operation. Used in error messages
            formatting.
        args : tuple[OptCellValue, ...]
            Positional arguments.
        kwargs : dict[str, OptCellValue]
            Named arguments.

        Returns
        -------
        Self

        Raises
        ------
        TypeError
            Errors out if `kwargs` repeats existing positional arguments.
        """
        cls_name = self.__class__.__name__
        clashing_names = self._merge_kwargs(args, kwargs)
        if clashing_names is not None:
            raise TypeError(
                f"{cls_name}{fn_name} got repeating arguments: "
                f"{', '.join(clashing_names)}"
            )
        _strict = kwargs.pop("_strict", True)
        self.__edit_dict(_strict=_strict, **kwargs)  # type: ignore
        self.__ensure_requried(f"cannot be {op_name} to None.")
        return self

    def __edit_dict(
        self, _strict: bool = True, **kwargs: OptCellValue
    ) -> Self:
        if "parent" in kwargs and _strict:
            raise TypeError(
                "Cannot pass a parent as an argument. To set a parent, add "
                "this row to a List via List.add(), List.insert() etc."
            )
        self._verify_kwargs(kwargs, _strict)
        for k, v in self._iterate_args(kwargs):
            setattr(self, k, v)
        return self

    def __ensure_requried(self, msg: str):
        for k in self._args_required:
            if getattr(self, k) is None:
                raise ValueError(f"{self.__class__.__name__}.{k} {msg}")

    def _try_promote_to_full_args(
        self, args: t.Iterable[str]
    ) -> t.Iterable[str]:
        """Converts aliases to full names, preserves unfamiliar args as
        is."""
        for arg in args:
            if not arg in self._args_names_flat:
                yield arg
                continue
            for self_args in self._args_names:
                if arg in self_args:
                    yield self_args[0]
                    continue

    def _map_args(self, attrs: t.Iterable[str]) -> t.Dict[str, str]:
        """Builds a 1-to-1 map of arguments. Matching ones or their
        aliases will be paired with each other. Keys are meant to be
        attr names for the `self`, values - for the other object.
        Example:

        1. We have a Row with attrs:
           ('visibility', 'namespace', 'value')
        2. We have the followung `attrs` argument:
           ('vis', 'namespace', 'status')

        The function will return a dict:
        {'visibility':'vis', 'namespace':'namespace',
          'value':'value', 'status':'status'
        }
        'namespace' and 'visibility' will be matched, 'value' will be
        taken from the Row, 'status' will be taken from the argument.
        """
        attrs_list = {k: k for k in self.full_args_names()}
        for k, v in zip(self._try_promote_to_full_args(attrs), attrs):
            attrs_list[k] = v
        return attrs_list

    @classmethod
    def _merge_kwargs(
        cls,
        args: t.Tuple[OptCellValue, ...],
        kwargs: t.Dict[str, OptCellValue],
    ) -> t.Optional[t.Set[str]]:
        """Merges positional `args` into `kwargs` for ease of further
        processing. Errors out if there are too many positional arguments.
        """
        cls_name = cls.__name__
        len_diff = len(args) - len(cls._args_names)
        if len_diff > 0:
            raise TypeError(
                f"{cls_name} expected {len(cls._args_names)} args but "
                f"got {len(args)}."
            )
        mapped_kwargs = {
            k: v for k, v in zip((x[0] for x in cls._args_names), args)
        }
        clashing_keys = set(mapped_kwargs) & set(kwargs)
        if len(clashing_keys):
            return clashing_keys
        else:
            kwargs.update(mapped_kwargs)

    def _verify_kwargs(self, kwargs: DictWrapped, strict: bool = True):
        """Verifies that there are no clashing args names. Errors out if some
        key and it's alias are present together. Errors out if strict mode is
        on and there are unrecognized keys.
        """
        if strict:
            for k in kwargs:
                if not k in self._args_names_flat:
                    raise TypeError(
                        f"Cannot set {self.__class__.__name__}.{k}, attribute "
                        "does not exist."
                    )
                v = kwargs[k]
                if isinstance(v, (str, List)):
                    continue
                elif is_pair(v):
                    continue
                elif v is None:
                    continue
                raise TypeError(
                    "Row's fields expect value of types str | List | Row | "
                    f"tuple[2], got {type(v).__name__}."
                )
        for args in self._args_names:
            num_collisions = 0
            for arg in args:
                num_collisions += arg in kwargs
                if num_collisions > 1:
                    raise TypeError(
                        "Can't use multiple mutually exclusive args: "
                        f"{', '.join(repr(x) for x in args)}."
                    )

    def _iterate_args(
        self, kwargs: DictWrapped
    ) -> t.Iterator[t.Tuple[str, OptCellValue]]:
        """Iterates kwargs while substituting aliases for their full names.
        Does not sanitize inputs by itself, use ``self._verify_kwargs()`` for
        that.
        """
        for k, v in kwargs.items():
            for aliases in self._args_names:
                if k in aliases:
                    yield (aliases[0], v)  # use original parameter name
                    break


class List(t.Sequence[GR]):
    """List()
    An abstract class for list-likes of the model.

    It serves as a foundation for any classes that are meant to store repeating
    structures of data (rows as they are called in this package). In many
    respects it acts as a :class:`list` but does not inherit from it because
    some APIs differ a bit plus it helps to filter one against the other in type
    checks.

    This class implements basic attribute getters and setters along with named
    methods for same actions but with return values and more explicit usage:

    ====================================== ====================================
    Pythonic way                            Explicit methods
    ====================================== ====================================
    :code:py:`lst[i] = "ndf code"`         :code:py:`lst.replace(i, "ndf code")`
    :code:py:`lst[i:j] = "ndf code"`       :code:py:`lst.replace(slice(i, j), "ndf code")`
    :code:py:`lst[i:i] = "nbf code"`       :code:py:`lst.insert(i, "ndf_code")`
    :code:py:`lst[len(lst):] = "ndf code"` :code:py:`lst.add("ndf_code")`
    :code:py:`del lst[i]`                  :code:py:`lst.remove(i)`
    :code:py:`del lst[i:j]`                :code:py:`lst.remove(slice(i, j))`
    ====================================== ====================================

    Explicit methods are advised in most cases because they are - well -
    explicit, have a return value and allow for :ref:`strictness manipulation
    <strict-attributes>`, while pythonic ones are in strict mode by default. But
    you can use pythonic ones for brevity, just be aware of these nuances.

    Some examples of pythonic setters:

    >>> from ndf_parse.model import List, ListRow
    >>> lst = List()
    >>> row = ListRow(namespace="Name", value="12")
    >>> lst[:] = row  # replace all (but list is empty so just insert)
    >>> lst[0:0] = "Before is 24"  # insert at index 0, string is treated as ndf
    >>> lst[2:2] = "After is 42, After2 is 69"  # can also insert multiple
    >>> lst
    List[ListRow[0](value='24', visibility=None, namespace='Before'),
    ListRow[1](value='42', visibility=None, namespace='After'),
    ListRow[2](value='69', visibility=None, namespace='After2')]
    >>> lst[1] = "Replace is 25"  # replace a given row
    >>> del lst[2]  # delete last row
    >>> lst
    List[ListRow[0](value='24', visibility=None, namespace='Before'),
    ListRow[1](value='25', visibility=None, namespace='Replace')]

    List supports the following operations over sequences:

    >>> len(lst)  # get it's length
    2
    >>> for row in lst:  # iterate over a List
    ...     print(row.v)
    24
    25
    >>> for row in reversed(lst):  # iterate over a reversed list
    ...     print(row.v)
    25
    24
    >>> lst == "Before is 24, Replace is 25"  # compare with an iterable
    True

    Warning
    -------
    For the moment :class:`abc.List <List>` does not implement all methods From
    :class:`~collections.abc.Sequence`. :meth:`~list.index` is not implemented
    because each row has such property itself and :meth:`~list.count` is not
    implemented because there is no much use for it with current implementation.
    """

    @property
    def parent(self) -> t.Optional["List[Row]"]:
        """**(readonly)** A parent list to which this list belongs. Example:

        .. code-block:: C

            BigList is ListOfObjs(
                first_obj = FirstObj("I'm first")
            )

        Getting ``parent`` for `FirstObj` would return `ListOfObjs`, not the row
        it's stored in.
        """
        if self._parent is not None:
            return self._parent.parent

    @property
    def parent_row(self) -> t.Optional[Row]:
        """**(readonly)** A row to which this list belongs. In the example above
        getting ``parent_row`` for `FirstObj` would not return the `ListOfObjs`
        but a ``MemberRow[0](value=Object[...], member='first_obj', ... )``
        where `value` is the `FirstObj`.
        """
        if self._parent is not None:
            return self._parent

    _row_type: t.Type[GR]

    def __init__(self) -> None:
        self.__inner: t.List[GR] = []
        self._parent: t.Optional[Row] = None

    def inner(self) -> t.List[GR]:
        """inner() -> list[GR]
        Returns internal list containing all rows.

        Warning
        -------
        Insertions and edits on
        this list do not perform any checks nor reparentings on rows. It is
        completely possible to reference the same row twice or make a recursive
        structure. 99% of the time you shouldn't access this list.

        Returns
        -------
            list[GR]
        """
        return self.__inner

    def copy(self) -> Self:
        """Performs a deep copy of a list. It's an alias to a
        :meth:`__deepcopy__` method (shallow copying :ref:`is disabled
        intentionally <no-referencing>`).
        """
        return self.__deepcopy__({})

    def compare(self, other: object, existing_only: bool = True) -> bool:
        r"""Compare a List against another iterable (except `str` and `bytes`).
        If `existing_only` is True then seek a 1-to-1 match. Else `other` acts
        as a pattern that must be present inside the List being compared.

        >>> from ndf_parse.model import List, ListRow
        >>> lit = List()
        >>> lit[:] = "Value is 12, Other is 24, Nested is Obj(the_one = 42\n unneeded = 'whatever')"
        >>> # strict compare
        >>> # `compare()` accepts list-likes, lists or rows and strings as code
        >>> lit.compare("Value is 12, Other is 24", existing_only = False)
        False
        >>> # pattern compare
        >>> lit.compare("Value is 12, Other is 24")
        True
        >>> # we can even compare mested patterns
        >>> lit.compare([ListRow.from_ndf("Nested is Obj(the_one = 42)")])
        True

        Parameters
        ----------
        other : object
            Object to compare against or to use as a pattern.
        existing_only : bool, default=True
            Controls comparison mode between full comparison and pattern
            matching (default mode).

        Returns
        -------
        bool
            If items match or not.
        """
        if isinstance(other, str):
            new = self.__class__()
            new.add(other)
            other = new
        return self._compare(other, existing_only)

    def _compare(self, other: object, existing_only: bool = True) -> bool:
        if not hasattr(other, "__iter__") and hasattr(other, "__len__"):
            return False
        if isinstance(other, (str, bytes)):
            return False
        other = t.cast(t.Collection[t.Any], other)
        if not existing_only:
            if len(self.__inner) != len(other):
                return False
            for rs, ro in zip(self.__inner, other):
                if rs != ro:
                    return False
            return True
        else:  # existing_only
            for row in other:
                if not self.__pattern_present__(row):
                    return False
            return True

    def match_pattern(self, row: RowInput[GR]) -> t.Iterable[GR]:
        r"""match_pattern(row: str | GR | DictWrapped) -> Iterable[GR]
        Return each row that matches a given pattern.

        >>> import ndf_parse as ndf
        >>> lst = ndf.model.List()
        >>> lst.add("A is Weapon(name='Steur AUG'\n caliber = 5.56), \
        ... B is Weapon(name='FN SCAR-H'\n caliber = 7.62), \
        ... C is Weapon(name='M16'\n caliber = 5.56), \
        ... D is Weapon(name='Steur Scout'\n caliber = 7.62), \
        ... E is Weapon(name='AK-108'\n caliber = 5.56)")
        [ListRow[0](...)]
        >>> for row in lst.match_pattern("Weapon(caliber = 5.56)"): ndf.printer.print(row)
        A is Weapon
        (
            name = 'Steur AUG'
            caliber = 5.56
        )
        C is Weapon
        (
            name = 'M16'
            caliber = 5.56
        )
        E is Weapon
        (
            name = 'AK-108'
            caliber = 5.56
        )

        Parameters
        ----------
        row : str | GR | DictWrapped
            A pattern to match against. Can be a row, a dict, a string with ndf
            code.

        Yields
        ------
        GR
            Rows from this List that match the pattern.

        Raises
        ------
        TypeError
            Errors out if got multiple patterns to match against.
        """
        _iter = iter(r for r in self.__yield_rows__(row))
        _, match_item = next(_iter)
        try:
            next(_iter)
        except StopIteration:
            pass
        else:
            raise TypeError(
                "Cannot match against multiple rows, provide a single "
                "template row to match against"
            )
        for r in self.__inner:
            if r.compare(match_item):
                yield r

    @t.overload
    def find_by_cond(self, condition: t.Callable[[GR], bool]) -> GR: ...
    @t.overload
    def find_by_cond(
        self, condition: t.Callable[[GR], bool], strict: t.Literal[True]
    ) -> GR: ...
    @t.overload
    def find_by_cond(
        self, condition: t.Callable[[GR], bool], strict: bool = True
    ) -> t.Optional[GR]: ...
    def find_by_cond(
        self, condition: t.Callable[[GR], bool], strict: bool = True
    ) -> t.Optional[GR]:
        r"""Find a row by a condition. The condition is a function that returns
        ``True`` if a row satisfies all requirements. Always returns the first
        row that matches.

        Examples
        --------

            >>> import ndf_parse as ndf
            >>> scene = ndf.convert("A is 12\nB is 24\nC is 24\nC is 42")  # note 2 values `24`
            >>> scene.find_by_cond(lambda x: x.v == '24')
            ListRow[1](value='24', visibility=None, namespace='B')
            >>> # first row matching the condition was returned

        This example is intentionally simple, but this method has it's use like
        catching a descriptor of specific type in a list of descriptors with no
        namespaces (Unit's module descriptors are a good example).

        Parameters
        ----------
        condition : callable[[GR], bool]
            A function or a lambda that checks each row.

        strict : bool, default=True
            If strict and now row found then raises an error. Else returns
            ``None``.

        Raises
        ------
        TypeError
            Errors out if in strict mode and no matching row as found.
        """
        for row in self.__inner:
            if condition(row):
                return row
        if strict:
            raise TypeError("No rows match given condition.")

    # ================ add()
    @t.overload
    def add(self, input: str) -> t.Union[t.List[GR], GR]: ...  # type: ignore
    @t.overload
    def add(self, input: t.Union[DictWrapped, GR]) -> GR: ...
    @t.overload
    def add(self, *input: AllRowInputs[GR]) -> t.List[GR]: ...
    def add(
        self, *input: AllRowInputs[GR], **kwargs: OptCellValue
    ) -> t.Union[t.List[GR], GR]:
        """Add a row/rows to the end of the list. Supports multiple inputs: ndf
        code as a str, a row, a dict representation of a row, an iterable with
        any of the above. Also supports entering keywords for row's parameters
        directly. Will return a single row for dict, kwargs, single row. Will
        try to return a single value for a str of code. Will always return a
        list of rows if got a list-like iterable, even if it has a single row
        in it."""
        k = len(self.__inner)
        args = self._homogenize_setattr_inputs(input, kwargs, "add")
        return self.__set_rows(slice(k, k), args)

    # ================ insert()
    # fmt: off
    @t.overload
    def insert(self, key: t.SupportsIndex, input: str) -> t.Union[t.List[GR], GR]: ...  # type: ignore
    @t.overload
    def insert(self, key: t.SupportsIndex, input: t.Union[DictWrapped, GR]) -> GR: ...
    @t.overload
    def insert(self, key: t.SupportsIndex, *input: AllRowInputs[GR]) -> t.List[GR]: ...
    # fmt: on
    def insert(
        self,
        key: t.SupportsIndex,
        *input: AllRowInputs[GR],
        **kwargs: OptCellValue,
    ) -> t.Union[t.List[GR], GR]:
        """Insert a row/rows at a given index (key). Same input rules as for
        `add()`."""
        k = int(key)
        args = self._homogenize_setattr_inputs(input, kwargs, "insert")
        return self.__set_rows(slice(k, k), args)

    # ================ replace()
    # fmt: off
    @t.overload
    def replace(self, key: ItemKey, input: str) -> t.Union[t.List[GR], GR]: ...  # type: ignore
    @t.overload
    def replace(self, key: ItemKey, input: t.Union[DictWrapped, GR]) -> GR: ...
    @t.overload
    def replace(self, key: ItemKey, *input: AllRowInputs[GR]) -> t.List[GR]: ...
    # fmt: on
    def replace(
        self,
        key: ItemKey,
        *input: t.Any,
        **kwargs: OptCellValue,
    ) -> t.Union[t.List[GR], GR]:
        """Replace a row/rows at a given index/slice. Same input rules as for
        `add()`."""
        if isinstance(key, slice):
            start = key.start or 0
            stop = key.stop or len(self.__inner)
            assert (stop - start) != 0, (
                f"Attempt at using `replace()` as `insert()` with slice {key}. "
                "Use `insert()` if you want to insert or fix your slice range."
            )
        args = self._homogenize_setattr_inputs(input, kwargs, "replace")
        return self.__set_rows(key, args)

    # ================ remove()
    @t.overload
    def remove(self, key: slice) -> t.List[GR]: ...
    @t.overload
    def remove(self, key: t.SupportsIndex) -> GR: ...
    def remove(self, key: ItemKey) -> t.Union[t.List[GR], GR]:
        """Remove a row/rows at a given key/slice."""
        return self.__delitem__(key)

    # ================ DUNDER METHODS
    def __iter__(self) -> t.Iterator[GR]:
        return iter(self.__inner)

    def __reversed__(self) -> t.Iterator[GR]:
        return self.__inner.__reversed__()

    def __len__(self) -> int:
        return len(self.__inner)

    def __contains__(self, value: t.Any) -> bool:
        if not isinstance(value, self._row_type):
            return False
        return any(value is x for x in self.__inner)

    def __eq__(self, other: object) -> bool:
        return self.compare(other, False)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"[{', '.join(repr(x) for x in self.__inner)}]"
        )

    @t.overload
    def __getitem__(self, key: t.SupportsIndex) -> GR: ...
    @t.overload
    def __getitem__(
        self, key: t.Union[slice, t.Iterable[t.SupportsIndex]]
    ) -> t.List[GR]: ...
    def __getitem__(self, key: ItemKey) -> t.Union[t.List[GR], GR]:
        if isinstance(key, (t.SupportsIndex, slice)):
            return self.__inner[key]
        else:
            return [self.__inner[k] for k in key]

    def __delitem__(self, key: ItemKey) -> t.Union[t.List[GR], GR]:
        if isinstance(key, t.SupportsIndex):
            rem_one: GR = self.__inner[key]
            del self.__inner[key]
            rem_one._parent = None  # type: ignore
            return rem_one
        elif isinstance(key, slice):
            removed = self.__inner[key]
            del self.__inner[key]
        else:
            removed: t.List[GR] = []
            for k in key:
                removed.append(self.__inner[k])
                del self.__inner[k]
        for row in removed:
            row._parent = None  # type: ignore
        return removed

    def __setitem__(
        self, key: ItemKey, value: t.Any
    ) -> t.Union[t.List[GR], GR]:
        if isinstance(value, tuple):
            input: t.Tuple[t.Any, ...] = value  # type: ignore
        else:
            input = (value,)
        return self.__set_rows(key, input)  # type: ignore

    def __deepcopy__(self, memo: t.Dict[int, t.Any]) -> Self:
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        new._parent = None
        new.__inner = copy.deepcopy(self.__inner, memo)
        for row in new.__inner:
            row._parent = new  # type: ignore
        return new

    def __copy__(self) -> Self:
        return self.__deepcopy__({})

    def __pattern_present__(self, row: t.Union[Row, DictWrapped]):
        """Used in compare(). Possible place for optimizations in concrete
        classes. Generic solution implements a brute force approach.
        """
        for rs in self.__inner:
            if rs.compare(row):
                return True
        return False

    # ================ UTILS
    def _homogenize_setattr_inputs(
        self,
        args: t.Tuple[t.Any, ...],
        kwargs: t.Dict[str, t.Any],
        method_name: str,
    ) -> t.Tuple[t.Any, ...]:
        """Validates combination of args and kwargs to comply with API
        1. accept 1 arg
        2. accept tuple|list of args and no kwargs
        3. kwargs only.

        Returns tuple each item of which must be a row or be convertable
        into a row.
        """
        cls_name = self.__class__.__name__
        has_args = len(args)
        has_kwargs = len(kwargs)
        if has_args and has_kwargs:
            # case method_name(*args, **kwargs)
            raise TypeError(
                f"{cls_name}.{method_name}() expects either series of "
                f"arguments without keywords (ex. {cls_name}.{method_name}"
                '(row1, {"v":12}, "ndf code", ...)) or keywords for a single '
                f'row, (ex. {cls_name}.{method_name}(namespace="Ns", value='
                '"12", ...)). Intermixing non-keyword args and keyword '
                "args is prohibited due to ambiguity (both row values and ndf "
                "code can be represetned as strings)."
            )
        elif not has_args and not has_kwargs:
            # case method_name()
            raise TypeError(f"{cls_name}.{method_name}() got no input.")
        elif has_kwargs:
            if len(kwargs) == 1 and "input" in kwargs:
                # case method_name(input=...)
                return (kwargs["input"],)
            else:
                # case method_name(**kwargs)
                return (kwargs,)
        else:
            # case method_name(*args)
            return args

    def __yield_rows__(self, input: t.Any) -> t.Iterable[t.Tuple[bool, GR]]:
        """As input accepts any single object that is able to be converted
        to a row (by this exact function) or an iterable of such objects.

        Yields Tuple[bool, Row] where bool means 'not a freshly generated
        row'.
        """
        if isinstance(input, self._row_type):
            yield (True, input)
        elif isinstance(input, str):
            yield from ((False, x) for x in self.__from_str__(input))
        elif isinstance(input, dict):
            yield (False, self._row_type(**input))  # type: ignore
        elif isinstance(input, bytes):
            raise TypeError(
                "Expected str, got bytes. Please convert explicitly if you "
                "want to pass ndf code to the function."
            )
        else:
            raise TypeError(
                f"Got unsupported type of row: {type(input).__name__}"
            )

    def _possibly_single_return(self, arg: t.Any) -> bool:
        return isinstance(arg, (str, dict, self._row_type))

    def __set_rows(
        self, key: ItemKey, args: t.Tuple[t.Any, ...]
    ) -> t.Union[t.List[GR], GR]:
        single_output = False
        if len(args) == 1:
            arg = args[0]
            if self._possibly_single_return(arg):
                single_output = True
            else:
                # allows to do calls like insert(list[Any]) where list will be
                # iterated instead of trying to convert it to a row itself.
                args = arg
        rows_gen = (row for arg in args for row in self.__yield_rows__(arg))
        if isinstance(key, t.SupportsIndex):
            return self.__set_single_row(key, rows_gen)
        if isinstance(key, slice):
            result = self.__set_with_slice(key, rows_gen)
        elif isinstance(key, t.Iterable):  # type: ignore
            result = self.__set_with_iterable(key, rows_gen)
        else:
            raise KeyError(
                "This method expects key to be int (or convertable to int), "
                f"slice or an iterable of ints, got: {type(key).__name__}"
            )
        if len(result) == 1 and single_output:
            return result[0]
        else:
            return result

    def __set_single_row(
        self,
        key: t.SupportsIndex,
        args: t.Generator[t.Tuple[bool, GR], None, None],
    ) -> GR:
        k = int(key)
        reused, row = next(args)
        try:
            next(args)
        except StopIteration:
            pass
        else:
            cls_name = self.__class__.__name__
            raise ValueError(
                f"Cannot replace single item {cls_name}[{k}] with multiple "
                "ones. If you really want to replace one item with multiple "
                f"then index as `{cls_name}[{k}:{k+1}] = ...`"
            )
        if reused and self.__inner[k] is row:
            return row
        else:
            row = row.copy()
        old = self.__inner[k]
        self.__inner[k] = row
        old._parent = None  # type: ignore
        row._parent = self  # type: ignore
        return row

    def __set_with_slice(
        self,
        key: slice,
        args: t.Generator[t.Tuple[bool, GR], None, None],
    ) -> t.List[GR]:
        start = key.start or 0
        stop = key.stop or len(self.__inner)
        step = key.step or 1
        rows: t.List[GR] = []
        if start != stop:
            # make copies for any rows that are to be reused except for ones
            # that replace themselves
            indices = range(start, stop, step)
            for idx, (reused, row) in zip(indices, args):
                if (
                    reused
                    and row is not self.__inner[idx]
                    and row.parent is not None
                ):
                    row = row.copy()
                rows.append(row)
        # make copies for any rows that are to be reused and exhaust generator
        # till the end after previous block
        for reused, row in args:
            if reused and row.parent is not None:
                row = row.copy()
            rows.append(row)
        # insert/replace and reparent on success
        old = self.__inner[start:stop:step]
        self.__inner[start:stop:step] = rows
        for r in old:
            r._parent = None  # type: ignore
        for r in rows:
            r._parent = self  # type: ignore
        return rows

    def __set_with_iterable(
        self,
        key: t.Iterable[t.SupportsIndex],
        args: t.Generator[t.Tuple[bool, GR], None, None],
    ) -> t.List[GR]:
        keys: t.List[int] = []
        rows: t.List[GR] = []
        old: t.List[GR] = []
        ikey = iter(keys)
        for k, (reused, row_new) in zip(ikey, args):
            _k = int(k)
            old_row = self.__inner[_k]
            if reused and not old_row is row_new:
                row_new = row_new.copy()
            keys.append(_k)
            rows.append(row_new)
            old.append(old_row)
        try:
            next(ikey)
            raise TypeError("Got more key indices than rows to set.")
        except StopIteration:
            pass
        try:
            next(args)
            raise TypeError("Got more rows to set than key indices.")
        except StopIteration:
            pass
        for k, r in zip(keys, rows):
            self.__inner[k] = r
            r._parent = self  # type: ignore
        for o in old:
            o._parent = None  # type: ignore
        return rows

    def _remove_by_cell(
        self, cell_name: str, cell_value: str, strict: bool = True
    ) -> t.Optional[GR]:
        index = self._find_by(cell_name, cell_value, strict)
        if index is not None:
            result = self[index]
            del self[index]
            return result

    def _find_by(
        self, attr_name: str, value: OptCellValue, strict: bool = True
    ) -> t.Optional[int]:
        if attr_name not in self._row_type._args_names_flat:  # type: ignore
            raise KeyError(
                f"{self.__class__.__name__} has now rows with argument "
                f"'{attr_name}'."
            )
        for i, row in enumerate(self.__inner):
            row_val = getattr(row, attr_name)
            if row_val == value:
                return i
        if strict:
            raise ValueError(
                f"Found no rows with {self.__class__.__name__}.{attr_name}=={value}."
            )

    def _validate_row_dict(
        self, value: t.Dict[t.Any, t.Any]
    ) -> t.Dict[str, OptCellValue]:
        assert all(
            type(k) is str for k in value
        ), "dict argument bust have all it's keys of type str."
        assert all(
            isinstance(value[k], (str, List)) or value[k] is None
            for k in value
        ), (
            "dict argument must have all it's values or types: "
            "str, model.List, None"
        )
        return value

    # ================ VIRTUAL METHODS
    def __from_str__(self, code: str) -> t.Iterable[GR]:
        """Most basic implementation for the code converter. Should be overriden
        as necessary.

        :meta public:
        """
        yield from (
            self._row_type(**converter.find_converter(n))
            for n in self._row_type._entries_parser(code)  # type: ignore
        )


# ========================= pprint dispatcher ==========================


def _pprint_model_list(
    self: pprint.PrettyPrinter,
    object: List[GR],
    stream: t.IO[str],
    indent: int,
    allowance: int,
    context: t.Dict[int, int],
    level: int,
):
    child_indent: int = indent + max(self._indent_per_level - 2, 0)  # type: ignore
    stream.write(f"{object.__class__.__name__}[\n{' ' * child_indent}")
    self._format_items(  # type: ignore
        object.inner(), stream, indent, allowance + 1, context, level
    )
    stream.write(f"]")


pprint.PrettyPrinter._dispatch[List.__repr__] = _pprint_model_list  # type: ignore
d = pprint.PrettyPrinter._dispatch  # type: ignore
