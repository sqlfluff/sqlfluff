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
Grammar::OneOf {
    elements: vec![
Grammar::TypedParser()
,
Grammar::Ref {
    name: "ParameterizedSegment",
    optional: false,
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
    name: "SingleQuotedIdentifierSegment",
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
    name: "BackQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Sequence {
    elements: vec![
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
    name: "DatetimeKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Nothing()
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
Grammar::Ref {
    name: "ParameterizedSegment",
    optional: false,
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
Grammar::Nothing()
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
Grammar::Ref {
    name: "ColumnPathOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InlinePathOperatorSegment",
    optional: false,
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
Grammar::Ref {
    name: "TemporaryGrammar",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GlobKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RegexpKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MatchKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "WindowKeywordSegment",
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
    name: "WithNoSchemaBindingClauseSegment",
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
    name: "WindowKeywordSegment",
    optional: false,
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
    name: "WindowKeywordSegment",
    optional: false,
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
    name: "LimitKeywordSegment",
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
Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AutoincrementKeywordSegment",
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
Grammar::Nothing()
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
Grammar::Nothing()
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
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
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
Grammar::Nothing()
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
    name: "RenameKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
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
    ],
    optional: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
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
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnKeywordSegment",
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
Grammar::Nothing()
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
    name: "OrderByClauseSegment",
    optional: false,
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
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailKeywordSegment",
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
    name: "CommaSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FilterClauseGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverClauseSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
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
    name: "RoleKeywordSegment",
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
    name: "WarehouseKeywordSegment",
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
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
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
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "PipeKeywordSegment",
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
    name: "StageKeywordSegment",
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
Grammar::Ref {
    name: "RoutineKeywordSegment",
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
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
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
Grammar::Ref {
    name: "ExternalKeywordSegment",
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
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ApplyKeywordSegment",
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
    name: "CreateKeywordSegment",
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
    name: "ExecuteKeywordSegment",
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
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Reference_usageKeywordSegment",
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
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Ref {
    name: "TriggerKeywordSegment",
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
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
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
    ],
    optional: false,
    terminators: vec![
    ],
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AccountKeywordSegment",
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
    name: "ResourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "WarehouseKeywordSegment",
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
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LanguageKeywordSegment",
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
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TablespaceKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
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
    name: "StageKeywordSegment",
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
Grammar::Ref {
    name: "RoutineKeywordSegment",
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
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
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
Grammar::Ref {
    name: "ExternalKeywordSegment",
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
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "DatabaseKeywordSegment",
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WildcardIdentifierSegment",
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
    name: "RoleKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OwnershipKeywordSegment",
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
    name: "UserKeywordSegment",
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
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
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
    name: "ShareKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RoleReferenceSegment",
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
    name: "PublicKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CopyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantedKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Current_userKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Session_userKeywordSegment",
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
    name: "RevokeKeywordSegment",
    optional: false,
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
    name: "OptionKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
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
    name: "RoleKeywordSegment",
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
    name: "WarehouseKeywordSegment",
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
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
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
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "PipeKeywordSegment",
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
    name: "StageKeywordSegment",
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
Grammar::Ref {
    name: "RoutineKeywordSegment",
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
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
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
Grammar::Ref {
    name: "ExternalKeywordSegment",
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
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ApplyKeywordSegment",
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
    name: "CreateKeywordSegment",
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
    name: "ExecuteKeywordSegment",
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
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Reference_usageKeywordSegment",
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
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Ref {
    name: "TriggerKeywordSegment",
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
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
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
    ],
    optional: false,
    terminators: vec![
    ],
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AccountKeywordSegment",
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
    name: "ResourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "WarehouseKeywordSegment",
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
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LanguageKeywordSegment",
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
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TablespaceKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
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
    name: "StageKeywordSegment",
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
Grammar::Ref {
    name: "RoutineKeywordSegment",
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
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
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
Grammar::Ref {
    name: "ExternalKeywordSegment",
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
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "DatabaseKeywordSegment",
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WildcardIdentifierSegment",
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
    name: "RoleKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OwnershipKeywordSegment",
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
    name: "UserKeywordSegment",
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
    name: "GroupKeywordSegment",
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
    name: "ShareKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "AlterTableOptionsGrammar",
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
    name: "LiteralGrammar",
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
Grammar::Ref {
    name: "ConflictClauseSegment",
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
    name: "CheckKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnConstraintDefaultGrammar",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConflictClauseSegment",
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
    name: "AutoIncrementGrammar",
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
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CollateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CollationReferenceSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GeneratedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlwaysKeywordSegment",
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
    name: "AsKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "StoredKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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

// name='ColumnDefinitionSegment'
pub static COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::Bracketed {
    elements: vec![
// Missing elements match_grammar=<Anything: []>, type:<class 'sqlfluff.core.parser.grammar.base.Anything'>
todo!()
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnConstraintSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
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
    ],
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
Grammar::Nothing()
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
    name: "TemporaryGrammar",
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
    name: "IfNotExistsGrammar",
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
    name: "FunctionParameterListGrammar",
    optional: false,
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
Grammar::Ref {
    name: "DatatypeSegment",
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
    name: "FunctionDefinitionGrammar",
    optional: false,
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
    name: "IfNotExistsGrammar",
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
    name: "TemporaryTransientGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
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
    name: "TableEndClauseSegment",
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
    name: "TemporaryGrammar",
    optional: true,
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
    name: "IfNotExistsGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DeleteKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
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
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EachKeywordSegment",
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
    optional: true,
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OptionallyBracketed()
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
    name: "BeginKeywordSegment",
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
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
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
    ),
    allow_trailing: true,
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
    name: "TemporaryGrammar",
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
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
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
Grammar::Ref {
    name: "DoubleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecisionKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "UnsignedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BigKeywordSegment",
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
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NativeKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NativeKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "DatatypeIdentifierSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UnsignedKeywordSegment",
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
    name: "FromClauseSegment",
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
Grammar::Ref {
    name: "ReturningClauseSegment",
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
    name: "TemporaryGrammar",
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
    name: "IfExistsGrammar",
    optional: true,
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
Grammar::Nothing()
);

// name='FileSegment'
pub static FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    delimiter: Box::new(
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "ExpressionSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "UnboundedKeywordSegment",
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
Grammar::Ref {
    name: "ExpressionSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ExcludeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OthersKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "TiesKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
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
    name: "CubeRollupClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Nothing()
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IgnoreKeywordSegment",
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
,
Grammar::Ref {
    name: "IntoKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpsertClauseSegment",
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
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "UpsertClauseSegment",
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
    name: "DefaultValuesGrammar",
    optional: false,
    allow_gaps: true,
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
    name: "ReturningClauseSegment",
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

// name='IntervalExpressionSegment'
pub static INTERVAL_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OptionallyBracketed()
,
Grammar::OneOf {
    elements: vec![
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
    ],
    optional: true,
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
Grammar::Nothing()
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
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='MergeMatchSegment'
pub static MERGE_MATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "MergeMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeNotMatchedClauseSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
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
Grammar::Ref {
    name: "ThenKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
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
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "MergeInsertClauseSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "SetClauseListSegment",
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
Grammar::Nothing()
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
Grammar::Nothing()
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
    name: "WhereClauseSegment",
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
    name: "OverlapsClauseSegment",
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
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchClauseSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
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
Grammar::Ref {
    name: "EqualsSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IntersectKeywordSegment",
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
    name: "AlterTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateIndexStatementSegment",
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
    name: "CreateVirtualTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTriggerStatementSegment",
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
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropIndexStatementSegment",
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
    name: "DropTriggerStatementSegment",
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
    name: "ExplainStatementSegment",
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
    name: "PragmaStatementSegment",
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
    name: "TransactionStatementSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "StatementSegment",
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
    name: "CheckKeywordSegment",
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
Grammar::Ref {
    name: "ConflictClauseSegment",
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
Grammar::Ref {
    name: "ConflictClauseSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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

// name='TableEndClauseSegment'
pub static TABLE_END_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithoutKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowidKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "StrictKeywordSegment",
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

// name='TableExpressionSegment'
pub static TABLE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ValuesClauseSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "MergeStatementSegment",
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
Grammar::Sequence {
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnPathOperatorSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InlinePathOperatorSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Nothing()
);

// name='TransactionStatementSegment'
pub static TRANSACTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TransactionKeywordSegment",
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
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SavepointKeywordSegment",
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
    name: "WhereClauseSegment",
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
    name: "OverlapsClauseSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IgnoreKeywordSegment",
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
Grammar::Ref {
    name: "TableReferenceSegment",
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
    name: "ReturningClauseSegment",
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
Grammar::Sequence {
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

// name='BackQuotedIdentifierSegment'
pub static BACK_QUOTED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='ColumnPathOperatorSegment'
pub static COLUMN_PATH_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InlinePathOperatorSegment'
pub static INLINE_PATH_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QuestionMarkSegment'
pub static QUESTION_MARK_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtSignLiteralSegment'
pub static AT_SIGN_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='ColonLiteralSegment'
pub static COLON_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='QuestionLiteralSegment'
pub static QUESTION_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='DollarLiteralSegment'
pub static DOLLAR_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='ConflictClauseSegment'
pub static CONFLICT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConflictKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IgnoreKeywordSegment",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConflictTargetSegment'
pub static CONFLICT_TARGET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
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

// name='CreateVirtualTableStatementSegment'
pub static CREATE_VIRTUAL_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::Ref {
    name: "UsingKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
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
    name: "NumericLiteralSegment",
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
);

// name='ParameterizedSegment'
pub static PARAMETERIZED_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AtSignLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuestionMarkSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColonLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuestionLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DollarLiteralSegment",
    optional: false,
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

// name='PragmaReferenceSegment'
pub static PRAGMA_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
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

// name='PragmaStatementSegment'
pub static PRAGMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PragmaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PragmaReferenceSegment",
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
Grammar::Ref {
    name: "LiteralGrammar",
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
    name: "YesKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IncrementalKeywordSegment",
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
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PersistKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MemoryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NormalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExclusiveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExtraKeywordSegment",
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
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PassiveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RestartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ResetKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
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

// name='ReturningClauseSegment'
pub static RETURNING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReturningKeywordSegment",
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
    name: "WildcardExpressionSegment",
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

// name='UpsertClauseSegment'
pub static UPSERT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConflictKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConflictTargetSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NothingKeywordSegment",
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
Grammar::Ref {
    name: "EqualsSegment",
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

// name='StoredKeywordSegment'
pub static STORED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MediumintKeywordSegment'
pub static MEDIUMINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClobKeywordSegment'
pub static CLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SmallintKeywordSegment'
pub static SMALLINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BooleanKeywordSegment'
pub static BOOLEAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharacterKeywordSegment'
pub static CHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestartKeywordSegment'
pub static RESTART_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowidKeywordSegment'
pub static ROWID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MemoryKeywordSegment'
pub static MEMORY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NvarcharKeywordSegment'
pub static NVARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExtraKeywordSegment'
pub static EXTRA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NcharKeywordSegment'
pub static NCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegerKeywordSegment'
pub static INTEGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BigKeywordSegment'
pub static BIG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarcharKeywordSegment'
pub static VARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NormalKeywordSegment'
pub static NORMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TinyintKeywordSegment'
pub static TINYINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NativeKeywordSegment'
pub static NATIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FloatKeywordSegment'
pub static FLOAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PassiveKeywordSegment'
pub static PASSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StrictKeywordSegment'
pub static STRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnsignedKeywordSegment'
pub static UNSIGNED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WalKeywordSegment'
pub static WAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BigintKeywordSegment'
pub static BIGINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumericKeywordSegment'
pub static NUMERIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntKeywordSegment'
pub static INT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RealKeywordSegment'
pub static REAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatetimeKeywordSegment'
pub static DATETIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int8KeywordSegment'
pub static INT8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int2KeywordSegment'
pub static INT2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FastKeywordSegment'
pub static FAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocaseKeywordSegment'
pub static NOCASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecimalKeywordSegment'
pub static DECIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PersistKeywordSegment'
pub static PERSIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TextKeywordSegment'
pub static TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YesKeywordSegment'
pub static YES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RtrimKeywordSegment'
pub static RTRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncrementalKeywordSegment'
pub static INCREMENTAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResetKeywordSegment'
pub static RESET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlobKeywordSegment'
pub static BLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlanKeywordSegment'
pub static PLAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupsKeywordSegment'
pub static GROUPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QueryKeywordSegment'
pub static QUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RaiseKeywordSegment'
pub static RAISE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnalyzeKeywordSegment'
pub static ANALYZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilterKeywordSegment'
pub static FILTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SavepointKeywordSegment'
pub static SAVEPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchKeywordSegment'
pub static MATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LimitKeywordSegment'
pub static LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndexedKeywordSegment'
pub static INDEXED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferrableKeywordSegment'
pub static DEFERRABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbortKeywordSegment'
pub static ABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConflictKeywordSegment'
pub static CONFLICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TempKeywordSegment'
pub static TEMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReleaseKeywordSegment'
pub static RELEASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsnullKeywordSegment'
pub static ISNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FailKeywordSegment'
pub static FAIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReindexKeywordSegment'
pub static REINDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotnullKeywordSegment'
pub static NOTNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NothingKeywordSegment'
pub static NOTHING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GlobKeywordSegment'
pub static GLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VirtualKeywordSegment'
pub static VIRTUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExcludeKeywordSegment'
pub static EXCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PragmaKeywordSegment'
pub static PRAGMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferredKeywordSegment'
pub static DEFERRED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoKeywordSegment'
pub static DO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AutoincrementKeywordSegment'
pub static AUTOINCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VacuumKeywordSegment'
pub static VACUUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TemporaryKeywordSegment'
pub static TEMPORARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExclusiveKeywordSegment'
pub static EXCLUSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OthersKeywordSegment'
pub static OTHERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EachKeywordSegment'
pub static EACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitiallyKeywordSegment'
pub static INITIALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaterializedKeywordSegment'
pub static MATERIALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RegexpKeywordSegment'
pub static REGEXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsteadKeywordSegment'
pub static INSTEAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturningKeywordSegment'
pub static RETURNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NaturalKeywordSegment'
pub static NATURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DetachKeywordSegment'
pub static DETACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImmediateKeywordSegment'
pub static IMMEDIATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttachKeywordSegment'
pub static ATTACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

pub fn get_sqlite_segment_grammar(name: &str) -> Option<&'static Grammar> {
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
            "BackQuotedIdentifierSegment" => Some(&BACK_QUOTED_IDENTIFIER_SEGMENT),
            "ColumnPathOperatorSegment" => Some(&COLUMN_PATH_OPERATOR_SEGMENT),
            "InlinePathOperatorSegment" => Some(&INLINE_PATH_OPERATOR_SEGMENT),
            "QuestionMarkSegment" => Some(&QUESTION_MARK_SEGMENT),
            "AtSignLiteralSegment" => Some(&AT_SIGN_LITERAL_SEGMENT),
            "ColonLiteralSegment" => Some(&COLON_LITERAL_SEGMENT),
            "QuestionLiteralSegment" => Some(&QUESTION_LITERAL_SEGMENT),
            "DollarLiteralSegment" => Some(&DOLLAR_LITERAL_SEGMENT),
            "ConflictClauseSegment" => Some(&CONFLICT_CLAUSE_SEGMENT),
            "ConflictTargetSegment" => Some(&CONFLICT_TARGET_SEGMENT),
            "CreateVirtualTableStatementSegment" => Some(&CREATE_VIRTUAL_TABLE_STATEMENT_SEGMENT),
            "ParameterizedSegment" => Some(&PARAMETERIZED_SEGMENT),
            "PragmaReferenceSegment" => Some(&PRAGMA_REFERENCE_SEGMENT),
            "PragmaStatementSegment" => Some(&PRAGMA_STATEMENT_SEGMENT),
            "ReturningClauseSegment" => Some(&RETURNING_CLAUSE_SEGMENT),
            "UpsertClauseSegment" => Some(&UPSERT_CLAUSE_SEGMENT),
            "StoredKeywordSegment" => Some(&STORED_KEYWORD_SEGMENT),
            "MediumintKeywordSegment" => Some(&MEDIUMINT_KEYWORD_SEGMENT),
            "ClobKeywordSegment" => Some(&CLOB_KEYWORD_SEGMENT),
            "SmallintKeywordSegment" => Some(&SMALLINT_KEYWORD_SEGMENT),
            "BooleanKeywordSegment" => Some(&BOOLEAN_KEYWORD_SEGMENT),
            "CharacterKeywordSegment" => Some(&CHARACTER_KEYWORD_SEGMENT),
            "RestartKeywordSegment" => Some(&RESTART_KEYWORD_SEGMENT),
            "OffKeywordSegment" => Some(&OFF_KEYWORD_SEGMENT),
            "RowidKeywordSegment" => Some(&ROWID_KEYWORD_SEGMENT),
            "MemoryKeywordSegment" => Some(&MEMORY_KEYWORD_SEGMENT),
            "NvarcharKeywordSegment" => Some(&NVARCHAR_KEYWORD_SEGMENT),
            "ExtraKeywordSegment" => Some(&EXTRA_KEYWORD_SEGMENT),
            "NcharKeywordSegment" => Some(&NCHAR_KEYWORD_SEGMENT),
            "ActionKeywordSegment" => Some(&ACTION_KEYWORD_SEGMENT),
            "KeyKeywordSegment" => Some(&KEY_KEYWORD_SEGMENT),
            "IntegerKeywordSegment" => Some(&INTEGER_KEYWORD_SEGMENT),
            "BigKeywordSegment" => Some(&BIG_KEYWORD_SEGMENT),
            "NoneKeywordSegment" => Some(&NONE_KEYWORD_SEGMENT),
            "VarcharKeywordSegment" => Some(&VARCHAR_KEYWORD_SEGMENT),
            "DoubleKeywordSegment" => Some(&DOUBLE_KEYWORD_SEGMENT),
            "NormalKeywordSegment" => Some(&NORMAL_KEYWORD_SEGMENT),
            "TinyintKeywordSegment" => Some(&TINYINT_KEYWORD_SEGMENT),
            "NativeKeywordSegment" => Some(&NATIVE_KEYWORD_SEGMENT),
            "FloatKeywordSegment" => Some(&FLOAT_KEYWORD_SEGMENT),
            "PassiveKeywordSegment" => Some(&PASSIVE_KEYWORD_SEGMENT),
            "BinaryKeywordSegment" => Some(&BINARY_KEYWORD_SEGMENT),
            "StrictKeywordSegment" => Some(&STRICT_KEYWORD_SEGMENT),
            "UnsignedKeywordSegment" => Some(&UNSIGNED_KEYWORD_SEGMENT),
            "WalKeywordSegment" => Some(&WAL_KEYWORD_SEGMENT),
            "BigintKeywordSegment" => Some(&BIGINT_KEYWORD_SEGMENT),
            "NumericKeywordSegment" => Some(&NUMERIC_KEYWORD_SEGMENT),
            "TruncateKeywordSegment" => Some(&TRUNCATE_KEYWORD_SEGMENT),
            "IntKeywordSegment" => Some(&INT_KEYWORD_SEGMENT),
            "RealKeywordSegment" => Some(&REAL_KEYWORD_SEGMENT),
            "DatetimeKeywordSegment" => Some(&DATETIME_KEYWORD_SEGMENT),
            "Int8KeywordSegment" => Some(&INT8_KEYWORD_SEGMENT),
            "Int2KeywordSegment" => Some(&INT2_KEYWORD_SEGMENT),
            "FastKeywordSegment" => Some(&FAST_KEYWORD_SEGMENT),
            "NocaseKeywordSegment" => Some(&NOCASE_KEYWORD_SEGMENT),
            "PrecisionKeywordSegment" => Some(&PRECISION_KEYWORD_SEGMENT),
            "DecimalKeywordSegment" => Some(&DECIMAL_KEYWORD_SEGMENT),
            "TiesKeywordSegment" => Some(&TIES_KEYWORD_SEGMENT),
            "PersistKeywordSegment" => Some(&PERSIST_KEYWORD_SEGMENT),
            "VaryingKeywordSegment" => Some(&VARYING_KEYWORD_SEGMENT),
            "TextKeywordSegment" => Some(&TEXT_KEYWORD_SEGMENT),
            "FileKeywordSegment" => Some(&FILE_KEYWORD_SEGMENT),
            "YesKeywordSegment" => Some(&YES_KEYWORD_SEGMENT),
            "RtrimKeywordSegment" => Some(&RTRIM_KEYWORD_SEGMENT),
            "DateKeywordSegment" => Some(&DATE_KEYWORD_SEGMENT),
            "IncrementalKeywordSegment" => Some(&INCREMENTAL_KEYWORD_SEGMENT),
            "ResetKeywordSegment" => Some(&RESET_KEYWORD_SEGMENT),
            "BlobKeywordSegment" => Some(&BLOB_KEYWORD_SEGMENT),
            "OverKeywordSegment" => Some(&OVER_KEYWORD_SEGMENT),
            "PlanKeywordSegment" => Some(&PLAN_KEYWORD_SEGMENT),
            "InKeywordSegment" => Some(&IN_KEYWORD_SEGMENT),
            "GroupsKeywordSegment" => Some(&GROUPS_KEYWORD_SEGMENT),
            "IntersectKeywordSegment" => Some(&INTERSECT_KEYWORD_SEGMENT),
            "OrKeywordSegment" => Some(&OR_KEYWORD_SEGMENT),
            "QueryKeywordSegment" => Some(&QUERY_KEYWORD_SEGMENT),
            "RaiseKeywordSegment" => Some(&RAISE_KEYWORD_SEGMENT),
            "WithoutKeywordSegment" => Some(&WITHOUT_KEYWORD_SEGMENT),
            "AnalyzeKeywordSegment" => Some(&ANALYZE_KEYWORD_SEGMENT),
            "OffsetKeywordSegment" => Some(&OFFSET_KEYWORD_SEGMENT),
            "RollbackKeywordSegment" => Some(&ROLLBACK_KEYWORD_SEGMENT),
            "PartitionKeywordSegment" => Some(&PARTITION_KEYWORD_SEGMENT),
            "EndKeywordSegment" => Some(&END_KEYWORD_SEGMENT),
            "SetKeywordSegment" => Some(&SET_KEYWORD_SEGMENT),
            "AddKeywordSegment" => Some(&ADD_KEYWORD_SEGMENT),
            "CollateKeywordSegment" => Some(&COLLATE_KEYWORD_SEGMENT),
            "DeleteKeywordSegment" => Some(&DELETE_KEYWORD_SEGMENT),
            "FilterKeywordSegment" => Some(&FILTER_KEYWORD_SEGMENT),
            "PrimaryKeywordSegment" => Some(&PRIMARY_KEYWORD_SEGMENT),
            "SavepointKeywordSegment" => Some(&SAVEPOINT_KEYWORD_SEGMENT),
            "MatchKeywordSegment" => Some(&MATCH_KEYWORD_SEGMENT),
            "DistinctKeywordSegment" => Some(&DISTINCT_KEYWORD_SEGMENT),
            "IntoKeywordSegment" => Some(&INTO_KEYWORD_SEGMENT),
            "LimitKeywordSegment" => Some(&LIMIT_KEYWORD_SEGMENT),
            "RowKeywordSegment" => Some(&ROW_KEYWORD_SEGMENT),
            "IfKeywordSegment" => Some(&IF_KEYWORD_SEGMENT),
            "IndexedKeywordSegment" => Some(&INDEXED_KEYWORD_SEGMENT),
            "OnKeywordSegment" => Some(&ON_KEYWORD_SEGMENT),
            "EscapeKeywordSegment" => Some(&ESCAPE_KEYWORD_SEGMENT),
            "RightKeywordSegment" => Some(&RIGHT_KEYWORD_SEGMENT),
            "ThenKeywordSegment" => Some(&THEN_KEYWORD_SEGMENT),
            "IndexKeywordSegment" => Some(&INDEX_KEYWORD_SEGMENT),
            "DeferrableKeywordSegment" => Some(&DEFERRABLE_KEYWORD_SEGMENT),
            "GroupKeywordSegment" => Some(&GROUP_KEYWORD_SEGMENT),
            "OuterKeywordSegment" => Some(&OUTER_KEYWORD_SEGMENT),
            "AbortKeywordSegment" => Some(&ABORT_KEYWORD_SEGMENT),
            "ColumnKeywordSegment" => Some(&COLUMN_KEYWORD_SEGMENT),
            "UnboundedKeywordSegment" => Some(&UNBOUNDED_KEYWORD_SEGMENT),
            "InsertKeywordSegment" => Some(&INSERT_KEYWORD_SEGMENT),
            "WhenKeywordSegment" => Some(&WHEN_KEYWORD_SEGMENT),
            "ConflictKeywordSegment" => Some(&CONFLICT_KEYWORD_SEGMENT),
            "ExplainKeywordSegment" => Some(&EXPLAIN_KEYWORD_SEGMENT),
            "TableKeywordSegment" => Some(&TABLE_KEYWORD_SEGMENT),
            "TempKeywordSegment" => Some(&TEMP_KEYWORD_SEGMENT),
            "UniqueKeywordSegment" => Some(&UNIQUE_KEYWORD_SEGMENT),
            "ReplaceKeywordSegment" => Some(&REPLACE_KEYWORD_SEGMENT),
            "ReleaseKeywordSegment" => Some(&RELEASE_KEYWORD_SEGMENT),
            "RenameKeywordSegment" => Some(&RENAME_KEYWORD_SEGMENT),
            "IgnoreKeywordSegment" => Some(&IGNORE_KEYWORD_SEGMENT),
            "IsnullKeywordSegment" => Some(&ISNULL_KEYWORD_SEGMENT),
            "CommitKeywordSegment" => Some(&COMMIT_KEYWORD_SEGMENT),
            "ForeignKeywordSegment" => Some(&FOREIGN_KEYWORD_SEGMENT),
            "GeneratedKeywordSegment" => Some(&GENERATED_KEYWORD_SEGMENT),
            "TransactionKeywordSegment" => Some(&TRANSACTION_KEYWORD_SEGMENT),
            "NullKeywordSegment" => Some(&NULL_KEYWORD_SEGMENT),
            "AlwaysKeywordSegment" => Some(&ALWAYS_KEYWORD_SEGMENT),
            "CaseKeywordSegment" => Some(&CASE_KEYWORD_SEGMENT),
            "ByKeywordSegment" => Some(&BY_KEYWORD_SEGMENT),
            "CastKeywordSegment" => Some(&CAST_KEYWORD_SEGMENT),
            "FailKeywordSegment" => Some(&FAIL_KEYWORD_SEGMENT),
            "ReindexKeywordSegment" => Some(&REINDEX_KEYWORD_SEGMENT),
            "NoKeywordSegment" => Some(&NO_KEYWORD_SEGMENT),
            "NotnullKeywordSegment" => Some(&NOTNULL_KEYWORD_SEGMENT),
            "JoinKeywordSegment" => Some(&JOIN_KEYWORD_SEGMENT),
            "ToKeywordSegment" => Some(&TO_KEYWORD_SEGMENT),
            "SelectKeywordSegment" => Some(&SELECT_KEYWORD_SEGMENT),
            "NothingKeywordSegment" => Some(&NOTHING_KEYWORD_SEGMENT),
            "DescKeywordSegment" => Some(&DESC_KEYWORD_SEGMENT),
            "RestrictKeywordSegment" => Some(&RESTRICT_KEYWORD_SEGMENT),
            "CreateKeywordSegment" => Some(&CREATE_KEYWORD_SEGMENT),
            "TriggerKeywordSegment" => Some(&TRIGGER_KEYWORD_SEGMENT),
            "GlobKeywordSegment" => Some(&GLOB_KEYWORD_SEGMENT),
            "ViewKeywordSegment" => Some(&VIEW_KEYWORD_SEGMENT),
            "VirtualKeywordSegment" => Some(&VIRTUAL_KEYWORD_SEGMENT),
            "DropKeywordSegment" => Some(&DROP_KEYWORD_SEGMENT),
            "AlterKeywordSegment" => Some(&ALTER_KEYWORD_SEGMENT),
            "LastKeywordSegment" => Some(&LAST_KEYWORD_SEGMENT),
            "ExcludeKeywordSegment" => Some(&EXCLUDE_KEYWORD_SEGMENT),
            "PragmaKeywordSegment" => Some(&PRAGMA_KEYWORD_SEGMENT),
            "DeferredKeywordSegment" => Some(&DEFERRED_KEYWORD_SEGMENT),
            "ForKeywordSegment" => Some(&FOR_KEYWORD_SEGMENT),
            "BetweenKeywordSegment" => Some(&BETWEEN_KEYWORD_SEGMENT),
            "AscKeywordSegment" => Some(&ASC_KEYWORD_SEGMENT),
            "DoKeywordSegment" => Some(&DO_KEYWORD_SEGMENT),
            "AutoincrementKeywordSegment" => Some(&AUTOINCREMENT_KEYWORD_SEGMENT),
            "CrossKeywordSegment" => Some(&CROSS_KEYWORD_SEGMENT),
            "OrderKeywordSegment" => Some(&ORDER_KEYWORD_SEGMENT),
            "LikeKeywordSegment" => Some(&LIKE_KEYWORD_SEGMENT),
            "HavingKeywordSegment" => Some(&HAVING_KEYWORD_SEGMENT),
            "ExistsKeywordSegment" => Some(&EXISTS_KEYWORD_SEGMENT),
            "Current_dateKeywordSegment" => Some(&CURRENT_DATE_KEYWORD_SEGMENT),
            "FullKeywordSegment" => Some(&FULL_KEYWORD_SEGMENT),
            "VacuumKeywordSegment" => Some(&VACUUM_KEYWORD_SEGMENT),
            "AndKeywordSegment" => Some(&AND_KEYWORD_SEGMENT),
            "Current_timestampKeywordSegment" => Some(&CURRENT_TIMESTAMP_KEYWORD_SEGMENT),
            "WithKeywordSegment" => Some(&WITH_KEYWORD_SEGMENT),
            "TemporaryKeywordSegment" => Some(&TEMPORARY_KEYWORD_SEGMENT),
            "RecursiveKeywordSegment" => Some(&RECURSIVE_KEYWORD_SEGMENT),
            "PrecedingKeywordSegment" => Some(&PRECEDING_KEYWORD_SEGMENT),
            "ValuesKeywordSegment" => Some(&VALUES_KEYWORD_SEGMENT),
            "ExclusiveKeywordSegment" => Some(&EXCLUSIVE_KEYWORD_SEGMENT),
            "WindowKeywordSegment" => Some(&WINDOW_KEYWORD_SEGMENT),
            "AllKeywordSegment" => Some(&ALL_KEYWORD_SEGMENT),
            "Current_timeKeywordSegment" => Some(&CURRENT_TIME_KEYWORD_SEGMENT),
            "UpdateKeywordSegment" => Some(&UPDATE_KEYWORD_SEGMENT),
            "ConstraintKeywordSegment" => Some(&CONSTRAINT_KEYWORD_SEGMENT),
            "NotKeywordSegment" => Some(&NOT_KEYWORD_SEGMENT),
            "NullsKeywordSegment" => Some(&NULLS_KEYWORD_SEGMENT),
            "OthersKeywordSegment" => Some(&OTHERS_KEYWORD_SEGMENT),
            "RowsKeywordSegment" => Some(&ROWS_KEYWORD_SEGMENT),
            "EachKeywordSegment" => Some(&EACH_KEYWORD_SEGMENT),
            "AfterKeywordSegment" => Some(&AFTER_KEYWORD_SEGMENT),
            "BeforeKeywordSegment" => Some(&BEFORE_KEYWORD_SEGMENT),
            "ElseKeywordSegment" => Some(&ELSE_KEYWORD_SEGMENT),
            "WhereKeywordSegment" => Some(&WHERE_KEYWORD_SEGMENT),
            "CascadeKeywordSegment" => Some(&CASCADE_KEYWORD_SEGMENT),
            "IsKeywordSegment" => Some(&IS_KEYWORD_SEGMENT),
            "ReferencesKeywordSegment" => Some(&REFERENCES_KEYWORD_SEGMENT),
            "DatabaseKeywordSegment" => Some(&DATABASE_KEYWORD_SEGMENT),
            "UsingKeywordSegment" => Some(&USING_KEYWORD_SEGMENT),
            "InitiallyKeywordSegment" => Some(&INITIALLY_KEYWORD_SEGMENT),
            "MaterializedKeywordSegment" => Some(&MATERIALIZED_KEYWORD_SEGMENT),
            "CurrentKeywordSegment" => Some(&CURRENT_KEYWORD_SEGMENT),
            "OfKeywordSegment" => Some(&OF_KEYWORD_SEGMENT),
            "DefaultKeywordSegment" => Some(&DEFAULT_KEYWORD_SEGMENT),
            "RegexpKeywordSegment" => Some(&REGEXP_KEYWORD_SEGMENT),
            "FirstKeywordSegment" => Some(&FIRST_KEYWORD_SEGMENT),
            "AsKeywordSegment" => Some(&AS_KEYWORD_SEGMENT),
            "FollowingKeywordSegment" => Some(&FOLLOWING_KEYWORD_SEGMENT),
            "RangeKeywordSegment" => Some(&RANGE_KEYWORD_SEGMENT),
            "BeginKeywordSegment" => Some(&BEGIN_KEYWORD_SEGMENT),
            "FromKeywordSegment" => Some(&FROM_KEYWORD_SEGMENT),
            "InsteadKeywordSegment" => Some(&INSTEAD_KEYWORD_SEGMENT),
            "ReturningKeywordSegment" => Some(&RETURNING_KEYWORD_SEGMENT),
            "NaturalKeywordSegment" => Some(&NATURAL_KEYWORD_SEGMENT),
            "InnerKeywordSegment" => Some(&INNER_KEYWORD_SEGMENT),
            "CheckKeywordSegment" => Some(&CHECK_KEYWORD_SEGMENT),
            "DetachKeywordSegment" => Some(&DETACH_KEYWORD_SEGMENT),
            "ExceptKeywordSegment" => Some(&EXCEPT_KEYWORD_SEGMENT),
            "LeftKeywordSegment" => Some(&LEFT_KEYWORD_SEGMENT),
            "UnionKeywordSegment" => Some(&UNION_KEYWORD_SEGMENT),
            "ImmediateKeywordSegment" => Some(&IMMEDIATE_KEYWORD_SEGMENT),
            "AttachKeywordSegment" => Some(&ATTACH_KEYWORD_SEGMENT),
            _ => None,
    }
}
