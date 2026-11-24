
"""Read, validate, and compare PE03 grammar and parse-table CSV files."""
import csv
import os

from models import EMPTY, END_MARKER, FileFormatError, Production, Productions, ParseTable, normalize_symbol

# This function reads a CSV file and returns its nonblank rows.
def read_csv_rows(path):
    """Return (physical line number, normalized cells) for nonblank CSV rows."""

    # Define a helper function that reads the file using a given encoding.
    def read_with_encoding(encoding):

        # Open the file in reading mode using the specified encoding.
        # newline="" allows the csv module to handle line endings correctly.
        with open(path, newline="", encoding=encoding) as source:

            # Create a CSV reader that checks for malformed CSV formatting.
            reader = csv.reader(source, strict=True)

            # Prepare an empty list to store valid, nonblank rows.
            rows = []

            # Go through every row in the CSV file.
            for cells in reader:

                # Normalize every cell by removing surrounding spaces
                # and converting curly apostrophes into straight apostrophes.
                normalized = [normalize_symbol(cell) for cell in cells]

                # Check whether the row contains at least one nonblank cell.
                if any(normalized):

                    # Store the physical line number and normalized cells.
                    rows.append((reader.line_num, normalized))

            # Return all nonblank rows with their line numbers.
            return rows

    # Try reading the file and handle CSV formatting errors.
    try:

        # First, attempt to read the file using UTF-8 encoding.
        try:
            return read_with_encoding("utf-8-sig")

        # If UTF-8 decoding fails, try Windows encoding instead.
        except UnicodeDecodeError:
            return read_with_encoding("cp1252")

    # Catch errors caused by invalid CSV formatting.
    except csv.Error as error:

        # Raise a custom error containing the filename and problem.
        raise FileFormatError(
            f"{os.path.basename(path)}: invalid CSV: {error}"
        ) from error


# This function loads and validates a .prod grammar file.
def load_productions(path):
    """Load a .prod file into a Productions object, validating each row."""

    # Get only the filename from the complete file path.
    filename = os.path.basename(path)

    # Read the nonblank rows from the production file.
    rows = read_csv_rows(path)

    # Check whether the file contains no production rules.
    if not rows:

        # Reject the file if it is empty.
        raise FileFormatError(f"{filename} has no productions.")

    # Create a dictionary to store production rules by their numbers.
    items = {}

    # Initially, no start symbol has been selected.
    start_symbol = None

    # Process each production row together with its line number.
    for line, cells in rows:

        # Check whether the row has fewer than three columns
        # or any of its first three required fields is blank.
        if len(cells) < 3 or not all(cells[:3]):

            # Reject rows with missing required information.
            raise FileFormatError(
                f"{filename}, line {line}: "
                "expected number, non-terminal, production."
            )

        # Check whether extra columns contain nonblank values.
        if any(cells[3:]):

            # Reject unexpected additional information.
            raise FileFormatError(
                f"{filename}, line {line}: too many columns."
            )

        # Extract the production number, non-terminal, and production body.
        raw_number, head, raw_body = cells[:3]

        # Check whether the production number is:
        # 1. Written using ASCII characters.
        # 2. Made entirely of decimal digits.
        # 3. Greater than or equal to 1.
        if (
            not raw_number.isascii()
            or not raw_number.isdecimal()
            or int(raw_number) < 1
        ):

            # Reject invalid production numbers.
            raise FileFormatError(
                f"{filename}, line {line}: "
                f"'{raw_number}' is not a production number."
            )

        # Convert the valid production number from text into an integer.
        number = int(raw_number)

        # Check whether the production number already exists.
        if number in items:

            # Reject duplicate production numbers.
            raise FileFormatError(
                f"{filename}, line {line}: "
                f"production number {number} is used twice."
            )

        # Check whether the non-terminal contains whitespace.
        if any(char.isspace() for char in head):

            # Reject non-terminals containing spaces.
            raise FileFormatError(
                f"{filename}, line {line}: "
                f"non-terminal '{head}' contains a space."
            )

        # Split the production body into individual grammar symbols.
        # Example: "+ T E'" becomes ["+", "T", "E'"].
        body = [normalize_symbol(symbol) for symbol in raw_body.split()]

        # Check whether the empty symbol "e" appears with other symbols.
        if EMPTY in body and len(body) != 1:

            # Reject productions such as "e T".
            raise FileFormatError(
                f"{filename}, line {line}: "
                "e must be the only symbol in its production."
            )

        # Check whether the start symbol has not yet been assigned.
        if start_symbol is None:

            # Use the first production's non-terminal as the start symbol.
            start_symbol = head

        # Create a Production object and store it using its number.
        items[number] = Production(number, head, body)

    # Return the complete Productions object.
    return Productions(path, items, start_symbol)


