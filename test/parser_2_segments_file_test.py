""" The Test file for The New Parser """

import logging

from sqlfluff.parser_2.segments_file import FileSegment

# from sqlfluff.parser_2.proto import StatementSegment
# from sqlfluff.parser_2.proto import SelectStatementSegment


raw = """\
# COMMENT
-- Another Comment
Select A from Sys.dual where a
-- inline comment
in  ('RED',  /* Inline */  'GREEN','BLUE');
select * from tbl_b; # as another comment
insert into sch.tbl_b
    (col1)
values (123);
with tmp as (
    select * from  blah
)
select a, b from tmp;
# And that's the end
"""

# Something simple for testing
raw2 = """select a, b from tmp"""


# ############## Chunks
def test__parser_2__base_parse():
    raw = "select a from tbl"
    fs = FileSegment.from_raw(raw)

    # check structure pre parse
    logging.warning(fs.segments)
    logging.warning(fs.to_tuple())
    logging.warning(fs.stringify())

    parsed = fs.parse()

    # check structure using the structure checker.
    logging.warning(parsed.to_tuple())
    logging.warning(parsed.segments)
    logging.warning(parsed.raw)
    logging.warning(parsed.stringify())

    # check outline structure
    tpl = parsed.to_tuple()
    assert tpl[0] == 'file'
    assert tpl[1][0][0] == 'statement'
    assert tpl[1][0][1][0][0] == 'select_statement'
    assert tpl[1][0][1][0][1][0][0] == 'keyword'
    # check reconstruction, and that nothing was lost
    assert parsed.raw == raw

    raise ValueError("blah")
