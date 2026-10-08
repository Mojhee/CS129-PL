"""Shared token names and data structures for the IOL lexical analyzer."""
from dataclasses import dataclass, field

INT_LIT = "INT_LIT"
IDENT = "IDENT"
ERR_LEX = "ERR_LEX"

KEYWORDS = {
    "IOL", "LOI", "INT", "STR", "IS", "INTO", "BEG",
    "PRINT", "ADD", "SUB", "MULT", "DIV", "MOD", "NEWLN",
}
TYPE_KEYWORDS = {"INT", "STR"}


@dataclass
class Lexeme:
    text: str     # the characters as written, e.g. "num1"
    token: str    # INT_LIT, IDENT, ERR_LEX, or the keyword itself
    line: int     # 1-based line number in the source


@dataclass
class Variable:
    name: str     # e.g. "num"
    type: str     # "INT" or "STR"


@dataclass
class CompileResult:
    lexemes: list = field(default_factory=list)     # list[Lexeme]
    variables: list = field(default_factory=list)   # list[Variable]
    token_stream: str = ""                          # contents of the .tkn file
    messages: list = field(default_factory=list)    # console lines
    has_errors: bool = False
    tkn_path: str = ""                              # where the .tkn was saved
