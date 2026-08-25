"""Keyword lists for the Microsoft Fabric Data Warehouse dialect.

Fabric Warehouse shares T-SQL's lexer and reserved word list wholesale, so
rather than re-forking the ~700-entry T-SQL keyword lists (which would
have to be manually kept in sync with ``dialect_tsql_keywords.py`` forever,
with no automated check to catch drift), this module imports them
unchanged and adds only the two words this dialect actually needs on top:

* ``ENFORCED`` -- used by the ``NOT ENFORCED`` clause that Fabric requires
  on PRIMARY KEY, UNIQUE and FOREIGN KEY constraints (Fabric stores these
  as informational-only metadata; it does not enforce them).
* ``CLUSTER`` -- used by the ``WITH (CLUSTER BY (...))`` clause that
  Fabric Warehouse uses on ``CREATE TABLE`` / CTAS instead of Synapse's
  ``DISTRIBUTION = ...`` clause.

See ``dialect_fabric_warehouse.py``'s module docstring for the full
rationale behind this fork (product naming, scope, sourcing) -- not
repeated here to avoid two copies of the same rationale drifting apart.
"""

from sqlfluff.dialects.dialect_tsql_keywords import (
    FUTURE_RESERVED_KEYWORDS,
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS as _TSQL_UNRESERVED_KEYWORDS,
)

__all__ = [
    "RESERVED_KEYWORDS",
    "UNRESERVED_KEYWORDS",
    "FUTURE_RESERVED_KEYWORDS",
]

UNRESERVED_KEYWORDS = [
    *_TSQL_UNRESERVED_KEYWORDS,
    "ENFORCED",
    "CLUSTER",
]
