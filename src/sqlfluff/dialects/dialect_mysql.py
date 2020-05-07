"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from .dialect_ansi import ansi_dialect

mysql_dialect = ansi_dialect.copy_as('mysql')

mysql_dialect.patch_lexer_struct([
    # name, type, pattern, kwargs
    ("inline_comment", "regex", r"(-- |#)[^\n]*", dict(is_comment=True, type="comment", trim_start=('-- ', '#')))
])
