from models import (EMPTY, END_MARKER, ParseStep, ParseResult,
                    normalize_symbol)
 
MAX_STEPS = 10000   # safety limit against a broken parse table
 
 
def tokenize_input(text):
    """Split the input on any whitespace. Raise ValueError if $ is typed."""
 
 
def format_stack(stack):
    """Stack list (top = last item) -> "T E' $" (top on the left)."""
 
 
def format_buffer(tokens, position):
    """Remaining tokens from position onward -> "id * id $"."""
 
 
def parse(tokens, productions, table):
    stack = [END_MARKER, productions.start_symbol]
    buffer = tokens + [END_MARKER]
    position = 0
    steps = [ParseStep(format_stack(stack), format_buffer(buffer, 0), "")]
    nonterminals = set(table.nonterminals)
    terminals = set(table.terminals)
    
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
