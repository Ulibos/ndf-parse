"""This module presents ndf entities in a form of easy(ish)-to-work
structures.

.. _model-representation:

How NDF is Represented By The model
===================================

List with ListRows
------------------

+----------------------------------------+---------------------------------------+
| NDF                                    | python                                |
+========================================+=======================================+
| .. code-block:: ndf                    | .. code-block:: python                |
|                                        |                                       |
|     // as list                         |      lst = model.List(type='ListType')|
|     ListType[                          |      lst.add(                         |
|         export Namespace is "Value", 12|          model.ListRow(               |
|     ]                                  |              visibility = 'export',   |
|                                        |              namespace  = 'Namespace',|
|     // as source                       |              value      = '"Value"'   |
|     export Namespace is "Value"        |          ),                           |
|     12                                 |          model.ListRow(               |
|                                        |              visibility = None,       |
|                                        |              namespace  = None,       |
|                                        |              value      = '12'        |
|                                        |          )                            |
|                                        |      )                                |
|                                        |                                       |
+----------------------------------------+---------------------------------------+

Source List is the same as ordinary List but with :code:py:`lst.is_root = True`.

Object (and Template) with MemberRows
-------------------------------------

+-------------------------------------------+---------------------------------------+
| NDF                                       | python                                |
+===========================================+=======================================+
| .. code-block:: ndf                       | .. code-block:: python                |
|                                           |                                       |
|     ObjType(                              |    obj = model.Object(type='ObjType') |
|         memb_name : int = export Ns is 12 |    obj.add(                           |
|     )                                     |        model.MemberRow(               |
|                                           |            member     = 'memb_name',  |
|                                           |            type       = 'int',        |
|                                           |            visibility = 'export',     |
|                                           |            namespace  = 'Ns',         |
|                                           |            value      = '12'          |
|                                           |        )                              |
|                                           |    )                                  |
|                                           |                                       |
+-------------------------------------------+---------------------------------------+

:class:`Template` derives from :class:`Object` so it has the same row type plus
an additional property described below:

Template's Param with ParamRow
------------------------------

+----------------------------+------------------------------------------+
| NDF                        | python                                   |
+============================+==========================================+
| .. code-block:: ndf        | .. code-block:: python                   |
|                            |                                          |
|     template Ns            |      tpl = model.Template(type='ObjType')|
|     [                      |      tpl.params.add(                     |
|      param_name : int = 12 |          model.ParamRow(                 |
|     ] is ObjType()         |              param='param_name',         |
|                            |              type ='int',                |
|                            |              value='12'                  |
|                            |          )                               |
|                            |      )                                   |
|                            |                                          |
+----------------------------+------------------------------------------+

Usage Examples
--------------
Here is a basic example of working with this module's classes:

.. doctest::

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
    MemberRow[0](value='1', member='Member1', type='int', visibility=None, namespace=None)
    >>> expr = ndf.expression("MemberRenamed = Namespace is 2")
    >>> print(expr)
    {'value': '2', 'namespace': 'Namespace', 'member': 'MemberRenamed'}
    >>> m1.edit(**expr)  # edit row via dict decomposition
    MemberRow[0](value='2', member='MemberRenamed', type='int', visibility=None, namespace='Namespace')
    >>> ndf.printer.print(obj)
    TObject
    (
        MemberRenamed: int = Namespace is 2
    )
    >>> m1.edit(v='3', n='Ns', vis="export")  # edit using aliases
    MemberRow[0](value='3', member='MemberRenamed', type='int', visibility='export', namespace='Ns')
    >>> m1.edit(nonexistent="4", _strict=False)  # silently ignores
    MemberRow[0](value='3', member='MemberRenamed', type='int', visibility='export', namespace='Ns')
    >>> m1.edit(nonexistent="4")  # Raises an error
    Traceback (most recent call last):
        ...
    TypeError: Cannot set MemberRow.nonexistent, attribute does not exist.
    >>> obj.add(m1)  # add a copy of a row (will copy it under the hood)
    MemberRow[1](value='3', member='MemberRenamed', type='int', visibility='export', namespace='Ns')
    >>> obj.by_member('MemberRenamed')  # will find the first matching row
    MemberRow[0](value='3', member='MemberRenamed', type='int', visibility='export', namespace='Ns')

"""

from __future__ import annotations
import typing as t
import sys
import copy
from .. import converter, parser
from . import abc

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

OptStr = t.Optional[str]
OptParent = t.Optional[abc.List[abc.Row]]
_T = t.TypeVar("_T")

def flatten(lst: abc.ArgsNames) -> abc.ArgsNamesFlat:
    return tuple(x for y in lst for x in y)

