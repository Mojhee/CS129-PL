# IOL IDE — PE02 Lexical Analysis

CMSC 129, Programming Exercise 02. A desktop IDE for the **Integer-Oriented
Language (IOL)** that performs lexical analysis: it splits IOL source code into
tokens, writes the token stream to a `.tkn` file, reports unknown words with
their line numbers, and lists the defined variables.

Written in Python 3 with Tkinter, using the standard library only.

## Group members

| Member | Task | Files |
|---|---|---|
| Estroga, Ezra Aneurin | Task 1: GUI, integration, packaging | `main.py`, `gui.py`, `tokens.py` |
| Guillen, Luigi Antonio | Task 3: Variable table, documentation assembly | `symbol_table.py` |
| Senoy, Kyle Howard | Task 4: Output, compile pipeline, tests | `reporter.py`, `compiler.py`, `tests/` |
| Tabon, Jeycel Ann | Task 2: Lexer | `lexer.py` |

## Requirements

- Python 3.10 or newer, with **tkinter**. No pip packages are needed.
  - **Windows / macOS (python.org installer):** tkinter is included. On Windows,
    keep "tcl/tk and IDLE" checked during installation (it is checked by default).
  - **Linux:** install it separately if needed, e.g. `sudo apt install python3-tk`.
  - **macOS (Homebrew Python):** `brew install python-tk`.
- To check that tkinter works, run `python -c "import tkinter; tkinter._test()"`.
  A small window should appear.

## How to run

From this folder:

```
python main.py
```

On some systems the command is `py` or `python3` instead of `python`.

## How to test

From this folder:

```
python3 -m unittest tests.test_compile -v
```

All 10 tests should pass. They call `compile_code()` and the reporter functions
directly, without the GUI. They cover a clean program, blank lines, a missing
final newline, empty source, case-sensitive keywords, unknown words with line
numbers, the `.tkn` file location, a folder that cannot be written to, and the
return values of `build_messages` and `write_tkn`.

`lexer.py` and `symbol_table.py` also have self-tests: run `python lexer.py` or
`python symbol_table.py`.

## Using the IDE

1. **Open or write code.** Use File > Open File to load a `.iol` file, or type in
   the editor. File > New File starts empty code named `untitled.iol`.
2. **Compile Code (F5).** The code is saved first, then analyzed. The results
   appear in three places:
   - **Console:** a success message, or one line per unknown word with its line
     number (in red) followed by the error count.
   - **Table of Variables:** the name and type of each defined variable.
   - **`.tkn` file:** the token stream, saved next to the `.iol` file.
3. **Show Tokenized Code (F6).** Opens a window with the token stream from the
   last compile.

| Menu | Item | Shortcut |
|---|---|---|
| File | New File / Open File | Ctrl+N / Ctrl+O |
| File | Save / Save As | Ctrl+S / Ctrl+Shift+S |
| File | Exit | — |
| Compile | Compile Code | F5 |
| Compile | Show Tokenized Code | F6 |
| Execute | Execute Code (not part of PE02) | F7 |

**Saving and files:**
- Save on new code uses a default name in the folder you ran the program from:
  `untitled.iol`, then `untitled1.iol`, `untitled2.iol`, and so on.
- The editor tab and the title bar show the file name. A `*` means there are
  unsaved changes.
- New File, Open File, and Exit ask before discarding unsaved changes.

## Lexical rules

Lexemes are separated by whitespace (spaces, tabs, newlines). Keywords are
case-sensitive. Each lexeme gets one token:

| Token | Rule | Examples |
|---|---|---|
| Keyword (the keyword itself) | Exact match with one of the 14 keywords | `IOL`, `PRINT`, `NEWLN` |
| `INT_LIT` | Digits only | `0`, `007`, `42` |
| `IDENT` | A letter, then letters or digits (a–z, A–Z, 0–9 only) | `num`, `msg1`, `print`, `IOLx` |
| `ERR_LEX` | Anything else | `-5`, `1x`, `my_var`, `@` |

Keywords: `IOL LOI INT STR IS INTO BEG PRINT ADD SUB MULT DIV MOD NEWLN`

A variable is defined by `INT` or `STR` followed by an identifier, e.g.
`INT num IS 0` or `STR msg1`. If a name is defined twice, only the first
definition is listed.

**Example.** Compiling `errors.iol`:

```
Line 4: unknown word 'my_var'
Line 5: unknown word '1x'
Line 6: unknown word '-5'
Line 6: unknown word '@'
errors.iol: 4 lexical error(s) found.
Token stream saved to errors.tkn.
```

Without errors, the console shows
`valid.iol: lexical analysis completed with no errors found.`

In the `.tkn` file, each lexeme is replaced by its token name. Line N of the
`.tkn` file matches line N of the `.iol` file, and blank lines are kept:

```
IOL                           IOL
INT num IS 0                  INT IDENT IS INT_LIT
PRINT -5                      PRINT ERR_LEX
LOI                           LOI
```

## Project structure

```
main.py           Entry point: opens the IDE
gui.py            Tkinter IDE: editor, menus, console, Table of Variables
tokens.py         Shared token names, keywords, and data classes
compiler.py       compile_code(): runs the whole compile pipeline
lexer.py          scan() and classify(): character-by-character scanner with a DFA
symbol_table.py   build_variable_table(): finds variable definitions
reporter.py       Token stream, console messages, and writing the .tkn file
tests/            Unit tests and sample .iol files
```

**What happens when you press Compile Code:**

```
gui.py         compile_action()  saves the code, then calls compile_code
compiler.py    compile_code(source, iol_path)                  -> CompileResult
  lexer.py         scan(source)                                -> list[Lexeme]
  symbol_table.py  build_variable_table(lexemes)               -> list[Variable]
  reporter.py      to_token_stream(lexemes, line_count)        -> str
  reporter.py      build_messages(lexemes, filename)           -> (list[str], bool)
  reporter.py      write_tkn(token_stream, iol_path)           -> str (.tkn path)
gui.py         shows the messages, the variables, and keeps the token stream for F6
```

These function names, parameters, and return values are the group's shared
contract (task guide, Section 4). The shared data classes `Lexeme`, `Variable`,
and `CompileResult` are in `tokens.py`.

**Sample files in `tests/`:**

| File | Expected result |
|---|---|
| `valid.iol` | No errors. Variables: `num INT`, `res INT`, `msg1 STR`. |
| `errors.iol` | 4 errors, on lines 4, 5, and 6. Variables: `x INT`. |
| `empty.iol` | No errors, an empty `.tkn` file, and no variables. |

## Building the executable

On Windows:

```
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name IOL_IDE main.py
```

The executable is created at `dist/IOL_IDE.exe`. Copy it to another folder and
check that it runs. `build/`, `dist/`, `*.spec`, `*.tkn`, and `__pycache__/` are
ignored by git.

## Before submission

- [ ] Run the unit tests and compile every file in `tests/` through the IDE.
- [ ] Build the executable and check it on another folder.
- [ ] Zip the documentation, the source files with `tests/`, and the executable as
      `Estroga_Guillen_Senoy_Tabon_PE02.zip`. Leave out `__pycache__/`, `build/`,
      and `.spec` files.
