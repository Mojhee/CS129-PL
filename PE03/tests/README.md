# PE03 test files

Sample grammars and broken files for testing the parser. Load them with the
program's **Load** button. Generated `.prsd` files are written into this
folder; only `expected_test_rules.prsd` belongs in the repository.

## Sample grammars

| Files | Grammar | Inputs to try |
|---|---|---|
| `rules.prod`, `rules.ptbl` | The handout's expression grammar | `id + id * id` (VALID, 18 rows), `( id + id ) * id` (VALID, 25 rows), `id + * id` (INVALID) |
| `paren.prod`, `paren.ptbl` | Balanced parentheses, `S -> ( S ) S \| e` | `( ( ) ) ( )` (VALID), `( ( )` (INVALID) |
| `iol_mini.prod`, `iol_mini.ptbl` | A small part of IOL, using IOL token names | `INTO IDENT IS ADD IDENT INT_LIT PRINT IDENT` (VALID), `PRINT IS` (INVALID) |
| `rules_curly.prod`, `rules_curly.ptbl` | `rules` with curly apostrophes (’) in some symbols, as in the handout | Same results as `rules` |
| `expected_test_rules.prsd` | Exact output for `id + id * id` with output name `test` (Section 3.3 of the task guide) | Compare with the generated `test_rules.prsd` |

## Files that must be refused

| File | What is wrong | Expected message |
|---|---|---|
| `bad_columns.prod` | Line 4 has only two columns | `bad_columns.prod, line 4: expected number, non-terminal, production.` |
| `bad_number.prod` | Line 4 has `x` as its number | `bad_number.prod, line 4: 'x' is not a production number.` |
| `bad_duplicate.prod` | Line 6 uses number 3 again | `bad_duplicate.prod, line 6: production number 3 is used twice.` |
| `bad_cell.ptbl` | A cell contains `x` | `bad_cell.ptbl, line 3, column '+': 'x' is not a production number.` |
| `no_end.ptbl` | Header has no `$` column | `no_end.ptbl, line 1: there is no $ column.` |
| `notes.txt` | Wrong extension | `Only .prod and .ptbl files can be loaded.` |
| `rules_mismatch.prod`, `rules_mismatch.ptbl` | Both load, but cell (E, id) uses production 9 | Parse shows: `Cell (E, id) uses production 9, which is not in rules_mismatch.prod.` |