############################# ListRow Implementations ##########################
class ListRow(abc.Row):
    """ListRow(value, visibility = None, namespace = None)
    Row of data from a :class:`List` object.
    """

    _args_names = (
        ("value", "v"),
        ("visibility", "vis"),
        ("namespace", "n"),
    )
    _args_required = ("value",)
    _args_names_flat = flatten(_args_names)
    _entries_parser = parser.entries_list

    visibility: OptStr
    vis: OptStr
    namespace: OptStr
    n: OptStr
    value: abc.CellValue
    v: abc.CellValue


class MemberRow(abc.Row):
    """MemberRow(value, member = None, type = None, visibility = None, namespace = None)
    Row of data from :class:`Object` and :class:`Template` objects.
    """

    member: OptStr
    m: OptStr
    type: OptStr
    t: OptStr
    visibility: OptStr
    vis: OptStr
    namespace: OptStr
    n: OptStr
    value: abc.CellValue
    v: abc.CellValue

    _args_names = (
        ("value", "v"),
        ("member", "m"),
        ("type", "t"),
        ("visibility", "vis"),
        ("namespace", "n"),
    )
    _args_required = ("value",)
    _args_names_flat = flatten(_args_names)
    _entries_parser = parser.entries_member


class ParamRow(abc.Row):
    """ParamRow(param, type = None, value = None)
    Row of data from a :class:`Params` object.
    """

    _args_names = (("param", "p"), ("type", "t"), ("value", "v"))
    _args_required = ("param",)
    _args_names_flat = flatten(_args_names)
    _entries_parser = parser.entries_param

    param: str
    p: str
    type: OptStr
    t: OptStr
    value: abc.OptCellValue
    v: abc.OptCellValue


class MapRow(abc.Row):
    """MapRow(key, value)
    Row of data from a :class:`Map` object.
    """

    _args_names = (("key", "k"), ("value", "v"))
    _args_required = ("key", "value")
    _args_names_flat = flatten(_args_names)
    _entries_parser = parser.entries_map

    key: str
    k: str
    value: abc.CellValue
    v: abc.CellValue

    def compare(self, other: object, existing_only: bool = True) -> bool:
        """Extends :meth:`original method <abc.Row.compare>` by adding
        comparisons against tuple pairs.
        """
        if abc.is_pair(other):
            other = t.cast(t.Tuple[abc.OptCellValue, abc.OptCellValue], other)
            if existing_only:
                result = True
                for v1, v2 in zip((self.k, self.v), other):
                    if v2 is None:
                        continue
                    if isinstance(v1, abc.List):
                        result &= v1.compare(v2)
                    if result is False:
                        return False
                return True
            else:
                return self.k == other[0] and self.v == other[1]  # type: ignore
        else:
            return super().compare(other, existing_only)

    def __init__(
        self, *args: abc.OptCellValue, **kwargs: abc.OptCellValue
    ) -> None:
        return self.__apply_args(super().__init__, args, kwargs)

    def edit(self, *args: abc.OptCellValue, **kwargs: abc.OptCellValue) -> abc.Self:  # type: ignore
        """Extends :meth:`original method <abc.Row.edit>` by adding editing with
        a tuple pair:

            >>> from ndf_parse.model import MapRow
            >>> row = MapRow("k1", "v1")
            >>> row
            MapRow[DANGLING](key='k1', value='v1')
            >>> row.edit(('k2', 'v2'))  # editing with a tuple
            MapRow[DANGLING](key='k2', value='v2')
            >>> row.edit(k='k3', v='v3')  # normal editing mode
            MapRow[DANGLING](key='k3', value='v3')

        """
        return self.__apply_args(super().edit, args, kwargs)

    def edit_ndf(self, code: str) -> Self:
        entries = self.__class__._entries_parser(code)
        if len(entries) != 1:
            raise ValueError(
                "edit(code) expects exactly one statement to be present in the "
                f"ndf code, got {len(entries)}."
            )
        return self.__apply_args(
            super().edit, converter.find_converter(entries[0])["value"], {}
        )

    def __apply_args(
        self,
        __method: t.Callable[[t.Any], _T],
        args: t.Tuple[abc.OptCellValue, ...],
        kwargs: t.Dict[str, abc.OptCellValue],
    ) -> _T:
        if len(args) == 1 and len(kwargs) == 0 and abc.is_pair(args[0]):
            # case .__apply_args(TuplePair)
            return __method(*args[0], **kwargs)
        elif (
            len(args) == 0
            and len(kwargs) == 1
            and "input" in kwargs
            and abc.is_pair(kwargs["input"])
        ):
            # case .__apply_args(input=TuplePair)
            args = kwargs.pop("input")  # type: ignore
        # case .__apply_args(*args, **kwargs)
        return __method(*args, **kwargs)


############################# List Implementations #############################


