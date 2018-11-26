""" Base Objects for the Parser """



class Chunk(object):
    """
    A chunk of text, with a line number and position
    It can be split and eventually turned into a token.
    A chunk should have a reference to the chunk before
    and after it to maintain the sense of a chunk in it's
    order within a file.

    A chunk can optionally have corrections applied to it.
    """
    pass


class Token(Chunk):
    """
    A piece of text of fixed length, with a particular
    meaning. It will also have a normalised form for
    comparison purposes.

    A token is linked to a single SyntaxTerminal.

    In the case that multiple tokens match a chunk, then
    it it possible for multiple to initially bind ("match")
    but at parse time (when building the AST) if that
    ambiguity still exists then it should raise an exception.

    ALL tokens are based on regexes (for simplicity)
    """
    pass


class Element(object):
    """
    A seletion of tokens, which define a unit of syntax.
    Optionally an element can be `terminal` meaning that
    it has no child elements, or equivalently that it has
    a single token.

    An element is linked to a single SyntaxConstruct
    """
    pass



string_literal = Token(
    name='string_literal',
    pattern='\''
)


string_literal = Token(
    name='string_literal',
    pattern='\''
)






