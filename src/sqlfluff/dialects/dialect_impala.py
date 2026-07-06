"""The Impala dialect."""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    CommentSegment,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    OneOf,
    ParseMode,
    Ref,
    RegexLexer,
    Sequence,
    StringParser,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_hive as hive
from sqlfluff.dialects.dialect_impala_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

hive_dialect = load_raw_dialect("hive")
impala_dialect = hive_dialect.copy_as(
    "impala",
    formatted_name="Apache Impala",
    docstring="The dialect for Apache `Impala <https://impala.apache.org/>`_.",
)

impala_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
impala_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

impala_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "impala_block_hint",
            r"/\* \+(?:SHUFFLE|NOSHUFFLE|CLUSTERED) \*/",
            CommentSegment,
        ),
    ],
    before="block_comment",
)
impala_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "impala_dash_hint",
            r"-- \+(?:SHUFFLE|NOSHUFFLE|CLUSTERED)",
            CommentSegment,
            segment_kwargs={"trim_start": ("--",)},
        ),
    ],
    before="inline_comment",
)

# --------------------------------------------------------------------------- #
# Grammar replacements (targeted sub-segment overrides)
# --------------------------------------------------------------------------- #

impala_dialect.replace(
    DivideSegment=OneOf(
        StringParser("DIV", BinaryOperatorSegment),
        StringParser("/", BinaryOperatorSegment),
    ),
    NonStandardJoinTypeKeywordsGrammar=OneOf(
        Sequence(OneOf("LEFT", "RIGHT"), OneOf("SEMI", "ANTI")),
    ),
    PostTableExpressionGrammar=Sequence(
        "TABLESAMPLE",
        "SYSTEM",
        Bracketed(Ref("ExpressionSegment")),
        Sequence(
            "REPEATABLE",
            Bracketed(Ref("ExpressionSegment")),
            optional=True,
        ),
    ),
)

impala_dialect.add(
    ImpalaCacheSpecGrammar=OneOf(
        Sequence(
            "CACHED",
            "IN",
            Ref("QuotedLiteralSegment"),
            Sequence(
                "WITH",
                "REPLICATION",
                Ref("RawEqualsSegment"),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
        ),
        Ref.keyword("UNCACHED"),
    ),
    ImpalaBracketHintGrammar=Bracketed(
        OneOf("SHUFFLE", "NOSHUFFLE"),
        bracket_type="square",
    ),
    ImpalaDashHintGrammar=TypedParser(
        "impala_dash_hint",
        CommentSegment,
        type="impala_hint",
    ),
    ImpalaBlockHintGrammar=TypedParser(
        "impala_block_hint",
        CommentSegment,
        type="impala_hint",
    ),
    ImpalaHintClauseGrammar=OneOf(
        Ref("ImpalaBracketHintGrammar"),
        Ref("ImpalaDashHintGrammar"),
        Ref("ImpalaBlockHintGrammar"),
    ),
    KuduColumnAttributeGrammar=OneOf(
        Sequence(Ref.keyword("NOT", optional=True), "NULL"),
        Sequence("ENCODING", Ref("SingleIdentifierGrammar")),
        Sequence("COMPRESSION", Ref("SingleIdentifierGrammar")),
        Sequence("DEFAULT", Ref("ExpressionSegment")),
        Sequence("BLOCK_SIZE", Ref("NumericLiteralSegment")),
    ),
    KuduHashPartitionGrammar=Sequence(
        "HASH",
        Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
        OneOf(
            Sequence("PARTITIONS", Ref("NumericLiteralSegment")),
            Sequence("INTO", Ref("NumericLiteralSegment"), "BUCKETS"),
        ),
    ),
    KuduRangePartitionSpecGrammar=OneOf(
        Sequence("VALUE", Ref("EqualsSegment"), Ref("ExpressionSegment")),
        Sequence(
            Ref("ExpressionSegment"),
            OneOf(Ref("LessThanOrEqualToSegment"), Ref("LessThanSegment")),
            "VALUES",
            OneOf(Ref("LessThanOrEqualToSegment"), Ref("LessThanSegment")),
            Ref("ExpressionSegment"),
        ),
    ),
    KuduRangePartitionElementGrammar=Sequence(
        "PARTITION",
        Ref.keyword("IF", optional=True),
        Ref.keyword("NOT", optional=True),
        Ref.keyword("EXISTS", optional=True),
        Ref("KuduRangePartitionSpecGrammar"),
    ),
    KuduRangePartitionGrammar=Sequence(
        "RANGE",
        Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
        Bracketed(Delimited(Ref("KuduRangePartitionElementGrammar"))),
    ),
    KuduPartitionByGrammar=Delimited(
        OneOf(
            Ref("KuduHashPartitionGrammar"),
            Ref("KuduRangePartitionGrammar"),
        ),
    ),
    ImpalaPrivilegeGrammar=OneOf(
        "ALL",
        "ALTER",
        "CREATE",
        "DROP",
        "INSERT",
        "REFRESH",
        "SELECT",
        Sequence("SELECT", Bracketed(Ref("SingleIdentifierGrammar"))),
    ),
    ImpalaSecurableGrammar=OneOf(
        Sequence("SERVER"),
        Sequence("URI", Ref("QuotedLiteralSegment")),
        Sequence("DATABASE", Ref("DatabaseReferenceSegment")),
        Sequence("TABLE", Ref("TableReferenceSegment")),
        Sequence(
            "COLUMN",
            Ref("ColumnReferenceSegment"),
        ),
    ),
    ImpalaUdfPropertyGrammar=OneOf(
        Sequence("LOCATION", Ref("QuotedLiteralSegment")),
        Sequence(
            "SYMBOL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "INTERMEDIATE",
            Ref("DatatypeSegment"),
        ),
        Sequence(
            OneOf(
                "INIT_FN",
                "UPDATE_FN",
                "MERGE_FN",
                "PREPARE_FN",
                "CLOSE_FN",
                "CLOSEFN",
                "SERIALIZE_FN",
                "FINALIZE_FN",
            ),
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
    ),
    ImpalaShowLikeGrammar=Sequence(
        Ref.keyword("LIKE", optional=True),
        Ref("QuotedLiteralSegment"),
        optional=True,
    ),
    ImpalaShowInGrammar=Sequence(
        "IN",
        Ref("DatabaseReferenceSegment"),
        Ref("ImpalaShowLikeGrammar", optional=True),
        optional=True,
    ),
    ImpalaIncrementalStatsPartitionSpecGrammar=Sequence(
        "PARTITION",
        Bracketed(
            OneOf(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                    ),
                ),
                Ref("ExpressionSegment"),
            ),
        ),
    ),
)


