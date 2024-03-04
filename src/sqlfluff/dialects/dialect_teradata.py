"""The Teradata dialect.

This inherits from the ansi dialect, with changes as specified by
Teradata Database SQL Data Definition Language Syntax and Examples

    Release Number 15.10
    Release Date December 2015

"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    ComparisonOperatorSegment,
    CompositeComparisonOperatorSegment,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    Sequence,
    StringParser,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
teradata_dialect = ansi_dialect.copy_as("teradata")

teradata_dialect.patch_lexer_matchers(
    [
        # so it also matches 1.
        RegexLexer(
            "numeric_literal",
            r"([0-9]+(\.[0-9]*)?)",
            CodeSegment,
        ),
    ]
)

# Remove unused keywords from the dialect.
teradata_dialect.sets("unreserved_keywords").difference_update(
    [
        # 'auto_increment',
        # The following are moved to being reserved keywords
        "UNION",
        "TIMESTAMP",
    ]
)

teradata_dialect.sets("unreserved_keywords").update(
    [
        "AUTOINCREMENT",
        "ACTIVITYCOUNT",
        "CASESPECIFIC",
        "CS",
        "DAYS",
        "DEL",
        "DUAL",
        "ERRORCODE",
        "EXPORT",
        "FALLBACK",
        "FORMAT",
        "HASH",
        "IMPORT",
        "JOURNAL",
        "LABEL",
        "LOGON",
        "LOGOFF",
        "MACRO",
        "MAXINTERVALS",
        "MAXVALUELENGTH",
        "MEETS",
        "MERGEBLOCKRATIO",
        "NONE",
        "PERCENT",
        "PROFILE",
        "PROTECTION",
        "QUERY_BAND",
        "QUIT",
        "RUN",
        "SAMPLE",
        "SEL",
        "SS",
        "STAT",
        "STATS",
        "STATISTICS",
        "SUMMARY",
        "THRESHOLD",
        "UC",
        "UPPERCASE",
    ]
)

teradata_dialect.sets("reserved_keywords").update(["UNION", "TIMESTAMP"])

teradata_dialect.sets("bare_functions").update(["DATE"])

teradata_dialect.replace(
    # ANSI standard comparison operators plus Teradata extensions
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("EqualsSegment_a"),
        Ref("GreaterThanSegment"),
        Ref("GreaterThanSegment_a"),
        Ref("LessThanSegment"),
        Ref("LessThanSegment_a"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("GreaterThanOrEqualToSegment_a"),
        Ref("LessThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment_a"),
        Ref("NotEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("NotEqualToSegment_c"),
        Ref("LikeOperatorSegment"),
        Sequence("IS", "DISTINCT", "FROM"),
        Sequence("IS", "NOT", "DISTINCT", "FROM"),
    )
)

teradata_dialect.add(
    # Add Teradata comparison operator extensions
    EqualsSegment_a=StringParser("EQ", ComparisonOperatorSegment),
    GreaterThanSegment_a=StringParser("GT", ComparisonOperatorSegment),
    LessThanSegment_a=StringParser("LT", ComparisonOperatorSegment),
    GreaterThanOrEqualToSegment_a=StringParser("GE", ComparisonOperatorSegment),
    LessThanOrEqualToSegment_a=StringParser("LE", ComparisonOperatorSegment),
    NotEqualToSegment_a=StringParser("NE", ComparisonOperatorSegment),
    NotEqualToSegment_b=StringParser("NOT=", ComparisonOperatorSegment),
    NotEqualToSegment_c=StringParser("^=", ComparisonOperatorSegment),
)


# BTEQ statement
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


class BteqStatementSegment(BaseSegment):
    """Bteq statements start with a dot, followed by a Keyword.

    Non exhaustive and maybe catching too many statements?

    # BTEQ commands
    .if errorcode > 0 then .quit 2
    .IF ACTIVITYCOUNT = 0 THEN .QUIT
    """

    type = "bteq_statement"
    match_grammar = Sequence(
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


class TdCollectStatUsingOptionClauseSegment(BaseSegment):
    """'using_option' for COLLECT STAT clause."""

    type = "collect_stat_using_option_clause"

    match_grammar = Sequence(
        OneOf(
            Sequence("SAMPLE", Ref("NumericLiteralSegment"), "PERCENT"),
            Sequence("SYSTEM", "THRESHOLD", OneOf("PERCENT", "DAYS", optional=True)),
            Sequence("SYSTEM", "SAMPLE"),
            Sequence(
                "THRESHOLD",
                Ref("NumericLiteralSegment"),
                OneOf("PERCENT", "DAYS"),
            ),
            Sequence("NO", "THRESHOLD", OneOf("PERCENT", "DAYS", optional=True)),
            Sequence("NO", "SAMPLE"),
            Sequence("MAXINTERVALS", Ref("NumericLiteralSegment")),
            Sequence("SYSTEM", "MAXINTERVALS"),
            Sequence("MAXVALUELENGTH", Ref("NumericLiteralSegment")),
            Sequence("SYSTEM", "MAXVALUELENGTH"),
            "SAMPLE",
        ),
        Sequence("FOR", "CURRENT", optional=True),
    )


class TdOrderByStatClauseSegment(BaseSegment):
    """An `ORDER BY (VALUES|HASH) (column_name)` clause in COLLECT STATS."""

    type = "stat_orderby_clause"
    match_grammar = Sequence(
        "ORDER", "BY", OneOf("VALUES", "HASH"), Bracketed(Ref("ColumnReferenceSegment"))
    )


# Collect Statistics statement
class TdCollectStatisticsStatementSegment(BaseSegment):
    """A `COLLECT STATISTICS (Optimizer Form)` statement.

    # TODO: add expression
    COLLECT [SUMMARY] (STATISTICS|STAT) [[COLUMN| [UNIQUE] INDEX]
    (expression (, expression ...)] ON TABLENAME
    """

    type = "collect_statistics_statement"
    match_grammar = Sequence(
        "COLLECT",
        Ref.keyword("SUMMARY", optional=True),
        OneOf("STAT", "STATS", "STATISTICS"),
        Sequence(
            "USING",
            Delimited(
                Ref("TdCollectStatUsingOptionClauseSegment"),
                delimiter="AND",
            ),
            optional=True,
        ),
        Delimited(
            OneOf(
                # UNIQUE INDEX index_name ALL (column_name, ...) ORDER BY VALUES|HASH
                # (column_name)
                Sequence(
                    Ref.keyword("UNIQUE", optional=True),
                    "INDEX",
                    Ref("IndexReferenceSegment", optional=True),
                    Ref.keyword("ALL", optional=True),
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    Ref("TdOrderByStatClauseSegment", optional=True),
                ),
                # UNIQUE INDEX index_name
                Sequence(
                    Ref.keyword("UNIQUE", optional=True),
                    "INDEX",
                    Ref("IndexReferenceSegment"),
                ),
                # COLUMN ...
                Sequence(
                    "COLUMN",
                    OptionallyBracketed(
                        Delimited(
                            OneOf(
                                Ref("ColumnReferenceSegment"),
                                Ref.keyword("PARTITION"),
                                # TODO: expression
                            ),
                        ),
                    ),
                    Sequence(
                        Ref.keyword("AS", optional=True),
                        Ref("ObjectReferenceSegment"),  # statistics_name
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
        "ON",
        Ref.keyword("TEMPORARY", optional=True),
        Ref("TableReferenceSegment"),
    )


class TdCommentStatementSegment(BaseSegment):
    """A `COMMENT` statement.

    COMMENT [ON] (object_kind_1|object_kind_2) name [[AS|IS] comment]
    object_kind_1: (COLUMN|FUNCTION|GLOP SET|MACRO|MAP|METHOD|PROCEDURE|PROFILE|ROLE|
                    TRIGGER|TYPE|VIEW)
    object_kind_2: (DATABASE|FILE|TABLE|USER)
    """

    type = "comment_clause"
    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = Sequence(
        "COMMENT",
        OneOf("ON", optional=True),
        OneOf(
            Sequence("COLUMN", Ref("ColumnReferenceSegment")),
            Sequence("FUNCTION", Ref("ObjectReferenceSegment")),
            Sequence("MACRO", Ref("ObjectReferenceSegment")),
            Sequence("MAP", Ref("ObjectReferenceSegment")),
            Sequence("METHOD", Ref("ObjectReferenceSegment")),
            Sequence("PROCEDURE", Ref("ObjectReferenceSegment")),
            Sequence("PROFILE", Ref("ObjectReferenceSegment")),
            Sequence("ROLE", Ref("ObjectReferenceSegment")),
            Sequence("TRIGGER", Ref("ObjectReferenceSegment")),
            Sequence("TYPE", Ref("ObjectReferenceSegment")),
            Sequence("VIEW", Ref("TableReferenceSegment")),
            Sequence("DATABASE", Ref("DatabaseReferenceSegment")),
            Sequence("FILE", Ref("ObjectReferenceSegment")),
            Sequence("TABLE", Ref("TableReferenceSegment")),
            Sequence("USER", Ref("ObjectReferenceSegment")),
        ),
        Sequence(
            OneOf("AS", "IS", optional=True),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


# Rename table statement
class TdRenameStatementSegment(BaseSegment):
    """A `RENAME TABLE` statement.

    https://docs.teradata.com/reader/eWpPpcMoLGQcZEoyt5AjEg/Kl~F4lxPauOELYJVuFLjag
    RENAME TABLE OLD_TABLENAME (TO|AS) NEW_TABLENAME
    """

    type = "rename_table_statement"
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
class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment.

    DATE FORMAT 'YYYY-MM-DD'
    """

    match_grammar = Sequence(
        Ref("DatatypeIdentifierSegment"),
        Ref("BracketedArguments", optional=True),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
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
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
            # Adding Teradata specific column definitions
            Ref("TdColumnConstraintSegment", optional=True),
        ),
    )


