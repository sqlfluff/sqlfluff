"""The Microsoft Fabric Data Warehouse dialect.

This is a fork of ``dialect_tsql.py`` (sqlfluff 4.3.0), not of
``dialect_ansi.py`` directly -- Fabric Warehouse's T-SQL surface is a
*subset* of box-product T-SQL / SQL Server, so it makes more sense to
inherit tsql's large existing grammar and subtract/adjust the handful of
places where Fabric genuinely differs, rather than rebuild it from ANSI.

Naming note: "Fabric Data Warehouse" and "SQL database in Microsoft
Fabric" are two different products with two different T-SQL engines.
"SQL database in Fabric" runs the same engine as Azure SQL Database --
CHECK/DEFAULT constraints, enforced foreign keys, computed columns and
triggers are all intact, and it needs little to no divergence from the
existing ``tsql`` dialect. "Fabric Data Warehouse" is the OneLake/
Parquet-backed analytical engine with a much narrower, genuinely different
T-SQL surface for table DDL -- that is what this dialect (``fabric_warehouse``)
models. Do not assume this dialect also covers "SQL database in Fabric";
it doesn't, and that product would need its own (much smaller) fork if
it ever needs one.

Scope of this fork
-------------------
This file only overrides the segments involved in ``CREATE TABLE`` and
``ALTER TABLE`` (plus the constraint/column/data-type grammar they depend
on). It deliberately does NOT attempt to prune the rest of the inherited
T-SQL surface (CREATE LOGIN, BACKUP, Service Broker, CLR, full-text
search, standalone CREATE INDEX, SQL Graph, sequences, synonyms, etc.),
all of which Fabric Warehouse also does not support (confirmed via the
T-SQL surface area doc below). 
Future work required to ensure all other commands are valid

Sourcing note
-------------
Fabric Warehouse ships fast, and some of its T-SQL reference pages are
shared with Synapse dedicated SQL pools under a `?view=fabric` query
param on the same Microsoft Learn URL, which makes it easy to
misattribute a Synapse-only clause to Fabric. The grammar below was
cross-checked against several live Microsoft Learn pages fetched while
drafting this revision (not just training-time knowledge, and not just
the generic CREATE TABLE (Transact-SQL) reference page, which turned out
to omit Fabric-specific syntax like IDENTITY and CLUSTER BY entirely):

* https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=fabric
  -- the authoritative CREATE TABLE syntax diagram for Fabric Warehouse
  specifically (distinct from the generic CREATE TABLE (Transact-SQL) page).
* https://learn.microsoft.com/en-us/fabric/data-warehouse/data-clustering
  -- WITH (CLUSTER BY (...)) syntax, column count (1-4) and eligible types.
* https://learn.microsoft.com/en-us/fabric/data-warehouse/table-constraints
  -- PK/UNIQUE/FK must be added via ALTER TABLE, never inline in CREATE TABLE.
* https://learn.microsoft.com/en-us/fabric/data-warehouse/identity
  -- IDENTITY is BIGINT-only, no seed/increment, no parentheses at all.
* https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types
  -- the supported/unsupported data type lists.
* https://learn.microsoft.com/en-us/fabric/data-warehouse/tables
  -- confirms computed columns, partitioning, indexed views, unique
  indexes, sequences, synonyms, triggers, UDTs, external tables and
  global temp tables are all unsupported.
* https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area
  -- broader DDL/DML surface (out of scope here, but explains why the
  rest of this file only touches table DDL).

Even across these, two official pages disagreed with each other at the
edges (one generic CREATE TABLE syntax box omitted IDENTITY entirely,
while the dedicated identity page confirms it as a documented, if
preview, feature) -- Microsoft's docs are clearly maintained at different
cadences per page. Anything below is only as current as the page it cites;
spot-check against the live page before relying on this beyond
illustration, and especially before extending it to cover more than
CREATE/ALTER TABLE.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Bracketed,
    Delimited,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_tsql as tsql
from sqlfluff.dialects.dialect_fabric_warehouse_keywords import (
    FUTURE_RESERVED_KEYWORDS,
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

tsql_dialect = load_raw_dialect("tsql")

fabric_warehouse_dialect = tsql_dialect.copy_as(
    "fabric_warehouse",
    formatted_name="Microsoft Fabric Data Warehouse",
    docstring="""**Default Casing**: ``case-insensitive``

