
from .base import TerminalRule, Rule, Dialect
from .base import Seq, ZeroOrOne

ansi_rules = [
    # Terminals
    TerminalRule(r'select'),
    TerminalRule(r'from'),
    TerminalRule(r'group by', name='groupby'),
    TerminalRule(r'order by', name='orderby'),
    TerminalRule(r'\.', name='dot'),
    TerminalRule(r'[a-z_]+', name='object_literal'),
    TerminalRule(r'\s+', name='whitespace'),
    # Simple composites
    Rule('qualified_object_literal', Seq('object_literal', ZeroOrOne('dot', 'object_literal'))),
    Rule('col_expr', Seq('qualified_object_literal')),
    Rule('table_expr', Seq('qualified_object_literal')),
    # Statement rules
    Rule('select_stmt', Seq('select', 'whitespace', 'col_expr', 'whitespace', 'from',
                            'whitespace', 'table_expr', ZeroOrOne('group_by_expr'),
                            ZeroOrOne('order_by_expr'))),
    
    Rule('group_by_expr', Seq('whitespace', 'groupby', 'whitespace', 'col_expr')),
    Rule('order_by_expr', Seq('whitespace', 'orderby', 'whitespace', 'col_expr'))
]

ansi = Dialect('ansi', 'select_stmt', ansi_rules)
