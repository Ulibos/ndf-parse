from __future__ import annotations
from typing import (
    Tuple,
    List,
    Iterator,
    Dict,
    Any,
    Callable,
    Union,
)
import tree_sitter as ts
from .traverser import traverse


DictWrapped = Dict[str, Any]
ConverterReturn = Union[DictWrapped, str]
Processor = Callable[[ts.Node, "Processor", int], DictWrapped]
Processors = Dict[str, Processor]

MAX_DEPTH: int = 0xFF_FF_FF_FF  # technically not max but deep enough for parsing


# ============================= Utilities ==============================

def field(node: ts.Node, field: str) -> ts.Node:
    return node.child_by_field_name(field)  # type: ignore


def is_ignored(node: ts.Node) -> bool:
    return node.type in IGNORE


def unignored_children(root_node: ts.Node) -> Iterator[ts.Node]:
    for child in root_node.named_children:
        if child.type not in IGNORE:
            yield child


# =========================== Main Converters ==========================

def convert_basic(node: ts.Node, processor: Processor, depth: int = 0):
    """
    Default parser setup used since 0.10, used as main parser for
    backwards compatibility.
    """
    return PROCESSORS.get(node.type, unparsed_expression)(node, convert_basic, depth+1)


def convert_all(node: ts.Node, processor: Processor, depth: int = 0):
    """Extended parser that parses everything (except comments)."""
    return PROCESSORS_ALL.get(node.type, unparsed_expression)(node, convert_all, depth+1)


def convert_expand(node: ts.Node, processor: Processor, depth: int = 0):
    """
    Designed to forecefully expand an expression and continue converting
    in basic mode.
    """
    return PROCESSORS_ALL.get(node.type, unparsed_expression)(node, convert_basic, depth+1)


def convert_exprs(node: ts.Node, processor: Processor, depth: int = 0):
    """
    Designed to work mostly like a basic converter except for expressions that
    have complex types nested within them, those are parsed fully.
    """
    if node.type in ("expression_unary", "expression_binary", "expression_ternary"):
        for n in traverse(node):
            if n.type in ("object", "map", "template", "vector"):
                return PROCESSORS_ALL.get(node.type, unparsed_expression)(node, convert_exprs, depth+1)
    return PROCESSORS.get(node.type, unparsed_expression)(node, convert_exprs, depth+1)


def convert(node: ts.Node, processor: Processor = convert_basic) -> md.List:
    result = md.List(is_root=True)
    for child_node in unignored_children(node):
        child: DictWrapped = processor(child_node, processor, 0)
        result.add(**child)
    return result


# =========================== Type Converters ==========================

def visibility(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    res_node: DictWrapped = processor(field(node, "item"), processor,  depth)
    res_node["visibility"] = field(node, "type").text.decode()
    return res_node


def unnamed(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    res_node: DictWrapped = processor(field(node, "object"), processor,  depth)
    res_node["visibility"] = "unnamed"
    return res_node


def assignment(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    res_node: DictWrapped = processor(field(node, "value"), processor,  depth)
    res_node["namespace"] = field(node, "name").text.decode()
    return res_node


def conv_object(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    result = md.Object()
    result.type = field(node, "type").text.decode()
    members = field(node, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = processor(child_node, processor,  depth)
            result.add(**child)
    return {"value": result}


def template(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    result = md.Template()
    obj = field(node, "value")
    result.type = field(obj, "type").text.decode()
    namespace = field(node, "name").text.decode()
    members = field(obj, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = processor(child_node, processor,  depth)
            result.add(**child)
    params = field(node, "params")
    if params:
        for child_node in unignored_children(params):
            child: DictWrapped = processor(child_node, processor,  depth)
            result.params.add(**child)
    return {"value": result, "namespace": namespace}


def _member_or_param(node: ts.Node, processor: Processor, depth: int) -> Tuple[str, DictWrapped]:
    name = field(node, "name").text.decode()
    res_node: DictWrapped = {}
    type = node.child_by_field_name("type")
    if type:
        res_node["type"] = type.text.decode()
    value_node = node.child_by_field_name("value")
    if value_node:
        res_node.update(processor(value_node, processor,  depth))
    return (name, res_node)


def member(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    name, res_node = _member_or_param(node, processor, depth)
    res_node["member"] = name
    return res_node


def param(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    name, res_node = _member_or_param(node, processor, depth)
    res_node["param"] = name
    return res_node


def conv_list(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    result = md.List()
    n_type = node.type
    if n_type == "vector":
        result.type = field(node, "type").text.decode()
    items = node.child_by_field_name("items")
    if items is not None:
        for child_node in unignored_children(items):
            child: DictWrapped = processor(child_node, processor,  depth)
            result.add(**child)
    return {"value": result}


def conv_map(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    result = md.Map()
    pairs = field(node, "pairs")
    if pairs:
        for child in unignored_children(pairs):
            result.add(md.MapRow(*pair(child, processor, depth)["value"]))
    return {"value": result}


def pair(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    return {
        "value": (
            processor(field(node, "left"), processor,  depth)["value"],
            processor(field(node, "right"), processor,  depth)["value"],
        )
    }


def expr_unary(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    return {"value": md.ExprUnary(
        processor(field(node, "right"), processor,  depth)["value"],
        field(node, "operator").text.decode(),
    )}


def expr_binary(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    return {"value": md.ExprBinary(
        processor(field(node, "left"), processor,  depth)["value"],
        processor(field(node, "right"), processor,  depth)["value"],
        field(node, "operator").text.decode(),
    )}



def expr_ternary(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    return {"value": md.ExprTernary(
        processor(field(node, "cond"), processor,  depth)["value"],
        processor(field(node, "true"), processor,  depth)["value"],
        processor(field(node, "false"), processor,  depth)["value"],
    )}


def group(node: ts.Node, processor: Processor, depth: int) -> DictWrapped:
    result = processor(field(node, "item"), processor,  depth)
    v = result["value"]
    if isinstance(v, abc.Expression):
        v.grouped = True
    return result


def unparsed_expression(node: ts.Node, processor: Processor, depth: int):
    return {"value": node.text.decode()}


IGNORE: List[str] = [
    "comment_inline",
    "comment_block_classic",
    "comment_block_round",
    "comment_block_curly",
]

PROCESSORS: Processors = {
    "visibility": visibility,
    "builtin_vector_type": conv_list,
    "vector": conv_list,
    "assignment": assignment,
    "template": template,
    "object": conv_object,
    "param": param,
    "member": member,
    "map": conv_map,
    "list": conv_list,
    "pair": pair,
    "unnamed": unnamed,
}

PROCESSORS_ALL: Processors = PROCESSORS | {
    "expression_unary": expr_unary,
    "expression_binary": expr_binary,
    "expression_ternary": expr_ternary,
    "group": group,
}


__all__ = [
    "DictWrapped",
    "Processor",
    "convert",
    "convert_basic",
    "convert_all",
    "convert_expand",
    "convert_exprs",
]


from . import model as md
from .model import abc