"""Compiler UI (IDE) for the Integer-Oriented Language (IOL).

The IDE lets the user create, open, edit, and save .iol files, compile the
code in the editor (lexical analysis for PE02), view the tokenized code, and
read the results in the built-in console and the table of variables.

All compiler work is done by compile_code() in compiler.py. This module only
collects input from the user and displays the results.
"""
import os
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont

# Use the real compiler once compiler.py and the modules it imports exist.
# Until then, a stub keeps the GUI usable.
# TODO(before submission): remove the fallback (see README.md).
try:
    from compiler import compile_code
    MISSING_MODULE = None
except ModuleNotFoundError as missing:
    if missing.name not in ("compiler", "lexer", "symbol_table", "reporter"):
        raise
    MISSING_MODULE = missing.name
    from tokens import CompileResult, Variable

    def compile_code(source, iol_path):
        """Temporary stub until compiler.py is ready."""
        return CompileResult(
            variables=[Variable("num", "INT"), Variable("msg1", "STR")],
            token_stream="IOL\nINT IDENT IS INT_LIT\nLOI",
            messages=["(stub) compile_code is not connected yet."],
        )


IDE_NAME = "IOL IDE"
SOURCE_EXT = ".iol"
DEFAULT_BASENAME = "untitled"
FILE_TYPES = [("IOL source files", "*.iol"), ("All files", "*.*")]

# Colors used in the editor gutter and console.
GUTTER_BG = "#f0f0f0"
GUTTER_FG = "#8a8a8a"
ERROR_FG = "#b00020"
INFO_FG = "#555555"

SHIFT_MASK = 0x0001   # Shift bit in a Tk key event's state


