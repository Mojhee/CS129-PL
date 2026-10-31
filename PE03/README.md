# Predictive Parser — PE03 Non-Recursive Predictive Parsing

CMSC 129, Programming Exercise 03. A desktop program that checks whether a
sequence of tokens is valid under a grammar, using a **non-recursive predictive
(LL(1)) parser**. The grammar is given as a productions file (`.prod`) and a
parse table file (`.ptbl`). Every parsing step is shown in a table and saved to
a `.prsd` file.

Written in Python 3 with Tkinter, using the standard library only.

## Group members

| Member | Task | Files |
|---|---|---|
| Estroga, Ezra Aneurin | Task 1: User interface and program flow | `main.py`, `gui.py` |
| Guillen, Luigi Antonio | Task 3: Parser engine, documentation assembly | `parser.py` |
| Senoy, Kyle Howard | Task 4: Output file, tests, integration, executable | `output.py`, `tests/` |
| Tabon, Jeycel Ann | Task 2: Loading and checking the files | `models.py`, `loaders.py` |

## Requirements

- Python 3.10 or newer, with **tkinter**. No pip packages are needed.
  - **Windows / macOS (python.org installer):** tkinter is included.
  - **Linux:** install it separately if needed, e.g. `sudo apt install python3-tk`.
- To check that tkinter works, run `python -c "import tkinter; tkinter._test()"`.

## How to run

From this folder:

```
python main.py
```

On some systems the command is `py` or `python3` instead of `python`.

## Using the program

1. **Load the files.** Click **Load** and pick a `.prod` file, then click
   **Load** again and pick the `.ptbl` file with the same name (for example
   `rules.prod` and `rules.ptbl`). Files can be loaded from any folder, in any
   order. LOADED shows the most recently loaded file.
2. **Type the input.** Enter the tokens in the INPUT field, separated by spaces
   (for example `id + id * id`). Do not type `$`; it is added automatically.
3. **Parse.** Click **Parse** (or press Enter) and type an output name when
   asked. The solution table shows every step, and PARSING shows whether the
   input is Valid or Invalid.
4. **Read the output file.** The steps are saved as `outname_prodname.prsd` in
   the same folder as the `.prod` file (for example `test_rules.prsd`).

Rules the program follows:

- Parse is enabled only when both a `.prod` and a `.ptbl` file are loaded.
- Every Load attempt clears the solution table and the PARSING message, even
  when it is cancelled or fails.
- A failed or cancelled load keeps the previously loaded file of that type.
- A successful load replaces only the display of that file type.
- The `.prod` and `.ptbl` files must have the same name and must match each
  other, or Parse shows a message instead of parsing.

## Input and output files

All files are CSV.

**`.prod`** — one production per line: number, non-terminal, production.
Symbols in the production are separated by spaces, and `e` is the empty
production. The first line's non-terminal is the start symbol.

```
1,E,T E'
2,E',+ T E'
3,E',e
```

**`.ptbl`** — the first row is a blank cell followed by the terminals and `$`.
Each later row is a non-terminal followed by a production number or a blank
cell for each terminal.

```
,id,+,*,(,),$
E,1,,,1,,
E',,2,,,3,3
```

**`.prsd`** — one row per step: stack (top on the left), input buffer, and
action. The first row is the starting state and has no action. A valid parse
ends with `,,Match $`; an invalid parse ends with an `Error: ...` row.

```
E $,id + id * id $
T E' $,id + id * id $,Output E > T E'
...
,,Match $
```

## Files

| File | Contents |
|---|---|
| `main.py` | Entry point; opens the window. |
| `gui.py` | Tkinter window: Load, Parse, and all displays. |
| `models.py` | Shared data classes and constants used by every module. |
| `loaders.py` | Reads and checks `.prod` and `.ptbl` files. |
| `parser.py` | Splits the input into tokens and runs the parser. |
| `output.py` | Builds the output file name and writes the `.prsd` file. |
| `tests/` | Sample grammars, broken files, and expected outputs. |
| `stubs.py` | **Temporary.** Fake versions of `loaders.py`, `parser.py`, and `output.py`, used by `gui.py` until the real modules are merged. Delete before submission. |

## Building the executable

On the build computer only:

```
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name PE03_Parser main.py
```

The executable is written to `dist/PE03_Parser.exe`.
