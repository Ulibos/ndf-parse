"""This submodule presents ndf entities in a form of easy(ish)-to-work
structures.
"""
from __future__ import annotations
import sys
import dataclasses as dc
import typing as tp
from typing import overload, Any, Optional, Union, Dict, Tuple

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

##################################### Consts ###################################

ArgsNamesFlat = Tuple[str, ...]
ArgsNames = Tuple[Tuple[str, ...], ...]


def flatten(lst: ArgsNames) -> ArgsNamesFlat:
    return tuple(x for y in lst for x in y)


LIST_ROWS = (
    ("visibility", "vis"),
    ("namespace", "n"),
    ("value", "v"),
)
LIST_ROWS_FLAT = flatten(LIST_ROWS)

MEMBER_ROWS = (
    ("member", "m"),
    ("type", "t"),
    ("visibility", "vis"),
    ("namespace", "n"),
    ("value", "v"),
)
MEMBER_ROWS_FLAT = flatten(MEMBER_ROWS)

PARAM_ROWS = (("param", "p"), ("type", "t"), ("value", "v"))
PARAM_ROWS_FLAT = flatten(PARAM_ROWS)

MAP_ROWS = (("key", "k"), ("value", "v"))
MAP_ROWS_FLAT = flatten(MAP_ROWS)

###################################### Utils ###################################
def verify_kwargs(
    kwargs: Dict[str, OptCellVal],
    owner: tp.Type[DeclListRow],
    strict: bool = True,
):
    """verify_kwargs(kwargs: dict, owner: type, strict = True)
    Function to verify that kwargs don't contain colliding attributes and
    garbage keys.

    Parameters
    ----------
    kwargs : Dict[str, OptCellVal]
        dict of kwargs who's keys to validate.
    owner : tp.Type[DeclListRow]
        Class/subclass to check against.
    strict : bool, default=True
        If set to ``True`` and kwargs have a key that doesn't match against any
        property of the owner, then throws an exception. If set to ``False``
        then ignores any non-represented keys but still tracks parameter
        collisions.

    Raises
    ------
    TypeError
        If strict mode is set and there was a key that doesn't represent any
        owner's parameter.
    TypeError
        If there is a parameter collision (2 or more aliases are simultaneously
        present in kwargs).
    """
    if strict:
        for k in kwargs:
            if not k in owner._args_names_flat:
                raise TypeError(
                    f"Cannot set {owner.__name__}.{k}, attribute does "
                    "not exist."
                )
    for args in owner._args_names:  # type: ignore
        num_collisions = 0
        for arg in args:
            num_collisions += arg in kwargs
            if num_collisions > 1:
                raise TypeError(
                    "Can't use multiple mutually exclusive args: "
                    f"{', '.join(repr(x) for x in args)}."  # type: ignore
                )


def iterate_args(
    kwargs: Dict[str, OptCellVal],
    owner: tp.Type[Union[DeclListRow_co, DeclarationsList[DeclListRow_co]]],
) -> tp.Iterator[Tuple[str, OptCellVal]]:
    """iterate_args(kwargs, owner) -> Iterator<str, OptCellVal>
    Applies kwargs to the owner. It never fails. Any kwargs that are not
    represented as parameters of the owner are simply ignored. Any collisions
    are passed as is.

    Parameters
    ----------
    kwargs : Dict[str, OptCellVal]
        kwargs to apply to the owner.
    owner : tp.Type[Union[DeclListRow, DeclarationsList[DeclListRow]]]
        Class/subclass to apply kwargs to.

    Returns
    -------
    tp.Iterator[Tuple[str, OptCellVal]]
        Garbage free ``parameter: value`` pair iterator.

    Yields
    ------
    Iterator[tp.Iterator[Tuple[str, OptCellVal]]]
        ``parameter: value`` pair.
    """
    for k, v in kwargs.items():
            for aliases in owner._args_names:  # type: ignore
                if k in aliases:
                    yield (aliases[0], v)  # use original parameter name
                    break


############################# ListRow Implementations ##########################


