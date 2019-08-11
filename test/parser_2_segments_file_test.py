""" The Test file for The New Parser """

import pytest
import logging

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
    "raw,res",
    [
        ("a b", ['a', ' ', 'b']),
        ("b.c", ['b', '.', 'c']),
        ("abc \n \t def  ;blah", ['abc', ' ', '\n', ' \t ', 'def', '  ', ';', 'blah'])
    ]
)
def test__parser_2__file_from_raw(raw, res, caplog):
    with caplog.at_level(logging.DEBUG):
        fs = FileSegment.from_raw(raw)
    # From just the initial parse, check we're all there
    assert fs.raw == raw
    assert fs.raw_list() == res


@pytest.mark.parametrize(
    "raw",
    [
        "select a from tbl",
        # "select * from blah",
        # "select a, b from tmp", " select 12 -- ends with comment",
        # multi_statement_test
    ]
)
def test__parser_2__base_file_parse(raw, caplog):
    fs = FileSegment.from_raw(raw)
    # From just the initial parse, check we're all there
    assert fs.raw == raw

    with caplog.at_level(logging.DEBUG):
        logging.debug("Pre-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
        logging.debug("Pre-parse structure: {0}".format(fs.stringify()))
        parsed = fs.parse(recurse=False)
        logging.debug("Post-parse structure: {0}".format(fs.to_tuple(show_raw=True)))
        logging.debug("Post-parse structure: {0}".format(fs.stringify()))
    # Check we're all there.
    assert parsed.raw == raw

    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert 'unparsable' not in typs


@pytest.mark.parametrize(
    "raw,res",
    # Need to add some full structures here, but also to
    # implement the logic to parse them.
    [
        (
            "select * from blah",
            ('file', (('statement', (('select_statement', (
                ('select_clause', (
                    ('keyword', ()),
                    ('blah', ())
                )),
                ('from_clause', (

                ))
            )),)),))
        ),
        ("select a,b, c from blah", ())
    ]
)
def DISABLED_test__parser_2__base_parse_struct(raw, res):
    """ Some simple statements to check full parsing structure """
    fs = FileSegment.from_raw(raw)
    parsed = fs.parse()
    assert parsed.to_tuple() == res  # if seg.is_code
