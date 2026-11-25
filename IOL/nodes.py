
"""
AST (Abstract Syntax Tree) node definitions for the IOL language.

This module defines the data structures used to represent an IOL program
after it has passed lexical and syntax analysis.

The AST allows later compiler stages to work with structured statements
and expressions instead of raw tokens.
"""

# Import dataclass to automatically generate constructors and other
# useful methods for our AST node classes.
from dataclasses import dataclass


# ============================================================
# EXPRESSIONS
# ============================================================
# Expressions are parts of a statement that produce a value.
# IOL expressions include:
#   - Integer literals
#   - Variable references
#   - Arithmetic operations


@dataclass
class IntLit:
    """
    Represents an integer literal.

    Example:
        25

    Attributes:
        value: The numeric value of the literal.
        line: The source line where the literal appears.
    """
    value: int
    line: int


@dataclass
class VarRef:
    """
    Represents a reference to a variable.

    Example:
        x

    Attributes:
        name: The name of the referenced variable.
        line: The source line where the variable is referenced.
    """
    name: str
    line: int


@dataclass
class BinOp:
    """
    Represents a binary arithmetic operation.

    Example:
        ADD x 5

    Attributes:
        op: The operator token (ADD, SUB, MULT, DIV, or MOD).
        left: The left operand.
        right: The right operand.
        line: The source line where the operator appears.
    """
    op: str
    left: "Expr"
    right: "Expr"
    line: int


# ============================================================
# STATEMENTS
# ============================================================
# Statements represent instructions that perform actions.
# IOL statements include variable declarations, assignments,
# input, output, and newline operations.


@dataclass
class Declare:
    """
    Represents a variable declaration.

    Example:
        INT age
        INT age IS 18

    Attributes:
        type_name: The declared type, such as INT or STR.
        name: The declared variable name.
        initializer: Optional expression used to initialize the variable.
        line: The source line of the declaration.
    """
    type_name: str
    name: str
    initializer: "Expr | None"
    line: int


@dataclass
class Assign:
    """
    Represents assignment to an existing variable.

    Example:
        INTO age IS 20

    Attributes:
        name: The variable receiving the value.
        value: The expression assigned to the variable.
        line: The source line of the assignment.
    """
    name: str
    value: "Expr"
    line: int


@dataclass
class Input:
    """
    Represents an input statement.

    Example:
        BEG age

    Attributes:
        name: The variable receiving the input.
        line: The source line of the input statement.
    """
    name: str
    line: int


@dataclass
class Print:
    """
    Represents a print statement.

    Example:
        PRINT age

    Attributes:
        value: The expression being printed.
        line: The source line of the print statement.
    """
    value: "Expr"
    line: int


@dataclass
class NewLine:
    """
    Represents an output newline statement.

    Example:
        NEWLN

    Attributes:
        line: The source line of the statement.
    """
    line: int


# ============================================================
# PROGRAM
# ============================================================
# Program is the root node of the AST.
# It contains the complete list of parsed statements.


@dataclass
class Program:
    """
    Represents a complete IOL source program.

    Attributes:
        name: Name of the source file.
        statements: Statements contained in the program.
        line: Starting line of the program.
    """
    name: str
    statements: list["Stmt"]
    line: int = 1


# ============================================================
# AST TYPE ALIASES
# ============================================================
# These aliases describe which node types can be used as expressions
# and statements.

# An expression can be an integer literal, variable reference,
# or arithmetic operation.
Expr = IntLit | VarRef | BinOp

# A statement can be a declaration, assignment, input, print,
# or newline operation.
Stmt = Declare | Assign | Input | Print | NewLine