**Quotes**: String Literals: ``''``, Identifiers: ``[]`` or ``""``

The dialect for `Microsoft Fabric Data Warehouse`_, the OneLake/Parquet-backed
analytical SQL engine in Microsoft Fabric.

Forked from the :ref:`tsql_dialect_ref` dialect, since Fabric Warehouse's
T-SQL surface for table DDL is a heavily constrained subset of SQL Server /
Synapse T-SQL rather than something better modelled from ANSI outward.

Note this is a distinct product/engine from "SQL database in Microsoft
Fabric", which runs the same engine as Azure SQL Database and is much
closer to unmodified T-SQL -- this dialect does not cover that product.

.. _`Microsoft Fabric Data Warehouse`: https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing""",
)

# Keywords: identical to T-SQL, plus ENFORCED (NOT ENFORCED constraints) and
# CLUSTER (WITH (CLUSTER BY (...))). Re-cleared and re-populated (rather
# than just `.update()`-ing the delta) to mirror exactly how tsql_dialect
# itself builds these sets from ansi.
fabric_warehouse_dialect.sets("reserved_keywords").clear()
fabric_warehouse_dialect.sets("unreserved_keywords").clear()
fabric_warehouse_dialect.sets("future_reserved_keywords").clear()
fabric_warehouse_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
fabric_warehouse_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
fabric_warehouse_dialect.sets("future_reserved_keywords").update(
    FUTURE_RESERVED_KEYWORDS
)


# ------------------------------------------------------------------------
# NotEnforcedGrammar / PrimaryKeyGrammar.
#
# ANSI already defines a `NotEnforcedGrammar` extension point (default
# `Nothing()`, i.e. never present) specifically for dialects that need a
# "NOT ENFORCED" clause on constraints -- BigQuery is the existing example
# (`NotEnforcedGrammar = Sequence("NOT", "ENFORCED")`). Fabric Warehouse
# reuses the same mechanism rather than hand-rolling "NOT"/"ENFORCED"
# literals.
#
# T-SQL also overrides `PrimaryKeyGrammar` to add an already-optional
# trailing CLUSTERED/NONCLUSTERED (and to accept bare "UNIQUE" as an
# alternative opener) -- convenient for box-product T-SQL, but it means
# `Ref("PrimaryKeyGrammar")` would silently swallow a NONCLUSTERED token
# that our own grammar below also wants to require explicitly, causing it
# to desync from the literal "NONCLUSTERED" that follows. Fabric Warehouse
# reverts this back to plain ANSI `Sequence("PRIMARY", "KEY")` and makes
# NONCLUSTERED + NOT ENFORCED explicit and mandatory in the segments below
# instead, since Fabric (unlike box-product T-SQL) never allows a
# CLUSTERED primary key.
# ------------------------------------------------------------------------
fabric_warehouse_dialect.replace(
    NotEnforcedGrammar=Sequence("NOT", "ENFORCED"),
    PrimaryKeyGrammar=Sequence("PRIMARY", "KEY"),
)


# ------------------------------------------------------------------------
# StatementSegment: drop the two CREATE/ALTER TABLE *variants* that Fabric
# Warehouse does not support at all. (Standalone CREATE INDEX, full-text,
# sequences, synonyms, triggers, etc. are left untouched -- out of scope
# per the module docstring above, though confirmed unsupported too.)
# ------------------------------------------------------------------------
class StatementSegment(tsql.StatementSegment):
    """Overriding StatementSegment to drop unsupported CREATE/ALTER TABLE variants."""

    match_grammar = tsql.StatementSegment.match_grammar.copy(
        remove=[
            # SQL Graph tables (CREATE TABLE ... AS NODE/EDGE) -- not
            # supported in Fabric Warehouse.
            Ref("CreateTableGraphStatementSegment"),
            # ALTER TABLE ... SWITCH -- partition switching. Confirmed
            # unsupported: "Partitioned tables" is explicitly listed as
            # unsupported at
            # https://learn.microsoft.com/en-us/fabric/data-warehouse/tables
            Ref("AlterTableSwitchStatementSegment"),
        ],
    )


# ------------------------------------------------------------------------
# CREATE TABLE ... WITH (CLUSTER BY (...)) clause.
#
# Fabric Warehouse dropped Synapse's WITH (DISTRIBUTION = HASH|ROUND_ROBIN
# |REPLICATE, <index type>) entirely. There is no distribution concept and
# no user-specified index type any more -- the only WITH (...) option left
# on CREATE TABLE / CTAS is CLUSTER BY, which takes 1-4 columns of
# eligible types (numerics except BIT; FLOAT/REAL; DATE/DATETIME2/TIME;
# CHAR/VARCHAR but not VARCHAR(MAX)). The column-count and eligible-type
# limits are semantic constraints Fabric enforces at execution time, not
# structural ones this grammar enforces -- same treatment as e.g.
# VARCHAR(MAX)'s 16MB limit not being encoded in DatatypeSegment either.
#
# CLUSTER BY can only be set at CREATE TABLE / CTAS time -- Fabric does
# not support adding or changing it via ALTER TABLE (you have to CTAS a
# new table instead), so this clause is not referenced anywhere in
# AlterTableStatementSegment below.
# https://learn.microsoft.com/en-us/fabric/data-warehouse/data-clustering
# ------------------------------------------------------------------------
class TableClusterByClause(BaseSegment):
    """`CREATE TABLE` / CTAS `WITH (CLUSTER BY (...))` clause (Fabric Warehouse)."""

    type = "table_cluster_by_clause"
    match_grammar = Sequence(
        "WITH",
        Bracketed(
            "CLUSTER",
            "BY",
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
        ),
    )


# ------------------------------------------------------------------------
# Table-level constraints.
#
# https://learn.microsoft.com/en-us/fabric/data-warehouse/table-constraints
# confirms only PRIMARY KEY, UNIQUE and FOREIGN KEY are supported, and
# ALL THREE MUST BE ADDED VIA ALTER TABLE -- never inline in CREATE TABLE
# (that page's own examples always `CREATE TABLE` bare, then a separate
# `ALTER TABLE ... ADD CONSTRAINT ...`). This class is therefore only
# referenced from AlterTableStatementSegment below, not from
# CreateTableStatementSegment.
#
# Differences from T-SQL:
#   * PRIMARY KEY and UNIQUE constraints must be NONCLUSTERED and must
#     carry a trailing NOT ENFORCED -- Fabric has no clustered index
#     concept for user tables, and PK/UNIQUE are stored as
#     informational-only metadata (never enforced by the engine).
#   * FOREIGN KEY constraints must likewise be NOT ENFORCED.
#   * CHECK constraints are not supported at all.
#   * DEFAULT constraints are not supported at all (confirmed on the same
#     page) -- there is no branch for them here or in
#     ColumnConstraintSegment below.
#   * RelationalIndexOptionsSegment (WITH (FILLFACTOR = ...) etc.) and
#     OnPartitionOrFilegroupOptionSegment do not apply -- no filegroups.
#   * Standalone UNIQUE table constraints aren't modelled in tsql's own
#     TableConstraintSegment at all (only PK/FK are); added here since
#     it's a real, documented piece of Fabric Warehouse syntax.
#
# NOT ENFORCED is written as required (not `optional=True`) so that a
# constraint missing it produces a parse error under this dialect, the
# same way Fabric's engine would reject it -- catching the mistake at
# lint time rather than at deploy time.
# ------------------------------------------------------------------------
class TableConstraintSegment(BaseSegment):
    """A table constraint for `ALTER TABLE ... ADD` (Fabric Warehouse).

    https://learn.microsoft.com/en-us/fabric/data-warehouse/table-constraints
    """

    type = "table_constraint"
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(
                Ref("PrimaryKeyGrammar"),
                "NONCLUSTERED",
                Ref("BracketedIndexColumnListGrammar"),
                Ref("NotEnforcedGrammar"),
            ),
            Sequence(
                "UNIQUE",
                "NONCLUSTERED",
                Ref("BracketedIndexColumnListGrammar"),
                Ref("NotEnforcedGrammar"),
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                Ref("ForeignKeyGrammar"),
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # REFERENCES reftable [ ( refcolumn) ]
                Ref("ReferencesConstraintGrammar"),
                Ref("NotEnforcedGrammar"),
            ),
            # No CHECK constraint branch -- not supported in Fabric.
        ),
    )


# ------------------------------------------------------------------------
# IDENTITY.
#
# https://learn.microsoft.com/en-us/fabric/data-warehouse/identity
# confirms IDENTITY in Fabric Warehouse is bare -- no parentheses, no
# custom seed/increment at all ("IDENTITY(1,1)" is explicitly rejected;
# only BIGINT columns may use it). The BIGINT-only restriction is a
# type/column coupling that this grammar doesn't enforce (matching how
# e.g. CLUSTER BY's eligible-types list isn't enforced either) -- that
# would be a job for a custom lint rule, not the dialect grammar.
# ------------------------------------------------------------------------
class IdentityGrammar(BaseSegment):
    """`IDENTITY` column option, no seed/increment (Fabric Warehouse)."""

    type = "identity_grammar"
    match_grammar = Sequence("IDENTITY")


# ------------------------------------------------------------------------
# Column-level constraints/options: NULL/NOT NULL, COLLATE, IDENTITY.
#
# https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=fabric
# gives the full `<column_options>` list for Fabric Warehouse as just
# `[ NULL | NOT NULL ]` and `[ COLLATE Windows_collation_name ]`; IDENTITY
# is documented separately (see class above) but is likewise a bare
# per-column option, not a named constraint.
#
# Removed relative to T-SQL (and relative to earlier drafts of this fork):
#   * DEFAULT -- confirmed not supported at all in Fabric Warehouse.
#   * Inline PRIMARY KEY / FOREIGN KEY (even NOT ENFORCED) -- confirmed
#     that constraints may ONLY be added via ALTER TABLE, never inline on
#     a column either. See TableConstraintSegment above.
#   * MASKED WITH FUNCTION (dynamic data masking) -- no positive
#     confirmation this is supported in Fabric Warehouse specifically
#     (unlike SQL database in Fabric); removed rather than assumed. VERIFY
#     if this matters to you.
#   * FILESTREAM, SPARSE, ROWGUIDCOL, ENCRYPTED WITH (Always Encrypted),
#     GENERATED ALWAYS AS ROW/TRANSACTION_ID/SEQUENCE_NUMBER (temporal
#     tables), the inline `INDEX <name> [CLUSTERED|NONCLUSTERED]`
#     shorthand, RelationalIndexOptionsSegment,
#     OnPartitionOrFilegroupOptionSegment, FilestreamOnOptionSegment,
#     CheckConstraintGrammar -- none apply; no filegroups, no temporal
#     tables, no user-managed indexes, no CHECK constraints.
# ------------------------------------------------------------------------
class ColumnConstraintSegment(BaseSegment):
    """A column option, e.g. for CREATE TABLE (Fabric Warehouse)."""

    type = "column_constraint_segment"
    match_grammar: Matchable = OneOf(
        Sequence("COLLATE", Ref("CollationReferenceSegment")),
        Ref("IdentityGrammar"),
        Sequence(Ref.keyword("NOT", optional=True), "NULL"),
    )


# ------------------------------------------------------------------------
# CREATE TABLE.
#
# Rebuilt directly from the authoritative Fabric Warehouse syntax diagram
# at
# https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=fabric
# rather than adapted from T-SQL's much larger grammar, since so much of
# T-SQL's CREATE TABLE surface (inline constraints, indexes, computed
# columns, temporal PERIOD FOR SYSTEM_TIME, filegroups/FILESTREAM, LIKE)
# turned out not to exist in that diagram at all. Kept:
#   * The plain column-list form, using ColumnDefinitionSegment (which
#     picks up the narrowed ColumnConstraintSegment above) and
#     TableClusterByClause for the optional WITH (CLUSTER BY (...)).
#   * The `CREATE TABLE ... AS <select>` form (see
#     CreateTableAsSelectStatementSegment below for the CTAS-specific
#     shape confirmed on the data-clustering page).
# Removed relative to earlier drafts of this fork:
#   * `CREATE TABLE ... LIKE <table>` -- the authoritative syntax diagram
#     doesn't include it at all; earlier drafts kept it as "permissive,
#     unconfirmed", but an authoritative diagram omitting it is stronger
#     evidence than the generic reference page being merely silent on it.
#   * Ref("TableConstraintSegment") from the column list -- constraints
#     are ALTER TABLE-only now; see TableConstraintSegment's docstring.
# ------------------------------------------------------------------------
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement (Fabric Warehouse).

    https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=fabric
    """

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnDefinitionSegment"),
                allow_trailing=True,
            ),
            optional=True,
        ),
        Ref("TableClusterByClause", optional=True),
    )