@dc.dataclass(repr=False)
class DeclListRow:
    """DeclListRow()
    Abstract class for rows of data in list-like structures of the model.

    It serves as a foundation for any classes that are meant to store assigned
    items along with any related metadata (variable names, visibility modifiers,
    mapping keys etc.)
    
    Attributes
    ----------
    parent : DeclarationsList[Self]
        List-like object to which this row belongs.
    index : int, readonly
        Index of this row in the parent object.
    """

    # !!! cannot use type hinting here, it triggers dataclass decorator
    _args_names = (("",),)  # should point to a DECL_ROW
    _args_names_flat = ("",)  # should point to a DECL_ROW_FLAT

    parent: DeclarationsList[Self] = dc.field(compare=False, hash=False)

    @property
    def index(self) -> int:
        return self.parent.index(self)

    def __repr__(self) -> str:
        args = (
            f"{k}={repr(getattr(self, k))}"
            for k in (x[0] for x in self._args_names)
        )
        return (
            f"{self.parent.__class__.__name__}[{self.index}]"
            f"({', '.join(args)})"
        )

    def __post_init__(self):
        for attr in (getattr(self, arg) for arg in self.__full_args_names()):
            self.__parent(attr)

    def edit(self, _strict: bool = True, **kwargs: OptCellVal) -> Self:
        """edit(_strict = True, **kwargs) -> Self
        Edit current row with multiple values (except `parent` and `index`).

        This method allows to edit a bunch of values in the row at once. It also
        accepts properties' aliases as well as easily unpacking an output of an
        :func:`ndf_parse.expression`.

        Note
        ----
        You cannot pass mutually exclusive keys at once, for example, you cannot
        pass ``namespace=...`` along with ``n=...`` to :meth:`ListRow.edit`, it
        will raise an error.

        Parameters
        ----------
        kwargs : :data:`CellValue` | None
            Properties to edit.
        _strict : bool, default=True
            If set to ``True`` and kwargs contain a key that doesn't match any
            properties of this row then it will fail. If ``False`` then it will
            silently skip it.
        
        Return
        ------
        Self

        Examples
        --------

        >>> import ndf_parse as ndf
        >>> source = ndf.convert(b"Test is TObject(Member1: int = 1)")
        >>> obj = source[0].v  # `v` is an alias for `value`
        >>> ndf.printer.print(obj)
        TObject
        (
            Member1: int = 1
        )
        >>> # note there was no "Test is", because we've printed only the value, not the row
        >>> m1 = obj[0]
        >>> print(m1)  # check the row
        Object[0](member='Member1', type='int', visibility=None, namespace=None, value='1')
        >>> expr = ndf.expression("MemberRenamed = Namespace is 2")
        >>> print(expr)
        {'value': '2', 'namespace': 'Namespace', 'member': 'MemberRenamed'}
        >>> m1.edit(**expr)  # edit row via dict decomposition
        Object[0](member='MemberRenamed', type='int', visibility=None, namespace='Namespace', value='2')
        >>> ndf.printer.print(obj)
        TObject
        (
            MemberRenamed: int = Namespace is 2
        )
        >>> m1.edit(v='3', n='Ns', vis="export")  # edit using aliases
        Object[0](member='MemberRenamed', type='int', visibility='export', namespace='Ns', value='3')
        >>> m1.edit(nonexistent="4", _strict=False)  # silently ignores
        Object[0](member='MemberRenamed', type='int', visibility='export', namespace='Ns', value='3')
        >>> m1.edit(nonexistent="4")  # Raises an error
        TypeError: Cannot set MemberRow.nonexistent, attribute does not exist.
        """
        verify_kwargs(kwargs, self.__class__, _strict)
        for k, v in iterate_args(kwargs, self.__class__):
            self.__parent(v)
            setattr(self, k, v)
        return self

    def as_dict(self):
        """Outputs given row in a form of a dict.
        
        Warnings
        --------
        It does not perform copy for it's `value`, so avoid using it to copy a row
        from one place to another.
        :ref:`More on referencing restrictions <no-referencing>`.
        """
        return {k: getattr(self, k) for k in self.__full_args_names()}

    def __full_args_names(self) -> tp.Iterable[str]:
        return (x[0] for x in self._args_names)

    def __parent(self, item: Any):
        """Parent any DeclarationList that isn't parented yet. Fail if parented
        to something else already. Skip all other types."""
        if isinstance(item, DeclarationsList):
            if item.parent is None:
                item.parent = self.parent
            elif item.parent != self.parent:
                raise AssertionError(
                    'Cannot reparent an object of type `DeclarationsList`, '
                    'operation not allowed!'
                )


