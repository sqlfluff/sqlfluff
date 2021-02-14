"""The Teradata dialect.

This inherits from the ansi dialect, with changes as specified by
Teradata Database SQL Data Definition Language Syntax and Examples

    Release Number 15.10
    Release Date December 2015

"""

from sqlfluff.core.dialects.dialect_ansi import ansi_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    GreedyUntil,
    StartsWith,
    OneOf,
    Delimited,
    Bracketed,
    AnyNumberOf,
    Ref,
    Anything,
)

teradata_dialect = ansi_dialect.copy_as("teradata")

teradata_dialect.patch_lexer_struct(
    [
        # name, type, pattern, kwargs, so it also matches 1.
        ("numeric_literal", "regex", r"([0-9]+(\.[0-9]*)?)", dict(is_code=True)),
    ]
)

# Remove unused keywords from the dialect.
teradata_dialect.sets("unreserved_keywords").difference_update(
    [
        # 'auto_increment',
        # The following are moved to being reserved keywords
        "UNION",
        "TIMESTAMP",
        "DATE",
    ]
)

teradata_dialect.sets("unreserved_keywords").update(
    [
        "AUTOINCREMENT",
        "ACTIVITYCOUNT",
        "CASESPECIFIC",
        "DUAL",
        "ERRORCODE",
        "EXPORT",
        "FALLBACK",
        "FORMAT",
        "IMPORT",
        "JOURNAL",
        "LABEL",
        "LOGON",
        "LOGOFF",
        "MERGEBLOCKRATIO",
        "PROTECTION",
        "QUIT",
        "RUN",
        "STAT",
        "SUMMARY",
    ]
)

teradata_dialect.sets("reserved_keywords").update(["UNION", "TIMESTAMP", "DATE"])


# BTEQ statement
@teradata_dialect.segment()
class BteqKeyWordSegment(BaseSegment):
    """Bteq Keywords.

    Often a string with a dot, sometimes followed by a Literal

    LOGON - Used to log into Teradata system.
    ACTIVITYCOUNT - Returns the number of rows affected by the previous query.
    ERRORCODE - Returns the status code of the previous query.
    DATABASE - Sets the default database.
    LABEL - Assigns a label to a set of SQL commands.
    RUN FILE - Executes the query contained in a file.
    GOTO - Transfers control to a label.
    LOGOFF - Logs off from database and terminates all sessions.
    IMPORT - Specifies the input file path.
    EXPORT - Specifies the output file path and initiates the export.
    """

    type = "bteq_key_word_segment"
    match_grammar = Sequence(
        Ref("DotSegment", optional=True),
        OneOf(
            "IF",
            "THEN",
            "LOGON",
            "ACTIVITYCOUNT",
            "ERRORCODE",
            "DATABASE",
            "LABEL",
            "GOTO",
            "LOGOFF",
            "IMPORT",
            "EXPORT",
            "RUN",
            "QUIT",
            "ACTIVITYCOUNT",
        ),
        Ref("LiteralGrammar", optional=True),
    )


@teradata_dialect.segment()
class BteqStatementSegment(BaseSegment):
    """Bteq statements start with a dot, followed by a Keyword.

    Non exhaustive and maybe catching too many statements?

    # BTEQ commands
    .if errorcode > 0 then .quit 2
    .IF ACTIVITYCOUNT = 0 THEN .QUIT
    """

    type = "bteq_statement"
    match_grammar = StartsWith(Ref("DotSegment"))
    parse_grammar = Sequence(
        Ref("DotSegment"),
        Ref("BteqKeyWordSegment"),
        AnyNumberOf(
            Ref("BteqKeyWordSegment"),
            # if ... then: the ...
            Sequence(
                Ref("ComparisonOperatorGrammar"), Ref("LiteralGrammar"), optional=True
            ),
            optional=True,
        ),
    )


# Collect Statistics statement
@teradata_dialect.segment()
class TdCollectStatisticsStatementSegment(BaseSegment):
    """A `COLLECT STATISTICS (Optimizer Form)` statement.

    # TODO: Make complete
    COLLECT [SUMMARY] (STATISTICS|STAT) [[COLUMN| [UNIQUE] INDEX] (expression (, expression ...)] ON TABLENAME
    """

    type = "collect_statistics_statement"
    match_grammar = Sequence(
        "COLLECT",
        Ref.keyword("SUMMARY", optional=True),
        OneOf("STATISTICS", "STAT"),
        OneOf(
            Sequence(
                OneOf(
                    "COLUMN",
                    Sequence(
                        Ref.keyword("UNIQUE", optional=True),
                        "INDEX",
                    ),
                ),
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref("ObjectReferenceSegment"), delimiter=Ref("CommaSegment")
                        )
                    ),
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            optional=True,
        ),
        "ON",
        Ref("ObjectReferenceSegment"),
    )


