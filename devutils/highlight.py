from __future__ import annotations
import typing as t
from collections.abc import Iterator
import re
import tree_sitter as ts
from pygments.lexer import Lexer
from pygments import token
import ndf_parse

parser = ndf_parse.parser.parser

# =================== typing ===================
TokenType = token._TokenType  # type: ignore
LexerOutput = t.Iterable[t.Tuple[int, TokenType, str]]
ConsumerIterable = t.Iterable[
    t.Tuple[TokenType, int, int]
]  # (token type, start, end)
TokensConsumer = t.Callable[[ts.Node], ConsumerIterable]


# =================== functions ===================
def get_next(c: ts.TreeCursor):
    c.goto_descendant(c.descendant_index() + 1)
    return c.depth != 0


def format_consumer(tree: ts.Tree, consumer: ConsumerIterable) -> LexerOutput:
    for ttype, start, end in consumer:
        yield start, ttype, tree.text[start:end].decode()


# =========== token type processors ============
def guid(node: ts.Node) -> ConsumerIterable:
    start_pos = node.byte_range[0]
    hex_pos = start_pos + 6
    bracket_pos = hex_pos + 36
    yield token.Name.Decorator, start_pos, hex_pos
    yield token.Literal.GUID, hex_pos, bracket_pos
    yield token.Name.Decorator, bracket_pos, bracket_pos + 1


def string(node: ts.Node) -> ConsumerIterable:
    quote_node = node.children[0]
    if quote_node.type == "'":
        yield token.String.Single, *node.byte_range
    else:
        yield token.String.Double, *node.byte_range


def simple_consumer(type: TokenType) -> TokensConsumer:
    def cons(node: ts.Node) -> ConsumerIterable:
        yield type, *node.byte_range

    return cons


def whitespaces(tree: ts.Tree, start: int, end: int) -> ConsumerIterable:
    cursor = start
    consumed = start
    while cursor < end:
        cursor = tree.text.find(b"\n", cursor, end)
        if cursor == -1:
            yield token.Token.Text, consumed, end
            return
        if cursor > consumed:
            yield token.Token.Text, consumed, cursor
        yield token.Whitespace, cursor, cursor + 1
        cursor = consumed = cursor + 1


# =================== consts ===================
WS = re.compile("\\s+$")

TOKENS_MAP: t.Dict[str, TokenType] = {
    "[": token.Punctuation,
    "]": token.Punctuation,
    "{": token.Punctuation,
    "}": token.Punctuation,
    ":": token.Punctuation,
    ",": token.Punctuation,
    "(": token.Punctuation,
    ")": token.Punctuation,
    ".": token.Punctuation,
    "keyword": token.Keyword,
    "builtin_type": token.Name.Builtin,
    "nil": token.Name.Builtin.Pseudo,
    "builtin_vector_type": token.Name.Builtin,
    "name": token.Name,
    "number_dec": token.Number.Integer,
    "number_float": token.Number.Float,
    "operator": token.Operator,
    "=": token.Operator,
    "type": token.Keyword.Type,
    "comment_inline": token.Comment.Single,
    "ref_scope": token.String.Regex,
    "ref_terminal": token.String.Regex,
}

CONSUMERS_MAP: t.Dict[str, TokensConsumer] = {
    "comment_block_classic": simple_consumer(token.Comment.Multiline),
    "comment_block_round": simple_consumer(token.Comment.Multiline),
    "comment_block_classic": simple_consumer(token.Comment.Multiline),
    "guid": guid,
    "string": string,
    "type": simple_consumer(token.Keyword.Type),
    "builtin_type": simple_consumer(token.Keyword.Type),
    "builtin_vector_type": simple_consumer(token.Keyword.Type),
}


class NdfLexer(Lexer):
    def get_tokens_unprocessed(
        self, text: str
    ) -> "Iterator[tuple[int, TokenType, str]]":
        tree: ts.Tree = parser.parse(text.encode())
        c = tree.walk()
        last_end = 0
        while get_next(c):
            n = c.node
            # deal with whitespace
            s, e = n.byte_range
            if s > last_end:
                # process multiline comments
                yield from format_consumer(tree, whitespaces(tree, last_end, s))
            # type-based tokens
            if n.type in CONSUMERS_MAP:
                yield from format_consumer(tree, CONSUMERS_MAP[n.type](n))
                c.goto_first_child_for_byte(e)
            # skip non-leaf tokens
            elif len(n.children):
                pass
            # process leaf tokens
            elif n.type in TOKENS_MAP:
                yield s, TOKENS_MAP[n.type], n.text.decode()
            else:
                print(f">>> {n.type} <<<")
                yield s, token.Token.Text, n.text.decode()

            last_end = c.node.byte_range[1]

            # safeguard
            if c.depth == 0:
                break


__all__ = ["NdfLexer"]
