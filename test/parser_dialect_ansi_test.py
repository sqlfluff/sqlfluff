""" The Test file for the ANSI dialect of SQLFluff """

from sqlfluff.parser.dialects import ansi


def test__parser__dialect_ansi_simple():
    root_node, _ = ansi.parse('SelECt sdfsaasd    FrOM   asdfawwwww   GroUP BY  asdfawwwww.fasfekjhsf   order BY  something_else    ')
    tkns = root_node.tokens()
    assert ('groupby', 'GroUP BY') in tkns
