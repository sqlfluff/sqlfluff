""" The Test file for the ANSI dialect of SQLFluff """

from sqlfluff.parser.dialects import ansi


def test__parser__dialect_ansi_simple_a():
    root_node, _ = ansi.parse('SelECt sdfsaasd    FrOM   asdfawwwww   GroUP BY  asdfawwwww.fasfekjhsf   order BY  something_else    ')
    tkns = root_node.tokens()
    assert ('groupby', 'GroUP BY') in tkns


def test__parser__dialect_ansi_simple_b():
    root_node, r = ansi.parse('SelECt     \n colsdanjn_As_   \n  \t   FrOM     blah__   ')
    tkns = root_node.tokens()
    assert ('object_literal', 'colsdanjn_As_') in tkns
    assert r.line_no == 3


def test__parser__dialect_ansi_comment_a():
    root_node, r = ansi.parse('SelECt     -- This is an end of line comment   \n colsdanjn_As_   -- And so is this\n  \t   FrOM     blah__   ')
    tkns = root_node.tokens()
    assert ('object_literal', 'colsdanjn_As_') in tkns
    assert ('eol_comment', '-- This is an end of line comment   \n') in tkns
    assert ('eol_comment', '-- And so is this\n') in tkns
    assert r.line_no == 3


def test__parser__dialect_ansi_comment_b():
    root_node, r = ansi.parse('SelECt  \n  /* Block Comment 1 */ colsdanjn_As_   /* Block  \n  \t  Comment 2 */  FrOM     blah__   ')
    tkns = root_node.tokens()
    assert ('object_literal', 'colsdanjn_As_') in tkns
    assert ('block_comment', '/* Block Comment 1 */') in tkns
    assert ('block_comment', '/* Block  \n  \t  Comment 2 */') in tkns
    assert r.line_no == 3
