/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::parser::Grammar;

// name='DelimiterGrammar'
pub static DELIMITER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='SemicolonSegment'
pub static SEMICOLON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColonSegment'
pub static COLON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SliceSegment'
pub static SLICE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColonDelimiterSegment'
pub static COLON_DELIMITER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColonPrefixSegment'
pub static COLON_PREFIX_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartBracketSegment'
pub static START_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndBracketSegment'
pub static END_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartSquareBracketSegment'
pub static START_SQUARE_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndSquareBracketSegment'
pub static END_SQUARE_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartCurlyBracketSegment'
pub static START_CURLY_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndCurlyBracketSegment'
pub static END_CURLY_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommaSegment'
pub static COMMA_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DotSegment'
pub static DOT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StarSegment'
pub static STAR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TildeSegment'
pub static TILDE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParameterSegment'
pub static PARAMETER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CastOperatorSegment'
pub static CAST_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlusSegment'
pub static PLUS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinusSegment'
pub static MINUS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PositiveSegment'
pub static POSITIVE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NegativeSegment'
pub static NEGATIVE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DivideSegment'
pub static DIVIDE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MultiplySegment'
pub static MULTIPLY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModuloSegment'
pub static MODULO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SlashSegment'
pub static SLASH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AmpersandSegment'
pub static AMPERSAND_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PipeSegment'
pub static PIPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BitwiseXorSegment'
pub static BITWISE_XOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GlobOperatorSegment'
pub static GLOB_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='LikeOperatorSegment'
pub static LIKE_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='RawNotSegment'
pub static RAW_NOT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RawEqualsSegment'
pub static RAW_EQUALS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RawGreaterThanSegment'
pub static RAW_GREATER_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RawLessThanSegment'
pub static RAW_LESS_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BareFunctionSegment'
pub static BARE_FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='NakedIdentifierSegment'
pub static NAKED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='ParameterNameSegment'
pub static PARAMETER_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='FunctionNameIdentifierSegment'
pub static FUNCTION_NAME_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='DatatypeIdentifierSegment'
pub static DATATYPE_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::RegexParser()
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DatetimeUnitSegment'
pub static DATETIME_UNIT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='DatePartFunctionName'
pub static DATE_PART_FUNCTION_NAME: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='QuotedIdentifierSegment'
pub static QUOTED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='QuotedLiteralSegment'
pub static QUOTED_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='SingleQuotedIdentifierSegment'
pub static SINGLE_QUOTED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='NumericLiteralSegment'
pub static NUMERIC_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='NullLiteralSegment'
pub static NULL_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NanLiteralSegment'
pub static NAN_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='UnknownLiteralSegment'
pub static UNKNOWN_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NormalizedGrammar'
pub static NORMALIZED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='TrueSegment'
pub static TRUE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FalseSegment'
pub static FALSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SingleIdentifierGrammar'
pub static SINGLE_IDENTIFIER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EscapedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BooleanLiteralGrammar'
pub static BOOLEAN_LITERAL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TrueSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FalseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnknownSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ArithmeticBinaryOperatorGrammar'
pub static ARITHMETIC_BINARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PlusSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinusSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DivideSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MultiplySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ModuloSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BitwiseAndSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BitwiseOrSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BitwiseXorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BitwiseLShiftSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BitwiseRShiftSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SignedSegmentGrammar'
pub static SIGNED_SEGMENT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PositiveSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NegativeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='StringBinaryOperatorGrammar'
pub static STRING_BINARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ConcatSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BooleanBinaryOperatorGrammar'
pub static BOOLEAN_BINARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AndOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IsDistinctFromGrammar'
pub static IS_DISTINCT_FROM_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ComparisonOperatorGrammar'
pub static COMPARISON_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LessThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GreaterThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LessThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotEqualToSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LikeOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsDistinctFromGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DateTimeLiteralGrammar'
pub static DATE_TIME_LITERAL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::TypedParser()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeIntoLiteralGrammar'
pub static MERGE_INTO_LITERAL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MergeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LiteralGrammar'
pub static LITERAL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifiedNumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TypedArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AndOperatorGrammar'
pub static AND_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrOperatorGrammar'
pub static OR_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotOperatorGrammar'
pub static NOT_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreTableFunctionKeywordsGrammar'
pub static PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='BinaryOperatorGrammar'
pub static BINARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ArithmeticBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BooleanBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BracketedColumnReferenceListGrammar'
pub static BRACKETED_COLUMN_REFERENCE_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OrReplaceGrammar'
pub static OR_REPLACE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TemporaryTransientGrammar'
pub static TEMPORARY_TRANSIENT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TransientKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TemporaryGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TemporaryGrammar'
pub static TEMPORARY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IfExistsGrammar'
pub static IF_EXISTS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IfNotExistsGrammar'
pub static IF_NOT_EXISTS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LikeGrammar'
pub static LIKE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Regexp_likeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LikeExpressionGrammar'
pub static LIKE_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LikeGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EscapeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PatternMatchingGrammar'
pub static PATTERN_MATCHING_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='UnionGrammar'
pub static UNION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UnionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IsClauseGrammar'
pub static IS_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NanLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnknownLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NormalizedGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='InOperatorGrammar'
pub static IN_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SelectClauseTerminatorGrammar'
pub static SELECT_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IsNullGrammar'
pub static IS_NULL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NotNullGrammar'
pub static NOT_NULL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='CollateGrammar'
pub static COLLATE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='FromClauseTerminatorGrammar'
pub static FROM_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WhereClauseTerminatorGrammar'
pub static WHERE_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GroupByClauseTerminatorGrammar'
pub static GROUP_BY_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='HavingClauseTerminatorGrammar'
pub static HAVING_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OrderByClauseTerminators'
pub static ORDER_BY_CLAUSE_TERMINATORS: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PrimaryKeyGrammar'
pub static PRIMARY_KEY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ForeignKeyGrammar'
pub static FOREIGN_KEY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UniqueKeyGrammar'
pub static UNIQUE_KEY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NotEnforcedGrammar'
pub static NOT_ENFORCED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='FunctionParameterGrammar'
pub static FUNCTION_PARAMETER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AutoIncrementGrammar'
pub static AUTO_INCREMENT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Auto_incrementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BaseExpressionElementGrammar'
pub static BASE_EXPRESSION_ELEMENT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='FilterClauseGrammar'
pub static FILTER_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FilterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IgnoreRespectNullsGrammar'
pub static IGNORE_RESPECT_NULLS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RespectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FrameClauseUnitGrammar'
pub static FRAME_CLAUSE_UNIT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConditionalCrossJoinKeywordsGrammar'
pub static CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "CrossKeywordSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='JoinTypeKeywordsGrammar'
pub static JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "InnerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LeftKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RightKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OuterKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NonStandardJoinTypeKeywordsGrammar'
pub static NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ConditionalJoinKeywordsGrammar'
pub static CONDITIONAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonStandardJoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='JoinUsingConditionGrammar'
pub static JOIN_USING_CONDITION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='JoinKeywordsGrammar'
pub static JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "JoinKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NaturalJoinKeywordsGrammar'
pub static NATURAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NaturalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UnconditionalCrossJoinKeywordsGrammar'
pub static UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='HorizontalJoinKeywordsGrammar'
pub static HORIZONTAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='UnconditionalJoinKeywordsGrammar'
pub static UNCONDITIONAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NaturalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnconditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HorizontalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExtendedNaturalJoinKeywordsGrammar'
pub static EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NestedJoinGrammar'
pub static NESTED_JOIN_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ReferentialActionGrammar'
pub static REFERENTIAL_ACTION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RestrictKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ActionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropBehaviorGrammar'
pub static DROP_BEHAVIOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RestrictKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnConstraintDefaultGrammar'
pub static COLUMN_CONSTRAINT_DEFAULT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ShorthandCastSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReferenceMatchGrammar'
pub static REFERENCE_MATCH_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MatchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartialKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SimpleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReferenceDefinitionGrammar'
pub static REFERENCE_DEFINITION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReferenceMatchGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<AnySetOf: [<Sequence: [<Ref: 'OnKeywordSegment'>, <..., <Sequence: [<Ref: 'OnKeywordSegment'>, <...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TrimParametersGrammar'
pub static TRIM_PARAMETERS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BothKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LeadingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TrailingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DefaultValuesGrammar'
pub static DEFAULT_VALUES_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectReferenceDelimiterGrammar'
pub static OBJECT_REFERENCE_DELIMITER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectReferenceTerminatorGrammar'
pub static OBJECT_REFERENCE_TERMINATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CastOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StartSquareBracketSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StartBracketSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.bracketed.BracketedSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableOptionsGrammar'
pub static ALTER_TABLE_OPTIONS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableDropColumnGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableDropColumnGrammar'
pub static ALTER_TABLE_DROP_COLUMN_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OrderNoOrderGrammar'
pub static ORDER_NO_ORDER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NoorderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnsExpressionNameGrammar'
pub static COLUMNS_EXPRESSION_NAME_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ColumnsExpressionGrammar'
pub static COLUMNS_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ListComprehensionGrammar'
pub static LIST_COMPREHENSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='TimeWithTZGrammar'
pub static TIME_WITH_T_Z_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithoutKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SequenceMinValueGrammar'
pub static SEQUENCE_MIN_VALUE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MinvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SequenceMaxValueGrammar'
pub static SEQUENCE_MAX_VALUE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaxvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnGeneratedGrammar'
pub static COLUMN_GENERATED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='CharCharacterSetGrammar'
pub static CHAR_CHARACTER_SET_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Utf8KeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsciiKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AliasedTableReferenceGrammar'
pub static ALIASED_TABLE_REFERENCE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionContentsExpressionGrammar'
pub static FUNCTION_CONTENTS_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='FunctionContentsGrammar'
pub static FUNCTION_CONTENTS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TrimParametersGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionContentsExpressionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AggregateOrderByClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IgnoreRespectNullsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EmptyStructLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PostFunctionGrammar'
pub static POST_FUNCTION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "EmitsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RespectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PostTableExpressionGrammar'
pub static POST_TABLE_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='JoinLikeClauseGrammar'
pub static JOIN_LIKE_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='Expression_A_Unary_Operator_Grammar'
pub static EXPRESSION_A_UNARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PriorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Tail_Recurse_Expression_A_Grammar'
pub static TAIL_RECURSE_EXPRESSION_A_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_A_Unary_Operator_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Expression_A_Grammar'
pub static EXPRESSION_A_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LikeExpressionGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsClauseGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsNullGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotNullGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CollateGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PatternMatchingGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Expression_B_Unary_Operator_Grammar'
pub static EXPRESSION_B_UNARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Tail_Recurse_Expression_B_Grammar'
pub static TAIL_RECURSE_EXPRESSION_B_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_B_Unary_Operator_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Expression_B_Grammar'
pub static EXPRESSION_B_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Tail_Recurse_Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ArithmeticBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Expression_C_Grammar'
pub static EXPRESSION_C_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_D_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ShorthandCastSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='Expression_D_Potential_Select_Statement_Without_Brackets'
pub static EXPRESSION_D_POTENTIAL_SELECT_STATEMENT_WITHOUT_BRACKETS: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TypedStructLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArrayExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Expression_D_Grammar'
pub static EXPRESSION_D_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Expression_D_Potential_Select_Statement_Without_Brackets",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MapTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ListComprehensionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AccessorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AccessorGrammar'
pub static ACCESSOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ArrayAccessorSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SelectableGrammar'
pub static SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::OptionallyBracketed()
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NonWithSelectableGrammar'
pub static NON_WITH_SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SetExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NonWithNonSelectableGrammar'
pub static NON_WITH_NON_SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NonSetSelectableGrammar'
pub static NON_SET_SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnorderedSelectStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedSetExpressionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BracketedSetExpressionGrammar'
pub static BRACKETED_SET_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "UnorderedSetExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AccessStatementSegment'
pub static ACCESS_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RevokeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GrantRevokeSystemPrivilegesSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantRevokeObjectPrivilegesSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantRevokeRolesSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantRevokeImpersonationSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantRevokeConnectionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantRevokeConnectionRestrictedSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AggregateOrderByClause'
pub static AGGREGATE_ORDER_BY_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='AliasExpressionSegment'
pub static ALIAS_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "AsAliasOperatorSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterSequenceOptionsSegment'
pub static ALTER_SEQUENCE_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CacheKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterSequenceStatementSegment'
pub static ALTER_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "AlterSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableStatementSegment'
pub static ALTER_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlterTableColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableDistributePartitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ArrayAccessorSegment'
pub static ARRAY_ACCESSOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "SliceSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ArrayExpressionSegment'
pub static ARRAY_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ArrayLiteralSegment'
pub static ARRAY_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ArrayTypeSegment'
pub static ARRAY_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='AsAliasOperatorSegment'
pub static AS_ALIAS_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BaseFileSegment'
pub static BASE_FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.file.BaseFileSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='BaseSegment'
pub static BASE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.base.BaseSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='BinaryOperatorSegment'
pub static BINARY_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.BinaryOperatorSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='BitwiseAndSegment'
pub static BITWISE_AND_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "AmpersandSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='BitwiseLShiftSegment'
pub static BITWISE_L_SHIFT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='BitwiseOrSegment'
pub static BITWISE_OR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='BitwiseRShiftSegment'
pub static BITWISE_R_SHIFT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='BracketedArguments'
pub static BRACKETED_ARGUMENTS: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BracketedSegment'
pub static BRACKETED_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.bracketed.BracketedSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='CTEColumnList'
pub static C_T_E_COLUMN_LIST: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CTEDefinitionSegment'
pub static C_T_E_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CTEColumnList",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CaseExpressionSegment'
pub static CASE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='CodeSegment'
pub static CODE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.CodeSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='CollationReferenceSegment'
pub static COLLATION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnConstraintSegment'
pub static COLUMN_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IdentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableInlineConstraintSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnDefinitionSegment'
pub static COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnDatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnConstraintSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnReferenceSegment'
pub static COLUMN_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='ColumnsExpressionFunctionContentsSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ColumnsExpressionFunctionNameSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "ColumnsExpressionNameGrammar",
    optional: false,
    allow_gaps: true,
}
);

// name='CommentClauseSegment'
pub static COMMENT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CommentSegment'
pub static COMMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.CommentSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='ComparisonOperatorSegment'
pub static COMPARISON_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.ComparisonOperatorSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='CompositeBinaryOperatorSegment'
pub static COMPOSITE_BINARY_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.CompositeBinaryOperatorSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='CompositeComparisonOperatorSegment'
pub static COMPOSITE_COMPARISON_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.CompositeComparisonOperatorSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='ConcatSegment'
pub static CONCAT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='CreateCastStatementSegment'
pub static CREATE_CAST_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SpecificKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "InstanceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StaticKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConstructorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MethodKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AssignmentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateDatabaseStatementSegment'
pub static CREATE_DATABASE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateFunctionStatementSegment'
pub static CREATE_FUNCTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReturnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "VariableNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReturnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionContentsExpressionGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionReferenceSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SemicolonSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateIndexStatementSegment'
pub static CREATE_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateModelStatementSegment'
pub static CREATE_MODEL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OptionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateRoleStatementSegment'
pub static CREATE_ROLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateSchemaStatementSegment'
pub static CREATE_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateSequenceOptionsSegment'
pub static CREATE_SEQUENCE_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CacheKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateSequenceStatementSegment'
pub static CREATE_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CreateSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateTableStatementSegment'
pub static CREATE_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableContentDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableDistributionPartitionClause",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableLikeClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateTriggerStatementSegment'
pub static CREATE_TRIGGER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BeforeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsteadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferencingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OldKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImmediateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeferredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EachKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StatementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionNameIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateUserStatementSegment'
pub static CREATE_USER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IdentifiedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UserPasswordAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKerberosAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserLDAPAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserOpenIDAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateViewStatementSegment'
pub static CREATE_VIEW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForceKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CubeFunctionNameSegment'
pub static CUBE_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CubeRollupClauseSegment'
pub static CUBE_ROLLUP_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CubeFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RollupFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "GroupingExpressionList",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DatabaseReferenceSegment'
pub static DATABASE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='DatatypeSegment'
pub static DATATYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DecimalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DecKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumberKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BigintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DoubleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecisionKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FloatKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntegerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RealKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ShortintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TinyintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SmallintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BooleanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BoolKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LocalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "YearKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonthKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DayKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecondKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GeometryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "HashtypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VaryingKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VarcharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Varchar2KeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NcharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NvarcharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Nvarchar2KeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LongKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VarcharKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ClobKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CharCharacterSetGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DatePartFunctionNameSegment'
pub static DATE_PART_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "DatePartFunctionName",
    optional: false,
    allow_gaps: true,
}
);

// name='DateTimeFunctionContentsSegment'
pub static DATE_TIME_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Dedent'
pub static DEDENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='DeleteStatementSegment'
pub static DELETE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DescribeStatementSegment'
pub static DESCRIBE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DescribeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropCastStatementSegment'
pub static DROP_CAST_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropDatabaseStatementSegment'
pub static DROP_DATABASE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropFunctionStatementSegment'
pub static DROP_FUNCTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropIndexStatementSegment'
pub static DROP_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropModelStatementSegment'
pub static DROP_MODEL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropRoleStatementSegment'
pub static DROP_ROLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropSchemaStatementSegment'
pub static DROP_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForceKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropSequenceStatementSegment'
pub static DROP_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropTableStatementSegment'
pub static DROP_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConstraintsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropTriggerStatementSegment'
pub static DROP_TRIGGER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropTypeStatementSegment'
pub static DROP_TYPE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropUserStatementSegment'
pub static DROP_USER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropViewStatementSegment'
pub static DROP_VIEW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ElseClauseSegment'
pub static ELSE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EmptyStructLiteralBracketsSegment'
pub static EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EmptyStructLiteralSegment'
pub static EMPTY_STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EmptyStructLiteralBracketsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EqualsSegment'
pub static EQUALS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='ExplainStatementSegment'
pub static EXPLAIN_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExplainKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExpressionSegment'
pub static EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
);

// name='ExtensionReferenceSegment'
pub static EXTENSION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='FetchClauseSegment'
pub static FETCH_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NextKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OnlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TiesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FileSegment'
pub static FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionScriptStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionScriptTerminatorSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FrameClauseSegment'
pub static FRAME_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FromClauseSegment'
pub static FROM_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FromExpressionElementSegment'
pub static FROM_EXPRESSION_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PreTableFunctionKeywordsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PreTableFunctionKeywordsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FromExpressionSegment'
pub static FROM_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OptionallyBracketed()
);

// name='FunctionContentsSegment'
pub static FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionDefinitionGrammar'
pub static FUNCTION_DEFINITION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionNameSegment'
pub static FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='FunctionParameterListGrammar'
pub static FUNCTION_PARAMETER_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionParameterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionSegment'
pub static FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatePartFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DateTimeFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnsExpressionGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PostFunctionGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GreaterThanOrEqualToSegment'
pub static GREATER_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='GreaterThanSegment'
pub static GREATER_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='GroupByClauseSegment'
pub static GROUP_BY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CubeRollupClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupingSetsClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GroupingExpressionList'
pub static GROUPING_EXPRESSION_LIST: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "GroupByClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GroupingSetsClauseSegment'
pub static GROUPING_SETS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "CubeRollupClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupingExpressionList",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='HavingClauseSegment'
pub static HAVING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OptionallyBracketed()
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IdentifierSegment'
pub static IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.IdentifierSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='ImplicitIndent'
pub static IMPLICIT_INDENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='Indent'
pub static INDENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='IndexColumnDefinitionSegment'
pub static INDEX_COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IndexReferenceSegment'
pub static INDEX_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='InsertStatementSegment'
pub static INSERT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ValuesRangeClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IntervalExpressionSegment'
pub static INTERVAL_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MonthKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "YearKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonthKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DayKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HourKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SecondKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "HourKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SecondKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='JoinClauseSegment'
pub static JOIN_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConditionalJoinKeywordsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "NestedJoinGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Sequence {
    elements: vec![
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JoinUsingConditionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UnconditionalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExtendedNaturalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='JoinOnConditionSegment'
pub static JOIN_ON_CONDITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::OptionallyBracketed()
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='KeywordSegment'
pub static KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.keyword.KeywordSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='LessThanOrEqualToSegment'
pub static LESS_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='LessThanSegment'
pub static LESS_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='LimitClauseSegment'
pub static LIMIT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LiteralKeywordSegment'
pub static LITERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.keyword.LiteralKeywordSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='LiteralSegment'
pub static LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.LiteralSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='LocalAliasSegment'
pub static LOCAL_ALIAS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LocalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MLTableExpressionSegment'
pub static M_L_TABLE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='MapTypeSegment'
pub static MAP_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='MatchConditionSegment'
pub static MATCH_CONDITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='MergeDeleteClauseSegment'
pub static MERGE_DELETE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeInsertClauseSegment'
pub static MERGE_INSERT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeMatchSegment'
pub static MERGE_MATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MergeMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeNotMatchedClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MergeNotMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeMatchedClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeMatchedClauseSegment'
pub static MERGE_MATCHED_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MergeUpdateClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeDeleteClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeNotMatchedClauseSegment'
pub static MERGE_NOT_MATCHED_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeInsertClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeStatementSegment'
pub static MERGE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MergeIntoLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "MergeMatchSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeUpdateClauseSegment'
pub static MERGE_UPDATE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NamedWindowExpressionSegment'
pub static NAMED_WINDOW_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NamedWindowSegment'
pub static NAMED_WINDOW_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "NamedWindowExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NewlineSegment'
pub static NEWLINE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.NewlineSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='NotEqualToSegment'
pub static NOT_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawNotSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectLiteralElementSegment'
pub static OBJECT_LITERAL_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectLiteralSegment'
pub static OBJECT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectLiteralElementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectReferenceSegment'
pub static OBJECT_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='OffsetClauseSegment'
pub static OFFSET_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OrderByClauseSegment'
pub static ORDER_BY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithFillSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OverClauseSegment'
pub static OVER_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "IgnoreRespectNullsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OverlapsClauseSegment'
pub static OVERLAPS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OverlapsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PartitionClauseSegment'
pub static PARTITION_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OptionallyBracketed()
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PathSegment'
pub static PATH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::TypedParser()
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='QualifiedNumericLiteralSegment'
pub static QUALIFIED_NUMERIC_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='RawSegment'
pub static RAW_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.raw.RawSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='RoleReferenceSegment'
pub static ROLE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
);

// name='RollupFunctionNameSegment'
pub static ROLLUP_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SamplingExpressionSegment'
pub static SAMPLING_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablesampleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BernoulliKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SystemKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RepeatableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SchemaReferenceSegment'
pub static SCHEMA_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='SelectClauseElementSegment'
pub static SELECT_CLAUSE_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "WildcardExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SelectClauseModifierSegment'
pub static SELECT_CLAUSE_MODIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SelectClauseSegment'
pub static SELECT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectClauseModifierSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseElementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: true,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithInvalidForeignKeySegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithInvalidUniquePKSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntoTableSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='SelectStatementSegment'
pub static SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReferencingClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='SequenceReferenceSegment'
pub static SEQUENCE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='SetClauseListSegment'
pub static SET_CLAUSE_LIST_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SetClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetClauseSegment'
pub static SET_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetExpressionSegment'
pub static SET_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetOperatorSegment'
pub static SET_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UnionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntersectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MinusKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExceptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetSchemaStatementSegment'
pub static SET_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ShorthandCastSegment'
pub static SHORTHAND_CAST_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_D_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CastOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SingleIdentifierListSegment'
pub static SINGLE_IDENTIFIER_LIST_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SizedArrayTypeSegment'
pub static SIZED_ARRAY_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArrayAccessorSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='StatementSegment'
pub static STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExportStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TruncateStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterVirtualSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateViewStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateVirtualSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropViewStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropFunctionStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropScriptStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RenameStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AccessStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterConnectionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterUserStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateConnectionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateRoleStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateUserStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropRoleStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropUserStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropConnectionStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateConsumerGroupSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterConsumerGroupSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropConsumerGroupSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterRoleStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterSessionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterSystemSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenSchemaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CloseSchemaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FlushStatisticsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImpersonateSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RecompressReorganizeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KillSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreloadSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TruncateAuditLogsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExplainVirtualSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TransactionStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExecuteScriptSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='StructLiteralSegment'
pub static STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='StructTypeSegment'
pub static STRUCT_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='SymbolSegment'
pub static SYMBOL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.SymbolSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='TableConstraintSegment'
pub static TABLE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableEndClauseSegment'
pub static TABLE_END_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='TableExpressionSegment'
pub static TABLE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ValuesRangeClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExplainVirtualSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableReferenceSegment'
pub static TABLE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='TablespaceReferenceSegment'
pub static TABLESPACE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='TagReferenceSegment'
pub static TAG_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='TemporalQuerySegment'
pub static TEMPORAL_QUERY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='TimeZoneGrammar'
pub static TIME_ZONE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TransactionStatementSegment'
pub static TRANSACTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CommitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WorkKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TriggerReferenceSegment'
pub static TRIGGER_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='TruncateStatementSegment'
pub static TRUNCATE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TupleSegment'
pub static TUPLE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TypedArrayLiteralSegment'
pub static TYPED_ARRAY_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TypedStructLiteralSegment'
pub static TYPED_STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StructLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UnorderedSelectStatementSegment'
pub static UNORDERED_SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReferencingClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QualifyClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
);

// name='UnorderedSetExpressionSegment'
pub static UNORDERED_SET_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UpdateStatementSegment'
pub static UPDATE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UseStatementSegment'
pub static USE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ValuesClauseSegment'
pub static VALUES_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WhenClauseSegment'
pub static WHEN_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WhereClauseSegment'
pub static WHERE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OptionallyBracketed()
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WhitespaceSegment'
pub static WHITESPACE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.WhitespaceSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='WildcardExpressionSegment'
pub static WILDCARD_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WildcardIdentifierSegment'
pub static WILDCARD_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='WindowSpecificationSegment'
pub static WINDOW_SPECIFICATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FrameClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithCompoundNonSelectStatementSegment'
pub static WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "NonWithNonSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithCompoundStatementSegment'
pub static WITH_COMPOUND_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
todo!()
,
Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithDataClauseSegment'
pub static WITH_DATA_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithFillSegment'
pub static WITH_FILL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='WithNoSchemaBindingClauseSegment'
pub static WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BindingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WordSegment'
pub static WORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.common.WordSegment'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
);

