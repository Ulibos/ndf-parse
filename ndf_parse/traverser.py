import typing as t
import tree_sitter as ts

SHOW_SOURCE_IN_ERROR_LOGS = False

class BadNdfError(Exception): pass

def ensure_node(tree: t.Union[ts.Node, ts.Tree]) -> ts.Node:
    if isinstance(tree, ts.Node):
        return tree
    else:
        return tree.root_node


def traverse(node: ts.Node) -> t.Iterator[ts.Node]:
    yield node
    for child in node.children:
        for inner in traverse(child):
            yield inner


def check_tree(node: ts.Node) -> t.Optional[t.List[ts.Node]]:
    errors: t.List[ts.Node] = []
    for node in traverse(node):
        if node.is_error or node.is_missing:
            errors.append(node)
    if len(errors):
        return errors


def format_tree_errors(errors: t.List[ts.Node], offset_rows: int = 0) -> str:
    msgs: t.List[str] = []
    for i, error in enumerate(errors):
        r, c = error.start_point
        if error.is_missing:
            msgs.append((f"{i}: Unfinished expression at {r-offset_rows}:{c}"))
        else:
            error_msg = error.text.split(b"\n")[0].decode()
            msgs.append(
                (f"{i}: Syntax error at {r-offset_rows}:{c}: {error_msg}")
            )
    return "\n".join(msgs)


def throw_tree_errors(
    data: t.Union[str, bytes],
    errors: t.List[ts.Node],
    offset_rows: int = 0,
    extra_message: str = "",
) -> t.NoReturn:
    errors_str = format_tree_errors(errors, offset_rows)
    msg = f"Errors while parsing expression:\n{extra_message}"
    if SHOW_SOURCE_IN_ERROR_LOGS:
        msg += f"{data}\nErrors:\n"
    raise BadNdfError(f"{msg}{errors_str}")
