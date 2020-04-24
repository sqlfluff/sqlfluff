"""The Teradata dialect.

This inherits from the ansi dialect, with changes as specified by
Teradata Database SQL Data Definition Language Syntax and Examples

    Release Number 15.10
    Release Date December 2015

# BTEQ commands
.if errorcode > 0 then .quit 2
.IF ACTIVITYCOUNT = 0 THEN .QUIT

LOGON − Used to log into Teradata system.
ACTIVITYCOUNT − Returns the number of rows affected by the previous query.
ERRORCODE − Returns the status code of the previous query.
DATABASE − Sets the default database.
LABEL − Assigns a label to a set of SQL commands.
RUN FILE − Executes the query contained in a file.
GOTO − Transfers control to a label.
LOGOFF − Logs off from database and terminates all sessions.
IMPORT − Specifies the input file path.
EXPORT − Specifies the output file path and initiates the export.

"""

from .dialect_ansi import ansi_dialect
from ..parser import (BaseSegment, KeywordSegment, Sequence, GreedyUntil,
                      StartsWith, OneOf, Delimited, Bracketed,
                      AnyNumberOf, Ref, Anything)

teradata_dialect = ansi_dialect.copy_as('teradata')

teradata_dialect.patch_lexer_struct([
    # name, type, pattern, kwargs, so it also matches 1.
    ("numeric_literal", "regex", r"([0-9]+(\.[0-9]*)?)", dict(is_code=True)),
])


# BTEQ statement
@teradata_dialect.segment()
class BteqKeyWordSegment(BaseSegment):
    """Bteq Keywords.

    Often stsrting with a dot, sometimes followed by a Literal
    """
    type = 'bteq_key_word_segment'
    match_grammar = Sequence(
        Ref('DotSegment', optional=True),
        OneOf(
            Ref('IfKeywordSegment'),
            Ref('ThenKeywordSegment'),
            Ref('LogonKeywordSegment'),
            Ref('ActivitycountKeywordSegment'),
            Ref('ErrorcodeKeywordSegment'),
            Ref('DatabaseKeywordSegment'),
            Ref('LabelKeywordSegment'),
            Ref('GotoKeywordSegment'),
            Ref('LogoffKeywordSegment'),
            Ref('ImportKeywordSegment'),
            Ref('ExportKeywordSegment'),
            Ref('RunKeywordSegment'),
            Ref('QuitKeywordSegment'),
            Ref('ActivitycountKeywordSegment'),
        ),
        Ref('LiteralGrammar', optional=True),
    )


@teradata_dialect.segment()
class BteqStatementSegment(BaseSegment):
    """Bteq statements start with a dot, followed by a Keyword.

    Non exhaustive and maybe catching too many statements?
    """
    type = 'bteq_statement'
    match_grammar = StartsWith(Ref('DotSegment'))
    parse_grammar = Sequence(
        Ref('DotSegment'),
        Ref('BteqKeyWordSegment'),
        AnyNumberOf(
            Ref('BteqKeyWordSegment'),
            # if ... then: the ...
            Sequence(
                Ref('ComparisonOperatorGrammar'),
                Ref('LiteralGrammar'),
                optional=True
            ),
            optional=True
        )
    )


# Collect Statistics statement
@teradata_dialect.segment()
class TdCollectStatisticsStatementSegment(BaseSegment):
    """A `COLLECT STATISTICS (Optimizer Form)` statement.

    # TODO: Make complete
    COLLECT [SUMMARY] (STATISTICS|STAT) [[COLUMN| [UNIQUE] INDEX] (expression (, expression ...)] ON TABLENAME
    """
    type = 'collect_statistics_statement'
    match_grammar = Sequence(
        Ref('CollectKeywordSegment'),
        Ref('SummaryKeywordSegment', optional=True),
        OneOf(
            Ref('StatisticsKeywordSegment'),
            Ref('StatKeywordSegment')
        ),
        OneOf(
            Sequence(
                OneOf(
                    Ref('ColumnKeywordSegment'),
                    Sequence(
                        Ref('UniqueKeywordSegment', optional=True),
                        Ref('IndexKeywordSegment'),
                    )
                ),
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref('ObjectReferenceSegment'),
                            delimiter=Ref('CommaSegment')
                        )
                    ),
                    Ref('ObjectReferenceSegment'),
                )
            ),
            optional=True
        ),
        Ref('OnKeywordSegment'),
        Ref('ObjectReferenceSegment'),
    )