// name='PasswordLiteralSegment'
pub static PASSWORD_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='UDFParameterDotSyntaxSegment'
pub static U_D_F_PARAMETER_DOT_SYNTAX_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='RangeOperator'
pub static RANGE_OPERATOR: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='UnknownSegment'
pub static UNKNOWN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForeignKeyReferencesClauseGrammar'
pub static FOREIGN_KEY_REFERENCES_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnReferenceListGrammar'
pub static COLUMN_REFERENCE_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableDistributeByGrammar'
pub static TABLE_DISTRIBUTE_BY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistributeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "TablePartitionByGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TablePartitionByGrammar'
pub static TABLE_PARTITION_BY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "TableDistributeByGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableConstraintEnableDisableGrammar'
pub static TABLE_CONSTRAINT_ENABLE_DISABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "EnableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DisableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EscapedIdentifierSegment'
pub static ESCAPED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='SessionParameterSegment'
pub static SESSION_PARAMETER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='SystemParameterSegment'
pub static SYSTEM_PARAMETER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='UDFParameterGrammar'
pub static U_D_F_PARAMETER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnDatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UDFParameterDotSyntaxSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionScriptTerminatorSegment'
pub static FUNCTION_SCRIPT_TERMINATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='WalrusOperatorSegment'
pub static WALRUS_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VariableNameSegment'
pub static VARIABLE_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='AlterConnectionSegment'
pub static ALTER_CONNECTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterConsumerGroupSegment'
pub static ALTER_CONSUMER_GROUP_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ConsumerGroupParameterSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterRoleStatementSegment'
pub static ALTER_ROLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Consumer_groupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterSchemaStatementSegment'
pub static ALTER_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Raw_size_limitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ChangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OwnerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterSessionSegment'
pub static ALTER_SESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SessionParameterSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterSystemSegment'
pub static ALTER_SYSTEM_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SystemKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SystemParameterSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableAddColumnSegment'
pub static ALTER_TABLE_ADD_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableAlterColumnSegment'
pub static ALTER_TABLE_ALTER_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IdentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IdentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableColumnSegment'
pub static ALTER_TABLE_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlterTableAddColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableDropColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableModifyColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableRenameColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableAlterColumnSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableConstraintSegment'
pub static ALTER_TABLE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableOutOfLineConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableConstraintEnableDisableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableDistributePartitionSegment'
pub static ALTER_TABLE_DISTRIBUTE_PARTITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableDistributionPartitionClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistributionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DistributionKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeysKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableDropColumnSegment'
pub static ALTER_TABLE_DROP_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConstraintsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableModifyColumnSegment'
pub static ALTER_TABLE_MODIFY_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterTableRenameColumnSegment'
pub static ALTER_TABLE_RENAME_COLUMN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterUserStatementSegment'
pub static ALTER_USER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IdentifiedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UserPasswordAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PasswordLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserLDAPAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKerberosAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserOpenIDAuthSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Password_expiry_policyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PasswordKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpireKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ResetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LoginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AttemptsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Consumer_groupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterVirtualSchemaStatementSegment'
pub static ALTER_VIRTUAL_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RefreshKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ChangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OwnerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CSVColumnDefinitionSegment'
pub static C_S_V_COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RangeOperator",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DelimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlwaysKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NeverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AutoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CloseSchemaSegment'
pub static CLOSE_SCHEMA_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CloseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ColumnDatatypeSegment'
pub static COLUMN_DATATYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CommentStatementSegment'
pub static COMMENT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConnectByClauseSegment'
pub static CONNECT_BY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConnectionDefinition'
pub static CONNECTION_DEFINITION: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IdentifiedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConsumerGroupParameterSegment'
pub static CONSUMER_GROUP_PARAMETER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Cpu_weightKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedenceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Group_temp_db_ram_limitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "User_temp_db_ram_limitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Session_temp_db_ram_limitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Query_timeoutKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Idle_timeoutKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateAdapterScriptStatementSegment'
pub static CREATE_ADAPTER_SCRIPT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JavaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PythonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LuaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AdapterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ScriptContentSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateConnectionSegment'
pub static CREATE_CONNECTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateConsumerGroupSegment'
pub static CREATE_CONSUMER_GROUP_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ConsumerGroupParameterSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateScriptingLuaScriptStatementSegment'
pub static CREATE_SCRIPTING_LUA_SCRIPT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LuaKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ArrayKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReturnsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowcountKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ScriptContentSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateTableLikeClauseSegment'
pub static CREATE_TABLE_LIKE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IncludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExcludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefaultsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IncludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExcludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IdentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IncludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExcludingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommentsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateUDFScriptStatementSegment'
pub static CREATE_U_D_F_SCRIPT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JavaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PythonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LuaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ScalarKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UDFParameterGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReturnsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EmitsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ScriptContentSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateVirtualSchemaStatementSegment'
pub static CREATE_VIRTUAL_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropConnectionStatementSegment'
pub static DROP_CONNECTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropConsumerGroupSegment'
pub static DROP_CONSUMER_GROUP_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropScriptStatementSegment'
pub static DROP_SCRIPT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AdapterKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EmitsSegment'
pub static EMITS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EmitsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "UDFParameterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExecuteScriptSegment'
pub static EXECUTE_SCRIPT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ArrayKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OutputKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExplainVirtualSegment'
pub static EXPLAIN_VIRTUAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExplainKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExportIntoClauseSegment'
pub static EXPORT_INTO_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ImportFromExportIntoDbSrcSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportFromExportIntoFileSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RejectClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportFromExportIntoScriptSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExportStatementSegment'
pub static EXPORT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExportIntoClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FBVColumnDefinitionSegment'
pub static F_B_V_COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SizeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PaddingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlignKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LeftKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RightKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FileOptionSegment'
pub static FILE_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "EncodingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BooleanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TrimKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LtrimKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RtrimKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SkipKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SizeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NamesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DelimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlwaysKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NeverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AutoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FlushStatisticsSegment'
pub static FLUSH_STATISTICS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FlushKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StatisticsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionAssignmentSegment'
pub static FUNCTION_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "VariableNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WalrusOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VariableNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionBodySegment'
pub static FUNCTION_BODY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionAssignmentSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionIfBranchSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionForLoopSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionWhileLoopSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionForLoopSegment'
pub static FUNCTION_FOR_LOOP_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WalrusOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RangeOperator",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LoopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LoopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionIfBranchSegment'
pub static FUNCTION_IF_BRANCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ElsifKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ElseifKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: None,
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionReferenceSegment'
pub static FUNCTION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='FunctionScriptStatementSegment'
pub static FUNCTION_SCRIPT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CreateFunctionStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateScriptingLuaScriptStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateUDFScriptStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateAdapterScriptStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionWhileLoopSegment'
pub static FUNCTION_WHILE_LOOP_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionBodySegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeConnectionRestrictedSegment'
pub static GRANT_REVOKE_CONNECTION_RESTRICTED_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AccessKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeConnectionSegment'
pub static GRANT_REVOKE_CONNECTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AdminKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeImpersonationSegment'
pub static GRANT_REVOKE_IMPERSONATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImpersonationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeObjectPrivilegesSegment'
pub static GRANT_REVOKE_OBJECT_PRIVILEGES_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectPrivilegesSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectsKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConstraintsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeRolesSegment'
pub static GRANT_REVOKE_ROLES_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RolesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AdminKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='GrantRevokeSystemPrivilegesSegment'
pub static GRANT_REVOKE_SYSTEM_PRIVILEGES_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SystemPrivilegesSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AdminKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImpersonateSegment'
pub static IMPERSONATE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImpersonateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportColumnsSegment'
pub static IMPORT_COLUMNS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnDatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableLikeClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportErrorDestinationSegment'
pub static IMPORT_ERROR_DESTINATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CsvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LocalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecureKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CsvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportErrorsClauseSegment'
pub static IMPORT_ERRORS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ErrorsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportErrorDestinationSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RejectClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportFromClauseSegment'
pub static IMPORT_FROM_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ImportFromExportIntoDbSrcSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportFromExportIntoFileSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportErrorsClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportFromExportIntoScriptSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportFromExportIntoDbSrcSegment'
pub static IMPORT_FROM_EXPORT_INTO_DB_SRC_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OraKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "JdbcKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DriverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreatedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(2),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StatementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportFromExportIntoFileSegment'
pub static IMPORT_FROM_EXPORT_INTO_FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CsvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FbvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LocalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecureKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CsvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FbvKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CSVColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FBVColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportFromExportIntoScriptSegment'
pub static IMPORT_FROM_EXPORT_INTO_SCRIPT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionDefinition",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 1,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ImportStatementSegment'
pub static IMPORT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ImportColumnsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser()
        ),
        Box::new(
Grammar::StringParser()
        )
    ),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportFromClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IntoTableSegment'
pub static INTO_TABLE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='KillSegment'
pub static KILL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "KillKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Current_sessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StatementKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MessageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ObjectPrivilegesSegment'
pub static OBJECT_PRIVILEGES_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OpenSchemaSegment'
pub static OPEN_SCHEMA_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PreferringClauseSegment'
pub static PREFERRING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PreferringKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "PartitionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PreferringPlusPriorTermSegment'
pub static PREFERRING_PLUS_PRIOR_TERM_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PlusKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PriorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringPreferenceTermSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InverseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringPreferenceTermSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PreferringPreferenceTermSegment'
pub static PREFERRING_PREFERENCE_TERM_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "HighKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PreferringPlusPriorTermSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PreloadSegment'
pub static PRELOAD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PreloadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='QualifyClauseSegment'
pub static QUALIFY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.ImplicitIndent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='RecompressReorganizeSegment'
pub static RECOMPRESS_REORGANIZE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RecompressKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReorganizeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EnforceKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReferencingClauseSegment'
pub static REFERENCING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferencingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='RejectClauseSegment'
pub static REJECT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RejectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UnlimitedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ErrorsKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='RenameStatementSegment'
pub static RENAME_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ScriptContentSegment'
pub static SCRIPT_CONTENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<Anything: []>, type:<class 'sqlfluff.core.parser.grammar.base.Anything'>
todo!()
);

// name='ScriptReferenceSegment'
pub static SCRIPT_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='SystemPrivilegesSegment'
pub static SYSTEM_PRIVILEGES_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ManageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConsumerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GroupsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "KillKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SystemKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImpersonateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AccessKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RefreshKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConnectionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SessionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DictionaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ScriptKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ImportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExportKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableContentDefinitionSegment'
pub static TABLE_CONTENT_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableOutOfLineConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableLikeClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableDistributionPartitionClause'
pub static TABLE_DISTRIBUTION_PARTITION_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableDistributeByGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TablePartitionByGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablePartitionByGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableDistributeByGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableInlineConstraintSegment'
pub static TABLE_INLINE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForeignKeyReferencesClauseGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableConstraintEnableDisableGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableOutOfLineConstraintSegment'
pub static TABLE_OUT_OF_LINE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForeignKeyReferencesClauseGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableConstraintEnableDisableGrammar",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TruncateAuditLogsSegment'
pub static TRUNCATE_AUDIT_LOGS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AuditKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LogsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "KeepKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DayKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonthKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "YearKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UserKerberosAuthSegment'
pub static USER_KERBEROS_AUTH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KerberosKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrincipalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UserLDAPAuthSegment'
pub static USER_L_D_A_P_AUTH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LdapKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForceKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UserOpenIDAuthSegment'
pub static USER_OPEN_I_D_AUTH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenidKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SubjectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UserPasswordAuthSegment'
pub static USER_PASSWORD_AUTH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PasswordLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ValuesRangeClauseSegment'
pub static VALUES_RANGE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StepKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ViewReferenceSegment'
pub static VIEW_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    allow_gaps: false,
}
);

