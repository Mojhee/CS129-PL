from models import (EMPTY, END_MARKER, ParseStep, ParseResult,
                    normalize_symbol)

MAX_STEPS = 10000   # safety limit against a broken parse table


def tokenize_input(text: str) -> list[str]:
    """Split the input on any whitespace. Raise ValueError if $ is typed."""
    tokens = [normalize_symbol(token) for token in text.split()]
    for token in tokens:
        if token == END_MARKER:
            raise ValueError("Do not type $; it is added at the end automatically.")
    return tokens


def format_stack(stack: list[str]) -> str:
    """Stack list (top = last item) -> "T E' $" (top on the left)."""
    return " ".join(reversed(stack))


def format_buffer(tokens: list[str], position: int) -> str:
    """Remaining tokens from position onward -> "id * id $"."""
    return " ".join(tokens[position:])


def parse(tokens, productions, table):
    """Run the parser and return a ParseResult."""
    stack = [END_MARKER, productions.start_symbol]
    buffer = tokens + [END_MARKER]
    position = 0
    steps = [ParseStep(format_stack(stack), format_buffer(buffer, 0), "")]
    nonterminals = set(table.nonterminals)
    terminals = set(table.terminals)

    def fail(message: str) -> ParseResult:
        steps.append(ParseStep(format_stack(stack), format_buffer(buffer, position), message))
        return ParseResult(False, steps, message)

    while len(steps) <= MAX_STEPS:
        top = stack[-1]
        current = buffer[position]
        if current not in terminals:
            return fail(f"Error: unknown token {current}")
        if top in nonterminals:
            number = table.cells.get((top, current))
            if number is None:
                return fail(f"Error: no production for {top} "
                            f"on input {current}")
            production = productions.items[number]
            stack.pop()
            if production.body != [EMPTY]:
                stack.extend(reversed(production.body))
            action = f"Output {top} > {' '.join(production.body)}"
        else:
            if top != current:
                return fail(f"Error: expected {top} but found {current}")
            stack.pop()
            position += 1
            action = f"Match {current}"
        steps.append(ParseStep(format_stack(stack),
                               format_buffer(buffer, position), action))
        if action == f"Match {END_MARKER}":
            return ParseResult(True, steps)

    return fail("Error: stopped after too many steps; "
                "check that the grammar is LL(1)")

# Running test cases with parser.py alone
# Run with $ python parser.py
if __name__ == "__main__":
    from models import Production, Productions, ParseTable

    # Construct the classic expression grammar (Section 3.1)
    prods = {
        1: Production(1, "E", ["T", "E'"]),
        2: Production(2, "E'", ["+", "T", "E'"]),
        3: Production(3, "E'", ["e"]),
        4: Production(4, "T", ["F", "T'"]),
        5: Production(5, "T'", ["*", "F", "T'"]),
        6: Production(6, "T'", ["e"]),
        7: Production(7, "F", ["(", "E", ")"]),
        8: Production(8, "F", ["id"]),
    }
    sample_productions = Productions("rules.prod", prods, "E")

    terminals = ["id", "+", "*", "(", ")", "$"]
    nonterminals = ["E", "E'", "T", "T'", "F"]
    cells = {
        ("E", "id"): 1,
        ("E", "("): 1,
        ("E'", "+"): 2,
        ("E'", ")"): 3,
        ("E'", "$"): 3,
        ("T", "id"): 4,
        ("T", "("): 4,
        ("T'", "+"): 6,
        ("T'", "*"): 5,
        ("T'", ")"): 6,
        ("T'", "$"): 6,
        ("F", "id"): 8,
        ("F", "("): 7,
    }
    sample_table = ParseTable("rules.ptbl", terminals, nonterminals, cells)

    # Test cases from Section 7, Step 3
    test_cases = [
        ("id + id * id", True, ",,Match $"),
        ("( id + id ) * id", True, ",,Match $"),
        ("id + * id", False, "T E' $,* id $,Error: no production for T on input *"),
        ("+ id", False, "E $,+ id $,Error: no production for E on input +"),
        ("id id", False, "T' E' $,id $,Error: no production for T' on input id"),
        ("( id", False, ") T' E' $,$,Error: expected ) but found $"),
        ("id + id )", False, "$,) $,Error: expected $ but found )"),
        ("id + num", False, "T E' $,num $,Error: unknown token num"),
    ]

    print("Running parser.py standalone test suite...")
    all_passed = True
    for inp, exp_valid, exp_last in test_cases:
        t = tokenize_input(inp)
        res = parse(t, sample_productions, sample_table)
        last_step_str = f"{res.steps[-1].stack},{res.steps[-1].buffer},{res.steps[-1].action}"
        passed = (res.valid == exp_valid) and (last_step_str == exp_last)
        if not passed:
            all_passed = False
        print(f"[{'PASS' if passed else 'FAIL'}] Input: {inp:<20} | Valid: {str(res.valid):<5}")

    # Test $ rejection
    try:
        tokenize_input("id + $")
        print("[FAIL] Rejection of typed $")
        all_passed = False
    except ValueError:
        print("[PASS] Rejection of typed $")

    print(f"\nAll tests passed: {all_passed}")