# Adding Teradata specific DATE FORMAT 'YYYYMM'
@teradata_dialect.segment()
class TdDatatypeSegment(BaseSegment):
    """A data type segment."""
    type = 'data_type'
    match_grammar = Sequence(
        Ref('DatatypeIdentifierSegment'),
        Bracketed(
            OneOf(
                Delimited(
                    Ref('ExpressionSegment'),
                    delimiter=Ref('CommaSegment')
                ),
                # The brackets might be empty for some cases...
                optional=True
            ),
            # There may be no brackets for some data types
            optional=True
        ),
        Sequence(  # FORMAT 'YYYY-MM-DD',
            Ref('FormatKeywordSegment'),
            Ref('QuotedLiteralSegment'),
            optional=True
        ),
    )


# Adding Teradata specific column definitions
@teradata_dialect.segment()
class TdColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""
    type = 'column_definition'
    match_grammar = Sequence(
        Ref('ObjectReferenceSegment'),  # Column name
        Ref('DatatypeSegment'),  # Column type
        Bracketed(  # For types like VARCHAR(100)
            Anything(),
            optional=True
        ),
        AnyNumberOf(
            Ref('ColumnOptionSegment', optional=True),
            # Adding Teradata specific column definitions
            Ref('TdColumnOptionSegment', optional=True),
        )
    )


@teradata_dialect.segment()
class TdColumnOptionSegment(BaseSegment):
    """Teradata specific column attributes.

    e.g. CHARACTER SET LATIN or [NOT] CASESPECIFIC
    """
    type = 'td_column_attribute_constraint'
    match_grammar = Sequence(
        OneOf(
            Sequence(  # CHARACTER SET LATIN
                Ref('CharacterKeywordSegment'),
                Ref('SetKeywordSegment'),
                Ref('SingleIdentifierGrammar')
            ),
            Sequence(  # [NOT] CASESPECIFIC
                Ref('NotKeywordSegment', optional=True),
                Ref('CasespecificKeywordSegment'),
            ),
            Sequence(  # COMPRESS [(1.,3.) | 3. | NULL],
                Ref('CompressKeywordSegment'),
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref('LiteralGrammar'),
                            delimiter=Ref('CommaSegment')
                        )
                    ),
                    Ref('LiteralGrammar'),
                    Ref('NullKeywordSegment'),
                    optional=True
                )
            ),
        ),
    )


# Create Teradata Create Table Statement
@teradata_dialect.segment()
class TdCreateTableOptions(BaseSegment):
    """CreateTableOptions.

    , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL, CHECKSUM = DEFAULT, DEFAULT MERGEBLOCKRATIO
    """
    type = 'create_table_options_statement'
    match_grammar = AnyNumberOf(
        Sequence(
            Ref('CommaSegment'),
            OneOf(
                # [ NO ] FALLBACK [ PROTECTION ]
                Sequence(
                    Ref('NoKeywordSegment', optional=True),
                    Ref('FallbackKeywordSegment'),
                    Ref('ProtectionKeywordSegment', optional=True),
                ),
                # [NO | DUAL | LOCAL |NOT LOCAL] [AFTER | BEFORE] JOURNAL
                Sequence(
                    OneOf(
                        Ref('NoKeywordSegment'),
                        Ref('DualKeywordSegment'),
                        Ref('LocalKeywordSegment'),
                        Sequence(Ref('NotKeywordSegment'), Ref('LocalKeywordSegment')),
                        optional=True
                    ),
                    OneOf(
                        Ref('BeforeKeywordSegment'),
                        Ref('AfterKeywordSegment'),
                        optional=True
                    ),
                    Ref('JournalKeywordSegment'),
                ),
                # CHECKSUM = (ON|OFF|DEFAULT)
                Sequence(
                    Ref('ChecksumKeywordSegment'),
                    Ref('EqualsSegment'),
                    OneOf(
                        Ref('OnKeywordSegment'),
                        Ref('OffKeywordSegment'),
                        Ref('DefaultKeywordSegment'),
                    ),
                ),
                # (NO|Default) MergeBlockRatio
                Sequence(
                    OneOf(
                        Ref('DefaultKeywordSegment'),
                        Ref('NoKeywordSegment'),
                    ),
                    Ref('MergeBlockRatioKeywordSegment'),
                ),
                # MergeBlockRatio = integer [PERCENT]
                Sequence(
                    Ref('MergeBlockRatioKeywordSegment'),
                    Ref('EqualsSegment'),
                    Ref('NumericLiteralSegment'),
                    Ref('PercentKeywordSegment', optional=True),
                ),
            ),
        ),
    )


