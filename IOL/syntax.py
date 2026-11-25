"""

Syntax Analysis for the IOL Language.

This module is responsible for:
1. Reading token files (.tkn).
2. Checking token sequences using the PE03 predictive parser.
3. Reporting the first syntax error with its source line.
4. Using original lexemes when available for error messages.
5. Building an Abstract Syntax Tree (AST) from valid lexemes.

The parser itself is reused from PE03.
"""


# ============================================================
# IMPORTS
# ============================================================

# Import the IOL grammar and predictive parsing table.
from iol_grammar import PRODUCTIONS, TABLE

# Import AST node definitions.
from nodes import (
    Program,
    Declare,
    Assign,
    Input,
    Print,
    NewLine,
    IntLit,
    VarRef,
    BinOp,
)

# Import the PE03 predictive parser.
from parser import parse

# Import the compiler error structure from PE02/Task 1.
from tokens import CompileError


# ============================================================
# TOKEN FILE READER
# ============================================================

def read_tkn(tkn_path):
    """
    Read a .tkn file and return tokens with source line numbers.

    Each line of the .tkn file represents the tokens belonging
    to the corresponding source line.

    Example file:
        IOL
        INT IDENT IS INT_LIT
        PRINT IDENT
        LOI

    Returned value:
        [
            ("IOL", 1),
            ("INT", 2),
            ("IDENT", 2),
            ("IS", 2),
            ("INT_LIT", 2),
            ("PRINT", 3),
            ("IDENT", 3),
            ("LOI", 4)
        ]

    Empty source lines are preserved in the line numbering.
    """

    # Store the tokens and their source line numbers.
    tokens = []

    # Read the entire token file.
    with open(tkn_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split by newline to preserve the original line numbering.
    lines = content.split("\n")

    # Enumerate source lines starting from line 1.
    for line_number, line in enumerate(lines, start=1):

        # Split the line by whitespace.
        # A line may contain multiple token names.
        parts = line.split()

        # Store every token with the line number of its source line.
        for token in parts:
            tokens.append((token, line_number))

    # Return the token list.
    return tokens


# ============================================================
# LEXEME HELPERS
# ============================================================

def _get_lexeme_text(lexeme):
    """
    Get the original text/spelling from a lexeme.

    Supports common lexeme representations:
        - Objects with a .text attribute
        - Dictionaries containing "text"
        - Tuples/lists containing token information

    The source spelling is preferred over the token category.
    """

    # Lexeme objects used by the lexer.
    if hasattr(lexeme, "text"):
        return str(lexeme.text)

    # Dictionary-based lexemes.
    if isinstance(lexeme, dict):
        if "text" in lexeme:
            return str(lexeme["text"])

        if "lexeme" in lexeme:
            return str(lexeme["lexeme"])

    # Tuple/list-based lexemes.
    if isinstance(lexeme, (tuple, list)):

        # A common format is (token_type, text, line).
        if len(lexeme) >= 2:
            return str(lexeme[1])

        # A single item tuple/list.
        if len(lexeme) == 1:
            return str(lexeme[0])

    # Fall back to string representation.
    return str(lexeme)


def _get_lexeme_line(lexeme, fallback=1):
    """
    Retrieve the line number from a lexeme if available.

    If no line number is available, use the supplied fallback.
    """

    # Object-based lexeme.
    if hasattr(lexeme, "line"):
        return lexeme.line

    # Dictionary-based lexeme.
    if isinstance(lexeme, dict):
        if "line" in lexeme:
            return lexeme["line"]

        if "line_number" in lexeme:
            return lexeme["line_number"]

    # Tuple/list-based lexeme.
    if isinstance(lexeme, (tuple, list)) and len(lexeme) >= 3:
        return lexeme[2]

    return fallback


def _get_lexeme_type(lexeme):
    """
    Retrieve the token category from a lexeme.

    Supports common object, dictionary, and tuple representations.
    """

    # Object-based token category.
    for attribute in ("token", "type", "token_type", "category"):
        if hasattr(lexeme, attribute):
            value = getattr(lexeme, attribute)

            # Avoid returning an object instead of its token name.
            if isinstance(value, str):
                return value

    # Dictionary-based lexeme.
    if isinstance(lexeme, dict):
        for key in ("token", "type", "token_type", "category"):
            if key in lexeme:
                return lexeme[key]

    # Tuple/list-based lexeme.
    if isinstance(lexeme, (tuple, list)) and lexeme:
        return lexeme[0]

    return None


def _lexeme_at(lexemes, position):
    """
    Return the lexeme at the specified position, if available.
    """

    if lexemes is not None and 0 <= position < len(lexemes):
        return lexemes[position]

    return None


def _display_token(token, lexemes=None, position=None):
    """
    Return the token's source spelling for error messages.

    When lexemes are provided, their text is used.
    Otherwise, the token name is used.
    """

    # Use the source lexeme if one is available.
    lexeme = _lexeme_at(lexemes, position)

    if lexeme is not None:
        return _get_lexeme_text(lexeme)

    # Without lexemes, use the token name.
    return str(token)


# ============================================================
# SYNTAX CHECKER
# ============================================================

def check_syntax(tokens, lexemes=None):
    """
    Check whether a token sequence follows the IOL grammar.

    Args:
        tokens:
            A list of (token_name, line_number) pairs.

        lexemes:
            Optional list of original lexemes in the same order.
            Original lexeme text is used in syntax error messages.

    Returns:
        [] when the token sequence is syntactically valid.

        [CompileError] when the first syntax error is encountered.
    """

    # Extract token names for the PE03 parser.
    token_names = [token for token, line in tokens]

    # Call the PE03 parser without modifying its implementation.
    result = parse(token_names, PRODUCTIONS, TABLE)

    # If the parser accepts the token sequence, there are no errors.
    if result.valid:
        return []

    # ========================================================
    # DETERMINE THE ERROR POSITION
    # ========================================================

    # The last parsing step contains the unconsumed input buffer.
    last_step = result.steps[-1]

    # The buffer contains remaining tokens plus the end marker "$".
    remaining_tokens = last_step.buffer.split()

    # Determine how many tokens were consumed by the parser.
    position = len(tokens) + 1 - len(remaining_tokens)

    # Prevent the position from going outside the token list.
    position = max(0, min(position, len(tokens)))

    # ========================================================
    # DETERMINE THE ERROR LINE
    # ========================================================

    # If an unexpected token remains, use its source line.
    if position < len(tokens):
        error_line = tokens[position][1]

    # If parsing stopped at EOF, use the last token's line.
    elif tokens:
        error_line = tokens[-1][1]

    # Empty input is reported on line 1.
    else:
        error_line = 1

    # ========================================================
    # DETERMINE THE TOP OF THE PARSER STACK
    # ========================================================

    # PE03 stores the stack as a string.
    # The top of the stack is displayed on the left.
    stack_symbols = last_step.stack.split()

    # Extract the complete top symbol.
    top = stack_symbols[0] if stack_symbols else "$"

    # Determine the unexpected token.
    if position < len(tokens):
        unexpected = tokens[position][0]
    else:
        unexpected = "EOF"

    # Get the source spelling of the unexpected token.
    unexpected_text = _display_token(
        unexpected,
        lexemes,
        position
    )

    # ========================================================
    # EXPECTED SYMBOL DESCRIPTIONS
    # ========================================================

    # Translate token names into human-readable descriptions.
    expected_names = {
        "IDENT": "a variable name",
        "INT_LIT": "an integer",
        "IOL": "IOL",
        "LOI": "LOI",
        "INT": "INT",
        "STR": "STR",
        "INTO": "INTO",
        "IS": "IS",
        "BEG": "BEG",
        "PRINT": "PRINT",
        "NEWLN": "NEWLN",
        "ADD": "ADD",
        "SUB": "SUB",
        "MULT": "MULT",
        "DIV": "DIV",
        "MOD": "MOD",
    }

    # ========================================================
    # BUILD THE FIRST SYNTAX ERROR MESSAGE
    # ========================================================

    # Case 1: There is code after LOI.
    if top == "$" and unexpected != "EOF":

        message = f"unexpected '{unexpected_text}' after LOI"

    # Case 2: The input ended unexpectedly.
    elif unexpected == "EOF":

        # Empty input means the program start symbol was never matched.
        if top == "program":
            message = (
                "unexpected end of file; "
                "expected IOL at the start of the program"
            )

        # Missing LOI or an incomplete statement/expression.
        else:
            message = (
                "unexpected end of file; "
                "expected a statement or LOI"
            )

    # Case 3: The parser expected a nonterminal but the parsing
    # table did not contain a valid production.
    elif top in ("program", "stmts", "stmt", "init", "expr"):

        # Describe what each nonterminal expects.
        nonterminal_expectations = {
            "program": "IOL at the start of the program",
            "stmts": "a statement or LOI",
            "stmt": "a statement",
            "init": "IS or the next statement",
            "expr": "an expression",
        }

        expected = nonterminal_expectations[top]

        # Task 2 specifies this wording for arithmetic operators that appear
        # where a statement is expected (e.g., ADD x 5 as a statement).
        if top == "stmts" and unexpected in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            expected = "IS or the next statement"

        message = (
            f"unexpected '{unexpected_text}'; "
            f"expected {expected}"
        )

    # Case 4: A terminal was expected but did not match.
    else:

        # Convert token names into readable descriptions.
        expected = expected_names.get(top, top)

        # Convert unexpected token names into readable descriptions.
        found = expected_names.get(unexpected, unexpected_text)

        message = (
            f"expected {expected} "
            f"but found '{unexpected_text}'"
        )

        # Special case: IDENT is described as a variable name.
        if top == "IDENT":
            message = (
                f"expected a variable name "
                f"but found '{unexpected_text}'"
            )

        # Special case: INT_LIT is described as an integer.
        elif top == "INT_LIT":
            message = (
                f"expected an integer "
                f"but found '{unexpected_text}'"
            )

    # ========================================================
    # CREATE THE COMPILE ERROR
    # ========================================================

    # Create the syntax error using the project's CompileError class.
    error = CompileError(
        error_line,
        "syntax",
        message
    )

    # Return only the first syntax error.
    return [error]


# ============================================================
# AST CONSTRUCTION
# ============================================================

def build_program(lexemes, name):
    """
    Build an AST from a syntactically valid list of lexemes.

    This function assumes lexical and syntax analysis have already
    succeeded. It walks the lexemes in order and creates AST nodes.

    Supported statements:
        INT name [IS expr]
        STR name [IS expr]
        INTO name IS expr
        BEG name
        PRINT expr
        NEWLN

    Supported expressions:
        INT_LIT
        IDENT
        ADD expr expr
        SUB expr expr
        MULT expr expr
        DIV expr expr
        MOD expr expr

    Args:
        lexemes: Original lexemes from lexical analysis.
        name: Name of the source file.

    Returns:
        Program AST node.
    """

    # Store the AST statements.
    statements = []

    # Current position in the lexeme list.
    index = 0

    # ========================================================
    # LEXEME ACCESS HELPERS
    # ========================================================

    def current():
        """Return the current lexeme without advancing."""

        if index < len(lexemes):
            return lexemes[index]

        return None

    def advance():
        """Return the current lexeme and advance the index."""

        nonlocal index

        lexeme = current()

        if lexeme is not None:
            index += 1

        return lexeme

    def token_type(lexeme):
        """Return the token category of a lexeme."""

        return _get_lexeme_type(lexeme)

    def token_text(lexeme):
        """Return the original text of a lexeme."""

        return _get_lexeme_text(lexeme)

    def token_line(lexeme):
        """Return the source line of a lexeme."""

        return _get_lexeme_line(lexeme)

    # ========================================================
    # EXPRESSION PARSER
    # ========================================================

    def parse_expr():
        """
        Convert an expression into an AST node.

        Expressions are prefix expressions. Arithmetic operators
        are followed by two operand expressions.
        """

        # Consume the expression's first lexeme.
        lexeme = advance()

        # Return an integer literal node.
        if token_type(lexeme) == "INT_LIT":

            return IntLit(
                int(token_text(lexeme)),
                token_line(lexeme)
            )

        # Return a variable reference node.
        if token_type(lexeme) == "IDENT":

            return VarRef(
                token_text(lexeme),
                token_line(lexeme)
            )

        # Handle binary arithmetic expressions.
        if token_type(lexeme) in (
            "ADD",
            "SUB",
            "MULT",
            "DIV",
            "MOD",
        ):

            # Store the operator token.
            operator = token_type(lexeme)

            # Parse the first operand recursively.
            left = parse_expr()

            # Parse the second operand recursively.
            right = parse_expr()

            # Create the binary operation node.
            return BinOp(
                operator,
                left,
                right,
                token_line(lexeme)
            )

        # This should never happen if syntax analysis succeeded.
        raise ValueError(
            f"Unexpected lexeme in expression: {lexeme}"
        )

    # ========================================================
    # SKIP THE PROGRAM START TOKEN
    # ========================================================

    # IOL marks the start of the program and is not an AST statement.
    if current() is not None and token_type(current()) == "IOL":
        advance()

    # ========================================================
    # PROCESS STATEMENTS
    # ========================================================

    # Walk the lexemes until LOI is encountered.
    while current() is not None:

        # Store the current lexeme.
        lexeme = current()

        # Stop at the program terminator.
        if token_type(lexeme) == "LOI":
            advance()
            break

        # ----------------------------------------------------
        # VARIABLE DECLARATION
        # ----------------------------------------------------

        if token_type(lexeme) in ("INT", "STR"):

            # The declaration token determines the type.
            type_name = token_type(advance())

            # Consume the variable name.
            name_lexeme = advance()

            # Get the variable name's source spelling.
            variable_name = token_text(name_lexeme)

            # The statement line is the declaration's line.
            statement_line = token_line(lexeme)

            # Initializer is optional.
            initializer = None

            # If IS is present, parse the initializer.
            if current() is not None and token_type(current()) == "IS":

                # Consume IS.
                advance()

                # Parse the initializer expression.
                initializer = parse_expr()

            # Add the declaration to the AST.
            statements.append(
                Declare(
                    type_name,
                    variable_name,
                    initializer,
                    statement_line
                )
            )

        # ----------------------------------------------------
        # ASSIGNMENT
        # ----------------------------------------------------

        elif token_type(lexeme) == "INTO":

            # Consume INTO.
            advance()

            # Consume the target variable.
            name_lexeme = advance()

            # Get the variable name.
            variable_name = token_text(name_lexeme)

            # Consume IS.
            advance()

            # Parse the assigned expression.
            value = parse_expr()

            # Create the assignment node.
            statements.append(
                Assign(
                    variable_name,
                    value,
                    token_line(lexeme)
                )
            )

        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        elif token_type(lexeme) == "BEG":

            # Consume BEG.
            advance()

            # Consume the variable name.
            name_lexeme = advance()

            # Create the input statement.
            statements.append(
                Input(
                    token_text(name_lexeme),
                    token_line(lexeme)
                )
            )

        # ----------------------------------------------------
        # PRINT
        # ----------------------------------------------------

        elif token_type(lexeme) == "PRINT":

            # Consume PRINT.
            advance()

            # Parse the expression being printed.
            value = parse_expr()

            # Create the print statement.
            statements.append(
                Print(
                    value,
                    token_line(lexeme)
                )
            )

        # ----------------------------------------------------
        # NEWLINE
        # ----------------------------------------------------

        elif token_type(lexeme) == "NEWLN":

            # Consume NEWLN.
            advance()

            # Create the newline statement.
            statements.append(
                NewLine(
                    token_line(lexeme)
                )
            )

        # ----------------------------------------------------
        # UNEXPECTED TOKEN
        # ----------------------------------------------------

        else:

            # Skip it defensively.
            # Valid programs should never enter this branch.
            advance()

    # ========================================================
    # RETURN THE PROGRAM AST
    # ========================================================

    # Wrap all statements inside the root Program node.
    return Program(
        name,
        statements
    )
