"""Compile pipeline for the IOL IDE (PE02, Task 4).

compile_code() is the only function gui.py calls. It runs the lexer, builds the
variable table, formats the output, and returns one CompileResult.
"""
import os

from lexer import scan
from symbol_table import build_variable_table
from reporter import to_token_stream, build_messages, write_tkn
from tokens import CompileResult, ERR_LEX


def compile_code(source, iol_path):
    """Run lexical analysis on `source` and return a CompileResult.

    source:   the editor text.
    iol_path: path of the saved .iol file (the .tkn is written beside it).
    Exceptions are not caught here; gui.compile_action() reports them.
    """
    lexemes = scan(source)
    variables = build_variable_table(lexemes)

    line_count = source.count("\n") + 1          # same counting rule as scan()
    token_stream = to_token_stream(lexemes, line_count)

    filename = os.path.basename(iol_path) if iol_path else "untitled.iol"
    messages = build_messages(lexemes, filename)

    tkn_path, save_message = write_tkn(token_stream, iol_path)
    messages.append(save_message)

    return CompileResult(
        lexemes=lexemes,
        variables=variables,
        token_stream=token_stream,
        messages=messages,
        has_errors=any(lx.token == ERR_LEX for lx in lexemes),
        tkn_path=tkn_path,
    )