class PoolNameReferenceSegment(BaseSegment):
    """Reference to an Impala cache pool name."""

    type = "pool_name_reference"
    match_grammar = Ref("SingleIdentifierGrammar")


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Impala SELECT modifiers including STRAIGHT_JOIN."""

    match_grammar = Sequence(
        OneOf("ALL", "DISTINCT", optional=True),
        Ref.keyword("STRAIGHT_JOIN", optional=True),
    )


class SelectClauseSegment(hive.SelectClauseSegment):
    """Impala SELECT clause with optional bracket hints."""

    match_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Ref("ImpalaBracketHintGrammar", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            allow_trailing=True,
        ),
        Dedent,
        terminators=[Ref("SelectClauseTerminatorGrammar")],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class TableConstraintSegment(hive.TableConstraintSegment):
    """Impala table constraints including FOREIGN KEY ... DISABLE NOVALIDATE RELY."""

    match_grammar = Sequence(
        Sequence("CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True),
        OneOf(
            Sequence(
                "UNIQUE",
                Ref("BracketedColumnReferenceListGrammar"),
            ),
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Ref("BracketedColumnReferenceListGrammar"),
                Sequence(
                    "DISABLE",
                    "NOVALIDATE",
                    OneOf("RELY", "NORELY", optional=True),
                    optional=True,
                ),
            ),
            Sequence(
                Ref("ForeignKeyGrammar"),
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("ReferenceDefinitionGrammar"),
                Sequence(
                    "DISABLE",
                    "NOVALIDATE",
                    OneOf("RELY", "NORELY", optional=True),
                    optional=True,
                ),
            ),
        ),
    )


class StatementSegment(hive.StatementSegment):
    """Impala statement routing.

    Only net-new statement refs belong in ``insert``. Segments that share a
    class name with Hive/ANSI (e.g. ``InsertStatementSegment``) are overridden
    by defining the Impala subclass in this module — do not insert them again.
    """

    type = "statement"

    match_grammar = hive.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateTableAsSelectStatementSegment"),
            Ref("ComputeStatsStatementSegment"),
            Ref("DropStatsStatementSegment"),
            Ref("UpsertStatementSegment"),
            Ref("InvalidateMetadataStatementSegment"),
            Ref("RefreshAuthorizationStatementSegment"),
            Ref("RefreshStatementSegment"),
            Ref("UnsetStatementSegment"),
            Ref("CommentOnStatementSegment"),
            Ref("ShowStatementSegment"),
            Ref("LoadDataStatementSegment"),
            Ref("ValuesStatementSegment"),
            Ref("ShutdownStatementSegment"),
        ],
        remove=[
            Ref("FromInsertStatementSegment"),
            Ref("MsckRepairTableStatementSegment"),
            Ref("MsckTableStatementSegment"),
        ],
    )


class ComputeStatsStatementSegment(BaseSegment):
    """A `COMPUTE STATS` statement."""

    type = "compute_stats_statement"

    match_grammar = Sequence(
        "COMPUTE",
        OneOf(
            Sequence(
                "STATS",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(Ref("ColumnReferenceSegment")),
                    optional=True,
                ),
                Sequence(
                    "TABLESAMPLE",
                    "SYSTEM",
                    Bracketed(Ref("ExpressionSegment")),
                    Sequence(
                        "REPEATABLE",
                        Bracketed(Ref("ExpressionSegment")),
                        optional=True,
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "INCREMENTAL",
                "STATS",
                Ref("TableReferenceSegment"),
                Ref("ImpalaIncrementalStatsPartitionSpecGrammar", optional=True),
                Bracketed(
                    Delimited(Ref("ColumnReferenceSegment")),
                    optional=True,
                ),
            ),
        ),
    )


class DropStatsStatementSegment(BaseSegment):
    """A `DROP STATS` statement."""

    type = "drop_stats_statement"

    match_grammar = Sequence(
        "DROP",
        OneOf(
            Sequence("STATS", Ref("TableReferenceSegment")),
            Sequence(
                "INCREMENTAL",
                "STATS",
                Ref("TableReferenceSegment"),
                Ref("PartitionSpecGrammar"),
            ),
        ),
    )


class CreateTableStatementSegment(hive.CreateTableStatementSegment):
    """Impala `CREATE TABLE` including Kudu and LIKE PARQUET variants."""

    type = "create_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "LIKE",
                "PARQUET",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "LIKE",
                Ref("TableReferenceSegment"),
            ),
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("TableConstraintSegment", optional=True),
                        Sequence(
                            Ref("ColumnDefinitionSegment"),
                            AnyNumberOf(Ref("KuduColumnAttributeGrammar")),
                            Ref("CommentGrammar", optional=True),
                        ),
                    ),
                    bracket_pairs_set="angle_bracket_pairs",
                ),
                optional=True,
            ),
            optional=True,
        ),
        Sequence(
            "PARTITIONED",
            "BY",
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "PARTITION",
            "BY",
            Ref("KuduPartitionByGrammar"),
            optional=True,
        ),
        Sequence(
            "SORT",
            "BY",
            Bracketed(Delimited(Sequence(Ref("ColumnReferenceSegment")))),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("SerdePropertiesGrammar", optional=True),
        OneOf(
            Ref("StoredAsGrammar"),
            Sequence("STORED", "AS", "KUDU"),
            optional=True,
        ),
        Ref("LocationGrammar", optional=True),
        Ref("ImpalaCacheSpecGrammar", optional=True),
        Ref("TablePropertiesGrammar", optional=True),
    )


class CreateTableAsSelectStatementSegment(BaseSegment):
    """Impala `CREATE TABLE ... AS SELECT`."""

    type = "create_table_as_select_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            Ref("PrimaryKeyGrammar"),
            Ref("BracketedColumnReferenceListGrammar"),
            optional=True,
        ),
        Sequence(
            "PARTITIONED",
            "BY",
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "PARTITION",
            "BY",
            Ref("KuduPartitionByGrammar"),
            optional=True,
        ),
        Sequence(
            "SORT",
            "BY",
            Bracketed(Delimited(Sequence(Ref("ColumnReferenceSegment")))),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("SerdePropertiesGrammar", optional=True),
        Ref("StoredAsGrammar", optional=True),
        Ref("LocationGrammar", optional=True),
        Ref("ImpalaCacheSpecGrammar", optional=True),
        Ref("TablePropertiesGrammar", optional=True),
        Sequence("STORED", "AS", "KUDU", optional=True),
        "AS",
        Ref("SelectableGrammar"),
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """Impala `CREATE VIEW` with column comments and TBLPROPERTIES."""

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    Ref("CommentGrammar", optional=True),
                ),
            ),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("TablePropertiesGrammar", optional=True),
        "AS",
        Ref("SelectableGrammar"),
    )


class CreateFunctionStatementSegment(ansi.CreateFunctionStatementSegment):
    """Impala UDF and aggregate function creation."""

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("AGGREGATE", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Sequence("RETURNS", Ref("DatatypeSegment"), optional=True),
        AnyNumberOf(Ref("ImpalaUdfPropertyGrammar"), min_times=1),
    )


class CreateRoleStatementSegment(ansi.CreateRoleStatementSegment):
    """Impala `CREATE ROLE`."""

    type = "create_role_statement"

    match_grammar = Sequence(
        "CREATE",
        "ROLE",
        Ref("SingleIdentifierGrammar"),
    )


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """Impala `ALTER TABLE` variants."""

    type = "alter_table_statement"

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Delimited(
            OneOf(
                Sequence(
                    "RENAME",
                    "TO",
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "ADD",
                    Ref.keyword("IF", optional=True),
                    Ref.keyword("NOT", optional=True),
                    Ref.keyword("EXISTS", optional=True),
                    OneOf(
                        Sequence(
                            "COLUMNS",
                            Bracketed(Delimited(Ref("ColumnDefinitionSegment"))),
                        ),
                        Sequence(
                            "COLUMN",
                            Ref.keyword("IF", optional=True),
                            Ref.keyword("NOT", optional=True),
                            Ref.keyword("EXISTS", optional=True),
                            Ref("ColumnDefinitionSegment"),
                        ),
                        Sequence(
                            Ref("PartitionSpecGrammar"),
                            Ref("LocationGrammar", optional=True),
                            Ref("ImpalaCacheSpecGrammar", optional=True),
                        ),
                        Sequence(
                            "RANGE",
                            "PARTITION",
                            Ref("KuduRangePartitionSpecGrammar"),
                        ),
                    ),
                ),
                Sequence(
                    "REPLACE",
                    "COLUMNS",
                    Bracketed(Delimited(Ref("ColumnDefinitionSegment"))),
                ),
                Sequence(
                    "DROP",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence(
                    "CHANGE",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("SingleIdentifierGrammar"),
                    Ref("ColumnDefinitionSegment"),
                ),
                Sequence(
                    "SET",
                    "OWNER",
                    OneOf(
                        Sequence("USER", Ref("SingleIdentifierGrammar")),
                        Sequence("ROLE", Ref("SingleIdentifierGrammar")),
                    ),
                ),
                Sequence(
                    "ALTER",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("SingleIdentifierGrammar"),
                    OneOf(
                        Sequence(
                            "SET",
                            OneOf(
                                Sequence("DEFAULT", Ref("ExpressionSegment")),
                                Sequence(
                                    Ref("SingleIdentifierGrammar"),
                                    Ref("ExpressionSegment"),
                                ),
                                Sequence("COMMENT", Ref("QuotedLiteralSegment")),
                                Sequence(
                                    "ENCODING",
                                    Ref("SingleIdentifierGrammar"),
                                ),
                                Sequence(
                                    "COMPRESSION",
                                    Ref("SingleIdentifierGrammar"),
                                ),
                                Sequence(
                                    "BLOCK_SIZE",
                                    Ref("NumericLiteralSegment"),
                                ),
                            ),
                        ),
                        "DROP",
                        "DEFAULT",
                    ),
                ),
                Sequence(
                    "RECOVER",
                    "PARTITIONS",
                ),
                Sequence(
                    Ref("PartitionSpecGrammar", optional=True),
                    "SET",
                    Ref("ImpalaCacheSpecGrammar"),
                ),
                Sequence(
                    Ref("PartitionSpecGrammar", optional=True),
                    "SET",
                    OneOf(
                        Ref("StoredAsGrammar"),
                        Sequence("FILEFORMAT", Ref("FileFormatGrammar")),
                        Ref("RowFormatClauseSegment"),
                        Ref("LocationGrammar"),
                        Ref("TablePropertiesGrammar"),
                        Ref("SerdePropertiesGrammar"),
                        Ref("ImpalaCacheSpecGrammar"),
                    ),
                ),
                Sequence(
                    "SET",
                    "COLUMN",
                    "STATS",
                    Ref("SingleIdentifierGrammar"),
                    Bracketed(Delimited(Ref("PropertyGrammar"))),
                ),
                Sequence(
                    "DROP",
                    Ref.keyword("IF", optional=True),
                    Ref.keyword("EXISTS", optional=True),
                    OneOf(
                        Ref("PartitionSpecGrammar"),
                        Sequence(
                            "RANGE",
                            "PARTITION",
                            Ref("KuduRangePartitionSpecGrammar"),
                        ),
                    ),
                    Ref.keyword("PURGE", optional=True),
                ),
                Sequence(
                    "UNSET",
                    "TBLPROPERTIES",
                    Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                ),
            ),
        ),
    )


class AlterViewStatementSegment(hive.AlterViewStatementSegment):
    """Impala `ALTER VIEW` variants."""

    type = "alter_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("SingleIdentifierGrammar"),
                            Ref("CommentGrammar", optional=True),
                        ),
                    ),
                    optional=True,
                ),
                "AS",
                Ref("SelectableGrammar"),
            ),
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "SET",
                "OWNER",
                "USER",
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence("SET", Ref("TablePropertiesGrammar")),
            Sequence(
                "UNSET",
                "TBLPROPERTIES",
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
            ),
        ),
    )


class AlterDatabaseStatementSegment(hive.AlterDatabaseStatementSegment):
    """Impala `ALTER DATABASE` — SET OWNER USER or ROLE."""

    type = "alter_database_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment"),
        "SET",
        "OWNER",
        OneOf(
            Sequence("USER", Ref("SingleIdentifierGrammar")),
            Sequence("ROLE", Ref("SingleIdentifierGrammar")),
        ),
    )


class DropFunctionStatementSegment(ansi.DropFunctionStatementSegment):
    """Impala `DROP FUNCTION` including aggregate form."""

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        Ref.keyword("AGGREGATE", optional=True),
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Bracketed(
            Delimited(Ref("DatatypeSegment")),
            optional=True,
        ),
    )


class DropRoleStatementSegment(ansi.DropRoleStatementSegment):
    """Impala `DROP ROLE`."""

    type = "drop_role_statement"

    match_grammar = Sequence(
        "DROP",
        "ROLE",
        Ref("SingleIdentifierGrammar"),
    )


class InsertStatementSegment(BaseSegment):
    """Impala `INSERT` with hints and VALUES."""

    type = "insert_statement"

    _insert_target = Sequence(
        OneOf("INTO", "OVERWRITE"),
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(Ref("ColumnReferenceSegment")),
            optional=True,
        ),
        Ref("PartitionSpecGrammar", optional=True),
    )

    match_grammar = Sequence(
        Ref("WithCompoundStatementSegment", optional=True),
        "INSERT",
        Ref("ImpalaHintClauseGrammar", optional=True),
        _insert_target,
        OneOf(
            Sequence(
                Ref("ImpalaHintClauseGrammar", optional=True),
                Ref("SelectableGrammar"),
            ),
            Ref("ValuesClauseSegment"),
        ),
    )


class UpsertStatementSegment(BaseSegment):
    """Impala `UPSERT` statement."""

    type = "upsert_statement"

    match_grammar = Sequence(
        "UPSERT",
        Ref("ImpalaBracketHintGrammar", optional=True),
        "INTO",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(Ref("ColumnReferenceSegment")),
            optional=True,
        ),
        OneOf(
            Sequence(
                Ref("ImpalaBracketHintGrammar", optional=True),
                Ref("SelectableGrammar"),
            ),
            Ref("ValuesClauseSegment"),
        ),
    )


class UpdateStatementSegment(ansi.UpdateStatementSegment):
    """Impala `UPDATE` with optional FROM clause."""

    type = "update_statement"

    match_grammar = Sequence(
        "UPDATE",
        Ref("TableReferenceSegment"),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


class DeleteStatementSegment(ansi.DeleteStatementSegment):
    """Impala `DELETE` simple and join forms."""

    type = "delete_statement"

    match_grammar = OneOf(
        Sequence(
            "DELETE",
            Ref.keyword("FROM", optional=True),
            Ref("TableReferenceSegment"),
            Ref("WhereClauseSegment", optional=True),
        ),
        Sequence(
            "DELETE",
            Ref("TableReferenceSegment"),
            "FROM",
            Ref("FromExpressionSegment"),
            Ref("WhereClauseSegment", optional=True),
        ),
    )


class ValuesStatementSegment(BaseSegment):
    """Standalone Impala `VALUES` statement."""

    type = "values_statement"
    match_grammar = Ref("ValuesClauseSegment")


class SetStatementSegment(hive.SetStatementSegment):
    """Impala query option `SET` statement."""

    type = "set_statement"

    match_grammar = Sequence(
        "SET",
        OneOf(
            "ALL",
            Sequence(
                Ref("ParameterNameSegment"),
                Ref("RawEqualsSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            optional=True,
        ),
    )


class UnsetStatementSegment(BaseSegment):
    """Impala `UNSET` query option statement."""

    type = "unset_statement"

    match_grammar = Sequence(
        "UNSET",
        OneOf(
            "ALL",
            Delimited(Ref("ParameterNameSegment")),
        ),
    )


class CommentOnStatementSegment(BaseSegment):
    """Impala `COMMENT ON` statement."""

    type = "comment_on_statement"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        OneOf(
            Sequence("DATABASE", Ref("DatabaseReferenceSegment")),
            Sequence("TABLE", Ref("TableReferenceSegment")),
            Sequence(
                "COLUMN",
                Ref("ColumnReferenceSegment"),
            ),
        ),
        "IS",
        OneOf(Ref("QuotedLiteralSegment"), "NULL"),
    )


class InvalidateMetadataStatementSegment(BaseSegment):
    """Impala `INVALIDATE METADATA` statement."""

    type = "invalidate_metadata_statement"

    match_grammar = Sequence(
        "INVALIDATE",
        "METADATA",
        Ref("TableReferenceSegment", optional=True),
    )


class RefreshStatementSegment(BaseSegment):
    """Impala `REFRESH` table or `REFRESH FUNCTIONS` statements."""

    type = "refresh_statement"

    match_grammar = OneOf(
        Sequence(
            "REFRESH",
            "FUNCTIONS",
            Ref("DatabaseReferenceSegment"),
        ),
        Sequence(
            "REFRESH",
            Ref("TableReferenceSegment"),
            Ref("PartitionSpecGrammar", optional=True),
        ),
    )


class RefreshAuthorizationStatementSegment(BaseSegment):
    """Impala `REFRESH AUTHORIZATION` statement."""

    type = "refresh_authorization_statement"

    match_grammar = Sequence(
        "REFRESH",
        "AUTHORIZATION",
    )


class LoadDataStatementSegment(BaseSegment):
    """Impala `LOAD DATA INPATH` statement."""

    type = "load_data_statement"

    match_grammar = Sequence(
        "LOAD",
        "DATA",
        "INPATH",
        Ref("QuotedLiteralSegment"),
        Ref.keyword("OVERWRITE", optional=True),
        "INTO",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("PartitionSpecGrammar", optional=True),
    )


class TruncateStatementSegment(hive.TruncateStatementSegment):
    """Impala `TRUNCATE TABLE` with optional IF EXISTS."""

    type = "truncate_table"

    match_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


class DescribeStatementSegment(ansi.DescribeStatementSegment):
    """Impala `DESCRIBE` statement."""

    type = "describe_statement"

    match_grammar = Sequence(
        OneOf("DESCRIBE", "DESC"),
        Ref.keyword("DATABASE", optional=True),
        OneOf("FORMATTED", "EXTENDED", optional=True),
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("DatabaseReferenceSegment"),
        ),
    )


class ExplainStatementSegment(ansi.ExplainStatementSegment):
    """Impala `EXPLAIN` for SELECT, CTAS, and INSERT."""

    type = "explain_statement"

    explainable_stmt: Matchable = OneOf(
        Ref("SelectableGrammar"),
        Ref("CreateTableAsSelectStatementSegment"),
        Ref("InsertStatementSegment"),
    )

    match_grammar = Sequence(
        "EXPLAIN",
        explainable_stmt,
    )


class GrantStatementSegment(ansi.GrantStatementSegment):
    """Impala `GRANT` statement."""

    type = "grant_statement"

    match_grammar = OneOf(
        Sequence(
            "GRANT",
            "ROLE",
            Ref("SingleIdentifierGrammar"),
            "TO",
            "GROUP",
            Ref("SingleIdentifierGrammar"),
        ),
        Sequence(
            "GRANT",
            Ref("ImpalaPrivilegeGrammar"),
            "ON",
            Ref("ImpalaSecurableGrammar"),
            "TO",
            OneOf(
                Sequence("USER", Ref("SingleIdentifierGrammar")),
                Sequence("GROUP", Ref("SingleIdentifierGrammar")),
                Sequence("ROLE", Ref("SingleIdentifierGrammar")),
            ),
            Sequence("WITH", "GRANT", "OPTION", optional=True),
        ),
    )


class RevokeStatementSegment(ansi.RevokeStatementSegment):
    """Impala `REVOKE` statement."""

    type = "revoke_statement"

    match_grammar = OneOf(
        Sequence(
            "REVOKE",
            "ROLE",
            Ref("SingleIdentifierGrammar"),
            "FROM",
            "GROUP",
            Ref("SingleIdentifierGrammar"),
        ),
        Sequence(
            "REVOKE",
            OneOf(
                Sequence(
                    "GRANT",
                    "OPTION",
                    "FOR",
                    Ref("ImpalaPrivilegeGrammar"),
                    "ON",
                    Ref("ImpalaSecurableGrammar"),
                    "FROM",
                    OneOf(
                        Sequence("USER", Ref("SingleIdentifierGrammar")),
                        Sequence("GROUP", Ref("SingleIdentifierGrammar")),
                        Sequence("ROLE", Ref("SingleIdentifierGrammar")),
                    ),
                ),
                Sequence(
                    Ref("ImpalaPrivilegeGrammar"),
                    "ON",
                    Ref("ImpalaSecurableGrammar"),
                    "FROM",
                    OneOf(
                        Sequence("USER", Ref("SingleIdentifierGrammar")),
                        Sequence("GROUP", Ref("SingleIdentifierGrammar")),
                        Sequence("ROLE", Ref("SingleIdentifierGrammar")),
                    ),
                ),
            ),
        ),
    )


class AccessStatementSegment(ansi.AccessStatementSegment):
    """Impala GRANT/REVOKE routing."""

    type = "access_statement"
    match_grammar = OneOf(
        Ref("GrantStatementSegment"),
        Ref("RevokeStatementSegment"),
    )


class ShowStatementSegment(BaseSegment):
    """Impala `SHOW` statement variants."""

    type = "show_statement"

    match_grammar = Sequence(
        "SHOW",
        OneOf(
            Sequence("DATABASES", Ref("ImpalaShowLikeGrammar", optional=True)),
            Sequence("SCHEMAS", Ref("ImpalaShowLikeGrammar", optional=True)),
            Sequence(
                "TABLES",
                Ref("ImpalaShowInGrammar", optional=True),
                Ref("ImpalaShowLikeGrammar", optional=True),
            ),
            Sequence(
                OneOf("AGGREGATE", "ANALYTIC", optional=True),
                "FUNCTIONS",
                Ref("ImpalaShowInGrammar", optional=True),
                Ref("ImpalaShowLikeGrammar", optional=True),
            ),
            Sequence(
                "CREATE",
                "TABLE",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "CREATE",
                "VIEW",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "TABLE",
                "STATS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "COLUMN",
                "STATS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                OneOf("RANGE", optional=True),
                "PARTITIONS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "FILES",
                "IN",
                Ref("TableReferenceSegment"),
                Ref("PartitionSpecGrammar", optional=True),
            ),
            Sequence("ROLES"),
            Sequence("CURRENT", "ROLES"),
            Sequence(
                "ROLE",
                "GRANT",
                "GROUP",
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
                "GRANT",
                OneOf("USER", "ROLE", "GROUP"),
                Ref("SingleIdentifierGrammar"),
                Sequence(
                    "ON",
                    OneOf(
                        "SERVER",
                        Sequence("URI", Ref("QuotedLiteralSegment")),
                        Sequence("DATABASE", Ref("DatabaseReferenceSegment")),
                        Sequence("TABLE", Ref("TableReferenceSegment")),
                        Sequence(
                            "COLUMN",
                            Ref("TableReferenceSegment"),
                            Ref("DotSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class ShutdownStatementSegment(BaseSegment):
    """Impala `:SHUTDOWN` admin statement."""

    type = "shutdown_statement"

    match_grammar = Sequence(
        Ref("ColonSegment"),
        "SHUTDOWN",
        Bracketed(
            Delimited(
                OneOf(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("ColonSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    Ref("SingleIdentifierGrammar"),
                    Ref("NumericLiteralSegment"),
                ),
            ),
            optional=True,
        ),
    )
