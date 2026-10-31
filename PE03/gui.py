"""User interface of the non-recursive predictive parser (PE03).

The window lets the user load a productions file (.prod) and a parse table
file (.ptbl) with one Load button, type a token sequence, and parse it. The
loaded files, the parsing steps, and the result are shown in the window, and
the steps are saved to an outname_prodname.prsd file.

Reading files, parsing, and writing the output are done by loaders.py,
parser.py, and output.py. This module only collects input from the user,
calls those functions, and displays the results.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from models import FileFormatError

try:
    from loaders import (load_productions, load_parse_table,
                         check_compatible, same_name)
    from parser import tokenize_input, parse
    from output import clean_outname, output_path, write_prsd
except ImportError:
    from stubs import *   # temporary fake versions; do not submit


APP_NAME = "Predictive Parser"   # shown in the title bar
FILE_TYPES = [("Grammar files", "*.prod *.ptbl"),
              ("Productions", "*.prod"), ("Parse tables", "*.ptbl")]
PROD_EXT = ".prod"
PTBL_EXT = ".ptbl"
MAX_PROBLEMS_SHOWN = 5   # compatibility problems listed in one error box

# Colors of the PARSING message.
VALID_FG = "#1b7f3b"
INVALID_FG = "#b00020"
INFO_FG = "#555555"


class ParserApp(tk.Tk):
    """Main window of the predictive parser."""

    def __init__(self):
        """Build the window and show it with nothing loaded."""
        super().__init__()
        self.productions = None   # Productions object, or None until a .prod loads
        self.table = None         # ParseTable object, or None until a .ptbl loads

        self.title(APP_NAME)
        self.geometry("1000x720")
        self.minsize(720, 560)

        self._build_layout()
        self._update_parse_button()
        self.input_entry.focus_set()

    # ------------------------------------------------------------------
    # Window construction
    # ------------------------------------------------------------------
    def _build_layout(self):
        """Create every area of the suggested interface on a grid.

        Row 0: Productions (left) and Parse Table (right)
        Row 1: LOADED message and Load button
        Row 2: INPUT field and Parse button
        Row 3: PARSING message
        Row 4: solution table
        """
        # The two top panels share the width equally. When the window is
        # resized, the extra height goes to the top tables and the solution.
        self.columnconfigure(0, weight=1, uniform="top")
        self.columnconfigure(1, weight=1, uniform="top")
        self.rowconfigure(0, weight=2)
        self.rowconfigure(4, weight=3)
        pad = {"padx": 8, "pady": 4}

        self._build_productions_panel().grid(row=0, column=0, sticky="nsew", **pad)
        self._build_table_panel().grid(row=0, column=1, sticky="nsew", **pad)

        # LOADED message on the left, the single Load button on the right.
        load_row = ttk.Frame(self)
        load_row.grid(row=1, column=0, columnspan=2, sticky="ew", **pad)
        load_row.columnconfigure(0, weight=1)
        self.loaded_label = ttk.Label(load_row, text="LOADED:")
        self.loaded_label.grid(row=0, column=0, sticky="w")
        ttk.Button(load_row, text="Load", command=self.load_file).grid(row=0, column=1)

        # INPUT label, the token field (stretches with the window), and Parse.
        input_row = ttk.Frame(self)
        input_row.grid(row=2, column=0, columnspan=2, sticky="ew", **pad)
        input_row.columnconfigure(1, weight=1)
        ttk.Label(input_row, text="INPUT:").grid(row=0, column=0, padx=(0, 6))
        self.input_entry = ttk.Entry(input_row)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self.input_entry.bind("<Return>", self._on_enter)
        # Parse starts disabled; _update_parse_button enables it later.
        self.parse_button = ttk.Button(input_row, text="Parse", command=self.parse_input)
        self.parse_button.grid(row=0, column=2)

        # Result or problem message of the last parse.
        self.parsing_label = ttk.Label(self, text="PARSING:")
        self.parsing_label.grid(row=3, column=0, columnspan=2, sticky="w", **pad)

        self._build_solution_panel().grid(row=4, column=0, columnspan=2, sticky="nsew",
                                          padx=8, pady=(4, 8))

    def _scrolled_tree(self, parent, columns, horizontal=False):
        """Return (frame, tree): a headings-only Treeview with scrollbars in a frame."""
        frame = ttk.Frame(parent)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=y_scroll.set)
        if horizontal:
            x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            x_scroll.grid(row=1, column=0, sticky="ew")
            tree.configure(xscrollcommand=x_scroll.set)
        return frame, tree

    def _panel_header(self, parent, title):
        """Add a "title  file name" header row to a panel; return the file name label."""
        header = ttk.Frame(parent)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(header, text=title, font=("TkDefaultFont", 10, "bold")).pack(side="left")
        name_label = ttk.Label(header, text="", foreground=INFO_FG)
        name_label.pack(side="left", padx=(8, 0))
        return name_label

    def _build_productions_panel(self):
        """Create the Productions panel: columns ID, NT, P."""
        panel = ttk.Frame(self)
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)
        self.prod_name_label = self._panel_header(panel, "Productions:")

        frame, self.prod_view = self._scrolled_tree(panel, ("id", "nt", "p"))
        frame.grid(row=1, column=0, sticky="nsew")
        for column, text, width, anchor in (("id", "ID", 40, "center"),
                                             ("nt", "NT", 60, "center"),
                                             ("p", "P", 200, "w")):
            self.prod_view.heading(column, text=text)
            self.prod_view.column(column, width=width, anchor=anchor,
                                  stretch=(column == "p"))
        return panel

    def _build_table_panel(self):
        """Create the Parse Table panel. Its columns are rebuilt on every load."""
        panel = ttk.Frame(self)
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)
        self.table_name_label = self._panel_header(panel, "Parse Table:")

        frame, self.table_view = self._scrolled_tree(panel, ("nt",), horizontal=True)
        frame.grid(row=1, column=0, sticky="nsew")
        self.table_view.heading("nt", text="")
        return panel

    def _build_solution_panel(self):
        """Create the solution table: columns Stack, Input Buffer, Action."""
        frame, self.solution_view = self._scrolled_tree(self, ("stack", "buffer", "action"))
        # Headings are centered; the Stack and Input Buffer cells are
        # right-aligned like the handout's sample.
        for column, text, anchor in (("stack", "Stack", "e"),
                                     ("buffer", "Input Buffer", "e"),
                                     ("action", "Action", "w")):
            self.solution_view.heading(column, text=text, anchor="center")
            self.solution_view.column(column, width=250, anchor=anchor)
        return frame

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    def _show_productions(self, productions):
        """Fill the Productions table with one row per production."""
        view = self.prod_view
        view.delete(*view.get_children())
        for production in productions.items.values():
            view.insert("", "end", values=(production.number, production.head,
                                           " ".join(production.body)))
        self.prod_name_label.config(text=os.path.basename(productions.path))

    def _show_parse_table(self, table):
        """Rebuild the Parse Table columns from the terminals and fill its rows.

        Generated column ids (t0, t1, ...) are used instead of the terminal
        names, because a terminal such as # or $ is not a safe Treeview column id.
        """
        view = self.table_view
        view.delete(*view.get_children())
        columns = ["nt"] + [f"t{i}" for i in range(len(table.terminals))]
        view["columns"] = columns
        view.heading("nt", text="")
        view.column("nt", width=60, anchor="w", stretch=False)
        for column, terminal in zip(columns[1:], table.terminals):
            view.heading(column, text=terminal)
            view.column(column, width=45, anchor="center", stretch=False)
        for nt in table.nonterminals:
            row = [nt] + [table.cells.get((nt, t), "") for t in table.terminals]
            view.insert("", "end", values=row)
        self.table_name_label.config(text=os.path.basename(table.path))

    def _show_solution(self, steps):
        """Fill the solution table with one row per ParseStep."""
        view = self.solution_view
        view.delete(*view.get_children())
        for step in steps:
            view.insert("", "end", values=(step.stack, step.buffer, step.action))

    def _set_parsing(self, text, color=INFO_FG):
        """Show text after "PARSING:" in the given color."""
        self.parsing_label.config(text=f"PARSING: {text}".rstrip(), foreground=color)

    def _clear_solution(self):
        """Empty the solution table and the PARSING message."""
        self.solution_view.delete(*self.solution_view.get_children())
        self._set_parsing("")

    def _update_parse_button(self):
        """Enable Parse only when both a .prod and a .ptbl file are loaded."""
        if self.productions and self.table:
            self.parse_button.state(["!disabled"])
        else:
            self.parse_button.state(["disabled"])

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    def load_file(self):
        """Load button: ask for a .prod or .ptbl file and load it.

        Every attempt clears the solution first, even a cancelled or failed one.
        A failed load keeps the previously loaded file of that type.
        """
        self._clear_solution()
        path = filedialog.askopenfilename(parent=self, title="Load",
                                          filetypes=FILE_TYPES)
        if not path:
            return   # cancelled
        self.load_path(path)

    def load_path(self, path):
        """Load the file at path by its extension. Return True on success."""
        name = os.path.basename(path)
        extension = os.path.splitext(path)[1].lower()
        if extension not in (PROD_EXT, PTBL_EXT):
            messagebox.showerror(APP_NAME, "Only .prod and .ptbl files can be loaded.",
                                 parent=self)
            return False

        try:
            if extension == PROD_EXT:
                loaded = load_productions(path)
            else:
                loaded = load_parse_table(path)
        except FileFormatError as error:
            messagebox.showerror(APP_NAME, f"{name} was not loaded.\n\n{error}", parent=self)
            return False
        except OSError as error:
            messagebox.showerror(APP_NAME, f"{name} could not be read.\n\n{error.strerror or error}",
                                 parent=self)
            return False

        # Only a successful load replaces the file (and display) of its type.
        if extension == PROD_EXT:
            self.productions = loaded
            self._show_productions(loaded)
        else:
            self.table = loaded
            self._show_parse_table(loaded)
        self.loaded_label.config(text=f"LOADED: {name}")
        self._update_parse_button()
        return True

    # ------------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------------
    def _on_enter(self, event=None):
        """Enter in the INPUT field runs Parse when the button is enabled."""
        if self.parse_button.instate(["!disabled"]):
            self.parse_input()

    def _ask_outname(self):
        """Ask for the output file name until it is usable. Return None if cancelled."""
        while True:
            answer = simpledialog.askstring("Output file", "Output file name:", parent=self)
            if answer is None:
                return None
            try:
                return clean_outname(answer)
            except ValueError as error:
                messagebox.showerror(APP_NAME, str(error), parent=self)

    def parse_input(self):
        """Parse button: check the input and files, parse, save, and show the result."""
        # The button is disabled without both files; this also guards the Enter key.
        if not (self.productions and self.table):
            return
        self._clear_solution()

        # 1. The input must not be empty or only spaces.
        text = self.input_entry.get()
        if not text.strip():
            self._set_parsing("Enter an input first.", INVALID_FG)
            return

        # 2. The .prod and .ptbl files must have the same name (rules.prod, rules.ptbl).
        prod_name = os.path.basename(self.productions.path)
        ptbl_name = os.path.basename(self.table.path)
        if not same_name(self.productions.path, self.table.path):
            self._set_parsing(f"{prod_name} and {ptbl_name} do not have the same name.",
                              INVALID_FG)
            return

        # 3. The two files must agree with each other; list the first few problems.
        problems = check_compatible(self.productions, self.table)
        if problems:
            shown = problems[:MAX_PROBLEMS_SHOWN]
            if len(problems) > len(shown):
                shown.append(f"... and {len(problems) - len(shown)} more.")
            messagebox.showerror(APP_NAME, f"{prod_name} and {ptbl_name} do not match:\n\n"
                                 + "\n".join(shown), parent=self)
            self._set_parsing(f"{prod_name} and {ptbl_name} do not match.", INVALID_FG)
            return

        # 4. Split the input into tokens. This is done before asking for a
        #    name, so a typed $ is reported right away.
        try:
            tokens = tokenize_input(text)
        except ValueError as error:
            self._set_parsing(str(error), INVALID_FG)
            return

        # 5. Ask for the output name; cancelling stops without parsing.
        outname = self._ask_outname()
        if outname is None:
            return

        # 6. Run the parser and show every step, valid or not.
        result = parse(tokens, self.productions, self.table)
        self._show_solution(result.steps)

        # 7. Save the steps as outname_prodname.prsd next to the .prod file.
        path = output_path(outname, self.productions.path)
        file_name = os.path.basename(path)
        verdict = "Valid" if result.valid else "Invalid"
        color = VALID_FG if result.valid else INVALID_FG
        try:
            write_prsd(result, path)
        except OSError as error:
            # The solution is still shown even if the file could not be saved.
            messagebox.showerror(APP_NAME, f"{file_name} could not be saved.\n\n"
                                 f"{error.strerror or error}", parent=self)
            self._set_parsing(f"{verdict}. {file_name} could not be saved.", color)
            return
        self._set_parsing(f"{verdict}. Please see {file_name}.", color)
