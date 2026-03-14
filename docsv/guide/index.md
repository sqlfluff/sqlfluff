# Introduction

Bored of not having a good SQL linter that works with whichever dialect
you're working with? Fluff is an extensible and modular linter designed
to help you write good SQL and catch errors and bad SQL before it hits
your database.


To get started just install the package, make a sql file and then run
SQLFluff and point it at the file. For more details or if you don't
have python or pip already installed see the [installation guide](./install).

```bash
pip install sqlfluff
echo "  SELECT a  +  b FROM tbl;  " > test.sql
sqlfluff lint test.sql --dialect ansi

== [test.sql] FAIL
L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                        | Found '  '. [layout.spacing]
L:   1 | P:   1 | LT02 | First line should not be indented.
                        | [layout.indent]
L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                        | [layout.start_of_file]
L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                        | Found '  '. [layout.spacing]
L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                        | Found '  '. [layout.spacing]
L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                        | [layout.spacing]
L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                        | [layout.end_of_file]
All Finished 📜 🎉!
```
