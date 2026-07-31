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


DictWrapped = Dict[str, Any]
ConverterReturn = Union[DictWrapped, str]
Processor = Callable[[ts.Node, "ConverterContext", int], DictWrapped]
Processors = Dict[str, Processor]

MAX_DEPTH: int = 0xFF_FF_FF_FF  # technically not max but deep enough for parsing

class ConverterContext:
    def __init__(self, max_depth: int, processors: Processors, terminator: Processor):
        self.max_depth: int = max_depth
        self.processors: Processors = processors
        self.terminator: Processor = terminator


# ============================= Utilities ==============================

def field(node: ts.Node, field: str) -> ts.Node:
    return node.child_by_field_name(field)  # type: ignore


def is_ignored(node: ts.Node) -> bool:
    return node.type in IGNORE


def unignored_children(root_node: ts.Node) -> Iterator[ts.Node]:
    for child in root_node.named_children:
        if child.type not in IGNORE:
            yield child


# ============================= Converters =============================

# parsers
def convert(node: ts.Node, context: ConverterContext) -> md.List:
    result = md.List(is_root=True)
    for child_node in unignored_children(node):
        child: DictWrapped = find_converter(child_node, context, 0)
        result.add(**child)
    return result


def find_converter(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    if (depth >= context.max_depth) \
    or (node.type not in context.processors):
        return context.terminator(node, context, depth)
    return context.processors[node.type](node, context, depth + 1)


def visibility(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "item"), context, depth)
    res_node["visibility"] = field(node, "type").text.decode()
    return res_node


def unnamed(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "object"), context, depth)
    res_node["visibility"] = "unnamed"
    return res_node


def assignment(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "value"), context, depth)
    res_node["namespace"] = field(node, "name").text.decode()
    return res_node


def conv_object(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    result = md.Object()
    result.type = field(node, "type").text.decode()
    members = field(node, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = find_converter(child_node, context, depth)
            result.add(**child)
    return {"value": result}


def template(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    result = md.Template()
    obj = field(node, "value")
    result.type = field(obj, "type").text.decode()
    namespace = field(node, "name").text.decode()
    members = field(obj, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = find_converter(child_node, context, depth)
            result.add(**child)
    params = field(node, "params")
    if params:
        for child_node in unignored_children(params):
            child: DictWrapped = find_converter(child_node, context, depth)
            result.params.add(**child)
    return {"value": result, "namespace": namespace}


def _member_or_param(node: ts.Node, context: ConverterContext, depth: int) -> Tuple[str, DictWrapped]:
    name = field(node, "name").text.decode()
    res_node: DictWrapped = {}
    type = node.child_by_field_name("type")
    if type:
        res_node["type"] = type.text.decode()
    value_node = node.child_by_field_name("value")
    if value_node:
        res_node.update(find_converter(value_node, context, depth))
    return (name, res_node)


def member(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    name, res_node = _member_or_param(node, context, depth)
    res_node["member"] = name
    return res_node


def param(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    name, res_node = _member_or_param(node, context, depth)
    res_node["param"] = name
    return res_node


def conv_list(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    result = md.List()
    n_type = node.type
    if n_type == "vector_type":
        result.type = field(node, "type").text.decode()
    items = node.child_by_field_name("items")
    if items is not None:
        for child_node in unignored_children(items):
            child: DictWrapped = find_converter(child_node, context, depth)
            result.add(**child)
    return {"value": result}


def conv_map(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    result = md.Map()
    pairs = field(node, "pairs")
    if pairs:
        for child in unignored_children(pairs):
            result.add(md.MapRow(*pair(child, context, depth)["value"]))
    return {"value": result}


def pair(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    return {
        "value": (
            find_converter(field(node, "left"), context, depth)["value"],
            find_converter(field(node, "right"), context, depth)["value"],
        )
    }


def expr_unary(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    return {"value": md.ExprUnary(
        find_converter(field(node, "right"), context, depth)["value"],
        field(node, "operator").text.decode(),
    )}


def expr_binary(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    return {"value": md.ExprBinary(
        find_converter(field(node, "left"), context, depth)["value"],
        find_converter(field(node, "right"), context, depth)["value"],
        field(node, "operator").text.decode(),
    )}



def expr_ternary(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    return {"value": md.ExprTernary(
        find_converter(field(node, "cond"), context, depth)["value"],
        find_converter(field(node, "true"), context, depth)["value"],
        find_converter(field(node, "false"), context, depth)["value"],
    )}


def group(node: ts.Node, context: ConverterContext, depth: int) -> DictWrapped:
    result = find_converter(field(node, "item"), context, depth)
    v = result["value"]
    if isinstance(v, abc.Expression):
        v.grouped = True
    return result


def unparsed_expression(node: ts.Node, context: ConverterContext, depth: int):
    return {"value": md.UnparsedExpression(node.text.decode(), tree_ref=node)}


IGNORE: List[str] = [
    "comment_inline",
    "comment_block_classic",
    "comment_block_round",
    "comment_block_curly",
]

PROCESSORS: Processors = {
    "visibility": visibility,
    "builtin_vector_type": conv_list,
    "vector_type": conv_list,
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
    "unary_expression": expr_unary,
    "binary_expression": expr_binary,
    "ternary": expr_ternary,
    "group": group,
}

# Default parser setup used since 0.10, used as main parser for
# backwards compatibility.
context_basic = ConverterContext(MAX_DEPTH, PROCESSORS, unparsed_expression)

# Extended parser that parses everything (except comments).
context_all = ConverterContext(MAX_DEPTH, PROCESSORS_ALL, unparsed_expression)

# Variation of the extended parser, parses one step deep,
# for finer control.
context_step = ConverterContext(1, PROCESSORS_ALL, unparsed_expression)

__all__ = ["convert", "find_converter", "DictWrapped"]


from . import model as md
from .model import abc