"""TEMPORARY fake versions of loaders.py, parser.py, and output.py.

gui.py falls back to these while the real modules are not in the folder yet.
Every function ignores the file contents and returns the handout's sample
grammar, so the displays can be tested. DO NOT SUBMIT this file.
"""
import os

from models import (FileFormatError, Production, Productions, ParseTable,
                    ParseStep, ParseResult)

# The handout's expression grammar: (number, non-terminal, production).
SAMPLE_PRODUCTIONS = [
    (1, "E", "T E'"), (2, "E'", "+ T E'"), (3, "E'", "e"), (4, "T", "F T'"),
    (5, "T'", "* F T'"), (6, "T'", "e"), (7, "F", "( E )"), (8, "F", "id"),
]
# Parse table columns (header order) and its non-blank cells.
SAMPLE_TERMINALS = ["id", "+", "*", "(", ")", "$"]
SAMPLE_CELLS = {
    ("E", "id"): 1, ("E", "("): 1,
    ("E'", "+"): 2, ("E'", ")"): 3, ("E'", "$"): 3,
    ("T", "id"): 4, ("T", "("): 4,
    ("T'", "+"): 6, ("T'", "*"): 5, ("T'", ")"): 6, ("T'", "$"): 6,
    ("F", "id"): 8, ("F", "("): 7,
}
# The 18 rows of the handout's sample output for id + id * id.
SAMPLE_STEPS = [
    ("E $", "id + id * id $", ""),
    ("T E' $", "id + id * id $", "Output E > T E'"),
    ("F T' E' $", "id + id * id $", "Output T > F T'"),
    ("id T' E' $", "id + id * id $", "Output F > id"),
    ("T' E' $", "+ id * id $", "Match id"),
    ("E' $", "+ id * id $", "Output T' > e"),
    ("+ T E' $", "+ id * id $", "Output E' > + T E'"),
    ("T E' $", "id * id $", "Match +"),
    ("F T' E' $", "id * id $", "Output T > F T'"),
    ("id T' E' $", "id * id $", "Output F > id"),
    ("T' E' $", "* id $", "Match id"),
    ("* F T' E' $", "* id $", "Output T' > * F T'"),
    ("F T' E' $", "id $", "Match *"),
    ("id T' E' $", "id $", "Output F > id"),
    ("T' E' $", "$", "Match id"),
    ("E' $", "$", "Output T' > e"),
    ("$", "$", "Output E' > e"),
    ("", "", "Match $"),
]


def load_productions(path):
    """Fake: return the sample productions, refusing files named bad*."""
    if os.path.basename(path).lower().startswith("bad"):
        raise FileFormatError(f"{os.path.basename(path)}, line 1: stub refuses bad* files.")
    items = {n: Production(n, head, body.split()) for n, head, body in SAMPLE_PRODUCTIONS}
    return Productions(path, items, "E")


def load_parse_table(path):
    """Fake: return the sample parse table, refusing files named bad*."""
    if os.path.basename(path).lower().startswith("bad"):
        raise FileFormatError(f"{os.path.basename(path)}, line 1: stub refuses bad* files.")
    return ParseTable(path, list(SAMPLE_TERMINALS), ["E", "E'", "T", "T'", "F"],
                      dict(SAMPLE_CELLS))


def check_compatible(productions, table):
    """Fake: always compatible."""
    return []


def same_name(prod_path, ptbl_path):
    """Compare file names without extensions, ignoring case."""
    def stem(path):
        return os.path.splitext(os.path.basename(path))[0].lower()
    return stem(prod_path) == stem(ptbl_path)


def tokenize_input(text):
    """Split on whitespace; refuse a typed $."""
    tokens = text.split()
    if "$" in tokens:
        raise ValueError("Do not type $; it is added at the end automatically.")
    return tokens


def parse(tokens, productions, table):
    """Fake: VALID with the sample steps when the input is id + id * id, else INVALID."""
    steps = [ParseStep(*row) for row in SAMPLE_STEPS]
    if tokens == ["id", "+", "id", "*", "id"]:
        return ParseResult(True, steps)
    message = "Error: stub parser only accepts id + id * id"
    return ParseResult(False, [steps[0], ParseStep(steps[0].stack, steps[0].buffer, message)],
                       message)


def clean_outname(name):
    """Strip, drop a typed .prsd, and refuse empty or forbidden names."""
    name = name.strip()
    if name.lower().endswith(".prsd"):
        name = name[:-5].strip()
    if not name:
        raise ValueError("Enter an output file name.")
    if any(ch in name for ch in '\\/:*?"<>|'):
        raise ValueError('The name cannot contain \\ / : * ? " < > |')
    return name


def output_path(outname, prod_path):
    """outname_prodname.prsd in the .prod file's folder."""
    prodname = os.path.splitext(os.path.basename(prod_path))[0]
    return os.path.join(os.path.dirname(prod_path), f"{outname}_{prodname}.prsd")


def write_prsd(result, path):
    """Write the steps as CSV; the first row has no trailing comma."""
    import csv   # only this stub writes files
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for step in result.steps:
            row = [step.stack, step.buffer] + ([step.action] if step.action else [])
            writer.writerow(row)
