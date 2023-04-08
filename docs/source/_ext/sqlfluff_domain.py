"""The sqlfluff domain for documenting rules.s"""


from sphinx import addnodes
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole
from sphinx.util.docfields import GroupedField, TypedField
from sphinx.util.nodes import make_refnode


class SQLFluffRule(ObjectDescription):

    doc_field_types = [
        TypedField('parameter', label='Parameters',
                   names=('param', 'parameter', 'arg', 'argument'),
                   typerolename='obj', typenames=('paramtype', 'type')),
        GroupedField("alias", label="Aliases", names=["alias"], can_collapse=False),  
    ]

    obj_type = "rule"

    def handle_signature(self, sig, signode):
        obj_type = self.obj_type.capitalize() + ' '
        signode += addnodes.desc_type(obj_type, obj_type)
        code, _, name = sig.partition(" ")
        signode += addnodes.desc_name(code + " ", code + " ")
        signode += addnodes.desc_name(name, name)

        fullname = obj_type + code
        signode['type'] = self.obj_type
        signode['code'] = code
        #signode['ids'].append(code)
        signode['name'] = name
        signode['fullname'] = fullname
        return (fullname, self.obj_type, sig)

    def needs_arglist(self):
        return False

    def add_target_and_index(self, name_cls, sig, signode):
        #signode['ids'].append(signode["name"])
        #signode['ids'].append(signode["code"])
        code, _, name = sig.partition(" ")
        #signode['ids'].append("rule-" + code)
        # signode['ids'].append(jinja_resource_anchor(*name_cls[1:]))
        # self.env.domaindata['jinja'][self.method][sig] = (self.env.docname, '')
        #self.env.domaindata['sqlfluff'][self.method][sig] = (self.env.docname, '')
        #self.env.note_
        #fluff = self.env.get_domain('sqlfluff')
        #fluff.data['rules'].append(
        #    (self._toc_entry_name(signode), "rule-" + code, 'Rule', fluff.env.docname, "rule-" + code, 1))
        signode['ids'].append('rule' + '-' + sig)
        fluff = self.env.get_domain('sqlfluff')
        fluff.add_rule(sig)

    #def get_index_text(self, modname, name):
    #    return ''

    #def _toc_entry_name(self, sig_node: addnodes.desc_signature) -> str:
    #    # Borrowed from https://www.sphinx-doc.org/en/master/_modules/sphinx/domains/python.html
    #    return "Rule " + sig_node['code']


class RuleIndex(Index):

    name = 'ruleindex'
    localname = 'SQLFluff Rule Index'
    shortname = 'rules'

    def generate(self, docnames=None):
        content = {}
        return (content, True)


class SQLFluffDomain(Domain):
    """SQLFluff domain."""

    name = 'sqlfluff'
    label = 'sqlfluff'

    object_types = {
        'rule': ObjType('rule', 'rule', 'obj'),
    }

    roles = {
        'ref': XRefRole(),
    }

    directives = {
        'rule': SQLFluffRule,
    }

    initial_data = {
        'rules': [],  # object list
    }

    def get_full_qualified_name(self, node):
        return f'rule.{node.arguments[0]}'

    def get_objects(self):
        yield from self.data['rules']
    
    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        match = [(docname, anchor)
                 for _, sig, _, docname, anchor, _
                 in self.get_objects() if sig == target]

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]

            return make_refnode(builder, fromdocname, todocname, targ,
                                contnode, targ)
        else:
            print(f'Failed to match xref: {target!r}')
            return None
    
    def add_rule(self, signature):
        """Add a new recipe to the domain."""
        name = f'rule.{signature}'
        anchor = f'rule-{signature}'

        # name, dispname, type, docname, anchor, priority
        self.data['rules'].append(
            (name, signature, 'Rule', self.env.docname, anchor, 0))


def setup(app):
    app.add_domain(SQLFluffDomain)
