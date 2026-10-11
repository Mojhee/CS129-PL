"""Output formatting for the IOL lexical analyzer (PE02, Task 4).

Builds the token stream (.tkn contents), the console messages, and writes the
.tkn file. Does no scanning: it only formats what lexer.scan() produced.
"""
import os

from tokens import ERR_LEX


def to_token_stream(lexemes, line_count):
    """Return the token names of each source line, one output line per source line.

    Token names on a line are separated by one space. A source line with no
    lexemes (blank line) becomes an empty line, so line numbers stay aligned.
    The result has no trailing newline.
    """
    rows = [[] for _ in range(max(line_count, 1))]
    for lexeme in lexemes:
        index = lexeme.line - 1
        while index >= len(rows):          # safety: never drop a lexeme
            rows.append([])
        rows[index].append(lexeme.token)
    return "\n".join(" ".join(row) for row in rows)


def build_messages(lexemes, filename):
    """Return the console lines for one compile.

    No errors:  ["<filename>: lexical analysis completed with no errors found."]
    Errors:     one "Line N: unknown word '<text>'" per ERR_LEX lexeme (in source
                order), then "<filename>: lexical analysis completed with N error(s) found."
    """
    errors = [lx for lx in lexemes if lx.token == ERR_LEX]
    if not errors:
        return [f"{filename}: lexical analysis completed with no errors found."]
    messages = [f"Line {lx.line}: unknown word '{lx.text}'" for lx in errors]
    messages.append(
        f"{filename}: lexical analysis completed with {len(errors)} error(s) found."
    )
    return messages


def write_tkn(token_stream, iol_path):
    """Write the token stream to <name>.tkn next to the .iol file.

    Returns (tkn_path, message). On success tkn_path is the file written and
    message says where it was saved. On failure tkn_path is "" and message
    starts with "Could not save" (the GUI shows it in red). Never raises.
    """
    if not iol_path:
        return "", "Could not save .tkn file: the source file has no path."
    tkn_path = os.path.splitext(iol_path)[0] + ".tkn"
    try:
        with open(tkn_path, "w", encoding="utf-8") as f:
            f.write(token_stream)
    except OSError as err:
        return "", f"Could not save {os.path.basename(tkn_path)}: {err.strerror or err}"
    return tkn_path, f"Token stream saved to {tkn_path}"