# ------------------------------------------------------------------------
# CREATE TABLE AS SELECT (CTAS).
#
# https://learn.microsoft.com/en-us/fabric/data-warehouse/data-clustering
# gives the CTAS shape as an (optional-in-practice, per its own worked
# example) column list, then WITH (CLUSTER BY (...)), then AS <select>.
# T-SQL/Synapse's CreateTableAsSelectStatementSegment (which this
# replaces) used TableDistributionIndexClause and OptionClauseSegment --
# both gone: no distribution/index clause concept any more (see
# TableClusterByClause above), and OptionClauseSegment (query hints) has
# no confirmed support here either, so it's dropped rather than assumed.
# ------------------------------------------------------------------------
class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement (Fabric Warehouse).

    https://learn.microsoft.com/en-us/fabric/data-warehouse/data-clustering
    """

    type = "create_table_as_select_statement"
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnDefinitionSegment"),
                allow_trailing=True,
            ),
            optional=True,
        ),
        Ref("TableClusterByClause", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


# ------------------------------------------------------------------------
# ALTER TABLE.
#
# https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area
# lists the complete supported set: ADD nullable columns of supported
# types, DROP COLUMN, ADD/DROP PRIMARY KEY/UNIQUE/FOREIGN KEY constraints
# (NOT ENFORCED only), and ALTER COLUMN (preview).
#
# Removed relative to T-SQL (and relative to earlier drafts of this fork):
#   * ADD used to accept a full ColumnDefinitionSegment (any nullability,
#     IDENTITY, COLLATE). The surface-area doc is specific that ADD only
#     allows *nullable* columns -- so this now uses a dedicated, narrower
#     `_AddColumnDefinition` (name + data type + optional bare NULL; no
#     NOT NULL, no IDENTITY, no COLLATE) instead of the general
#     ColumnDefinitionSegment.
#   * The bare `<ParameterName> [=] <value>` table-option form -- no
#     session/table options analogous to box-product SET options.
#   * ADD/DROP tied to PeriodSegment, or "ADD <ColumnConstraintSegment>
#     FOR <column>" -- both temporal-table-only.
#   * WITH CHECK|NOCHECK CONSTRAINT (enable/disable existing constraint
#     checking) -- meaningless when constraints are never enforced.
#   * ENABLE/DISABLE TRIGGER -- Fabric Warehouse tables don't support
#     triggers.
#   * REBUILD [WITH (...)] -- no user-controlled compression/rebuild;
#     Fabric manages physical storage automatically.
#   * SET (FILESTREAM_ON | SYSTEM_VERSIONING | DATA_DELETION) -- none of
#     these concepts exist in Fabric Warehouse.
#   * RENAME -- not part of the documented surface area.
# Kept:
#   * ALTER COLUMN -- still uses the full ColumnDefinitionSegment (the
#     surface-area doc doesn't say ALTER COLUMN is nullable-only the way
#     ADD is); flagged as preview in the comment below.
#   * DROP COLUMN, ADD/DROP CONSTRAINT -- as before.
# ------------------------------------------------------------------------
class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement (Fabric Warehouse).

    https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area
    """

    # ADD only allows nullable columns of supported data types -- no
    # NOT NULL, no IDENTITY, no COLLATE, no inline constraints.
    _add_column_definition = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("DatatypeSegment"),
        Ref.keyword("NULL", optional=True),
    )

    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # ALTER COLUMN is a preview feature as of this writing --
            # https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area
            Sequence(
                "ALTER",
                "COLUMN",
                Ref("ColumnDefinitionSegment"),
            ),
            Sequence(
                "ADD",
                Delimited(_add_column_definition),
            ),
            Sequence(
                "DROP",
                Delimited(
                    Sequence(
                        "COLUMN",
                        Ref("IfExistsGrammar", optional=True),
                        Delimited(Ref("ColumnReferenceSegment")),
                    ),
                ),
            ),
            Sequence(
                "ADD",
                Ref("TableConstraintSegment"),
            ),
            Sequence(
                "DROP",
                Delimited(
                    Sequence(
                        Sequence(
                            "CONSTRAINT",
                            Ref("IfExistsGrammar", optional=True),
                            optional=True,
                        ),
                        Ref("ObjectReferenceSegment"),
                    ),
                ),
            ),
        ),
    )


