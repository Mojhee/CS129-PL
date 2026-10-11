
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler import compile_code  # noqa: E402


class CompileCodeTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "t.iol")

    def tearDown(self):
        self.dir.cleanup()

    def run_src(self, source):
        return compile_code(source, self.path)

    def test_clean_program(self):
        r = self.run_src("IOL\nINT num IS 0\nPRINT num\nLOI")
        self.assertFalse(r.has_errors)
        self.assertEqual(r.token_stream, "IOL\nINT IDENT IS INT_LIT\nPRINT IDENT\nLOI")
        self.assertEqual(r.messages[0], "t.iol: lexical analysis completed with no errors found.")
        self.assertEqual([(v.name, v.type) for v in r.variables], [("num", "INT")])

    def test_blank_lines_keep_alignment(self):
        r = self.run_src("IOL\n\n\nLOI")
        self.assertEqual(r.token_stream, "IOL\n\n\nLOI")

    def test_last_lexeme_without_newline(self):
        self.assertEqual(self.run_src("IOL\nLOI").token_stream, "IOL\nLOI")

    def test_empty_source(self):
        r = self.run_src("")
        self.assertEqual(r.token_stream, "")
        self.assertFalse(r.has_errors)

    def test_keywords_are_case_sensitive(self):
        self.assertEqual(self.run_src("PRINT print IOLx").token_stream, "PRINT IDENT IDENT")

    def test_unknown_words_reported_with_line_numbers(self):
        r = self.run_src("IOL\nINT my_var\nPRINT 1x @\nLOI")
        self.assertTrue(r.has_errors)
        self.assertEqual(r.messages[:4], [
            "Line 2: unknown word 'my_var'",
            "Line 3: unknown word '1x'",
            "Line 3: unknown word '@'",
            "t.iol: lexical analysis completed with 3 error(s) found.",
        ])

    def test_tkn_file_written_next_to_iol(self):
        r = self.run_src("IOL\nLOI")
        self.assertEqual(r.tkn_path, os.path.join(self.dir.name, "t.tkn"))
        with open(r.tkn_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), r.token_stream)

    def test_unwritable_folder_does_not_crash(self):
        r = compile_code("IOL", os.path.join(self.dir.name, "missing", "t.iol"))
        self.assertEqual(r.tkn_path, "")
        self.assertTrue(r.messages[-1].startswith("Could not save"))


if __name__ == "__main__":
    unittest.main()