@dc.dataclass(repr=False)
class ListRow(DeclListRow):
    """ListRow(parent, value, visibility = None, namespace = None)
    Row of data from a :class:`List` object.
    
    Attributes
    ----------
    parent : List
        List-like object to which this row belongs.
    index : int, readonly
        Index of this row in the parent object.
    value : :data:`CellValue` | str
        Value of this row.
    visibility : str | None
        Visibility modifier of the assignment. Should be one of these:
        ``'unnamed'`` | ``'export'`` | ``'private'`` | ``'public'``
        Keep in mind that it won't protect from ``'unnamed'`` actually having a
        name or appearing multiple times the List, see :ref:`notes on checking
        strictness <checking-strictness>`.
    namespace : str | None
        Namespace name of the assignment.
    vis
        An alias for `visibility`.
    n
        An alias for `namespace`.
    v
        An alias for `value`.
    """

    value: CellValue
    visibility: OptStr = None
    namespace: OptStr = None

    _args_names = LIST_ROWS
    _args_names_flat = LIST_ROWS_FLAT

    # fmt: off
    @property
    def vis(self) -> OptStr: return self.visibility
    @vis.setter
    def vis(self, visibility: OptStr): self.visibility = visibility
    @property
    def n(self) -> OptStr: return self.namespace
    @n.setter
    def n(self, namespace: str): self.namespace = namespace
    @property
    def v(self) -> CellValue: return self.value
    @v.setter
    def v(self, value: CellValue): self.value = value
    # fmt: on


@dc.dataclass(repr=False)
class MemberRow(DeclListRow):
    """MemberRow(parent, value, member = None, type = None, visibility = None, namespace = None)
    Row of data from :class:`Object` and :class:`Template` objects.
    
    Attributes
    ----------
    parent : Object | Template
        List-like object to which this row belongs.
    index : int, readonly
        Index of this row in the parent object.
    member : str | None
        Member name of the object.
    type : str | None
        Typing data for this object. Keep in mind,
        :ref:`not all types are stored here. <typing-ambiguity>`
    value : :data:`CellValue` | str
        Value of this row.
    visibility : str | None
        Visibility modifier of the assignment. Should be one of these:
        ``'export'`` | ``'private'`` | ``'public'``
    namespace : str | None
        Namespace name of the assignment.
    vis
        An alias for `visibility`.
    m
        An alias for `member`.
    t
        An alias for `type`.
    n
        An alias for `namespace`.
    v
        An alias for `value`.
    """

    value: CellValue
    member: OptStr = None
    type: OptStr = None
    visibility: OptStr = None
    namespace: OptStr = None

    _args_names = MEMBER_ROWS
    _args_names_flat = MEMBER_ROWS_FLAT

    # fmt: off
    @property
    def m(self) -> OptStr: return self.member
    @m.setter
    def m(self, member: str): self.member = member
    @property
    def t(self) -> OptStr: return self.type
    @t.setter
    def t(self, type: str): self.type = type
    @property
    def vis(self) -> OptStr: return self.visibility
    @vis.setter
    def vis(self, visibility: OptStr): self.visibility = visibility
    @property
    def n(self) -> OptStr: return self.namespace
    @n.setter
    def n(self, namespace: str): self.namespace = namespace
    @property
    def v(self) -> CellValue: return self.value
    @v.setter
    def v(self, value: CellValue): self.value = value
    # fmt: on