# ------------------------------------------------------------------------
# Data types.
#
# Rewritten (not trimmed via .copy(remove=...), since T-SQL's
# DatatypeSegment is one large OneOf of inline literals/Sequences rather
# than Refs to named types) to match exactly the two independent,
# mutually-consistent lists confirmed live:
# https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types and
# the <data type> block in
# https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=fabric
#
# Supported: bit, smallint, int, bigint, decimal/numeric[(p[,s])], float
# [(n)], real, date, time[(n)], datetime2[(n)] (docs note precision is
# effectively capped at 6 fractional-second digits, not enforced here),
# char[(n)], varchar[(n|MAX)] (MAX capped at 16MB, not enforced here),
# varbinary[(n|MAX)] (same 16MB note), uniqueidentifier.
#
# Explicitly removed (confirmed unsupported, with docs' suggested
# alternative in parenthesis): tinyint (smallint), money/smallmoney
# (decimal), datetime/smalldatetime (datetime2), datetimeoffset
# (datetime2 + AT TIME ZONE), nchar/nvarchar (char/varchar), text/ntext
# (varchar), image (varbinary), geography/geometry (varbinary/varchar as
# WKB/WKT), xml (no equivalent), sql_variant/cursor/table/timestamp/
# rowversion/hierarchyid (not mentioned as supported anywhere checked),
# user-defined types (no equivalent, and DatatypeIdentifierSegment along
# with them), vector (no equivalent -- new in SQL Server 2025 / Azure SQL,
# not in Fabric Warehouse; the docs point to AI functions instead).
# ------------------------------------------------------------------------
class DatatypeSegment(BaseSegment):
    """A data type segment (Fabric Warehouse).

    https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types
    """

    type = "data_type"
    match_grammar = Sequence(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            "BIT",
            "SMALLINT",
            "INT",
            "BIGINT",
            Sequence(
                OneOf("DECIMAL", "NUMERIC", "DEC"),
                Ref("BracketedArguments", optional=True),
            ),
            Sequence(
                "FLOAT",
                Ref("BracketedArguments", optional=True),
            ),
            "REAL",
            "DATE",
            Sequence(
                OneOf("TIME", "DATETIME2"),
                Ref("BracketedArguments", optional=True),
            ),
            Sequence(
                OneOf("CHAR", "CHARACTER"),
                Ref("BracketedArguments", optional=True),
            ),
            Sequence(
                "VARCHAR",
                Ref("BracketedArguments", optional=True),
            ),
            Sequence(
                "VARBINARY",
                Ref("BracketedArguments", optional=True),
            ),
            "UNIQUEIDENTIFIER",
        ),
        Ref("CharCharacterSetGrammar", optional=True),
    )
