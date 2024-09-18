"""The sqlfluff domain for documenting rules."""

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class SQLFluffRule(ObjectDescription):
    """SQLFluff rule directive for sphinx.

    Rule directives can be used as shown below.

    .. code-block:: rst

        .. sqlfluff:rule:: AM01
                           ambiguous.distinct

            Write the documentation for the rule here.

    To cross reference (i.e. refer to) objects defined like this
    both the code and name reference is available:

    .. code-block:: rst

        :sqlfluff:ref:`CP02`
        :sqlfluff:ref:`capitalisation.identifiers`

    """

    def handle_signature(self, sig, signode):
        """Handle the initial signature of the node.

        This formats the header of the section.
        """
        raw_obj_type = "code" if len(sig) == 4 else "rule"
        obj_type = raw_obj_type.capitalize() + " "
        signode += addnodes.desc_type(obj_type, obj_type)
        signode += addnodes.desc_name(sig, sig)

        fullname = obj_type + sig
        signode["type"] = raw_obj_type
        signode["sig"] = sig
        signode["fullname"] = fullname
        return (fullname, raw_obj_type, sig)

    def add_target_and_index(self, name_cls, sig, signode):
        """Hook to add the permalink and index entries."""
        # Add an ID for permalinks
        node_id = "rule" + "-" + sig
        signode["ids"].append(node_id)
        if len(sig) == 4:
            # If it's a code, add support for legacy links too.
            # Both of these formats have been used in the past.
            signode["ids"].append(f"sqlfluff.rules.Rule_{sig}")
            signode["ids"].append(f"sqlfluff.rules.sphinx.Rule_{sig}")
        # Add to domain for xref resolution
        fluff = self.env.get_domain("sqlfluff")
        fluff.add_rule(sig)
        # Add to index
        self.indexnode["entries"].append(("single", sig, node_id, "", None))

    def _object_hierarchy_parts(self, sig_node):
        return ("bundle", "name")

    def _toc_entry_name(self, sig_node) -> str:
        # NOTE: toctree unpacking issues are due to incorrectly
        # setting _toc_parts.
        sig_node["_toc_parts"] = (
            "bundle",
            sig_node["sig"],
        )
        if len(sig_node["sig"]) == 4:
            # It's a code - don't return TOC entry.
            return ""
        else:
            # It's a name
            return sig_node["sig"]


class SQLFluffDomain(Domain):
    """SQLFluff domain."""

    name = "sqlfluff"
    label = "sqlfluff"

    object_types = {
        "rule": ObjType("rule", "rule", "obj"),
    }

    roles = {
        "ref": XRefRole(),
    }

    directives = {
        "rule": SQLFluffRule,
    }

    initial_data = {
        "rules": [],  # object list
    }

    def get_full_qualified_name(self, node):
        """Get the fully qualified name of the rule."""
        return f"rule.{node.arguments[0]}"

    def get_objects(self):
        """Hook to get all the rules."""
        yield from self.data["rules"]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        """Hook to resolve xrefs.

        References can be made by code or by name, e.g.
        - :sqlfluff:ref:`LT01`
        - :sqlfluff:ref:`layout.spacing`
        """
        match = [
            (docname, anchor)
            for _, sig, _, docname, anchor, _ in self.get_objects()
            if sig == target
        ]

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]

            return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
        else:
            print(f"Failed to match xref: {target!r}")
            return None

    def add_rule(self, signature):
        """Add a new recipe to the domain."""
        name = f"rule.{signature}"
        anchor = f"rule-{signature}"

        # name, dispname, type, docname, anchor, priority
        self.data["rules"].append(
            (name, signature, "Rule", self.env.docname, anchor, 0)
        )


def setup(app):
    """Setup the domain."""
    app.add_domain(SQLFluffDomain)