# Rename table statement
@teradata_dialect.segment()
class TdRenameStatementSegment(BaseSegment):
    """A `COLLECT STATISTICS (Optimizer Form)` statement.

    https://docs.teradata.com/reader/eWpPpcMoLGQcZEoyt5AjEg/Kl~F4lxPauOELYJVuFLjag
    RENAME TABLE OLD_TABLENAME (TO|AS) NEW_TABLENAME
    """

    type = "collect_statistics_statement"
    match_grammar = Sequence(
        "RENAME",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            "TO",
            "AS",
        ),
        Ref("TableReferenceSegment"),
    )


# Adding Teradata specific DATE FORMAT 'YYYYMM'
@teradata_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    DATE FORMAT 'YYYY-MM-DD'
    """

    type = "td_internal_data_type"
    match_grammar = Sequence(
        Ref("DatatypeIdentifierSegment"),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Sequence(  # FORMAT 'YYYY-MM-DD',
            "FORMAT", Ref("QuotedLiteralSegment"), optional=True
        ),
    )


@teradata_dialect.segment()
class TeradataCastSegment(BaseSegment):
    """A casting operation using Teradata conversion syntax.

    https://docs.teradata.com/reader/kmuOwjp1zEYg98JsB8fu_A/ypGGhd87xi3E2E7SlNS1Xg
    # Teradata Conversion Syntax in Explicit Data Type Conversions
    expression ([data_attribute,] data_type [, data_attribute])
    with

    data_type := a data type declaration such as INTEGER or DATE
    data_attribute := a data attribute such as FORMAT, NAMED or  TITLE

    e.g.
        '9999-12-31' (DATE),
        '9999-12-31' (DATE FORMAT 'YYYY-MM-DD')
        '100000' (SMALLINT)
         DATE FORMAT 'E4,BM4BDD,BY4'
         DATE '2007-01-01'
    """

    type = "cast_expression"
    match_grammar = Bracketed(Ref("DatatypeSegment"))


@teradata_dialect.segment(replace=True)
class ExpressionSegment(BaseSegment):
    """A expression, either arithmetic or boolean.

    We extend the expression segment in teradata to enable
    casting.
    """

    type = "expression"
    match_grammar = Sequence(
        Ref("Expression_A_Grammar"),
        Ref("TeradataCastSegment", optional=True),
    )


# Adding Teradata specific column definitions
@teradata_dialect.segment(replace=True)
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnOptionSegment", optional=True),
            # Adding Teradata specific column definitions
            Ref("TdColumnOptionSegment", optional=True),
        ),
    )


@teradata_dialect.segment()
class TdColumnOptionSegment(BaseSegment):
    """Teradata specific column attributes.

    e.g. CHARACTER SET LATIN or [NOT] CASESPECIFIC
    """

    type = "td_column_attribute_constraint"
    match_grammar = Sequence(
        OneOf(
            Sequence(  # CHARACTER SET LATIN
                "CHARACTER", "SET", Ref("SingleIdentifierGrammar")
            ),
            Sequence(  # [NOT] CASESPECIFIC
                Ref.keyword("NOT", optional=True),
                "CASESPECIFIC",
            ),
            Sequence(  # COMPRESS [(1.,3.) | 3. | NULL],
                "COMPRESS",
                OneOf(
                    Bracketed(
                        Delimited(Ref("LiteralGrammar"), delimiter=Ref("CommaSegment"))
                    ),
                    Ref("LiteralGrammar"),
                    "NULL",
                    optional=True,
                ),
            ),
        ),
    )


# Create Teradata Create Table Statement
@teradata_dialect.segment()
class TdCreateTableOptions(BaseSegment):
    """CreateTableOptions.

    , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL, CHECKSUM = DEFAULT, DEFAULT MERGEBLOCKRATIO
    """

    type = "create_table_options_statement"
    match_grammar = AnyNumberOf(
        Sequence(
            Ref("CommaSegment"),
            OneOf(
                # [ NO ] FALLBACK [ PROTECTION ]
                Sequence(
                    Ref.keyword("NO", optional=True),
                    "FALLBACK",
                    Ref.keyword("PROTECTION", optional=True),
                ),
                # [NO | DUAL | LOCAL |NOT LOCAL] [AFTER | BEFORE] JOURNAL
                Sequence(
                    OneOf(
                        "NO", "DUAL", "LOCAL", Sequence("NOT", "LOCAL"), optional=True
                    ),
                    OneOf("BEFORE", "AFTER", optional=True),
                    "JOURNAL",
                ),
                # CHECKSUM = (ON|OFF|DEFAULT)
                Sequence(
                    "CHECKSUM",
                    Ref("EqualsSegment"),
                    OneOf(
                        "ON",
                        "OFF",
                        "DEFAULT",
                    ),
                ),
                # (NO|Default) MergeBlockRatio
                Sequence(
                    OneOf(
                        "DEFAULT",
                        "NO",
                    ),
                    "MERGEBLOCKRATIO",
                ),
                # MergeBlockRatio = integer [PERCENT]
                Sequence(
                    "MERGEBLOCKRATIO",
                    Ref("EqualsSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref.keyword("PERCENT", optional=True),
                ),
            ),
        ),
    )


@teradata_dialect.segment()
class TdTablePartitioningLevel(BaseSegment):
    """Partitioning Level.

    https://docs.teradata.com/reader/eWpPpcMoLGQcZEoyt5AjEg/e0GX8Iw16u1SCwYvc5qXzg

    partition_expression or
    COLUMN [[NO] AUTO COMPRESS] [[ALL BUT] column_partition] [ADD constant]

    column_partition := ([COLUMN|ROW] column_name (, column_name2, ...) NO AUTOCOMPRESS

    partition_expression := CASE_N, RANGE_N, EXTRACT, expression and in case of multi-level in parenthesis
    """

    type = "td_partitioning_level"
    match_grammar = OneOf(
        Sequence(
            Ref("FunctionNameSegment"),
            Bracketed(Anything(optional=True)),
        ),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("FunctionNameSegment"),
                    Bracketed(Anything(optional=True)),
                ),
                delimiter=Ref("CommaSegment"),
            ),
        ),
    )


@teradata_dialect.segment()
class TdTableConstraints(BaseSegment):
    """Teradata specific table attributes.

    e.g.
        UNIQUE PRIMARY INDEX Column_name | ( Column_name, ... )
        NO PRIMARY INDEX
        ...
    """

    type = "td_table_constraint"
    match_grammar = Sequence(
        AnyNumberOf(
            # PRIMARY Index
            OneOf(
                Sequence(  # UNIQUE PRIMARY INDEX Column_name | ( Column_name, ... )
                    Ref.keyword("UNIQUE", optional=True),
                    "PRIMARY",
                    "INDEX",
                    OneOf(
                        Bracketed(
                            Delimited(
                                Ref("SingleIdentifierGrammar"),
                                delimiter=Ref("CommaSegment"),
                            )
                        ),
                        Ref("SingleIdentifierGrammar"),
                    ),
                ),
                Sequence("NO", "PRIMARY", "INDEX"),  # NO PRIMARY INDEX
            ),
            # PARTITION BY ...
            Sequence(  # INDEX HOPR_TRN_TRAV_SIN_MP_I ( IND_TIPO_TARJETA );
                "PARTITION",
                "BY",
                Ref("TdTablePartitioningLevel"),
            ),
            # Index
            Sequence(  # INDEX HOPR_TRN_TRAV_SIN_MP_I ( IND_TIPO_TARJETA );
                Ref.keyword("UNIQUE", optional=True),
                "INDEX",
                Ref("ObjectReferenceSegment"),  # Index name
                Ref.keyword("ALL", optional=True),
                Bracketed(  # Columns making up  constraint
                    Delimited(
                        Ref("ColumnReferenceSegment"), delimiter=Ref("CommaSegment")
                    ),
                ),
            ),
        )
    )


@teradata_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE [MULTISET| SET] TABLE` statement."""

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        # Adding Teradata specific [MULTISET| SET]
        OneOf("SET", "MULTISET", optional=True),
        OneOf(Sequence("GLOBAL", "TEMPORARY"), "VOLATILE", optional=True),
        "TABLE",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("TableReferenceSegment"),
        # , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL
        OneOf(Ref("TdCreateTableOptions"), optional=True),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("TableConstraintSegment"),
                        ),
                        delimiter=Ref("CommaSegment"),
                    )
                ),
                Sequence(  # [COMMENT 'string'] (MySQL)
                    "COMMENT", Ref("QuotedLiteralSegment"), optional=True
                ),
            ),
            # Create AS syntax:
            Sequence("AS", Ref("SelectableGrammar")),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        # PRIMARY INDEX( COD_TARJETA, COD_EST, IND_TIPO_TARJETA, FEC_ANIO_MES )
        OneOf(Ref("TdTableConstraints"), optional=True),
    )


