
"""Shared definitions for the non-recursive predictive parser (PE03)."""

from dataclasses import dataclass, field

# Special grammar and parsing symbols
EMPTY = "e"               # empty symbol in .prod files (represents ε)
END_MARKER = "$"          # input right end marker in .ptbl files
CURLY_QUOTES = {
    "’": "'",             # convert right curly apostrophe to a plain apostrophe
    "‘": "'",             # convert left curly apostrophe to a plain apostrophe
}


class FileFormatError(Exception):
    """A .prod or .ptbl file cannot be used. str(error) is shown to the user."""


def normalize_symbol(text: str) -> str:
    """Strip spaces around text and turn curly apostrophes into a plain '."""
    # MODIFIED: Added type annotation to specify that the function accepts and returns a string.
    for curly, plain in CURLY_QUOTES.items():
        text = text.replace(curly, plain)

    return text.strip()


@dataclass
class Production:
    """Represents one production rule in the grammar."""

    number: int         # first column, e.g. 2
    head: str           # non-terminal on the left side, e.g. "E'"
    body: list[str]     # MODIFIED: Added element type annotation to specify that the production body contains strings, e.g. ["+", "T", "E'"]; ["e"] if empty


@dataclass
class Productions:
    """Stores all production rules loaded from a .prod file."""

    path: str                  # full path of the .prod file
    items: dict[int, Production]  # MODIFIED: Added type annotations to specify that production numbers (int) map to Production objects
    start_symbol: str          # head of the first production in the file; starting non-terminal


@dataclass
class ParseTable:
    """Stores the predictive parsing table loaded from a .ptbl file."""

    path: str                          # full path of the .ptbl file
    terminals: list[str]               # MODIFIED: Added element type annotation to specify that the list contains terminal symbols in header order, including "$"
    nonterminals: list[str]            # MODIFIED: Added element type annotation to specify that the list contains non-terminal symbols in row order
    cells: dict[tuple[str, str], int]  # MODIFIED: Added type annotations to specify that each key is a (non-terminal, terminal) pair and its value is a production number


@dataclass
class ParseStep:
    """Stores one step or snapshot of the predictive parsing process."""

    stack: str          # current parser stack, e.g. "T E' $" (top of the stack is on the left)
    buffer: str         # remaining input symbols, e.g. "id + id * id $"
    action: str = ""    # MODIFIED: Added a default empty string so the action can be omitted when creating the initial parsing step


@dataclass
class ParseResult:
    """Stores the final result and parsing trace for an input string."""

    valid: bool                         # True if the input is accepted; False otherwise
    steps: list[ParseStep] = field(default_factory=list)  # MODIFIED: Added element type annotation to specify that the list contains ParseStep objects
    error: str = ""                     # reason for rejection; empty if valid
