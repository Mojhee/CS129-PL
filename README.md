# IOL IDE — PE02 Lexical Analysis

## Requirements

- Python 3.10 or newer, with **tkinter**. No pip packages are needed.
  - **Windows / macOS (python.org installer):** tkinter is included. On Windows,
    keep "tcl/tk and IDLE" checked during installation (it is checked by default).
  - **Linux:** install it separately if needed, e.g. `sudo apt install python3-tk`.
  - **macOS (Homebrew Python):** `brew install python-tk`.
- Check it works: `python -c "import tkinter; tkinter._test()"`.
  A small window should appear.

## How to run

From this folder:

```
python main.py
```

(On some systems the command is `py main.py` or `python3 main.py`.)
In VS Code, you can also open `main.py` and click **Run Python File**.

| Action | Shortcut |
|---|---|
| New / Open / Save / Save As | Ctrl+N / Ctrl+O / Ctrl+S / Ctrl+Shift+S |
| Compile Code | F5 |
| Show Tokenized Code | F6 |
| Execute Code (not part of PE02) | F7 |

Compile saves the code first. New code is saved as `untitled.iol` in the folder
you ran the program from. The `.tkn` file is written next to the `.iol` file.

Until `compiler.py`, `lexer.py`, `symbol_table.py`, and `reporter.py` are in this
folder, Compile Code uses a stub with fixed output, and the console says so.

## Before submission (Task 1)

- [ ] **Remove the stub fallback in `gui.py`.** Replace the whole `try/except`
      block at the top with `from compiler import compile_code`, and delete the
      two `MISSING_MODULE` lines in `IDE.__init__`.
- [ ] Run all files in `tests/` through the IDE.
- [ ] Build the executable on Windows:
      `pip install pyinstaller`, then
      `python -m PyInstaller --onefile --windowed --name IOL_IDE main.py`.
      Copy `dist/IOL_IDE.exe` to another folder and check that it runs.
- [ ] Leave `__pycache__/`, `build/`, `dist/`, and `.spec` files out of the
      source folder in the zip.