@dc.dataclass(repr=False)
class ParamRow(DeclListRow):
    """ParamRow(parent, param = None, type = None, value = None)
    Row of data from a :class:`Params` object.
    
    Attributes
    ----------
    parent : Params
        List-like object to which this row belongs.
    index : int, readonly
        Index of this row in the parent object.
    param : str
        Generic parameter's name.
    type : str | None
        Typing data for this parameter. Keep in mind,
        :ref:`not all types are stored here. <typing-ambiguity>`
    value : :data:`CellValue` | str | None
        Value of this parameter.
    p
        An alias for `param`.
    t
        An alias for `type`.
    v
        An alias for `value`.
    """

    param: str
    type: OptStr = None
    value: OptCellVal = None

    _args_names = PARAM_ROWS
    _args_names_flat = PARAM_ROWS_FLAT

    # fmt: off
    @property
    def p(self) -> OptStr: return self.param
    @p.setter
    def p(self, param: str): self.param = param
    @property
    def t(self) -> OptStr: return self.type
    @t.setter
    def t(self, type: str): self.type = type
    @property
    def v(self) -> OptCellVal: return self.value
    @v.setter
    def v(self, value: CellValue): self.value = value
    # fmt: on

    _args_names = (("param", "p"), ("type",), ("value", "v"))
    _args_names_flat = tuple(x[0] for x in _args_names)


@dc.dataclass(repr=False)
class MapRow(DeclListRow):
    """MapRow(parent, key, value)
    Row of data from a :class:`Params` object.
    
    Attributes
    ----------
    parent : MapRow
        List-like object to which this row belongs.
    index : int, readonly
        Index of this row in the parent object.
    key : str
        Key of this pair.
    value : :data:`CellValue` | str
        Value of this pair.
    k
        An alias for `key`.
    v
        An alias for `value`.
    """

    key: str
    value: CellValue

    _args_names = MAP_ROWS
    _args_names_flat = MAP_ROWS_FLAT

    # fmt: off
    @property
    def k(self) -> str: return self.key
    @k.setter
    def k(self, key: str): self.key = key
    @property
    def v(self) -> CellValue: return self.value
    @v.setter
    def v(self, value: CellValue): self.value = value
    # fmt: on


DeclListRow_co = tp.TypeVar(
    "DeclListRow_co", bound=DeclListRow, covariant=True
)


####################### DeclarationsList Implementations #######################


class DeclarationsList(tp.List[DeclListRow_co]):  # type: ignore
    """Abstract class for list-like objects of this model. It is used to store
    rows that are subclasses of :class:`DeclListRow`.
    
    Attributes
    ----------
    parent : DeclarationsList | None
        Parent of this object. All objects of this class and it's subclasses are
        expected to have it NOT equal to ``None``. Exceptions: root-level
        :class:`List` and objects that are generated with
        :func:`ndf_parse.expression` and not yet added to some parent.
    """

    _row_type: tp.Type[DeclListRow_co]

    def add(
        self, _strict: bool = True, **kwargs: OptCellVal
    ) -> DeclListRow_co:
        """add(_strict = True, **kwargs) -> DeclListRow
        Builds and adds a new row from given arguments.

        Parameters
        ----------
        kwargs : :data:`CellValue` | None
            Properties to edit.
        _strict : bool, default=True
            If set to ``True`` and kwargs contain a key that doesn't match any
            properties of this row then it will fail. If ``False`` then it will
            silently skip it.
        
        Examples
        --------
        >>> import ndf_parse as ndf
        >>> source = ndf.model.List(is_root = True)
        >>> source
        []  # all DeclarationLists in model derive from list hence the look
        >>> # add an item
        >>> source.add(namespace="Two", value="2")
        List[0](visibility=None, namespace='Two', value='2')
        >>> # use aliases
        >>> source.add(vis='export', n="Text", v="'My text.'")
        List[1](visibility='export', namespace='Text', value="'My text.'")
        >>> # silently skip non-existent arguments
        >>> source.add(n="Four", v="4", nonexistent='blah', _strict = False)
        List[2](visibility=None, namespace='Four', value='4')
        >>> # fail on non-existent arguments (default behaviour)
        >>> source.add(n="Four", v="4", nonexistent='blah')
        TypeError: Cannot set ListRow.nonexistent, attribute does not exist.
        >>> ndf.printer.print(source)
        Two is 2
        export Text is 'My text.'
        Four is 4

        """
        verify_kwargs(kwargs, self._row_type, _strict)
        result = self._row_type(
            self, **dict(iterate_args(kwargs, self._row_type))
        )
        super().append(result)
        return result

    def insert(  # type: ignore
        self, index: int, _strict: bool = True, **kwargs: OptCellVal,
    ) -> DeclListRow_co:
        """insert(index, _strict = True, **kwargs) -> DeclListRow
        Builds and inserts a new row from given arguments into a given place.
        
        Same logic applies as in :meth:`add` method, just with addition of an
        index as first positional argument.

        Parameters
        ----------
        index : int
            Where to insert a new row.
        kwargs : Optional[CellValue]
            Properties to edit.
        _strict : bool, default=True
            If set to ``True`` and kwargs contain a key that doesn't match any
            properties of this row then it will fail. If ``False`` then it will
            silently skip it.
        """
        verify_kwargs(kwargs, self._row_type, _strict)
        result = self._row_type(
            self, **dict(iterate_args(kwargs, self._row_type))
        )
        super().insert(index, result)
        return result

    def __init__(self):
        super().__init__()
        self.parent: Optional[DeclarationsList[Any]] = None

    @overload
    def _find_by(self, attr_name: str, value: Any) -> int:
        ...

    @overload
    def _find_by(
        self, attr_name: str, value: Any, strict: bool = False
    ) -> Optional[int]:
        ...

    def _find_by(
        self, attr_name: str, value: Any, strict: bool = True
    ) -> Optional[int]:
        for i, row in enumerate(self):
            self_val = getattr(row, attr_name)
            if (
                self_val is not None
                and value is not None
                and self_val == value
            ):
                return i
        if strict:
            raise ValueError(f"No rows with .{attr_name}=={value}.")


