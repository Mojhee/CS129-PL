"""
IOL Grammar and Predictive Parsing Table.

This module defines the grammar of the IOL language using the PE03
Production, Productions, and ParseTable data structures.

The grammar is used by the predictive parser during syntax analysis.
All grammar rules and parsing-table entries are defined directly
in Python so that no external .prod or .ptbl files are required.
"""

# Import the grammar structures from the reused PE03 implementation.
from models import EMPTY, END_MARKER, Production, Productions, ParseTable


# ============================================================
# TERMINALS
# ============================================================
TERMINALS = [
    "IOL",
    "LOI",
    "INT",
    "IDENT",
    "STR",
    "INTO",
    "IS",
    "BEG",
    "PRINT",
    "NEWLN",
    "INT_LIT",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
    END_MARKER,
]


# ============================================================
# NONTERMINALS
# ============================================================
NONTERMINALS = [
    "program",
    "stmts",
    "stmt",
    "init",
    "expr",
]


# ============================================================
# PRODUCTIONS
# ============================================================
PRODUCTION_ITEMS = {
    # program -> IOL stmts LOI
    1: Production(1, "program", ["IOL", "stmts", "LOI"]),

    # stmts -> stmt stmts
    2: Production(2, "stmts", ["stmt", "stmts"]),

    # stmts -> e
    3: Production(3, "stmts", [EMPTY]),

    # Statements
    4: Production(4, "stmt", ["INT", "IDENT", "init"]),
    5: Production(5, "stmt", ["STR", "IDENT", "init"]),
    6: Production(6, "stmt", ["INTO", "IDENT", "IS", "expr"]),
    7: Production(7, "stmt", ["BEG", "IDENT"]),
    8: Production(8, "stmt", ["PRINT", "expr"]),
    9: Production(9, "stmt", ["NEWLN"]),

    # Initializer
    10: Production(10, "init", ["IS", "expr"]),
    11: Production(11, "init", [EMPTY]),

    # Expressions
    12: Production(12, "expr", ["IDENT"]),
    13: Production(13, "expr", ["INT_LIT"]),
    14: Production(14, "expr", ["ADD", "expr", "expr"]),
    15: Production(15, "expr", ["SUB", "expr", "expr"]),
    16: Production(16, "expr", ["MULT", "expr", "expr"]),
    17: Production(17, "expr", ["DIV", "expr", "expr"]),
    18: Production(18, "expr", ["MOD", "expr", "expr"]),
}


# ============================================================
# PRODUCTIONS OBJECT
# ============================================================
PRODUCTIONS = Productions(
    "iol.prod",
    PRODUCTION_ITEMS,
    "program"
)


# ============================================================
# PREDICTIVE PARSING TABLE
# ============================================================
CELLS = {
    # --------------------------------------------------------
    # program -> IOL stmts LOI
    # --------------------------------------------------------
    ("program", "IOL"): 1,

    # --------------------------------------------------------
    # stmts -> stmt stmts
    # --------------------------------------------------------
    ("stmts", "INT"): 2,
    ("stmts", "STR"): 2,
    ("stmts", "INTO"): 2,
    ("stmts", "BEG"): 2,
    ("stmts", "PRINT"): 2,
    ("stmts", "NEWLN"): 2,

    # --------------------------------------------------------
    # stmts -> e
    # --------------------------------------------------------
    ("stmts", "LOI"): 3,

    # --------------------------------------------------------
    # stmt productions
    # --------------------------------------------------------
    ("stmt", "INT"): 4,
    ("stmt", "STR"): 5,
    ("stmt", "INTO"): 6,
    ("stmt", "BEG"): 7,
    ("stmt", "PRINT"): 8,
    ("stmt", "NEWLN"): 9,

    # --------------------------------------------------------
    # init -> IS expr
    # --------------------------------------------------------
    ("init", "IS"): 10,

    # --------------------------------------------------------
    # init -> e (optional initializer)
    #
    # After INT IDENT or STR IDENT, an initializer may be
    # omitted when the next token begins another statement
    # or when the program reaches LOI.
    # --------------------------------------------------------
    ("init", "INT"): 11,
    ("init", "STR"): 11,
    ("init", "INTO"): 11,
    ("init", "BEG"): 11,
    ("init", "PRINT"): 11,
    ("init", "NEWLN"): 11,
    ("init", "LOI"): 11,

    # --------------------------------------------------------
    # expr productions
    # --------------------------------------------------------
    ("expr", "IDENT"): 12,
    ("expr", "INT_LIT"): 13,
    ("expr", "ADD"): 14,
    ("expr", "SUB"): 15,
    ("expr", "MULT"): 16,
    ("expr", "DIV"): 17,
    ("expr", "MOD"): 18,
}


# ============================================================
# PARSE TABLE OBJECT
# ============================================================
TABLE = ParseTable(
    "iol.ptbl",
    TERMINALS,
    NONTERMINALS,
    CELLS
)


# ============================================================
# STANDALONE GRAMMAR COMPATIBILITY TEST
# ============================================================
if __name__ == "__main__":
    from loaders import check_compatible

    print(check_compatible(PRODUCTIONS, TABLE))