# This function loads and validates a .ptbl predictive parsing table.
def load_parse_table(path):
    """Load a .ptbl CSV file into a ParseTable object, validating its cells."""

    # Extract the filename for readable error messages.
    filename = os.path.basename(path)

    # Read the nonblank CSV rows.
    rows = read_csv_rows(path)

    # A parse table needs a header and at least one non-terminal row.
    if len(rows) < 2:

        # Reject files without enough rows.
        raise FileFormatError(f"{filename} has no rows.")

    # Separate the first row's line number and header values.
    header_line, header = rows[0]

    # Extract terminal symbols, skipping the first header cell.
    terminals = header[1:]

    # Create a set to track terminal symbols already encountered.
    seen = set()

    # Examine every terminal in the header.
    for terminal in terminals:

        # Check whether a terminal name is blank.
        if not terminal:

            # Reject blank terminal names.
            raise FileFormatError(
                f"{filename}, line {header_line}: blank terminal."
            )

        # Check whether this terminal was already encountered.
        if terminal in seen:

            # Reject duplicate terminal names.
            raise FileFormatError(
                f"{filename}, line {header_line}: "
                f"terminal '{terminal}' appears twice."
            )

        # Record the terminal to detect future duplicates.
        seen.add(terminal)

    # Check whether the required end marker "$" exists.
    if END_MARKER not in seen:

        # Reject a parse table without the end-marker column.
        raise FileFormatError(
            f"{filename}, line {header_line}: there is no $ column."
        )

    # Create a list to store the non-terminals in their original order.
    nonterminals = []

    # Create a dictionary for nonblank parsing-table cells.
    cells = {}

    # Create a set to detect duplicate non-terminal rows.
    seen_nt = set()

    # Process every row after the header.
    for line, row in rows[1:]:

        # Get the first cell, which represents the non-terminal.
        head = row[0] if row else ""

        # Check whether the non-terminal name is missing.
        if not head:

            # Reject rows without a non-terminal.
            raise FileFormatError(
                f"{filename}, line {line}: blank non-terminal."
            )

        # Check whether the non-terminal contains whitespace.
        if any(char.isspace() for char in head):

            # Reject non-terminals containing spaces.
            raise FileFormatError(
                f"{filename}, line {line}: "
                f"non-terminal '{head}' contains a space."
            )

        # Check whether the non-terminal row already exists.
        if head in seen_nt:

            # Reject duplicate non-terminal rows.
            raise FileFormatError(
                f"{filename}, line {line}: "
                f"non-terminal {head} appears twice."
            )

        # Check whether extra columns contain nonblank values.
        if any(row[len(terminals) + 1:]):

            # Reject rows containing more values than the header allows.
            raise FileFormatError(
                f"{filename}, line {line}: more cells than terminals."
            )

        # Mark the non-terminal as already encountered.
        seen_nt.add(head)

        # Store the non-terminal in the list.
        nonterminals.append(head)

        # Pair each terminal with the corresponding value in the row.
        for terminal, raw_number in zip(terminals, row[1:]):

            # Skip empty cells because they represent missing productions.
            if not raw_number:
                continue

            # Check whether the cell contains a valid positive integer.
            if (
                not raw_number.isascii()
                or not raw_number.isdecimal()
                or int(raw_number) < 1
            ):

                # Reject invalid production references.
                raise FileFormatError(
                    f"{filename}, line {line}, column '{terminal}': "
                    f"'{raw_number}' is not a production number."
                )

            # Store the production number using the non-terminal
            # and terminal as a pair of dictionary keys.
            # Example: cells[("E", "id")] = 1.
            cells[(head, terminal)] = int(raw_number)

    # Return the completed ParseTable object.
    return ParseTable(path, terminals, nonterminals, cells)