class List(DeclarationsList[ListRow]):
    """List represents ndf lists (``[]``), vector types (``typename[]``) and a
    collection of root level statements (source root).

    Attributes
    ----------
    is_root : bool, default=False
        Indicates whether this is a source root or any other nested item.
        Needed for :mod:`.printer` format them differently.
    type : str | None, default=None
        Stores type for vector types (like ``RGBA[0, 0, 0, 1]``). See
        :ref:`Typing Ambiguity <typing-ambiguity>` in main documentation for
        more info.
    """

    _row_type = ListRow

    def __init__(self, is_root: bool = False, type: OptStr = None):
        super().__init__()
        self.is_root: bool = is_root
        self.type: OptStr = type

    # fmt: off
    @overload
    def by_namespace(self, namespace: str) -> ListRow: ...
    @overload
    def by_namespace(self, namespace: str, strict : bool) -> Optional[ListRow]: ...
    def by_namespace(self, namespace: str, strict : bool = True) -> Optional[ListRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is ``True`` then raises an error. If ``False``
        then returns None. If `strict` is not set then it's ``True`` by default.
        """
        index = self._find_by("namespace", namespace, strict)
        if index is None: return
        return self[index]

    by_name = by_namespace
    by_n = by_namespace

    def remove_by_namespace(self, namespace: str):
        """Find and remove row by it's namespace. Removes first occurence if
        found. Raises error if nothing found.
        """
        index = self._find_by("namespace", namespace)
        del self[index]

    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace
    # fmt: on


class Object(DeclarationsList[MemberRow]):
    """Object represents ndf objects as a list of members.

    Attributes
    ----------
    type : str | None, default=None
        Stores object's type (for ``TObject( ... )`` it's `type` will be equal
        to ``TObject``). See :ref:`Typing Ambiguity <typing-ambiguity>` in main
        documentation for more info.
    """

    _row_type = MemberRow

    def __init__(self):
        super().__init__()
        self.type: OptStr = None

    # fmt: off
    @overload
    def by_namespace(self, namespace: str) -> MemberRow: ...
    @overload
    def by_namespace(self, namespace: str, strict : bool) -> Optional[MemberRow]: ...
    def by_namespace(self, namespace: str, strict : bool = True) -> Optional[MemberRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is ``True`` then raises an error. If ``False``
        then returns None. If `strict` is not set then it's ``True`` by default.
        """
        index = self._find_by("namespace", namespace, strict)
        if index is None: return
        return self[index]

    by_name = by_namespace
    by_n = by_namespace

    def remove_by_namespace(self, namespace: str):
        """Find and remove row by it's namespace. Removes first occurence if
        found. Raises error if nothing found.
        """
        index = self._find_by("namespace", namespace)
        del self[index]

    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace

    @overload
    def by_member(self, member: str) -> MemberRow: ...
    @overload
    def by_member(self, member: str, strict : bool) -> Optional[MemberRow]: ...
    def by_member(self, member: str, strict : bool = True) -> Optional[MemberRow]:
        """Returns first match that is found. If none found and `strict` is
        ``True`` then raises an error. If ``False`` then returns None. If
        `strict` is not set then it's ``True`` by default.
        """
        index = self._find_by("member", member, strict)
        if index is None: return
        return self[index]

    by_m = by_member

    def remove_by_member(self, member: str):
        """Find and remove row by it's member. Removes first occurence if found.
        Raises error if nothing found.
        """
        index = self._find_by("member", member)
        del self[index]

    rm_m = remove_by_member
    # fmt: on


