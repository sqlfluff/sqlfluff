"""The sqlfluff domain for documenting rules.s"""

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class SQLFluffRule(ObjectDescription):

    obj_type = "rule"

    def handle_signature(self, sig, signode):
        obj_type = self.obj_type.capitalize() + ' '
        signode += addnodes.desc_type(obj_type, obj_type)
        signode += addnodes.desc_name(sig, sig)

        fullname = obj_type + sig
        signode['type'] = self.obj_type
        signode['sig'] = sig
        signode['fullname'] = fullname
        return (fullname, self.obj_type, sig)

    def needs_arglist(self):
        return False

    def add_target_and_index(self, name_cls, sig, signode):
        # Add an ID for permalinks
        node_id = 'rule' + '-' + sig
        signode['ids'].append(node_id)
        # Add to domain for xref resolution
        fluff = self.env.get_domain('sqlfluff')
        fluff.add_rule(sig)
        # Add to index
        self.indexnode['entries'].append(('single', sig, node_id, '', None))
    
    def _object_hierarchy_parts(self, sig_node):
        return ("bundle", "name")

    def _toc_entry_name(self, sig_node) -> str:
         # NOTE: toctree unpacking issues are due to incorrectly
         # setting _toc_parts.
        sig_node["_toc_parts"] = ("bundle", sig_node["sig"],)
        if len(sig_node["sig"]) == 4:
            # It's a code - don't return TOC entry.
            return ""
        else:
            # It's a name
            return sig_node["sig"]


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