class TdColumnConstraintSegment(BaseSegment):
    """Teradata specific column attributes.

    e.g. CHARACTER SET LATIN | [NOT] (CASESPECIFIC|CS) | (UPPERCASE|UC)
    """

    type = "td_column_attribute_constraint"
    match_grammar = Sequence(
        OneOf(
            Sequence(  # CHARACTER SET LATIN
                "CHARACTER", "SET", Ref("SingleIdentifierGrammar")
            ),
            Sequence(  # [NOT] CASESPECIFIC
                Ref.keyword("NOT", optional=True),
                OneOf("CASESPECIFIC", "CS"),
            ),
            OneOf("UPPERCASE", "UC"),
            Sequence(  # COMPRESS [(1.,3.) | 3. | NULL],
                "COMPRESS",
                OneOf(
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                    Ref("LiteralGrammar"),
                    "NULL",
                    optional=True,
                ),
            ),
        ),
    )


# Create Teradata Create Table Statement
class TdCreateTableOptions(BaseSegment):
    """CreateTableOptions.

    , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL, CHECKSUM = DEFAULT
    , DEFAULT MERGEBLOCKRATIO
    """

    type = "create_table_options_statement"
    match_grammar = Sequence(
        Ref("CommaSegment"),
        Delimited(
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


class TdTablePartitioningLevel(BaseSegment):
    """Partitioning Level.

    https://docs.teradata.com/reader/eWpPpcMoLGQcZEoyt5AjEg/e0GX8Iw16u1SCwYvc5qXzg

    partition_expression or
    COLUMN [[NO] AUTO COMPRESS] [[ALL BUT] column_partition] [ADD constant]

    column_partition := ([COLUMN|ROW] column_name (, column_name2, ...) NO AUTOCOMPRESS

    partition_expression := CASE_N, RANGE_N, EXTRACT, expression and in case of
    multi-level in parenthesis
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
            ),
        ),
    )


class TdTableConstraints(BaseSegment):
    """Teradata specific table attributes.

    e.g.
        UNIQUE PRIMARY INDEX Column_name | ( Column_name, ... )
        NO PRIMARY INDEX
        ...
    """

    type = "td_table_constraint"
    match_grammar = AnyNumberOf(
        # PRIMARY Index
        OneOf(
            Sequence(  # UNIQUE PRIMARY INDEX Column_name | ( Column_name, ... )
                Ref.keyword("UNIQUE", optional=True),
                "PRIMARY",
                "INDEX",
                Ref("ObjectReferenceSegment", optional=True),  # primary index name
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref("SingleIdentifierGrammar"),
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
                Delimited(Ref("ColumnReferenceSegment")),
            ),
        ),
        # WITH DATA
        Sequence("WITH", Sequence("NO", optional=True), "DATA"),
        # AND STATISITCS
        Sequence(
            "AND",
            Sequence("NO", optional=True),
            OneOf("STAT", "STATS", "STATISTICS"),
            optional=True,
        ),
        # ON COMMIT PRESERVE ROWS
        Sequence("ON", "COMMIT", OneOf("PRESERVE", "DELETE"), "ROWS"),
    )


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE [MULTISET| SET] TABLE` statement."""

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        # Adding Teradata specific [MULTISET| SET]
        OneOf("SET", "MULTISET", optional=True),
        OneOf(Sequence("GLOBAL", "TEMPORARY"), "VOLATILE", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL
        Ref("TdCreateTableOptions", optional=True),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("TableConstraintSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
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
class UpdateStatementSegment(BaseSegment):
    """A `Update from` statement.

    The UPDATE statement FROM clause is a Teradata extension to the
    ANSI SQL:2011 standard.

    UPDATE (<table name> | FROM Statement)
    SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar = Sequence(
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


class FromUpdateClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT` but terminated by SET."""

    type = "from_in_update_clause"
    match_grammar = Sequence(
        "FROM",
        Delimited(
            # Optional old school delimited joins
            Ref("FromExpressionElementSegment"),
        ),
    )


# Adding Teradata specific statements
class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("TdCollectStatisticsStatementSegment"),
            Ref("BteqStatementSegment"),
            Ref("TdRenameStatementSegment"),
            Ref("QualifyClauseSegment"),
            Ref("TdCommentStatementSegment"),
            Ref("DatabaseStatementSegment"),
            Ref("SetSessionStatementSegment"),
            Ref("SetQueryBandStatementSegment"),
        ],
    )


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`."""

    type = "qualify_clause"
    match_grammar = Sequence(
        "QUALIFY",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement.

    https://dev.mysql.com/doc/refman/5.7/en/select.html
    """

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """An unordered `SELECT` statement.

    https://dev.mysql.com/doc/refman/5.7/en/select.html
    """

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """A group of elements in a select target statement.

    Remove OVERLAPS as a terminator as this can be part of SelectClauseModifierSegment
    """

    match_grammar = ansi.SelectClauseSegment.match_grammar.copy(
        # Allow "SEL" as in place of just "SELECT"
        insert=[OneOf("SELECT", "SEL")],
        before=Ref.keyword("SELECT"),
        remove=[Ref.keyword("SELECT")],
        terminators=[
            "FROM",
            "WHERE",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ],
        replace_terminators=True,
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DEL[ETE] FROM <table name> [ WHERE <search condition> ]
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar: Matchable = Sequence(
        OneOf("DELETE", "DEL"),
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns.

    Adds NORMALIZE clause:
    https://docs.teradata.com/r/2_MC9vCtAJRlKle2Rpb0mA/UuxiA0mklFgv~33X5nyKMA
    """

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
        Sequence(
            "TOP",
            Ref("ExpressionSegment"),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
        Sequence(
            "NORMALIZE",
            OneOf(
                Sequence(
                    "ON",
                    "MEETS",
                    "OR",
                    "OVERLAPS",
                ),
                Sequence(
                    "ON",
                    "OVERLAPS",
                ),
                Sequence(
                    "ON",
                    "OVERLAPS",
                    "OR",
                    "MEETS",
                ),
                optional=True,
            ),
        ),
    )


class DatabaseStatementSegment(BaseSegment):
    """A `DATABASE` statement.

    https://docs.teradata.com/r/Teradata-Database-SQL-Data-Definition-Language-Syntax-and-Examples/December-2015/Database-Statements/DATABASE
    """

    type = "database_statement"
    match_grammar: Matchable = Sequence(
        "DATABASE",
        Ref("DatabaseReferenceSegment"),
    )


# Limited to SET SESSION DATABASE for now.
# Many other session parameters may be set via SET SESSION.
class SetSessionStatementSegment(BaseSegment):
    """A `SET SESSION` statement.

    https://docs.teradata.com/r/Teradata-Database-SQL-Data-Definition-Language-Syntax-and-Examples/December-2015/Session-Statements/SET-SESSION-DATABASE
    """

    type = "set_session_statement"
    match_grammar: Matchable = Sequence(
        OneOf(
            Sequence("SET", "SESSION"),
            "SS",
        ),
        Ref("DatabaseStatementSegment"),
    )


class SetQueryBandStatementSegment(BaseSegment):
    """A `SET QUERY_BAND` statement.

    SET QUERY_BAND = { 'band_specification [...]' | NONE } [ UPDATE ]
    FOR { SESSION [VOLATILE] | TRANSACTION } [;]

    https://docs.teradata.com/r/Teradata-VantageTM-SQL-Data-Definition-Language-Syntax-and-Examples/July-2021/Session-Statements/SET-QUERY_BAND
    """

    type = "set_query_band_statement"
    match_grammar: Matchable = Sequence(
        "SET",
        "QUERY_BAND",
        Ref("EqualsSegment"),
        OneOf(Ref("QuotedLiteralSegment"), "NONE"),
        Sequence("UPDATE", optional=True),
        "FOR",
        OneOf(Sequence("SESSION", Sequence("VOLATILE", optional=True)), "TRANSACTION"),
    )


class NotEqualToSegment_b(CompositeComparisonOperatorSegment):
    """The comparison operator extension NOT=.

    https://www.docs.teradata.com/r/Teradata-Database-SQL-Functions-Operators-Expressions-and-Predicates/March-2017/Comparison-Operators-and-Functions/Comparison-Operators/Supported-Comparison-Operators
    """

    match_grammar = Sequence(
        Ref("NotOperatorGrammar"), Ref("RawEqualsSegment"), allow_gaps=False
    )


class NotEqualToSegment_c(CompositeComparisonOperatorSegment):
    """The comparison operator extension ^=.

    https://www.docs.teradata.com/r/Teradata-Database-SQL-Functions-Operators-Expressions-and-Predicates/March-2017/Comparison-Operators-and-Functions/Comparison-Operators/Supported-Comparison-Operators
    """

    match_grammar = Sequence(
        Ref("BitwiseXorSegment"), Ref("RawEqualsSegment"), allow_gaps=False
    )