class List(abc.List[ListRow]):
    """List represents ndf lists (``[]``), vector types (``typename[]``) and a
    collection of root level statements (source root).
    """

    _row_type = ListRow

    def __init__(self, is_root: bool = False, type: OptStr = None) -> None:
        super().__init__()
        self.is_root: bool = is_root
        self.type: OptStr = type

    def _compare(self, other: object, existing_only: bool = True) -> bool:
        if isinstance(other, Object):
            if not existing_only or (existing_only and other.type is not None):
                if self.type != other.type:
                    return False
        return super()._compare(other, existing_only)

    def __deepcopy__(self, memo: t.Dict[int, t.Any]) -> Self:
        result = super().__deepcopy__(memo)
        result.is_root = self.is_root
        result.type = self.type
        return result

    def __from_str__(self, code: str) -> t.Iterable[ListRow]:
        if self.is_root:  # default insert_str is implemented for scene root
            prs = parser.entries_root
        else:
            prs = parser.entries_list
        yield from (
            self._row_type(**converter.find_converter(n)) for n in prs(code)
        )

    def by_namespace(
        self, namespace: str, strict: bool = True
    ) -> t.Optional[ListRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is :code:py:`True` then raises an error. If
        :code:py:`False` then returns None. If `strict` is not set then it's
        :code:py:`True` by default.
        """
        index = self._find_by("namespace", namespace, strict)
        if index is None:
            return
        return self[index]

    by_name = by_namespace
    by_n = by_namespace

    def remove_by_namespace(
        self, namespace: str, strict: bool = True
    ) -> t.Optional[ListRow]:
        """Find and remove row by it's namespace. Removes first occurence if
        found. Raises error if nothing found and `strict` is :code:py:`True`,
        else returns :code:py:`None`.
        """
        return self._remove_by_cell("namespace", namespace, strict)

    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace


class Object(abc.List[MemberRow]):
    """Object represents ndf objects as a list of members.
    """

    _row_type = MemberRow

    def __init__(self, type: OptStr = None) -> None:
        super().__init__()
        self.type: OptStr = type

    def _compare(self, other: object, existing_only: bool = True) -> bool:
        if isinstance(other, Object):
            if not existing_only or (existing_only and other.type is not None):
                if self.type != other.type:
                    return False
        return super()._compare(other, existing_only)

    def __deepcopy__(self, memo: t.Dict[int, t.Any]) -> Self:
        result = super().__deepcopy__(memo)
        result.type = self.type
        return result

    def by_namespace(
        self, namespace: str, strict: bool = True
    ) -> t.Optional[MemberRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is :code:py:`True` then raises an error. If
        :code:py:`False` then returns None. If `strict` is not set then it's
        :code:py:`True` by default.
        """
        index = self._find_by("namespace", namespace, strict)
        if index is None:
            return
        return self[index]

    by_name = by_namespace
    by_n = by_namespace

    def remove_by_namespace(
        self, namespace: str, strict: bool = True
    ) -> t.Optional[MemberRow]:
        """Find and remove row by it's namespace. Removes first occurence if
        found. Raises error if nothing found and `strict` is :code:py:`True`,
        else returns :code:py:`None`.
        """
        return self._remove_by_cell("namespace", namespace, strict)

    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace

    def by_member(
        self, member: str, strict: bool = True
    ) -> t.Optional[MemberRow]:
        """Returns first match that is found. If none found and `strict` is
        :code:py:`True` then raises an error. If :code:py:`False` then returns
        None. If `strict` is not set then it's :code:py:`True` by default.
        """
        index = self._find_by("member", member, strict)
        if index is None:
            return
        return self[index]

    by_m = by_member

    def remove_by_member(
        self, member: str, strict: bool = True
    ) -> t.Optional[MemberRow]:
        """Find and remove row by it's member. Removes first occurence if found.
        Raises error if nothing found and `strict` is :code:py:`True`, else
        returns :code:py:`None`.
        """
        return self._remove_by_cell("member", member, strict)

    rm_m = remove_by_member


class Template(Object):
    """Template represents ndf templates as a list of members and template
    params.
    """

    _row_type = MemberRow

    def __init__(self, type: OptStr = None) -> None:
        super().__init__(type)
        self.params = Params()

    def _compare(self, other: object, existing_only: bool = True) -> bool:
        if isinstance(other, Template):
            if not self._compare(other.params, existing_only):
                return False
        return super()._compare(other, existing_only)

    def __deepcopy__(self, memo: t.Dict[int, t.Any]) -> Self:
        result = super().__deepcopy__(memo)
        result.type = self.type
        result.params = copy.deepcopy(self.params, memo)
        return result


class Params(abc.List[ParamRow]):
    """Params represents a list of generic parameters to be used in a template."""

    _row_type = ParamRow

    def by_param(
        self, param: str, strict: bool = True
    ) -> t.Optional[ParamRow]:
        """Find row by it's namespace. Returns first match that is found. If
        none found and `strict` is :code:py:`True` then raises an error. If
        :code:py:`False` then returns None. If `strict` is not set then it's
        :code:py:`True` by default.
        """
        index = self._find_by("param", param, strict)
        if index is None:
            return
        return self[index]

    by_p = by_param

    def remove_by_param(
        self, param: str, strict: bool = True
    ) -> t.Optional[ParamRow]:
        """Find and remove row by it's param. Removes first occurence if found.
        Raises error if nothing found and `strict` is :code:py:`True`, else
        returns :code:py:`None`.
        """
        return self._remove_by_cell("param", param, strict)

    rm_m = remove_by_param


class Map(abc.List[MapRow]):
    """Map represents ndf maps as a list of pairs represented as a
    :class:`MapRow`.

    Map has a couple things that set it apart from other list-like objects in
    this module. In ndf code pairs are represented in a way that lends itself
    perfectly into storing them as tuples in python (at least visually). But
    using them to set a row has a nuance. Here is an illustration of the issue,
    an explanation will follow:

        >>> from ndf_parse.model import Map
        >>> map = Map()
        >>> map[:] = ("key", "value")  # this will fail
        Traceback (most recent call last):
            ...
        ndf_parse.traverser.BadNdfError: Errors while parsing expression:
        0: Syntax error at 0:0: key
        >>> map[:] = (("key", "value"), )  # a tuple wrapped in another iterable will work
        >>> map[0] = ("key2", "value2"),  # same as above, just shorter (one extra comma)
        >>> map
        Map[MapRow[0](key='key2', value='value2')]

    Explanation: when a list-like recieves an iterable as an insertion,
    it iterates it and treats each value inside as a row or row's
    representation. In this case it iterates the pair and tries to interpret
    each string as an ndf code (which it obviously isn't). To avoid such
    behaviour we wrap our pair into any other iterable (tuple in this case but
    it can be a list too). For brevity python allows to omit tuple's brackets
    unless it's ambiguous (inside a function call for exampe) so we get left
    with just an extra comma.

    Map also supports checking if a key is inside of it in a pythonic way:

    >>> from ndf_parse.model import Map, MapRow
    >>> pairs = Map()
    >>> pairs.add(k='test', v='some_value')
    MapRow[0](key='test', value='some_value')
    >>> 'test' in pairs
    True
    >>> 'test2' in pairs
    False
    >>> 'some_value' in pairs  # checks only keys, not values!
    False
    >>> # it also retains ability to check for a row as other list-likes
    >>> pairs[0] in pairs
    True

    """

    _row_type = MapRow

    def by_key(self, key: str, strict: bool = True) -> t.Optional[MapRow]:
        """Find row by it's key. Returns first match or None if not found. If
        none found and `strict` is :code:py:`True` then raises an error. If
        :code:py:`False` then returns None. If `strict` is not set then it's
        :code:py:`True` by default.
        """
        index = self._find_by("key", key, strict)
        if index is None:
            return
        return self[index]

    by_k = by_key

    def remove_by_key(
        self, key: str, strict: bool = True
    ) -> t.Optional[MapRow]:
        """Find and remove row by it's key. Removes first occurence if found.
        Raises error if nothing found and `strict` is :code:py:`True`, else
        returns :code:py:`None`.
        """
        return self._remove_by_cell("key", key, strict)

    rm_k = remove_by_key

    def __from_str__(self, code: str) -> t.Iterable[MapRow]:
        yield from (
            self._row_type(*converter.pair(n)["value"])
            for n in parser.entries_map(code)
        )

    def __contains__(self, value: t.Any) -> bool:
        """Compare based on value type. Work as a dict for strings and as
        default for other inputs.
        """
        if isinstance(value, self._row_type):
            return next((True for x in self.inner() if value is x), False)
        elif isinstance(value, str):
            return next((True for x in self.inner() if value == x.key), False)
        return False

    def _possibly_single_return(self, arg: t.Any) -> bool:
        if abc.is_pair(arg):
            return True
        return super()._possibly_single_return(arg)

    def __yield_rows__(
        self, input: t.Any
    ) -> t.Iterable[t.Tuple[bool, MapRow]]:
        if abc.is_pair(input):
            yield (False, self._row_type(input))
        else:
            yield from super().__yield_rows__(input)


__all__ = [
    "abc",
    ## ------------ ##
    "MemberRow",
    "ListRow",
    "ParamRow",
    "MapRow",
    ## ------------ ##
    "Object",
    "Template",
    "List",
    "Map",
    "Params",
]
