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
Grammar::StringParser()
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
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "RlikeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IlikeKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverlapsKeywordSegment",
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
    name: "LimitClauseSegment",
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
Grammar::Ref {
    name: "FetchKeywordSegment",
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
    name: "LimitClauseSegment",
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
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OverlapsKeywordSegment",
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
    name: "OverClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilterClauseGrammar",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotEnforcedGrammar",
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
    name: "UniqueKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AutoIncrementGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NotEnforcedGrammar",
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
Grammar::Ref {
    name: "ColumnGeneratedGrammar",
    optional: false,
    allow_gaps: true,
}
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
Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
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
Grammar::Ref {
    name: "TimeWithTZGrammar",
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
    optional: false,
    allow_gaps: true,
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
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BinaryKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: false,
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
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "UnsignedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CharCharacterSetGrammar",
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
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
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
    name: "OverwriteKeywordSegment",
    optional: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
}
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
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
}
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MlKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ModelKeywordSegment",
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
    name: "CommaSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "OffsetClauseSegment",
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
Grammar::Ref {
    name: "ValuesClauseSegment",
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
Grammar::Ref {
    name: "UnionGrammar",
    optional: false,
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
Grammar::Ref {
    name: "MinusKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "MergeStatementSegment",
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
    name: "TransactionStatementSegment",
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
    name: "DropViewStatementSegment",
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
    name: "DropUserStatementSegment",
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
    name: "AccessStatementSegment",
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
    name: "CreateRoleStatementSegment",
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
    name: "AlterTableStatementSegment",
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
    name: "SetSchemaStatementSegment",
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
    name: "DropTypeStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateDatabaseStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropDatabaseStatementSegment",
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
    name: "DropIndexStatementSegment",
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
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateCastStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropCastStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateFunctionStatementSegment",
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
    name: "CreateModelStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropModelStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DescribeStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UseStatementSegment",
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
    name: "CreateSequenceStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterSequenceStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropSequenceStatementSegment",
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
    name: "DropTriggerStatementSegment",
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
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Ref {
    name: "WorkKeywordSegment",
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
    name: "NameKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ChainKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ValueKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
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

// name='NocheckKeywordSegment'
pub static NOCHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StringKeywordSegment'
pub static STRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CorrKeywordSegment'
pub static CORR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefinerKeywordSegment'
pub static DEFINER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Straight_joinKeywordSegment'
pub static STRAIGHT_JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BitvarKeywordSegment'
pub static BITVAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Trigger_schemaKeywordSegment'
pub static TRIGGER_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_specific_nameKeywordSegment'
pub static PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreserveKeywordSegment'
pub static PRESERVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TempKeywordSegment'
pub static TEMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BitKeywordSegment'
pub static BIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_schemaKeywordSegment'
pub static COLLATION_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Identity_insertKeywordSegment'
pub static IDENTITY_INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptionKeywordSegment'
pub static EXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainsKeywordSegment'
pub static CONTAINS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CallKeywordSegment'
pub static CALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Trigger_nameKeywordSegment'
pub static TRIGGER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DepthKeywordSegment'
pub static DEPTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantsKeywordSegment'
pub static GRANTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutputKeywordSegment'
pub static OUTPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SaveKeywordSegment'
pub static SAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AreKeywordSegment'
pub static ARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnlistenKeywordSegment'
pub static UNLISTEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentifiedKeywordSegment'
pub static IDENTIFIED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Last_insert_idKeywordSegment'
pub static LAST_INSERT_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImmediateKeywordSegment'
pub static IMMEDIATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RealKeywordSegment'
pub static REAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RequireKeywordSegment'
pub static REQUIRE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AccessKeywordSegment'
pub static ACCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcessKeywordSegment'
pub static PROCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HourKeywordSegment'
pub static HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NormalizedKeywordSegment'
pub static NORMALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Message_lengthKeywordSegment'
pub static MESSAGE_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='System_userKeywordSegment'
pub static SYSTEM_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TypeKeywordSegment'
pub static TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProceduresKeywordSegment'
pub static PROCEDURES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelimitersKeywordSegment'
pub static DELIMITERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InheritsKeywordSegment'
pub static INHERITS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='End-execKeywordSegment'
pub static END_EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PolicyKeywordSegment'
pub static POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocksKeywordSegment'
pub static LOCKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelayedKeywordSegment'
pub static DELAYED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InfileKeywordSegment'
pub static INFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScaleKeywordSegment'
pub static SCALE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrailingKeywordSegment'
pub static TRAILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetsKeywordSegment'
pub static OFFSETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatKeywordSegment'
pub static REPEAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WrapperKeywordSegment'
pub static WRAPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MediumintKeywordSegment'
pub static MEDIUMINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClusterKeywordSegment'
pub static CLUSTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonitorKeywordSegment'
pub static MONITOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreetextKeywordSegment'
pub static FREETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TasksKeywordSegment'
pub static TASKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpendatasourceKeywordSegment'
pub static OPENDATASOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Subclass_originKeywordSegment'
pub static SUBCLASS_ORIGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnsKeywordSegment'
pub static COLUMNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int1KeywordSegment'
pub static INT1_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TinytextKeywordSegment'
pub static TINYTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PathKeywordSegment'
pub static PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MillisecondKeywordSegment'
pub static MILLISECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharacteristicsKeywordSegment'
pub static CHARACTERISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncodingKeywordSegment'
pub static ENCODING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MoveKeywordSegment'
pub static MOVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubstringKeywordSegment'
pub static SUBSTRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonthnameKeywordSegment'
pub static MONTHNAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_big_tablesKeywordSegment'
pub static SQL_BIG_TABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CobolKeywordSegment'
pub static COBOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxKeywordSegment'
pub static MAX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClusteredKeywordSegment'
pub static CLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Connection_nameKeywordSegment'
pub static CONNECTION_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValidKeywordSegment'
pub static VALID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlstateKeywordSegment'
pub static SQLSTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Max_rowsKeywordSegment'
pub static MAX_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelimiterKeywordSegment'
pub static DELIMITER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultsKeywordSegment'
pub static DEFAULTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BernoulliKeywordSegment'
pub static BERNOULLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModeKeywordSegment'
pub static MODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_big_selectsKeywordSegment'
pub static SQL_BIG_SELECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChangeKeywordSegment'
pub static CHANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeysKeywordSegment'
pub static KEYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Routine_catalogKeywordSegment'
pub static ROUTINE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FlushKeywordSegment'
pub static FLUSH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SourceKeywordSegment'
pub static SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PowerKeywordSegment'
pub static POWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintsKeywordSegment'
pub static CONSTRAINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResourceKeywordSegment'
pub static RESOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_nameKeywordSegment'
pub static CHARACTER_SET_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Constraint_nameKeywordSegment'
pub static CONSTRAINT_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HierarchyKeywordSegment'
pub static HIERARCHY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbsKeywordSegment'
pub static ABS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NationalKeywordSegment'
pub static NATIONAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoutinesKeywordSegment'
pub static ROUTINES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SharesKeywordSegment'
pub static SHARES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenxmlKeywordSegment'
pub static OPENXML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrdinalityKeywordSegment'
pub static ORDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FinalKeywordSegment'
pub static FINAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Utc_dateKeywordSegment'
pub static UTC_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WorkKeywordSegment'
pub static WORK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NextKeywordSegment'
pub static NEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_specific_schemaKeywordSegment'
pub static PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdatetextKeywordSegment'
pub static UPDATETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InfixKeywordSegment'
pub static INFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SubmultisetKeywordSegment'
pub static SUBMULTISET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DomainKeywordSegment'
pub static DOMAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SequenceKeywordSegment'
pub static SEQUENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DaysKeywordSegment'
pub static DAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefinedKeywordSegment'
pub static DEFINED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MediumblobKeywordSegment'
pub static MEDIUMBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrefixKeywordSegment'
pub static PREFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsersKeywordSegment'
pub static USERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuditKeywordSegment'
pub static AUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HeaderKeywordSegment'
pub static HEADER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NosuperuserKeywordSegment'
pub static NOSUPERUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetuserKeywordSegment'
pub static SETUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocycleKeywordSegment'
pub static NOCYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecondKeywordSegment'
pub static SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Day_secondKeywordSegment'
pub static DAY_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExcludingKeywordSegment'
pub static EXCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Server_nameKeywordSegment'
pub static SERVER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WarehousesKeywordSegment'
pub static WAREHOUSES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsnullKeywordSegment'
pub static ISNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CoalesceKeywordSegment'
pub static COALESCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BreakKeywordSegment'
pub static BREAK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InvokerKeywordSegment'
pub static INVOKER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HandlerKeywordSegment'
pub static HANDLER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConversionKeywordSegment'
pub static CONVERSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoginKeywordSegment'
pub static LOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ServerKeywordSegment'
pub static SERVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreparedKeywordSegment'
pub static PREPARED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransformKeywordSegment'
pub static TRANSFORM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarcharacterKeywordSegment'
pub static VARCHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Scope_nameKeywordSegment'
pub static SCOPE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForceKeywordSegment'
pub static FORCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParametersKeywordSegment'
pub static PARAMETERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Session_userKeywordSegment'
pub static SESSION_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecurityKeywordSegment'
pub static SECURITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayofmonthKeywordSegment'
pub static DAYOFMONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LongKeywordSegment'
pub static LONG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartKeywordSegment'
pub static START_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Covar_sampKeywordSegment'
pub static COVAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SuccessfulKeywordSegment'
pub static SUCCESSFUL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImplicitKeywordSegment'
pub static IMPLICIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Minute_secondKeywordSegment'
pub static MINUTE_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NowaitKeywordSegment'
pub static NOWAIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgxKeywordSegment'
pub static REGR_AVGX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UserKeywordSegment'
pub static USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CloseKeywordSegment'
pub static CLOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TaskKeywordSegment'
pub static TASK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MKeywordSegment'
pub static M_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MergeKeywordSegment'
pub static MERGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StorageKeywordSegment'
pub static STORAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Cursor_nameKeywordSegment'
pub static CURSOR_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImportedKeywordSegment'
pub static IMPORTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExistingKeywordSegment'
pub static EXISTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LevelKeywordSegment'
pub static LEVEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EveryKeywordSegment'
pub static EVERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrivilegesKeywordSegment'
pub static PRIVILEGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InputKeywordSegment'
pub static INPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlerrorKeywordSegment'
pub static SQLERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NclobKeywordSegment'
pub static NCLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GoKeywordSegment'
pub static GO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotnullKeywordSegment'
pub static NOTNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_small_resultKeywordSegment'
pub static SQL_SMALL_RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranKeywordSegment'
pub static TRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoorderKeywordSegment'
pub static NOORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnlyKeywordSegment'
pub static ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlwarningKeywordSegment'
pub static SQLWARNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OidsKeywordSegment'
pub static OIDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecKeywordSegment'
pub static EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StatisticsKeywordSegment'
pub static STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoutineKeywordSegment'
pub static ROUTINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrimKeywordSegment'
pub static TRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QuarterKeywordSegment'
pub static QUARTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithinKeywordSegment'
pub static WITHIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayofyearKeywordSegment'
pub static DAYOFYEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencingKeywordSegment'
pub static REFERENCING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RaiserrorKeywordSegment'
pub static RAISERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Utc_timestampKeywordSegment'
pub static UTC_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OfflineKeywordSegment'
pub static OFFLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttributeKeywordSegment'
pub static ATTRIBUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DiskKeywordSegment'
pub static DISK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_countKeywordSegment'
pub static REGR_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReconfigureKeywordSegment'
pub static RECONFIGURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatableKeywordSegment'
pub static REPEATABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PadKeywordSegment'
pub static PAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Message_textKeywordSegment'
pub static MESSAGE_TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncryptedKeywordSegment'
pub static ENCRYPTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SynonymKeywordSegment'
pub static SYNONYM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullifKeywordSegment'
pub static NULLIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ObjectKeywordSegment'
pub static OBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneralKeywordSegment'
pub static GENERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LongblobKeywordSegment'
pub static LONGBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AdminKeywordSegment'
pub static ADMIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InoutKeywordSegment'
pub static INOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NonclusteredKeywordSegment'
pub static NONCLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChainKeywordSegment'
pub static CHAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionallyKeywordSegment'
pub static OPTIONALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlexceptionKeywordSegment'
pub static SQLEXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QualifyKeywordSegment'
pub static QUALIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WriteKeywordSegment'
pub static WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GreatestKeywordSegment'
pub static GREATEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartialKeywordSegment'
pub static PARTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VacuumKeywordSegment'
pub static VACUUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PriorKeywordSegment'
pub static PRIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GlobalKeywordSegment'
pub static GLOBAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StableKeywordSegment'
pub static STABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadKeywordSegment'
pub static READ_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Utc_timeKeywordSegment'
pub static UTC_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowcountKeywordSegment'
pub static ROWCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsymmetricKeywordSegment'
pub static ASYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayofweekKeywordSegment'
pub static DAYOFWEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TopKeywordSegment'
pub static TOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AggregateKeywordSegment'
pub static AGGREGATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StdoutKeywordSegment'
pub static STDOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_pathKeywordSegment'
pub static CURRENT_PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RegexpKeywordSegment'
pub static REGEXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_syyKeywordSegment'
pub static REGR_SYY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Table_nameKeywordSegment'
pub static TABLE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConnectKeywordSegment'
pub static CONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LogsKeywordSegment'
pub static LOGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DegreeKeywordSegment'
pub static DEGREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DummyKeywordSegment'
pub static DUMMY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnderKeywordSegment'
pub static UNDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecKeywordSegment'
pub static DEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BackupKeywordSegment'
pub static BACKUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_big_resultKeywordSegment'
pub static SQL_BIG_RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DiagnosticsKeywordSegment'
pub static DIAGNOSTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablesampleKeywordSegment'
pub static TABLESAMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuthorizationKeywordSegment'
pub static AUTHORIZATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Varchar2KeywordSegment'
pub static VARCHAR2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AvgKeywordSegment'
pub static AVG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DictionaryKeywordSegment'
pub static DICTIONARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrustedKeywordSegment'
pub static TRUSTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StrictKeywordSegment'
pub static STRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Minute_microsecondKeywordSegment'
pub static MINUTE_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateroleKeywordSegment'
pub static CREATEROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CompletionKeywordSegment'
pub static COMPLETION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenKeywordSegment'
pub static OPEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowguidcolKeywordSegment'
pub static ROWGUIDCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrintKeywordSegment'
pub static PRINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WritetextKeywordSegment'
pub static WRITETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Column_nameKeywordSegment'
pub static COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_defined_type_schemaKeywordSegment'
pub static USER_DEFINED_TYPE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Day_microsecondKeywordSegment'
pub static DAY_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SerializableKeywordSegment'
pub static SERIALIZABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_lengthKeywordSegment'
pub static RETURNED_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ZerofillKeywordSegment'
pub static ZEROFILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbsoluteKeywordSegment'
pub static ABSOLUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_catalogKeywordSegment'
pub static COLLATION_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OthersKeywordSegment'
pub static OTHERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtomicKeywordSegment'
pub static ATOMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Top_level_countKeywordSegment'
pub static TOP_LEVEL_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckpointKeywordSegment'
pub static CHECKPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RownumKeywordSegment'
pub static ROWNUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseifKeywordSegment'
pub static ELSEIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StagesKeywordSegment'
pub static STAGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ErrlvlKeywordSegment'
pub static ERRLVL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SmallintKeywordSegment'
pub static SMALLINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplicationKeywordSegment'
pub static REPLICATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElementKeywordSegment'
pub static ELEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Float8KeywordSegment'
pub static FLOAT8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutKeywordSegment'
pub static OUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocompressKeywordSegment'
pub static NOCOMPRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DenyKeywordSegment'
pub static DENY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModifiesKeywordSegment'
pub static MODIFIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OwnershipKeywordSegment'
pub static OWNERSHIP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_select_limitKeywordSegment'
pub static SQL_SELECT_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupingKeywordSegment'
pub static GROUPING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocreateroleKeywordSegment'
pub static NOCREATEROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LessKeywordSegment'
pub static LESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpecifictypeKeywordSegment'
pub static SPECIFICTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExclusiveKeywordSegment'
pub static EXCLUSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_userKeywordSegment'
pub static CURRENT_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharacterKeywordSegment'
pub static CHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SymmetricKeywordSegment'
pub static SYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollectKeywordSegment'
pub static COLLECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeterministicKeywordSegment'
pub static DETERMINISTIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescriptorKeywordSegment'
pub static DESCRIPTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnencryptedKeywordSegment'
pub static UNENCRYPTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReleaseKeywordSegment'
pub static RELEASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KKeywordSegment'
pub static K_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FulltextKeywordSegment'
pub static FULLTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transaction_activeKeywordSegment'
pub static TRANSACTION_ACTIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FunctionsKeywordSegment'
pub static FUNCTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Reference_usageKeywordSegment'
pub static REFERENCE_USAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Timezone_minuteKeywordSegment'
pub static TIMEZONE_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XorKeywordSegment'
pub static XOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartsKeywordSegment'
pub static STARTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocreateuserKeywordSegment'
pub static NOCREATEUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharKeywordSegment'
pub static CHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DivKeywordSegment'
pub static DIV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ObjectsKeywordSegment'
pub static OBJECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SomeKeywordSegment'
pub static SOME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TinyblobKeywordSegment'
pub static TINYBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UncommittedKeywordSegment'
pub static UNCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CacheKeywordSegment'
pub static CACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StreamsKeywordSegment'
pub static STREAMS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GetKeywordSegment'
pub static GET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CatalogKeywordSegment'
pub static CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InheritKeywordSegment'
pub static INHERIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BoolKeywordSegment'
pub static BOOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadedKeywordSegment'
pub static CASCADED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcesslistKeywordSegment'
pub static PROCESSLIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisconnectKeywordSegment'
pub static DISCONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistinctrowKeywordSegment'
pub static DISTINCTROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxyKeywordSegment'
pub static REGR_SXY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TemporaryKeywordSegment'
pub static TEMPORARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShowKeywordSegment'
pub static SHOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnableKeywordSegment'
pub static ENABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ApplyKeywordSegment'
pub static APPLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PascalKeywordSegment'
pub static PASCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ArrayKeywordSegment'
pub static ARRAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranslationKeywordSegment'
pub static TRANSLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RuleKeywordSegment'
pub static RULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoKeywordSegment'
pub static DO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchKeywordSegment'
pub static MATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThanKeywordSegment'
pub static THAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Catalog_nameKeywordSegment'
pub static CATALOG_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConvertKeywordSegment'
pub static CONVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Row_countKeywordSegment'
pub static ROW_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnnestKeywordSegment'
pub static UNNEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CharactersKeywordSegment'
pub static CHARACTERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ListenKeywordSegment'
pub static LISTEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Delay_key_writeKeywordSegment'
pub static DELAY_KEY_WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocreatedbKeywordSegment'
pub static NOCREATEDB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpaceKeywordSegment'
pub static SPACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Timezone_hourKeywordSegment'
pub static TIMEZONE_HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TemplateKeywordSegment'
pub static TEMPLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_discKeywordSegment'
pub static PERCENTILE_DISC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnsKeywordSegment'
pub static RETURNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LinenoKeywordSegment'
pub static LINENO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TreatKeywordSegment'
pub static TREAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonthKeywordSegment'
pub static MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotifyKeywordSegment'
pub static NOTIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TextKeywordSegment'
pub static TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RankKeywordSegment'
pub static RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoauditKeywordSegment'
pub static NOAUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FetchKeywordSegment'
pub static FETCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpperKeywordSegment'
pub static UPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Min_rowsKeywordSegment'
pub static MIN_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Scope_schemaKeywordSegment'
pub static SCOPE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Message_octet_lengthKeywordSegment'
pub static MESSAGE_OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocaltimeKeywordSegment'
pub static LOCALTIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResetKeywordSegment'
pub static RESET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VariablesKeywordSegment'
pub static VARIABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntersectionKeywordSegment'
pub static INTERSECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverwriteKeywordSegment'
pub static OVERWRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CursorKeywordSegment'
pub static CURSOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VariableKeywordSegment'
pub static VARIABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlcodeKeywordSegment'
pub static SQLCODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExcludeKeywordSegment'
pub static EXCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncrementKeywordSegment'
pub static INCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UseKeywordSegment'
pub static USE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DbccKeywordSegment'
pub static DBCC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Stddev_sampKeywordSegment'
pub static STDDEV_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExitKeywordSegment'
pub static EXIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Condition_numberKeywordSegment'
pub static CONDITION_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Day_hourKeywordSegment'
pub static DAY_HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverlayKeywordSegment'
pub static OVERLAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DestroyKeywordSegment'
pub static DESTROY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PipeKeywordSegment'
pub static PIPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WeekdayKeywordSegment'
pub static WEEKDAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablespaceKeywordSegment'
pub static TABLESPACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_slopeKeywordSegment'
pub static REGR_SLOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ViewsKeywordSegment'
pub static VIEWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckedKeywordSegment'
pub static CHECKED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeclareKeywordSegment'
pub static DECLARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferrableKeywordSegment'
pub static DEFERRABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BackwardKeywordSegment'
pub static BACKWARD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IterateKeywordSegment'
pub static ITERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SonameKeywordSegment'
pub static SONAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnlineKeywordSegment'
pub static ONLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExpKeywordSegment'
pub static EXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecutionKeywordSegment'
pub static EXECUTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsamKeywordSegment'
pub static ISAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AssertionKeywordSegment'
pub static ASSERTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Second_microsecondKeywordSegment'
pub static SECOND_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlcaKeywordSegment'
pub static SQLCA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ZoneKeywordSegment'
pub static ZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollationKeywordSegment'
pub static COLLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransactionsKeywordSegment'
pub static TRANSACTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentityKeywordSegment'
pub static IDENTITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumberKeywordSegment'
pub static NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TsequalKeywordSegment'
pub static TSEQUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PreorderKeywordSegment'
pub static PREORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Scope_catalogKeywordSegment'
pub static SCOPE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Key_typeKeywordSegment'
pub static KEY_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcKeywordSegment'
pub static PROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsteadKeywordSegment'
pub static INSTEAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlanKeywordSegment'
pub static PLAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Collation_nameKeywordSegment'
pub static COLLATION_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentitycolKeywordSegment'
pub static IDENTITYCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaskingKeywordSegment'
pub static MASKING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dense_rankKeywordSegment'
pub static DENSE_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImmutableKeywordSegment'
pub static IMMUTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeferredKeywordSegment'
pub static DEFERRED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MediumtextKeywordSegment'
pub static MEDIUMTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FillfactorKeywordSegment'
pub static FILLFACTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncludeKeywordSegment'
pub static INCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transactions_rolled_backKeywordSegment'
pub static TRANSACTIONS_ROLLED_BACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OldKeywordSegment'
pub static OLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Schema_nameKeywordSegment'
pub static SCHEMA_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LargeKeywordSegment'
pub static LARGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExtensionKeywordSegment'
pub static EXTENSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetsKeywordSegment'
pub static SETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShareKeywordSegment'
pub static SHARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VersionKeywordSegment'
pub static VERSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Avg_row_lengthKeywordSegment'
pub static AVG_ROW_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ManageKeywordSegment'
pub static MANAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainstableKeywordSegment'
pub static CONTAINSTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NestingKeywordSegment'
pub static NESTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutfileKeywordSegment'
pub static OUTFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Command_functionKeywordSegment'
pub static COMMAND_FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CubeKeywordSegment'
pub static CUBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NologinKeywordSegment'
pub static NOLOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SystemKeywordSegment'
pub static SYSTEM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverlapsKeywordSegment'
pub static OVERLAPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_lengthKeywordSegment'
pub static CHARACTER_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hour_secondKeywordSegment'
pub static HOUR_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InstanceKeywordSegment'
pub static INSTANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndicatorKeywordSegment'
pub static INDICATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StdinKeywordSegment'
pub static STDIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FutureKeywordSegment'
pub static FUTURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int2KeywordSegment'
pub static INT2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModKeywordSegment'
pub static MOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescribeKeywordSegment'
pub static DESCRIBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CardinalityKeywordSegment'
pub static CARDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SectionKeywordSegment'
pub static SECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AccountKeywordSegment'
pub static ACCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DataKeywordSegment'
pub static DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StateKeywordSegment'
pub static STATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EscapedKeywordSegment'
pub static ESCAPED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SizeKeywordSegment'
pub static SIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeaveKeywordSegment'
pub static LEAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PasswordKeywordSegment'
pub static PASSWORD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FoundKeywordSegment'
pub static FOUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QuoteKeywordSegment'
pub static QUOTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverridingKeywordSegment'
pub static OVERRIDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransientKeywordSegment'
pub static TRANSIENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatabasesKeywordSegment'
pub static DATABASES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecimalKeywordSegment'
pub static DECIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_octet_lengthKeywordSegment'
pub static RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SensitiveKeywordSegment'
pub static SENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SeparatorKeywordSegment'
pub static SEPARATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HoldKeywordSegment'
pub static HOLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SessionKeywordSegment'
pub static SESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranslateKeywordSegment'
pub static TRANSLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecuteKeywordSegment'
pub static EXECUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FusionKeywordSegment'
pub static FUSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeadingKeywordSegment'
pub static LEADING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitiallyKeywordSegment'
pub static INITIALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollupKeywordSegment'
pub static ROLLUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsensitiveKeywordSegment'
pub static ASENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateuserKeywordSegment'
pub static CREATEUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PliKeywordSegment'
pub static PLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HostKeywordSegment'
pub static HOST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HeapKeywordSegment'
pub static HEAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartingKeywordSegment'
pub static STARTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Var_popKeywordSegment'
pub static VAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NothingKeywordSegment'
pub static NOTHING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TinyintKeywordSegment'
pub static TINYINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PostfixKeywordSegment'
pub static POSTFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StageKeywordSegment'
pub static STAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Low_priorityKeywordSegment'
pub static LOW_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocaltimestampKeywordSegment'
pub static LOCALTIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResignalKeywordSegment'
pub static RESIGNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InstantiableKeywordSegment'
pub static INSTANTIABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitializeKeywordSegment'
pub static INITIALIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StructureKeywordSegment'
pub static STRUCTURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TextsizeKeywordSegment'
pub static TEXTSIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnsignedKeywordSegment'
pub static UNSIGNED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dynamic_function_codeKeywordSegment'
pub static DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HoldlockKeywordSegment'
pub static HOLDLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilterKeywordSegment'
pub static FILTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocacheKeywordSegment'
pub static NOCACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OperatorKeywordSegment'
pub static OPERATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StatementKeywordSegment'
pub static STATEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegerKeywordSegment'
pub static INTEGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenrowsetKeywordSegment'
pub static OPENROWSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='High_priorityKeywordSegment'
pub static HIGH_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='X509KeywordSegment'
pub static X509_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MumpsKeywordSegment'
pub static MUMPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MultisetKeywordSegment'
pub static MULTISET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NormalizeKeywordSegment'
pub static NORMALIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_modeKeywordSegment'
pub static PARAMETER_MODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Insert_idKeywordSegment'
pub static INSERT_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Year_monthKeywordSegment'
pub static YEAR_MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OwnerKeywordSegment'
pub static OWNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hour_microsecondKeywordSegment'
pub static HOUR_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MapKeywordSegment'
pub static MAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_defined_type_catalogKeywordSegment'
pub static USER_DEFINED_TYPE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Pack_keysKeywordSegment'
pub static PACK_KEYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModifyKeywordSegment'
pub static MODIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LowerKeywordSegment'
pub static LOWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlobKeywordSegment'
pub static BLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Routine_nameKeywordSegment'
pub static ROUTINE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnyKeywordSegment'
pub static ANY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RevokeKeywordSegment'
pub static REVOKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FormatKeywordSegment'
pub static FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_warningsKeywordSegment'
pub static SQL_WARNINGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LancompilerKeywordSegment'
pub static LANCOMPILER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_sqlstateKeywordSegment'
pub static RETURNED_SQLSTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ChecksumKeywordSegment'
pub static CHECKSUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarcharKeywordSegment'
pub static VARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchedKeywordSegment'
pub static MATCHED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Use_any_roleKeywordSegment'
pub static USE_ANY_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FieldsKeywordSegment'
pub static FIELDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClobKeywordSegment'
pub static CLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WeekKeywordSegment'
pub static WEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemasKeywordSegment'
pub static SCHEMAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimeKeywordSegment'
pub static TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CopyKeywordSegment'
pub static COPY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UidKeywordSegment'
pub static UID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgyKeywordSegment'
pub static REGR_AVGY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Covar_popKeywordSegment'
pub static COVAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Var_sampKeywordSegment'
pub static VAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinuteKeywordSegment'
pub static MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablesKeywordSegment'
pub static TABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Float4KeywordSegment'
pub static FLOAT4_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GKeywordSegment'
pub static G_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LateralKeywordSegment'
pub static LATERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_default_transform_groupKeywordSegment'
pub static CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValueKeywordSegment'
pub static VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_r2KeywordSegment'
pub static REGR_R2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VerboseKeywordSegment'
pub static VERBOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BrowseKeywordSegment'
pub static BROWSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MlslabelKeywordSegment'
pub static MLSLABEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MemberKeywordSegment'
pub static MEMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Class_originKeywordSegment'
pub static CLASS_ORIGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForwardKeywordSegment'
pub static FORWARD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MethodKeywordSegment'
pub static METHOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemaKeywordSegment'
pub static SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Trigger_catalogKeywordSegment'
pub static TRIGGER_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InitialKeywordSegment'
pub static INITIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ImplementationKeywordSegment'
pub static IMPLEMENTATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RolesKeywordSegment'
pub static ROLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BreadthKeywordSegment'
pub static BREADTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullableKeywordSegment'
pub static NULLABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParameterKeywordSegment'
pub static PARAMETER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UescapeKeywordSegment'
pub static UESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionsKeywordSegment'
pub static OPTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BulkKeywordSegment'
pub static BULK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SysdateKeywordSegment'
pub static SYSDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetofKeywordSegment'
pub static SETOF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatetimeKeywordSegment'
pub static DATETIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VolatileKeywordSegment'
pub static VOLATILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegrationsKeywordSegment'
pub static INTEGRATIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MyisamKeywordSegment'
pub static MYISAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncludingKeywordSegment'
pub static INCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlsoKeywordSegment'
pub static ALSO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Octet_lengthKeywordSegment'
pub static OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_transform_group_for_typeKeywordSegment'
pub static CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReindexKeywordSegment'
pub static REINDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EachKeywordSegment'
pub static EACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SignalKeywordSegment'
pub static SIGNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntegrationKeywordSegment'
pub static INTEGRATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModuleKeywordSegment'
pub static MODULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OperationKeywordSegment'
pub static OPERATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoinheritKeywordSegment'
pub static NOINHERIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreeKeywordSegment'
pub static FREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Bit_lengthKeywordSegment'
pub static BIT_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeastKeywordSegment'
pub static LEAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StaticKeywordSegment'
pub static STATIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConditionKeywordSegment'
pub static CONDITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommittedKeywordSegment'
pub static COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MlKeywordSegment'
pub static ML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CeilKeywordSegment'
pub static CEIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimestampKeywordSegment'
pub static TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_low_priority_updatesKeywordSegment'
pub static SQL_LOW_PRIORITY_UPDATES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReloadKeywordSegment'
pub static RELOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PercentKeywordSegment'
pub static PERCENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_roleKeywordSegment'
pub static CURRENT_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AliasKeywordSegment'
pub static ALIAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_log_offKeywordSegment'
pub static SQL_LOG_OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClassKeywordSegment'
pub static CLASS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CorrespondingKeywordSegment'
pub static CORRESPONDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecheckKeywordSegment'
pub static RECHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DumpKeywordSegment'
pub static DUMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxvalueKeywordSegment'
pub static MAXVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PurgeKeywordSegment'
pub static PURGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PctfreeKeywordSegment'
pub static PCTFREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SimilarKeywordSegment'
pub static SIMILAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NumericKeywordSegment'
pub static NUMERIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Stddev_popKeywordSegment'
pub static STDDEV_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlKeywordSegment'
pub static XML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FalseKeywordSegment'
pub static FALSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Row_numberKeywordSegment'
pub static ROW_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AssignmentKeywordSegment'
pub static ASSIGNMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NameKeywordSegment'
pub static NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SimpleKeywordSegment'
pub static SIMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transactions_committedKeywordSegment'
pub static TRANSACTIONS_COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SequencesKeywordSegment'
pub static SEQUENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Raid0KeywordSegment'
pub static RAID0_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqlKeywordSegment'
pub static SQL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SublistKeywordSegment'
pub static SUBLIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreetexttableKeywordSegment'
pub static FREETEXTTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_ordinal_positionKeywordSegment'
pub static PARAMETER_ORDINAL_POSITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UntilKeywordSegment'
pub static UNTIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Width_bucketKeywordSegment'
pub static WIDTH_BUCKET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinusKeywordSegment'
pub static MINUS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Datetime_interval_precisionKeywordSegment'
pub static DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PositionKeywordSegment'
pub static POSITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CeilingKeywordSegment'
pub static CEILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisableKeywordSegment'
pub static DISABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int8KeywordSegment'
pub static INT8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_schemaKeywordSegment'
pub static CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MiddleintKeywordSegment'
pub static MIDDLEINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GotoKeywordSegment'
pub static GOTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LnKeywordSegment'
pub static LN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreatedbKeywordSegment'
pub static CREATEDB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CountKeywordSegment'
pub static COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SqrtKeywordSegment'
pub static SQRT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LinesKeywordSegment'
pub static LINES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parameter_nameKeywordSegment'
pub static PARAMETER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DestructorKeywordSegment'
pub static DESTRUCTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocalKeywordSegment'
pub static LOCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ToastKeywordSegment'
pub static TOAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpatialKeywordSegment'
pub static SPATIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LockKeywordSegment'
pub static LOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TerminateKeywordSegment'
pub static TERMINATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_incrementKeywordSegment'
pub static AUTO_INCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstructorKeywordSegment'
pub static CONSTRUCTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_defined_type_nameKeywordSegment'
pub static USER_DEFINED_TYPE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Cume_distKeywordSegment'
pub static CUME_DIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LengthKeywordSegment'
pub static LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_defined_type_codeKeywordSegment'
pub static USER_DEFINED_TYPE_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StreamKeywordSegment'
pub static STREAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_contKeywordSegment'
pub static PERCENTILE_CONT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnumKeywordSegment'
pub static ENUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IlikeKeywordSegment'
pub static ILIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LimitKeywordSegment'
pub static LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionKeywordSegment'
pub static OPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HostsKeywordSegment'
pub static HOSTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderingKeywordSegment'
pub static ORDERING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScopeKeywordSegment'
pub static SCOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnknownKeywordSegment'
pub static UNKNOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlacingKeywordSegment'
pub static PLACING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestoreKeywordSegment'
pub static RESTORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnalyzeKeywordSegment'
pub static ANALYZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CycleKeywordSegment'
pub static CYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BothKeywordSegment'
pub static BOTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantedKeywordSegment'
pub static GRANTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='No_write_to_binlogKeywordSegment'
pub static NO_WRITE_TO_BINLOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcedureKeywordSegment'
pub static PROCEDURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EnclosedKeywordSegment'
pub static ENCLOSED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModelKeywordSegment'
pub static MODEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NewKeywordSegment'
pub static NEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttributesKeywordSegment'
pub static ATTRIBUTES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AccountsKeywordSegment'
pub static ACCOUNTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxextentsKeywordSegment'
pub static MAXEXTENTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percent_rankKeywordSegment'
pub static PERCENT_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EqualsKeywordSegment'
pub static EQUALS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Returned_cardinalityKeywordSegment'
pub static RETURNED_CARDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SysidKeywordSegment'
pub static SYSID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_interceptKeywordSegment'
pub static REGR_INTERCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Character_set_catalogKeywordSegment'
pub static CHARACTER_SET_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhileKeywordSegment'
pub static WHILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BooleanKeywordSegment'
pub static BOOLEAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BindingKeywordSegment'
pub static BINDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TerminatedKeywordSegment'
pub static TERMINATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValidateKeywordSegment'
pub static VALIDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayKeywordSegment'
pub static DAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Datetime_interval_codeKeywordSegment'
pub static DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinKeywordSegment'
pub static MIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Day_minuteKeywordSegment'
pub static DAY_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KillKeywordSegment'
pub static KILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScrollKeywordSegment'
pub static SCROLL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OperateKeywordSegment'
pub static OPERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContinueKeywordSegment'
pub static CONTINUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_calc_found_rowsKeywordSegment'
pub static SQL_CALC_FOUND_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SumKeywordSegment'
pub static SUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StyleKeywordSegment'
pub static STYLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WaitforKeywordSegment'
pub static WAITFOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShutdownKeywordSegment'
pub static SHUTDOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
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

// name='PrepareKeywordSegment'
pub static PREPARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxxKeywordSegment'
pub static REGR_SXX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowidKeywordSegment'
pub static ROWID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DispatchKeywordSegment'
pub static DISPATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VarbinaryKeywordSegment'
pub static VARBINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaterializedKeywordSegment'
pub static MATERIALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SslKeywordSegment'
pub static SSL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RawKeywordSegment'
pub static RAW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LongtextKeywordSegment'
pub static LONGTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeallocateKeywordSegment'
pub static DEALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistributedKeywordSegment'
pub static DISTRIBUTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptimizeKeywordSegment'
pub static OPTIMIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CompressKeywordSegment'
pub static COMPRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Key_memberKeywordSegment'
pub static KEY_MEMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtKeywordSegment'
pub static AT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NcharKeywordSegment'
pub static NCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoleKeywordSegment'
pub static ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YamlKeywordSegment'
pub static YAML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PublicKeywordSegment'
pub static PUBLIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JsonKeywordSegment'
pub static JSON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransformsKeywordSegment'
pub static TRANSFORMS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Hour_minuteKeywordSegment'
pub static HOUR_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NanKeywordSegment'
pub static NAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Char_lengthKeywordSegment'
pub static CHAR_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExternalKeywordSegment'
pub static EXTERNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SpecificKeywordSegment'
pub static SPECIFIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LanguageKeywordSegment'
pub static LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FloatKeywordSegment'
pub static FLOAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FortranKeywordSegment'
pub static FORTRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Specific_nameKeywordSegment'
pub static SPECIFIC_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WarehouseKeywordSegment'
pub static WAREHOUSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsolationKeywordSegment'
pub static ISOLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestartKeywordSegment'
pub static RESTART_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AdaKeywordSegment'
pub static ADA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DynamicKeywordSegment'
pub static DYNAMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SavepointKeywordSegment'
pub static SAVEPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CsvKeywordSegment'
pub static CSV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllocateKeywordSegment'
pub static ALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int3KeywordSegment'
pub static INT3_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RefKeywordSegment'
pub static REF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommentKeywordSegment'
pub static COMMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnalyseKeywordSegment'
pub static ANALYSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrueKeywordSegment'
pub static TRUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OctetsKeywordSegment'
pub static OCTETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinvalueKeywordSegment'
pub static MINVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FunctionKeywordSegment'
pub static FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnKeywordSegment'
pub static RETURN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BigintKeywordSegment'
pub static BIGINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MoreKeywordSegment'
pub static MORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sql_log_updateKeywordSegment'
pub static SQL_LOG_UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnnamedKeywordSegment'
pub static UNNAMED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocationKeywordSegment'
pub static LOCATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CalledKeywordSegment'
pub static CALLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantKeywordSegment'
pub static GRANT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoopKeywordSegment'
pub static LOOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Int4KeywordSegment'
pub static INT4_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocatorKeywordSegment'
pub static LOCATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dynamic_functionKeywordSegment'
pub static DYNAMIC_FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DerivedKeywordSegment'
pub static DERIVED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SearchKeywordSegment'
pub static SEARCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FloorKeywordSegment'
pub static FLOOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValidatorKeywordSegment'
pub static VALIDATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnlockKeywordSegment'
pub static UNLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResultKeywordSegment'
pub static RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelfKeywordSegment'
pub static SELF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Routine_schemaKeywordSegment'
pub static ROUTINE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConnectionKeywordSegment'
pub static CONNECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadsKeywordSegment'
pub static READS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenqueryKeywordSegment'
pub static OPENQUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Constraint_schemaKeywordSegment'
pub static CONSTRAINT_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DerefKeywordSegment'
pub static DEREF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WheneverKeywordSegment'
pub static WHENEVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsensitiveKeywordSegment'
pub static INSENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbortKeywordSegment'
pub static ABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreezeKeywordSegment'
pub static FREEZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadtextKeywordSegment'
pub static READTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RelativeKeywordSegment'
pub static RELATIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RlikeKeywordSegment'
pub static RLIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SuperuserKeywordSegment'
pub static SUPERUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UndoKeywordSegment'
pub static UNDO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Command_function_codeKeywordSegment'
pub static COMMAND_FUNCTION_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExtractKeywordSegment'
pub static EXTRACT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YearKeywordSegment'
pub static YEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ComputeKeywordSegment'
pub static COMPUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Constraint_catalogKeywordSegment'
pub static CONSTRAINT_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProceduralKeywordSegment'
pub static PROCEDURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoadKeywordSegment'
pub static LOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsageKeywordSegment'
pub static USAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntKeywordSegment'
pub static INT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntervalKeywordSegment'
pub static INTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RespectKeywordSegment'
pub static RESPECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NaturalKeywordSegment'
pub static NATURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

pub fn get_ansi_segment_grammar(name: &str) -> Option<&'static Grammar> {
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
            "NocheckKeywordSegment" => Some(&NOCHECK_KEYWORD_SEGMENT),
            "StringKeywordSegment" => Some(&STRING_KEYWORD_SEGMENT),
            "CorrKeywordSegment" => Some(&CORR_KEYWORD_SEGMENT),
            "DefinerKeywordSegment" => Some(&DEFINER_KEYWORD_SEGMENT),
            "Straight_joinKeywordSegment" => Some(&STRAIGHT_JOIN_KEYWORD_SEGMENT),
            "BitvarKeywordSegment" => Some(&BITVAR_KEYWORD_SEGMENT),
            "Trigger_schemaKeywordSegment" => Some(&TRIGGER_SCHEMA_KEYWORD_SEGMENT),
            "EscapeKeywordSegment" => Some(&ESCAPE_KEYWORD_SEGMENT),
            "Parameter_specific_nameKeywordSegment" => Some(&PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT),
            "PreserveKeywordSegment" => Some(&PRESERVE_KEYWORD_SEGMENT),
            "TempKeywordSegment" => Some(&TEMP_KEYWORD_SEGMENT),
            "BitKeywordSegment" => Some(&BIT_KEYWORD_SEGMENT),
            "Collation_schemaKeywordSegment" => Some(&COLLATION_SCHEMA_KEYWORD_SEGMENT),
            "Identity_insertKeywordSegment" => Some(&IDENTITY_INSERT_KEYWORD_SEGMENT),
            "ExceptionKeywordSegment" => Some(&EXCEPTION_KEYWORD_SEGMENT),
            "ContainsKeywordSegment" => Some(&CONTAINS_KEYWORD_SEGMENT),
            "CallKeywordSegment" => Some(&CALL_KEYWORD_SEGMENT),
            "Trigger_nameKeywordSegment" => Some(&TRIGGER_NAME_KEYWORD_SEGMENT),
            "DepthKeywordSegment" => Some(&DEPTH_KEYWORD_SEGMENT),
            "GrantsKeywordSegment" => Some(&GRANTS_KEYWORD_SEGMENT),
            "WhenKeywordSegment" => Some(&WHEN_KEYWORD_SEGMENT),
            "OutputKeywordSegment" => Some(&OUTPUT_KEYWORD_SEGMENT),
            "SaveKeywordSegment" => Some(&SAVE_KEYWORD_SEGMENT),
            "AreKeywordSegment" => Some(&ARE_KEYWORD_SEGMENT),
            "UnlistenKeywordSegment" => Some(&UNLISTEN_KEYWORD_SEGMENT),
            "IdentifiedKeywordSegment" => Some(&IDENTIFIED_KEYWORD_SEGMENT),
            "Last_insert_idKeywordSegment" => Some(&LAST_INSERT_ID_KEYWORD_SEGMENT),
            "ImmediateKeywordSegment" => Some(&IMMEDIATE_KEYWORD_SEGMENT),
            "RealKeywordSegment" => Some(&REAL_KEYWORD_SEGMENT),
            "RequireKeywordSegment" => Some(&REQUIRE_KEYWORD_SEGMENT),
            "AccessKeywordSegment" => Some(&ACCESS_KEYWORD_SEGMENT),
            "ProcessKeywordSegment" => Some(&PROCESS_KEYWORD_SEGMENT),
            "FollowingKeywordSegment" => Some(&FOLLOWING_KEYWORD_SEGMENT),
            "HourKeywordSegment" => Some(&HOUR_KEYWORD_SEGMENT),
            "NormalizedKeywordSegment" => Some(&NORMALIZED_KEYWORD_SEGMENT),
            "Message_lengthKeywordSegment" => Some(&MESSAGE_LENGTH_KEYWORD_SEGMENT),
            "System_userKeywordSegment" => Some(&SYSTEM_USER_KEYWORD_SEGMENT),
            "TypeKeywordSegment" => Some(&TYPE_KEYWORD_SEGMENT),
            "ProceduresKeywordSegment" => Some(&PROCEDURES_KEYWORD_SEGMENT),
            "DelimitersKeywordSegment" => Some(&DELIMITERS_KEYWORD_SEGMENT),
            "InheritsKeywordSegment" => Some(&INHERITS_KEYWORD_SEGMENT),
            "End-execKeywordSegment" => Some(&END_EXEC_KEYWORD_SEGMENT),
            "PolicyKeywordSegment" => Some(&POLICY_KEYWORD_SEGMENT),
            "LocksKeywordSegment" => Some(&LOCKS_KEYWORD_SEGMENT),
            "CommitKeywordSegment" => Some(&COMMIT_KEYWORD_SEGMENT),
            "DelayedKeywordSegment" => Some(&DELAYED_KEYWORD_SEGMENT),
            "InfileKeywordSegment" => Some(&INFILE_KEYWORD_SEGMENT),
            "ScaleKeywordSegment" => Some(&SCALE_KEYWORD_SEGMENT),
            "TrailingKeywordSegment" => Some(&TRAILING_KEYWORD_SEGMENT),
            "OffsetsKeywordSegment" => Some(&OFFSETS_KEYWORD_SEGMENT),
            "RepeatKeywordSegment" => Some(&REPEAT_KEYWORD_SEGMENT),
            "WrapperKeywordSegment" => Some(&WRAPPER_KEYWORD_SEGMENT),
            "BetweenKeywordSegment" => Some(&BETWEEN_KEYWORD_SEGMENT),
            "MediumintKeywordSegment" => Some(&MEDIUMINT_KEYWORD_SEGMENT),
            "ClusterKeywordSegment" => Some(&CLUSTER_KEYWORD_SEGMENT),
            "MonitorKeywordSegment" => Some(&MONITOR_KEYWORD_SEGMENT),
            "FreetextKeywordSegment" => Some(&FREETEXT_KEYWORD_SEGMENT),
            "TasksKeywordSegment" => Some(&TASKS_KEYWORD_SEGMENT),
            "OpendatasourceKeywordSegment" => Some(&OPENDATASOURCE_KEYWORD_SEGMENT),
            "Subclass_originKeywordSegment" => Some(&SUBCLASS_ORIGIN_KEYWORD_SEGMENT),
            "ColumnsKeywordSegment" => Some(&COLUMNS_KEYWORD_SEGMENT),
            "Int1KeywordSegment" => Some(&INT1_KEYWORD_SEGMENT),
            "TinytextKeywordSegment" => Some(&TINYTEXT_KEYWORD_SEGMENT),
            "PathKeywordSegment" => Some(&PATH_KEYWORD_SEGMENT),
            "LikeKeywordSegment" => Some(&LIKE_KEYWORD_SEGMENT),
            "MillisecondKeywordSegment" => Some(&MILLISECOND_KEYWORD_SEGMENT),
            "CharacteristicsKeywordSegment" => Some(&CHARACTERISTICS_KEYWORD_SEGMENT),
            "EncodingKeywordSegment" => Some(&ENCODING_KEYWORD_SEGMENT),
            "MoveKeywordSegment" => Some(&MOVE_KEYWORD_SEGMENT),
            "SubstringKeywordSegment" => Some(&SUBSTRING_KEYWORD_SEGMENT),
            "MonthnameKeywordSegment" => Some(&MONTHNAME_KEYWORD_SEGMENT),
            "FromKeywordSegment" => Some(&FROM_KEYWORD_SEGMENT),
            "Sql_big_tablesKeywordSegment" => Some(&SQL_BIG_TABLES_KEYWORD_SEGMENT),
            "TiesKeywordSegment" => Some(&TIES_KEYWORD_SEGMENT),
            "CobolKeywordSegment" => Some(&COBOL_KEYWORD_SEGMENT),
            "MaxKeywordSegment" => Some(&MAX_KEYWORD_SEGMENT),
            "ClusteredKeywordSegment" => Some(&CLUSTERED_KEYWORD_SEGMENT),
            "Connection_nameKeywordSegment" => Some(&CONNECTION_NAME_KEYWORD_SEGMENT),
            "ValidKeywordSegment" => Some(&VALID_KEYWORD_SEGMENT),
            "SqlstateKeywordSegment" => Some(&SQLSTATE_KEYWORD_SEGMENT),
            "CreateKeywordSegment" => Some(&CREATE_KEYWORD_SEGMENT),
            "Max_rowsKeywordSegment" => Some(&MAX_ROWS_KEYWORD_SEGMENT),
            "DelimiterKeywordSegment" => Some(&DELIMITER_KEYWORD_SEGMENT),
            "DefaultsKeywordSegment" => Some(&DEFAULTS_KEYWORD_SEGMENT),
            "BernoulliKeywordSegment" => Some(&BERNOULLI_KEYWORD_SEGMENT),
            "ModeKeywordSegment" => Some(&MODE_KEYWORD_SEGMENT),
            "Sql_big_selectsKeywordSegment" => Some(&SQL_BIG_SELECTS_KEYWORD_SEGMENT),
            "ChangeKeywordSegment" => Some(&CHANGE_KEYWORD_SEGMENT),
            "CastKeywordSegment" => Some(&CAST_KEYWORD_SEGMENT),
            "CascadeKeywordSegment" => Some(&CASCADE_KEYWORD_SEGMENT),
            "KeysKeywordSegment" => Some(&KEYS_KEYWORD_SEGMENT),
            "Routine_catalogKeywordSegment" => Some(&ROUTINE_CATALOG_KEYWORD_SEGMENT),
            "FlushKeywordSegment" => Some(&FLUSH_KEYWORD_SEGMENT),
            "SourceKeywordSegment" => Some(&SOURCE_KEYWORD_SEGMENT),
            "PowerKeywordSegment" => Some(&POWER_KEYWORD_SEGMENT),
            "ThenKeywordSegment" => Some(&THEN_KEYWORD_SEGMENT),
            "ConstraintsKeywordSegment" => Some(&CONSTRAINTS_KEYWORD_SEGMENT),
            "ResourceKeywordSegment" => Some(&RESOURCE_KEYWORD_SEGMENT),
            "Character_set_nameKeywordSegment" => Some(&CHARACTER_SET_NAME_KEYWORD_SEGMENT),
            "Constraint_nameKeywordSegment" => Some(&CONSTRAINT_NAME_KEYWORD_SEGMENT),
            "HierarchyKeywordSegment" => Some(&HIERARCHY_KEYWORD_SEGMENT),
            "AbsKeywordSegment" => Some(&ABS_KEYWORD_SEGMENT),
            "NationalKeywordSegment" => Some(&NATIONAL_KEYWORD_SEGMENT),
            "RoutinesKeywordSegment" => Some(&ROUTINES_KEYWORD_SEGMENT),
            "SharesKeywordSegment" => Some(&SHARES_KEYWORD_SEGMENT),
            "RestrictKeywordSegment" => Some(&RESTRICT_KEYWORD_SEGMENT),
            "OpenxmlKeywordSegment" => Some(&OPENXML_KEYWORD_SEGMENT),
            "ValuesKeywordSegment" => Some(&VALUES_KEYWORD_SEGMENT),
            "OrdinalityKeywordSegment" => Some(&ORDINALITY_KEYWORD_SEGMENT),
            "FinalKeywordSegment" => Some(&FINAL_KEYWORD_SEGMENT),
            "Utc_dateKeywordSegment" => Some(&UTC_DATE_KEYWORD_SEGMENT),
            "WorkKeywordSegment" => Some(&WORK_KEYWORD_SEGMENT),
            "NextKeywordSegment" => Some(&NEXT_KEYWORD_SEGMENT),
            "Parameter_specific_schemaKeywordSegment" => Some(&PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT),
            "UpdatetextKeywordSegment" => Some(&UPDATETEXT_KEYWORD_SEGMENT),
            "InfixKeywordSegment" => Some(&INFIX_KEYWORD_SEGMENT),
            "CollateKeywordSegment" => Some(&COLLATE_KEYWORD_SEGMENT),
            "SubmultisetKeywordSegment" => Some(&SUBMULTISET_KEYWORD_SEGMENT),
            "DomainKeywordSegment" => Some(&DOMAIN_KEYWORD_SEGMENT),
            "SequenceKeywordSegment" => Some(&SEQUENCE_KEYWORD_SEGMENT),
            "TruncateKeywordSegment" => Some(&TRUNCATE_KEYWORD_SEGMENT),
            "DaysKeywordSegment" => Some(&DAYS_KEYWORD_SEGMENT),
            "DefinedKeywordSegment" => Some(&DEFINED_KEYWORD_SEGMENT),
            "MediumblobKeywordSegment" => Some(&MEDIUMBLOB_KEYWORD_SEGMENT),
            "PrefixKeywordSegment" => Some(&PREFIX_KEYWORD_SEGMENT),
            "UsersKeywordSegment" => Some(&USERS_KEYWORD_SEGMENT),
            "AuditKeywordSegment" => Some(&AUDIT_KEYWORD_SEGMENT),
            "HeaderKeywordSegment" => Some(&HEADER_KEYWORD_SEGMENT),
            "NosuperuserKeywordSegment" => Some(&NOSUPERUSER_KEYWORD_SEGMENT),
            "SetuserKeywordSegment" => Some(&SETUSER_KEYWORD_SEGMENT),
            "NocycleKeywordSegment" => Some(&NOCYCLE_KEYWORD_SEGMENT),
            "SecondKeywordSegment" => Some(&SECOND_KEYWORD_SEGMENT),
            "Day_secondKeywordSegment" => Some(&DAY_SECOND_KEYWORD_SEGMENT),
            "ExcludingKeywordSegment" => Some(&EXCLUDING_KEYWORD_SEGMENT),
            "UpdateKeywordSegment" => Some(&UPDATE_KEYWORD_SEGMENT),
            "ViewKeywordSegment" => Some(&VIEW_KEYWORD_SEGMENT),
            "KeyKeywordSegment" => Some(&KEY_KEYWORD_SEGMENT),
            "Server_nameKeywordSegment" => Some(&SERVER_NAME_KEYWORD_SEGMENT),
            "WarehousesKeywordSegment" => Some(&WAREHOUSES_KEYWORD_SEGMENT),
            "IsnullKeywordSegment" => Some(&ISNULL_KEYWORD_SEGMENT),
            "CoalesceKeywordSegment" => Some(&COALESCE_KEYWORD_SEGMENT),
            "NoKeywordSegment" => Some(&NO_KEYWORD_SEGMENT),
            "BreakKeywordSegment" => Some(&BREAK_KEYWORD_SEGMENT),
            "InvokerKeywordSegment" => Some(&INVOKER_KEYWORD_SEGMENT),
            "HandlerKeywordSegment" => Some(&HANDLER_KEYWORD_SEGMENT),
            "ConversionKeywordSegment" => Some(&CONVERSION_KEYWORD_SEGMENT),
            "LoginKeywordSegment" => Some(&LOGIN_KEYWORD_SEGMENT),
            "ServerKeywordSegment" => Some(&SERVER_KEYWORD_SEGMENT),
            "PreparedKeywordSegment" => Some(&PREPARED_KEYWORD_SEGMENT),
            "TransformKeywordSegment" => Some(&TRANSFORM_KEYWORD_SEGMENT),
            "VarcharacterKeywordSegment" => Some(&VARCHARACTER_KEYWORD_SEGMENT),
            "Scope_nameKeywordSegment" => Some(&SCOPE_NAME_KEYWORD_SEGMENT),
            "DateKeywordSegment" => Some(&DATE_KEYWORD_SEGMENT),
            "ForceKeywordSegment" => Some(&FORCE_KEYWORD_SEGMENT),
            "ParametersKeywordSegment" => Some(&PARAMETERS_KEYWORD_SEGMENT),
            "Session_userKeywordSegment" => Some(&SESSION_USER_KEYWORD_SEGMENT),
            "PrecedingKeywordSegment" => Some(&PRECEDING_KEYWORD_SEGMENT),
            "SecurityKeywordSegment" => Some(&SECURITY_KEYWORD_SEGMENT),
            "DayofmonthKeywordSegment" => Some(&DAYOFMONTH_KEYWORD_SEGMENT),
            "LongKeywordSegment" => Some(&LONG_KEYWORD_SEGMENT),
            "StartKeywordSegment" => Some(&START_KEYWORD_SEGMENT),
            "Covar_sampKeywordSegment" => Some(&COVAR_SAMP_KEYWORD_SEGMENT),
            "SuccessfulKeywordSegment" => Some(&SUCCESSFUL_KEYWORD_SEGMENT),
            "ImplicitKeywordSegment" => Some(&IMPLICIT_KEYWORD_SEGMENT),
            "Minute_secondKeywordSegment" => Some(&MINUTE_SECOND_KEYWORD_SEGMENT),
            "NowaitKeywordSegment" => Some(&NOWAIT_KEYWORD_SEGMENT),
            "Regr_avgxKeywordSegment" => Some(&REGR_AVGX_KEYWORD_SEGMENT),
            "UserKeywordSegment" => Some(&USER_KEYWORD_SEGMENT),
            "CloseKeywordSegment" => Some(&CLOSE_KEYWORD_SEGMENT),
            "TaskKeywordSegment" => Some(&TASK_KEYWORD_SEGMENT),
            "MKeywordSegment" => Some(&M_KEYWORD_SEGMENT),
            "MergeKeywordSegment" => Some(&MERGE_KEYWORD_SEGMENT),
            "StorageKeywordSegment" => Some(&STORAGE_KEYWORD_SEGMENT),
            "Cursor_nameKeywordSegment" => Some(&CURSOR_NAME_KEYWORD_SEGMENT),
            "ImportedKeywordSegment" => Some(&IMPORTED_KEYWORD_SEGMENT),
            "ExistingKeywordSegment" => Some(&EXISTING_KEYWORD_SEGMENT),
            "LevelKeywordSegment" => Some(&LEVEL_KEYWORD_SEGMENT),
            "EveryKeywordSegment" => Some(&EVERY_KEYWORD_SEGMENT),
            "PrivilegesKeywordSegment" => Some(&PRIVILEGES_KEYWORD_SEGMENT),
            "PrimaryKeywordSegment" => Some(&PRIMARY_KEYWORD_SEGMENT),
            "InputKeywordSegment" => Some(&INPUT_KEYWORD_SEGMENT),
            "SqlerrorKeywordSegment" => Some(&SQLERROR_KEYWORD_SEGMENT),
            "NclobKeywordSegment" => Some(&NCLOB_KEYWORD_SEGMENT),
            "GoKeywordSegment" => Some(&GO_KEYWORD_SEGMENT),
            "NotnullKeywordSegment" => Some(&NOTNULL_KEYWORD_SEGMENT),
            "Sql_small_resultKeywordSegment" => Some(&SQL_SMALL_RESULT_KEYWORD_SEGMENT),
            "TranKeywordSegment" => Some(&TRAN_KEYWORD_SEGMENT),
            "NoorderKeywordSegment" => Some(&NOORDER_KEYWORD_SEGMENT),
            "OnlyKeywordSegment" => Some(&ONLY_KEYWORD_SEGMENT),
            "SqlwarningKeywordSegment" => Some(&SQLWARNING_KEYWORD_SEGMENT),
            "Current_dateKeywordSegment" => Some(&CURRENT_DATE_KEYWORD_SEGMENT),
            "OidsKeywordSegment" => Some(&OIDS_KEYWORD_SEGMENT),
            "FirstKeywordSegment" => Some(&FIRST_KEYWORD_SEGMENT),
            "ExecKeywordSegment" => Some(&EXEC_KEYWORD_SEGMENT),
            "StatisticsKeywordSegment" => Some(&STATISTICS_KEYWORD_SEGMENT),
            "ReplaceKeywordSegment" => Some(&REPLACE_KEYWORD_SEGMENT),
            "RoutineKeywordSegment" => Some(&ROUTINE_KEYWORD_SEGMENT),
            "TrimKeywordSegment" => Some(&TRIM_KEYWORD_SEGMENT),
            "QuarterKeywordSegment" => Some(&QUARTER_KEYWORD_SEGMENT),
            "WithinKeywordSegment" => Some(&WITHIN_KEYWORD_SEGMENT),
            "DayofyearKeywordSegment" => Some(&DAYOFYEAR_KEYWORD_SEGMENT),
            "ReferencingKeywordSegment" => Some(&REFERENCING_KEYWORD_SEGMENT),
            "RaiserrorKeywordSegment" => Some(&RAISERROR_KEYWORD_SEGMENT),
            "Utc_timestampKeywordSegment" => Some(&UTC_TIMESTAMP_KEYWORD_SEGMENT),
            "OfflineKeywordSegment" => Some(&OFFLINE_KEYWORD_SEGMENT),
            "AttributeKeywordSegment" => Some(&ATTRIBUTE_KEYWORD_SEGMENT),
            "DiskKeywordSegment" => Some(&DISK_KEYWORD_SEGMENT),
            "Regr_countKeywordSegment" => Some(&REGR_COUNT_KEYWORD_SEGMENT),
            "ReconfigureKeywordSegment" => Some(&RECONFIGURE_KEYWORD_SEGMENT),
            "RepeatableKeywordSegment" => Some(&REPEATABLE_KEYWORD_SEGMENT),
            "PadKeywordSegment" => Some(&PAD_KEYWORD_SEGMENT),
            "Message_textKeywordSegment" => Some(&MESSAGE_TEXT_KEYWORD_SEGMENT),
            "EncryptedKeywordSegment" => Some(&ENCRYPTED_KEYWORD_SEGMENT),
            "SynonymKeywordSegment" => Some(&SYNONYM_KEYWORD_SEGMENT),
            "NullifKeywordSegment" => Some(&NULLIF_KEYWORD_SEGMENT),
            "ObjectKeywordSegment" => Some(&OBJECT_KEYWORD_SEGMENT),
            "GeneralKeywordSegment" => Some(&GENERAL_KEYWORD_SEGMENT),
            "LongblobKeywordSegment" => Some(&LONGBLOB_KEYWORD_SEGMENT),
            "AdminKeywordSegment" => Some(&ADMIN_KEYWORD_SEGMENT),
            "InoutKeywordSegment" => Some(&INOUT_KEYWORD_SEGMENT),
            "NonclusteredKeywordSegment" => Some(&NONCLUSTERED_KEYWORD_SEGMENT),
            "ChainKeywordSegment" => Some(&CHAIN_KEYWORD_SEGMENT),
            "OptionallyKeywordSegment" => Some(&OPTIONALLY_KEYWORD_SEGMENT),
            "SqlexceptionKeywordSegment" => Some(&SQLEXCEPTION_KEYWORD_SEGMENT),
            "QualifyKeywordSegment" => Some(&QUALIFY_KEYWORD_SEGMENT),
            "WhereKeywordSegment" => Some(&WHERE_KEYWORD_SEGMENT),
            "WriteKeywordSegment" => Some(&WRITE_KEYWORD_SEGMENT),
            "GreatestKeywordSegment" => Some(&GREATEST_KEYWORD_SEGMENT),
            "PartialKeywordSegment" => Some(&PARTIAL_KEYWORD_SEGMENT),
            "VacuumKeywordSegment" => Some(&VACUUM_KEYWORD_SEGMENT),
            "PriorKeywordSegment" => Some(&PRIOR_KEYWORD_SEGMENT),
            "GlobalKeywordSegment" => Some(&GLOBAL_KEYWORD_SEGMENT),
            "StableKeywordSegment" => Some(&STABLE_KEYWORD_SEGMENT),
            "ReadKeywordSegment" => Some(&READ_KEYWORD_SEGMENT),
            "Utc_timeKeywordSegment" => Some(&UTC_TIME_KEYWORD_SEGMENT),
            "RowcountKeywordSegment" => Some(&ROWCOUNT_KEYWORD_SEGMENT),
            "AsymmetricKeywordSegment" => Some(&ASYMMETRIC_KEYWORD_SEGMENT),
            "DayofweekKeywordSegment" => Some(&DAYOFWEEK_KEYWORD_SEGMENT),
            "TopKeywordSegment" => Some(&TOP_KEYWORD_SEGMENT),
            "AggregateKeywordSegment" => Some(&AGGREGATE_KEYWORD_SEGMENT),
            "StdoutKeywordSegment" => Some(&STDOUT_KEYWORD_SEGMENT),
            "Current_pathKeywordSegment" => Some(&CURRENT_PATH_KEYWORD_SEGMENT),
            "RegexpKeywordSegment" => Some(&REGEXP_KEYWORD_SEGMENT),
            "Regr_syyKeywordSegment" => Some(&REGR_SYY_KEYWORD_SEGMENT),
            "Table_nameKeywordSegment" => Some(&TABLE_NAME_KEYWORD_SEGMENT),
            "ConnectKeywordSegment" => Some(&CONNECT_KEYWORD_SEGMENT),
            "LogsKeywordSegment" => Some(&LOGS_KEYWORD_SEGMENT),
            "DegreeKeywordSegment" => Some(&DEGREE_KEYWORD_SEGMENT),
            "LastKeywordSegment" => Some(&LAST_KEYWORD_SEGMENT),
            "DummyKeywordSegment" => Some(&DUMMY_KEYWORD_SEGMENT),
            "UnderKeywordSegment" => Some(&UNDER_KEYWORD_SEGMENT),
            "DecKeywordSegment" => Some(&DEC_KEYWORD_SEGMENT),
            "BackupKeywordSegment" => Some(&BACKUP_KEYWORD_SEGMENT),
            "Sql_big_resultKeywordSegment" => Some(&SQL_BIG_RESULT_KEYWORD_SEGMENT),
            "DiagnosticsKeywordSegment" => Some(&DIAGNOSTICS_KEYWORD_SEGMENT),
            "TablesampleKeywordSegment" => Some(&TABLESAMPLE_KEYWORD_SEGMENT),
            "AuthorizationKeywordSegment" => Some(&AUTHORIZATION_KEYWORD_SEGMENT),
            "Varchar2KeywordSegment" => Some(&VARCHAR2_KEYWORD_SEGMENT),
            "AvgKeywordSegment" => Some(&AVG_KEYWORD_SEGMENT),
            "DictionaryKeywordSegment" => Some(&DICTIONARY_KEYWORD_SEGMENT),
            "TrustedKeywordSegment" => Some(&TRUSTED_KEYWORD_SEGMENT),
            "StrictKeywordSegment" => Some(&STRICT_KEYWORD_SEGMENT),
            "Minute_microsecondKeywordSegment" => Some(&MINUTE_MICROSECOND_KEYWORD_SEGMENT),
            "CreateroleKeywordSegment" => Some(&CREATEROLE_KEYWORD_SEGMENT),
            "CompletionKeywordSegment" => Some(&COMPLETION_KEYWORD_SEGMENT),
            "OpenKeywordSegment" => Some(&OPEN_KEYWORD_SEGMENT),
            "RowguidcolKeywordSegment" => Some(&ROWGUIDCOL_KEYWORD_SEGMENT),
            "PrintKeywordSegment" => Some(&PRINT_KEYWORD_SEGMENT),
            "WritetextKeywordSegment" => Some(&WRITETEXT_KEYWORD_SEGMENT),
            "ElseKeywordSegment" => Some(&ELSE_KEYWORD_SEGMENT),
            "Column_nameKeywordSegment" => Some(&COLUMN_NAME_KEYWORD_SEGMENT),
            "User_defined_type_schemaKeywordSegment" => Some(&USER_DEFINED_TYPE_SCHEMA_KEYWORD_SEGMENT),
            "Day_microsecondKeywordSegment" => Some(&DAY_MICROSECOND_KEYWORD_SEGMENT),
            "SerializableKeywordSegment" => Some(&SERIALIZABLE_KEYWORD_SEGMENT),
            "Returned_lengthKeywordSegment" => Some(&RETURNED_LENGTH_KEYWORD_SEGMENT),
            "ZerofillKeywordSegment" => Some(&ZEROFILL_KEYWORD_SEGMENT),
            "AbsoluteKeywordSegment" => Some(&ABSOLUTE_KEYWORD_SEGMENT),
            "CurrentKeywordSegment" => Some(&CURRENT_KEYWORD_SEGMENT),
            "Collation_catalogKeywordSegment" => Some(&COLLATION_CATALOG_KEYWORD_SEGMENT),
            "OthersKeywordSegment" => Some(&OTHERS_KEYWORD_SEGMENT),
            "AtomicKeywordSegment" => Some(&ATOMIC_KEYWORD_SEGMENT),
            "Top_level_countKeywordSegment" => Some(&TOP_LEVEL_COUNT_KEYWORD_SEGMENT),
            "CheckpointKeywordSegment" => Some(&CHECKPOINT_KEYWORD_SEGMENT),
            "RownumKeywordSegment" => Some(&ROWNUM_KEYWORD_SEGMENT),
            "ElseifKeywordSegment" => Some(&ELSEIF_KEYWORD_SEGMENT),
            "StagesKeywordSegment" => Some(&STAGES_KEYWORD_SEGMENT),
            "ErrlvlKeywordSegment" => Some(&ERRLVL_KEYWORD_SEGMENT),
            "SmallintKeywordSegment" => Some(&SMALLINT_KEYWORD_SEGMENT),
            "ReplicationKeywordSegment" => Some(&REPLICATION_KEYWORD_SEGMENT),
            "ElementKeywordSegment" => Some(&ELEMENT_KEYWORD_SEGMENT),
            "Float8KeywordSegment" => Some(&FLOAT8_KEYWORD_SEGMENT),
            "OutKeywordSegment" => Some(&OUT_KEYWORD_SEGMENT),
            "NocompressKeywordSegment" => Some(&NOCOMPRESS_KEYWORD_SEGMENT),
            "DenyKeywordSegment" => Some(&DENY_KEYWORD_SEGMENT),
            "ModifiesKeywordSegment" => Some(&MODIFIES_KEYWORD_SEGMENT),
            "OwnershipKeywordSegment" => Some(&OWNERSHIP_KEYWORD_SEGMENT),
            "Sql_select_limitKeywordSegment" => Some(&SQL_SELECT_LIMIT_KEYWORD_SEGMENT),
            "GroupingKeywordSegment" => Some(&GROUPING_KEYWORD_SEGMENT),
            "NocreateroleKeywordSegment" => Some(&NOCREATEROLE_KEYWORD_SEGMENT),
            "LessKeywordSegment" => Some(&LESS_KEYWORD_SEGMENT),
            "SpecifictypeKeywordSegment" => Some(&SPECIFICTYPE_KEYWORD_SEGMENT),
            "ExclusiveKeywordSegment" => Some(&EXCLUSIVE_KEYWORD_SEGMENT),
            "TransactionKeywordSegment" => Some(&TRANSACTION_KEYWORD_SEGMENT),
            "HavingKeywordSegment" => Some(&HAVING_KEYWORD_SEGMENT),
            "ExplainKeywordSegment" => Some(&EXPLAIN_KEYWORD_SEGMENT),
            "Current_userKeywordSegment" => Some(&CURRENT_USER_KEYWORD_SEGMENT),
            "CharacterKeywordSegment" => Some(&CHARACTER_KEYWORD_SEGMENT),
            "SymmetricKeywordSegment" => Some(&SYMMETRIC_KEYWORD_SEGMENT),
            "CollectKeywordSegment" => Some(&COLLECT_KEYWORD_SEGMENT),
            "DeterministicKeywordSegment" => Some(&DETERMINISTIC_KEYWORD_SEGMENT),
            "DescriptorKeywordSegment" => Some(&DESCRIPTOR_KEYWORD_SEGMENT),
            "UnencryptedKeywordSegment" => Some(&UNENCRYPTED_KEYWORD_SEGMENT),
            "ReleaseKeywordSegment" => Some(&RELEASE_KEYWORD_SEGMENT),
            "KKeywordSegment" => Some(&K_KEYWORD_SEGMENT),
            "FulltextKeywordSegment" => Some(&FULLTEXT_KEYWORD_SEGMENT),
            "Transaction_activeKeywordSegment" => Some(&TRANSACTION_ACTIVE_KEYWORD_SEGMENT),
            "FunctionsKeywordSegment" => Some(&FUNCTIONS_KEYWORD_SEGMENT),
            "Reference_usageKeywordSegment" => Some(&REFERENCE_USAGE_KEYWORD_SEGMENT),
            "Timezone_minuteKeywordSegment" => Some(&TIMEZONE_MINUTE_KEYWORD_SEGMENT),
            "XorKeywordSegment" => Some(&XOR_KEYWORD_SEGMENT),
            "StartsKeywordSegment" => Some(&STARTS_KEYWORD_SEGMENT),
            "IndexKeywordSegment" => Some(&INDEX_KEYWORD_SEGMENT),
            "NocreateuserKeywordSegment" => Some(&NOCREATEUSER_KEYWORD_SEGMENT),
            "CharKeywordSegment" => Some(&CHAR_KEYWORD_SEGMENT),
            "DivKeywordSegment" => Some(&DIV_KEYWORD_SEGMENT),
            "ObjectsKeywordSegment" => Some(&OBJECTS_KEYWORD_SEGMENT),
            "SomeKeywordSegment" => Some(&SOME_KEYWORD_SEGMENT),
            "TinyblobKeywordSegment" => Some(&TINYBLOB_KEYWORD_SEGMENT),
            "UncommittedKeywordSegment" => Some(&UNCOMMITTED_KEYWORD_SEGMENT),
            "CacheKeywordSegment" => Some(&CACHE_KEYWORD_SEGMENT),
            "ReferencesKeywordSegment" => Some(&REFERENCES_KEYWORD_SEGMENT),
            "StreamsKeywordSegment" => Some(&STREAMS_KEYWORD_SEGMENT),
            "GetKeywordSegment" => Some(&GET_KEYWORD_SEGMENT),
            "CatalogKeywordSegment" => Some(&CATALOG_KEYWORD_SEGMENT),
            "InheritKeywordSegment" => Some(&INHERIT_KEYWORD_SEGMENT),
            "BoolKeywordSegment" => Some(&BOOL_KEYWORD_SEGMENT),
            "CascadedKeywordSegment" => Some(&CASCADED_KEYWORD_SEGMENT),
            "ProcesslistKeywordSegment" => Some(&PROCESSLIST_KEYWORD_SEGMENT),
            "AlwaysKeywordSegment" => Some(&ALWAYS_KEYWORD_SEGMENT),
            "DisconnectKeywordSegment" => Some(&DISCONNECT_KEYWORD_SEGMENT),
            "DistinctrowKeywordSegment" => Some(&DISTINCTROW_KEYWORD_SEGMENT),
            "Regr_sxyKeywordSegment" => Some(&REGR_SXY_KEYWORD_SEGMENT),
            "TemporaryKeywordSegment" => Some(&TEMPORARY_KEYWORD_SEGMENT),
            "ShowKeywordSegment" => Some(&SHOW_KEYWORD_SEGMENT),
            "EnableKeywordSegment" => Some(&ENABLE_KEYWORD_SEGMENT),
            "ApplyKeywordSegment" => Some(&APPLY_KEYWORD_SEGMENT),
            "PascalKeywordSegment" => Some(&PASCAL_KEYWORD_SEGMENT),
            "ArrayKeywordSegment" => Some(&ARRAY_KEYWORD_SEGMENT),
            "TranslationKeywordSegment" => Some(&TRANSLATION_KEYWORD_SEGMENT),
            "RuleKeywordSegment" => Some(&RULE_KEYWORD_SEGMENT),
            "OffsetKeywordSegment" => Some(&OFFSET_KEYWORD_SEGMENT),
            "DoKeywordSegment" => Some(&DO_KEYWORD_SEGMENT),
            "MatchKeywordSegment" => Some(&MATCH_KEYWORD_SEGMENT),
            "ThanKeywordSegment" => Some(&THAN_KEYWORD_SEGMENT),
            "Catalog_nameKeywordSegment" => Some(&CATALOG_NAME_KEYWORD_SEGMENT),
            "ConvertKeywordSegment" => Some(&CONVERT_KEYWORD_SEGMENT),
            "BeginKeywordSegment" => Some(&BEGIN_KEYWORD_SEGMENT),
            "Row_countKeywordSegment" => Some(&ROW_COUNT_KEYWORD_SEGMENT),
            "UnnestKeywordSegment" => Some(&UNNEST_KEYWORD_SEGMENT),
            "AsKeywordSegment" => Some(&AS_KEYWORD_SEGMENT),
            "CharactersKeywordSegment" => Some(&CHARACTERS_KEYWORD_SEGMENT),
            "ListenKeywordSegment" => Some(&LISTEN_KEYWORD_SEGMENT),
            "Delay_key_writeKeywordSegment" => Some(&DELAY_KEY_WRITE_KEYWORD_SEGMENT),
            "NocreatedbKeywordSegment" => Some(&NOCREATEDB_KEYWORD_SEGMENT),
            "SpaceKeywordSegment" => Some(&SPACE_KEYWORD_SEGMENT),
            "Timezone_hourKeywordSegment" => Some(&TIMEZONE_HOUR_KEYWORD_SEGMENT),
            "TemplateKeywordSegment" => Some(&TEMPLATE_KEYWORD_SEGMENT),
            "Percentile_discKeywordSegment" => Some(&PERCENTILE_DISC_KEYWORD_SEGMENT),
            "ReturnsKeywordSegment" => Some(&RETURNS_KEYWORD_SEGMENT),
            "LinenoKeywordSegment" => Some(&LINENO_KEYWORD_SEGMENT),
            "TreatKeywordSegment" => Some(&TREAT_KEYWORD_SEGMENT),
            "MonthKeywordSegment" => Some(&MONTH_KEYWORD_SEGMENT),
            "NotifyKeywordSegment" => Some(&NOTIFY_KEYWORD_SEGMENT),
            "TextKeywordSegment" => Some(&TEXT_KEYWORD_SEGMENT),
            "RankKeywordSegment" => Some(&RANK_KEYWORD_SEGMENT),
            "NoauditKeywordSegment" => Some(&NOAUDIT_KEYWORD_SEGMENT),
            "FetchKeywordSegment" => Some(&FETCH_KEYWORD_SEGMENT),
            "UpperKeywordSegment" => Some(&UPPER_KEYWORD_SEGMENT),
            "Min_rowsKeywordSegment" => Some(&MIN_ROWS_KEYWORD_SEGMENT),
            "Scope_schemaKeywordSegment" => Some(&SCOPE_SCHEMA_KEYWORD_SEGMENT),
            "Message_octet_lengthKeywordSegment" => Some(&MESSAGE_OCTET_LENGTH_KEYWORD_SEGMENT),
            "LocaltimeKeywordSegment" => Some(&LOCALTIME_KEYWORD_SEGMENT),
            "ResetKeywordSegment" => Some(&RESET_KEYWORD_SEGMENT),
            "VariablesKeywordSegment" => Some(&VARIABLES_KEYWORD_SEGMENT),
            "IntersectionKeywordSegment" => Some(&INTERSECTION_KEYWORD_SEGMENT),
            "OverwriteKeywordSegment" => Some(&OVERWRITE_KEYWORD_SEGMENT),
            "CursorKeywordSegment" => Some(&CURSOR_KEYWORD_SEGMENT),
            "VariableKeywordSegment" => Some(&VARIABLE_KEYWORD_SEGMENT),
            "SqlcodeKeywordSegment" => Some(&SQLCODE_KEYWORD_SEGMENT),
            "ExcludeKeywordSegment" => Some(&EXCLUDE_KEYWORD_SEGMENT),
            "IncrementKeywordSegment" => Some(&INCREMENT_KEYWORD_SEGMENT),
            "RecursiveKeywordSegment" => Some(&RECURSIVE_KEYWORD_SEGMENT),
            "UseKeywordSegment" => Some(&USE_KEYWORD_SEGMENT),
            "DbccKeywordSegment" => Some(&DBCC_KEYWORD_SEGMENT),
            "Stddev_sampKeywordSegment" => Some(&STDDEV_SAMP_KEYWORD_SEGMENT),
            "ExitKeywordSegment" => Some(&EXIT_KEYWORD_SEGMENT),
            "Condition_numberKeywordSegment" => Some(&CONDITION_NUMBER_KEYWORD_SEGMENT),
            "Day_hourKeywordSegment" => Some(&DAY_HOUR_KEYWORD_SEGMENT),
            "OverlayKeywordSegment" => Some(&OVERLAY_KEYWORD_SEGMENT),
            "DestroyKeywordSegment" => Some(&DESTROY_KEYWORD_SEGMENT),
            "PipeKeywordSegment" => Some(&PIPE_KEYWORD_SEGMENT),
            "WeekdayKeywordSegment" => Some(&WEEKDAY_KEYWORD_SEGMENT),
            "TablespaceKeywordSegment" => Some(&TABLESPACE_KEYWORD_SEGMENT),
            "Regr_slopeKeywordSegment" => Some(&REGR_SLOPE_KEYWORD_SEGMENT),
            "CheckKeywordSegment" => Some(&CHECK_KEYWORD_SEGMENT),
            "ViewsKeywordSegment" => Some(&VIEWS_KEYWORD_SEGMENT),
            "CheckedKeywordSegment" => Some(&CHECKED_KEYWORD_SEGMENT),
            "DeclareKeywordSegment" => Some(&DECLARE_KEYWORD_SEGMENT),
            "DeferrableKeywordSegment" => Some(&DEFERRABLE_KEYWORD_SEGMENT),
            "BackwardKeywordSegment" => Some(&BACKWARD_KEYWORD_SEGMENT),
            "DistinctKeywordSegment" => Some(&DISTINCT_KEYWORD_SEGMENT),
            "NoneKeywordSegment" => Some(&NONE_KEYWORD_SEGMENT),
            "IterateKeywordSegment" => Some(&ITERATE_KEYWORD_SEGMENT),
            "SonameKeywordSegment" => Some(&SONAME_KEYWORD_SEGMENT),
            "OnlineKeywordSegment" => Some(&ONLINE_KEYWORD_SEGMENT),
            "ExpKeywordSegment" => Some(&EXP_KEYWORD_SEGMENT),
            "RangeKeywordSegment" => Some(&RANGE_KEYWORD_SEGMENT),
            "ExecutionKeywordSegment" => Some(&EXECUTION_KEYWORD_SEGMENT),
            "IsamKeywordSegment" => Some(&ISAM_KEYWORD_SEGMENT),
            "AssertionKeywordSegment" => Some(&ASSERTION_KEYWORD_SEGMENT),
            "ExistsKeywordSegment" => Some(&EXISTS_KEYWORD_SEGMENT),
            "Second_microsecondKeywordSegment" => Some(&SECOND_MICROSECOND_KEYWORD_SEGMENT),
            "SqlcaKeywordSegment" => Some(&SQLCA_KEYWORD_SEGMENT),
            "ZoneKeywordSegment" => Some(&ZONE_KEYWORD_SEGMENT),
            "CollationKeywordSegment" => Some(&COLLATION_KEYWORD_SEGMENT),
            "TransactionsKeywordSegment" => Some(&TRANSACTIONS_KEYWORD_SEGMENT),
            "IdentityKeywordSegment" => Some(&IDENTITY_KEYWORD_SEGMENT),
            "NumberKeywordSegment" => Some(&NUMBER_KEYWORD_SEGMENT),
            "TsequalKeywordSegment" => Some(&TSEQUAL_KEYWORD_SEGMENT),
            "PreorderKeywordSegment" => Some(&PREORDER_KEYWORD_SEGMENT),
            "Scope_catalogKeywordSegment" => Some(&SCOPE_CATALOG_KEYWORD_SEGMENT),
            "Key_typeKeywordSegment" => Some(&KEY_TYPE_KEYWORD_SEGMENT),
            "ProcKeywordSegment" => Some(&PROC_KEYWORD_SEGMENT),
            "InsteadKeywordSegment" => Some(&INSTEAD_KEYWORD_SEGMENT),
            "PlanKeywordSegment" => Some(&PLAN_KEYWORD_SEGMENT),
            "RenameKeywordSegment" => Some(&RENAME_KEYWORD_SEGMENT),
            "Collation_nameKeywordSegment" => Some(&COLLATION_NAME_KEYWORD_SEGMENT),
            "WithKeywordSegment" => Some(&WITH_KEYWORD_SEGMENT),
            "IdentitycolKeywordSegment" => Some(&IDENTITYCOL_KEYWORD_SEGMENT),
            "EndKeywordSegment" => Some(&END_KEYWORD_SEGMENT),
            "MaskingKeywordSegment" => Some(&MASKING_KEYWORD_SEGMENT),
            "Dense_rankKeywordSegment" => Some(&DENSE_RANK_KEYWORD_SEGMENT),
            "ImmutableKeywordSegment" => Some(&IMMUTABLE_KEYWORD_SEGMENT),
            "DeferredKeywordSegment" => Some(&DEFERRED_KEYWORD_SEGMENT),
            "GeneratedKeywordSegment" => Some(&GENERATED_KEYWORD_SEGMENT),
            "PrecisionKeywordSegment" => Some(&PRECISION_KEYWORD_SEGMENT),
            "MediumtextKeywordSegment" => Some(&MEDIUMTEXT_KEYWORD_SEGMENT),
            "FillfactorKeywordSegment" => Some(&FILLFACTOR_KEYWORD_SEGMENT),
            "IncludeKeywordSegment" => Some(&INCLUDE_KEYWORD_SEGMENT),
            "Transactions_rolled_backKeywordSegment" => Some(&TRANSACTIONS_ROLLED_BACK_KEYWORD_SEGMENT),
            "OldKeywordSegment" => Some(&OLD_KEYWORD_SEGMENT),
            "Schema_nameKeywordSegment" => Some(&SCHEMA_NAME_KEYWORD_SEGMENT),
            "LargeKeywordSegment" => Some(&LARGE_KEYWORD_SEGMENT),
            "ExtensionKeywordSegment" => Some(&EXTENSION_KEYWORD_SEGMENT),
            "SetsKeywordSegment" => Some(&SETS_KEYWORD_SEGMENT),
            "ShareKeywordSegment" => Some(&SHARE_KEYWORD_SEGMENT),
            "VersionKeywordSegment" => Some(&VERSION_KEYWORD_SEGMENT),
            "Avg_row_lengthKeywordSegment" => Some(&AVG_ROW_LENGTH_KEYWORD_SEGMENT),
            "ManageKeywordSegment" => Some(&MANAGE_KEYWORD_SEGMENT),
            "ContainstableKeywordSegment" => Some(&CONTAINSTABLE_KEYWORD_SEGMENT),
            "NestingKeywordSegment" => Some(&NESTING_KEYWORD_SEGMENT),
            "OutfileKeywordSegment" => Some(&OUTFILE_KEYWORD_SEGMENT),
            "Command_functionKeywordSegment" => Some(&COMMAND_FUNCTION_KEYWORD_SEGMENT),
            "CubeKeywordSegment" => Some(&CUBE_KEYWORD_SEGMENT),
            "NologinKeywordSegment" => Some(&NOLOGIN_KEYWORD_SEGMENT),
            "SystemKeywordSegment" => Some(&SYSTEM_KEYWORD_SEGMENT),
            "OffKeywordSegment" => Some(&OFF_KEYWORD_SEGMENT),
            "Current_timestampKeywordSegment" => Some(&CURRENT_TIMESTAMP_KEYWORD_SEGMENT),
            "OverlapsKeywordSegment" => Some(&OVERLAPS_KEYWORD_SEGMENT),
            "DatabaseKeywordSegment" => Some(&DATABASE_KEYWORD_SEGMENT),
            "Character_lengthKeywordSegment" => Some(&CHARACTER_LENGTH_KEYWORD_SEGMENT),
            "Hour_secondKeywordSegment" => Some(&HOUR_SECOND_KEYWORD_SEGMENT),
            "InstanceKeywordSegment" => Some(&INSTANCE_KEYWORD_SEGMENT),
            "IndicatorKeywordSegment" => Some(&INDICATOR_KEYWORD_SEGMENT),
            "StdinKeywordSegment" => Some(&STDIN_KEYWORD_SEGMENT),
            "FutureKeywordSegment" => Some(&FUTURE_KEYWORD_SEGMENT),
            "Int2KeywordSegment" => Some(&INT2_KEYWORD_SEGMENT),
            "ModKeywordSegment" => Some(&MOD_KEYWORD_SEGMENT),
            "DescribeKeywordSegment" => Some(&DESCRIBE_KEYWORD_SEGMENT),
            "CardinalityKeywordSegment" => Some(&CARDINALITY_KEYWORD_SEGMENT),
            "SectionKeywordSegment" => Some(&SECTION_KEYWORD_SEGMENT),
            "AccountKeywordSegment" => Some(&ACCOUNT_KEYWORD_SEGMENT),
            "DataKeywordSegment" => Some(&DATA_KEYWORD_SEGMENT),
            "StateKeywordSegment" => Some(&STATE_KEYWORD_SEGMENT),
            "EscapedKeywordSegment" => Some(&ESCAPED_KEYWORD_SEGMENT),
            "SizeKeywordSegment" => Some(&SIZE_KEYWORD_SEGMENT),
            "LeaveKeywordSegment" => Some(&LEAVE_KEYWORD_SEGMENT),
            "PasswordKeywordSegment" => Some(&PASSWORD_KEYWORD_SEGMENT),
            "BinaryKeywordSegment" => Some(&BINARY_KEYWORD_SEGMENT),
            "FoundKeywordSegment" => Some(&FOUND_KEYWORD_SEGMENT),
            "WithoutKeywordSegment" => Some(&WITHOUT_KEYWORD_SEGMENT),
            "QuoteKeywordSegment" => Some(&QUOTE_KEYWORD_SEGMENT),
            "OverridingKeywordSegment" => Some(&OVERRIDING_KEYWORD_SEGMENT),
            "TransientKeywordSegment" => Some(&TRANSIENT_KEYWORD_SEGMENT),
            "DatabasesKeywordSegment" => Some(&DATABASES_KEYWORD_SEGMENT),
            "DecimalKeywordSegment" => Some(&DECIMAL_KEYWORD_SEGMENT),
            "Returned_octet_lengthKeywordSegment" => Some(&RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT),
            "SensitiveKeywordSegment" => Some(&SENSITIVE_KEYWORD_SEGMENT),
            "SeparatorKeywordSegment" => Some(&SEPARATOR_KEYWORD_SEGMENT),
            "HoldKeywordSegment" => Some(&HOLD_KEYWORD_SEGMENT),
            "SessionKeywordSegment" => Some(&SESSION_KEYWORD_SEGMENT),
            "TranslateKeywordSegment" => Some(&TRANSLATE_KEYWORD_SEGMENT),
            "ExecuteKeywordSegment" => Some(&EXECUTE_KEYWORD_SEGMENT),
            "ForKeywordSegment" => Some(&FOR_KEYWORD_SEGMENT),
            "FusionKeywordSegment" => Some(&FUSION_KEYWORD_SEGMENT),
            "LeadingKeywordSegment" => Some(&LEADING_KEYWORD_SEGMENT),
            "InitiallyKeywordSegment" => Some(&INITIALLY_KEYWORD_SEGMENT),
            "RollupKeywordSegment" => Some(&ROLLUP_KEYWORD_SEGMENT),
            "AsensitiveKeywordSegment" => Some(&ASENSITIVE_KEYWORD_SEGMENT),
            "CreateuserKeywordSegment" => Some(&CREATEUSER_KEYWORD_SEGMENT),
            "PliKeywordSegment" => Some(&PLI_KEYWORD_SEGMENT),
            "RollbackKeywordSegment" => Some(&ROLLBACK_KEYWORD_SEGMENT),
            "HostKeywordSegment" => Some(&HOST_KEYWORD_SEGMENT),
            "AfterKeywordSegment" => Some(&AFTER_KEYWORD_SEGMENT),
            "HeapKeywordSegment" => Some(&HEAP_KEYWORD_SEGMENT),
            "StartingKeywordSegment" => Some(&STARTING_KEYWORD_SEGMENT),
            "Var_popKeywordSegment" => Some(&VAR_POP_KEYWORD_SEGMENT),
            "NothingKeywordSegment" => Some(&NOTHING_KEYWORD_SEGMENT),
            "TinyintKeywordSegment" => Some(&TINYINT_KEYWORD_SEGMENT),
            "PostfixKeywordSegment" => Some(&POSTFIX_KEYWORD_SEGMENT),
            "StageKeywordSegment" => Some(&STAGE_KEYWORD_SEGMENT),
            "Low_priorityKeywordSegment" => Some(&LOW_PRIORITY_KEYWORD_SEGMENT),
            "LocaltimestampKeywordSegment" => Some(&LOCALTIMESTAMP_KEYWORD_SEGMENT),
            "ResignalKeywordSegment" => Some(&RESIGNAL_KEYWORD_SEGMENT),
            "InstantiableKeywordSegment" => Some(&INSTANTIABLE_KEYWORD_SEGMENT),
            "InitializeKeywordSegment" => Some(&INITIALIZE_KEYWORD_SEGMENT),
            "StructureKeywordSegment" => Some(&STRUCTURE_KEYWORD_SEGMENT),
            "TextsizeKeywordSegment" => Some(&TEXTSIZE_KEYWORD_SEGMENT),
            "UnsignedKeywordSegment" => Some(&UNSIGNED_KEYWORD_SEGMENT),
            "Dynamic_function_codeKeywordSegment" => Some(&DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT),
            "HoldlockKeywordSegment" => Some(&HOLDLOCK_KEYWORD_SEGMENT),
            "FilterKeywordSegment" => Some(&FILTER_KEYWORD_SEGMENT),
            "NocacheKeywordSegment" => Some(&NOCACHE_KEYWORD_SEGMENT),
            "OperatorKeywordSegment" => Some(&OPERATOR_KEYWORD_SEGMENT),
            "StatementKeywordSegment" => Some(&STATEMENT_KEYWORD_SEGMENT),
            "IntegerKeywordSegment" => Some(&INTEGER_KEYWORD_SEGMENT),
            "OpenrowsetKeywordSegment" => Some(&OPENROWSET_KEYWORD_SEGMENT),
            "High_priorityKeywordSegment" => Some(&HIGH_PRIORITY_KEYWORD_SEGMENT),
            "X509KeywordSegment" => Some(&X509_KEYWORD_SEGMENT),
            "MumpsKeywordSegment" => Some(&MUMPS_KEYWORD_SEGMENT),
            "MultisetKeywordSegment" => Some(&MULTISET_KEYWORD_SEGMENT),
            "NormalizeKeywordSegment" => Some(&NORMALIZE_KEYWORD_SEGMENT),
            "Parameter_modeKeywordSegment" => Some(&PARAMETER_MODE_KEYWORD_SEGMENT),
            "Insert_idKeywordSegment" => Some(&INSERT_ID_KEYWORD_SEGMENT),
            "Year_monthKeywordSegment" => Some(&YEAR_MONTH_KEYWORD_SEGMENT),
            "OwnerKeywordSegment" => Some(&OWNER_KEYWORD_SEGMENT),
            "Hour_microsecondKeywordSegment" => Some(&HOUR_MICROSECOND_KEYWORD_SEGMENT),
            "MapKeywordSegment" => Some(&MAP_KEYWORD_SEGMENT),
            "User_defined_type_catalogKeywordSegment" => Some(&USER_DEFINED_TYPE_CATALOG_KEYWORD_SEGMENT),
            "Pack_keysKeywordSegment" => Some(&PACK_KEYS_KEYWORD_SEGMENT),
            "ModifyKeywordSegment" => Some(&MODIFY_KEYWORD_SEGMENT),
            "LowerKeywordSegment" => Some(&LOWER_KEYWORD_SEGMENT),
            "BlobKeywordSegment" => Some(&BLOB_KEYWORD_SEGMENT),
            "Routine_nameKeywordSegment" => Some(&ROUTINE_NAME_KEYWORD_SEGMENT),
            "AnyKeywordSegment" => Some(&ANY_KEYWORD_SEGMENT),
            "RevokeKeywordSegment" => Some(&REVOKE_KEYWORD_SEGMENT),
            "FormatKeywordSegment" => Some(&FORMAT_KEYWORD_SEGMENT),
            "Sql_warningsKeywordSegment" => Some(&SQL_WARNINGS_KEYWORD_SEGMENT),
            "LancompilerKeywordSegment" => Some(&LANCOMPILER_KEYWORD_SEGMENT),
            "Returned_sqlstateKeywordSegment" => Some(&RETURNED_SQLSTATE_KEYWORD_SEGMENT),
            "ByKeywordSegment" => Some(&BY_KEYWORD_SEGMENT),
            "ChecksumKeywordSegment" => Some(&CHECKSUM_KEYWORD_SEGMENT),
            "VarcharKeywordSegment" => Some(&VARCHAR_KEYWORD_SEGMENT),
            "MatchedKeywordSegment" => Some(&MATCHED_KEYWORD_SEGMENT),
            "Use_any_roleKeywordSegment" => Some(&USE_ANY_ROLE_KEYWORD_SEGMENT),
            "FieldsKeywordSegment" => Some(&FIELDS_KEYWORD_SEGMENT),
            "ClobKeywordSegment" => Some(&CLOB_KEYWORD_SEGMENT),
            "WeekKeywordSegment" => Some(&WEEK_KEYWORD_SEGMENT),
            "SchemasKeywordSegment" => Some(&SCHEMAS_KEYWORD_SEGMENT),
            "TimeKeywordSegment" => Some(&TIME_KEYWORD_SEGMENT),
            "CopyKeywordSegment" => Some(&COPY_KEYWORD_SEGMENT),
            "UidKeywordSegment" => Some(&UID_KEYWORD_SEGMENT),
            "Regr_avgyKeywordSegment" => Some(&REGR_AVGY_KEYWORD_SEGMENT),
            "Covar_popKeywordSegment" => Some(&COVAR_POP_KEYWORD_SEGMENT),
            "Var_sampKeywordSegment" => Some(&VAR_SAMP_KEYWORD_SEGMENT),
            "MinuteKeywordSegment" => Some(&MINUTE_KEYWORD_SEGMENT),
            "TablesKeywordSegment" => Some(&TABLES_KEYWORD_SEGMENT),
            "Float4KeywordSegment" => Some(&FLOAT4_KEYWORD_SEGMENT),
            "GKeywordSegment" => Some(&G_KEYWORD_SEGMENT),
            "LateralKeywordSegment" => Some(&LATERAL_KEYWORD_SEGMENT),
            "Current_default_transform_groupKeywordSegment" => Some(&CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT),
            "ValueKeywordSegment" => Some(&VALUE_KEYWORD_SEGMENT),
            "Regr_r2KeywordSegment" => Some(&REGR_R2_KEYWORD_SEGMENT),
            "VerboseKeywordSegment" => Some(&VERBOSE_KEYWORD_SEGMENT),
            "BrowseKeywordSegment" => Some(&BROWSE_KEYWORD_SEGMENT),
            "MlslabelKeywordSegment" => Some(&MLSLABEL_KEYWORD_SEGMENT),
            "MemberKeywordSegment" => Some(&MEMBER_KEYWORD_SEGMENT),
            "Class_originKeywordSegment" => Some(&CLASS_ORIGIN_KEYWORD_SEGMENT),
            "ForwardKeywordSegment" => Some(&FORWARD_KEYWORD_SEGMENT),
            "MethodKeywordSegment" => Some(&METHOD_KEYWORD_SEGMENT),
            "SchemaKeywordSegment" => Some(&SCHEMA_KEYWORD_SEGMENT),
            "Trigger_catalogKeywordSegment" => Some(&TRIGGER_CATALOG_KEYWORD_SEGMENT),
            "GroupKeywordSegment" => Some(&GROUP_KEYWORD_SEGMENT),
            "InitialKeywordSegment" => Some(&INITIAL_KEYWORD_SEGMENT),
            "ImplementationKeywordSegment" => Some(&IMPLEMENTATION_KEYWORD_SEGMENT),
            "RolesKeywordSegment" => Some(&ROLES_KEYWORD_SEGMENT),
            "BreadthKeywordSegment" => Some(&BREADTH_KEYWORD_SEGMENT),
            "NullableKeywordSegment" => Some(&NULLABLE_KEYWORD_SEGMENT),
            "ParameterKeywordSegment" => Some(&PARAMETER_KEYWORD_SEGMENT),
            "UescapeKeywordSegment" => Some(&UESCAPE_KEYWORD_SEGMENT),
            "OptionsKeywordSegment" => Some(&OPTIONS_KEYWORD_SEGMENT),
            "BulkKeywordSegment" => Some(&BULK_KEYWORD_SEGMENT),
            "SysdateKeywordSegment" => Some(&SYSDATE_KEYWORD_SEGMENT),
            "SetofKeywordSegment" => Some(&SETOF_KEYWORD_SEGMENT),
            "DatetimeKeywordSegment" => Some(&DATETIME_KEYWORD_SEGMENT),
            "VolatileKeywordSegment" => Some(&VOLATILE_KEYWORD_SEGMENT),
            "OverKeywordSegment" => Some(&OVER_KEYWORD_SEGMENT),
            "IntegrationsKeywordSegment" => Some(&INTEGRATIONS_KEYWORD_SEGMENT),
            "MyisamKeywordSegment" => Some(&MYISAM_KEYWORD_SEGMENT),
            "IncludingKeywordSegment" => Some(&INCLUDING_KEYWORD_SEGMENT),
            "IntersectKeywordSegment" => Some(&INTERSECT_KEYWORD_SEGMENT),
            "AlsoKeywordSegment" => Some(&ALSO_KEYWORD_SEGMENT),
            "Octet_lengthKeywordSegment" => Some(&OCTET_LENGTH_KEYWORD_SEGMENT),
            "Current_transform_group_for_typeKeywordSegment" => Some(&CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT),
            "ReindexKeywordSegment" => Some(&REINDEX_KEYWORD_SEGMENT),
            "EachKeywordSegment" => Some(&EACH_KEYWORD_SEGMENT),
            "SignalKeywordSegment" => Some(&SIGNAL_KEYWORD_SEGMENT),
            "IntegrationKeywordSegment" => Some(&INTEGRATION_KEYWORD_SEGMENT),
            "ModuleKeywordSegment" => Some(&MODULE_KEYWORD_SEGMENT),
            "OperationKeywordSegment" => Some(&OPERATION_KEYWORD_SEGMENT),
            "NoinheritKeywordSegment" => Some(&NOINHERIT_KEYWORD_SEGMENT),
            "FreeKeywordSegment" => Some(&FREE_KEYWORD_SEGMENT),
            "Bit_lengthKeywordSegment" => Some(&BIT_LENGTH_KEYWORD_SEGMENT),
            "LeastKeywordSegment" => Some(&LEAST_KEYWORD_SEGMENT),
            "StaticKeywordSegment" => Some(&STATIC_KEYWORD_SEGMENT),
            "ConditionKeywordSegment" => Some(&CONDITION_KEYWORD_SEGMENT),
            "CommittedKeywordSegment" => Some(&COMMITTED_KEYWORD_SEGMENT),
            "MlKeywordSegment" => Some(&ML_KEYWORD_SEGMENT),
            "CeilKeywordSegment" => Some(&CEIL_KEYWORD_SEGMENT),
            "TimestampKeywordSegment" => Some(&TIMESTAMP_KEYWORD_SEGMENT),
            "InKeywordSegment" => Some(&IN_KEYWORD_SEGMENT),
            "Sql_low_priority_updatesKeywordSegment" => Some(&SQL_LOW_PRIORITY_UPDATES_KEYWORD_SEGMENT),
            "ReloadKeywordSegment" => Some(&RELOAD_KEYWORD_SEGMENT),
            "PercentKeywordSegment" => Some(&PERCENT_KEYWORD_SEGMENT),
            "Current_roleKeywordSegment" => Some(&CURRENT_ROLE_KEYWORD_SEGMENT),
            "AliasKeywordSegment" => Some(&ALIAS_KEYWORD_SEGMENT),
            "Sql_log_offKeywordSegment" => Some(&SQL_LOG_OFF_KEYWORD_SEGMENT),
            "ClassKeywordSegment" => Some(&CLASS_KEYWORD_SEGMENT),
            "CorrespondingKeywordSegment" => Some(&CORRESPONDING_KEYWORD_SEGMENT),
            "RecheckKeywordSegment" => Some(&RECHECK_KEYWORD_SEGMENT),
            "DumpKeywordSegment" => Some(&DUMP_KEYWORD_SEGMENT),
            "MaxvalueKeywordSegment" => Some(&MAXVALUE_KEYWORD_SEGMENT),
            "PurgeKeywordSegment" => Some(&PURGE_KEYWORD_SEGMENT),
            "ColumnKeywordSegment" => Some(&COLUMN_KEYWORD_SEGMENT),
            "PctfreeKeywordSegment" => Some(&PCTFREE_KEYWORD_SEGMENT),
            "SimilarKeywordSegment" => Some(&SIMILAR_KEYWORD_SEGMENT),
            "NumericKeywordSegment" => Some(&NUMERIC_KEYWORD_SEGMENT),
            "Stddev_popKeywordSegment" => Some(&STDDEV_POP_KEYWORD_SEGMENT),
            "XmlKeywordSegment" => Some(&XML_KEYWORD_SEGMENT),
            "FalseKeywordSegment" => Some(&FALSE_KEYWORD_SEGMENT),
            "FileKeywordSegment" => Some(&FILE_KEYWORD_SEGMENT),
            "Row_numberKeywordSegment" => Some(&ROW_NUMBER_KEYWORD_SEGMENT),
            "AssignmentKeywordSegment" => Some(&ASSIGNMENT_KEYWORD_SEGMENT),
            "NameKeywordSegment" => Some(&NAME_KEYWORD_SEGMENT),
            "SimpleKeywordSegment" => Some(&SIMPLE_KEYWORD_SEGMENT),
            "Transactions_committedKeywordSegment" => Some(&TRANSACTIONS_COMMITTED_KEYWORD_SEGMENT),
            "SequencesKeywordSegment" => Some(&SEQUENCES_KEYWORD_SEGMENT),
            "Raid0KeywordSegment" => Some(&RAID0_KEYWORD_SEGMENT),
            "SqlKeywordSegment" => Some(&SQL_KEYWORD_SEGMENT),
            "SublistKeywordSegment" => Some(&SUBLIST_KEYWORD_SEGMENT),
            "TableKeywordSegment" => Some(&TABLE_KEYWORD_SEGMENT),
            "FreetexttableKeywordSegment" => Some(&FREETEXTTABLE_KEYWORD_SEGMENT),
            "Parameter_ordinal_positionKeywordSegment" => Some(&PARAMETER_ORDINAL_POSITION_KEYWORD_SEGMENT),
            "ConstraintKeywordSegment" => Some(&CONSTRAINT_KEYWORD_SEGMENT),
            "UntilKeywordSegment" => Some(&UNTIL_KEYWORD_SEGMENT),
            "Width_bucketKeywordSegment" => Some(&WIDTH_BUCKET_KEYWORD_SEGMENT),
            "MinusKeywordSegment" => Some(&MINUS_KEYWORD_SEGMENT),
            "Datetime_interval_precisionKeywordSegment" => Some(&DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT),
            "InsertKeywordSegment" => Some(&INSERT_KEYWORD_SEGMENT),
            "PositionKeywordSegment" => Some(&POSITION_KEYWORD_SEGMENT),
            "DeleteKeywordSegment" => Some(&DELETE_KEYWORD_SEGMENT),
            "CeilingKeywordSegment" => Some(&CEILING_KEYWORD_SEGMENT),
            "IntoKeywordSegment" => Some(&INTO_KEYWORD_SEGMENT),
            "DisableKeywordSegment" => Some(&DISABLE_KEYWORD_SEGMENT),
            "BeforeKeywordSegment" => Some(&BEFORE_KEYWORD_SEGMENT),
            "Int8KeywordSegment" => Some(&INT8_KEYWORD_SEGMENT),
            "Character_set_schemaKeywordSegment" => Some(&CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT),
            "MiddleintKeywordSegment" => Some(&MIDDLEINT_KEYWORD_SEGMENT),
            "GotoKeywordSegment" => Some(&GOTO_KEYWORD_SEGMENT),
            "LnKeywordSegment" => Some(&LN_KEYWORD_SEGMENT),
            "CreatedbKeywordSegment" => Some(&CREATEDB_KEYWORD_SEGMENT),
            "CountKeywordSegment" => Some(&COUNT_KEYWORD_SEGMENT),
            "SqrtKeywordSegment" => Some(&SQRT_KEYWORD_SEGMENT),
            "IfKeywordSegment" => Some(&IF_KEYWORD_SEGMENT),
            "LinesKeywordSegment" => Some(&LINES_KEYWORD_SEGMENT),
            "Parameter_nameKeywordSegment" => Some(&PARAMETER_NAME_KEYWORD_SEGMENT),
            "DestructorKeywordSegment" => Some(&DESTRUCTOR_KEYWORD_SEGMENT),
            "LocalKeywordSegment" => Some(&LOCAL_KEYWORD_SEGMENT),
            "ToastKeywordSegment" => Some(&TOAST_KEYWORD_SEGMENT),
            "SpatialKeywordSegment" => Some(&SPATIAL_KEYWORD_SEGMENT),
            "LockKeywordSegment" => Some(&LOCK_KEYWORD_SEGMENT),
            "DoubleKeywordSegment" => Some(&DOUBLE_KEYWORD_SEGMENT),
            "TerminateKeywordSegment" => Some(&TERMINATE_KEYWORD_SEGMENT),
            "Auto_incrementKeywordSegment" => Some(&AUTO_INCREMENT_KEYWORD_SEGMENT),
            "ConstructorKeywordSegment" => Some(&CONSTRUCTOR_KEYWORD_SEGMENT),
            "WindowKeywordSegment" => Some(&WINDOW_KEYWORD_SEGMENT),
            "AndKeywordSegment" => Some(&AND_KEYWORD_SEGMENT),
            "User_defined_type_nameKeywordSegment" => Some(&USER_DEFINED_TYPE_NAME_KEYWORD_SEGMENT),
            "Cume_distKeywordSegment" => Some(&CUME_DIST_KEYWORD_SEGMENT),
            "LengthKeywordSegment" => Some(&LENGTH_KEYWORD_SEGMENT),
            "User_defined_type_codeKeywordSegment" => Some(&USER_DEFINED_TYPE_CODE_KEYWORD_SEGMENT),
            "DescKeywordSegment" => Some(&DESC_KEYWORD_SEGMENT),
            "StreamKeywordSegment" => Some(&STREAM_KEYWORD_SEGMENT),
            "Percentile_contKeywordSegment" => Some(&PERCENTILE_CONT_KEYWORD_SEGMENT),
            "EnumKeywordSegment" => Some(&ENUM_KEYWORD_SEGMENT),
            "IlikeKeywordSegment" => Some(&ILIKE_KEYWORD_SEGMENT),
            "LimitKeywordSegment" => Some(&LIMIT_KEYWORD_SEGMENT),
            "OptionKeywordSegment" => Some(&OPTION_KEYWORD_SEGMENT),
            "HostsKeywordSegment" => Some(&HOSTS_KEYWORD_SEGMENT),
            "OrderingKeywordSegment" => Some(&ORDERING_KEYWORD_SEGMENT),
            "ScopeKeywordSegment" => Some(&SCOPE_KEYWORD_SEGMENT),
            "UnknownKeywordSegment" => Some(&UNKNOWN_KEYWORD_SEGMENT),
            "PlacingKeywordSegment" => Some(&PLACING_KEYWORD_SEGMENT),
            "RestoreKeywordSegment" => Some(&RESTORE_KEYWORD_SEGMENT),
            "AnalyzeKeywordSegment" => Some(&ANALYZE_KEYWORD_SEGMENT),
            "CycleKeywordSegment" => Some(&CYCLE_KEYWORD_SEGMENT),
            "UnboundedKeywordSegment" => Some(&UNBOUNDED_KEYWORD_SEGMENT),
            "BothKeywordSegment" => Some(&BOTH_KEYWORD_SEGMENT),
            "GrantedKeywordSegment" => Some(&GRANTED_KEYWORD_SEGMENT),
            "No_write_to_binlogKeywordSegment" => Some(&NO_WRITE_TO_BINLOG_KEYWORD_SEGMENT),
            "ProcedureKeywordSegment" => Some(&PROCEDURE_KEYWORD_SEGMENT),
            "EnclosedKeywordSegment" => Some(&ENCLOSED_KEYWORD_SEGMENT),
            "ModelKeywordSegment" => Some(&MODEL_KEYWORD_SEGMENT),
            "NewKeywordSegment" => Some(&NEW_KEYWORD_SEGMENT),
            "AttributesKeywordSegment" => Some(&ATTRIBUTES_KEYWORD_SEGMENT),
            "OrKeywordSegment" => Some(&OR_KEYWORD_SEGMENT),
            "AccountsKeywordSegment" => Some(&ACCOUNTS_KEYWORD_SEGMENT),
            "MaxextentsKeywordSegment" => Some(&MAXEXTENTS_KEYWORD_SEGMENT),
            "Percent_rankKeywordSegment" => Some(&PERCENT_RANK_KEYWORD_SEGMENT),
            "DefaultKeywordSegment" => Some(&DEFAULT_KEYWORD_SEGMENT),
            "EqualsKeywordSegment" => Some(&EQUALS_KEYWORD_SEGMENT),
            "Returned_cardinalityKeywordSegment" => Some(&RETURNED_CARDINALITY_KEYWORD_SEGMENT),
            "SysidKeywordSegment" => Some(&SYSID_KEYWORD_SEGMENT),
            "UniqueKeywordSegment" => Some(&UNIQUE_KEYWORD_SEGMENT),
            "Regr_interceptKeywordSegment" => Some(&REGR_INTERCEPT_KEYWORD_SEGMENT),
            "AscKeywordSegment" => Some(&ASC_KEYWORD_SEGMENT),
            "Character_set_catalogKeywordSegment" => Some(&CHARACTER_SET_CATALOG_KEYWORD_SEGMENT),
            "WhileKeywordSegment" => Some(&WHILE_KEYWORD_SEGMENT),
            "BooleanKeywordSegment" => Some(&BOOLEAN_KEYWORD_SEGMENT),
            "BindingKeywordSegment" => Some(&BINDING_KEYWORD_SEGMENT),
            "TerminatedKeywordSegment" => Some(&TERMINATED_KEYWORD_SEGMENT),
            "ValidateKeywordSegment" => Some(&VALIDATE_KEYWORD_SEGMENT),
            "DayKeywordSegment" => Some(&DAY_KEYWORD_SEGMENT),
            "Datetime_interval_codeKeywordSegment" => Some(&DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT),
            "MinKeywordSegment" => Some(&MIN_KEYWORD_SEGMENT),
            "Day_minuteKeywordSegment" => Some(&DAY_MINUTE_KEYWORD_SEGMENT),
            "KillKeywordSegment" => Some(&KILL_KEYWORD_SEGMENT),
            "ScrollKeywordSegment" => Some(&SCROLL_KEYWORD_SEGMENT),
            "OperateKeywordSegment" => Some(&OPERATE_KEYWORD_SEGMENT),
            "AllKeywordSegment" => Some(&ALL_KEYWORD_SEGMENT),
            "ContinueKeywordSegment" => Some(&CONTINUE_KEYWORD_SEGMENT),
            "Sql_calc_found_rowsKeywordSegment" => Some(&SQL_CALC_FOUND_ROWS_KEYWORD_SEGMENT),
            "SumKeywordSegment" => Some(&SUM_KEYWORD_SEGMENT),
            "OfKeywordSegment" => Some(&OF_KEYWORD_SEGMENT),
            "StyleKeywordSegment" => Some(&STYLE_KEYWORD_SEGMENT),
            "WaitforKeywordSegment" => Some(&WAITFOR_KEYWORD_SEGMENT),
            "ShutdownKeywordSegment" => Some(&SHUTDOWN_KEYWORD_SEGMENT),
            "DropKeywordSegment" => Some(&DROP_KEYWORD_SEGMENT),
            "NamesKeywordSegment" => Some(&NAMES_KEYWORD_SEGMENT),
            "Parameter_specific_catalogKeywordSegment" => Some(&PARAMETER_SPECIFIC_CATALOG_KEYWORD_SEGMENT),
            "PrepareKeywordSegment" => Some(&PREPARE_KEYWORD_SEGMENT),
            "Regr_sxxKeywordSegment" => Some(&REGR_SXX_KEYWORD_SEGMENT),
            "RowidKeywordSegment" => Some(&ROWID_KEYWORD_SEGMENT),
            "DispatchKeywordSegment" => Some(&DISPATCH_KEYWORD_SEGMENT),
            "VarbinaryKeywordSegment" => Some(&VARBINARY_KEYWORD_SEGMENT),
            "MaterializedKeywordSegment" => Some(&MATERIALIZED_KEYWORD_SEGMENT),
            "SslKeywordSegment" => Some(&SSL_KEYWORD_SEGMENT),
            "RawKeywordSegment" => Some(&RAW_KEYWORD_SEGMENT),
            "LongtextKeywordSegment" => Some(&LONGTEXT_KEYWORD_SEGMENT),
            "DeallocateKeywordSegment" => Some(&DEALLOCATE_KEYWORD_SEGMENT),
            "DistributedKeywordSegment" => Some(&DISTRIBUTED_KEYWORD_SEGMENT),
            "OptimizeKeywordSegment" => Some(&OPTIMIZE_KEYWORD_SEGMENT),
            "CompressKeywordSegment" => Some(&COMPRESS_KEYWORD_SEGMENT),
            "Key_memberKeywordSegment" => Some(&KEY_MEMBER_KEYWORD_SEGMENT),
            "AtKeywordSegment" => Some(&AT_KEYWORD_SEGMENT),
            "NcharKeywordSegment" => Some(&NCHAR_KEYWORD_SEGMENT),
            "RoleKeywordSegment" => Some(&ROLE_KEYWORD_SEGMENT),
            "YamlKeywordSegment" => Some(&YAML_KEYWORD_SEGMENT),
            "PublicKeywordSegment" => Some(&PUBLIC_KEYWORD_SEGMENT),
            "JsonKeywordSegment" => Some(&JSON_KEYWORD_SEGMENT),
            "TransformsKeywordSegment" => Some(&TRANSFORMS_KEYWORD_SEGMENT),
            "Hour_minuteKeywordSegment" => Some(&HOUR_MINUTE_KEYWORD_SEGMENT),
            "NanKeywordSegment" => Some(&NAN_KEYWORD_SEGMENT),
            "Char_lengthKeywordSegment" => Some(&CHAR_LENGTH_KEYWORD_SEGMENT),
            "ExternalKeywordSegment" => Some(&EXTERNAL_KEYWORD_SEGMENT),
            "SpecificKeywordSegment" => Some(&SPECIFIC_KEYWORD_SEGMENT),
            "LanguageKeywordSegment" => Some(&LANGUAGE_KEYWORD_SEGMENT),
            "FloatKeywordSegment" => Some(&FLOAT_KEYWORD_SEGMENT),
            "NullsKeywordSegment" => Some(&NULLS_KEYWORD_SEGMENT),
            "ForeignKeywordSegment" => Some(&FOREIGN_KEYWORD_SEGMENT),
            "FortranKeywordSegment" => Some(&FORTRAN_KEYWORD_SEGMENT),
            "Specific_nameKeywordSegment" => Some(&SPECIFIC_NAME_KEYWORD_SEGMENT),
            "WarehouseKeywordSegment" => Some(&WAREHOUSE_KEYWORD_SEGMENT),
            "IsolationKeywordSegment" => Some(&ISOLATION_KEYWORD_SEGMENT),
            "RestartKeywordSegment" => Some(&RESTART_KEYWORD_SEGMENT),
            "AdaKeywordSegment" => Some(&ADA_KEYWORD_SEGMENT),
            "DynamicKeywordSegment" => Some(&DYNAMIC_KEYWORD_SEGMENT),
            "SavepointKeywordSegment" => Some(&SAVEPOINT_KEYWORD_SEGMENT),
            "IsKeywordSegment" => Some(&IS_KEYWORD_SEGMENT),
            "CsvKeywordSegment" => Some(&CSV_KEYWORD_SEGMENT),
            "AllocateKeywordSegment" => Some(&ALLOCATE_KEYWORD_SEGMENT),
            "Int3KeywordSegment" => Some(&INT3_KEYWORD_SEGMENT),
            "RefKeywordSegment" => Some(&REF_KEYWORD_SEGMENT),
            "CommentKeywordSegment" => Some(&COMMENT_KEYWORD_SEGMENT),
            "AnalyseKeywordSegment" => Some(&ANALYSE_KEYWORD_SEGMENT),
            "AlterKeywordSegment" => Some(&ALTER_KEYWORD_SEGMENT),
            "TrueKeywordSegment" => Some(&TRUE_KEYWORD_SEGMENT),
            "OctetsKeywordSegment" => Some(&OCTETS_KEYWORD_SEGMENT),
            "MinvalueKeywordSegment" => Some(&MINVALUE_KEYWORD_SEGMENT),
            "VaryingKeywordSegment" => Some(&VARYING_KEYWORD_SEGMENT),
            "FunctionKeywordSegment" => Some(&FUNCTION_KEYWORD_SEGMENT),
            "AddKeywordSegment" => Some(&ADD_KEYWORD_SEGMENT),
            "ReturnKeywordSegment" => Some(&RETURN_KEYWORD_SEGMENT),
            "BigintKeywordSegment" => Some(&BIGINT_KEYWORD_SEGMENT),
            "MoreKeywordSegment" => Some(&MORE_KEYWORD_SEGMENT),
            "Sql_log_updateKeywordSegment" => Some(&SQL_LOG_UPDATE_KEYWORD_SEGMENT),
            "UnnamedKeywordSegment" => Some(&UNNAMED_KEYWORD_SEGMENT),
            "LocationKeywordSegment" => Some(&LOCATION_KEYWORD_SEGMENT),
            "CalledKeywordSegment" => Some(&CALLED_KEYWORD_SEGMENT),
            "GrantKeywordSegment" => Some(&GRANT_KEYWORD_SEGMENT),
            "LoopKeywordSegment" => Some(&LOOP_KEYWORD_SEGMENT),
            "Current_timeKeywordSegment" => Some(&CURRENT_TIME_KEYWORD_SEGMENT),
            "Int4KeywordSegment" => Some(&INT4_KEYWORD_SEGMENT),
            "LocatorKeywordSegment" => Some(&LOCATOR_KEYWORD_SEGMENT),
            "Dynamic_functionKeywordSegment" => Some(&DYNAMIC_FUNCTION_KEYWORD_SEGMENT),
            "DerivedKeywordSegment" => Some(&DERIVED_KEYWORD_SEGMENT),
            "SearchKeywordSegment" => Some(&SEARCH_KEYWORD_SEGMENT),
            "FloorKeywordSegment" => Some(&FLOOR_KEYWORD_SEGMENT),
            "ValidatorKeywordSegment" => Some(&VALIDATOR_KEYWORD_SEGMENT),
            "UnlockKeywordSegment" => Some(&UNLOCK_KEYWORD_SEGMENT),
            "ResultKeywordSegment" => Some(&RESULT_KEYWORD_SEGMENT),
            "SelfKeywordSegment" => Some(&SELF_KEYWORD_SEGMENT),
            "Routine_schemaKeywordSegment" => Some(&ROUTINE_SCHEMA_KEYWORD_SEGMENT),
            "ConnectionKeywordSegment" => Some(&CONNECTION_KEYWORD_SEGMENT),
            "ReadsKeywordSegment" => Some(&READS_KEYWORD_SEGMENT),
            "OpenqueryKeywordSegment" => Some(&OPENQUERY_KEYWORD_SEGMENT),
            "Constraint_schemaKeywordSegment" => Some(&CONSTRAINT_SCHEMA_KEYWORD_SEGMENT),
            "DerefKeywordSegment" => Some(&DEREF_KEYWORD_SEGMENT),
            "ExceptKeywordSegment" => Some(&EXCEPT_KEYWORD_SEGMENT),
            "ToKeywordSegment" => Some(&TO_KEYWORD_SEGMENT),
            "WheneverKeywordSegment" => Some(&WHENEVER_KEYWORD_SEGMENT),
            "InsensitiveKeywordSegment" => Some(&INSENSITIVE_KEYWORD_SEGMENT),
            "AbortKeywordSegment" => Some(&ABORT_KEYWORD_SEGMENT),
            "FreezeKeywordSegment" => Some(&FREEZE_KEYWORD_SEGMENT),
            "ReadtextKeywordSegment" => Some(&READTEXT_KEYWORD_SEGMENT),
            "ActionKeywordSegment" => Some(&ACTION_KEYWORD_SEGMENT),
            "RelativeKeywordSegment" => Some(&RELATIVE_KEYWORD_SEGMENT),
            "RlikeKeywordSegment" => Some(&RLIKE_KEYWORD_SEGMENT),
            "SuperuserKeywordSegment" => Some(&SUPERUSER_KEYWORD_SEGMENT),
            "UndoKeywordSegment" => Some(&UNDO_KEYWORD_SEGMENT),
            "Command_function_codeKeywordSegment" => Some(&COMMAND_FUNCTION_CODE_KEYWORD_SEGMENT),
            "ExtractKeywordSegment" => Some(&EXTRACT_KEYWORD_SEGMENT),
            "RowKeywordSegment" => Some(&ROW_KEYWORD_SEGMENT),
            "YearKeywordSegment" => Some(&YEAR_KEYWORD_SEGMENT),
            "ComputeKeywordSegment" => Some(&COMPUTE_KEYWORD_SEGMENT),
            "Constraint_catalogKeywordSegment" => Some(&CONSTRAINT_CATALOG_KEYWORD_SEGMENT),
            "ProceduralKeywordSegment" => Some(&PROCEDURAL_KEYWORD_SEGMENT),
            "TriggerKeywordSegment" => Some(&TRIGGER_KEYWORD_SEGMENT),
            "LoadKeywordSegment" => Some(&LOAD_KEYWORD_SEGMENT),
            "UsageKeywordSegment" => Some(&USAGE_KEYWORD_SEGMENT),
            "IntKeywordSegment" => Some(&INT_KEYWORD_SEGMENT),
            "LeftKeywordSegment" => Some(&LEFT_KEYWORD_SEGMENT),
            "UsingKeywordSegment" => Some(&USING_KEYWORD_SEGMENT),
            "IgnoreKeywordSegment" => Some(&IGNORE_KEYWORD_SEGMENT),
            "IntervalKeywordSegment" => Some(&INTERVAL_KEYWORD_SEGMENT),
            "SelectKeywordSegment" => Some(&SELECT_KEYWORD_SEGMENT),
            "FullKeywordSegment" => Some(&FULL_KEYWORD_SEGMENT),
            "NotKeywordSegment" => Some(&NOT_KEYWORD_SEGMENT),
            "RowsKeywordSegment" => Some(&ROWS_KEYWORD_SEGMENT),
            "JoinKeywordSegment" => Some(&JOIN_KEYWORD_SEGMENT),
            "CaseKeywordSegment" => Some(&CASE_KEYWORD_SEGMENT),
            "NullKeywordSegment" => Some(&NULL_KEYWORD_SEGMENT),
            "OuterKeywordSegment" => Some(&OUTER_KEYWORD_SEGMENT),
            "CrossKeywordSegment" => Some(&CROSS_KEYWORD_SEGMENT),
            "RespectKeywordSegment" => Some(&RESPECT_KEYWORD_SEGMENT),
            "NaturalKeywordSegment" => Some(&NATURAL_KEYWORD_SEGMENT),
            "UnionKeywordSegment" => Some(&UNION_KEYWORD_SEGMENT),
            "PartitionKeywordSegment" => Some(&PARTITION_KEYWORD_SEGMENT),
            "SetKeywordSegment" => Some(&SET_KEYWORD_SEGMENT),
            "RightKeywordSegment" => Some(&RIGHT_KEYWORD_SEGMENT),
            "OrderKeywordSegment" => Some(&ORDER_KEYWORD_SEGMENT),
            "InnerKeywordSegment" => Some(&INNER_KEYWORD_SEGMENT),
            "OnKeywordSegment" => Some(&ON_KEYWORD_SEGMENT),
            _ => None,
    }
}