class IDE(tk.Tk):
    """Main window of the IOL IDE."""

    def __init__(self):
        super().__init__()
        self.current_path = None   # path of the open .iol file; None for new code
        self.last_result = None    # CompileResult of the last compile
        self.last_source = None    # editor text at the last compile
        self.token_window = None   # Show Tokenized Code window, if open

        self.title(IDE_NAME)
        self.geometry("1100x700")
        self.minsize(760, 480)
        self.code_font = self._pick_code_font()

        self._build_menu()
        self._build_layout()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        self._update_titles()
        self._refresh_editor_view()
        self.editor.focus_set()
        self.log(f"{IDE_NAME} ready. Open a .iol file (Ctrl+O) or start typing.", "info")
        if MISSING_MODULE:
            self.log(f"Note: {MISSING_MODULE}.py not found; Compile Code is using a stub.", "error")

    # ------------------------------------------------------------------
    # Window construction
    # ------------------------------------------------------------------
    def _pick_code_font(self):
        """Return a monospaced font, preferring common coding fonts."""
        families = set(tkfont.families(self))
        for name in ("Consolas", "Cascadia Mono", "Menlo", "DejaVu Sans Mono", "Courier New"):
            if name in families:
                return tkfont.Font(self, family=name, size=11)
        fallback = tkfont.nametofont("TkFixedFont").copy()
        fallback.configure(size=11)
        return fallback

    def _build_menu(self):
        """Create the File, Compile, and Execute menus."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open File...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        compile_menu = tk.Menu(menubar, tearoff=False)
        compile_menu.add_command(label="Compile Code", accelerator="F5", command=self.compile_action)
        compile_menu.add_command(label="Show Tokenized Code", accelerator="F6",
                                 command=self.show_tokenized_code)
        menubar.add_cascade(label="Compile", menu=compile_menu)

        execute_menu = tk.Menu(menubar, tearoff=False)
        execute_menu.add_command(label="Execute Code", accelerator="F7", command=self.execute_code)
        menubar.add_cascade(label="Execute", menu=execute_menu)

        self.config(menu=menubar)

    def _build_layout(self):
        """Create the editor, table of variables, console, and status bar."""
        self.status = ttk.Label(self, anchor="w", padding=(8, 2))
        self.status.pack(side="bottom", fill="x")

        outer = ttk.Panedwindow(self, orient="vertical")
        outer.pack(fill="both", expand=True, padx=6, pady=(6, 0))

        upper = ttk.Panedwindow(outer, orient="horizontal")
        outer.add(upper, weight=3)
        upper.add(self._build_editor(upper), weight=4)
        upper.add(self._build_variable_table(upper), weight=1)

        outer.add(self._build_console(outer), weight=1)

    def _build_editor(self, parent):
        """Create the tabbed code editor with a line-number gutter."""
        self.notebook = ttk.Notebook(parent)
        tab = ttk.Frame(self.notebook)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        self.gutter = tk.Canvas(tab, width=40, background=GUTTER_BG,
                                highlightthickness=0, borderwidth=0)
        # A small requested width lets the pane weights, not the default
        # 80-character width, decide how wide the editor is.
        self.editor = tk.Text(tab, wrap="none", undo=True, font=self.code_font, width=40,
                              borderwidth=0, padx=6, pady=4, tabs=self.code_font.measure("    "))
        y_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.editor.yview)
        x_scroll = ttk.Scrollbar(tab, orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=lambda *args: self._on_editor_scroll(y_scroll, *args),
                              xscrollcommand=x_scroll.set)

        self.gutter.grid(row=0, column=0, sticky="ns")
        self.editor.grid(row=0, column=1, sticky="nsew")
        y_scroll.grid(row=0, column=2, sticky="ns")
        x_scroll.grid(row=1, column=1, sticky="ew")

        self.notebook.add(tab, text=DEFAULT_BASENAME + SOURCE_EXT)

        self.editor.bind("<<Modified>>", lambda event: self._update_titles())
        for sequence in ("<KeyRelease>", "<ButtonRelease-1>", "<Configure>"):
            self.editor.bind(sequence, lambda event: self._refresh_editor_view(), add="+")
        return self.notebook

    def _build_variable_table(self, parent):
        """Create the Table of Variables (name and type)."""
        frame = ttk.LabelFrame(parent, text="Table of Variables", padding=4)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Size rows from the font so they do not overlap on high-DPI displays.
        row_height = tkfont.nametofont("TkDefaultFont").metrics("linespace") + 6
        ttk.Style(self).configure("Treeview", rowheight=row_height)

        self.var_table = ttk.Treeview(frame, columns=("name", "type"), show="headings",
                                      selectmode="browse")
        self.var_table.heading("name", text="Name")
        self.var_table.heading("type", text="Type")
        self.var_table.column("name", width=140, anchor="w")
        self.var_table.column("type", width=70, anchor="center", stretch=False)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.var_table.yview)
        self.var_table.configure(yscrollcommand=scroll.set)

        self.var_table.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        return frame

    def _build_console(self, parent):
        """Create the read-only built-in console."""
        frame = ttk.LabelFrame(parent, text="Console", padding=4)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.console = tk.Text(frame, height=9, wrap="word", font=self.code_font,
                               state="disabled", borderwidth=0, padx=6, pady=4,
                               background="#fbfbfb")
        self.console.tag_configure("error", foreground=ERROR_FG)
        self.console.tag_configure("info", foreground=INFO_FG)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=scroll.set)

        self.console.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        return frame

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts for the menu items.

        Letter shortcuts are bound in both cases so they still work with
        Caps Lock on (Tk then reports Ctrl+N as Control-N).
        """
        shortcuts = {
            "<Control-n>": self.new_file,
            "<Control-N>": self.new_file,
            "<Control-o>": self.open_file,
            "<Control-O>": self.open_file,
            "<F5>": self.compile_action,
            "<F6>": self.show_tokenized_code,
            "<F7>": self.execute_code,
        }
        for sequence, command in shortcuts.items():
            self._bind_key(sequence, lambda event, command=command: command())

        # With Caps Lock, Ctrl+S and Ctrl+Shift+S swap letter case, so the
        # Shift key is checked directly instead of relying on the letter case.
        for sequence in ("<Control-s>", "<Control-S>"):
            self._bind_key(sequence, self._save_shortcut)

    def _bind_key(self, sequence, handler):
        """Bind a shortcut on the window and the editor.

        The binding returns "break" so the Text widget's own key behavior
        (e.g. Ctrl+O inserting a line on some systems) does not run.
        """
        def wrapper(event):
            handler(event)
            return "break"
        self.bind(sequence, wrapper)
        self.editor.bind(sequence, wrapper)

    def _save_shortcut(self, event):
        """Ctrl+S runs Save; Ctrl+Shift+S runs Save As."""
        if event.state & SHIFT_MASK:
            self.save_file_as()
        else:
            self.save_file()

    # ------------------------------------------------------------------
    # Editor helpers
    # ------------------------------------------------------------------
    def get_code(self):
        """Return the editor text without the newline Tk always keeps at the end."""
        return self.editor.get("1.0", "end-1c")

    def _set_code(self, text):
        """Replace the editor contents and mark them as unmodified."""
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self.editor.mark_set("insert", "1.0")
        self.editor.see("1.0")
        self._refresh_editor_view()

    def _file_name(self):
        """Return the display name of the current file."""
        if self.current_path:
            return os.path.basename(self.current_path)
        return DEFAULT_BASENAME + SOURCE_EXT

    def _update_titles(self):
        """Show the file name in the window title and tab label (* = unsaved)."""
        name = self._file_name()
        marker = "*" if self.editor.edit_modified() else ""
        self.notebook.tab(0, text=marker + name)
        self.title(f"{IDE_NAME} - {marker}{name}")

    def _on_editor_scroll(self, scrollbar, first, last):
        scrollbar.set(first, last)
        self._redraw_gutter()

    def _refresh_editor_view(self):
        self._redraw_gutter()
        line, column = self.editor.index("insert").split(".")
        self.status.configure(text=f"Ln {line}, Col {int(column) + 1}")

    def _redraw_gutter(self):
        """Draw line numbers for the lines currently visible in the editor."""
        self.gutter.delete("all")
        last_line = int(self.editor.index("end-1c").split(".")[0])
        width = self.code_font.measure("0" * max(3, len(str(last_line)))) + 14
        self.gutter.configure(width=width)

        index = self.editor.index("@0,0")
        while True:
            info = self.editor.dlineinfo(index)
            if info is None:
                break
            line_number = index.split(".")[0]
            self.gutter.create_text(width - 6, info[1], anchor="ne", text=line_number,
                                    font=self.code_font, fill=GUTTER_FG)
            next_index = self.editor.index(f"{index}+1line")
            if next_index == index:
                break
            index = next_index

    # ------------------------------------------------------------------
    # Console and table helpers
    # ------------------------------------------------------------------
    def log(self, text, tag=None):
        """Append one line to the console."""
        self.console.configure(state="normal")
        self.console.insert("end", text + "\n", tag or ())
        self.console.configure(state="disabled")
        self.console.see("end")

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def show_variables(self, variables):
        """Replace the rows of the Table of Variables."""
        self.clear_variables()
        for variable in variables:
            self.var_table.insert("", "end", values=(variable.name, variable.type))

    def clear_variables(self):
        self.var_table.delete(*self.var_table.get_children())

    def _reset_results(self):
        """Forget the last compile and clear its displays."""
        self.last_result = None
        self.last_source = None
        self.clear_variables()
        self.clear_console()
        if self.token_window is not None and self.token_window.winfo_exists():
            self.token_window.destroy()
        self.token_window = None

    # ------------------------------------------------------------------
    # File menu
    # ------------------------------------------------------------------
    def confirm_discard_changes(self):
        """Ask to save unsaved changes. Return True if it is safe to continue."""
        if not self.editor.edit_modified():
            return True
        answer = messagebox.askyesnocancel(
            "Unsaved changes", f"Save changes to {self._file_name()}?", parent=self)
        if answer is None:        # Cancel
            return False
        if answer:                # Yes
            return self.save_file()
        return True               # No: discard

    def new_file(self):
        if not self.confirm_discard_changes():
            return
        self.current_path = None
        self._set_code("")
        self._reset_results()
        self._update_titles()
        self.log("New file created.", "info")

    def open_file(self):
        if not self.confirm_discard_changes():
            return
        path = filedialog.askopenfilename(parent=self, title="Open IOL File", filetypes=FILE_TYPES)
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as source_file:
                text = source_file.read()
        except (OSError, UnicodeDecodeError) as err:
            messagebox.showerror("Open File", f"Could not open the file:\n{err}", parent=self)
            return
        self.current_path = path
        self._set_code(text)
        self._reset_results()
        self._update_titles()
        self.log(f"Opened {self._file_name()}.", "info")

    def save_file(self):
        """Save to the current file, or to a default file name for new code.

        Returns True if the code was saved.
        """
        if self.current_path:
            return self._write_file(self.current_path)
        path = self._next_default_path()
        if self._write_file(path):
            self.log(f"Saved as {os.path.basename(path)} in {os.path.dirname(path)}.", "info")
            return True
        return False

    def save_file_as(self):
        """Save to a file name chosen by the user. Returns True if saved."""
        path = filedialog.asksaveasfilename(
            parent=self, title="Save IOL File As", defaultextension=SOURCE_EXT,
            filetypes=FILE_TYPES, initialfile=self._file_name())
        if not path:
            return False
        if self._write_file(path):
            self.log(f"Saved as {os.path.basename(path)}.", "info")
            return True
        return False

    def _next_default_path(self):
        """Return untitled.iol, untitled1.iol, ... in the working folder, whichever is free."""
        folder = os.getcwd()
        number = 0
        while True:
            suffix = str(number) if number else ""
            path = os.path.join(folder, DEFAULT_BASENAME + suffix + SOURCE_EXT)
            if not os.path.exists(path):
                return path
            number += 1

    def _write_file(self, path):
        """Write the editor text to path. Returns True on success."""
        try:
            with open(path, "w", encoding="utf-8") as source_file:
                source_file.write(self.get_code())
        except OSError as err:
            messagebox.showerror("Save File", f"Could not save the file:\n{err}", parent=self)
            return False
        self.current_path = path
        self.editor.edit_modified(False)
        self._update_titles()
        return True

    def exit_app(self):
        if self.confirm_discard_changes():
            self.destroy()

    # ------------------------------------------------------------------
    # Compile menu
    # ------------------------------------------------------------------
    def compile_action(self):
        """Save the code, run compile_code(), and display the results."""
        if not self.save_file():
            self.log("Compile cancelled: the code could not be saved.", "error")
            return
        source = self.get_code()

        self.clear_console()
        self.clear_variables()
        self.log(f"Compiling {self._file_name()}...", "info")
        try:
            result = compile_code(source, self.current_path)
        except Exception:   # show teammates' errors in the IDE instead of crashing silently
            self.last_result = None
            self.log("Internal error during compilation:", "error")
            self.log(traceback.format_exc().rstrip(), "error")
            return

        for message in result.messages:
            self.log(message, self._message_tag(message, result.has_errors))
        self.show_variables(result.variables)
        self.last_result = result
        self.last_source = source
        if self.token_window is not None and self.token_window.winfo_exists():
            self.show_tokenized_code()   # keep an open tokenized view up to date

    @staticmethod
    def _message_tag(message, has_errors):
        """Return "error" for console lines that report a problem.

        Relies on the message formats in reporter.py (task guide, Section 8).
        """
        if message.startswith("Line ") or message.startswith("Could not save"):
            return "error"
        if has_errors and message.endswith("error(s) found."):
            return "error"
        return None

    def show_tokenized_code(self):
        """Display the token stream from the last compile in its own window."""
        if self.last_result is None:
            self.log("Nothing compiled yet. Use Compile Code (F5) first.", "info")
            return
        if self.get_code() != self.last_source:
            self.log("The code changed since the last compile. Showing the last compiled "
                     "version; press F5 to recompile.", "info")

        if self.last_result.tkn_path:
            name = os.path.basename(self.last_result.tkn_path)
        else:
            name = os.path.splitext(self._file_name())[0] + ".tkn"

        if self.token_window is None or not self.token_window.winfo_exists():
            self._create_token_window()
        self.token_window.title(f"Tokenized Code - {name}")

        lines = self.last_result.token_stream.split("\n")
        width = len(str(len(lines)))
        viewer = self.token_viewer
        viewer.configure(state="normal")
        viewer.delete("1.0", "end")
        for number, line in enumerate(lines, start=1):
            viewer.insert("end", f"{number:>{width}}  ", "lineno")
            viewer.insert("end", line + ("\n" if number < len(lines) else ""))
        viewer.configure(state="disabled")
        self.token_window.deiconify()
        self.token_window.lift()

    def _create_token_window(self):
        window = tk.Toplevel(self)
        window.geometry("640x420")
        window.transient(self)
        frame = ttk.Frame(window, padding=6)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        viewer = tk.Text(frame, wrap="none", font=self.code_font, state="disabled",
                         borderwidth=0, padx=6, pady=4)
        viewer.tag_configure("lineno", foreground=GUTTER_FG)
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=viewer.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=viewer.xview)
        viewer.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        viewer.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        window.bind("<Escape>", lambda event: window.destroy())
        self.token_window = window
        self.token_viewer = viewer

    # ------------------------------------------------------------------
    # Execute menu
    # ------------------------------------------------------------------
    def execute_code(self):
        """Placeholder: program execution is implemented in a later PE."""
        self.log("Execute Code is not part of PE02 (lexical analysis only).", "info")