// name='WithInvalidForeignKeySegment'
pub static WITH_INVALID_FOREIGN_KEY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InvalidKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForeignKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithInvalidUniquePKSegment'
pub static WITH_INVALID_UNIQUE_P_K_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InvalidKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NiceKeywordSegment'
pub static NICE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Date_truncKeywordSegment'
pub static DATE_TRUNC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RadiansKeywordSegment'
pub static RADIANS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FailedKeywordSegment'
pub static FAILED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_timestampKeywordSegment'
pub static IS_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecordKeywordSegment'
pub static RECORD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RKeywordSegment'
pub static R_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeastKeywordSegment'
pub static LEAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Posix_timeKeywordSegment'
pub static POSIX_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelimiterKeywordSegment'
pub static DELIMITER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_differenceKeywordSegment'
pub static ST_DIFFERENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Query_timeoutKeywordSegment'
pub static QUERY_TIMEOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LpadKeywordSegment'
pub static LPAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VirtualKeywordSegment'
pub static VIRTUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_issimpleKeywordSegment'
pub static ST_ISSIMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_rrotateKeywordSegment'
pub static BIT_RROTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PascalKeywordSegment'
pub static PASCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StatisticsKeywordSegment'
pub static STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_intersectionKeywordSegment'
pub static ST_INTERSECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CorrKeywordSegment'
pub static CORR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PaddingKeywordSegment'
pub static PADDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MumpsKeywordSegment'
pub static MUMPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_orKeywordSegment'
pub static BIT_OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TruncKeywordSegment'
pub static TRUNC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_interceptKeywordSegment'
pub static REGR_INTERCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_interiorringnKeywordSegment'
pub static ST_INTERIORRINGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Value2procKeywordSegment'
pub static VALUE2PROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DepthKeywordSegment'
pub static DEPTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Raw_size_limitKeywordSegment'
pub static RAW_SIZE_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NeverKeywordSegment'
pub static NEVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UncommittedKeywordSegment'
pub static UNCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Days_betweenKeywordSegment'
pub static DAYS_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Minutes_betweenKeywordSegment'
pub static MINUTES_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SkipKeywordSegment'
pub static SKIP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NormalizedKeywordSegment'
pub static NORMALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LuaKeywordSegment'
pub static LUA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_touchesKeywordSegment'
pub static ST_TOUCHES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_isclosedKeywordSegment'
pub static ST_ISCLOSED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Json_valueKeywordSegment'
pub static JSON_VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepKeywordSegment'
pub static KEEP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RolesKeywordSegment'
pub static ROLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_charKeywordSegment'
pub static TO_CHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UseKeywordSegment'
pub static USE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Consumer_groupKeywordSegment'
pub static CONSUMER_GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_md5KeywordSegment'
pub static HASHTYPE_MD5_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_lrotateKeywordSegment'
pub static BIT_LROTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_md5KeywordSegment'
pub static HASH_MD5_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_secondsKeywordSegment'
pub static ADD_SECONDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsymmetricKeywordSegment'
pub static ASYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JsonKeywordSegment'
pub static JSON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResetKeywordSegment'
pub static RESET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_startpointKeywordSegment'
pub static ST_STARTPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SizeKeywordSegment'
pub static SIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlignKeywordSegment'
pub static ALIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_numpointsKeywordSegment'
pub static ST_NUMPOINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AssignmentKeywordSegment'
pub static ASSIGNMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_sha512KeywordSegment'
pub static HASH_SHA512_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoginKeywordSegment'
pub static LOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='From_posix_timeKeywordSegment'
pub static FROM_POSIX_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_timestampKeywordSegment'
pub static TO_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CoshKeywordSegment'
pub static COSH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_intersectsKeywordSegment'
pub static ST_INTERSECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubjectKeywordSegment'
pub static SUBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nvl2KeywordSegment'
pub static NVL2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuthenticatedKeywordSegment'
pub static AUTHENTICATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreatedKeywordSegment'
pub static CREATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_sha256KeywordSegment'
pub static HASHTYPE_SHA256_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitcapKeywordSegment'
pub static INITCAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='First_valueKeywordSegment'
pub static FIRST_VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_dateKeywordSegment'
pub static TO_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultsKeywordSegment'
pub static DEFAULTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CeilingKeywordSegment'
pub static CEILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_overlapsKeywordSegment'
pub static ST_OVERLAPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharactersKeywordSegment'
pub static CHARACTERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MidKeywordSegment'
pub static MID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_equalsKeywordSegment'
pub static ST_EQUALS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_lshiftKeywordSegment'
pub static BIT_LSHIFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExpKeywordSegment'
pub static EXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Covar_popKeywordSegment'
pub static COVAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PasswordKeywordSegment'
pub static PASSWORD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Cpu_weightKeywordSegment'
pub static CPU_WEIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Temp_db_ram_limitKeywordSegment'
pub static TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CosKeywordSegment'
pub static COS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqrtKeywordSegment'
pub static SQRT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MultipleKeywordSegment'
pub static MULTIPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReorganizeKeywordSegment'
pub static REORGANIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SumKeywordSegment'
pub static SUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EmptyKeywordSegment'
pub static EMPTY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Stddev_popKeywordSegment'
pub static STDDEV_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoleKeywordSegment'
pub static ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrincipalKeywordSegment'
pub static PRINCIPAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Convert_tzKeywordSegment'
pub static CONVERT_TZ_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Var_popKeywordSegment'
pub static VAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_boundaryKeywordSegment'
pub static ST_BOUNDARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablesKeywordSegment'
pub static TABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtomicKeywordSegment'
pub static ATOMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Session_temp_db_ram_limitKeywordSegment'
pub static SESSION_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Edit_distanceKeywordSegment'
pub static EDIT_DISTANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChrKeywordSegment'
pub static CHR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_lengthKeywordSegment'
pub static CHARACTER_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnlimitedKeywordSegment'
pub static UNLIMITED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxxKeywordSegment'
pub static REGR_SXX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Idle_timeoutKeywordSegment'
pub static IDLE_TIMEOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HierarchyKeywordSegment'
pub static HIERARCHY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_numberKeywordSegment'
pub static TO_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbsKeywordSegment'
pub static ABS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JavascriptKeywordSegment'
pub static JAVASCRIPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_booleanKeywordSegment'
pub static IS_BOOLEAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AutoKeywordSegment'
pub static AUTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreloadKeywordSegment'
pub static PRELOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncodingKeywordSegment'
pub static ENCODING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_disjointKeywordSegment'
pub static ST_DISJOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxKeywordSegment'
pub static MAX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RpadKeywordSegment'
pub static RPAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_bufferKeywordSegment'
pub static ST_BUFFER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Years_betweenKeywordSegment'
pub static YEARS_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BackupKeywordSegment'
pub static BACKUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_withinKeywordSegment'
pub static ST_WITHIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ratio_to_reportKeywordSegment'
pub static RATIO_TO_REPORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_contKeywordSegment'
pub static PERCENTILE_CONT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoticeKeywordSegment'
pub static NOTICE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Time_zoneKeywordSegment'
pub static TIME_ZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SymmetricKeywordSegment'
pub static SYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CurdateKeywordSegment'
pub static CURDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UcaseKeywordSegment'
pub static UCASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_notKeywordSegment'
pub static BIT_NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Json_extractKeywordSegment'
pub static JSON_EXTRACT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Months_betweenKeywordSegment'
pub static MONTHS_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EvaluateKeywordSegment'
pub static EVALUATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoundKeywordSegment'
pub static ROUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LtrimKeywordSegment'
pub static LTRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ZeroifnullKeywordSegment'
pub static ZEROIFNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_consumer_groupKeywordSegment'
pub static DEFAULT_CONSUMER_GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_xKeywordSegment'
pub static ST_X_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaximalKeywordSegment'
pub static MAXIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DictionaryKeywordSegment'
pub static DICTIONARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Last_valueKeywordSegment'
pub static LAST_VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_xorKeywordSegment'
pub static BIT_XOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DebugKeywordSegment'
pub static DEBUG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConsumerKeywordSegment'
pub static CONSUMER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistributeKeywordSegment'
pub static DISTRIBUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Timestamp_arithmetic_behaviorKeywordSegment'
pub static TIMESTAMP_ARITHMETIC_BEHAVIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_max_decimal_digitsKeywordSegment'
pub static ST_MAX_DECIMAL_DIGITS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsolationKeywordSegment'
pub static ISOLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LongKeywordSegment'
pub static LONG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_temp_db_ram_limitKeywordSegment'
pub static USER_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_isringKeywordSegment'
pub static ST_ISRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExpressionKeywordSegment'
pub static EXPRESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecedenceKeywordSegment'
pub static PRECEDENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SoundexKeywordSegment'
pub static SOUNDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DumpKeywordSegment'
pub static DUMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InvalidKeywordSegment'
pub static INVALID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShutKeywordSegment'
pub static SHUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DiagnosticsKeywordSegment'
pub static DIAGNOSTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Cologne_phoneticKeywordSegment'
pub static COLOGNE_PHONETIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NprocKeywordSegment'
pub static NPROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BernoulliKeywordSegment'
pub static BERNOULLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CountKeywordSegment'
pub static COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturningKeywordSegment'
pub static RETURNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowidKeywordSegment'
pub static ROWID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_lengthKeywordSegment'
pub static BIT_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TraceKeywordSegment'
pub static TRACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regexp_substrKeywordSegment'
pub static REGEXP_SUBSTR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_ymintervalKeywordSegment'
pub static IS_YMINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QuietKeywordSegment'
pub static QUIET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Atan2KeywordSegment'
pub static ATAN2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TypeKeywordSegment'
pub static TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RejectKeywordSegment'
pub static REJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Log10KeywordSegment'
pub static LOG10_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsinKeywordSegment'
pub static ASIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TanhKeywordSegment'
pub static TANH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConcatKeywordSegment'
pub static CONCAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Group_temp_db_ram_limitKeywordSegment'
pub static GROUP_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullifzeroKeywordSegment'
pub static NULLIFZERO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelimitKeywordSegment'
pub static DELIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InstrKeywordSegment'
pub static INSTR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeadKeywordSegment'
pub static LEAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecompressKeywordSegment'
pub static RECOMPRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AdminKeywordSegment'
pub static ADMIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_weeksKeywordSegment'
pub static ADD_WEEKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DegreesKeywordSegment'
pub static DEGREES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_force2dKeywordSegment'
pub static ST_FORCE2D_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LengthKeywordSegment'
pub static LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DownKeywordSegment'
pub static DOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LagKeywordSegment'
pub static LAG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Session_parameterKeywordSegment'
pub static SESSION_PARAMETER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Var_sampKeywordSegment'
pub static VAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CeilKeywordSegment'
pub static CEIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StepKeywordSegment'
pub static STEP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AvgKeywordSegment'
pub static AVG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_geometrytypeKeywordSegment'
pub static ST_GEOMETRYTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecodeKeywordSegment'
pub static DECODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrivilegeKeywordSegment'
pub static PRIVILEGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Time_zone_behaviorKeywordSegment'
pub static TIME_ZONE_BEHAVIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncludingKeywordSegment'
pub static INCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_numgeometriesKeywordSegment'
pub static ST_NUMGEOMETRIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PliKeywordSegment'
pub static PLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Password_expiry_policyKeywordSegment'
pub static PASSWORD_EXPIRY_POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UndoKeywordSegment'
pub static UNDO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverflowKeywordSegment'
pub static OVERFLOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitiallyKeywordSegment'
pub static INITIALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Covar_sampKeywordSegment'
pub static COVAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentifiedKeywordSegment'
pub static IDENTIFIED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DivKeywordSegment'
pub static DIV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_hoursKeywordSegment'
pub static ADD_HOURS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regexp_instrKeywordSegment'
pub static REGEXP_INSTR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SinhKeywordSegment'
pub static SINH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptimizeKeywordSegment'
pub static OPTIMIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_pointnKeywordSegment'
pub static ST_POINTN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_to_numKeywordSegment'
pub static BIT_TO_NUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LogsKeywordSegment'
pub static LOGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_discKeywordSegment'
pub static PERCENTILE_DISC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GreatestKeywordSegment'
pub static GREATEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QueryKeywordSegment'
pub static QUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ErrorKeywordSegment'
pub static ERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_dateKeywordSegment'
pub static IS_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_setsridKeywordSegment'
pub static ST_SETSRID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CobolKeywordSegment'
pub static COBOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_symdifferenceKeywordSegment'
pub static ST_SYMDIFFERENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DriverKeywordSegment'
pub static DRIVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HandlerKeywordSegment'
pub static HANDLER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Row_numberKeywordSegment'
pub static ROW_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NvlKeywordSegment'
pub static NVL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Snapshot_modeKeywordSegment'
pub static SNAPSHOT_MODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExpireKeywordSegment'
pub static EXPIRE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RespectKeywordSegment'
pub static RESPECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ObjectsKeywordSegment'
pub static OBJECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JavaKeywordSegment'
pub static JAVA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Stddev_sampKeywordSegment'
pub static STDDEV_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsciiKeywordSegment'
pub static ASCII_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Grouping_idKeywordSegment'
pub static GROUPING_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FloorKeywordSegment'
pub static FLOOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_shaKeywordSegment'
pub static HASHTYPE_SHA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_yearsKeywordSegment'
pub static ADD_YEARS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Script_output_addressKeywordSegment'
pub static SCRIPT_OUTPUT_ADDRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AdapterKeywordSegment'
pub static ADAPTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_isemptyKeywordSegment'
pub static ST_ISEMPTY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_exteriorringKeywordSegment'
pub static ST_EXTERIORRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SerializableKeywordSegment'
pub static SERIALIZABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LowerKeywordSegment'
pub static LOWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regexp_replaceKeywordSegment'
pub static REGEXP_REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sys_connect_by_pathKeywordSegment'
pub static SYS_CONNECT_BY_PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LockKeywordSegment'
pub static LOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_convexhullKeywordSegment'
pub static ST_CONVEXHULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImpersonationKeywordSegment'
pub static IMPERSONATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EstimateKeywordSegment'
pub static ESTIMATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dense_rankKeywordSegment'
pub static DENSE_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LnKeywordSegment'
pub static LN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WeekKeywordSegment'
pub static WEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_minutesKeywordSegment'
pub static ADD_MINUTES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Script_languagesKeywordSegment'
pub static SCRIPT_LANGUAGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Approximate_count_distinctKeywordSegment'
pub static APPROXIMATE_COUNT_DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClearKeywordSegment'
pub static CLEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FortranKeywordSegment'
pub static FORTRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GraphKeywordSegment'
pub static GRAPH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KillKeywordSegment'
pub static KILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EveryKeywordSegment'
pub static EVERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MessageKeywordSegment'
pub static MESSAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Log2KeywordSegment'
pub static LOG2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemasKeywordSegment'
pub static SCHEMAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnicodechrKeywordSegment'
pub static UNICODECHR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StddevKeywordSegment'
pub static STDDEV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_dsintervalKeywordSegment'
pub static IS_DSINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistributionKeywordSegment'
pub static DISTRIBUTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumtodsintervalKeywordSegment'
pub static NUMTODSINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_envelopeKeywordSegment'
pub static ST_ENVELOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PowerKeywordSegment'
pub static POWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_syyKeywordSegment'
pub static REGR_SYY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SimpleKeywordSegment'
pub static SIMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemeKeywordSegment'
pub static SCHEME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sys_guidKeywordSegment'
pub static SYS_GUID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablesampleKeywordSegment'
pub static TABLESAMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExcludeKeywordSegment'
pub static EXCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_tigerKeywordSegment'
pub static HASH_TIGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CotKeywordSegment'
pub static COT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_transformKeywordSegment'
pub static ST_TRANSFORM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SignKeywordSegment'
pub static SIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttemptsKeywordSegment'
pub static ATTEMPTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_geometrynKeywordSegment'
pub static ST_GEOMETRYN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PiKeywordSegment'
pub static PI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgxKeywordSegment'
pub static REGR_AVGX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_centroidKeywordSegment'
pub static ST_CENTROID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RandKeywordSegment'
pub static RAND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_numinteriorringsKeywordSegment'
pub static ST_NUMINTERIORRINGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RtrimKeywordSegment'
pub static RTRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Seconds_betweenKeywordSegment'
pub static SECONDS_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HashKeywordSegment'
pub static HASH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Query_cacheKeywordSegment'
pub static QUERY_CACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_dimensionKeywordSegment'
pub static ST_DIMENSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OctetsKeywordSegment'
pub static OCTETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReverseKeywordSegment'
pub static REVERSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_sha256KeywordSegment'
pub static HASH_SHA256_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_lengthKeywordSegment'
pub static ST_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpperKeywordSegment'
pub static UPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ManageKeywordSegment'
pub static MANAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_containsKeywordSegment'
pub static ST_CONTAINS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_countKeywordSegment'
pub static REGR_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FlushKeywordSegment'
pub static FLUSH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_andKeywordSegment'
pub static BIT_AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_sha512KeywordSegment'
pub static HASHTYPE_SHA512_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_monthsKeywordSegment'
pub static ADD_MONTHS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatableKeywordSegment'
pub static REPEATABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_areaKeywordSegment'
pub static ST_AREA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChangeKeywordSegment'
pub static CHANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_unionKeywordSegment'
pub static ST_UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnicodeKeywordSegment'
pub static UNICODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_sha1KeywordSegment'
pub static HASHTYPE_SHA1_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_shaKeywordSegment'
pub static HASH_SHA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KerberosKeywordSegment'
pub static KERBEROS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Add_daysKeywordSegment'
pub static ADD_DAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Octet_lengthKeywordSegment'
pub static OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RankKeywordSegment'
pub static RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxyKeywordSegment'
pub static REGR_SXY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranslateKeywordSegment'
pub static TRANSLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PythonKeywordSegment'
pub static PYTHON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OwnerKeywordSegment'
pub static OWNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocateKeywordSegment'
pub static LOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecureKeywordSegment'
pub static SECURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_ymintervalKeywordSegment'
pub static TO_YMINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExaKeywordSegment'
pub static EXA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SinKeywordSegment'
pub static SIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarianceKeywordSegment'
pub static VARIANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AccessKeywordSegment'
pub static ACCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IprocKeywordSegment'
pub static IPROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LcaseKeywordSegment'
pub static LCASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Utf8KeywordSegment'
pub static UTF8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JdbcKeywordSegment'
pub static JDBC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinKeywordSegment'
pub static MIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OraKeywordSegment'
pub static ORA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScalarKeywordSegment'
pub static SCALAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LanguageKeywordSegment'
pub static LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_crossesKeywordSegment'
pub static ST_CROSSES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnalyzeKeywordSegment'
pub static ANALYZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='To_dsintervalKeywordSegment'
pub static TO_DSINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExcludingKeywordSegment'
pub static EXCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NowKeywordSegment'
pub static NOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptimizerKeywordSegment'
pub static OPTIMIZER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TanKeywordSegment'
pub static TAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumtoymintervalKeywordSegment'
pub static NUMTOYMINTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubstrKeywordSegment'
pub static SUBSTR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_endpointKeywordSegment'
pub static ST_ENDPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConnectKeywordSegment'
pub static CONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtanKeywordSegment'
pub static ATAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MedianKeywordSegment'
pub static MEDIAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MulKeywordSegment'
pub static MUL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeysKeywordSegment'
pub static KEYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TypeofKeywordSegment'
pub static TYPEOF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_r2KeywordSegment'
pub static REGR_R2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_checkKeywordSegment'
pub static BIT_CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_setKeywordSegment'
pub static BIT_SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_rshiftKeywordSegment'
pub static BIT_RSHIFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Min_scaleKeywordSegment'
pub static MIN_SCALE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommentsKeywordSegment'
pub static COMMENTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuditKeywordSegment'
pub static AUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgyKeywordSegment'
pub static REGR_AVGY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowcountKeywordSegment'
pub static ROWCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HasKeywordSegment'
pub static HAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TasksKeywordSegment'
pub static TASKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExperimentalKeywordSegment'
pub static EXPERIMENTAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Is_numberKeywordSegment'
pub static IS_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilesKeywordSegment'
pub static FILES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_yKeywordSegment'
pub static ST_Y_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_tigerKeywordSegment'
pub static HASHTYPE_TIGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommittedKeywordSegment'
pub static COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LinkKeywordSegment'
pub static LINK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WriteKeywordSegment'
pub static WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hash_sha1KeywordSegment'
pub static HASH_SHA1_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenidKeywordSegment'
pub static OPENID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommentKeywordSegment'
pub static COMMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_slopeKeywordSegment'
pub static REGR_SLOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BreadthKeywordSegment'
pub static BREADTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Password_security_policyKeywordSegment'
pub static PASSWORD_SECURITY_POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='St_distanceKeywordSegment'
pub static ST_DISTANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AcosKeywordSegment'
pub static ACOS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hours_betweenKeywordSegment'
pub static HOURS_BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnsiKeywordSegment'
pub static ANSI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrueKeywordSegment'
pub static TRUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DynamicKeywordSegment'
pub static DYNAMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_nameKeywordSegment'
pub static CHARACTER_SET_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReleaseKeywordSegment'
pub static RELEASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckedKeywordSegment'
pub static CHECKED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StructureKeywordSegment'
pub static STRUCTURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RandomKeywordSegment'
pub static RANDOM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InstanceKeywordSegment'
pub static INSTANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NationalKeywordSegment'
pub static NATIONAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumericKeywordSegment'
pub static NUMERIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnKeywordSegment'
pub static RETURN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClobKeywordSegment'
pub static CLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocatorKeywordSegment'
pub static LOCATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_nameKeywordSegment'
pub static COLLATION_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_decimalKeywordSegment'
pub static SQL_DECIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BigintKeywordSegment'
pub static BIGINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NewKeywordSegment'
pub static NEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_schemaKeywordSegment'
pub static CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImpersonateKeywordSegment'
pub static IMPERSONATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinuteKeywordSegment'
pub static MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YesKeywordSegment'
pub static YES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttributeKeywordSegment'
pub static ATTRIBUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SearchKeywordSegment'
pub static SEARCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlvalueKeywordSegment'
pub static DLVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantKeywordSegment'
pub static GRANT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Connect_by_rootKeywordSegment'
pub static CONNECT_BY_ROOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnnestKeywordSegment'
pub static UNNEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChainKeywordSegment'
pub static CHAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SimilarKeywordSegment'
pub static SIMILAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BitKeywordSegment'
pub static BIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntKeywordSegment'
pub static INT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlurlpathKeywordSegment'
pub static DLURLPATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InvokerKeywordSegment'
pub static INVOKER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeadingKeywordSegment'
pub static LEADING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_like_escape_characterKeywordSegment'
pub static DEFAULT_LIKE_ESCAPE_CHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nls_timestamp_formatKeywordSegment'
pub static NLS_TIMESTAMP_FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonthKeywordSegment'
pub static MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimeKeywordSegment'
pub static TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinusKeywordSegment'
pub static MINUS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnabledKeywordSegment'
pub static ENABLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FinalKeywordSegment'
pub static FINAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_timestampKeywordSegment'
pub static SQL_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescriptorKeywordSegment'
pub static DESCRIPTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nvarchar2KeywordSegment'
pub static NVARCHAR2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_preprocessor_scriptKeywordSegment'
pub static SQL_PREPROCESSOR_SCRIPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LogKeywordSegment'
pub static LOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderingKeywordSegment'
pub static ORDERING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OthersKeywordSegment'
pub static OTHERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ListaggKeywordSegment'
pub static LISTAGG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadsKeywordSegment'
pub static READS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ObjectKeywordSegment'
pub static OBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupsKeywordSegment'
pub static GROUPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecondKeywordSegment'
pub static SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TemporaryKeywordSegment'
pub static TEMPORARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatKeywordSegment'
pub static REPEAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LevelKeywordSegment'
pub static LEVEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnyKeywordSegment'
pub static ANY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharKeywordSegment'
pub static CHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreferringKeywordSegment'
pub static PREFERRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FloatKeywordSegment'
pub static FLOAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RelativeKeywordSegment'
pub static RELATIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecurityKeywordSegment'
pub static SECURITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CardinalityKeywordSegment'
pub static CARDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MethodKeywordSegment'
pub static METHOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_specific_nameKeywordSegment'
pub static PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_tinyintKeywordSegment'
pub static SQL_TINYINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DispatchKeywordSegment'
pub static DISPATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantedKeywordSegment'
pub static GRANTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetsKeywordSegment'
pub static SETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoopKeywordSegment'
pub static LOOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatalinkKeywordSegment'
pub static DATALINK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TinyintKeywordSegment'
pub static TINYINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_type_dateKeywordSegment'
pub static SQL_TYPE_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlurlserverKeywordSegment'
pub static DLURLSERVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegrityKeywordSegment'
pub static INTEGRITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrdinalityKeywordSegment'
pub static ORDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExternalKeywordSegment'
pub static EXTERNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreeKeywordSegment'
pub static FREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsageKeywordSegment'
pub static USAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NclobKeywordSegment'
pub static NCLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DerefKeywordSegment'
pub static DEREF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CalledKeywordSegment'
pub static CALLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferrableKeywordSegment'
pub static DEFERRABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_statementKeywordSegment'
pub static CURRENT_STATEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_charKeywordSegment'
pub static SQL_CHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_schemaKeywordSegment'
pub static CURRENT_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverlayKeywordSegment'
pub static OVERLAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstantKeywordSegment'
pub static CONSTANT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StatementKeywordSegment'
pub static STATEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForallKeywordSegment'
pub static FORALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SequenceKeywordSegment'
pub static SEQUENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnderKeywordSegment'
pub static UNDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentityKeywordSegment'
pub static IDENTITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_lengthKeywordSegment'
pub static RETURNED_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuthidKeywordSegment'
pub static AUTHID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SessionKeywordSegment'
pub static SESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlockedKeywordSegment'
pub static BLOCKED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnsKeywordSegment'
pub static RETURNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocaltimeKeywordSegment'
pub static LOCALTIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NaturalKeywordSegment'
pub static NATURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemaKeywordSegment'
pub static SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScopeKeywordSegment'
pub static SCOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrailingKeywordSegment'
pub static TRAILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_roleKeywordSegment'
pub static CURRENT_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResultKeywordSegment'
pub static RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_schemaKeywordSegment'
pub static COLLATION_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HighKeywordSegment'
pub static HIGH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeallocateKeywordSegment'
pub static DEALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProfileKeywordSegment'
pub static PROFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MapKeywordSegment'
pub static MAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuthorizationKeywordSegment'
pub static AUTHORIZATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImmediateKeywordSegment'
pub static IMMEDIATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadKeywordSegment'
pub static READ_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnableKeywordSegment'
pub static ENABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InverseKeywordSegment'
pub static INVERSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StyleKeywordSegment'
pub static STYLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RefreshKeywordSegment'
pub static REFRESH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_realKeywordSegment'
pub static SQL_REAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefinedKeywordSegment'
pub static DEFINED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShortintKeywordSegment'
pub static SHORTINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeaveKeywordSegment'
pub static LEAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_userKeywordSegment'
pub static CURRENT_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Timezone_hourKeywordSegment'
pub static TIMEZONE_HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlurlschemeKeywordSegment'
pub static DLURLSCHEME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GotoKeywordSegment'
pub static GOTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ControlKeywordSegment'
pub static CONTROL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AppendKeywordSegment'
pub static APPEND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UserKeywordSegment'
pub static USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartialKeywordSegment'
pub static PARTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CatalogKeywordSegment'
pub static CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeclareKeywordSegment'
pub static DECLARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnknownKeywordSegment'
pub static UNKNOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TextKeywordSegment'
pub static TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AssertionKeywordSegment'
pub static ASSERTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImplementationKeywordSegment'
pub static IMPLEMENTATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelfKeywordSegment'
pub static SELF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElsifKeywordSegment'
pub static ELSIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndicatorKeywordSegment'
pub static INDICATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpecificKeywordSegment'
pub static SPECIFIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarrayKeywordSegment'
pub static VARRAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModifyKeywordSegment'
pub static MODIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_doubleKeywordSegment'
pub static SQL_DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrimKeywordSegment'
pub static TRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DataKeywordSegment'
pub static DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayKeywordSegment'
pub static DAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecimalKeywordSegment'
pub static DECIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FbvKeywordSegment'
pub static FBV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SessiontimezoneKeywordSegment'
pub static SESSIONTIMEZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConnectionKeywordSegment'
pub static CONNECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LongvarcharKeywordSegment'
pub static LONGVARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PositionKeywordSegment'
pub static POSITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StateKeywordSegment'
pub static STATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithinKeywordSegment'
pub static WITHIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisableKeywordSegment'
pub static DISABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpecifictypeKeywordSegment'
pub static SPECIFICTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CallKeywordSegment'
pub static CALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValueKeywordSegment'
pub static VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntervalKeywordSegment'
pub static INTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_numericKeywordSegment'
pub static SQL_NUMERIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_pathKeywordSegment'
pub static CURRENT_PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_floatKeywordSegment'
pub static SQL_FLOAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SmallintKeywordSegment'
pub static SMALLINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintsKeywordSegment'
pub static CONSTRAINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InstantiableKeywordSegment'
pub static INSTANTIABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SourceKeywordSegment'
pub static SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WheneverKeywordSegment'
pub static WHENEVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseifKeywordSegment'
pub static ELSEIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExtractKeywordSegment'
pub static EXTRACT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConditionKeywordSegment'
pub static CONDITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoKeywordSegment'
pub static DO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubtypeKeywordSegment'
pub static SUBTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GetKeywordSegment'
pub static GET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocaltimestampKeywordSegment'
pub static LOCALTIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlstateKeywordSegment'
pub static SQLSTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DomainKeywordSegment'
pub static DOMAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QualifyKeywordSegment'
pub static QUALIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlexceptionKeywordSegment'
pub static SQLEXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FoundKeywordSegment'
pub static FOUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RealKeywordSegment'
pub static REAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FetchKeywordSegment'
pub static FETCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dynamic_functionKeywordSegment'
pub static DYNAMIC_FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HoldKeywordSegment'
pub static HOLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BoolKeywordSegment'
pub static BOOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpaceKeywordSegment'
pub static SPACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeometryKeywordSegment'
pub static GEOMETRY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RefKeywordSegment'
pub static REF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SystemKeywordSegment'
pub static SYSTEM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ErrorsKeywordSegment'
pub static ERRORS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IterateKeywordSegment'
pub static ITERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Connect_by_isleafKeywordSegment'
pub static CONNECT_BY_ISLEAF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nls_date_languageKeywordSegment'
pub static NLS_DATE_LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_longvarcharKeywordSegment'
pub static SQL_LONGVARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InoutKeywordSegment'
pub static INOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LdapKeywordSegment'
pub static LDAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullifKeywordSegment'
pub static NULLIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_type_timestampKeywordSegment'
pub static SQL_TYPE_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScriptKeywordSegment'
pub static SCRIPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AreKeywordSegment'
pub static ARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NvarcharKeywordSegment'
pub static NVARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecKeywordSegment'
pub static DEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_bitKeywordSegment'
pub static SQL_BIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocalKeywordSegment'
pub static LOCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CycleKeywordSegment'
pub static CYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InputKeywordSegment'
pub static INPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Group_concatKeywordSegment'
pub static GROUP_CONCAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainsKeywordSegment'
pub static CONTAINS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneralKeywordSegment'
pub static GENERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Key_memberKeywordSegment'
pub static KEY_MEMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LateralKeywordSegment'
pub static LATERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DbtimezoneKeywordSegment'
pub static DBTIMEZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForceKeywordSegment'
pub static FORCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrepareKeywordSegment'
pub static PREPARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SeparatorKeywordSegment'
pub static SEPARATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransformsKeywordSegment'
pub static TRANSFORMS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HashtypeKeywordSegment'
pub static HASHTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PathKeywordSegment'
pub static PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ArrayKeywordSegment'
pub static ARRAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StaticKeywordSegment'
pub static STATIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GoKeywordSegment'
pub static GO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YearKeywordSegment'
pub static YEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExportKeywordSegment'
pub static EXPORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnlinkKeywordSegment'
pub static UNLINK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllocateKeywordSegment'
pub static ALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nls_date_formatKeywordSegment'
pub static NLS_DATE_FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_sessionKeywordSegment'
pub static CURRENT_SESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VerifyKeywordSegment'
pub static VERIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConvertKeywordSegment'
pub static CONVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenKeywordSegment'
pub static OPEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CloseKeywordSegment'
pub static CLOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Datetime_interval_precisionKeywordSegment'
pub static DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Constraint_state_defaultKeywordSegment'
pub static CONSTRAINT_STATE_DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrivilegesKeywordSegment'
pub static PRIVILEGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScrollKeywordSegment'
pub static SCROLL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parallel_enableKeywordSegment'
pub static PARALLEL_ENABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regexp_likeKeywordSegment'
pub static REGEXP_LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlacingKeywordSegment'
pub static PLACING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollationKeywordSegment'
pub static COLLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EachKeywordSegment'
pub static EACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_specific_schemaKeywordSegment'
pub static PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NcharKeywordSegment'
pub static NCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dynamic_function_codeKeywordSegment'
pub static DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CoalesceKeywordSegment'
pub static COALESCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ZoneKeywordSegment'
pub static ZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SomeKeywordSegment'
pub static SOME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WorkKeywordSegment'
pub static WORK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModuleKeywordSegment'
pub static MODULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nls_first_day_of_weekKeywordSegment'
pub static NLS_FIRST_DAY_OF_WEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SystimestampKeywordSegment'
pub static SYSTIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EqualsKeywordSegment'
pub static EQUALS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlusKeywordSegment'
pub static PLUS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartKeywordSegment'
pub static START_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchedKeywordSegment'
pub static MATCHED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MergeKeywordSegment'
pub static MERGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollupKeywordSegment'
pub static ROLLUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CorrespondingKeywordSegment'
pub static CORRESPONDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndifKeywordSegment'
pub static ENDIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlobKeywordSegment'
pub static BLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CsKeywordSegment'
pub static CS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hashtype_formatKeywordSegment'
pub static HASHTYPE_FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NextKeywordSegment'
pub static NEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PermissionKeywordSegment'
pub static PERMISSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstructorKeywordSegment'
pub static CONSTRUCTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlurlcompleteKeywordSegment'
pub static DLURLCOMPLETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegerKeywordSegment'
pub static INTEGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HourKeywordSegment'
pub static HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimestampKeywordSegment'
pub static TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FunctionKeywordSegment'
pub static FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharacteristicsKeywordSegment'
pub static CHARACTERISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Connect_by_iscycleKeywordSegment'
pub static CONNECT_BY_ISCYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CursorKeywordSegment'
pub static CURSOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecKeywordSegment'
pub static EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarcharKeywordSegment'
pub static VARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreserveKeywordSegment'
pub static PRESERVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbsoluteKeywordSegment'
pub static ABSOLUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverlapsKeywordSegment'
pub static OVERLAPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SectionKeywordSegment'
pub static SECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CsvKeywordSegment'
pub static CSV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransformKeywordSegment'
pub static TRANSFORM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionsKeywordSegment'
pub static OPTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Scope_userKeywordSegment'
pub static SCOPE_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Session_userKeywordSegment'
pub static SESSION_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EmitsKeywordSegment'
pub static EMITS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharacterKeywordSegment'
pub static CHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ByteKeywordSegment'
pub static BYTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecuteKeywordSegment'
pub static EXECUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_integerKeywordSegment'
pub static SQL_INTEGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsensitiveKeywordSegment'
pub static ASENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_catalogKeywordSegment'
pub static CHARACTER_SET_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencingKeywordSegment'
pub static REFERENCING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoutineKeywordSegment'
pub static ROUTINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RevokeKeywordSegment'
pub static REVOKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_catalogKeywordSegment'
pub static COLLATION_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SensitiveKeywordSegment'
pub static SENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContinueKeywordSegment'
pub static CONTINUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadedKeywordSegment'
pub static CASCADED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LimitKeywordSegment'
pub static LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BooleanKeywordSegment'
pub static BOOLEAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CasespecificKeywordSegment'
pub static CASESPECIFIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Datetime_interval_codeKeywordSegment'
pub static DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowtypeKeywordSegment'
pub static ROWTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nls_numeric_charactersKeywordSegment'
pub static NLS_NUMERIC_CHARACTERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GlobalKeywordSegment'
pub static GLOBAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PriorKeywordSegment'
pub static PRIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhileKeywordSegment'
pub static WHILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IfnullKeywordSegment'
pub static IFNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutputKeywordSegment'
pub static OUTPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DlurlpathonlyKeywordSegment'
pub static DLURLPATHONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CubeKeywordSegment'
pub static CUBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImportKeywordSegment'
pub static IMPORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NologgingKeywordSegment'
pub static NOLOGGING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Key_typeKeywordSegment'
pub static KEY_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UntilKeywordSegment'
pub static UNTIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverridingKeywordSegment'
pub static OVERRIDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DerivedKeywordSegment'
pub static DERIVED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelectiveKeywordSegment'
pub static SELECTIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='End-execKeywordSegment'
pub static END_EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubstringKeywordSegment'
pub static SUBSTRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtKeywordSegment'
pub static AT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_varcharKeywordSegment'
pub static SQL_VARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescribeKeywordSegment'
pub static DESCRIBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcedureKeywordSegment'
pub static PROCEDURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlKeywordSegment'
pub static SQL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LargeKeywordSegment'
pub static LARGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnforceKeywordSegment'
pub static ENFORCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Varchar2KeywordSegment'
pub static VARCHAR2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlwarningKeywordSegment'
pub static SQLWARNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SavepointKeywordSegment'
pub static SAVEPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutKeywordSegment'
pub static OUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModKeywordSegment'
pub static MOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_smallintKeywordSegment'
pub static SQL_SMALLINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsensitiveKeywordSegment'
pub static INSENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefinerKeywordSegment'
pub static DEFINER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParameterKeywordSegment'
pub static PARAMETER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LowKeywordSegment'
pub static LOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumberKeywordSegment'
pub static NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PadKeywordSegment'
pub static PAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeterministicKeywordSegment'
pub static DETERMINISTIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupingKeywordSegment'
pub static GROUPING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_dateKeywordSegment'
pub static SQL_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferredKeywordSegment'
pub static DEFERRED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocycleKeywordSegment'
pub static NOCYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_bigintKeywordSegment'
pub static SQL_BIGINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FalseKeywordSegment'
pub static FALSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FormatKeywordSegment'
pub static FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SysdateKeywordSegment'
pub static SYSDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TreatKeywordSegment'
pub static TREAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OldKeywordSegment'
pub static OLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptionKeywordSegment'
pub static EXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchKeywordSegment'
pub static MATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExitKeywordSegment'
pub static EXIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModifiesKeywordSegment'
pub static MODIFIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnlyKeywordSegment'
pub static ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Timezone_minuteKeywordSegment'
pub static TIMEZONE_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='System_userKeywordSegment'
pub static SYSTEM_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisconnectKeywordSegment'
pub static DISCONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisabledKeywordSegment'
pub static DISABLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecoveryKeywordSegment'
pub static RECOVERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestoreKeywordSegment'
pub static RESTORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NamesKeywordSegment'
pub static NAMES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_specific_catalogKeywordSegment'
pub static PARAMETER_SPECIFIC_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionKeywordSegment'
pub static OPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranslationKeywordSegment'
pub static TRANSLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BothKeywordSegment'
pub static BOTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_octet_lengthKeywordSegment'
pub static RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FsKeywordSegment'
pub static FS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

