"""This module is responsible for converting data represented as a tree of
:mod:`~ndf_parse.model` classes. It exposes 3 main functions that should
cover most of user's needs.
"""

from __future__ import annotations
import typing as t
import sys
import io
from . import model as md


Tree = t.Union[md.abc.CellValue, md.abc.Row, t.Tuple[t.Any, t.Any]]
AnyPrinter = t.Callable[["State", t.Any], None]


#  high level
def format(tree: Tree, handle: t.TextIO):
    """format(data, handle)
    Wtire model tree as an ndf code to a given IO writer.

    .. doctest::

        >>> from ndf_parse.printer import format as ndf_format
        >>> from ndf_parse import convert
        >>> from io import StringIO
        >>> stream = StringIO()
        >>> stream.write("Here is a streamed in ndf code:\\n\\n")
        33
        >>> ndf_format(convert("A is Obj(memb1 = 12)"), stream)
        >>> print(stream.getvalue())
        Here is a streamed in ndf code:
        <BLANKLINE>
        A is Obj
        (
            memb1 = 12
        )

    Parameters
    ----------
    data : :data:`~ndf_parse.model.abc.CellValue`
        Model tree.
    handle : TextIO
        String IO handle to write into.
    """
    state = State(handle)
    parse(state, tree)
    state.write_line("")


def print(tree: Tree):
    """print(data)
    Print model tree as an ndf code to stdout.

    .. doctest::

        >>> from ndf_parse.printer import print as ndf_print
        >>> from ndf_parse import convert
        >>> ndf_print(convert("export    A is Obj(memb=12)"))  # note formatting
        export A is Obj
        (
            memb = 12
        )

    Parameters
    ----------
    data : :data:`~ndf_parse.model.abc.CellValue`
        Model tree.
    """
    handle = sys.stdout
    format(tree, handle)


def string(tree: Tree):
    """string(data)
    Return model tree represented as a formatted ndf code in a string.

    .. doctest::

        >>> from ndf_parse.printer import string as ndf_string
        >>> from ndf_parse import convert
        >>> code = ndf_string(convert("export    A is Obj(memb=12)"))  # note formatting
        >>> print(code)
        export A is Obj
        (
            memb = 12
        )

    Parameters
    ----------
    data : :data:`~ndf_parse.model.abc.CellValue`
        Model tree.
    """
    handle = io.StringIO()
    format(tree, handle)
    return handle.getvalue()


# helper
class State:
    def __init__(self, io: t.TextIO):
        self.io: t.TextIO = io
        self.indent = 0
        self.indent_token = "    "
        self.line_width = 100

    def write(self, arg: t.Any):
        self.io.write(arg)

    def write_line(self, arg: t.Any):
        self.io.write(f"\n{self.indent_token * self.indent}{arg}")

    def space_left(self):
        return self.line_width - len(self.indent_token) * self.indent


# printers
def _source_file(state: State, source: md.List):
    last_item_idx = len(source) - 1
    wl = state.write_line
    indent = state.indent
    for i, item in enumerate(source):
        root_assignment_printer(state, item)
        state.indent = indent
        if i < last_item_idx:
            wl("")
            wl("")
    wl("")


def _parse_list(state: State, item: md.List):
    w = state.write
    with_newline = is_multiline_needed(state, item)
    if item.type is not None:  # type: ignore
        w(item.type)
    # write
    if len(item):
        print_condensed_or_multiline(
            state, item, parse, "[", "]", ",", with_newline
        )
    else:
        w("[]")


def parse_list(state: State, item: md.List):
    if item.is_root:
        _source_file(state, item)
    else:
        _parse_list(state, item)


def template(state: State, template: md.Template, namespace: str = "_"):
    w = state.write
    w(f"template {namespace}")
    if len(template.params):
        print_condensed_or_multiline(
            state, template.params, param_printer, "[", "]", ",", True
        )
    else:
        w("[]")
    w(f" is ")
    object(state, template)


def object(state: State, obj: md.Object):
    w = state.write
    w(obj.type)
    if len(obj):
        print_condensed_or_multiline(
            state, obj, member_printer, "(", ")", "", True
        )
    else:
        w("()")


def parse_map(state: State, item: md.Map):
    w = state.write
    w("MAP")
    with_newline = is_multiline_needed(state, item)  # type: ignore
    if len(item):
        print_condensed_or_multiline(
            state, item, map_pair_printer, "[", "]", ",", with_newline
        )
    else:
        w("[]")


