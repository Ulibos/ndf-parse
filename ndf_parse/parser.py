import os
from typing import Optional, Union, List
import tree_sitter as ts

from . import traverser

# 3 places to search for ndf.dll in descending priority order:
# 1. - via env variable NDF_LIB_PATH
lang_path: Optional[str] = os.environ.get("NDF_LIB_PATH", None)
if lang_path is None:
    # 2. - where tree-sitter-cli builds by default
    dev_path = os.path.expanduser(r"~\AppData\Local\tree-sitter\lib\ndf.dll")
    if os.path.exists(dev_path):
        lang_path = dev_path
if lang_path is None:
    # 3. - inside of the package distribution
    lang_path = os.path.join(os.path.dirname(__file__), "bin\\ndf.dll")
    if not os.path.exists(lang_path):
        raise RuntimeError(
            "Could not find ndf.dll in any of default paths. "
            "Please set env variable `NDF_LIB_PATH=path/to/dll` "
            "before running this script."
        )

# kill deprecation warning since we are locked into 0.21 version where
# dll path is a viable argument
ts._deprecate = lambda a, b: ...  # type: ignore
NDF_LANG = ts.Language(lang_path, "ndf")

parser = ts.Parser()
parser.set_language(NDF_LANG)


def parse(
    data: Union[str, bytes], ensure_no_errors: bool = True  # type: ignore
) -> Union[ts.Node, List[ts.Node]]:
    """Converts `string`/`byte` data to a tree sitter tree object.
    Should be used to parse ndf files as a whole.

    Parameters
    ----------
    data : AnyStr
        ndf code to parse.
    ensure_no_errors : bool, default=True
        If True then fail if ndf code contains syntax errors. Be mindful of
        :ref:`checking strictness <checking-strictness>`.

    Returns
    -------
    ~model.List
        Model representation of a file.
    """
    if isinstance(data, str):
        data: bytes = data.encode()
    tree: ts.Node = parser.parse(data).root_node
    if ensure_no_errors:
        errors = traverser.check_tree(tree)
        if errors is not None:
            return errors
    return tree


# utility converters
def _validate_code_(
    code: str,
    wrapper: str = "",
    offset_rows: int = 0,
    extra_error_msg: str = "",
) -> ts.Node:
    if not len(code):
        raise ValueError("Expected ndf code, got empty string.")
    tree = parse(wrapper.format(code=code)) if len(wrapper) else parse(code)
    if isinstance(tree, list):
        traverser.throw_tree_errors(code, tree, offset_rows, extra_error_msg)
    return tree


def entries_root(code: str) -> List[ts.Node]:
    e = "Remember NOT to use commas between root level items, only newlines!\n"
    tree = _validate_code_(code, extra_error_msg=e)
    return tree.children


def entries_list(code: str) -> List[ts.Node]:
    extra_error_msg = "Remember to use commas between list items!\n"
    tree = _validate_code_(code, "[\n{code}\n]", 1, extra_error_msg)
    return tree.children[0].named_children[0].named_children


def entries_member(code: str) -> List[ts.Node]:
    tree = _validate_code_(code, "T(\n{code}\n)", 1)
    return tree.children[0].named_children[1].children


def entries_param(code: str) -> List[ts.Node]:
    extra_error_msg = "Remember to use commas between template params!\n"
    tree = _validate_code_(
        code, "template N[\n{code}\n] is T()", 1, extra_error_msg
    )
    return tree.children[0].named_children[2].named_children


def entries_map(code: str) -> List[ts.Node]:
    tree = _validate_code_(code, "MAP[\n{code}\n]", 1)
    return tree.children[0].named_children[1].named_children


__all__ = ["parse"]
