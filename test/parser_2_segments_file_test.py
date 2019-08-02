""" The Test file for The New Parser """

import logging
import pytest

from sqlfluff.parser_2.segments_file import FileSegment


multi_statement_test = """\
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


@pytest.mark.parametrize(
    "raw",
    [
        "select a from tbl", "select * from blah",
        "select a, b from tmp", " select 12 -- ends with comment",
        multi_statement_test
    ]
)
def test__parser_2__base_parse(raw):
    fs = FileSegment.from_raw(raw)
    # From just the initial parse, check we're all there
    assert fs.raw == raw

    # check structure pre parse
    logging.warning(fs.segments)
    logging.warning(fs.to_tuple())
    logging.warning(fs.stringify())

    parsed = fs.parse()
    # Check we're all there.
    assert parsed.raw == raw

    # check structure post parse
    logging.warning(parsed.segments)
    logging.warning(parsed.to_tuple())
    logging.warning(parsed.stringify())

    # Make a recursive function to collect types
    def collect_types(seg):
        typs = set([seg.type])
        for s in seg.segments:
            typs |= collect_types(s)
        return typs

    # Check that there's nothing un parsable
    typs = collect_types(parsed)
    assert 'unparsable' not in typs