pub fn get_exasol_segment_grammar(name: &str) -> Option<&'static Grammar> {
    match name {
            "DelimiterGrammar" => Some(&DELIMITER_GRAMMAR),
            "SemicolonSegment" => Some(&SEMICOLON_SEGMENT),
            "ColonSegment" => Some(&COLON_SEGMENT),
            "SliceSegment" => Some(&SLICE_SEGMENT),
            "ColonDelimiterSegment" => Some(&COLON_DELIMITER_SEGMENT),
            "ColonPrefixSegment" => Some(&COLON_PREFIX_SEGMENT),
            "StartBracketSegment" => Some(&START_BRACKET_SEGMENT),
            "EndBracketSegment" => Some(&END_BRACKET_SEGMENT),
            "StartSquareBracketSegment" => Some(&START_SQUARE_BRACKET_SEGMENT),
            "EndSquareBracketSegment" => Some(&END_SQUARE_BRACKET_SEGMENT),
            "StartCurlyBracketSegment" => Some(&START_CURLY_BRACKET_SEGMENT),
            "EndCurlyBracketSegment" => Some(&END_CURLY_BRACKET_SEGMENT),
            "CommaSegment" => Some(&COMMA_SEGMENT),
            "DotSegment" => Some(&DOT_SEGMENT),
            "StarSegment" => Some(&STAR_SEGMENT),
            "TildeSegment" => Some(&TILDE_SEGMENT),
            "ParameterSegment" => Some(&PARAMETER_SEGMENT),
            "CastOperatorSegment" => Some(&CAST_OPERATOR_SEGMENT),
            "PlusSegment" => Some(&PLUS_SEGMENT),
            "MinusSegment" => Some(&MINUS_SEGMENT),
            "PositiveSegment" => Some(&POSITIVE_SEGMENT),
            "NegativeSegment" => Some(&NEGATIVE_SEGMENT),
            "DivideSegment" => Some(&DIVIDE_SEGMENT),
            "MultiplySegment" => Some(&MULTIPLY_SEGMENT),
            "ModuloSegment" => Some(&MODULO_SEGMENT),
            "SlashSegment" => Some(&SLASH_SEGMENT),
            "AmpersandSegment" => Some(&AMPERSAND_SEGMENT),
            "PipeSegment" => Some(&PIPE_SEGMENT),
            "BitwiseXorSegment" => Some(&BITWISE_XOR_SEGMENT),
            "GlobOperatorSegment" => Some(&GLOB_OPERATOR_SEGMENT),
            "LikeOperatorSegment" => Some(&LIKE_OPERATOR_SEGMENT),
            "RawNotSegment" => Some(&RAW_NOT_SEGMENT),
            "RawEqualsSegment" => Some(&RAW_EQUALS_SEGMENT),
            "RawGreaterThanSegment" => Some(&RAW_GREATER_THAN_SEGMENT),
            "RawLessThanSegment" => Some(&RAW_LESS_THAN_SEGMENT),
            "BareFunctionSegment" => Some(&BARE_FUNCTION_SEGMENT),
            "NakedIdentifierSegment" => Some(&NAKED_IDENTIFIER_SEGMENT),
            "ParameterNameSegment" => Some(&PARAMETER_NAME_SEGMENT),
            "FunctionNameIdentifierSegment" => Some(&FUNCTION_NAME_IDENTIFIER_SEGMENT),
            "DatatypeIdentifierSegment" => Some(&DATATYPE_IDENTIFIER_SEGMENT),
            "DatetimeUnitSegment" => Some(&DATETIME_UNIT_SEGMENT),
            "DatePartFunctionName" => Some(&DATE_PART_FUNCTION_NAME),
            "QuotedIdentifierSegment" => Some(&QUOTED_IDENTIFIER_SEGMENT),
            "QuotedLiteralSegment" => Some(&QUOTED_LITERAL_SEGMENT),
            "SingleQuotedIdentifierSegment" => Some(&SINGLE_QUOTED_IDENTIFIER_SEGMENT),
            "NumericLiteralSegment" => Some(&NUMERIC_LITERAL_SEGMENT),
            "NullLiteralSegment" => Some(&NULL_LITERAL_SEGMENT),
            "NanLiteralSegment" => Some(&NAN_LITERAL_SEGMENT),
            "UnknownLiteralSegment" => Some(&UNKNOWN_LITERAL_SEGMENT),
            "NormalizedGrammar" => Some(&NORMALIZED_GRAMMAR),
            "TrueSegment" => Some(&TRUE_SEGMENT),
            "FalseSegment" => Some(&FALSE_SEGMENT),
            "SingleIdentifierGrammar" => Some(&SINGLE_IDENTIFIER_GRAMMAR),
            "BooleanLiteralGrammar" => Some(&BOOLEAN_LITERAL_GRAMMAR),
            "ArithmeticBinaryOperatorGrammar" => Some(&ARITHMETIC_BINARY_OPERATOR_GRAMMAR),
            "SignedSegmentGrammar" => Some(&SIGNED_SEGMENT_GRAMMAR),
            "StringBinaryOperatorGrammar" => Some(&STRING_BINARY_OPERATOR_GRAMMAR),
            "BooleanBinaryOperatorGrammar" => Some(&BOOLEAN_BINARY_OPERATOR_GRAMMAR),
            "IsDistinctFromGrammar" => Some(&IS_DISTINCT_FROM_GRAMMAR),
            "ComparisonOperatorGrammar" => Some(&COMPARISON_OPERATOR_GRAMMAR),
            "DateTimeLiteralGrammar" => Some(&DATE_TIME_LITERAL_GRAMMAR),
            "MergeIntoLiteralGrammar" => Some(&MERGE_INTO_LITERAL_GRAMMAR),
            "LiteralGrammar" => Some(&LITERAL_GRAMMAR),
            "AndOperatorGrammar" => Some(&AND_OPERATOR_GRAMMAR),
            "OrOperatorGrammar" => Some(&OR_OPERATOR_GRAMMAR),
            "NotOperatorGrammar" => Some(&NOT_OPERATOR_GRAMMAR),
            "PreTableFunctionKeywordsGrammar" => Some(&PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR),
            "BinaryOperatorGrammar" => Some(&BINARY_OPERATOR_GRAMMAR),
            "BracketedColumnReferenceListGrammar" => Some(&BRACKETED_COLUMN_REFERENCE_LIST_GRAMMAR),
            "OrReplaceGrammar" => Some(&OR_REPLACE_GRAMMAR),
            "TemporaryTransientGrammar" => Some(&TEMPORARY_TRANSIENT_GRAMMAR),
            "TemporaryGrammar" => Some(&TEMPORARY_GRAMMAR),
            "IfExistsGrammar" => Some(&IF_EXISTS_GRAMMAR),
            "IfNotExistsGrammar" => Some(&IF_NOT_EXISTS_GRAMMAR),
            "LikeGrammar" => Some(&LIKE_GRAMMAR),
            "LikeExpressionGrammar" => Some(&LIKE_EXPRESSION_GRAMMAR),
            "PatternMatchingGrammar" => Some(&PATTERN_MATCHING_GRAMMAR),
            "UnionGrammar" => Some(&UNION_GRAMMAR),
            "IsClauseGrammar" => Some(&IS_CLAUSE_GRAMMAR),
            "InOperatorGrammar" => Some(&IN_OPERATOR_GRAMMAR),
            "SelectClauseTerminatorGrammar" => Some(&SELECT_CLAUSE_TERMINATOR_GRAMMAR),
            "IsNullGrammar" => Some(&IS_NULL_GRAMMAR),
            "NotNullGrammar" => Some(&NOT_NULL_GRAMMAR),
            "CollateGrammar" => Some(&COLLATE_GRAMMAR),
            "FromClauseTerminatorGrammar" => Some(&FROM_CLAUSE_TERMINATOR_GRAMMAR),
            "WhereClauseTerminatorGrammar" => Some(&WHERE_CLAUSE_TERMINATOR_GRAMMAR),
            "GroupByClauseTerminatorGrammar" => Some(&GROUP_BY_CLAUSE_TERMINATOR_GRAMMAR),
            "HavingClauseTerminatorGrammar" => Some(&HAVING_CLAUSE_TERMINATOR_GRAMMAR),
            "OrderByClauseTerminators" => Some(&ORDER_BY_CLAUSE_TERMINATORS),
            "PrimaryKeyGrammar" => Some(&PRIMARY_KEY_GRAMMAR),
            "ForeignKeyGrammar" => Some(&FOREIGN_KEY_GRAMMAR),
            "UniqueKeyGrammar" => Some(&UNIQUE_KEY_GRAMMAR),
            "NotEnforcedGrammar" => Some(&NOT_ENFORCED_GRAMMAR),
            "FunctionParameterGrammar" => Some(&FUNCTION_PARAMETER_GRAMMAR),
            "AutoIncrementGrammar" => Some(&AUTO_INCREMENT_GRAMMAR),
            "BaseExpressionElementGrammar" => Some(&BASE_EXPRESSION_ELEMENT_GRAMMAR),
            "FilterClauseGrammar" => Some(&FILTER_CLAUSE_GRAMMAR),
            "IgnoreRespectNullsGrammar" => Some(&IGNORE_RESPECT_NULLS_GRAMMAR),
            "FrameClauseUnitGrammar" => Some(&FRAME_CLAUSE_UNIT_GRAMMAR),
            "ConditionalCrossJoinKeywordsGrammar" => Some(&CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR),
            "JoinTypeKeywordsGrammar" => Some(&JOIN_TYPE_KEYWORDS_GRAMMAR),
            "NonStandardJoinTypeKeywordsGrammar" => Some(&NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR),
            "ConditionalJoinKeywordsGrammar" => Some(&CONDITIONAL_JOIN_KEYWORDS_GRAMMAR),
            "JoinUsingConditionGrammar" => Some(&JOIN_USING_CONDITION_GRAMMAR),
            "JoinKeywordsGrammar" => Some(&JOIN_KEYWORDS_GRAMMAR),
            "NaturalJoinKeywordsGrammar" => Some(&NATURAL_JOIN_KEYWORDS_GRAMMAR),
            "UnconditionalCrossJoinKeywordsGrammar" => Some(&UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR),
            "HorizontalJoinKeywordsGrammar" => Some(&HORIZONTAL_JOIN_KEYWORDS_GRAMMAR),
            "UnconditionalJoinKeywordsGrammar" => Some(&UNCONDITIONAL_JOIN_KEYWORDS_GRAMMAR),
            "ExtendedNaturalJoinKeywordsGrammar" => Some(&EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR),
            "NestedJoinGrammar" => Some(&NESTED_JOIN_GRAMMAR),
            "ReferentialActionGrammar" => Some(&REFERENTIAL_ACTION_GRAMMAR),
            "DropBehaviorGrammar" => Some(&DROP_BEHAVIOR_GRAMMAR),
            "ColumnConstraintDefaultGrammar" => Some(&COLUMN_CONSTRAINT_DEFAULT_GRAMMAR),
            "ReferenceMatchGrammar" => Some(&REFERENCE_MATCH_GRAMMAR),
            "ReferenceDefinitionGrammar" => Some(&REFERENCE_DEFINITION_GRAMMAR),
            "TrimParametersGrammar" => Some(&TRIM_PARAMETERS_GRAMMAR),
            "DefaultValuesGrammar" => Some(&DEFAULT_VALUES_GRAMMAR),
            "ObjectReferenceDelimiterGrammar" => Some(&OBJECT_REFERENCE_DELIMITER_GRAMMAR),
            "ObjectReferenceTerminatorGrammar" => Some(&OBJECT_REFERENCE_TERMINATOR_GRAMMAR),
            "AlterTableOptionsGrammar" => Some(&ALTER_TABLE_OPTIONS_GRAMMAR),
            "AlterTableDropColumnGrammar" => Some(&ALTER_TABLE_DROP_COLUMN_GRAMMAR),
            "OrderNoOrderGrammar" => Some(&ORDER_NO_ORDER_GRAMMAR),
            "ColumnsExpressionNameGrammar" => Some(&COLUMNS_EXPRESSION_NAME_GRAMMAR),
            "ColumnsExpressionGrammar" => Some(&COLUMNS_EXPRESSION_GRAMMAR),
            "ListComprehensionGrammar" => Some(&LIST_COMPREHENSION_GRAMMAR),
            "TimeWithTZGrammar" => Some(&TIME_WITH_T_Z_GRAMMAR),
            "SequenceMinValueGrammar" => Some(&SEQUENCE_MIN_VALUE_GRAMMAR),
            "SequenceMaxValueGrammar" => Some(&SEQUENCE_MAX_VALUE_GRAMMAR),
            "ColumnGeneratedGrammar" => Some(&COLUMN_GENERATED_GRAMMAR),
            "CharCharacterSetGrammar" => Some(&CHAR_CHARACTER_SET_GRAMMAR),
            "AliasedTableReferenceGrammar" => Some(&ALIASED_TABLE_REFERENCE_GRAMMAR),
            "FunctionContentsExpressionGrammar" => Some(&FUNCTION_CONTENTS_EXPRESSION_GRAMMAR),
            "FunctionContentsGrammar" => Some(&FUNCTION_CONTENTS_GRAMMAR),
            "PostFunctionGrammar" => Some(&POST_FUNCTION_GRAMMAR),
            "PostTableExpressionGrammar" => Some(&POST_TABLE_EXPRESSION_GRAMMAR),
            "JoinLikeClauseGrammar" => Some(&JOIN_LIKE_CLAUSE_GRAMMAR),
            "Expression_A_Unary_Operator_Grammar" => Some(&EXPRESSION_A_UNARY_OPERATOR_GRAMMAR),
            "Tail_Recurse_Expression_A_Grammar" => Some(&TAIL_RECURSE_EXPRESSION_A_GRAMMAR),
            "Expression_A_Grammar" => Some(&EXPRESSION_A_GRAMMAR),
            "Expression_B_Unary_Operator_Grammar" => Some(&EXPRESSION_B_UNARY_OPERATOR_GRAMMAR),
            "Tail_Recurse_Expression_B_Grammar" => Some(&TAIL_RECURSE_EXPRESSION_B_GRAMMAR),
            "Expression_B_Grammar" => Some(&EXPRESSION_B_GRAMMAR),
            "Expression_C_Grammar" => Some(&EXPRESSION_C_GRAMMAR),
            "Expression_D_Potential_Select_Statement_Without_Brackets" => Some(&EXPRESSION_D_POTENTIAL_SELECT_STATEMENT_WITHOUT_BRACKETS),
            "Expression_D_Grammar" => Some(&EXPRESSION_D_GRAMMAR),
            "AccessorGrammar" => Some(&ACCESSOR_GRAMMAR),
            "SelectableGrammar" => Some(&SELECTABLE_GRAMMAR),
            "NonWithSelectableGrammar" => Some(&NON_WITH_SELECTABLE_GRAMMAR),
            "NonWithNonSelectableGrammar" => Some(&NON_WITH_NON_SELECTABLE_GRAMMAR),
            "NonSetSelectableGrammar" => Some(&NON_SET_SELECTABLE_GRAMMAR),
            "BracketedSetExpressionGrammar" => Some(&BRACKETED_SET_EXPRESSION_GRAMMAR),
            "AccessStatementSegment" => Some(&ACCESS_STATEMENT_SEGMENT),
            "AggregateOrderByClause" => Some(&AGGREGATE_ORDER_BY_CLAUSE),
            "AliasExpressionSegment" => Some(&ALIAS_EXPRESSION_SEGMENT),
            "AlterSequenceOptionsSegment" => Some(&ALTER_SEQUENCE_OPTIONS_SEGMENT),
            "AlterSequenceStatementSegment" => Some(&ALTER_SEQUENCE_STATEMENT_SEGMENT),
            "AlterTableStatementSegment" => Some(&ALTER_TABLE_STATEMENT_SEGMENT),
            "ArrayAccessorSegment" => Some(&ARRAY_ACCESSOR_SEGMENT),
            "ArrayExpressionSegment" => Some(&ARRAY_EXPRESSION_SEGMENT),
            "ArrayLiteralSegment" => Some(&ARRAY_LITERAL_SEGMENT),
            "ArrayTypeSegment" => Some(&ARRAY_TYPE_SEGMENT),
            "AsAliasOperatorSegment" => Some(&AS_ALIAS_OPERATOR_SEGMENT),
            "BaseFileSegment" => Some(&BASE_FILE_SEGMENT),
            "BaseSegment" => Some(&BASE_SEGMENT),
            "BinaryOperatorSegment" => Some(&BINARY_OPERATOR_SEGMENT),
            "BitwiseAndSegment" => Some(&BITWISE_AND_SEGMENT),
            "BitwiseLShiftSegment" => Some(&BITWISE_L_SHIFT_SEGMENT),
            "BitwiseOrSegment" => Some(&BITWISE_OR_SEGMENT),
            "BitwiseRShiftSegment" => Some(&BITWISE_R_SHIFT_SEGMENT),
            "BracketedArguments" => Some(&BRACKETED_ARGUMENTS),
            "BracketedSegment" => Some(&BRACKETED_SEGMENT),
            "CTEColumnList" => Some(&C_T_E_COLUMN_LIST),
            "CTEDefinitionSegment" => Some(&C_T_E_DEFINITION_SEGMENT),
            "CaseExpressionSegment" => Some(&CASE_EXPRESSION_SEGMENT),
            "CodeSegment" => Some(&CODE_SEGMENT),
            "CollationReferenceSegment" => Some(&COLLATION_REFERENCE_SEGMENT),
            "ColumnConstraintSegment" => Some(&COLUMN_CONSTRAINT_SEGMENT),
            "ColumnDefinitionSegment" => Some(&COLUMN_DEFINITION_SEGMENT),
            "ColumnReferenceSegment" => Some(&COLUMN_REFERENCE_SEGMENT),
            "ColumnsExpressionFunctionContentsSegment" => Some(&COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT),
            "ColumnsExpressionFunctionNameSegment" => Some(&COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT),
            "CommentClauseSegment" => Some(&COMMENT_CLAUSE_SEGMENT),
            "CommentSegment" => Some(&COMMENT_SEGMENT),
            "ComparisonOperatorSegment" => Some(&COMPARISON_OPERATOR_SEGMENT),
            "CompositeBinaryOperatorSegment" => Some(&COMPOSITE_BINARY_OPERATOR_SEGMENT),
            "CompositeComparisonOperatorSegment" => Some(&COMPOSITE_COMPARISON_OPERATOR_SEGMENT),
            "ConcatSegment" => Some(&CONCAT_SEGMENT),
            "CreateCastStatementSegment" => Some(&CREATE_CAST_STATEMENT_SEGMENT),
            "CreateDatabaseStatementSegment" => Some(&CREATE_DATABASE_STATEMENT_SEGMENT),
            "CreateFunctionStatementSegment" => Some(&CREATE_FUNCTION_STATEMENT_SEGMENT),
            "CreateIndexStatementSegment" => Some(&CREATE_INDEX_STATEMENT_SEGMENT),
            "CreateModelStatementSegment" => Some(&CREATE_MODEL_STATEMENT_SEGMENT),
            "CreateRoleStatementSegment" => Some(&CREATE_ROLE_STATEMENT_SEGMENT),
            "CreateSchemaStatementSegment" => Some(&CREATE_SCHEMA_STATEMENT_SEGMENT),
            "CreateSequenceOptionsSegment" => Some(&CREATE_SEQUENCE_OPTIONS_SEGMENT),
            "CreateSequenceStatementSegment" => Some(&CREATE_SEQUENCE_STATEMENT_SEGMENT),
            "CreateTableStatementSegment" => Some(&CREATE_TABLE_STATEMENT_SEGMENT),
            "CreateTriggerStatementSegment" => Some(&CREATE_TRIGGER_STATEMENT_SEGMENT),
            "CreateUserStatementSegment" => Some(&CREATE_USER_STATEMENT_SEGMENT),
            "CreateViewStatementSegment" => Some(&CREATE_VIEW_STATEMENT_SEGMENT),
            "CubeFunctionNameSegment" => Some(&CUBE_FUNCTION_NAME_SEGMENT),
            "CubeRollupClauseSegment" => Some(&CUBE_ROLLUP_CLAUSE_SEGMENT),
            "DatabaseReferenceSegment" => Some(&DATABASE_REFERENCE_SEGMENT),
            "DatatypeSegment" => Some(&DATATYPE_SEGMENT),
            "DatePartFunctionNameSegment" => Some(&DATE_PART_FUNCTION_NAME_SEGMENT),
            "DateTimeFunctionContentsSegment" => Some(&DATE_TIME_FUNCTION_CONTENTS_SEGMENT),
            "Dedent" => Some(&DEDENT),
            "DeleteStatementSegment" => Some(&DELETE_STATEMENT_SEGMENT),
            "DescribeStatementSegment" => Some(&DESCRIBE_STATEMENT_SEGMENT),
            "DropCastStatementSegment" => Some(&DROP_CAST_STATEMENT_SEGMENT),
            "DropDatabaseStatementSegment" => Some(&DROP_DATABASE_STATEMENT_SEGMENT),
            "DropFunctionStatementSegment" => Some(&DROP_FUNCTION_STATEMENT_SEGMENT),
            "DropIndexStatementSegment" => Some(&DROP_INDEX_STATEMENT_SEGMENT),
            "DropModelStatementSegment" => Some(&DROP_MODEL_STATEMENT_SEGMENT),
            "DropRoleStatementSegment" => Some(&DROP_ROLE_STATEMENT_SEGMENT),
            "DropSchemaStatementSegment" => Some(&DROP_SCHEMA_STATEMENT_SEGMENT),
            "DropSequenceStatementSegment" => Some(&DROP_SEQUENCE_STATEMENT_SEGMENT),
            "DropTableStatementSegment" => Some(&DROP_TABLE_STATEMENT_SEGMENT),
            "DropTriggerStatementSegment" => Some(&DROP_TRIGGER_STATEMENT_SEGMENT),
            "DropTypeStatementSegment" => Some(&DROP_TYPE_STATEMENT_SEGMENT),
            "DropUserStatementSegment" => Some(&DROP_USER_STATEMENT_SEGMENT),
            "DropViewStatementSegment" => Some(&DROP_VIEW_STATEMENT_SEGMENT),
            "ElseClauseSegment" => Some(&ELSE_CLAUSE_SEGMENT),
            "EmptyStructLiteralBracketsSegment" => Some(&EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT),
            "EmptyStructLiteralSegment" => Some(&EMPTY_STRUCT_LITERAL_SEGMENT),
            "EqualsSegment" => Some(&EQUALS_SEGMENT),
            "ExplainStatementSegment" => Some(&EXPLAIN_STATEMENT_SEGMENT),
            "ExpressionSegment" => Some(&EXPRESSION_SEGMENT),
            "ExtensionReferenceSegment" => Some(&EXTENSION_REFERENCE_SEGMENT),
            "FetchClauseSegment" => Some(&FETCH_CLAUSE_SEGMENT),
            "FileSegment" => Some(&FILE_SEGMENT),
            "FrameClauseSegment" => Some(&FRAME_CLAUSE_SEGMENT),
            "FromClauseSegment" => Some(&FROM_CLAUSE_SEGMENT),
            "FromExpressionElementSegment" => Some(&FROM_EXPRESSION_ELEMENT_SEGMENT),
            "FromExpressionSegment" => Some(&FROM_EXPRESSION_SEGMENT),
            "FunctionContentsSegment" => Some(&FUNCTION_CONTENTS_SEGMENT),
            "FunctionDefinitionGrammar" => Some(&FUNCTION_DEFINITION_GRAMMAR),
            "FunctionNameSegment" => Some(&FUNCTION_NAME_SEGMENT),
            "FunctionParameterListGrammar" => Some(&FUNCTION_PARAMETER_LIST_GRAMMAR),
            "FunctionSegment" => Some(&FUNCTION_SEGMENT),
            "GreaterThanOrEqualToSegment" => Some(&GREATER_THAN_OR_EQUAL_TO_SEGMENT),
            "GreaterThanSegment" => Some(&GREATER_THAN_SEGMENT),
            "GroupByClauseSegment" => Some(&GROUP_BY_CLAUSE_SEGMENT),
            "GroupingExpressionList" => Some(&GROUPING_EXPRESSION_LIST),
            "GroupingSetsClauseSegment" => Some(&GROUPING_SETS_CLAUSE_SEGMENT),
            "HavingClauseSegment" => Some(&HAVING_CLAUSE_SEGMENT),
            "IdentifierSegment" => Some(&IDENTIFIER_SEGMENT),
            "ImplicitIndent" => Some(&IMPLICIT_INDENT),
            "Indent" => Some(&INDENT),
            "IndexColumnDefinitionSegment" => Some(&INDEX_COLUMN_DEFINITION_SEGMENT),
            "IndexReferenceSegment" => Some(&INDEX_REFERENCE_SEGMENT),
            "InsertStatementSegment" => Some(&INSERT_STATEMENT_SEGMENT),
            "IntervalExpressionSegment" => Some(&INTERVAL_EXPRESSION_SEGMENT),
            "JoinClauseSegment" => Some(&JOIN_CLAUSE_SEGMENT),
            "JoinOnConditionSegment" => Some(&JOIN_ON_CONDITION_SEGMENT),
            "KeywordSegment" => Some(&KEYWORD_SEGMENT),
            "LessThanOrEqualToSegment" => Some(&LESS_THAN_OR_EQUAL_TO_SEGMENT),
            "LessThanSegment" => Some(&LESS_THAN_SEGMENT),
            "LimitClauseSegment" => Some(&LIMIT_CLAUSE_SEGMENT),
            "LiteralKeywordSegment" => Some(&LITERAL_KEYWORD_SEGMENT),
            "LiteralSegment" => Some(&LITERAL_SEGMENT),
            "LocalAliasSegment" => Some(&LOCAL_ALIAS_SEGMENT),
            "MLTableExpressionSegment" => Some(&M_L_TABLE_EXPRESSION_SEGMENT),
            "MapTypeSegment" => Some(&MAP_TYPE_SEGMENT),
            "MatchConditionSegment" => Some(&MATCH_CONDITION_SEGMENT),
            "MergeDeleteClauseSegment" => Some(&MERGE_DELETE_CLAUSE_SEGMENT),
            "MergeInsertClauseSegment" => Some(&MERGE_INSERT_CLAUSE_SEGMENT),
            "MergeMatchSegment" => Some(&MERGE_MATCH_SEGMENT),
            "MergeMatchedClauseSegment" => Some(&MERGE_MATCHED_CLAUSE_SEGMENT),
            "MergeNotMatchedClauseSegment" => Some(&MERGE_NOT_MATCHED_CLAUSE_SEGMENT),
            "MergeStatementSegment" => Some(&MERGE_STATEMENT_SEGMENT),
            "MergeUpdateClauseSegment" => Some(&MERGE_UPDATE_CLAUSE_SEGMENT),
            "NamedWindowExpressionSegment" => Some(&NAMED_WINDOW_EXPRESSION_SEGMENT),
            "NamedWindowSegment" => Some(&NAMED_WINDOW_SEGMENT),
            "NewlineSegment" => Some(&NEWLINE_SEGMENT),
            "NotEqualToSegment" => Some(&NOT_EQUAL_TO_SEGMENT),
            "ObjectLiteralElementSegment" => Some(&OBJECT_LITERAL_ELEMENT_SEGMENT),
            "ObjectLiteralSegment" => Some(&OBJECT_LITERAL_SEGMENT),
            "ObjectReferenceSegment" => Some(&OBJECT_REFERENCE_SEGMENT),
            "OffsetClauseSegment" => Some(&OFFSET_CLAUSE_SEGMENT),
            "OrderByClauseSegment" => Some(&ORDER_BY_CLAUSE_SEGMENT),
            "OverClauseSegment" => Some(&OVER_CLAUSE_SEGMENT),
            "OverlapsClauseSegment" => Some(&OVERLAPS_CLAUSE_SEGMENT),
            "PartitionClauseSegment" => Some(&PARTITION_CLAUSE_SEGMENT),
            "PathSegment" => Some(&PATH_SEGMENT),
            "QualifiedNumericLiteralSegment" => Some(&QUALIFIED_NUMERIC_LITERAL_SEGMENT),
            "RawSegment" => Some(&RAW_SEGMENT),
            "RoleReferenceSegment" => Some(&ROLE_REFERENCE_SEGMENT),
            "RollupFunctionNameSegment" => Some(&ROLLUP_FUNCTION_NAME_SEGMENT),
            "SamplingExpressionSegment" => Some(&SAMPLING_EXPRESSION_SEGMENT),
            "SchemaReferenceSegment" => Some(&SCHEMA_REFERENCE_SEGMENT),
            "SelectClauseElementSegment" => Some(&SELECT_CLAUSE_ELEMENT_SEGMENT),
            "SelectClauseModifierSegment" => Some(&SELECT_CLAUSE_MODIFIER_SEGMENT),
            "SelectClauseSegment" => Some(&SELECT_CLAUSE_SEGMENT),
            "SelectStatementSegment" => Some(&SELECT_STATEMENT_SEGMENT),
            "SequenceReferenceSegment" => Some(&SEQUENCE_REFERENCE_SEGMENT),
            "SetClauseListSegment" => Some(&SET_CLAUSE_LIST_SEGMENT),
            "SetClauseSegment" => Some(&SET_CLAUSE_SEGMENT),
            "SetExpressionSegment" => Some(&SET_EXPRESSION_SEGMENT),
            "SetOperatorSegment" => Some(&SET_OPERATOR_SEGMENT),
            "SetSchemaStatementSegment" => Some(&SET_SCHEMA_STATEMENT_SEGMENT),
            "ShorthandCastSegment" => Some(&SHORTHAND_CAST_SEGMENT),
            "SingleIdentifierListSegment" => Some(&SINGLE_IDENTIFIER_LIST_SEGMENT),
            "SizedArrayTypeSegment" => Some(&SIZED_ARRAY_TYPE_SEGMENT),
            "StatementSegment" => Some(&STATEMENT_SEGMENT),
            "StructLiteralSegment" => Some(&STRUCT_LITERAL_SEGMENT),
            "StructTypeSegment" => Some(&STRUCT_TYPE_SEGMENT),
            "SymbolSegment" => Some(&SYMBOL_SEGMENT),
            "TableConstraintSegment" => Some(&TABLE_CONSTRAINT_SEGMENT),
            "TableEndClauseSegment" => Some(&TABLE_END_CLAUSE_SEGMENT),
            "TableExpressionSegment" => Some(&TABLE_EXPRESSION_SEGMENT),
            "TableReferenceSegment" => Some(&TABLE_REFERENCE_SEGMENT),
            "TablespaceReferenceSegment" => Some(&TABLESPACE_REFERENCE_SEGMENT),
            "TagReferenceSegment" => Some(&TAG_REFERENCE_SEGMENT),
            "TemporalQuerySegment" => Some(&TEMPORAL_QUERY_SEGMENT),
            "TimeZoneGrammar" => Some(&TIME_ZONE_GRAMMAR),
            "TransactionStatementSegment" => Some(&TRANSACTION_STATEMENT_SEGMENT),
            "TriggerReferenceSegment" => Some(&TRIGGER_REFERENCE_SEGMENT),
            "TruncateStatementSegment" => Some(&TRUNCATE_STATEMENT_SEGMENT),
            "TupleSegment" => Some(&TUPLE_SEGMENT),
            "TypedArrayLiteralSegment" => Some(&TYPED_ARRAY_LITERAL_SEGMENT),
            "TypedStructLiteralSegment" => Some(&TYPED_STRUCT_LITERAL_SEGMENT),
            "UnorderedSelectStatementSegment" => Some(&UNORDERED_SELECT_STATEMENT_SEGMENT),
            "UnorderedSetExpressionSegment" => Some(&UNORDERED_SET_EXPRESSION_SEGMENT),
            "UpdateStatementSegment" => Some(&UPDATE_STATEMENT_SEGMENT),
            "UseStatementSegment" => Some(&USE_STATEMENT_SEGMENT),
            "ValuesClauseSegment" => Some(&VALUES_CLAUSE_SEGMENT),
            "WhenClauseSegment" => Some(&WHEN_CLAUSE_SEGMENT),
            "WhereClauseSegment" => Some(&WHERE_CLAUSE_SEGMENT),
            "WhitespaceSegment" => Some(&WHITESPACE_SEGMENT),
            "WildcardExpressionSegment" => Some(&WILDCARD_EXPRESSION_SEGMENT),
            "WildcardIdentifierSegment" => Some(&WILDCARD_IDENTIFIER_SEGMENT),
            "WindowSpecificationSegment" => Some(&WINDOW_SPECIFICATION_SEGMENT),
            "WithCompoundNonSelectStatementSegment" => Some(&WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT),
            "WithCompoundStatementSegment" => Some(&WITH_COMPOUND_STATEMENT_SEGMENT),
            "WithDataClauseSegment" => Some(&WITH_DATA_CLAUSE_SEGMENT),
            "WithFillSegment" => Some(&WITH_FILL_SEGMENT),
            "WithNoSchemaBindingClauseSegment" => Some(&WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT),
            "WordSegment" => Some(&WORD_SEGMENT),
            "PasswordLiteralSegment" => Some(&PASSWORD_LITERAL_SEGMENT),
            "UDFParameterDotSyntaxSegment" => Some(&U_D_F_PARAMETER_DOT_SYNTAX_SEGMENT),
            "RangeOperator" => Some(&RANGE_OPERATOR),
            "UnknownSegment" => Some(&UNKNOWN_SEGMENT),
            "ForeignKeyReferencesClauseGrammar" => Some(&FOREIGN_KEY_REFERENCES_CLAUSE_GRAMMAR),
            "ColumnReferenceListGrammar" => Some(&COLUMN_REFERENCE_LIST_GRAMMAR),
            "TableDistributeByGrammar" => Some(&TABLE_DISTRIBUTE_BY_GRAMMAR),
            "TablePartitionByGrammar" => Some(&TABLE_PARTITION_BY_GRAMMAR),
            "TableConstraintEnableDisableGrammar" => Some(&TABLE_CONSTRAINT_ENABLE_DISABLE_GRAMMAR),
            "EscapedIdentifierSegment" => Some(&ESCAPED_IDENTIFIER_SEGMENT),
            "SessionParameterSegment" => Some(&SESSION_PARAMETER_SEGMENT),
            "SystemParameterSegment" => Some(&SYSTEM_PARAMETER_SEGMENT),
            "UDFParameterGrammar" => Some(&U_D_F_PARAMETER_GRAMMAR),
            "FunctionScriptTerminatorSegment" => Some(&FUNCTION_SCRIPT_TERMINATOR_SEGMENT),
            "WalrusOperatorSegment" => Some(&WALRUS_OPERATOR_SEGMENT),
            "VariableNameSegment" => Some(&VARIABLE_NAME_SEGMENT),
            "AlterConnectionSegment" => Some(&ALTER_CONNECTION_SEGMENT),
            "AlterConsumerGroupSegment" => Some(&ALTER_CONSUMER_GROUP_SEGMENT),
            "AlterRoleStatementSegment" => Some(&ALTER_ROLE_STATEMENT_SEGMENT),
            "AlterSchemaStatementSegment" => Some(&ALTER_SCHEMA_STATEMENT_SEGMENT),
            "AlterSessionSegment" => Some(&ALTER_SESSION_SEGMENT),
            "AlterSystemSegment" => Some(&ALTER_SYSTEM_SEGMENT),
            "AlterTableAddColumnSegment" => Some(&ALTER_TABLE_ADD_COLUMN_SEGMENT),
            "AlterTableAlterColumnSegment" => Some(&ALTER_TABLE_ALTER_COLUMN_SEGMENT),
            "AlterTableColumnSegment" => Some(&ALTER_TABLE_COLUMN_SEGMENT),
            "AlterTableConstraintSegment" => Some(&ALTER_TABLE_CONSTRAINT_SEGMENT),
            "AlterTableDistributePartitionSegment" => Some(&ALTER_TABLE_DISTRIBUTE_PARTITION_SEGMENT),
            "AlterTableDropColumnSegment" => Some(&ALTER_TABLE_DROP_COLUMN_SEGMENT),
            "AlterTableModifyColumnSegment" => Some(&ALTER_TABLE_MODIFY_COLUMN_SEGMENT),
            "AlterTableRenameColumnSegment" => Some(&ALTER_TABLE_RENAME_COLUMN_SEGMENT),
            "AlterUserStatementSegment" => Some(&ALTER_USER_STATEMENT_SEGMENT),
            "AlterVirtualSchemaStatementSegment" => Some(&ALTER_VIRTUAL_SCHEMA_STATEMENT_SEGMENT),
            "CSVColumnDefinitionSegment" => Some(&C_S_V_COLUMN_DEFINITION_SEGMENT),
            "CloseSchemaSegment" => Some(&CLOSE_SCHEMA_SEGMENT),
            "ColumnDatatypeSegment" => Some(&COLUMN_DATATYPE_SEGMENT),
            "CommentStatementSegment" => Some(&COMMENT_STATEMENT_SEGMENT),
            "ConnectByClauseSegment" => Some(&CONNECT_BY_CLAUSE_SEGMENT),
            "ConnectionDefinition" => Some(&CONNECTION_DEFINITION),
            "ConsumerGroupParameterSegment" => Some(&CONSUMER_GROUP_PARAMETER_SEGMENT),
            "CreateAdapterScriptStatementSegment" => Some(&CREATE_ADAPTER_SCRIPT_STATEMENT_SEGMENT),
            "CreateConnectionSegment" => Some(&CREATE_CONNECTION_SEGMENT),
            "CreateConsumerGroupSegment" => Some(&CREATE_CONSUMER_GROUP_SEGMENT),
            "CreateScriptingLuaScriptStatementSegment" => Some(&CREATE_SCRIPTING_LUA_SCRIPT_STATEMENT_SEGMENT),
            "CreateTableLikeClauseSegment" => Some(&CREATE_TABLE_LIKE_CLAUSE_SEGMENT),
            "CreateUDFScriptStatementSegment" => Some(&CREATE_U_D_F_SCRIPT_STATEMENT_SEGMENT),
            "CreateVirtualSchemaStatementSegment" => Some(&CREATE_VIRTUAL_SCHEMA_STATEMENT_SEGMENT),
            "DropConnectionStatementSegment" => Some(&DROP_CONNECTION_STATEMENT_SEGMENT),
            "DropConsumerGroupSegment" => Some(&DROP_CONSUMER_GROUP_SEGMENT),
            "DropScriptStatementSegment" => Some(&DROP_SCRIPT_STATEMENT_SEGMENT),
            "EmitsSegment" => Some(&EMITS_SEGMENT),
            "ExecuteScriptSegment" => Some(&EXECUTE_SCRIPT_SEGMENT),
            "ExplainVirtualSegment" => Some(&EXPLAIN_VIRTUAL_SEGMENT),
            "ExportIntoClauseSegment" => Some(&EXPORT_INTO_CLAUSE_SEGMENT),
            "ExportStatementSegment" => Some(&EXPORT_STATEMENT_SEGMENT),
            "FBVColumnDefinitionSegment" => Some(&F_B_V_COLUMN_DEFINITION_SEGMENT),
            "FileOptionSegment" => Some(&FILE_OPTION_SEGMENT),
            "FlushStatisticsSegment" => Some(&FLUSH_STATISTICS_SEGMENT),
            "FunctionAssignmentSegment" => Some(&FUNCTION_ASSIGNMENT_SEGMENT),
            "FunctionBodySegment" => Some(&FUNCTION_BODY_SEGMENT),
            "FunctionForLoopSegment" => Some(&FUNCTION_FOR_LOOP_SEGMENT),
            "FunctionIfBranchSegment" => Some(&FUNCTION_IF_BRANCH_SEGMENT),
            "FunctionReferenceSegment" => Some(&FUNCTION_REFERENCE_SEGMENT),
            "FunctionScriptStatementSegment" => Some(&FUNCTION_SCRIPT_STATEMENT_SEGMENT),
            "FunctionWhileLoopSegment" => Some(&FUNCTION_WHILE_LOOP_SEGMENT),
            "GrantRevokeConnectionRestrictedSegment" => Some(&GRANT_REVOKE_CONNECTION_RESTRICTED_SEGMENT),
            "GrantRevokeConnectionSegment" => Some(&GRANT_REVOKE_CONNECTION_SEGMENT),
            "GrantRevokeImpersonationSegment" => Some(&GRANT_REVOKE_IMPERSONATION_SEGMENT),
            "GrantRevokeObjectPrivilegesSegment" => Some(&GRANT_REVOKE_OBJECT_PRIVILEGES_SEGMENT),
            "GrantRevokeRolesSegment" => Some(&GRANT_REVOKE_ROLES_SEGMENT),
            "GrantRevokeSystemPrivilegesSegment" => Some(&GRANT_REVOKE_SYSTEM_PRIVILEGES_SEGMENT),
            "ImpersonateSegment" => Some(&IMPERSONATE_SEGMENT),
            "ImportColumnsSegment" => Some(&IMPORT_COLUMNS_SEGMENT),
            "ImportErrorDestinationSegment" => Some(&IMPORT_ERROR_DESTINATION_SEGMENT),
            "ImportErrorsClauseSegment" => Some(&IMPORT_ERRORS_CLAUSE_SEGMENT),
            "ImportFromClauseSegment" => Some(&IMPORT_FROM_CLAUSE_SEGMENT),
            "ImportFromExportIntoDbSrcSegment" => Some(&IMPORT_FROM_EXPORT_INTO_DB_SRC_SEGMENT),
            "ImportFromExportIntoFileSegment" => Some(&IMPORT_FROM_EXPORT_INTO_FILE_SEGMENT),
            "ImportFromExportIntoScriptSegment" => Some(&IMPORT_FROM_EXPORT_INTO_SCRIPT_SEGMENT),
            "ImportStatementSegment" => Some(&IMPORT_STATEMENT_SEGMENT),
            "IntoTableSegment" => Some(&INTO_TABLE_SEGMENT),
            "KillSegment" => Some(&KILL_SEGMENT),
            "ObjectPrivilegesSegment" => Some(&OBJECT_PRIVILEGES_SEGMENT),
            "OpenSchemaSegment" => Some(&OPEN_SCHEMA_SEGMENT),
            "PreferringClauseSegment" => Some(&PREFERRING_CLAUSE_SEGMENT),
            "PreferringPlusPriorTermSegment" => Some(&PREFERRING_PLUS_PRIOR_TERM_SEGMENT),
            "PreferringPreferenceTermSegment" => Some(&PREFERRING_PREFERENCE_TERM_SEGMENT),
            "PreloadSegment" => Some(&PRELOAD_SEGMENT),
            "QualifyClauseSegment" => Some(&QUALIFY_CLAUSE_SEGMENT),
            "RecompressReorganizeSegment" => Some(&RECOMPRESS_REORGANIZE_SEGMENT),
            "ReferencingClauseSegment" => Some(&REFERENCING_CLAUSE_SEGMENT),
            "RejectClauseSegment" => Some(&REJECT_CLAUSE_SEGMENT),
            "RenameStatementSegment" => Some(&RENAME_STATEMENT_SEGMENT),
            "ScriptContentSegment" => Some(&SCRIPT_CONTENT_SEGMENT),
            "ScriptReferenceSegment" => Some(&SCRIPT_REFERENCE_SEGMENT),
            "SystemPrivilegesSegment" => Some(&SYSTEM_PRIVILEGES_SEGMENT),
            "TableContentDefinitionSegment" => Some(&TABLE_CONTENT_DEFINITION_SEGMENT),
            "TableDistributionPartitionClause" => Some(&TABLE_DISTRIBUTION_PARTITION_CLAUSE),
            "TableInlineConstraintSegment" => Some(&TABLE_INLINE_CONSTRAINT_SEGMENT),
            "TableOutOfLineConstraintSegment" => Some(&TABLE_OUT_OF_LINE_CONSTRAINT_SEGMENT),
            "TruncateAuditLogsSegment" => Some(&TRUNCATE_AUDIT_LOGS_SEGMENT),
            "UserKerberosAuthSegment" => Some(&USER_KERBEROS_AUTH_SEGMENT),
            "UserLDAPAuthSegment" => Some(&USER_L_D_A_P_AUTH_SEGMENT),
            "UserOpenIDAuthSegment" => Some(&USER_OPEN_I_D_AUTH_SEGMENT),
            "UserPasswordAuthSegment" => Some(&USER_PASSWORD_AUTH_SEGMENT),
            "ValuesRangeClauseSegment" => Some(&VALUES_RANGE_CLAUSE_SEGMENT),
            "ViewReferenceSegment" => Some(&VIEW_REFERENCE_SEGMENT),
            "WithInvalidForeignKeySegment" => Some(&WITH_INVALID_FOREIGN_KEY_SEGMENT),
            "WithInvalidUniquePKSegment" => Some(&WITH_INVALID_UNIQUE_P_K_SEGMENT),
            "NiceKeywordSegment" => Some(&NICE_KEYWORD_SEGMENT),
            "Date_truncKeywordSegment" => Some(&DATE_TRUNC_KEYWORD_SEGMENT),
            "RadiansKeywordSegment" => Some(&RADIANS_KEYWORD_SEGMENT),
            "FailedKeywordSegment" => Some(&FAILED_KEYWORD_SEGMENT),
            "Is_timestampKeywordSegment" => Some(&IS_TIMESTAMP_KEYWORD_SEGMENT),
            "RecordKeywordSegment" => Some(&RECORD_KEYWORD_SEGMENT),
            "RKeywordSegment" => Some(&R_KEYWORD_SEGMENT),
            "LeastKeywordSegment" => Some(&LEAST_KEYWORD_SEGMENT),
            "Posix_timeKeywordSegment" => Some(&POSIX_TIME_KEYWORD_SEGMENT),
            "DelimiterKeywordSegment" => Some(&DELIMITER_KEYWORD_SEGMENT),
            "St_differenceKeywordSegment" => Some(&ST_DIFFERENCE_KEYWORD_SEGMENT),
            "Query_timeoutKeywordSegment" => Some(&QUERY_TIMEOUT_KEYWORD_SEGMENT),
            "LpadKeywordSegment" => Some(&LPAD_KEYWORD_SEGMENT),
            "VirtualKeywordSegment" => Some(&VIRTUAL_KEYWORD_SEGMENT),
            "St_issimpleKeywordSegment" => Some(&ST_ISSIMPLE_KEYWORD_SEGMENT),
            "Bit_rrotateKeywordSegment" => Some(&BIT_RROTATE_KEYWORD_SEGMENT),
            "PascalKeywordSegment" => Some(&PASCAL_KEYWORD_SEGMENT),
            "StatisticsKeywordSegment" => Some(&STATISTICS_KEYWORD_SEGMENT),
            "St_intersectionKeywordSegment" => Some(&ST_INTERSECTION_KEYWORD_SEGMENT),
            "CorrKeywordSegment" => Some(&CORR_KEYWORD_SEGMENT),
            "PaddingKeywordSegment" => Some(&PADDING_KEYWORD_SEGMENT),
            "MumpsKeywordSegment" => Some(&MUMPS_KEYWORD_SEGMENT),
            "Bit_orKeywordSegment" => Some(&BIT_OR_KEYWORD_SEGMENT),
            "TruncKeywordSegment" => Some(&TRUNC_KEYWORD_SEGMENT),
            "Regr_interceptKeywordSegment" => Some(&REGR_INTERCEPT_KEYWORD_SEGMENT),
            "St_interiorringnKeywordSegment" => Some(&ST_INTERIORRINGN_KEYWORD_SEGMENT),
            "Value2procKeywordSegment" => Some(&VALUE2PROC_KEYWORD_SEGMENT),
            "DepthKeywordSegment" => Some(&DEPTH_KEYWORD_SEGMENT),
            "Raw_size_limitKeywordSegment" => Some(&RAW_SIZE_LIMIT_KEYWORD_SEGMENT),
            "VaryingKeywordSegment" => Some(&VARYING_KEYWORD_SEGMENT),
            "NeverKeywordSegment" => Some(&NEVER_KEYWORD_SEGMENT),
            "UncommittedKeywordSegment" => Some(&UNCOMMITTED_KEYWORD_SEGMENT),
            "Days_betweenKeywordSegment" => Some(&DAYS_BETWEEN_KEYWORD_SEGMENT),
            "Minutes_betweenKeywordSegment" => Some(&MINUTES_BETWEEN_KEYWORD_SEGMENT),
            "SkipKeywordSegment" => Some(&SKIP_KEYWORD_SEGMENT),
            "NormalizedKeywordSegment" => Some(&NORMALIZED_KEYWORD_SEGMENT),
            "LuaKeywordSegment" => Some(&LUA_KEYWORD_SEGMENT),
            "St_touchesKeywordSegment" => Some(&ST_TOUCHES_KEYWORD_SEGMENT),
            "St_isclosedKeywordSegment" => Some(&ST_ISCLOSED_KEYWORD_SEGMENT),
            "Json_valueKeywordSegment" => Some(&JSON_VALUE_KEYWORD_SEGMENT),
            "KeepKeywordSegment" => Some(&KEEP_KEYWORD_SEGMENT),
            "RolesKeywordSegment" => Some(&ROLES_KEYWORD_SEGMENT),
            "To_charKeywordSegment" => Some(&TO_CHAR_KEYWORD_SEGMENT),
            "UseKeywordSegment" => Some(&USE_KEYWORD_SEGMENT),
            "Consumer_groupKeywordSegment" => Some(&CONSUMER_GROUP_KEYWORD_SEGMENT),
            "Hashtype_md5KeywordSegment" => Some(&HASHTYPE_MD5_KEYWORD_SEGMENT),
            "Bit_lrotateKeywordSegment" => Some(&BIT_LROTATE_KEYWORD_SEGMENT),
            "Hash_md5KeywordSegment" => Some(&HASH_MD5_KEYWORD_SEGMENT),
            "Add_secondsKeywordSegment" => Some(&ADD_SECONDS_KEYWORD_SEGMENT),
            "AsymmetricKeywordSegment" => Some(&ASYMMETRIC_KEYWORD_SEGMENT),
            "JsonKeywordSegment" => Some(&JSON_KEYWORD_SEGMENT),
            "ResetKeywordSegment" => Some(&RESET_KEYWORD_SEGMENT),
            "St_startpointKeywordSegment" => Some(&ST_STARTPOINT_KEYWORD_SEGMENT),
            "SizeKeywordSegment" => Some(&SIZE_KEYWORD_SEGMENT),
            "AlignKeywordSegment" => Some(&ALIGN_KEYWORD_SEGMENT),
            "St_numpointsKeywordSegment" => Some(&ST_NUMPOINTS_KEYWORD_SEGMENT),
            "AssignmentKeywordSegment" => Some(&ASSIGNMENT_KEYWORD_SEGMENT),
            "Hash_sha512KeywordSegment" => Some(&HASH_SHA512_KEYWORD_SEGMENT),
            "LoginKeywordSegment" => Some(&LOGIN_KEYWORD_SEGMENT),
            "From_posix_timeKeywordSegment" => Some(&FROM_POSIX_TIME_KEYWORD_SEGMENT),
            "To_timestampKeywordSegment" => Some(&TO_TIMESTAMP_KEYWORD_SEGMENT),
            "CoshKeywordSegment" => Some(&COSH_KEYWORD_SEGMENT),
            "St_intersectsKeywordSegment" => Some(&ST_INTERSECTS_KEYWORD_SEGMENT),
            "SubjectKeywordSegment" => Some(&SUBJECT_KEYWORD_SEGMENT),
            "Nvl2KeywordSegment" => Some(&NVL2_KEYWORD_SEGMENT),
            "AuthenticatedKeywordSegment" => Some(&AUTHENTICATED_KEYWORD_SEGMENT),
            "CreatedKeywordSegment" => Some(&CREATED_KEYWORD_SEGMENT),
            "Hashtype_sha256KeywordSegment" => Some(&HASHTYPE_SHA256_KEYWORD_SEGMENT),
            "InitcapKeywordSegment" => Some(&INITCAP_KEYWORD_SEGMENT),
            "First_valueKeywordSegment" => Some(&FIRST_VALUE_KEYWORD_SEGMENT),
            "To_dateKeywordSegment" => Some(&TO_DATE_KEYWORD_SEGMENT),
            "DefaultsKeywordSegment" => Some(&DEFAULTS_KEYWORD_SEGMENT),
            "CeilingKeywordSegment" => Some(&CEILING_KEYWORD_SEGMENT),
            "St_overlapsKeywordSegment" => Some(&ST_OVERLAPS_KEYWORD_SEGMENT),
            "CharactersKeywordSegment" => Some(&CHARACTERS_KEYWORD_SEGMENT),
            "MidKeywordSegment" => Some(&MID_KEYWORD_SEGMENT),
            "St_equalsKeywordSegment" => Some(&ST_EQUALS_KEYWORD_SEGMENT),
            "Bit_lshiftKeywordSegment" => Some(&BIT_LSHIFT_KEYWORD_SEGMENT),
            "ExpKeywordSegment" => Some(&EXP_KEYWORD_SEGMENT),
            "Covar_popKeywordSegment" => Some(&COVAR_POP_KEYWORD_SEGMENT),
            "PasswordKeywordSegment" => Some(&PASSWORD_KEYWORD_SEGMENT),
            "Cpu_weightKeywordSegment" => Some(&CPU_WEIGHT_KEYWORD_SEGMENT),
            "Temp_db_ram_limitKeywordSegment" => Some(&TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT),
            "CosKeywordSegment" => Some(&COS_KEYWORD_SEGMENT),
            "SqrtKeywordSegment" => Some(&SQRT_KEYWORD_SEGMENT),
            "MultipleKeywordSegment" => Some(&MULTIPLE_KEYWORD_SEGMENT),
            "ReorganizeKeywordSegment" => Some(&REORGANIZE_KEYWORD_SEGMENT),
            "SumKeywordSegment" => Some(&SUM_KEYWORD_SEGMENT),
            "EmptyKeywordSegment" => Some(&EMPTY_KEYWORD_SEGMENT),
            "Stddev_popKeywordSegment" => Some(&STDDEV_POP_KEYWORD_SEGMENT),
            "RoleKeywordSegment" => Some(&ROLE_KEYWORD_SEGMENT),
            "PrincipalKeywordSegment" => Some(&PRINCIPAL_KEYWORD_SEGMENT),
            "Convert_tzKeywordSegment" => Some(&CONVERT_TZ_KEYWORD_SEGMENT),
            "Var_popKeywordSegment" => Some(&VAR_POP_KEYWORD_SEGMENT),
            "St_boundaryKeywordSegment" => Some(&ST_BOUNDARY_KEYWORD_SEGMENT),
            "TablesKeywordSegment" => Some(&TABLES_KEYWORD_SEGMENT),
            "AtomicKeywordSegment" => Some(&ATOMIC_KEYWORD_SEGMENT),
            "Session_temp_db_ram_limitKeywordSegment" => Some(&SESSION_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT),
            "Edit_distanceKeywordSegment" => Some(&EDIT_DISTANCE_KEYWORD_SEGMENT),
            "ChrKeywordSegment" => Some(&CHR_KEYWORD_SEGMENT),
            "Character_lengthKeywordSegment" => Some(&CHARACTER_LENGTH_KEYWORD_SEGMENT),
            "UnlimitedKeywordSegment" => Some(&UNLIMITED_KEYWORD_SEGMENT),
            "Regr_sxxKeywordSegment" => Some(&REGR_SXX_KEYWORD_SEGMENT),
            "Idle_timeoutKeywordSegment" => Some(&IDLE_TIMEOUT_KEYWORD_SEGMENT),
            "HierarchyKeywordSegment" => Some(&HIERARCHY_KEYWORD_SEGMENT),
            "ForeignKeywordSegment" => Some(&FOREIGN_KEYWORD_SEGMENT),
            "To_numberKeywordSegment" => Some(&TO_NUMBER_KEYWORD_SEGMENT),
            "AbsKeywordSegment" => Some(&ABS_KEYWORD_SEGMENT),
            "JavascriptKeywordSegment" => Some(&JAVASCRIPT_KEYWORD_SEGMENT),
            "Is_booleanKeywordSegment" => Some(&IS_BOOLEAN_KEYWORD_SEGMENT),
            "AutoKeywordSegment" => Some(&AUTO_KEYWORD_SEGMENT),
            "PreloadKeywordSegment" => Some(&PRELOAD_KEYWORD_SEGMENT),
            "EncodingKeywordSegment" => Some(&ENCODING_KEYWORD_SEGMENT),
            "St_disjointKeywordSegment" => Some(&ST_DISJOINT_KEYWORD_SEGMENT),
            "MaxKeywordSegment" => Some(&MAX_KEYWORD_SEGMENT),
            "RpadKeywordSegment" => Some(&RPAD_KEYWORD_SEGMENT),
            "St_bufferKeywordSegment" => Some(&ST_BUFFER_KEYWORD_SEGMENT),
            "Years_betweenKeywordSegment" => Some(&YEARS_BETWEEN_KEYWORD_SEGMENT),
            "BackupKeywordSegment" => Some(&BACKUP_KEYWORD_SEGMENT),
            "St_withinKeywordSegment" => Some(&ST_WITHIN_KEYWORD_SEGMENT),
            "Ratio_to_reportKeywordSegment" => Some(&RATIO_TO_REPORT_KEYWORD_SEGMENT),
            "Percentile_contKeywordSegment" => Some(&PERCENTILE_CONT_KEYWORD_SEGMENT),
            "NoticeKeywordSegment" => Some(&NOTICE_KEYWORD_SEGMENT),
            "Time_zoneKeywordSegment" => Some(&TIME_ZONE_KEYWORD_SEGMENT),
            "SymmetricKeywordSegment" => Some(&SYMMETRIC_KEYWORD_SEGMENT),
            "CurdateKeywordSegment" => Some(&CURDATE_KEYWORD_SEGMENT),
            "UcaseKeywordSegment" => Some(&UCASE_KEYWORD_SEGMENT),
            "Bit_notKeywordSegment" => Some(&BIT_NOT_KEYWORD_SEGMENT),
            "Json_extractKeywordSegment" => Some(&JSON_EXTRACT_KEYWORD_SEGMENT),
            "Months_betweenKeywordSegment" => Some(&MONTHS_BETWEEN_KEYWORD_SEGMENT),
            "EvaluateKeywordSegment" => Some(&EVALUATE_KEYWORD_SEGMENT),
            "RoundKeywordSegment" => Some(&ROUND_KEYWORD_SEGMENT),
            "LtrimKeywordSegment" => Some(&LTRIM_KEYWORD_SEGMENT),
            "ZeroifnullKeywordSegment" => Some(&ZEROIFNULL_KEYWORD_SEGMENT),
            "Default_consumer_groupKeywordSegment" => Some(&DEFAULT_CONSUMER_GROUP_KEYWORD_SEGMENT),
            "St_xKeywordSegment" => Some(&ST_X_KEYWORD_SEGMENT),
            "MaximalKeywordSegment" => Some(&MAXIMAL_KEYWORD_SEGMENT),
            "DictionaryKeywordSegment" => Some(&DICTIONARY_KEYWORD_SEGMENT),
            "UnboundedKeywordSegment" => Some(&UNBOUNDED_KEYWORD_SEGMENT),
            "Last_valueKeywordSegment" => Some(&LAST_VALUE_KEYWORD_SEGMENT),
            "Bit_xorKeywordSegment" => Some(&BIT_XOR_KEYWORD_SEGMENT),
            "DebugKeywordSegment" => Some(&DEBUG_KEYWORD_SEGMENT),
            "ConsumerKeywordSegment" => Some(&CONSUMER_KEYWORD_SEGMENT),
            "DistributeKeywordSegment" => Some(&DISTRIBUTE_KEYWORD_SEGMENT),
            "Timestamp_arithmetic_behaviorKeywordSegment" => Some(&TIMESTAMP_ARITHMETIC_BEHAVIOR_KEYWORD_SEGMENT),
            "St_max_decimal_digitsKeywordSegment" => Some(&ST_MAX_DECIMAL_DIGITS_KEYWORD_SEGMENT),
            "IsolationKeywordSegment" => Some(&ISOLATION_KEYWORD_SEGMENT),
            "LongKeywordSegment" => Some(&LONG_KEYWORD_SEGMENT),
            "User_temp_db_ram_limitKeywordSegment" => Some(&USER_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT),
            "St_isringKeywordSegment" => Some(&ST_ISRING_KEYWORD_SEGMENT),
            "ExpressionKeywordSegment" => Some(&EXPRESSION_KEYWORD_SEGMENT),
            "PrecedenceKeywordSegment" => Some(&PRECEDENCE_KEYWORD_SEGMENT),
            "SoundexKeywordSegment" => Some(&SOUNDEX_KEYWORD_SEGMENT),
            "DumpKeywordSegment" => Some(&DUMP_KEYWORD_SEGMENT),
            "InvalidKeywordSegment" => Some(&INVALID_KEYWORD_SEGMENT),
            "ShutKeywordSegment" => Some(&SHUT_KEYWORD_SEGMENT),
            "DiagnosticsKeywordSegment" => Some(&DIAGNOSTICS_KEYWORD_SEGMENT),
            "Cologne_phoneticKeywordSegment" => Some(&COLOGNE_PHONETIC_KEYWORD_SEGMENT),
            "NprocKeywordSegment" => Some(&NPROC_KEYWORD_SEGMENT),
            "BernoulliKeywordSegment" => Some(&BERNOULLI_KEYWORD_SEGMENT),
            "CountKeywordSegment" => Some(&COUNT_KEYWORD_SEGMENT),
            "ReturningKeywordSegment" => Some(&RETURNING_KEYWORD_SEGMENT),
            "RowidKeywordSegment" => Some(&ROWID_KEYWORD_SEGMENT),
            "Bit_lengthKeywordSegment" => Some(&BIT_LENGTH_KEYWORD_SEGMENT),
            "TraceKeywordSegment" => Some(&TRACE_KEYWORD_SEGMENT),
            "Regexp_substrKeywordSegment" => Some(&REGEXP_SUBSTR_KEYWORD_SEGMENT),
            "Is_ymintervalKeywordSegment" => Some(&IS_YMINTERVAL_KEYWORD_SEGMENT),
            "QuietKeywordSegment" => Some(&QUIET_KEYWORD_SEGMENT),
            "Atan2KeywordSegment" => Some(&ATAN2_KEYWORD_SEGMENT),
            "TypeKeywordSegment" => Some(&TYPE_KEYWORD_SEGMENT),
            "RejectKeywordSegment" => Some(&REJECT_KEYWORD_SEGMENT),
            "Log10KeywordSegment" => Some(&LOG10_KEYWORD_SEGMENT),
            "AsinKeywordSegment" => Some(&ASIN_KEYWORD_SEGMENT),
            "TanhKeywordSegment" => Some(&TANH_KEYWORD_SEGMENT),
            "ConcatKeywordSegment" => Some(&CONCAT_KEYWORD_SEGMENT),
            "Group_temp_db_ram_limitKeywordSegment" => Some(&GROUP_TEMP_DB_RAM_LIMIT_KEYWORD_SEGMENT),
            "NullifzeroKeywordSegment" => Some(&NULLIFZERO_KEYWORD_SEGMENT),
            "DelimitKeywordSegment" => Some(&DELIMIT_KEYWORD_SEGMENT),
            "InstrKeywordSegment" => Some(&INSTR_KEYWORD_SEGMENT),
            "LeadKeywordSegment" => Some(&LEAD_KEYWORD_SEGMENT),
            "RecompressKeywordSegment" => Some(&RECOMPRESS_KEYWORD_SEGMENT),
            "AdminKeywordSegment" => Some(&ADMIN_KEYWORD_SEGMENT),
            "Add_weeksKeywordSegment" => Some(&ADD_WEEKS_KEYWORD_SEGMENT),
            "DegreesKeywordSegment" => Some(&DEGREES_KEYWORD_SEGMENT),
            "St_force2dKeywordSegment" => Some(&ST_FORCE2D_KEYWORD_SEGMENT),
            "LengthKeywordSegment" => Some(&LENGTH_KEYWORD_SEGMENT),
            "DownKeywordSegment" => Some(&DOWN_KEYWORD_SEGMENT),
            "LagKeywordSegment" => Some(&LAG_KEYWORD_SEGMENT),
            "Session_parameterKeywordSegment" => Some(&SESSION_PARAMETER_KEYWORD_SEGMENT),
            "Var_sampKeywordSegment" => Some(&VAR_SAMP_KEYWORD_SEGMENT),
            "CeilKeywordSegment" => Some(&CEIL_KEYWORD_SEGMENT),
            "StepKeywordSegment" => Some(&STEP_KEYWORD_SEGMENT),
            "AvgKeywordSegment" => Some(&AVG_KEYWORD_SEGMENT),
            "St_geometrytypeKeywordSegment" => Some(&ST_GEOMETRYTYPE_KEYWORD_SEGMENT),
            "DecodeKeywordSegment" => Some(&DECODE_KEYWORD_SEGMENT),
            "PrivilegeKeywordSegment" => Some(&PRIVILEGE_KEYWORD_SEGMENT),
            "Time_zone_behaviorKeywordSegment" => Some(&TIME_ZONE_BEHAVIOR_KEYWORD_SEGMENT),
            "IncludingKeywordSegment" => Some(&INCLUDING_KEYWORD_SEGMENT),
            "IgnoreKeywordSegment" => Some(&IGNORE_KEYWORD_SEGMENT),
            "St_numgeometriesKeywordSegment" => Some(&ST_NUMGEOMETRIES_KEYWORD_SEGMENT),
            "PliKeywordSegment" => Some(&PLI_KEYWORD_SEGMENT),
            "Password_expiry_policyKeywordSegment" => Some(&PASSWORD_EXPIRY_POLICY_KEYWORD_SEGMENT),
            "UndoKeywordSegment" => Some(&UNDO_KEYWORD_SEGMENT),
            "OverflowKeywordSegment" => Some(&OVERFLOW_KEYWORD_SEGMENT),
            "InitiallyKeywordSegment" => Some(&INITIALLY_KEYWORD_SEGMENT),
            "Covar_sampKeywordSegment" => Some(&COVAR_SAMP_KEYWORD_SEGMENT),
            "ExplainKeywordSegment" => Some(&EXPLAIN_KEYWORD_SEGMENT),
            "IdentifiedKeywordSegment" => Some(&IDENTIFIED_KEYWORD_SEGMENT),
            "DivKeywordSegment" => Some(&DIV_KEYWORD_SEGMENT),
            "Add_hoursKeywordSegment" => Some(&ADD_HOURS_KEYWORD_SEGMENT),
            "Regexp_instrKeywordSegment" => Some(&REGEXP_INSTR_KEYWORD_SEGMENT),
            "SinhKeywordSegment" => Some(&SINH_KEYWORD_SEGMENT),
            "OptimizeKeywordSegment" => Some(&OPTIMIZE_KEYWORD_SEGMENT),
            "St_pointnKeywordSegment" => Some(&ST_POINTN_KEYWORD_SEGMENT),
            "AlwaysKeywordSegment" => Some(&ALWAYS_KEYWORD_SEGMENT),
            "Bit_to_numKeywordSegment" => Some(&BIT_TO_NUM_KEYWORD_SEGMENT),
            "LogsKeywordSegment" => Some(&LOGS_KEYWORD_SEGMENT),
            "Percentile_discKeywordSegment" => Some(&PERCENTILE_DISC_KEYWORD_SEGMENT),
            "GreatestKeywordSegment" => Some(&GREATEST_KEYWORD_SEGMENT),
            "QueryKeywordSegment" => Some(&QUERY_KEYWORD_SEGMENT),
            "ErrorKeywordSegment" => Some(&ERROR_KEYWORD_SEGMENT),
            "Is_dateKeywordSegment" => Some(&IS_DATE_KEYWORD_SEGMENT),
            "St_setsridKeywordSegment" => Some(&ST_SETSRID_KEYWORD_SEGMENT),
            "CobolKeywordSegment" => Some(&COBOL_KEYWORD_SEGMENT),
            "St_symdifferenceKeywordSegment" => Some(&ST_SYMDIFFERENCE_KEYWORD_SEGMENT),
            "DriverKeywordSegment" => Some(&DRIVER_KEYWORD_SEGMENT),
            "HandlerKeywordSegment" => Some(&HANDLER_KEYWORD_SEGMENT),
            "Row_numberKeywordSegment" => Some(&ROW_NUMBER_KEYWORD_SEGMENT),
            "NvlKeywordSegment" => Some(&NVL_KEYWORD_SEGMENT),
            "Snapshot_modeKeywordSegment" => Some(&SNAPSHOT_MODE_KEYWORD_SEGMENT),
            "ExpireKeywordSegment" => Some(&EXPIRE_KEYWORD_SEGMENT),
            "RespectKeywordSegment" => Some(&RESPECT_KEYWORD_SEGMENT),
            "ObjectsKeywordSegment" => Some(&OBJECTS_KEYWORD_SEGMENT),
            "JavaKeywordSegment" => Some(&JAVA_KEYWORD_SEGMENT),
            "Stddev_sampKeywordSegment" => Some(&STDDEV_SAMP_KEYWORD_SEGMENT),
            "AsciiKeywordSegment" => Some(&ASCII_KEYWORD_SEGMENT),
            "Grouping_idKeywordSegment" => Some(&GROUPING_ID_KEYWORD_SEGMENT),
            "FloorKeywordSegment" => Some(&FLOOR_KEYWORD_SEGMENT),
            "Hashtype_shaKeywordSegment" => Some(&HASHTYPE_SHA_KEYWORD_SEGMENT),
            "Add_yearsKeywordSegment" => Some(&ADD_YEARS_KEYWORD_SEGMENT),
            "Script_output_addressKeywordSegment" => Some(&SCRIPT_OUTPUT_ADDRESS_KEYWORD_SEGMENT),
            "AdapterKeywordSegment" => Some(&ADAPTER_KEYWORD_SEGMENT),
            "KeyKeywordSegment" => Some(&KEY_KEYWORD_SEGMENT),
            "St_isemptyKeywordSegment" => Some(&ST_ISEMPTY_KEYWORD_SEGMENT),
            "St_exteriorringKeywordSegment" => Some(&ST_EXTERIORRING_KEYWORD_SEGMENT),
            "SerializableKeywordSegment" => Some(&SERIALIZABLE_KEYWORD_SEGMENT),
            "DatabaseKeywordSegment" => Some(&DATABASE_KEYWORD_SEGMENT),
            "LowerKeywordSegment" => Some(&LOWER_KEYWORD_SEGMENT),
            "Regexp_replaceKeywordSegment" => Some(&REGEXP_REPLACE_KEYWORD_SEGMENT),
            "Sys_connect_by_pathKeywordSegment" => Some(&SYS_CONNECT_BY_PATH_KEYWORD_SEGMENT),
            "LockKeywordSegment" => Some(&LOCK_KEYWORD_SEGMENT),
            "St_convexhullKeywordSegment" => Some(&ST_CONVEXHULL_KEYWORD_SEGMENT),
            "ImpersonationKeywordSegment" => Some(&IMPERSONATION_KEYWORD_SEGMENT),
            "EstimateKeywordSegment" => Some(&ESTIMATE_KEYWORD_SEGMENT),
            "Dense_rankKeywordSegment" => Some(&DENSE_RANK_KEYWORD_SEGMENT),
            "LnKeywordSegment" => Some(&LN_KEYWORD_SEGMENT),
            "WeekKeywordSegment" => Some(&WEEK_KEYWORD_SEGMENT),
            "Add_minutesKeywordSegment" => Some(&ADD_MINUTES_KEYWORD_SEGMENT),
            "Script_languagesKeywordSegment" => Some(&SCRIPT_LANGUAGES_KEYWORD_SEGMENT),
            "Approximate_count_distinctKeywordSegment" => Some(&APPROXIMATE_COUNT_DISTINCT_KEYWORD_SEGMENT),
            "ClearKeywordSegment" => Some(&CLEAR_KEYWORD_SEGMENT),
            "FortranKeywordSegment" => Some(&FORTRAN_KEYWORD_SEGMENT),
            "GraphKeywordSegment" => Some(&GRAPH_KEYWORD_SEGMENT),
            "KillKeywordSegment" => Some(&KILL_KEYWORD_SEGMENT),
            "EveryKeywordSegment" => Some(&EVERY_KEYWORD_SEGMENT),
            "MessageKeywordSegment" => Some(&MESSAGE_KEYWORD_SEGMENT),
            "Log2KeywordSegment" => Some(&LOG2_KEYWORD_SEGMENT),
            "SchemasKeywordSegment" => Some(&SCHEMAS_KEYWORD_SEGMENT),
            "UnicodechrKeywordSegment" => Some(&UNICODECHR_KEYWORD_SEGMENT),
            "TiesKeywordSegment" => Some(&TIES_KEYWORD_SEGMENT),
            "StddevKeywordSegment" => Some(&STDDEV_KEYWORD_SEGMENT),
            "Is_dsintervalKeywordSegment" => Some(&IS_DSINTERVAL_KEYWORD_SEGMENT),
            "DistributionKeywordSegment" => Some(&DISTRIBUTION_KEYWORD_SEGMENT),
            "NumtodsintervalKeywordSegment" => Some(&NUMTODSINTERVAL_KEYWORD_SEGMENT),
            "St_envelopeKeywordSegment" => Some(&ST_ENVELOPE_KEYWORD_SEGMENT),
            "PowerKeywordSegment" => Some(&POWER_KEYWORD_SEGMENT),
            "Regr_syyKeywordSegment" => Some(&REGR_SYY_KEYWORD_SEGMENT),
            "SimpleKeywordSegment" => Some(&SIMPLE_KEYWORD_SEGMENT),
            "SchemeKeywordSegment" => Some(&SCHEME_KEYWORD_SEGMENT),
            "Sys_guidKeywordSegment" => Some(&SYS_GUID_KEYWORD_SEGMENT),
            "TablesampleKeywordSegment" => Some(&TABLESAMPLE_KEYWORD_SEGMENT),
            "ExcludeKeywordSegment" => Some(&EXCLUDE_KEYWORD_SEGMENT),
            "Hash_tigerKeywordSegment" => Some(&HASH_TIGER_KEYWORD_SEGMENT),
            "CotKeywordSegment" => Some(&COT_KEYWORD_SEGMENT),
            "St_transformKeywordSegment" => Some(&ST_TRANSFORM_KEYWORD_SEGMENT),
            "SignKeywordSegment" => Some(&SIGN_KEYWORD_SEGMENT),
            "AttemptsKeywordSegment" => Some(&ATTEMPTS_KEYWORD_SEGMENT),
            "PrimaryKeywordSegment" => Some(&PRIMARY_KEYWORD_SEGMENT),
            "St_geometrynKeywordSegment" => Some(&ST_GEOMETRYN_KEYWORD_SEGMENT),
            "PiKeywordSegment" => Some(&PI_KEYWORD_SEGMENT),
            "Regr_avgxKeywordSegment" => Some(&REGR_AVGX_KEYWORD_SEGMENT),
            "St_centroidKeywordSegment" => Some(&ST_CENTROID_KEYWORD_SEGMENT),
            "RandKeywordSegment" => Some(&RAND_KEYWORD_SEGMENT),
            "St_numinteriorringsKeywordSegment" => Some(&ST_NUMINTERIORRINGS_KEYWORD_SEGMENT),
            "RtrimKeywordSegment" => Some(&RTRIM_KEYWORD_SEGMENT),
            "Seconds_betweenKeywordSegment" => Some(&SECONDS_BETWEEN_KEYWORD_SEGMENT),
            "HashKeywordSegment" => Some(&HASH_KEYWORD_SEGMENT),
            "Query_cacheKeywordSegment" => Some(&QUERY_CACHE_KEYWORD_SEGMENT),
            "St_dimensionKeywordSegment" => Some(&ST_DIMENSION_KEYWORD_SEGMENT),
            "OctetsKeywordSegment" => Some(&OCTETS_KEYWORD_SEGMENT),
            "ReverseKeywordSegment" => Some(&REVERSE_KEYWORD_SEGMENT),
            "Hash_sha256KeywordSegment" => Some(&HASH_SHA256_KEYWORD_SEGMENT),
            "St_lengthKeywordSegment" => Some(&ST_LENGTH_KEYWORD_SEGMENT),
            "UpperKeywordSegment" => Some(&UPPER_KEYWORD_SEGMENT),
            "ManageKeywordSegment" => Some(&MANAGE_KEYWORD_SEGMENT),
            "St_containsKeywordSegment" => Some(&ST_CONTAINS_KEYWORD_SEGMENT),
            "Regr_countKeywordSegment" => Some(&REGR_COUNT_KEYWORD_SEGMENT),
            "PrecisionKeywordSegment" => Some(&PRECISION_KEYWORD_SEGMENT),
            "FlushKeywordSegment" => Some(&FLUSH_KEYWORD_SEGMENT),
            "Bit_andKeywordSegment" => Some(&BIT_AND_KEYWORD_SEGMENT),
            "Hashtype_sha512KeywordSegment" => Some(&HASHTYPE_SHA512_KEYWORD_SEGMENT),
            "Add_monthsKeywordSegment" => Some(&ADD_MONTHS_KEYWORD_SEGMENT),
            "RepeatableKeywordSegment" => Some(&REPEATABLE_KEYWORD_SEGMENT),
            "St_areaKeywordSegment" => Some(&ST_AREA_KEYWORD_SEGMENT),
            "ChangeKeywordSegment" => Some(&CHANGE_KEYWORD_SEGMENT),
            "St_unionKeywordSegment" => Some(&ST_UNION_KEYWORD_SEGMENT),
            "UnicodeKeywordSegment" => Some(&UNICODE_KEYWORD_SEGMENT),
            "Hashtype_sha1KeywordSegment" => Some(&HASHTYPE_SHA1_KEYWORD_SEGMENT),
            "Hash_shaKeywordSegment" => Some(&HASH_SHA_KEYWORD_SEGMENT),
            "KerberosKeywordSegment" => Some(&KERBEROS_KEYWORD_SEGMENT),
            "Add_daysKeywordSegment" => Some(&ADD_DAYS_KEYWORD_SEGMENT),
            "Octet_lengthKeywordSegment" => Some(&OCTET_LENGTH_KEYWORD_SEGMENT),
            "RankKeywordSegment" => Some(&RANK_KEYWORD_SEGMENT),
            "Regr_sxyKeywordSegment" => Some(&REGR_SXY_KEYWORD_SEGMENT),
            "TranslateKeywordSegment" => Some(&TRANSLATE_KEYWORD_SEGMENT),
            "PythonKeywordSegment" => Some(&PYTHON_KEYWORD_SEGMENT),
            "OwnerKeywordSegment" => Some(&OWNER_KEYWORD_SEGMENT),
            "LocateKeywordSegment" => Some(&LOCATE_KEYWORD_SEGMENT),
            "SecureKeywordSegment" => Some(&SECURE_KEYWORD_SEGMENT),
            "To_ymintervalKeywordSegment" => Some(&TO_YMINTERVAL_KEYWORD_SEGMENT),
            "ExaKeywordSegment" => Some(&EXA_KEYWORD_SEGMENT),
            "SinKeywordSegment" => Some(&SIN_KEYWORD_SEGMENT),
            "VarianceKeywordSegment" => Some(&VARIANCE_KEYWORD_SEGMENT),
            "AccessKeywordSegment" => Some(&ACCESS_KEYWORD_SEGMENT),
            "OffsetKeywordSegment" => Some(&OFFSET_KEYWORD_SEGMENT),
            "IprocKeywordSegment" => Some(&IPROC_KEYWORD_SEGMENT),
            "LcaseKeywordSegment" => Some(&LCASE_KEYWORD_SEGMENT),
            "Utf8KeywordSegment" => Some(&UTF8_KEYWORD_SEGMENT),
            "JdbcKeywordSegment" => Some(&JDBC_KEYWORD_SEGMENT),
            "MinKeywordSegment" => Some(&MIN_KEYWORD_SEGMENT),
            "OraKeywordSegment" => Some(&ORA_KEYWORD_SEGMENT),
            "ScalarKeywordSegment" => Some(&SCALAR_KEYWORD_SEGMENT),
            "LanguageKeywordSegment" => Some(&LANGUAGE_KEYWORD_SEGMENT),
            "St_crossesKeywordSegment" => Some(&ST_CROSSES_KEYWORD_SEGMENT),
            "AnalyzeKeywordSegment" => Some(&ANALYZE_KEYWORD_SEGMENT),
            "To_dsintervalKeywordSegment" => Some(&TO_DSINTERVAL_KEYWORD_SEGMENT),
            "ExcludingKeywordSegment" => Some(&EXCLUDING_KEYWORD_SEGMENT),
            "NowKeywordSegment" => Some(&NOW_KEYWORD_SEGMENT),
            "OptimizerKeywordSegment" => Some(&OPTIMIZER_KEYWORD_SEGMENT),
            "TanKeywordSegment" => Some(&TAN_KEYWORD_SEGMENT),
            "NumtoymintervalKeywordSegment" => Some(&NUMTOYMINTERVAL_KEYWORD_SEGMENT),
            "SubstrKeywordSegment" => Some(&SUBSTR_KEYWORD_SEGMENT),
            "St_endpointKeywordSegment" => Some(&ST_ENDPOINT_KEYWORD_SEGMENT),
            "ConnectKeywordSegment" => Some(&CONNECT_KEYWORD_SEGMENT),
            "AtanKeywordSegment" => Some(&ATAN_KEYWORD_SEGMENT),
            "MedianKeywordSegment" => Some(&MEDIAN_KEYWORD_SEGMENT),
            "NullsKeywordSegment" => Some(&NULLS_KEYWORD_SEGMENT),
            "MulKeywordSegment" => Some(&MUL_KEYWORD_SEGMENT),
            "KeysKeywordSegment" => Some(&KEYS_KEYWORD_SEGMENT),
            "TypeofKeywordSegment" => Some(&TYPEOF_KEYWORD_SEGMENT),
            "Regr_r2KeywordSegment" => Some(&REGR_R2_KEYWORD_SEGMENT),
            "Bit_checkKeywordSegment" => Some(&BIT_CHECK_KEYWORD_SEGMENT),
            "Bit_setKeywordSegment" => Some(&BIT_SET_KEYWORD_SEGMENT),
            "Bit_rshiftKeywordSegment" => Some(&BIT_RSHIFT_KEYWORD_SEGMENT),
            "Min_scaleKeywordSegment" => Some(&MIN_SCALE_KEYWORD_SEGMENT),
            "CommentsKeywordSegment" => Some(&COMMENTS_KEYWORD_SEGMENT),
            "AuditKeywordSegment" => Some(&AUDIT_KEYWORD_SEGMENT),
            "Regr_avgyKeywordSegment" => Some(&REGR_AVGY_KEYWORD_SEGMENT),
            "RowcountKeywordSegment" => Some(&ROWCOUNT_KEYWORD_SEGMENT),
            "HasKeywordSegment" => Some(&HAS_KEYWORD_SEGMENT),
            "TasksKeywordSegment" => Some(&TASKS_KEYWORD_SEGMENT),
            "ExperimentalKeywordSegment" => Some(&EXPERIMENTAL_KEYWORD_SEGMENT),
            "Is_numberKeywordSegment" => Some(&IS_NUMBER_KEYWORD_SEGMENT),
            "FilesKeywordSegment" => Some(&FILES_KEYWORD_SEGMENT),
            "St_yKeywordSegment" => Some(&ST_Y_KEYWORD_SEGMENT),
            "Hashtype_tigerKeywordSegment" => Some(&HASHTYPE_TIGER_KEYWORD_SEGMENT),
            "CommittedKeywordSegment" => Some(&COMMITTED_KEYWORD_SEGMENT),
            "LinkKeywordSegment" => Some(&LINK_KEYWORD_SEGMENT),
            "WriteKeywordSegment" => Some(&WRITE_KEYWORD_SEGMENT),
            "Hash_sha1KeywordSegment" => Some(&HASH_SHA1_KEYWORD_SEGMENT),
            "OpenidKeywordSegment" => Some(&OPENID_KEYWORD_SEGMENT),
            "CommentKeywordSegment" => Some(&COMMENT_KEYWORD_SEGMENT),
            "Regr_slopeKeywordSegment" => Some(&REGR_SLOPE_KEYWORD_SEGMENT),
            "BreadthKeywordSegment" => Some(&BREADTH_KEYWORD_SEGMENT),
            "Password_security_policyKeywordSegment" => Some(&PASSWORD_SECURITY_POLICY_KEYWORD_SEGMENT),
            "St_distanceKeywordSegment" => Some(&ST_DISTANCE_KEYWORD_SEGMENT),
            "AcosKeywordSegment" => Some(&ACOS_KEYWORD_SEGMENT),
            "Hours_betweenKeywordSegment" => Some(&HOURS_BETWEEN_KEYWORD_SEGMENT),
            "AnsiKeywordSegment" => Some(&ANSI_KEYWORD_SEGMENT),
            "RollbackKeywordSegment" => Some(&ROLLBACK_KEYWORD_SEGMENT),
            "TrueKeywordSegment" => Some(&TRUE_KEYWORD_SEGMENT),
            "DynamicKeywordSegment" => Some(&DYNAMIC_KEYWORD_SEGMENT),
            "Character_set_nameKeywordSegment" => Some(&CHARACTER_SET_NAME_KEYWORD_SEGMENT),
            "ReleaseKeywordSegment" => Some(&RELEASE_KEYWORD_SEGMENT),
            "CheckedKeywordSegment" => Some(&CHECKED_KEYWORD_SEGMENT),
            "StructureKeywordSegment" => Some(&STRUCTURE_KEYWORD_SEGMENT),
            "DistinctKeywordSegment" => Some(&DISTINCT_KEYWORD_SEGMENT),
            "RandomKeywordSegment" => Some(&RANDOM_KEYWORD_SEGMENT),
            "InstanceKeywordSegment" => Some(&INSTANCE_KEYWORD_SEGMENT),
            "NationalKeywordSegment" => Some(&NATIONAL_KEYWORD_SEGMENT),
            "NumericKeywordSegment" => Some(&NUMERIC_KEYWORD_SEGMENT),
            "ReturnKeywordSegment" => Some(&RETURN_KEYWORD_SEGMENT),
            "ClobKeywordSegment" => Some(&CLOB_KEYWORD_SEGMENT),
            "UpdateKeywordSegment" => Some(&UPDATE_KEYWORD_SEGMENT),
            "LocatorKeywordSegment" => Some(&LOCATOR_KEYWORD_SEGMENT),
            "Collation_nameKeywordSegment" => Some(&COLLATION_NAME_KEYWORD_SEGMENT),
            "Sql_decimalKeywordSegment" => Some(&SQL_DECIMAL_KEYWORD_SEGMENT),
            "BigintKeywordSegment" => Some(&BIGINT_KEYWORD_SEGMENT),
            "NewKeywordSegment" => Some(&NEW_KEYWORD_SEGMENT),
            "Character_set_schemaKeywordSegment" => Some(&CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT),
            "ImpersonateKeywordSegment" => Some(&IMPERSONATE_KEYWORD_SEGMENT),
            "PrecedingKeywordSegment" => Some(&PRECEDING_KEYWORD_SEGMENT),
            "MinuteKeywordSegment" => Some(&MINUTE_KEYWORD_SEGMENT),
            "YesKeywordSegment" => Some(&YES_KEYWORD_SEGMENT),
            "AttributeKeywordSegment" => Some(&ATTRIBUTE_KEYWORD_SEGMENT),
            "BeforeKeywordSegment" => Some(&BEFORE_KEYWORD_SEGMENT),
            "SearchKeywordSegment" => Some(&SEARCH_KEYWORD_SEGMENT),
            "DlvalueKeywordSegment" => Some(&DLVALUE_KEYWORD_SEGMENT),
            "GrantKeywordSegment" => Some(&GRANT_KEYWORD_SEGMENT),
            "Connect_by_rootKeywordSegment" => Some(&CONNECT_BY_ROOT_KEYWORD_SEGMENT),
            "UnnestKeywordSegment" => Some(&UNNEST_KEYWORD_SEGMENT),
            "ChainKeywordSegment" => Some(&CHAIN_KEYWORD_SEGMENT),
            "SimilarKeywordSegment" => Some(&SIMILAR_KEYWORD_SEGMENT),
            "BitKeywordSegment" => Some(&BIT_KEYWORD_SEGMENT),
            "IntKeywordSegment" => Some(&INT_KEYWORD_SEGMENT),
            "DlurlpathKeywordSegment" => Some(&DLURLPATH_KEYWORD_SEGMENT),
            "InvokerKeywordSegment" => Some(&INVOKER_KEYWORD_SEGMENT),
            "OffKeywordSegment" => Some(&OFF_KEYWORD_SEGMENT),
            "ExistsKeywordSegment" => Some(&EXISTS_KEYWORD_SEGMENT),
            "LeadingKeywordSegment" => Some(&LEADING_KEYWORD_SEGMENT),
            "Default_like_escape_characterKeywordSegment" => Some(&DEFAULT_LIKE_ESCAPE_CHARACTER_KEYWORD_SEGMENT),
            "Nls_timestamp_formatKeywordSegment" => Some(&NLS_TIMESTAMP_FORMAT_KEYWORD_SEGMENT),
            "MonthKeywordSegment" => Some(&MONTH_KEYWORD_SEGMENT),
            "TimeKeywordSegment" => Some(&TIME_KEYWORD_SEGMENT),
            "MinusKeywordSegment" => Some(&MINUS_KEYWORD_SEGMENT),
            "EnabledKeywordSegment" => Some(&ENABLED_KEYWORD_SEGMENT),
            "FinalKeywordSegment" => Some(&FINAL_KEYWORD_SEGMENT),
            "SelectKeywordSegment" => Some(&SELECT_KEYWORD_SEGMENT),
            "Sql_timestampKeywordSegment" => Some(&SQL_TIMESTAMP_KEYWORD_SEGMENT),
            "CurrentKeywordSegment" => Some(&CURRENT_KEYWORD_SEGMENT),
            "DescriptorKeywordSegment" => Some(&DESCRIPTOR_KEYWORD_SEGMENT),
            "Nvarchar2KeywordSegment" => Some(&NVARCHAR2_KEYWORD_SEGMENT),
            "WithKeywordSegment" => Some(&WITH_KEYWORD_SEGMENT),
            "Sql_preprocessor_scriptKeywordSegment" => Some(&SQL_PREPROCESSOR_SCRIPT_KEYWORD_SEGMENT),
            "LogKeywordSegment" => Some(&LOG_KEYWORD_SEGMENT),
            "OrderingKeywordSegment" => Some(&ORDERING_KEYWORD_SEGMENT),
            "OthersKeywordSegment" => Some(&OTHERS_KEYWORD_SEGMENT),
            "ListaggKeywordSegment" => Some(&LISTAGG_KEYWORD_SEGMENT),
            "ReadsKeywordSegment" => Some(&READS_KEYWORD_SEGMENT),
            "ViewKeywordSegment" => Some(&VIEW_KEYWORD_SEGMENT),
            "ObjectKeywordSegment" => Some(&OBJECT_KEYWORD_SEGMENT),
            "GroupsKeywordSegment" => Some(&GROUPS_KEYWORD_SEGMENT),
            "SecondKeywordSegment" => Some(&SECOND_KEYWORD_SEGMENT),
            "OrKeywordSegment" => Some(&OR_KEYWORD_SEGMENT),
            "TemporaryKeywordSegment" => Some(&TEMPORARY_KEYWORD_SEGMENT),
            "RepeatKeywordSegment" => Some(&REPEAT_KEYWORD_SEGMENT),
            "LevelKeywordSegment" => Some(&LEVEL_KEYWORD_SEGMENT),
            "AnyKeywordSegment" => Some(&ANY_KEYWORD_SEGMENT),
            "IntoKeywordSegment" => Some(&INTO_KEYWORD_SEGMENT),
            "CharKeywordSegment" => Some(&CHAR_KEYWORD_SEGMENT),
            "PreferringKeywordSegment" => Some(&PREFERRING_KEYWORD_SEGMENT),
            "FloatKeywordSegment" => Some(&FLOAT_KEYWORD_SEGMENT),
            "RelativeKeywordSegment" => Some(&RELATIVE_KEYWORD_SEGMENT),
            "SecurityKeywordSegment" => Some(&SECURITY_KEYWORD_SEGMENT),
            "CardinalityKeywordSegment" => Some(&CARDINALITY_KEYWORD_SEGMENT),
            "MethodKeywordSegment" => Some(&METHOD_KEYWORD_SEGMENT),
            "Parameter_specific_nameKeywordSegment" => Some(&PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT),
            "Sql_tinyintKeywordSegment" => Some(&SQL_TINYINT_KEYWORD_SEGMENT),
            "DispatchKeywordSegment" => Some(&DISPATCH_KEYWORD_SEGMENT),
            "GrantedKeywordSegment" => Some(&GRANTED_KEYWORD_SEGMENT),
            "SetsKeywordSegment" => Some(&SETS_KEYWORD_SEGMENT),
            "LoopKeywordSegment" => Some(&LOOP_KEYWORD_SEGMENT),
            "DatalinkKeywordSegment" => Some(&DATALINK_KEYWORD_SEGMENT),
            "TinyintKeywordSegment" => Some(&TINYINT_KEYWORD_SEGMENT),
            "Sql_type_dateKeywordSegment" => Some(&SQL_TYPE_DATE_KEYWORD_SEGMENT),
            "IntersectKeywordSegment" => Some(&INTERSECT_KEYWORD_SEGMENT),
            "DlurlserverKeywordSegment" => Some(&DLURLSERVER_KEYWORD_SEGMENT),
            "FileKeywordSegment" => Some(&FILE_KEYWORD_SEGMENT),
            "IntegrityKeywordSegment" => Some(&INTEGRITY_KEYWORD_SEGMENT),
            "OrdinalityKeywordSegment" => Some(&ORDINALITY_KEYWORD_SEGMENT),
            "ExternalKeywordSegment" => Some(&EXTERNAL_KEYWORD_SEGMENT),
            "FreeKeywordSegment" => Some(&FREE_KEYWORD_SEGMENT),
            "UsageKeywordSegment" => Some(&USAGE_KEYWORD_SEGMENT),
            "NoKeywordSegment" => Some(&NO_KEYWORD_SEGMENT),
            "WithoutKeywordSegment" => Some(&WITHOUT_KEYWORD_SEGMENT),
            "ActionKeywordSegment" => Some(&ACTION_KEYWORD_SEGMENT),
            "TableKeywordSegment" => Some(&TABLE_KEYWORD_SEGMENT),
            "NclobKeywordSegment" => Some(&NCLOB_KEYWORD_SEGMENT),
            "DerefKeywordSegment" => Some(&DEREF_KEYWORD_SEGMENT),
            "TruncateKeywordSegment" => Some(&TRUNCATE_KEYWORD_SEGMENT),
            "CalledKeywordSegment" => Some(&CALLED_KEYWORD_SEGMENT),
            "Current_timestampKeywordSegment" => Some(&CURRENT_TIMESTAMP_KEYWORD_SEGMENT),
            "DefaultKeywordSegment" => Some(&DEFAULT_KEYWORD_SEGMENT),
            "DeferrableKeywordSegment" => Some(&DEFERRABLE_KEYWORD_SEGMENT),
            "Current_statementKeywordSegment" => Some(&CURRENT_STATEMENT_KEYWORD_SEGMENT),
            "Sql_charKeywordSegment" => Some(&SQL_CHAR_KEYWORD_SEGMENT),
            "Current_schemaKeywordSegment" => Some(&CURRENT_SCHEMA_KEYWORD_SEGMENT),
            "OverlayKeywordSegment" => Some(&OVERLAY_KEYWORD_SEGMENT),
            "ConstantKeywordSegment" => Some(&CONSTANT_KEYWORD_SEGMENT),
            "StatementKeywordSegment" => Some(&STATEMENT_KEYWORD_SEGMENT),
            "ByKeywordSegment" => Some(&BY_KEYWORD_SEGMENT),
            "ForallKeywordSegment" => Some(&FORALL_KEYWORD_SEGMENT),
            "SequenceKeywordSegment" => Some(&SEQUENCE_KEYWORD_SEGMENT),
            "UnderKeywordSegment" => Some(&UNDER_KEYWORD_SEGMENT),
            "InnerKeywordSegment" => Some(&INNER_KEYWORD_SEGMENT),
            "IdentityKeywordSegment" => Some(&IDENTITY_KEYWORD_SEGMENT),
            "Returned_lengthKeywordSegment" => Some(&RETURNED_LENGTH_KEYWORD_SEGMENT),
            "DropKeywordSegment" => Some(&DROP_KEYWORD_SEGMENT),
            "AuthidKeywordSegment" => Some(&AUTHID_KEYWORD_SEGMENT),
            "SessionKeywordSegment" => Some(&SESSION_KEYWORD_SEGMENT),
            "OnKeywordSegment" => Some(&ON_KEYWORD_SEGMENT),
            "BlockedKeywordSegment" => Some(&BLOCKED_KEYWORD_SEGMENT),
            "ReturnsKeywordSegment" => Some(&RETURNS_KEYWORD_SEGMENT),
            "LocaltimeKeywordSegment" => Some(&LOCALTIME_KEYWORD_SEGMENT),
            "NaturalKeywordSegment" => Some(&NATURAL_KEYWORD_SEGMENT),
            "TriggerKeywordSegment" => Some(&TRIGGER_KEYWORD_SEGMENT),
            "SchemaKeywordSegment" => Some(&SCHEMA_KEYWORD_SEGMENT),
            "ScopeKeywordSegment" => Some(&SCOPE_KEYWORD_SEGMENT),
            "TrailingKeywordSegment" => Some(&TRAILING_KEYWORD_SEGMENT),
            "Current_roleKeywordSegment" => Some(&CURRENT_ROLE_KEYWORD_SEGMENT),
            "ResultKeywordSegment" => Some(&RESULT_KEYWORD_SEGMENT),
            "Collation_schemaKeywordSegment" => Some(&COLLATION_SCHEMA_KEYWORD_SEGMENT),
            "HighKeywordSegment" => Some(&HIGH_KEYWORD_SEGMENT),
            "DeallocateKeywordSegment" => Some(&DEALLOCATE_KEYWORD_SEGMENT),
            "ProfileKeywordSegment" => Some(&PROFILE_KEYWORD_SEGMENT),
            "MapKeywordSegment" => Some(&MAP_KEYWORD_SEGMENT),
            "AuthorizationKeywordSegment" => Some(&AUTHORIZATION_KEYWORD_SEGMENT),
            "ImmediateKeywordSegment" => Some(&IMMEDIATE_KEYWORD_SEGMENT),
            "ReadKeywordSegment" => Some(&READ_KEYWORD_SEGMENT),
            "NullKeywordSegment" => Some(&NULL_KEYWORD_SEGMENT),
            "EnableKeywordSegment" => Some(&ENABLE_KEYWORD_SEGMENT),
            "ReferencesKeywordSegment" => Some(&REFERENCES_KEYWORD_SEGMENT),
            "InverseKeywordSegment" => Some(&INVERSE_KEYWORD_SEGMENT),
            "StyleKeywordSegment" => Some(&STYLE_KEYWORD_SEGMENT),
            "RefreshKeywordSegment" => Some(&REFRESH_KEYWORD_SEGMENT),
            "OrderKeywordSegment" => Some(&ORDER_KEYWORD_SEGMENT),
            "Sql_realKeywordSegment" => Some(&SQL_REAL_KEYWORD_SEGMENT),
            "DefinedKeywordSegment" => Some(&DEFINED_KEYWORD_SEGMENT),
            "ShortintKeywordSegment" => Some(&SHORTINT_KEYWORD_SEGMENT),
            "LeaveKeywordSegment" => Some(&LEAVE_KEYWORD_SEGMENT),
            "Current_userKeywordSegment" => Some(&CURRENT_USER_KEYWORD_SEGMENT),
            "PartitionKeywordSegment" => Some(&PARTITION_KEYWORD_SEGMENT),
            "CollateKeywordSegment" => Some(&COLLATE_KEYWORD_SEGMENT),
            "Timezone_hourKeywordSegment" => Some(&TIMEZONE_HOUR_KEYWORD_SEGMENT),
            "DlurlschemeKeywordSegment" => Some(&DLURLSCHEME_KEYWORD_SEGMENT),
            "GotoKeywordSegment" => Some(&GOTO_KEYWORD_SEGMENT),
            "ExceptKeywordSegment" => Some(&EXCEPT_KEYWORD_SEGMENT),
            "ControlKeywordSegment" => Some(&CONTROL_KEYWORD_SEGMENT),
            "AppendKeywordSegment" => Some(&APPEND_KEYWORD_SEGMENT),
            "UserKeywordSegment" => Some(&USER_KEYWORD_SEGMENT),
            "PartialKeywordSegment" => Some(&PARTIAL_KEYWORD_SEGMENT),
            "CatalogKeywordSegment" => Some(&CATALOG_KEYWORD_SEGMENT),
            "DeclareKeywordSegment" => Some(&DECLARE_KEYWORD_SEGMENT),
            "UnknownKeywordSegment" => Some(&UNKNOWN_KEYWORD_SEGMENT),
            "BinaryKeywordSegment" => Some(&BINARY_KEYWORD_SEGMENT),
            "WhenKeywordSegment" => Some(&WHEN_KEYWORD_SEGMENT),
            "TextKeywordSegment" => Some(&TEXT_KEYWORD_SEGMENT),
            "AssertionKeywordSegment" => Some(&ASSERTION_KEYWORD_SEGMENT),
            "ImplementationKeywordSegment" => Some(&IMPLEMENTATION_KEYWORD_SEGMENT),
            "RightKeywordSegment" => Some(&RIGHT_KEYWORD_SEGMENT),
            "SelfKeywordSegment" => Some(&SELF_KEYWORD_SEGMENT),
            "ElsifKeywordSegment" => Some(&ELSIF_KEYWORD_SEGMENT),
            "IndicatorKeywordSegment" => Some(&INDICATOR_KEYWORD_SEGMENT),
            "EndKeywordSegment" => Some(&END_KEYWORD_SEGMENT),
            "SpecificKeywordSegment" => Some(&SPECIFIC_KEYWORD_SEGMENT),
            "VarrayKeywordSegment" => Some(&VARRAY_KEYWORD_SEGMENT),
            "ModifyKeywordSegment" => Some(&MODIFY_KEYWORD_SEGMENT),
            "Sql_doubleKeywordSegment" => Some(&SQL_DOUBLE_KEYWORD_SEGMENT),
            "TrimKeywordSegment" => Some(&TRIM_KEYWORD_SEGMENT),
            "LastKeywordSegment" => Some(&LAST_KEYWORD_SEGMENT),
            "DataKeywordSegment" => Some(&DATA_KEYWORD_SEGMENT),
            "DayKeywordSegment" => Some(&DAY_KEYWORD_SEGMENT),
            "DecimalKeywordSegment" => Some(&DECIMAL_KEYWORD_SEGMENT),
            "FbvKeywordSegment" => Some(&FBV_KEYWORD_SEGMENT),
            "SessiontimezoneKeywordSegment" => Some(&SESSIONTIMEZONE_KEYWORD_SEGMENT),
            "ConnectionKeywordSegment" => Some(&CONNECTION_KEYWORD_SEGMENT),
            "LongvarcharKeywordSegment" => Some(&LONGVARCHAR_KEYWORD_SEGMENT),
            "PositionKeywordSegment" => Some(&POSITION_KEYWORD_SEGMENT),
            "StateKeywordSegment" => Some(&STATE_KEYWORD_SEGMENT),
            "OuterKeywordSegment" => Some(&OUTER_KEYWORD_SEGMENT),
            "WithinKeywordSegment" => Some(&WITHIN_KEYWORD_SEGMENT),
            "InsertKeywordSegment" => Some(&INSERT_KEYWORD_SEGMENT),
            "DisableKeywordSegment" => Some(&DISABLE_KEYWORD_SEGMENT),
            "SpecifictypeKeywordSegment" => Some(&SPECIFICTYPE_KEYWORD_SEGMENT),
            "CreateKeywordSegment" => Some(&CREATE_KEYWORD_SEGMENT),
            "CallKeywordSegment" => Some(&CALL_KEYWORD_SEGMENT),
            "ValueKeywordSegment" => Some(&VALUE_KEYWORD_SEGMENT),
            "IntervalKeywordSegment" => Some(&INTERVAL_KEYWORD_SEGMENT),
            "Sql_numericKeywordSegment" => Some(&SQL_NUMERIC_KEYWORD_SEGMENT),
            "Current_pathKeywordSegment" => Some(&CURRENT_PATH_KEYWORD_SEGMENT),
            "Sql_floatKeywordSegment" => Some(&SQL_FLOAT_KEYWORD_SEGMENT),
            "SmallintKeywordSegment" => Some(&SMALLINT_KEYWORD_SEGMENT),
            "ConstraintsKeywordSegment" => Some(&CONSTRAINTS_KEYWORD_SEGMENT),
            "InstantiableKeywordSegment" => Some(&INSTANTIABLE_KEYWORD_SEGMENT),
            "ColumnKeywordSegment" => Some(&COLUMN_KEYWORD_SEGMENT),
            "SourceKeywordSegment" => Some(&SOURCE_KEYWORD_SEGMENT),
            "WheneverKeywordSegment" => Some(&WHENEVER_KEYWORD_SEGMENT),
            "ElseifKeywordSegment" => Some(&ELSEIF_KEYWORD_SEGMENT),
            "ExtractKeywordSegment" => Some(&EXTRACT_KEYWORD_SEGMENT),
            "ConditionKeywordSegment" => Some(&CONDITION_KEYWORD_SEGMENT),
            "AllKeywordSegment" => Some(&ALL_KEYWORD_SEGMENT),
            "DoKeywordSegment" => Some(&DO_KEYWORD_SEGMENT),
            "ConstraintKeywordSegment" => Some(&CONSTRAINT_KEYWORD_SEGMENT),
            "SubtypeKeywordSegment" => Some(&SUBTYPE_KEYWORD_SEGMENT),
            "GetKeywordSegment" => Some(&GET_KEYWORD_SEGMENT),
            "LocaltimestampKeywordSegment" => Some(&LOCALTIMESTAMP_KEYWORD_SEGMENT),
            "InKeywordSegment" => Some(&IN_KEYWORD_SEGMENT),
            "ToKeywordSegment" => Some(&TO_KEYWORD_SEGMENT),
            "SqlstateKeywordSegment" => Some(&SQLSTATE_KEYWORD_SEGMENT),
            "DomainKeywordSegment" => Some(&DOMAIN_KEYWORD_SEGMENT),
            "DoubleKeywordSegment" => Some(&DOUBLE_KEYWORD_SEGMENT),
            "QualifyKeywordSegment" => Some(&QUALIFY_KEYWORD_SEGMENT),
            "BeginKeywordSegment" => Some(&BEGIN_KEYWORD_SEGMENT),
            "SqlexceptionKeywordSegment" => Some(&SQLEXCEPTION_KEYWORD_SEGMENT),
            "FoundKeywordSegment" => Some(&FOUND_KEYWORD_SEGMENT),
            "RealKeywordSegment" => Some(&REAL_KEYWORD_SEGMENT),
            "FetchKeywordSegment" => Some(&FETCH_KEYWORD_SEGMENT),
            "Current_timeKeywordSegment" => Some(&CURRENT_TIME_KEYWORD_SEGMENT),
            "Dynamic_functionKeywordSegment" => Some(&DYNAMIC_FUNCTION_KEYWORD_SEGMENT),
            "HoldKeywordSegment" => Some(&HOLD_KEYWORD_SEGMENT),
            "BoolKeywordSegment" => Some(&BOOL_KEYWORD_SEGMENT),
            "SpaceKeywordSegment" => Some(&SPACE_KEYWORD_SEGMENT),
            "GeometryKeywordSegment" => Some(&GEOMETRY_KEYWORD_SEGMENT),
            "RefKeywordSegment" => Some(&REF_KEYWORD_SEGMENT),
            "SystemKeywordSegment" => Some(&SYSTEM_KEYWORD_SEGMENT),
            "ValuesKeywordSegment" => Some(&VALUES_KEYWORD_SEGMENT),
            "ErrorsKeywordSegment" => Some(&ERRORS_KEYWORD_SEGMENT),
            "CheckKeywordSegment" => Some(&CHECK_KEYWORD_SEGMENT),
            "IterateKeywordSegment" => Some(&ITERATE_KEYWORD_SEGMENT),
            "Connect_by_isleafKeywordSegment" => Some(&CONNECT_BY_ISLEAF_KEYWORD_SEGMENT),
            "Nls_date_languageKeywordSegment" => Some(&NLS_DATE_LANGUAGE_KEYWORD_SEGMENT),
            "Sql_longvarcharKeywordSegment" => Some(&SQL_LONGVARCHAR_KEYWORD_SEGMENT),
            "GroupKeywordSegment" => Some(&GROUP_KEYWORD_SEGMENT),
            "InoutKeywordSegment" => Some(&INOUT_KEYWORD_SEGMENT),
            "LdapKeywordSegment" => Some(&LDAP_KEYWORD_SEGMENT),
            "NullifKeywordSegment" => Some(&NULLIF_KEYWORD_SEGMENT),
            "Sql_type_timestampKeywordSegment" => Some(&SQL_TYPE_TIMESTAMP_KEYWORD_SEGMENT),
            "CommitKeywordSegment" => Some(&COMMIT_KEYWORD_SEGMENT),
            "ScriptKeywordSegment" => Some(&SCRIPT_KEYWORD_SEGMENT),
            "AreKeywordSegment" => Some(&ARE_KEYWORD_SEGMENT),
            "NvarcharKeywordSegment" => Some(&NVARCHAR_KEYWORD_SEGMENT),
            "DecKeywordSegment" => Some(&DEC_KEYWORD_SEGMENT),
            "Sql_bitKeywordSegment" => Some(&SQL_BIT_KEYWORD_SEGMENT),
            "LocalKeywordSegment" => Some(&LOCAL_KEYWORD_SEGMENT),
            "CaseKeywordSegment" => Some(&CASE_KEYWORD_SEGMENT),
            "CycleKeywordSegment" => Some(&CYCLE_KEYWORD_SEGMENT),
            "InputKeywordSegment" => Some(&INPUT_KEYWORD_SEGMENT),
            "Group_concatKeywordSegment" => Some(&GROUP_CONCAT_KEYWORD_SEGMENT),
            "ContainsKeywordSegment" => Some(&CONTAINS_KEYWORD_SEGMENT),
            "GeneralKeywordSegment" => Some(&GENERAL_KEYWORD_SEGMENT),
            "Key_memberKeywordSegment" => Some(&KEY_MEMBER_KEYWORD_SEGMENT),
            "LateralKeywordSegment" => Some(&LATERAL_KEYWORD_SEGMENT),
            "DbtimezoneKeywordSegment" => Some(&DBTIMEZONE_KEYWORD_SEGMENT),
            "EscapeKeywordSegment" => Some(&ESCAPE_KEYWORD_SEGMENT),
            "FullKeywordSegment" => Some(&FULL_KEYWORD_SEGMENT),
            "RangeKeywordSegment" => Some(&RANGE_KEYWORD_SEGMENT),
            "ForceKeywordSegment" => Some(&FORCE_KEYWORD_SEGMENT),
            "PrepareKeywordSegment" => Some(&PREPARE_KEYWORD_SEGMENT),
            "ThenKeywordSegment" => Some(&THEN_KEYWORD_SEGMENT),
            "SeparatorKeywordSegment" => Some(&SEPARATOR_KEYWORD_SEGMENT),
            "TransformsKeywordSegment" => Some(&TRANSFORMS_KEYWORD_SEGMENT),
            "IsKeywordSegment" => Some(&IS_KEYWORD_SEGMENT),
            "HashtypeKeywordSegment" => Some(&HASHTYPE_KEYWORD_SEGMENT),
            "PathKeywordSegment" => Some(&PATH_KEYWORD_SEGMENT),
            "ArrayKeywordSegment" => Some(&ARRAY_KEYWORD_SEGMENT),
            "FromKeywordSegment" => Some(&FROM_KEYWORD_SEGMENT),
            "StaticKeywordSegment" => Some(&STATIC_KEYWORD_SEGMENT),
            "RowsKeywordSegment" => Some(&ROWS_KEYWORD_SEGMENT),
            "GoKeywordSegment" => Some(&GO_KEYWORD_SEGMENT),
            "YearKeywordSegment" => Some(&YEAR_KEYWORD_SEGMENT),
            "AlterKeywordSegment" => Some(&ALTER_KEYWORD_SEGMENT),
            "ExportKeywordSegment" => Some(&EXPORT_KEYWORD_SEGMENT),
            "UnlinkKeywordSegment" => Some(&UNLINK_KEYWORD_SEGMENT),
            "AllocateKeywordSegment" => Some(&ALLOCATE_KEYWORD_SEGMENT),
            "Nls_date_formatKeywordSegment" => Some(&NLS_DATE_FORMAT_KEYWORD_SEGMENT),
            "Current_sessionKeywordSegment" => Some(&CURRENT_SESSION_KEYWORD_SEGMENT),
            "VerifyKeywordSegment" => Some(&VERIFY_KEYWORD_SEGMENT),
            "ConvertKeywordSegment" => Some(&CONVERT_KEYWORD_SEGMENT),
            "OpenKeywordSegment" => Some(&OPEN_KEYWORD_SEGMENT),
            "CloseKeywordSegment" => Some(&CLOSE_KEYWORD_SEGMENT),
            "Datetime_interval_precisionKeywordSegment" => Some(&DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT),
            "Constraint_state_defaultKeywordSegment" => Some(&CONSTRAINT_STATE_DEFAULT_KEYWORD_SEGMENT),
            "IndexKeywordSegment" => Some(&INDEX_KEYWORD_SEGMENT),
            "PrivilegesKeywordSegment" => Some(&PRIVILEGES_KEYWORD_SEGMENT),
            "ScrollKeywordSegment" => Some(&SCROLL_KEYWORD_SEGMENT),
            "Parallel_enableKeywordSegment" => Some(&PARALLEL_ENABLE_KEYWORD_SEGMENT),
            "Regexp_likeKeywordSegment" => Some(&REGEXP_LIKE_KEYWORD_SEGMENT),
            "PlacingKeywordSegment" => Some(&PLACING_KEYWORD_SEGMENT),
            "CollationKeywordSegment" => Some(&COLLATION_KEYWORD_SEGMENT),
            "ElseKeywordSegment" => Some(&ELSE_KEYWORD_SEGMENT),
            "EachKeywordSegment" => Some(&EACH_KEYWORD_SEGMENT),
            "Parameter_specific_schemaKeywordSegment" => Some(&PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT),
            "NcharKeywordSegment" => Some(&NCHAR_KEYWORD_SEGMENT),
            "Dynamic_function_codeKeywordSegment" => Some(&DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT),
            "CastKeywordSegment" => Some(&CAST_KEYWORD_SEGMENT),
            "CoalesceKeywordSegment" => Some(&COALESCE_KEYWORD_SEGMENT),
            "ZoneKeywordSegment" => Some(&ZONE_KEYWORD_SEGMENT),
            "SomeKeywordSegment" => Some(&SOME_KEYWORD_SEGMENT),
            "WorkKeywordSegment" => Some(&WORK_KEYWORD_SEGMENT),
            "UnionKeywordSegment" => Some(&UNION_KEYWORD_SEGMENT),
            "ModuleKeywordSegment" => Some(&MODULE_KEYWORD_SEGMENT),
            "SetKeywordSegment" => Some(&SET_KEYWORD_SEGMENT),
            "Nls_first_day_of_weekKeywordSegment" => Some(&NLS_FIRST_DAY_OF_WEEK_KEYWORD_SEGMENT),
            "SystimestampKeywordSegment" => Some(&SYSTIMESTAMP_KEYWORD_SEGMENT),
            "LikeKeywordSegment" => Some(&LIKE_KEYWORD_SEGMENT),
            "EqualsKeywordSegment" => Some(&EQUALS_KEYWORD_SEGMENT),
            "PlusKeywordSegment" => Some(&PLUS_KEYWORD_SEGMENT),
            "StartKeywordSegment" => Some(&START_KEYWORD_SEGMENT),
            "MatchedKeywordSegment" => Some(&MATCHED_KEYWORD_SEGMENT),
            "MergeKeywordSegment" => Some(&MERGE_KEYWORD_SEGMENT),
            "RollupKeywordSegment" => Some(&ROLLUP_KEYWORD_SEGMENT),
            "CorrespondingKeywordSegment" => Some(&CORRESPONDING_KEYWORD_SEGMENT),
            "EndifKeywordSegment" => Some(&ENDIF_KEYWORD_SEGMENT),
            "BlobKeywordSegment" => Some(&BLOB_KEYWORD_SEGMENT),
            "CsKeywordSegment" => Some(&CS_KEYWORD_SEGMENT),
            "Hashtype_formatKeywordSegment" => Some(&HASHTYPE_FORMAT_KEYWORD_SEGMENT),
            "AscKeywordSegment" => Some(&ASC_KEYWORD_SEGMENT),
            "NextKeywordSegment" => Some(&NEXT_KEYWORD_SEGMENT),
            "PermissionKeywordSegment" => Some(&PERMISSION_KEYWORD_SEGMENT),
            "AddKeywordSegment" => Some(&ADD_KEYWORD_SEGMENT),
            "ConstructorKeywordSegment" => Some(&CONSTRUCTOR_KEYWORD_SEGMENT),
            "DlurlcompleteKeywordSegment" => Some(&DLURLCOMPLETE_KEYWORD_SEGMENT),
            "IntegerKeywordSegment" => Some(&INTEGER_KEYWORD_SEGMENT),
            "LeftKeywordSegment" => Some(&LEFT_KEYWORD_SEGMENT),
            "HourKeywordSegment" => Some(&HOUR_KEYWORD_SEGMENT),
            "TimestampKeywordSegment" => Some(&TIMESTAMP_KEYWORD_SEGMENT),
            "FunctionKeywordSegment" => Some(&FUNCTION_KEYWORD_SEGMENT),
            "CharacteristicsKeywordSegment" => Some(&CHARACTERISTICS_KEYWORD_SEGMENT),
            "Connect_by_iscycleKeywordSegment" => Some(&CONNECT_BY_ISCYCLE_KEYWORD_SEGMENT),
            "CursorKeywordSegment" => Some(&CURSOR_KEYWORD_SEGMENT),
            "ExecKeywordSegment" => Some(&EXEC_KEYWORD_SEGMENT),
            "VarcharKeywordSegment" => Some(&VARCHAR_KEYWORD_SEGMENT),
            "PreserveKeywordSegment" => Some(&PRESERVE_KEYWORD_SEGMENT),
            "AbsoluteKeywordSegment" => Some(&ABSOLUTE_KEYWORD_SEGMENT),
            "GeneratedKeywordSegment" => Some(&GENERATED_KEYWORD_SEGMENT),
            "RenameKeywordSegment" => Some(&RENAME_KEYWORD_SEGMENT),
            "OverlapsKeywordSegment" => Some(&OVERLAPS_KEYWORD_SEGMENT),
            "SectionKeywordSegment" => Some(&SECTION_KEYWORD_SEGMENT),
            "CsvKeywordSegment" => Some(&CSV_KEYWORD_SEGMENT),
            "TransformKeywordSegment" => Some(&TRANSFORM_KEYWORD_SEGMENT),
            "OptionsKeywordSegment" => Some(&OPTIONS_KEYWORD_SEGMENT),
            "JoinKeywordSegment" => Some(&JOIN_KEYWORD_SEGMENT),
            "NoneKeywordSegment" => Some(&NONE_KEYWORD_SEGMENT),
            "Scope_userKeywordSegment" => Some(&SCOPE_USER_KEYWORD_SEGMENT),
            "Session_userKeywordSegment" => Some(&SESSION_USER_KEYWORD_SEGMENT),
            "EmitsKeywordSegment" => Some(&EMITS_KEYWORD_SEGMENT),
            "CharacterKeywordSegment" => Some(&CHARACTER_KEYWORD_SEGMENT),
            "ByteKeywordSegment" => Some(&BYTE_KEYWORD_SEGMENT),
            "ExecuteKeywordSegment" => Some(&EXECUTE_KEYWORD_SEGMENT),
            "Sql_integerKeywordSegment" => Some(&SQL_INTEGER_KEYWORD_SEGMENT),
            "AsensitiveKeywordSegment" => Some(&ASENSITIVE_KEYWORD_SEGMENT),
            "Character_set_catalogKeywordSegment" => Some(&CHARACTER_SET_CATALOG_KEYWORD_SEGMENT),
            "IfKeywordSegment" => Some(&IF_KEYWORD_SEGMENT),
            "ReferencingKeywordSegment" => Some(&REFERENCING_KEYWORD_SEGMENT),
            "RoutineKeywordSegment" => Some(&ROUTINE_KEYWORD_SEGMENT),
            "RevokeKeywordSegment" => Some(&REVOKE_KEYWORD_SEGMENT),
            "Collation_catalogKeywordSegment" => Some(&COLLATION_CATALOG_KEYWORD_SEGMENT),
            "SensitiveKeywordSegment" => Some(&SENSITIVE_KEYWORD_SEGMENT),
            "ContinueKeywordSegment" => Some(&CONTINUE_KEYWORD_SEGMENT),
            "CascadedKeywordSegment" => Some(&CASCADED_KEYWORD_SEGMENT),
            "LimitKeywordSegment" => Some(&LIMIT_KEYWORD_SEGMENT),
            "BooleanKeywordSegment" => Some(&BOOLEAN_KEYWORD_SEGMENT),
            "AsKeywordSegment" => Some(&AS_KEYWORD_SEGMENT),
            "CasespecificKeywordSegment" => Some(&CASESPECIFIC_KEYWORD_SEGMENT),
            "Datetime_interval_codeKeywordSegment" => Some(&DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT),
            "FollowingKeywordSegment" => Some(&FOLLOWING_KEYWORD_SEGMENT),
            "RestrictKeywordSegment" => Some(&RESTRICT_KEYWORD_SEGMENT),
            "RowtypeKeywordSegment" => Some(&ROWTYPE_KEYWORD_SEGMENT),
            "Nls_numeric_charactersKeywordSegment" => Some(&NLS_NUMERIC_CHARACTERS_KEYWORD_SEGMENT),
            "GlobalKeywordSegment" => Some(&GLOBAL_KEYWORD_SEGMENT),
            "NotKeywordSegment" => Some(&NOT_KEYWORD_SEGMENT),
            "PriorKeywordSegment" => Some(&PRIOR_KEYWORD_SEGMENT),
            "WhileKeywordSegment" => Some(&WHILE_KEYWORD_SEGMENT),
            "IfnullKeywordSegment" => Some(&IFNULL_KEYWORD_SEGMENT),
            "OutputKeywordSegment" => Some(&OUTPUT_KEYWORD_SEGMENT),
            "DlurlpathonlyKeywordSegment" => Some(&DLURLPATHONLY_KEYWORD_SEGMENT),
            "CubeKeywordSegment" => Some(&CUBE_KEYWORD_SEGMENT),
            "ImportKeywordSegment" => Some(&IMPORT_KEYWORD_SEGMENT),
            "DateKeywordSegment" => Some(&DATE_KEYWORD_SEGMENT),
            "Current_dateKeywordSegment" => Some(&CURRENT_DATE_KEYWORD_SEGMENT),
            "DescKeywordSegment" => Some(&DESC_KEYWORD_SEGMENT),
            "NologgingKeywordSegment" => Some(&NOLOGGING_KEYWORD_SEGMENT),
            "Key_typeKeywordSegment" => Some(&KEY_TYPE_KEYWORD_SEGMENT),
            "UntilKeywordSegment" => Some(&UNTIL_KEYWORD_SEGMENT),
            "BetweenKeywordSegment" => Some(&BETWEEN_KEYWORD_SEGMENT),
            "ForKeywordSegment" => Some(&FOR_KEYWORD_SEGMENT),
            "OverridingKeywordSegment" => Some(&OVERRIDING_KEYWORD_SEGMENT),
            "DerivedKeywordSegment" => Some(&DERIVED_KEYWORD_SEGMENT),
            "SelectiveKeywordSegment" => Some(&SELECTIVE_KEYWORD_SEGMENT),
            "End-execKeywordSegment" => Some(&END_EXEC_KEYWORD_SEGMENT),
            "ReplaceKeywordSegment" => Some(&REPLACE_KEYWORD_SEGMENT),
            "SubstringKeywordSegment" => Some(&SUBSTRING_KEYWORD_SEGMENT),
            "AtKeywordSegment" => Some(&AT_KEYWORD_SEGMENT),
            "Sql_varcharKeywordSegment" => Some(&SQL_VARCHAR_KEYWORD_SEGMENT),
            "DescribeKeywordSegment" => Some(&DESCRIBE_KEYWORD_SEGMENT),
            "ProcedureKeywordSegment" => Some(&PROCEDURE_KEYWORD_SEGMENT),
            "WhereKeywordSegment" => Some(&WHERE_KEYWORD_SEGMENT),
            "SqlKeywordSegment" => Some(&SQL_KEYWORD_SEGMENT),
            "LargeKeywordSegment" => Some(&LARGE_KEYWORD_SEGMENT),
            "EnforceKeywordSegment" => Some(&ENFORCE_KEYWORD_SEGMENT),
            "Varchar2KeywordSegment" => Some(&VARCHAR2_KEYWORD_SEGMENT),
            "OverKeywordSegment" => Some(&OVER_KEYWORD_SEGMENT),
            "SqlwarningKeywordSegment" => Some(&SQLWARNING_KEYWORD_SEGMENT),
            "SavepointKeywordSegment" => Some(&SAVEPOINT_KEYWORD_SEGMENT),
            "OutKeywordSegment" => Some(&OUT_KEYWORD_SEGMENT),
            "ModKeywordSegment" => Some(&MOD_KEYWORD_SEGMENT),
            "Sql_smallintKeywordSegment" => Some(&SQL_SMALLINT_KEYWORD_SEGMENT),
            "OfKeywordSegment" => Some(&OF_KEYWORD_SEGMENT),
            "AfterKeywordSegment" => Some(&AFTER_KEYWORD_SEGMENT),
            "CascadeKeywordSegment" => Some(&CASCADE_KEYWORD_SEGMENT),
            "InsensitiveKeywordSegment" => Some(&INSENSITIVE_KEYWORD_SEGMENT),
            "RowKeywordSegment" => Some(&ROW_KEYWORD_SEGMENT),
            "DefinerKeywordSegment" => Some(&DEFINER_KEYWORD_SEGMENT),
            "UsingKeywordSegment" => Some(&USING_KEYWORD_SEGMENT),
            "ParameterKeywordSegment" => Some(&PARAMETER_KEYWORD_SEGMENT),
            "LowKeywordSegment" => Some(&LOW_KEYWORD_SEGMENT),
            "NumberKeywordSegment" => Some(&NUMBER_KEYWORD_SEGMENT),
            "PadKeywordSegment" => Some(&PAD_KEYWORD_SEGMENT),
            "TransactionKeywordSegment" => Some(&TRANSACTION_KEYWORD_SEGMENT),
            "DeterministicKeywordSegment" => Some(&DETERMINISTIC_KEYWORD_SEGMENT),
            "GroupingKeywordSegment" => Some(&GROUPING_KEYWORD_SEGMENT),
            "Sql_dateKeywordSegment" => Some(&SQL_DATE_KEYWORD_SEGMENT),
            "DeferredKeywordSegment" => Some(&DEFERRED_KEYWORD_SEGMENT),
            "UniqueKeywordSegment" => Some(&UNIQUE_KEYWORD_SEGMENT),
            "NocycleKeywordSegment" => Some(&NOCYCLE_KEYWORD_SEGMENT),
            "Sql_bigintKeywordSegment" => Some(&SQL_BIGINT_KEYWORD_SEGMENT),
            "FalseKeywordSegment" => Some(&FALSE_KEYWORD_SEGMENT),
            "DeleteKeywordSegment" => Some(&DELETE_KEYWORD_SEGMENT),
            "FormatKeywordSegment" => Some(&FORMAT_KEYWORD_SEGMENT),
            "SysdateKeywordSegment" => Some(&SYSDATE_KEYWORD_SEGMENT),
            "FirstKeywordSegment" => Some(&FIRST_KEYWORD_SEGMENT),
            "TreatKeywordSegment" => Some(&TREAT_KEYWORD_SEGMENT),
            "OldKeywordSegment" => Some(&OLD_KEYWORD_SEGMENT),
            "ExceptionKeywordSegment" => Some(&EXCEPTION_KEYWORD_SEGMENT),
            "MatchKeywordSegment" => Some(&MATCH_KEYWORD_SEGMENT),
            "ExitKeywordSegment" => Some(&EXIT_KEYWORD_SEGMENT),
            "ModifiesKeywordSegment" => Some(&MODIFIES_KEYWORD_SEGMENT),
            "OnlyKeywordSegment" => Some(&ONLY_KEYWORD_SEGMENT),
            "Timezone_minuteKeywordSegment" => Some(&TIMEZONE_MINUTE_KEYWORD_SEGMENT),
            "AndKeywordSegment" => Some(&AND_KEYWORD_SEGMENT),
            "System_userKeywordSegment" => Some(&SYSTEM_USER_KEYWORD_SEGMENT),
            "DisconnectKeywordSegment" => Some(&DISCONNECT_KEYWORD_SEGMENT),
            "CrossKeywordSegment" => Some(&CROSS_KEYWORD_SEGMENT),
            "DisabledKeywordSegment" => Some(&DISABLED_KEYWORD_SEGMENT),
            "RecoveryKeywordSegment" => Some(&RECOVERY_KEYWORD_SEGMENT),
            "HavingKeywordSegment" => Some(&HAVING_KEYWORD_SEGMENT),
            "RestoreKeywordSegment" => Some(&RESTORE_KEYWORD_SEGMENT),
            "NamesKeywordSegment" => Some(&NAMES_KEYWORD_SEGMENT),
            "Parameter_specific_catalogKeywordSegment" => Some(&PARAMETER_SPECIFIC_CATALOG_KEYWORD_SEGMENT),
            "RecursiveKeywordSegment" => Some(&RECURSIVE_KEYWORD_SEGMENT),
            "WindowKeywordSegment" => Some(&WINDOW_KEYWORD_SEGMENT),
            "OptionKeywordSegment" => Some(&OPTION_KEYWORD_SEGMENT),
            "TranslationKeywordSegment" => Some(&TRANSLATION_KEYWORD_SEGMENT),
            "BothKeywordSegment" => Some(&BOTH_KEYWORD_SEGMENT),
            "Returned_octet_lengthKeywordSegment" => Some(&RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT),
            "FsKeywordSegment" => Some(&FS_KEYWORD_SEGMENT),
            _ => None,
    }
}
