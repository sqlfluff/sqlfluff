"""The sqlfluff domain for documenting rules.s"""

import re

from sphinx import addnodes
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import GroupedField, TypedField

def jinja_resource_anchor(method, path):
    path = re.sub(r'[<>:/]', '-', path)
    return method.lower() + '-' + path


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
        signode['name'] = name
        signode['fullname'] = fullname
        return (fullname, self.obj_type, sig)

    def needs_arglist(self):
        return False

    def add_target_and_index(self, name_cls, sig, signode):
        #signode['ids'].append(signode["name"])
        #signode['ids'].append(signode["code"])
        #signode['ids'].append(f'{sig}')
        # signode['ids'].append(jinja_resource_anchor(*name_cls[1:]))
        # self.env.domaindata['jinja'][self.method][sig] = (self.env.docname, '')
        #self.env.domaindata['sqlfluff'][self.method][sig] = (self.env.docname, '')
        fluff = self.env.get_domain('sqlfluff')
        fluff.add_rule(sig)
        pass

    def get_index_text(self, modname, name):
        return ''

    def _toc_entry_name(self, sig_node: addnodes.desc_signature) -> str:
        # Borrowed from https://www.sphinx-doc.org/en/master/_modules/sphinx/domains/python.html
        return "Rule " + sig_node['code']


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

    directives = {
        'rule': SQLFluffRule,
    }

    initial_data = {
        'rules': [],  # object list
    }

    indices = [RuleIndex]

    def get_objects(self):
        yield from self.data['rules']
    
    def add_rule(self, signature):
        """Add a new rule to the domain."""
        name = f'rule.{signature}'
        anchor = f'rule-{signature}'

        # name, dispname, type, docname, anchor, priority
        self.data['rules'].append(
            (name, signature, 'Rule', self.env.docname, anchor, 0))


def setup(app):
    app.add_domain(SQLFluffDomain)
