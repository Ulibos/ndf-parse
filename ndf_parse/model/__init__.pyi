from __future__ import annotations
import sys
import typing as t
from typing import overload
from . import abc

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

OptStr = t.Optional[str]
OptParent = t.Optional[abc.List[abc.Row]]
Pair = t.Tuple[abc.CellValue, abc.CellValue]

class ListRow(abc.Row):
    visibility: OptStr
    namespace: OptStr
    value: abc.CellValue

    @property
    def vis(self) -> OptStr: ...
    @vis.setter
    def vis(self, visibility: OptStr) -> None: ...
    @property
    def n(self) -> OptStr: ...
    @n.setter
    def n(self, namespace: str) -> None: ...
    @property
    def v(self) -> abc.CellValue: ...
    @v.setter
    def v(self, value: abc.CellValue) -> None: ...

    # fmt: off
    @overload
    def __init__(self, value: abc.CellValue, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, value: abc.CellValue, visibility: OptStr = None, namespace: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...
    @overload
    def __init__(self, v: abc.CellValue, vis: OptStr = None, n: OptStr = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, v: abc.CellValue, vis: OptStr = None, n: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...

    @overload
    def edit(self, value: abc.CellValue = None, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, value: abc.CellValue = None, visibility: OptStr = None, namespace: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, v: abc.CellValue = None, vis: OptStr = None, n: OptStr = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, v: abc.CellValue = None, vis: OptStr = None, n: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    # fmt: on

class MemberRow(abc.Row):
    member: OptStr
    type: OptStr
    visibility: OptStr
    namespace: OptStr
    value: abc.CellValue

    @property
    def m(self) -> OptStr: ...
    @m.setter
    def m(self, member: str) -> None: ...
    @property
    def t(self) -> OptStr: ...
    @t.setter
    def t(self, type: str) -> None: ...
    @property
    def vis(self) -> OptStr: ...
    @vis.setter
    def vis(self, visibility: OptStr) -> None: ...
    @property
    def n(self) -> OptStr: ...
    @n.setter
    def n(self, namespace: str) -> None: ...
    @property
    def v(self) -> abc.CellValue: ...
    @v.setter
    def v(self, value: abc.CellValue) -> None: ...

    # fmt: off
    @overload
    def __init__(self, value: abc.CellValue, member: OptStr = None, type: OptStr = None, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, value: abc.CellValue, member: OptStr = None, type: OptStr = None, visibility: OptStr = None, namespace: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...
    @overload
    def __init__(self, v: abc.CellValue, m: OptStr = None, t: OptStr = None, vis: OptStr = None, n: OptStr = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, v: abc.CellValue, m: OptStr = None, t: OptStr = None, vis: OptStr = None, n: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...

    @overload
    def edit(self, value: abc.CellValue = None, member: OptStr = None, type: OptStr = None, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, value: abc.CellValue = None, member: OptStr = None, type: OptStr = None, visibility: OptStr = None, namespace: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, v: abc.CellValue = None, m: OptStr = None, t: OptStr = None, vis: OptStr = None, n: OptStr = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, v: abc.CellValue = None, m: OptStr = None, t: OptStr = None, vis: OptStr = None, n: OptStr = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    # fmt: on

class ParamRow(abc.Row):
    param: str
    type: OptStr
    value: abc.OptCellValue

    @property
    def p(self) -> OptStr: ...
    @p.setter
    def p(self, param: str) -> None: ...
    @property
    def t(self) -> OptStr: ...
    @t.setter
    def t(self, type: str) -> None: ...
    @property
    def v(self) -> abc.OptCellValue: ...
    @v.setter
    def v(self, value: abc.OptCellValue) -> None: ...

    # fmt: off
    @overload
    def __init__(self, param: str, type: OptStr = None, value: abc.OptCellValue = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, param: str, type: OptStr = None, value: abc.OptCellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...
    @overload
    def __init__(self, p: str, t: OptStr = None, v: abc.OptCellValue = None, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, p: str, t: OptStr = None, v: abc.OptCellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...

    @overload
    def edit(self, param: str = None, type: OptStr = None, value: abc.OptCellValue = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, param: str = None, type: OptStr = None, value: abc.OptCellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, p: str = None, t: OptStr = None, v: abc.OptCellValue = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, p: str = None, t: OptStr = None, v: abc.OptCellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    # fmt: on

class MapRow(abc.Row):
    key: str
    value: abc.CellValue

    @property
    def k(self) -> str: ...
    @k.setter
    def k(self, key: str) -> None: ...
    @property
    def v(self) -> abc.CellValue: ...
    @v.setter
    def v(self, value: abc.CellValue) -> None: ...
    def __is_pair(self, args: t.Any) -> bool: ...

    # fmt: off
    @overload
    def __init__(self, input: Pair) -> None: ...
    @overload
    def __init__(self, key: str, value: abc.CellValue, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, key: str, value: abc.CellValue, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...
    @overload
    def __init__(self, k: str, v: abc.CellValue, _strict: bool = True) -> None: ...
    @overload
    def __init__(self, k: str, v: abc.CellValue, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> None: ...

    @overload
    def edit(self, input: Pair) -> Self: ...
    @overload
    def edit(self, key: str = None, value: abc.CellValue = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, key: str = None, value: abc.CellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, k: str = None, v: abc.CellValue = None, _strict: bool = True) -> Self: ...  # type: ignore
    @overload
    def edit(self, k: str = None, v: abc.CellValue = None, _strict: t.Literal[False] = False, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    @overload
    def edit(self, **kwargs: abc.OptCellValue) -> Self: ...  # type: ignore
    # fmt: on

class List(abc.List[ListRow]):
    _row_type = ListRow
    is_root: bool
    type: str
    def __init__(self, is_root: bool = False, type: OptStr = None) -> None: ...

    # fmt: off
    @overload
    def add(self, value: abc.CellValue, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def add(self, v: abc.CellValue, vis: OptStr = None, n: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def add(self, input: str) -> t.Union[t.List[ListRow], ListRow]: ...
    @overload
    def add(self, input: t.Union[abc.DictWrapped, ListRow]) -> ListRow: ...
    @overload
    def add(self, *input: abc.AllRowInputs[ListRow]) -> t.List[ListRow]: ...  # type: ignore

    @overload
    def insert(self, key: t.SupportsIndex, value: abc.CellValue, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def insert(self, key: t.SupportsIndex, v: abc.CellValue, vis: OptStr = None, n: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def insert(self, key: t.SupportsIndex, input: str) -> t.Union[t.List[ListRow], ListRow]: ...  # type: ignore
    @overload
    def insert(self, key: t.SupportsIndex, input: t.Union[abc.DictWrapped, ListRow]) -> ListRow: ...
    @overload
    def insert(self, key: t.SupportsIndex, *input: abc.AllRowInputs[ListRow]) -> t.List[ListRow]: ...  # type: ignore

    @overload
    def replace(self, key: abc.ItemKey, value: abc.CellValue, visibility: OptStr = None, namespace: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def replace(self, key: abc.ItemKey, v: abc.CellValue, vis: OptStr = None, n: OptStr = None, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def replace(self, key: abc.ItemKey, input: str) -> t.Union[t.List[ListRow], ListRow]: ...  # type: ignore
    @overload
    def replace(self, key: abc.ItemKey, input: t.Union[abc.DictWrapped, ListRow]) -> ListRow: ...
    @overload
    def replace(self, key: abc.ItemKey, *input: abc.AllRowInputs[ListRow]) -> t.List[ListRow]: ...  # type: ignore

    @overload
    def by_namespace(self, namespace: str) -> ListRow: ...
    @overload
    def by_namespace(self, namespace: str, strict: t.Literal[True]) -> ListRow: ...
    @overload
    def by_namespace(self, namespace: str, strict: bool = True) -> t.Optional[ListRow]: ...
    by_name = by_namespace
    by_n = by_namespace

    @overload
    def remove_by_namespace(self, namespace: str) -> ListRow: ...
    @overload
    def remove_by_namespace(self, namespace: str, strict: t.Literal[True]) -> ListRow: ...
    @overload
    def remove_by_namespace(self, namespace: str, strict: bool = True) -> t.Optional[ListRow]: ...
    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace
    # fmt: on

class Object(abc.List[MemberRow]):
    _row_type = MemberRow
    type: str
    def __init__(self, type: OptStr = None) -> None: ...

    # fmt: off
    @overload
    def by_namespace(self, namespace: str) -> MemberRow: ...
    @overload
    def by_namespace(self, namespace: str, strict: t.Literal[True]) -> MemberRow: ...
    @overload
    def by_namespace(self, namespace: str, strict: bool = True) -> t.Optional[MemberRow]: ...
    by_name = by_namespace
    by_n = by_namespace

    @overload
    def remove_by_namespace(self, namespace: str) -> MemberRow: ...
    @overload
    def remove_by_namespace(self, namespace: str, strict: t.Literal[True]) -> MemberRow: ...
    @overload
    def remove_by_namespace(self, namespace: str, strict: bool = True) -> t.Optional[MemberRow]: ...
    remove_by_name = remove_by_namespace
    rm_n = remove_by_namespace

    @overload
    def by_member(self, member: str) -> MemberRow: ...
    @overload
    def by_member(self, member: str, strict: t.Literal[True]) -> MemberRow: ...
    @overload
    def by_member(self, member: str, strict: bool = True) -> t.Optional[MemberRow]: ...
    by_m = by_member

    @overload
    def remove_by_member(self, member: str) -> MemberRow: ...
    @overload
    def remove_by_member(self, member: str, strict: t.Literal[True]) -> MemberRow: ...
    @overload
    def remove_by_member(self, member: str, strict: bool = True) -> t.Optional[MemberRow]: ...
    rm_m = remove_by_member
    # fmt: on

class Template(Object):
    _row_type = MemberRow
    params: Params
    def __init__(self, type: OptStr = None) -> None: ...

class Params(abc.List[ParamRow]):
    _row_type = ParamRow

    # fmt: off
    @overload
    def by_param(self, param: str) -> ParamRow: ...
    @overload
    def by_param(self, param: str, strict: t.Literal[True]) -> ParamRow: ...
    @overload
    def by_param(self, param: str, strict: bool = True) -> t.Optional[ParamRow]: ...
    by_p = by_param

    @overload
    def remove_by_param(self, param: str) -> ParamRow: ...
    @overload
    def remove_by_param(self, param: str, strict: t.Literal[True]) -> ParamRow: ...
    @overload
    def remove_by_param(self, param: str, strict: bool = True) -> t.Optional[ParamRow]: ...
    rm_m = remove_by_param
    # fmt: on

class Map(abc.List[MapRow]):
    _row_type = MapRow

    # fmt: off
    @overload
    def add(self, key: str, value: abc.CellValue, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def add(self, k: str, v: abc.CellValue, _strict: bool = True, **kwargs: abc.OptCellValue) -> ListRow: ...
    @overload
    def add(self, input: str) -> t.Union[t.List[MapRow], MapRow]: ...
    @overload
    def add(self, input: t.Union[abc.DictWrapped, MapRow, Pair]) -> MapRow: ...
    @overload
    def add(self, *input: abc.AllRowInputs[MapRow]) -> t.List[MapRow]: ...  # type: ignore

    @overload
    def by_key(self, key: str) -> MapRow: ...
    @overload
    def by_key(self, key: str, strict: t.Literal[True]) -> MapRow: ...
    @overload
    def by_key(self, key: str, strict: bool = True) -> t.Optional[MapRow]: ...
    by_k = by_key

    @overload
    def remove_by_key(self, key: str) -> MapRow: ...
    @overload
    def remove_by_key(self, key: str, strict: t.Literal[True]) -> MapRow: ...
    @overload
    def remove_by_key(self, key: str, strict: bool = True) -> t.Optional[MapRow]: ...
    rm_k = remove_by_key
    # fmt: on

