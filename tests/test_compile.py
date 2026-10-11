"""Unit tests for the IOL lexical analyzer (PE02).

Run from the project folder:  python3 -m unittest tests.test_compile -v

The tests call compile_code() and the reporter functions directly, without the
GUI. Each test writes its .iol/.tkn files to a temporary folder.
"""
import os
import sys
import tempfile
import unittest

# Make the project folder importable when the tests are run from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler import compile_code  # noqa: E402
from lexer import scan  # noqa: E402
from reporter import build_messages, write_tkn  # noqa: E402


class CompileCodeTests(unittest.TestCase):
    """End-to-end tests of compile_code() (lexer + variable table + reporter)."""

    def setUp(self):
        # A fresh temporary folder per test, holding the .iol path t.iol.
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "t.iol")

    def tearDown(self):
        self.dir.cleanup()

    def run_src(self, source):
        """Compile source as if it were saved at <temp folder>/t.iol."""
        return compile_code(source, self.path)

    def test_clean_program(self):
        """Valid code: no errors, correct tokens, message, and variables."""
        r = self.run_src("IOL\nINT num IS 0\nPRINT num\nLOI")
        self.assertFalse(r.has_errors)
        self.assertEqual(r.token_stream, "IOL\nINT IDENT IS INT_LIT\nPRINT IDENT\nLOI")
        self.assertEqual(r.messages[0], "t.iol: lexical analysis completed with no errors found.")
        self.assertEqual([(v.name, v.type) for v in r.variables], [("num", "INT")])

    def test_blank_lines_keep_alignment(self):
        """Blank source lines stay as empty lines in the token stream."""
        r = self.run_src("IOL\n\n\nLOI")
        self.assertEqual(r.token_stream, "IOL\n\n\nLOI")

    def test_last_lexeme_without_newline(self):
        """The last word is kept even when the file has no final newline."""
        self.assertEqual(self.run_src("IOL\nLOI").token_stream, "IOL\nLOI")

    def test_empty_source(self):
        """Empty code gives an empty token stream and no errors."""
        r = self.run_src("")
        self.assertEqual(r.token_stream, "")
        self.assertFalse(r.has_errors)

    def test_keywords_are_case_sensitive(self):
        """Only exact keywords match; print and IOLx are identifiers."""
        self.assertEqual(self.run_src("PRINT print IOLx").token_stream, "PRINT IDENT IDENT")

    def test_unknown_words_reported_with_line_numbers(self):
        """Each unknown word gets a line with its line number, then a summary."""
        r = self.run_src("IOL\nINT my_var\nPRINT 1x @\nLOI")
        self.assertTrue(r.has_errors)
        self.assertEqual(r.messages, [
            "Line 2: unknown word 'my_var'",
            "Line 3: unknown word '1x'",
            "Line 3: unknown word '@'",
            "t.iol: 3 lexical error(s) found.",
            "Token stream saved to t.tkn.",
        ])

    def test_tkn_file_written_next_to_iol(self):
        """The .tkn file has the .iol file's name and holds the token stream."""
        r = self.run_src("IOL\nLOI")
        self.assertEqual(r.tkn_path, os.path.join(self.dir.name, "t.tkn"))
        with open(r.tkn_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), r.token_stream)

    def test_unwritable_folder_does_not_crash(self):
        """If the .tkn file cannot be written, the compile still finishes."""
        r = compile_code("IOL", os.path.join(self.dir.name, "missing", "t.iol"))
        self.assertEqual(r.tkn_path, "")
        self.assertTrue(r.messages[-1].startswith("Could not save the token file: "))


class ReporterContractTests(unittest.TestCase):
    """The reporter functions return what the shared contract (task guide, Section 4) says."""

    def test_build_messages_returns_messages_and_flag(self):
        """build_messages returns (list of str, bool)."""
        self.assertEqual(build_messages(scan("IOL LOI"), "a.iol"),
                         (["a.iol: lexical analysis completed with no errors found."], False))
        self.assertEqual(build_messages(scan("IOL\n-5"), "a.iol"),
                         (["Line 2: unknown word '-5'", "a.iol: 1 lexical error(s) found."], True))

    def test_write_tkn_returns_path(self):
        """write_tkn returns the .tkn path, and raises OSError if it cannot write."""
        with tempfile.TemporaryDirectory() as folder:
            path = write_tkn("IOL", os.path.join(folder, "a.iol"))
            self.assertEqual(path, os.path.join(folder, "a.tkn"))
            with self.assertRaises(OSError):
                write_tkn("IOL", os.path.join(folder, "missing", "a.iol"))


if __name__ == "__main__":
    unittest.main()