@teradata_dialect.segment()
class TdColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""
    type = 'column_definition'
    match_grammar = Sequence(
        Ref('ObjectReferenceSegment'),  # Column name
        Ref('DatatypeSegment'),  # Column type
        Bracketed(  # For types like VARCHAR(100)
            Anything(),
            optional=True
        ),
        AnyNumberOf(
            Ref('ColumnOptionSegment', optional=True),
            Ref('TdColumnOptionSegment', optional=True),
        )
    )


@teradata_dialect.segment()
class TdColumnOptionSegment(BaseSegment):
    """Teradata specific column attributes.

    e.g. CHARACTER SET LATIN or [NOT] CASESPECIFIC
    """
    type = 'td_column_attribute_constraint'
    match_grammar = Sequence(
        OneOf(
            Sequence(  # CHARACTER SET LATIN
                Ref('CharacterKeywordSegment'),
                Ref('SetKeywordSegment'),
                Ref('SingleIdentifierGrammar')
            ),
            Sequence(  # [NOT] CASESPECIFIC
                Ref('NotKeywordSegment', optional=True),
                Ref('CasespecificKeywordSegment'),
            ),
            Sequence(  # COMPRESS [(1.,3.) | 3. | NULL],
                Ref('CompressKeywordSegment'),
                OneOf(
                    Bracketed(
                        Delimited(
                            Ref('LiteralGrammar'),
                            delimiter=Ref('CommaSegment')
                        )
                    ),
                    Ref('LiteralGrammar'),
                    Ref('NullKeywordSegment'),
                    optional=True
                )
            ),
            Sequence(  # FORMAT 'YYYY-MM-DD',
                Ref('FormatKeywordSegment'),
                Ref('QuotedLiteralSegment'),
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
    type = 'td_partitioning_level'
    match_grammar = OneOf(
        Sequence(
            Ref('FunctionNameSegment'),
            Bracketed(
                Anything(optional=True)
            ),
        ),
        Bracketed(
            Delimited(
                Sequence(
                    Ref('FunctionNameSegment'),
                    Bracketed(
                        Anything(optional=True)
                    ),
                ),
                delimiter=Ref('CommaSegment')
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
    type = 'td_table_constraint'
    match_grammar = Sequence(
        AnyNumberOf(
            # PRIMARY Index
            OneOf(
                Sequence(  # UNIQUE PRIMARY INDEX Column_name | ( Column_name, ... )
                    Ref('UniqueKeywordSegment', optional=True),
                    Ref('PrimaryKeywordSegment'),
                    Ref('IndexKeywordSegment'),
                    OneOf(
                        Bracketed(
                            Delimited(
                                Ref('SingleIdentifierGrammar'),
                                delimiter=Ref('CommaSegment')
                            )
                        ),
                        Ref('SingleIdentifierGrammar'),
                    ),
                ),
                Sequence(  # NO PRIMARY INDEX
                    Ref('NoKeywordSegment'),
                    Ref('PrimaryKeywordSegment'),
                    Ref('IndexKeywordSegment')
                ),
            ),
            # PARTITION BY ...
            Sequence(  # INDEX HOPR_TRN_TRAV_SIN_MP_I ( IND_TIPO_TARJETA );
                Ref('PartitionKeywordSegment'),
                Ref('ByKeywordSegment'),
                Ref('TdTablePartitioningLevel'),
            ),
            # Index
            Sequence(  # INDEX HOPR_TRN_TRAV_SIN_MP_I ( IND_TIPO_TARJETA );
                Ref('UniqueKeywordSegment', optional=True),
                Ref('IndexKeywordSegment'),
                Ref('ObjectReferenceSegment'),  # Index name
                Ref('AllKeywordSegment', optional=True),
                Bracketed(  # Columns making up  constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
            ),
        )
    )


@teradata_dialect.segment()
class TdCreateTableStatementSegment(BaseSegment):
    """A `CREATE [MULTISET| SET] TABLE` statement."""
    type = 'create_table_statement'
    match_grammar = Sequence(
        Ref('CreateKeywordSegment'),
        Sequence(
            Ref('OrKeywordSegment'),
            Ref('ReplaceKeywordSegment'),
            optional=True
        ),
        # Adding Teradata specific [MULTISET| SET]
        OneOf(
            Ref('SetKeywordSegment'),
            Ref('MultiSetKeywordSegment'),
            optional=True
        ),
        OneOf(
            Sequence(
                Ref('GlobalKeywordSegment'), Ref('TemporaryKeywordSegment')
            ),
            Ref('VolatileKeywordSegment'),
            optional=True
        ),
        Ref('TableKeywordSegment'),
        Sequence(
            Ref('IfKeywordSegment'),
            Ref('NotKeywordSegment'),
            Ref('ExistsKeywordSegment'),
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
        # , NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL
        OneOf(
            Ref('TdCreateTableOptions'),
            optional=True
        ),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref('ColumnDefinitionSegment'),
                            Ref('TableConstraintSegment'),
                        ),
                        delimiter=Ref('CommaSegment')
                    )
                ),
                Sequence(  # [COMMENT 'string'] (MySQL)
                    Ref('CommentKeywordSegment'),
                    Ref('QuotedLiteralSegment'),
                    optional=True
                )
            ),
            # Create AS syntax:
            Sequence(
                Ref('AsKeywordSegment'),
                OneOf(
                    Ref('SelectStatementSegment'),
                    Ref('WithCompoundStatementSegment')
                )
            ),
            # Create like syntax
            Sequence(
                Ref('LikeKeywordSegment'),
                Ref('ObjectReferenceSegment')
            )
        ),
        # PRIMARY INDEX( COD_TARJETA, COD_EST, IND_TIPO_TARJETA, FEC_ANIO_MES )
        OneOf(
            Ref('TdTableConstraints'),
            optional=True
        ),
    )


# Update
@teradata_dialect.segment()
class TdUpdateStatementSegment(BaseSegment):
    """A `Update from` statement.

    The UPDATE statement FROM clause is a Teradata extension to the
    ANSI SQL:2011 standard.

    UPDATE (<table name> | FROM Statement)
    SET <set clause list> [ WHERE <search condition> ]
    """
    type = 'delete_statement'
    match_grammar = StartsWith(Ref('UpdateKeywordSegment'))
    parse_grammar = Sequence(
        Ref('UpdateKeywordSegment'),
        OneOf(
            Ref('ObjectReferenceSegment'),
            Ref('FromUpdateClauseSegment'),
            Sequence(
                Ref('ObjectReferenceSegment'),
                Ref('FromUpdateClauseSegment'),
            ),
        ),
        Ref('SetClauseListSegment'),
        Ref('WhereClauseSegment', optional=True),
    )


@teradata_dialect.segment()
class FromUpdateClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT` but terminated by SET."""
    type = 'from_in_update_clause'
    match_grammar = StartsWith(
        Ref('FromKeywordSegment'),
        terminator=Ref('SetKeywordSegment')
    )
    parse_grammar = Sequence(
        Ref('FromKeywordSegment'),
        Delimited(
            # Optional old school delimited joins
            Ref('TableExpressionSegment'),
            delimiter=Ref('CommaSegment')
        ),
    )


# Adding Teradata specific statements
@teradata_dialect.segment()
class TdStatementSegment(BaseSegment):
    """A generic segment, to any of it's child subsegments.

    NOTE: Should this actually be a grammar?
    """
    type = 'statement'
    parse_grammar = OneOf(
        Ref('SetExpressionSegment'),
        Ref('SelectStatementSegment'), Ref('InsertStatementSegment'),
        Ref('EmptyStatementSegment'), Ref('WithCompoundStatementSegment'),
        Ref('TransactionStatementSegment'), Ref('DropStatementSegment'),
        Ref('AccessStatementSegment'), Ref('CreateTableStatementSegment'),
        Ref('CreateViewStatementSegment'),
        Ref('DeleteStatementSegment'), Ref('UpdateStatementSegment'),
        # Teradata specific statements
        Ref('TdCollectStatisticsStatementSegment'),
        Ref('BteqStatementSegment'),
        Ref('TdCreateTableStatementSegment'),
        Ref('TdUpdateStatementSegment'),
    )
    match_grammar = GreedyUntil(Ref('SemicolonSegment'))


teradata_dialect.add(
    MultiSetKeywordSegment=KeywordSegment.make('multiset'),
    TemporaryKeywordSegment=KeywordSegment.make('temporary'),
    GlobalKeywordSegment=KeywordSegment.make('global'),
    VolatileKeywordSegment=KeywordSegment.make('volatile'),
    FallbackKeywordSegment=KeywordSegment.make('fallback'),
    ProtectionKeywordSegment=KeywordSegment.make('protection'),
    DualKeywordSegment=KeywordSegment.make('dual'),
    BeforeKeywordSegment=KeywordSegment.make('before'),
    AfterKeywordSegment=KeywordSegment.make('after'),
    JournalKeywordSegment=KeywordSegment.make('journal'),
    LocalKeywordSegment=KeywordSegment.make('local'),
    CharacterKeywordSegment=KeywordSegment.make('character'),
    CasespecificKeywordSegment=KeywordSegment.make('casespecific'),
    CompressKeywordSegment=KeywordSegment.make('compress'),
    IndexKeywordSegment=KeywordSegment.make('index'),
    FormatKeywordSegment=KeywordSegment.make('format'),
    ChecksumKeywordSegment=KeywordSegment.make('checksum'),
    OffKeywordSegment=KeywordSegment.make('off'),
    MergeBlockRatioKeywordSegment=KeywordSegment.make('mergeblockratio'),
    PercentKeywordSegment=KeywordSegment.make('percent'),
    # Collect Statistics Keywords:
    CollectKeywordSegment=KeywordSegment.make('collect'),
    SummaryKeywordSegment=KeywordSegment.make('summary'),
    StatisticsKeywordSegment=KeywordSegment.make('statistics'),
    StatKeywordSegment=KeywordSegment.make('stat'),
    ColumnKeywordSegment=KeywordSegment.make('column'),
    # BTEQ Keywords
    LogonKeywordSegment=KeywordSegment.make('logon'),
    ActivitycountKeywordSegment=KeywordSegment.make('activitycount'),
    ErrorcodeKeywordSegment=KeywordSegment.make('errorcode'),
    DatabaseKeywordSegment=KeywordSegment.make('database'),
    LabelKeywordSegment=KeywordSegment.make('label'),
    GotoKeywordSegment=KeywordSegment.make('goto'),
    LogoffKeywordSegment=KeywordSegment.make('logoff'),
    ImportKeywordSegment=KeywordSegment.make('import'),
    ExportKeywordSegment=KeywordSegment.make('export'),
    RunKeywordSegment=KeywordSegment.make('run'),
    QuitKeywordSegment=KeywordSegment.make('quit'),
)

teradata_dialect.replace(
    DatatypeSegment=Ref('TdDatatypeSegment'),
    ColumnDefinitionSegment=Ref('TdColumnDefinitionSegment'),
    StatementSegment=Ref('TdStatementSegment'),
    UpdateStatementSegment=Ref('TdUpdateStatementSegment'),
)
