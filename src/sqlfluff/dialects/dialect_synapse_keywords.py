"""A list of Azure Synapse Analytics unreserved keywords.

https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/reference-tsql-language-elements
"""

# Azure Synapse Analytics adds TABLE_OPTIONS and a handful of
# Synapse-specific identifiers not present in base T-SQL.
UNRESERVED_KEYWORDS = [
    "TABLE_OPTIONS",
]
