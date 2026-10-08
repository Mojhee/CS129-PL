# Import the shared data structures and token definitions
# from tokens.py.
from tokens import Lexeme, KEYWORDS, INT_LIT, IDENT, ERR_LEX


def is_letter(ch):
    """True only for a-z and A-Z."""

    # Check if the character is a lowercase letter
    # or an uppercase letter.
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z")


def is_digit(ch):
    """True only for 0-9."""

    # Check if the character is an ASCII digit from 0 to 9.
    return "0" <= ch <= "9"


def classify(text):
    """Return the token name for one lexeme."""

    # An empty string is not a valid lexeme.
    if text == "":
        return ERR_LEX

    # Start in the START state of the DFA.
    #
    # Possible states:
    # START  - no character has been processed yet
    # INT    - the lexeme contains only digits
    # IDENT  - the lexeme starts with a letter and contains
    #          only letters and digits
    # ERROR  - the lexeme contains an invalid character
    state = "START"

    # Read the lexeme one character at a time.
    for ch in text:

        # ----------------------------------------------------
        # START STATE
        # ----------------------------------------------------
        if state == "START":

            # If the first character is a letter,
            # this lexeme may be an identifier.
            if is_letter(ch):
                state = "IDENT"

            # If the first character is a digit,
            # this lexeme may be an integer literal.
            elif is_digit(ch):
                state = "INT"

            # Any other first character is invalid.
            else:
                state = "ERROR"

        # ----------------------------------------------------
        # INT STATE
        # ----------------------------------------------------
        elif state == "INT":

            # An integer literal may continue only with digits.
            if is_digit(ch):
                state = "INT"

            # A letter or any other character makes it invalid.
            #
            # Example:
            # 123  -> INT_LIT
            # 1x   -> ERR_LEX
            else:
                state = "ERROR"

        # ----------------------------------------------------
        # IDENT STATE
        # ----------------------------------------------------
        elif state == "IDENT":

            # An identifier may contain letters or digits
            # after its first letter.
            #
            # Examples:
            # x
            # num
            # num1
            # ABC123
            if is_letter(ch) or is_digit(ch):
                state = "IDENT"

            # Characters such as _, -, +, @, etc. are invalid.
            else:
                state = "ERROR"

        # ----------------------------------------------------
        # ERROR STATE
        # ----------------------------------------------------
        elif state == "ERROR":

            # Once an invalid character is found, the lexeme
            # can never become valid again.
            #
            # Therefore, we can stop checking the remaining
            # characters.
            break

    # --------------------------------------------------------
    # DETERMINE THE FINAL TOKEN
    # --------------------------------------------------------

    # If the final state is INT, the lexeme contains
    # only digits.
    if state == "INT":
        return INT_LIT

    # If the final state is IDENT, check whether the
    # identifier is actually one of the IOL keywords.
    if state == "IDENT":

        # Keywords must match exactly and are case-sensitive.
        #
        # Example:
        # PRINT -> PRINT
        # print -> IDENT
        if text in KEYWORDS:
            return text

        # If it is not a keyword, it is a normal identifier.
        return IDENT

    # If the DFA ended in ERROR, the lexeme is invalid.
    return ERR_LEX


def scan(source):
    """Split source into lexemes and return a list of Lexeme objects."""

    # This list will contain all Lexeme objects found
    # in the source code.
    lexemes = []

    # Stores the characters of the lexeme currently being built.
    current = ""

    # IOL source lines start at line 1.
    line = 1

    # Read the entire source character by character.
    for ch in source:

        # Whitespace separates lexemes.
        #
        # This handles spaces, tabs, and newlines.
        if ch.isspace():

            # If we already collected characters, then
            # the current lexeme is complete.
            if current != "":

                # Classify the completed lexeme and create
                # a Lexeme object containing:
                #
                # text  -> the original characters
                # token -> its token type
                # line  -> its source line
                lexemes.append(
                    Lexeme(
                        text=current,
                        token=classify(current),
                        line=line
                    )
                )

                # Clear current so we can build the next lexeme.
                current = ""

            # A newline means the next lexeme belongs
            # to the next source line.
            if ch == "\n":
                line += 1

        else:
            # If the character is not whitespace, add it
            # to the current lexeme.
            current += ch

    # --------------------------------------------------------
    # HANDLE THE LAST LEXEME
    # --------------------------------------------------------

    # A file does not necessarily end with a newline.
    #
    # For example:
    #
    # IOL
    # INT x
    # LOI
    #
    # If LOI is the last character, it still needs to
    # be added to the list.
    if current != "":
        lexemes.append(
            Lexeme(
                text=current,
                token=classify(current),
                line=line
            )
        )

    # Return all lexemes in the same order they appeared
    # in the source code.
    return lexemes



if __name__ == "__main__":
    for word in ["PRINT", "print", "IOLx", "007", "-5", "1x", "my_var"]:
        print(word, "->", classify(word))
    for lx in scan("IOL\n\n  x @\nLOI"):
        print(lx)
