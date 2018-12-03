
from .base import TerminalRule, Rule, Dialect
from .base import Seq, ZeroOrOne, AnyOf  # OneOf

ansi_rules = [
    # Terminals
    TerminalRule(r'select'),
    TerminalRule(r'from'),
    TerminalRule(r'group by', name='groupby'),
    TerminalRule(r'order by', name='orderby'),
    TerminalRule(r'\.', name='dot'),
    TerminalRule(r'[a-z_]+', name='object_literal'),
    TerminalRule(r'\s+', name='whitespace'),
    # Comments
    TerminalRule(r'(--|#)[^\n]*', name='eol_comment'),
    TerminalRule(r'\/\*([^\*]|\n|\*[^\/])*\*\/', name='block_comment'),
    # The Non Syntax Join Rule
    Rule('nsj', AnyOf('whitespace', 'eol_comment', 'block_comment')),
    # Simple composites
    Rule('qualified_object_literal', Seq('object_literal', ZeroOrOne('dot', 'object_literal'))),
    Rule('col_expr', Seq('qualified_object_literal')),
    Rule('table_expr', Seq('qualified_object_literal')),
    # Statement rules
    Rule('select_stmt', Seq('select', 'col_expr', 'from',
                            'table_expr', ZeroOrOne('group_by_expr'),
                            ZeroOrOne('order_by_expr'))),
    Rule('group_by_expr', Seq('groupby', 'col_expr')),
    Rule('order_by_expr', Seq('orderby', 'col_expr'))
]

ansi = Dialect('ansi', 'select_stmt', ansi_rules,
               join_rule='nsj')