class Template(Object):
    """Template represents ndf templates as a list of members and template
    params.

    Attributes
    ----------
    type : str | None, default=None
        Stores template's type (for ``template [ ... ] Ns is TObject( ... )``
        it's `type` will be equal ``TObject``). See :ref:`Typing Ambiguity
        <typing-ambiguity>` in main documentation for more info.
    params : Params
        Attribute that holds template parameters.
    """

    _row_type = MemberRow

    def __init__(self):
        super().__init__()
        self.params = Params()


class Params(DeclarationsList[ParamRow]):
    """Params represents a list of generic parameters to be used in a template.
    """

    _row_type = ParamRow

    # fmt: off
    @overload
    def by_param(self, param: str) -> ParamRow: ...
    @overload
    def by_param(self, param: str, strict : bool) -> Optional[ParamRow]: ...
    def by_param(self, param: str, strict : bool = True) -> Optional[ParamRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is ``True`` then raises an error. If ``False``
        then returns None. If `strict` is not set then it's ``True`` by default.
        """
        index = self._find_by("param", param, strict)
        if index is None: return
        return self[index]

    by_p = by_param

    def remove_by_param(self, param: str):
        """Find and remove row by it's param. Removes first occurence if found.
        Raises error if nothing found.
        """
        index = self._find_by("param", param)
        del self[index]

    rm_m = remove_by_param
    # fmt: on


class Map(DeclarationsList[MapRow]):
    """Map represents ndf maps as a list of pairs represented as a
    :class:`MapRow`. It supports checking if key is inside of it in pythonic
    way:

    >>> pairs = Map()
    >>> pairs.add('test', 'some_value')
    >>> 'test' in pairs
    True
    >>> 'test2' in pairs
    False
    >>> 'some_value' in pairs  # checks only keys, not values!
    False

    """

    _row_type = MapRow

    def __contains__(self, key: Any) -> bool:
        for i in self:
            if key in i.key:
                return True
        return False

    # fmt: off
    @overload
    def by_key(self, key: str) -> MapRow: ...
    @overload
    def by_key(self, key: str, strict : bool) -> Optional[MapRow]: ...
    def by_key(self, key: str, strict : bool = True) -> Optional[MapRow]:
        """Find row by it's key. Returns first match or None if not found. If
        none found and `strict` is ``True`` then raises an error. If ``False``
        then returns None. If `strict` is not set then it's ``True`` by default.
        """
        index = self._find_by("key", key, strict)
        if index is None: return
        return self[index]

    by_k = by_key

    def remove_by_key(self, key: str):
        """Find and remove row by it's key. Removes first occurence if found.
         Raises error if nothing found.
         """
        index = self._find_by("key", key)
        del self[index]

    rm_k = remove_by_key
    # fmt: on


OptStr = Optional[str]
DictLists = tp.Union[
    DeclarationsList[ListRow],
    DeclarationsList[MapRow],
    DeclarationsList[MemberRow],
    DeclarationsList[ParamRow],
]

CellValue = tp.Union[
    str,
    DeclarationsList[ListRow],
    DeclarationsList[MapRow],
    DeclarationsList[MemberRow],
]
OptCellVal = Optional[CellValue]
Rows = Union[ParamRow, MemberRow, ListRow, MapRow]

__all__ = [
    "DeclListRow",
    "MemberRow",
    "ListRow",
    "ParamRow",
    "MapRow",
    "Rows",
    ## ------------ ##
    "DeclarationsList",
    "Object",
    "List",
    "Map",
    "Params",
    "Rows",
]
