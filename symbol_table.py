"""Variable table builder for the IOL lexical analyzer."""
from tokens import Variable, IDENT, TYPE_KEYWORDS


def build_variable_table(lexemes):
    """Return a list of Variable(name, type) in order of definition."""
    variables = []
    seen = set() # Keep track of variables that have already been seen

    # Iterates inclusively of the whole list.
    # Pseudocode of "len(lexemes) - 1" is synonymous with "- 2" below.
    # It is "len(lexemes) - 1" instead of "len(lexemes) - 2" because the last
    # element is checked with "following = lexemes[i + 1]" below.
    for i in range(len(lexemes) - 1):
        current = lexemes[i]
        following = lexemes[i + 1]

        # If a type keyword is followed by an identifier that hasn't been declared yet,
        # register the new variable and record it in the seen set to prevent duplicates.

        if current.token in TYPE_KEYWORDS and following.token == IDENT:
            if following.text not in seen:
                variables.append(Variable(following.text, current.token))
                seen.add(following.text)

    return variables

# This block runs when the file is executed directly
# Running test cases are defined and executed below
if __name__ == "__main__":
    from tokens import Lexeme

    def L(text, token, line=1):
        return Lexeme(text, token, line)

    print("FIRST SAMPLE RUN FROM INDEPENDENT TESTING:")

    sample = [
        L("INT", "INT"),
        L("num", "IDENT"),
        L("IS", "IS"),
        L("0", "INT_LIT"),
        L("STR", "STR", 2),
        L("msg1", "IDENT", 2),
    ]
    print(build_variable_table(sample))
    # expected: [Variable(name='num', type='INT'), Variable(name='msg1', type='STR')]

    print("\n" + "TEST CASES RUN:")

    test_cases = [
        # 1. INT num IS 0 INT res IS 0 -> num INT, res INT
        (
            "INT num IS 0 INT res IS 0",
            [
                L("INT", "INT"), L("num", "IDENT"), L("IS", "IS"), L("0", "INT_LIT"),
                L("INT", "INT"), L("res", "IDENT"), L("IS", "IS"), L("0", "INT_LIT"),
            ],
            [Variable("num", "INT"), Variable("res", "INT")],
        ),
        # 2. STR msg1 STR msg2 -> msg1 STR, msg2 STR
        (
            "STR msg1 STR msg2",
            [
                L("STR", "STR"), L("msg1", "IDENT"),
                L("STR", "STR"), L("msg2", "IDENT"),
            ],
            [Variable("msg1", "STR"), Variable("msg2", "STR")],
        ),
        # 3. INT x INT x -> x INT (listed once)
        (
            "INT x INT x",
            [
                L("INT", "INT"), L("x", "IDENT"),
                L("INT", "INT"), L("x", "IDENT"),
            ],
            [Variable("x", "INT")],
        ),
        # 4. INT x STR x -> x INT (first definition wins)
        (
            "INT x STR x",
            [
                L("INT", "INT"), L("x", "IDENT"),
                L("STR", "STR"), L("x", "IDENT"),
            ],
            [Variable("x", "INT")],
        ),
        # 5. INT INT -> empty
        (
            "INT INT",
            [L("INT", "INT"), L("INT", "INT")],
            [],
        ),
        # 6. INT 5 -> empty
        (
            "INT 5",
            [L("INT", "INT"), L("5", "INT_LIT")],
            [],
        ),
        # 7. STR my_var (my_var is ERR_LEX) -> empty
        (
            "STR my_var (ERR_LEX)",
            [L("STR", "STR"), L("my_var", "ERR_LEX")],
            [],
        ),
        # 8. INTO res IS 5 -> empty (INTO is not a type)
        (
            "INTO res IS 5",
            [
                L("INTO", "INTO"), L("res", "IDENT"),
                L("IS", "IS"), L("5", "INT_LIT"),
            ],
            [],
        ),
        # 9. INT at the very end of the code -> empty, and no crash
        (
            "INT at end of code",
            [L("INT", "INT")],
            [],
        ),
        # 10. no lexemes at all -> empty, and no crash
        (
            "No lexemes (empty list)",
            [],
            [],
        ),
    ]

    all_passed = True
    for name, input_lexemes, expected in test_cases:
        actual = build_variable_table(input_lexemes)
        if actual == expected:
            print(f"PASS: {name}")
        else:
            print(f"FAIL: {name}")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            all_passed = False
    print("-" * 50)
    if all_passed:
        print("All 10 test cases PASSED successfully!")
    else:
        print("Some tests failed.")