# Update
@teradata_dialect.segment(replace=True)
class UpdateStatementSegment(BaseSegment):
    """A `Update from` statement.

    The UPDATE statement FROM clause is a Teradata extension to the
    ANSI SQL:2011 standard.

    UPDATE (<table name> | FROM Statement)
    SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar = StartsWith("UPDATE")
    parse_grammar = Sequence(
        "UPDATE",
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("FromUpdateClauseSegment"),
            Sequence(
                Ref("TableReferenceSegment"),
                Ref("FromUpdateClauseSegment"),
            ),
        ),
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


@teradata_dialect.segment()
class FromUpdateClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT` but terminated by SET."""

    type = "from_in_update_clause"
    match_grammar = StartsWith("FROM", terminator=Ref.keyword("SET"))
    parse_grammar = Sequence(
        "FROM",
        Delimited(
            # Optional old school delimited joins
            Ref("TableExpressionSegment"),
            delimiter=Ref("CommaSegment"),
        ),
    )


# Adding Teradata specific statements
@teradata_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    parse_grammar = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        # Teradata specific statements
        Ref("TdCollectStatisticsStatementSegment"),
        Ref("BteqStatementSegment"),
        Ref("TdRenameStatementSegment"),
    )
    match_grammar = GreedyUntil(Ref("SemicolonSegment"))


teradata_dialect.add(
    TdCastIdentifierSegment=Sequence(
        OneOf("DATE", "TIMESTAMP"), Ref("ExpressionSegment")
    ),
)

teradata_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("TdCastIdentifierSegment"),
    )
)