def pair(state: State, node: t.Tuple[t.Any, t.Any]):
    if len(node) != 2:
        raise ValueError(f"Bad tuple, expected size 2, got {tuple}")
    with_newline = (
        any(isinstance(x, (md.abc.List, tuple)) for x in node)
        or sum(len(str(x)) + 2 for x in node) > state.space_left()
    )
    print_condensed_or_multiline(
        state, node, parse, "(", ")", ",", with_newline
    )


# utils
item_view_columns = set(["namespace", "member", "param", "visibility"])


def is_multiline_needed(state: State, items: md.abc.List[md.abc.Row]) -> bool:
    if len(items):
        item = items[0]
        columns = set(item.full_args_names()) & item_view_columns
        total_len = 0
        for i in items:
            if any((getattr(i, x) is not None for x in columns)):
                return True
            i = i.value  # type: ignore
            # check i for type
            if not isinstance(i, (str, float, int, bool)):
                return True
            total_len += len(str(i)) + 2
        return total_len > state.space_left()
    return False


def root_assignment_printer(state: State, item: md.ListRow):
    w = state.write
    vis, nsp, val = item.visibility, item.namespace, item.value
    if vis is not None:
        w(f"{vis} ")
    if isinstance(val, md.Template):
        assert isinstance(nsp, str), (
            "Template item cannot have it's namespace be equal to None, "
            f"got {item}"
        )
        template(state, val, nsp)
    else:
        if nsp is not None:
            w(f"{nsp} is ")
        parse(state, val)


def param_printer(state: State, param: md.ParamRow):
    w = state.write
    par = param.param
    typ = param.type
    val = param.value
    w(f"{par}")
    if typ is not None:
        w(f": {typ}")
    if val is not None:
        w(f" = ")
        parse(state, val)


def member_printer(state: State, member: md.MemberRow):
    w, indent = state.write, state.indent
    vis = member.visibility
    memb = member.member
    typ = member.type
    namesp = member.namespace
    val = member.value
    # fmt: off
    if memb is not None:
        w(f"{memb}")
        if typ is not None: w(f": {typ}")
        w(' = ')
    if vis    is not None: w(f"{vis} ")
    if namesp is not None: w(f"{namesp} is ")
    parse(state, val) 
    state.indent = indent
    # fmt: on


def itemview_printer(state: State, item: md.abc.Row):
    if isinstance(item, md.ParamRow):
        return param_printer(state, item)
    elif isinstance(item, md.MemberRow):
        return member_printer(state, item)
    elif isinstance(item, md.ListRow):
        return root_assignment_printer(state, item)
    else:
        raise ValueError(f"{item} is not a sublass of model.DeclListRow.")


def map_pair_printer(state: State, item: md.MapRow):
    pair(state, (item.key, item.value))


def print_condensed_or_multiline(
    state: State,
    items: t.Sequence[md.abc.Row],
    item_printer: AnyPrinter,
    open: str = "",
    close: str = "",
    sep: str = ",",
    multiline: bool = False,
):
    w, wl, indent = state.write, state.write_line, state.indent
    if len(items) == 0:
        return

    if multiline:
        wl(open)
        state.indent += 1
        wl("")
        item_printer(state, items[0])
        for item in items[1:]:
            w(sep)
            wl("")
            item_printer(state, item)
        state.indent = indent
        wl(close)
    else:
        w(open)
        item_printer(state, items[0])
        for item in items[1:]:
            w(f"{sep} ")
            item_printer(state, item)
        state.indent = indent
        w(close)


def parse(state: State, item: Tree) -> None:
    n_type = type(item)
    p: t.Optional[AnyPrinter] = NODE_PRINTERS.get(n_type, None)
    if p is None:
        raise KeyError(
            f"No printer found for node of type `{n_type}`, item: {item}"
        )
    return p(state, item)


def default(state: State, item: t.Any):
    state.write(str(item))


NODE_PRINTERS: t.Dict[type, t.Callable[[State, t.Any], None]] = {
    md.Template: template,
    md.Object: object,
    md.Map: parse_map,
    md.ParamRow: param_printer,
    md.MemberRow: member_printer,
    md.ListRow: root_assignment_printer,
    md.List: parse_list,
    tuple: pair,
    str: default,
    float: default,
    int: default,
    bool: default,
}


__all__ = ["print", "format", "string"]
