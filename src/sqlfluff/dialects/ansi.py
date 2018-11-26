

from .base import SyntaxDialect, SyntaxConstruct, SyntaxTerminal



ansi = SyntaxDialect(
    name='ansi',
    description="Standard ANSI SQL"


)

# SQL dialects are defined as classes, subclassed from the
# base dialect, this keeps them lightweight, but also makes
# inheritance a little more manageable.



# ## The standard ANSI SQL dialect.
# ## Designec also to be the base for other dialects
class AnsiDialect(SyntaxDialect):
    name='ansi'
    description="Standard ANSI SQL"

    @sql_terminal(p=100)
    def statement_terminator():
        return SyntaxTerminal
    
    statement_terminator = SyntaxTerminal(c=';', p=100)

    sql_statement = SyntaxConstruct(
        c=';',
        p=100)

    sql_statement_set = 