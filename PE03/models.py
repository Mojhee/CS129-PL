"""Shared definitions for the non-recursive predictive parser (PE03)."""
from dataclasses import dataclass, field

EMPTY = "e"               # empty symbol in .prod files
END_MARKER = "$"          # input right end marker in .ptbl files
CURLY_QUOTES = {"’": "'", "‘": "'"}


class FileFormatError(Exception):
    """A .prod or .ptbl file cannot be used. str(error) is shown to the user."""


def normalize_symbol(text):
    """Strip spaces around text and turn curly apostrophes into a plain '."""
    for curly, plain in CURLY_QUOTES.items():
        text = text.replace(curly, plain)
    return text.strip()


@dataclass
class Production:
    number: int         # first column, e.g. 2
    head: str           # non-terminal, e.g. "E'"
    body: list          # list[str], e.g. ["+", "T", "E'"]; ["e"] if empty


@dataclass
class Productions:
    path: str           # full path of the .prod file
    items: dict         # dict[int, Production], keyed by number, file order
    start_symbol: str   # head of the first production in the file


@dataclass
class ParseTable:
    path: str           # full path of the .ptbl file
    terminals: list     # list[str] in header order; includes "$"
    nonterminals: list  # list[str] in row order
    cells: dict         # dict[(non-terminal, terminal), int]; blanks left out


@dataclass
class ParseStep:
    stack: str          # e.g. "T E' $"  (top of the stack on the left)
    buffer: str         # e.g. "id + id * id $"
    action: str         # e.g. "Output E > T E'", "Match id", "" (first row)


@dataclass
class ParseResult:
    valid: bool
    steps: list = field(default_factory=list)   # list[ParseStep]
    error: str = ""                             # reason when not valid
