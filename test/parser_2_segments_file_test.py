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
        "select * from blah",
        "select a, b from tmp", " select 12 -- ends with comment",
        # A simple multi statement example
        "select a from tbl1; select b from tbl2;   -- trailling ending comment\n  \t "
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
        parsed = fs.parse()  # Optional: set recurse=1 to limit recursion
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
            "select 1",  # A REALLY SIMPLE, BUT VALID QUERY
            ('file', (('statement', (('select_statement', (
                ('keyword', 'select'),
                ('select_target_group', (('raw', '1'),))
            )),)),))
        ),
        (
            "select * from blah",
            ('file', (('statement', (('select_statement', (
                ('keyword', 'select'),
                ('select_target_group', (('raw', '*'),)),
                ('from_clause', (
                    ('keyword', 'from'),
                    ('table_expression', (
                        ('identifier', (
                            ('naked_identifier', 'blah'),
                        )),
                    ))
                )),
            )),)),))
        ),
        (
            'select a,b, c from sch."blah"',
            ('file', (('statement', (('select_statement', (
                ('keyword', 'select'),
                ('select_target_group', (
                    ('raw', 'a'),
                    ('raw', ','),
                    ('raw', 'b'),
                    ('raw', ','),
                    ('raw', 'c'),
                )),
                ('from_clause', (
                    ('keyword', 'from'),
                    ('table_expression', (
                        ('identifier', (
                            ('naked_identifier', 'sch'),
                            ('dot', '.'),
                            ('quoted_identifier', '"blah"'),
                        )),
                    ))
                )),
            )),)),))
        )
    ]
)
def test__parser_2__base_parse_struct(raw, res, caplog):
    """ Some simple statements to check full parsing structure """
    fs = FileSegment.from_raw(raw)
    with caplog.at_level(logging.DEBUG):
        parsed = fs.parse()
    assert parsed.to_tuple(code_only=True, show_raw=True) == res  # if seg.is_code
