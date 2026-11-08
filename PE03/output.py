"""Name and write the parsing solution file (.prsd) for PE03.

The solution is saved as outname_prodname.prsd in the same folder as the
productions file. Each row is one parsing step: stack, input buffer, action,
in CSV format. This module never talks to the user; it returns values or
raises exceptions, and gui.py shows the messages.
"""
import csv
import os

OUTPUT_EXT = ".prsd"
FORBIDDEN = '\\/:*?"<>|'   # characters Windows does not allow in file names


def clean_outname(name):
    """Return the typed name, cleaned. Raise ValueError if unusable.

    Spaces around the name are removed, and a typed .prsd extension is
    dropped (test.prsd becomes test), since it is added automatically.
    """
    name = name.strip()
    if name.lower().endswith(OUTPUT_EXT):
        name = name[:-len(OUTPUT_EXT)].strip()
    if not name:
        raise ValueError("Enter an output file name.")
    if any(char in FORBIDDEN for char in name):
        raise ValueError('The output file name cannot contain '
                         'any of these characters: \\ / : * ? " < > |')
    return name


def output_path(outname, prod_path):
    """Full path of outname_prodname.prsd, in the .prod file's folder.

    For test and C:/grammars/rules.prod the result is
    C:/grammars/test_rules.prsd.
    """
    prodname = os.path.splitext(os.path.basename(prod_path))[0]
    folder = os.path.dirname(prod_path)
    return os.path.join(folder, f"{outname}_{prodname}{OUTPUT_EXT}")


def step_row(step):
    """Return the CSV cells of one ParseStep.

    The first row (initial state) has no action, so only the stack and the
    buffer are written and the line has no trailing comma.
    """
    if step.action:
        return [step.stack, step.buffer, step.action]
    return [step.stack, step.buffer]


def write_prsd(result, path):
    """Write the steps of a ParseResult to a CSV file.

    An existing file with the same name is replaced. OSError (for example,
    a read-only folder) is not caught here; gui.py reports it.
    """
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for step in result.steps:
            writer.writerow(step_row(step))


# Quick test of this module alone. Run with: python output.py
if __name__ == "__main__":
    import tempfile
    from models import ParseStep, ParseResult

    print(clean_outname("  test.prsd "))                       # test
    print(output_path("test", "C:/grammars/rules.prod"))       # C:/grammars/test_rules.prsd
    for bad in ("", "   ", ".prsd", "a/b", "what?"):
        try:
            clean_outname(bad)
            print(f"[FAIL] {bad!r} was accepted")
        except ValueError as error:
            print(f"[PASS] {bad!r}: {error}")

    sample = ParseResult(True, [ParseStep("E $", "id $", ""),
                                ParseStep("T E' $", "id $", "Output E > T E'"),
                                ParseStep("", "", "Match $")])
    target = os.path.join(tempfile.gettempdir(), "test_rules.prsd")
    write_prsd(sample, target)
    with open(target, encoding="utf-8") as file:
        print(file.read())
