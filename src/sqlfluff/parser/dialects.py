
from .base import TerminalRule, Rule, Dialect
from .base import Seq, ZeroOrOne, AnyOf, OneOf, ZeroOrMore, ZeroOrOneOf

# Inspired by https://forcedotcom.github.io/phoenix/

ansi_rules = [
    # Terminals
    TerminalRule(r'select'),
    TerminalRule(r'from'),
    TerminalRule(r'distinct'),
    TerminalRule(r'all'),
    TerminalRule(r'as'),
    TerminalRule(r'group by', name='groupby'),
    TerminalRule(r'order by', name='orderby'),
    TerminalRule(r'\.', name='dot'),
    TerminalRule(r'\*', name='star'),
    TerminalRule(r',', name='comma'),
    TerminalRule(r'[a-z_]+', name='object_literal'),
    TerminalRule(r'\s+', name='whitespace'),
    # Comments
    TerminalRule(r'(--|#)[^\n]*', name='eol_comment'),
    TerminalRule(r'\/\*([^\*]|\n|\*[^\/])*\*\/', name='block_comment'),
    # The Non Syntax Join Rule
    Rule('nsj', AnyOf('whitespace', 'eol_comment', 'block_comment')),
    # Simple composites
    Rule('qualified_object_literal', Seq('object_literal', ZeroOrOne('dot', 'object_literal'), nsj=False)),  # Don't allow NSJ here
    Rule('col_expr', Seq('qualified_object_literal')),
    Rule('table_expr', Seq('qualified_object_literal')),
    Rule('select_expression', OneOf(
        'star', Seq('object_literal', 'dot', 'star'),
        Seq('qualified_object_literal', ZeroOrOne('as', 'object_literal')))),
    # Statement rules
    Rule('select_stmt', Seq('select', ZeroOrOneOf('distinct', 'all'), 'select_expression',
                            ZeroOrMore('comma', 'select_expression'),
                            'from', 'table_expr', ZeroOrOne('group_by_expr'),
                            ZeroOrOne('order_by_expr'))),
    Rule('group_by_expr', Seq('groupby', 'col_expr')),
    Rule('order_by_expr', Seq('orderby', 'col_expr'))
]

ansi = Dialect('ansi', 'select_stmt', ansi_rules,
               join_rule='nsj')
