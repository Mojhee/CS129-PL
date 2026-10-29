"""Shared token names and data structures for the IOL lexical analyzer."""
from dataclasses import dataclass, field

# Token names. A keyword's token name is the keyword itself (see KEYWORDS).
INT_LIT = "INT_LIT"   # integer literal: one or more digits
IDENT = "IDENT"       # identifier (variable name): a letter, then letters or digits
ERR_LEX = "ERR_LEX"   # error lexeme: any word that is not a valid token

# The 14 IOL keywords. Matching is exact and case-sensitive.
KEYWORDS = {
    "IOL", "LOI", "INT", "STR", "IS", "INTO", "BEG",
    "PRINT", "ADD", "SUB", "MULT", "DIV", "MOD", "NEWLN",
}
# Data type keywords; a type keyword followed by an IDENT defines a variable.
TYPE_KEYWORDS = {"INT", "STR"}


@dataclass
class Lexeme:
    """One word of the source code, created by scan() in lexer.py."""
    text: str     # the characters as written, e.g. "num1"
    token: str    # INT_LIT, IDENT, ERR_LEX, or the keyword itself
    line: int     # 1-based line number in the source


@dataclass
class Variable:
    """One defined variable, created by build_variable_table() in symbol_table.py."""
    name: str     # e.g. "num"
    type: str     # "INT" or "STR"


@dataclass
class CompileResult:
    """Everything one compile produces; returned by compile_code() in compiler.py."""
    lexemes: list = field(default_factory=list)     # list[Lexeme]
    variables: list = field(default_factory=list)   # list[Variable]
    token_stream: str = ""                          # contents of the .tkn file
    messages: list = field(default_factory=list)    # console lines
    has_errors: bool = False
    tkn_path: str = ""                              # where the .tkn was saved
