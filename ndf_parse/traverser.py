from typing import Union, Iterator, List
import tree_sitter as ts

def ensure_node(tree: Union[ts.Node, ts.Tree])->ts.Node:
    if isinstance(tree, ts.Node):
        return tree
    else:
        return tree.root_node

def traverse(node: ts.Node)->Iterator[ts.Node]:
    yield node
    for child in node.children:
        for inner in traverse(child):
            yield inner

def check_tree(node: ts.Node):
    errors: List[ts.Node] = []
    for node in traverse(node):
        if node.type in ('ERROR', 'MISSING'):
            errors.append(node)
    if len(errors):
        raise SyntaxError(f"Bad ndf code:\n"+'\n'.join(str(x) for x in errors))