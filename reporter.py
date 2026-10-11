"""Output formatting for the IOL lexical analyzer (PE02, Task 4).

Builds the token stream (.tkn contents) and the console messages, and writes
the .tkn file. Does no scanning: it only formats what lexer.scan() produced.
"""
import os

from tokens import ERR_LEX


def to_token_stream(lexemes, line_count):
    """Return the tokenized code: one output line per source line.

    Each lexeme is replaced by its token name, and the token names on a line
    are separated by one space. A source line with no lexemes (a blank line)
    becomes an empty line, so line N of the .tkn always matches line N of the
    .iol. The result has no trailing newline.
    """
    # One list of token names per source line. Always keep at least one line,
    # so empty source still gives a valid (empty) token stream.
    lines = [[] for _ in range(max(line_count, 1))]

    for lexeme in lexemes:
        index = lexeme.line - 1          # Lexeme.line is 1-based
        # Safety net: if a lexeme's line is past line_count, add lines
        # instead of dropping the lexeme.
        while index >= len(lines):
            lines.append([])
        lines[index].append(lexeme.token)

    # Join the tokens of each line with spaces, then the lines with newlines.
    return "\n".join(" ".join(tokens_on_line) for tokens_on_line in lines)


def write_tkn(token_stream, iol_path):
    """Write the token stream next to the .iol file. Return the .tkn path.

    The .tkn file has the same name as the .iol file, e.g. C:/code/test.iol
    gives C:/code/test.tkn. It is written even when there are lexical errors,
    because ERR_LEX is part of the token stream. Raises OSError if the file
    cannot be written; compile_code() catches it.
    """
    tkn_path = os.path.splitext(iol_path)[0] + ".tkn"
    with open(tkn_path, "w", encoding="utf-8") as tkn_file:
        tkn_file.write(token_stream)
    return tkn_path


def build_messages(lexemes, filename):
    """Return (list of console lines, has_errors).

    No errors:   ["test.iol: lexical analysis completed with no errors found."]
    Errors:      one "Line 2: unknown word 'my_var'" line per ERR_LEX lexeme,
                 in source order, then "errors.iol: 3 lexical error(s) found."
    has_errors is True when at least one ERR_LEX lexeme exists.
    """
    # Every lexeme the lexer could not classify is a lexical error.
    errors = [lexeme for lexeme in lexemes if lexeme.token == ERR_LEX]

    if not errors:
        return [f"{filename}: lexical analysis completed with no errors found."], False

    # One line per unknown word, then a summary line with the error count.
    messages = [f"Line {lexeme.line}: unknown word '{lexeme.text}'" for lexeme in errors]
    messages.append(f"{filename}: {len(errors)} lexical error(s) found.")
    return messages, True
