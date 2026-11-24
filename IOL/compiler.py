"""Compile pipeline for the IOL IDE (PE02, Task 4).

compile_code() is the only function gui.py calls. It runs the lexer, builds the
variable table, formats the output, writes the .tkn file, and returns one
CompileResult.
"""
import os

from tokens import CompileResult
from lexer import scan
from symbol_table import build_variable_table
from reporter import to_token_stream, write_tkn, build_messages


def compile_code(source, iol_path):
    """Run lexical analysis on source and return a CompileResult.

    source:   the code from the editor.
    iol_path: path of the saved .iol file; the .tkn file is written beside it.
    """
    # 1. Split the code into lexemes and give each one its token (lexer.py).
    lexemes = scan(source)

    # 2. Find the variable definitions for the Table of Variables (symbol_table.py).
    variables = build_variable_table(lexemes)

    # 3. Build the token stream with one line per source line. The line count
    #    uses the same rule as scan(): every "\n" starts a new line.
    token_stream = to_token_stream(lexemes, source.count("\n") + 1)

    # 4. Build the console messages: success, or each unknown word with its line.
    filename = os.path.basename(iol_path)
    messages, has_errors = build_messages(lexemes, filename)

    # 5. Save the .tkn file. A failure (e.g. a read-only folder) is reported in
    #    the console instead of stopping the compile.
    tkn_path = ""
    try:
        tkn_path = write_tkn(token_stream, iol_path)
        messages.append("Token stream saved to " + os.path.basename(tkn_path) + ".")
    except OSError as err:
        messages.append("Could not save the token file: " + str(err))

    return CompileResult(lexemes, variables, token_stream,
                         messages, has_errors, tkn_path)
