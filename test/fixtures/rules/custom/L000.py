"""Test std rule import."""
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
class Rule_L000:
    """Test std rule import."""

    groups = ("all",)
    pass
