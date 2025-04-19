from __future__ import annotations
from typing import (
    Dict,
    Any,
    Callable,
    Tuple,
    List,
    Union,
    Iterator,
)  # , Optional, TYPE_CHECKING
import tree_sitter as ts
from . import model as md


DictWrapped = Dict[str, Any]
ConverterReturn = Union[DictWrapped, str]
Processor = Callable[[ts.Node], DictWrapped]


def field(node: ts.Node, field: str) -> ts.Node:
    return node.child_by_field_name(field)  # type: ignore


def is_ignored(node: ts.Node) -> bool:
    return node.type in IGNORE


def unignored_children(root_node: ts.Node) -> Iterator[ts.Node]:
    for child in root_node.named_children:
        if child.type not in IGNORE:
            yield child


def find_converter(node: ts.Node) -> DictWrapped:
    if node.type in PROCESSORS:
        return PROCESSORS[node.type](node)
    else:
        return {"value": node.text.decode()}


# parsers
def convert(node: ts.Node) -> md.List:
    result = md.List(is_root=True)
    for child_node in unignored_children(node):
        child: DictWrapped = find_converter(child_node)
        result.add(**child)
    return result


def visibility(node: ts.Node) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "item"))
    res_node["visibility"] = field(node, "type").text.decode()
    return res_node


def unnamed(node: ts.Node) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "object"))
    res_node["visibility"] = "unnamed"
    return res_node


def assignment(node: ts.Node) -> DictWrapped:
    res_node: DictWrapped = find_converter(field(node, "value"))
    res_node["namespace"] = field(node, "name").text.decode()
    return res_node


def conv_object(node: ts.Node) -> DictWrapped:
    result = md.Object()
    result.type = field(node, "type").text.decode()
    members = field(node, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = find_converter(child_node)
            result.add(**child)
    return {"value": result}


def template(node: ts.Node) -> DictWrapped:
    result = md.Template()
    obj = field(node, "value")
    result.type = field(obj, "type").text.decode()
    namespace = field(node, "name").text.decode()
    members = field(obj, "members")
    if members:
        for child_node in unignored_children(members):
            child: DictWrapped = find_converter(child_node)
            result.add(**child)
    params = field(node, "params")
    if params:
        for child_node in unignored_children(params):
            child: DictWrapped = find_converter(child_node)
            result.params.add(**child)
    return {"value": result, "namespace": namespace}


def _member_or_param(node: ts.Node) -> Tuple[str, DictWrapped]:
    name = field(node, "name").text.decode()
    res_node: DictWrapped = {}
    type = node.child_by_field_name("type")
    if type:
        res_node["type"] = type.text.decode()
    value_node = node.child_by_field_name("value")
    if value_node:
        res_node.update(find_converter(value_node))
    return (name, res_node)


def member(node: ts.Node) -> DictWrapped:
    name, res_node = _member_or_param(node)
    res_node["member"] = name
    return res_node


def param(node: ts.Node) -> DictWrapped:
    name, res_node = _member_or_param(node)
    res_node["param"] = name
    return res_node


def conv_list(node: ts.Node) -> DictWrapped:
    result = md.List()
    n_type = node.type
    if n_type == "vector_type":
        result.type = field(node, "type").text.decode()
    items = node.child_by_field_name("items")
    if items is not None:
        for child_node in unignored_children(items):
            child: DictWrapped = find_converter(child_node)
            result.add(**child)
    return {"value": result}


def conv_map(node: ts.Node) -> DictWrapped:
    result = md.Map()
    pairs = field(node, "pairs")
    if pairs:
        for child in unignored_children(pairs):
            result.add(md.MapRow(*pair(child)["value"]))
    return {"value": result}


def pair(node: ts.Node) -> DictWrapped:
    return {
        "value": (
            find_converter(field(node, "left"))["value"],
            find_converter(field(node, "right"))["value"],
        )
    }


IGNORE: List[str] = [
    "comment_inline",
    "comment_block_classic",
    "comment_block_round",
    "comment_block_curly",
]

PROCESSORS: Dict[str, Processor] = {
    "visibility": visibility,
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

__all__ = ["convert", "find_converter", "DictWrapped"]