# This function checks whether the grammar and parse table are compatible.
def check_compatible(productions, table):
    """Return all mismatches between the production rules and parse table."""

    # Create a list to collect compatibility problems.
    problems = []

    # Get the grammar filename for error messages.
    prod_filename = os.path.basename(productions.path)

    # Get the parse-table filename for error messages.
    table_filename = os.path.basename(table.path)

    # Collect all unique non-terminals defined by the grammar rules.
    heads = {
        production.head
        for production in productions.items.values()
    }

    # Convert the table's terminals into a set for quick searching.
    terminal_set = set(table.terminals)

    # Convert the table's non-terminals into a set.
    nonterminal_set = set(table.nonterminals)

    # CHECK 1: Verify that every table cell references an existing
    # production and that it belongs to the correct non-terminal.

    # Go through every stored parse-table cell.
    for (head, terminal), number in table.cells.items():

        # Look for the referenced production number.
        production = productions.items.get(number)

        # Check whether the production number does not exist.
        if production is None:

            # Record a missing-production compatibility problem.
            problems.append(
                f"Cell ({head}, {terminal}) uses production {number}, "
                f"which is not in {prod_filename}."
            )

        # Check whether the production belongs to another non-terminal.
        elif production.head != head:

            # Record a mismatch between the row and production.
            problems.append(
                f"Cell ({head}, {terminal}) uses production {number}, "
                f"which is for {production.head}, not {head}."
            )

    # CHECK 2: Verify that every grammar non-terminal has a table row.

    # Find grammar non-terminals missing from the parse table.
    for head in sorted(heads - nonterminal_set):

        # Record each missing non-terminal row.
        problems.append(
            f"Non-terminal {head} has no row in {table_filename}."
        )

    # CHECK 3: Verify that table non-terminals exist in the grammar.

    # Find parse-table non-terminals without corresponding grammar rules.
    for head in sorted(nonterminal_set - heads):

        # Record each extra non-terminal.
        problems.append(
            f"Non-terminal {head} has no production in {prod_filename}."
        )

    # CHECK 4: Verify that every production symbol is recognized.

    # Go through all production rules.
    for production in productions.items.values():

        # Examine each symbol in the production body.
        for symbol in production.body:

            # Check whether the symbol is not:
            # - the empty symbol "e",
            # - a defined non-terminal,
            # - or a recognized terminal.
            if (
                symbol not in (EMPTY,)
                and symbol not in heads
                and symbol not in terminal_set
            ):

                # Record the unknown grammar symbol.
                problems.append(
                    f"Production {production.number} uses '{symbol}', "
                    f"which is not in {table_filename}."
                )

    # CHECK 5: Verify that no symbol is both terminal and non-terminal.

    # Find symbols that appear in both categories.
    for symbol in sorted(heads & terminal_set):

        # Record each conflicting symbol.
        problems.append(
            f"'{symbol}' is both a terminal and a non-terminal."
        )

    # Return all compatibility problems.
    # An empty list means no problems were detected.
    return problems


# This function checks whether the two filenames match.
def same_name(prod_path, ptbl_path):
    """Compare filename stems without extensions, ignoring case."""

    # Define a helper function to extract a filename without its extension.
    def stem(path):

        # Get the filename, remove its extension, and ignore letter case.
        return os.path.splitext(os.path.basename(path))[0].casefold()

    # Compare the two filenames and return True or False.
    return stem(prod_path) == stem(ptbl_path)