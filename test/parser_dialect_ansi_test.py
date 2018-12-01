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
