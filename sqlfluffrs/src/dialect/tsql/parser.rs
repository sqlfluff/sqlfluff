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
Grammar::RegexParser()
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
Grammar::TypedParser()
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
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HashIdentifierSegment",
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
    name: "VariableIdentifierSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "AdditionAssignmentSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SubtractionAssignmentSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MultiplicationAssignmentSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DivisionAssignmentSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ModulusAssignmentSegment",
    optional: false,
    allow_gaps: true,
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
    name: "TopPercentGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
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
    name: "QuotedLiteralSegmentWithN",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntegerLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BinaryLiteralSegment",
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
    name: "TypedArrayLiteralSegment",
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
    name: "SystemVariableSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Nothing()
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
    name: "DelimiterGrammar",
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
Grammar::OneOf {
    elements: vec![
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
,
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
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonclusteredKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: true,
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
    ],
    optional: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
Grammar::Nothing()
);

// name='JoinTypeKeywordsGrammar'
pub static JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
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
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LoopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HashKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeKeywordSegment",
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
    optional: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "CrossKeywordSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OuterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='NestedJoinGrammar'
pub static NESTED_JOIN_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "JoinClauseSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
Grammar::Ref {
    name: "TableHintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableHintSegment",
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

// name='JoinLikeClauseGrammar'
pub static JOIN_LIKE_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
// Missing elements match_grammar=<AnySetOf: [<Ref: 'PivotUnpivotStatementSegment'>]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "ColumnReferenceSegment",
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
    name: "ArrayLiteralSegment",
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
    name: "ControlKeywordSegment",
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
    name: "ReceiveKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TakeKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ChangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TrackingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefinitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LoginKeywordSegment",
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
    name: "ObjectKeywordSegment",
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
    name: "SchemaKeywordSegment",
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
Grammar::Ref {
    name: "CastOperatorSegment",
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
    name: "DatabaseKeywordSegment",
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
    name: "SequenceKeywordSegment",
    optional: false,
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
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ToKeywordSegment",
    optional: false,
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DenyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
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
    name: "ControlKeywordSegment",
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
    name: "ReceiveKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TakeKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ChangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TrackingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefinitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LoginKeywordSegment",
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
    name: "ObjectKeywordSegment",
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
    name: "SchemaKeywordSegment",
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
Grammar::Ref {
    name: "CastOperatorSegment",
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
    name: "DatabaseKeywordSegment",
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
    name: "SequenceKeywordSegment",
    optional: false,
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
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
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
    name: "CascadeKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
    name: "ControlKeywordSegment",
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
    name: "ReceiveKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TakeKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ChangeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TrackingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DefinitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LoginKeywordSegment",
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
    name: "ObjectKeywordSegment",
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
    name: "SchemaKeywordSegment",
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
Grammar::Ref {
    name: "CastOperatorSegment",
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
    name: "DatabaseKeywordSegment",
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
    name: "SequenceKeywordSegment",
    optional: false,
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
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "CascadeKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Ref {
    name: "AlterKeywordSegment",
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
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ComputedColumnDefinitionSegment",
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
    name: "DropKeywordSegment",
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
    name: "IfExistsGrammar",
    optional: true,
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
Grammar::Ref {
    name: "ColumnConstraintSegment",
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
    name: "PeriodSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CheckKeywordSegment",
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
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Filestream_onKeywordSegment",
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
    name: "FilegroupNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionSchemeNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "System_versioningKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "History_tableKeywordSegment",
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
    name: "TableReferenceSegment",
    optional: false,
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
    name: "Data_consistency_checkKeywordSegment",
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
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "History_retention_periodKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: true,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Data_deletionKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "Filter_columnKeywordSegment",
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
    name: "ColumnReferenceSegment",
    optional: false,
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
    name: "Retention_periodKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MaxKeywordSegment",
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
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Database_defaultKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
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
Grammar::Ref {
    name: "FilestreamKeywordSegment",
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
    name: "SparseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaskedKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "FunctionKeywordSegment",
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
Grammar::Ref {
    name: "DefaultKeywordSegment",
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
Grammar::Ref {
    name: "IdentityGrammar",
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
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplicationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Transaction_idKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Sequence_numberKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "StartKeywordSegment",
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
Grammar::Ref {
    name: "HiddenKeywordSegment",
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
    name: "RowguidcolKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EncryptedWithGrammar",
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
Grammar::Ref {
    name: "RelationalIndexOptionsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
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
    name: "ReferencesConstraintGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CheckConstraintGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilestreamOnOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IndexKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonclusteredKeywordSegment",
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
,
Grammar::Ref {
    name: "TableConstraintSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Ref {
    name: "PlusSegment",
    optional: false,
    allow_gaps: true,
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
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ContainmentKeywordSegment",
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
    name: "NoneKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeywordSegment",
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
    name: "FileSpecSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FilegroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedOrQuotedIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ContainsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilestreamKeywordSegment",
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
    name: "DefaultKeywordSegment",
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
    name: "ContainsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Memory_optimized_dataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
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
    name: "FileSpecSegment",
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
    optional: true,
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
    name: "LogKeywordSegment",
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
    name: "FileSpecSegment",
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
    optional: true,
    terminators: vec![
    ],
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
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FilestreamKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Non_transacted_accessKeywordSegment",
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
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Read_onlyKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Directory_nameKeywordSegment",
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
    name: "Default_fulltext_languageKeywordSegment",
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
    name: "NumericLiteralSegment",
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
Grammar::Ref {
    name: "Default_languageKeywordSegment",
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
    name: "NumericLiteralSegment",
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
Grammar::Ref {
    name: "Nested_triggersKeywordSegment",
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
    name: "OffKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Transform_noise_wordsKeywordSegment",
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
    name: "OffKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Two_digit_year_cutoffKeywordSegment",
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
    name: "Db_chainingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OffKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "TrustworthyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OffKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Persistent_log_bufferKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Directory_nameKeywordSegment",
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
    name: "LedgerKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Catalog_collationKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FileSpecSegment",
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
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AttachKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Enable_brokerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "New_brokerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Error_broker_conversationsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Restricted_userKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FilestreamKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Directory_nameKeywordSegment",
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
    name: "Attach_rebuild_logKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LogicalFileNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecFileNameSegment",
    optional: false,
    allow_gaps: true,
}
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
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SnapshotKeywordSegment",
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

// name='CreateFunctionStatementSegment'
pub static CREATE_FUNCTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "FunctionKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "FunctionOptionSegment",
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
Grammar::Ref {
    name: "ProcedureDefinitionGrammar",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeywordSegment",
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
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonclusteredKeywordSegment",
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
    name: "IndexKeywordSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
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
Grammar::Ref {
    name: "BracketedIndexColumnListGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IncludeKeywordSegment",
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
    optional: true,
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
    name: "RelationalIndexOptionsSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilestreamOnOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AuthorizationKeywordSegment",
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
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AuthorizationKeywordSegment",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='CreateSequenceOptionsSegment'
pub static CREATE_SEQUENCE_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
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
Grammar::Sequence {
    elements: vec![
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
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CacheKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ComputedColumnDefinitionSegment",
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
Grammar::Ref {
    name: "TableIndexSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PeriodSegment",
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
    name: "TableDistributionIndexClause",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilestreamOnOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TextimageOnOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
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
    ],
    optional: true,
    terminators: vec![
    ],
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
Grammar::Ref {
    name: "OnKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<AnySetOf: [<Ref: 'EncryptionKeywordSegment'>, <Ref: 'Native_compilationKeywordSegment'..., <Ref: 'Schemabinding...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
,
Grammar::Ref {
    name: "ExecuteAsClause",
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
    name: "ForKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AppendKeywordSegment",
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
    name: "NotKeywordSegment",
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
Grammar::Ref {
    name: "ReplicationKeywordSegment",
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
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
    optional: false,
    allow_gaps: true,
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Default_schemaKeywordSegment",
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
    name: "Default_languageKeywordSegment",
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
    name: "SidKeywordSegment",
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
    name: "HexadecimalLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Allow_encrypted_value_modificationsKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
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
Grammar::Ref {
    name: "LoginKeywordSegment",
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
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Default_schemaKeywordSegment",
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
    name: "Default_languageKeywordSegment",
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
    name: "Allow_encrypted_value_modificationsKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "FromKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CertificateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsymmetricKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithoutKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Default_schemaKeywordSegment",
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
    name: "Default_languageKeywordSegment",
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
    name: "Allow_encrypted_value_modificationsKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProviderKeywordSegment",
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
    name: "Object_idKeywordSegment",
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
    ],
    optional: true,
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

// name='CreateViewStatementSegment'
pub static CREATE_VIEW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "ViewKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "EncryptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemabindingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "View_metadataKeywordSegment",
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
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
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
    name: "CheckKeywordSegment",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DatatypeSegment'
pub static DATATYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatatypeIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeIdentifierSegment",
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
    name: "VaryingKeywordSegment",
    optional: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TopPercentGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpendatasourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
    name: "QuotedLiteralSegment",
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
    name: "DotSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenqueryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NakedIdentifierSegment",
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
    name: "QuotedLiteralSegment",
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
    name: "OpenRowSetSegment",
    optional: false,
    allow_gaps: true,
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
    name: "OutputClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: false,
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
    name: "CurrentKeywordSegment",
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
Grammar::Ref {
    name: "CursorNameGrammar",
    optional: false,
    allow_gaps: true,
}
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
Grammar::Ref {
    name: "JoinKeywordSegment",
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
    name: "JoinOnConditionSegment",
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
,
Grammar::Ref {
    name: "OpenQuerySegment",
    optional: false,
    allow_gaps: true,
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
    name: "OptionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameSegment",
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
    name: "DelimiterGrammar",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TriggerReferenceSegment",
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
    name: "OnKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "DelimiterGrammar",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NextValueSequenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExtensionReferenceSegment'
pub static EXTENSION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "BatchSegment",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FunctionParameterGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReadonlyKeywordSegment",
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
Grammar::Ref {
    name: "ReservedKeywordBareFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RankFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RankFunctionContentsSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConvertFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConvertFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "CastFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CastFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ReplicateFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplicateFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "WithinGroupFunctionNameSegment",
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
Grammar::Ref {
    name: "WithinGroupClause",
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
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReservedKeywordFunctionNameSegment",
    optional: false,
    allow_gaps: true,
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
    name: "FunctionContentsSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "JsonFunctionNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "JsonFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
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
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawNotSegment",
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
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WithRollupClauseSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenQuerySegment",
    optional: false,
    allow_gaps: true,
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
    name: "PostTableExpressionGrammar",
    optional: true,
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
    name: "OutputClauseSegment",
    optional: true,
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
    name: "ExecuteScriptSegment",
    optional: false,
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
Grammar::OneOf {
    elements: vec![
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
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawNotSegment",
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
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
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

// name='MergeMatchSegment'
pub static MERGE_MATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
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
,
Grammar::Ref {
    name: "OutputClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OptionClauseSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
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
Grammar::OneOf {
    elements: vec![
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
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TargetKeywordSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
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
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SourceKeywordSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
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
Grammar::Ref {
    name: "TableReferenceSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableHintSegment",
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
    optional: true,
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
    allow_gaps: true,
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
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "OffsetClauseSegment",
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
    name: "OffsetClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchClauseSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::OptionallyBracketed()
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SystemKeywordSegment",
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
    name: "PercentKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "AltAliasExpressionSegment",
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
Grammar::AnyNumberOf {
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PercentKeywordSegment",
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
Grammar::Ref {
    name: "TiesKeywordSegment",
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
    min_times: 0,
    max_times: None,
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
    name: "IntoTableSegment",
    optional: true,
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
    name: "OptionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForClauseSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Ref {
    name: "SetClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetClauseSegment",
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
    name: "AssignmentOperatorSegment",
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
    name: "OptionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
    name: "UseStatementSegment",
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
Grammar::Ref {
    name: "AlterDatabaseStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableGraphStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterTableSwitchStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterIndexStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateProcedureStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropProcedureStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropStatisticsStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DisableTriggerStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreatePartitionFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterPartitionSchemeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateMasterKeySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterMasterKeySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropMasterKeySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateSecurityPolicySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterSecurityPolicySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropSecurityPolicySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateSynonymStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropSynonymStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BulkInsertStatementSegment",
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
    name: "BeginEndSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BreakStatement",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ContinueStatement",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GotoStatement",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfExpressionStatement",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReturnStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ThrowStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TryCatchSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WaitForStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WhileExpressionStatement",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeclareCursorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenCursorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FetchCursorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CloseCursorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeallocateCursorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrintStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RaiserrorStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DeclareStatementSegment",
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
Grammar::Ref {
    name: "SetStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTableAsSelectStatementSegment",
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
    name: "UpdateStatisticsStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LabelStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateTypeStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateDatabaseScopedCredentialStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateExternalDataSourceStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SqlcmdCommandSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateExternalFileFormat",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateExternalTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DropExternalTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CopyIntoTableStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateFullTextIndexStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AtomicBeginEndSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReconfigureStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateColumnstoreIndexStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreatePartitionSchemeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AlterPartitionFunctionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenSymmetricKeySegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CreateLoginStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SetContextInfoSegment",
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
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedIndexColumnListGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RelationalIndexOptionsSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
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
    name: "ReferencesConstraintGrammar",
    optional: false,
    allow_gaps: true,
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
    name: "CheckConstraintGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: false,
    allow_gaps: true,
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
    name: "OpenRowSetSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenJsonSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OpenQuerySegment",
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
    name: "StorageLocationSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TableExpressionSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinClauseSegment",
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
// Missing elements match_grammar=<Conditional: []>, type:<class 'sqlfluff.core.parser.grammar.conditional.Conditional'>
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "LeadingDotSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
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
    max_times: Some(2),
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "System_timeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
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
    name: "OfKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
Grammar::Ref {
    name: "ToKeywordSegment",
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
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
Grammar::Ref {
    name: "AndKeywordSegment",
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
    name: "ContainedKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistributedKeywordSegment",
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
    name: "TransactionGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MarkKeywordSegment",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
    name: "TransactionGrammar",
    optional: true,
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
    name: "VariableIdentifierSegment",
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
    name: "DelimiterGrammar",
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
Grammar::Sequence {
    elements: vec![
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
Grammar::Ref {
    name: "DelimiterGrammar",
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
    name: "SaveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TransactionGrammar",
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
    name: "VariableIdentifierSegment",
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
    name: "DelimiterGrammar",
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
    name: "IntoTableSegment",
    optional: true,
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
Grammar::Ref {
    name: "OpenQuerySegment",
    optional: false,
    allow_gaps: true,
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
    name: "PostTableExpressionGrammar",
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
    name: "OutputClauseSegment",
    optional: true,
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
    name: "OptionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
    allow_trailing: false,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonWithNonSelectableGrammar",
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

// name='PercentSegment'
pub static PERCENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='BracketedIdentifierSegment'
pub static BRACKETED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='HashIdentifierSegment'
pub static HASH_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='VariableIdentifierSegment'
pub static VARIABLE_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='BatchDelimiterGrammar'
pub static BATCH_DELIMITER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "GoStatementSegment",
    optional: false,
    allow_gaps: true,
}
);

// name='QuotedLiteralSegmentWithN'
pub static QUOTED_LITERAL_SEGMENT_WITH_N: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='QuotedLiteralSegmentOptWithN'
pub static QUOTED_LITERAL_SEGMENT_OPT_WITH_N: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentWithN",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='IntegerLiteralSegment'
pub static INTEGER_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='BinaryLiteralSegment'
pub static BINARY_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='TransactionGrammar'
pub static TRANSACTION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TransactionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TranKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SystemVariableSegment'
pub static SYSTEM_VARIABLE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='StatementAndDelimiterGrammar'
pub static STATEMENT_AND_DELIMITER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
);

// name='OneOrMoreStatementsGrammar'
pub static ONE_OR_MORE_STATEMENTS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
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

// name='TopPercentGrammar'
pub static TOP_PERCENT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "PercentKeywordSegment",
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

// name='CursorNameGrammar'
pub static CURSOR_NAME_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GlobalKeywordSegment",
    optional: true,
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
);

// name='CredentialGrammar'
pub static CREDENTIAL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IdentityKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecretKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AzureBlobStoragePath'
pub static AZURE_BLOB_STORAGE_PATH: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='AzureDataLakeStorageGen2Path'
pub static AZURE_DATA_LAKE_STORAGE_GEN2_PATH: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='SqlcmdOperatorSegment'
pub static SQLCMD_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='SqlcmdFilePathSegment'
pub static SQLCMD_FILE_PATH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser()
);

// name='FileCompressionSegment'
pub static FILE_COMPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='FileEncodingSegment'
pub static FILE_ENCODING_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='SerdeMethodSegment'
pub static SERDE_METHOD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='ProcedureParameterGrammar'
pub static PROCEDURE_PARAMETER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: true,
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
    ],
    optional: true,
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
// Missing elements match_grammar=<AnySetOf: [<Ref: 'VaryingKeywordSegment'>, <Sequence: [<Ref: 'NotKeywordSegment'>]>, <Ref: 'NullKeywordSegment'...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
,
Grammar::Sequence {
    elements: vec![
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

// name='DateFormatSegment'
pub static DATE_FORMAT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser()
);

// name='LeadingDotSegment'
pub static LEADING_DOT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HexadecimalLiteralSegment'
pub static HEXADECIMAL_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='PlusComparisonSegment'
pub static PLUS_COMPARISON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinusComparisonSegment'
pub static MINUS_COMPARISON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MultiplyComparisonSegment'
pub static MULTIPLY_COMPARISON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DivideComparisonSegment'
pub static DIVIDE_COMPARISON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModuloComparisonSegment'
pub static MODULO_COMPARISON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SizeLiteralSegment'
pub static SIZE_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser()
);

// name='NakedOrQuotedIdentifierGrammar'
pub static NAKED_OR_QUOTED_IDENTIFIER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
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
    name: "BracketedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AdditionAssignmentSegment'
pub static ADDITION_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PlusComparisonSegment",
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
    allow_gaps: true,
}
);

// name='AllowConnectionsSegment'
pub static ALLOW_CONNECTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Allow_connectionsKeywordSegment",
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
    name: "AllKeywordSegment",
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
    name: "Read_onlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Read_writeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AltAliasExpressionSegment'
pub static ALT_ALIAS_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
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
    name: "BracketedIdentifierSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "EqualAliasOperatorSegment",
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

// name='AlterDatabaseStatementSegment'
pub static ALTER_DATABASE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatabaseReferenceSegment",
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
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NameKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BackupStorageRedundancySegment",
    optional: false,
    allow_gaps: true,
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
    name: "AddKeywordSegment",
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
    name: "FileSpecSegmentInAlterDatabase",
    optional: false,
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
    name: "FilegroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedOrQuotedIdentifierGrammar",
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
Grammar::Ref {
    name: "LogKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FileSpecSegmentInAlterDatabase",
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
    name: "RemoveKeywordSegment",
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
    name: "LiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecSegmentInAlterDatabase",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "RemoveKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "FilegroupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FileSpecMaxSizeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EditionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ServiceObjectiveSegment",
    optional: false,
    allow_gaps: true,
}
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Manual_cutoverKeywordSegment",
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
    name: "CollateGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RemoveKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "SecondaryKeywordSegment",
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
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NakedOrQuotedIdentifierGrammar",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AllowConnectionsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ServiceObjectiveSegment",
    optional: false,
    allow_gaps: true,
}
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Perform_cutoverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FailoverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Force_failover_allow_data_lossKeywordSegment",
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

// name='AlterIndexStatementSegment'
pub static ALTER_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RebuildKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Pad_indexKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Sort_in_tempdbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ignore_dup_keyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Statistics_norecomputeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Statistics_incrementalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ResumableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Allow_row_locksKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Allow_page_locksKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "MaxdopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FillfactorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Max_durationKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "OnlineKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Wait_at_low_priorityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Max_durationKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Abort_after_waitKeywordSegment",
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
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "NoneKeywordSegment",
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
    name: "PageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnstoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Columnstore_archiveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Xml_compressionKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Xml_compressionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Sort_in_tempdbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ResumableKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "MaxdopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Max_durationKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "Data_compressionKeywordSegment",
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
    name: "NoneKeywordSegment",
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
    name: "PageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnstoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Columnstore_archiveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "OnlineKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Wait_at_low_priorityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Max_durationKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Abort_after_waitKeywordSegment",
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
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "DisableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReorganizeKeywordSegment",
    optional: false,
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
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Lob_compactionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Compress_all_row_groupsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Allow_row_locksKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Allow_page_locksKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Optimize_for_sequential_keyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ignore_dup_keyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Statistics_norecomputeKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Compression_delayKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
,
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
    name: "ResumeKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Max_durationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxdopKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "Wait_at_low_priorityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Max_durationKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Abort_after_waitKeywordSegment",
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
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PauseKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterMasterKeySegment'
pub static ALTER_MASTER_KEY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MasterKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForceKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RegenerateKeywordSegment",
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
    name: "EncryptionKeywordSegment",
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
    name: "MasterKeyEncryptionSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "EncryptionKeywordSegment",
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
    name: "MasterKeyEncryptionSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterPartitionFunctionSegment'
pub static ALTER_PARTITION_FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
    name: "ObjectReferenceSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SplitKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    name: "MergeKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AlterPartitionSchemeSegment'
pub static ALTER_PARTITION_SCHEME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemeKeywordSegment",
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
    name: "NextKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UsedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
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

// name='AlterSecurityPolicySegment'
pub static ALTER_SECURITY_POLICY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecurityKeywordSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
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
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "FilterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockKeywordSegment",
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
    name: "PredicateKeywordSegment",
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
Grammar::Ref {
    name: "OnKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "BeforeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FilterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockKeywordSegment",
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
    name: "PredicateKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
    name: "StateKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "SchemabindingKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "NotKeywordSegment",
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
Grammar::Ref {
    name: "ReplicationKeywordSegment",
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

// name='AlterTableSwitchStatementSegment'
pub static ALTER_TABLE_SWITCH_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SwitchKeywordSegment",
    optional: false,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "Wait_at_low_priorityKeywordSegment",
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
    name: "Max_durationKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
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
    name: "Abort_after_waitKeywordSegment",
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
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "Truncate_targetKeywordSegment",
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
,
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='AssignmentOperatorSegment'
pub static ASSIGNMENT_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='AtomicBeginEndSegment'
pub static ATOMIC_BEGIN_END_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtomicKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LanguageKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "TransactionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsolationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LevelKeywordSegment",
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
    name: "SnapshotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RepeatableKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SerializableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "DatefirstKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DateformatKeywordSegment",
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
    name: "DateFormatSegment",
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
    name: "Delayed_durabilityKeywordSegment",
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
    name: "DelimiterGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EndKeywordSegment",
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

// name='AutoOptionSegment'
pub static AUTO_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Auto_closeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Auto_shrinkKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Auto_update_statisticsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Auto_update_statistics_asyncKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Auto_create_statisticsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "IncrementalKeywordSegment",
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

// name='BackupStorageRedundancySegment'
pub static BACKUP_STORAGE_REDUNDANCY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Backup_storage_redundancyKeywordSegment",
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
);

// name='BatchSegment'
pub static BATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BatchDelimiterGrammar",
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
    name: "BatchDelimiterGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BeginEndSegment'
pub static BEGIN_END_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BracketedIndexColumnListGrammar'
pub static BRACKETED_INDEX_COLUMN_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
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
);

// name='BreakStatement'
pub static BREAK_STATEMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BreakKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='BulkInsertStatementSegment'
pub static BULK_INSERT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BulkKeywordSegment",
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
    name: "TableReferenceSegment",
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
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BulkInsertStatementWithSegment",
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

// name='BulkInsertStatementWithSegment'
pub static BULK_INSERT_STATEMENT_WITH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "BatchsizeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FirstrowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Kilobytes_per_batchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LastrowKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxerrorsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Rows_per_batchKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "CodepageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DatafiletypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Data_sourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ErrorfileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Errorfile_data_sourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Formatfile_data_sourceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowterminatorKeywordSegment",
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
Grammar::Ref {
    name: "FieldquoteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FormatfileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FieldterminatorKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "OrderKeywordSegment",
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
    name: "Check_constraintsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Fire_triggersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeepidentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeepnullsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TablockKeywordSegment",
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

// name='CastFunctionContentsSegment'
pub static CAST_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
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

// name='CastFunctionNameSegment'
pub static CAST_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CheckConstraintGrammar'
pub static CHECK_CONSTRAINT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CheckKeywordSegment",
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
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplicationKeywordSegment",
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
);

// name='CloseCursorStatementSegment'
pub static CLOSE_CURSOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CloseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CursorNameGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CompatibilityLevelSegment'
pub static COMPATIBILITY_LEVEL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Compatibility_levelKeywordSegment",
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

// name='ComputedColumnDefinitionSegment'
pub static COMPUTED_COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::OptionallyBracketed()
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PersistedKeywordSegment",
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
    name: "NullKeywordSegment",
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

// name='ConnectionConstraintGrammar'
pub static CONNECTION_CONSTRAINT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConnectionKeywordSegment",
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
    name: "TableReferenceSegment",
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
    name: "TableReferenceSegment",
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

// name='ContinueStatement'
pub static CONTINUE_STATEMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ContinueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ConvertFunctionContentsSegment'
pub static CONVERT_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
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
Grammar::Ref {
    name: "CommaSegment",
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

// name='ConvertFunctionNameSegment'
pub static CONVERT_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ConvertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Try_convertKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CopyIntoTableStatementSegment'
pub static COPY_INTO_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CopyKeywordSegment",
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
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnDefinitionSegment",
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
Grammar::Ref {
    name: "FromClauseSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
// Missing elements match_grammar=<AnySetOf: [<Sequence: [<Ref: 'File_typeKeywordSegme..., <Sequence: [<Ref: 'File_formatKeywordSeg..., <Sequence:...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateColumnstoreIndexStatementSegment'
pub static CREATE_COLUMNSTORE_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonclusteredKeywordSegment",
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
    name: "ColumnstoreKeywordSegment",
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
Grammar::Ref {
    name: "BracketedIndexColumnListGrammar",
    optional: true,
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
,
    ],
    optional: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Drop_existingKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "MaxdopKeywordSegment",
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
    name: "OnlineKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Compression_delayKeywordSegment",
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
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MinutesKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "ColumnstoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Columnstore_archiveKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
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

// name='CreateDatabaseScopedCredentialStatementSegment'
pub static CREATE_DATABASE_SCOPED_CREDENTIAL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "ScopedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CredentialKeywordSegment",
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
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CredentialGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateExternalDataSourceStatementSegment'
pub static CREATE_EXTERNAL_DATA_SOURCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SourceKeywordSegment",
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
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableLocationClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Connection_optionsKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
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
    name: "CredentialKeywordSegment",
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
    name: "PushdownKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateExternalFileFormat'
pub static CREATE_EXTERNAL_FILE_FORMAT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalKeywordSegment",
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
    name: "FormatKeywordSegment",
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
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExternalFileFormatDelimitedTextClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalFileFormatRcClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalFileFormatOrcClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalFileFormatParquetClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalFileFormatJsonClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExternalFileFormatDeltaClause",
    optional: false,
    allow_gaps: true,
}
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

// name='CreateExternalTableStatementSegment'
pub static CREATE_EXTERNAL_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnDefinitionSegment",
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
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableLocationClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Data_sourceKeywordSegment",
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
    name: "File_formatKeywordSegment",
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
    name: "Reject_typeKeywordSegment",
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
    name: "ValueKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PercentageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Reject_valueKeywordSegment",
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
    name: "Reject_sample_valueKeywordSegment",
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
    name: "Rejected_row_locationKeywordSegment",
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

// name='CreateFullTextIndexStatementSegment'
pub static CREATE_FULL_TEXT_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FulltextKeywordSegment",
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
// Missing elements match_grammar=<AnySetOf: [<Sequence: [<Ref: 'TypeKeywordSegment'>,..., <Sequence: [<Ref: 'LanguageKeywordSegmen..., <Ref: 'Sta...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "KeyKeywordSegment",
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
// Missing elements match_grammar=<AnySetOf: [<Ref: 'ObjectReferenceSegment'>, <Sequence: [<Ref: 'FilegroupKeywordSegme...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
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
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Change_trackingKeywordSegment",
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
    name: "ManualKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "OffKeywordSegment",
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
Grammar::Ref {
    name: "PopulationKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StoplistKeywordSegment",
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
    name: "OffKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SearchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PropertyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ListKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateLoginStatementSegment'
pub static CREATE_LOGIN_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
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
Grammar::Ref {
    name: "WindowsKeywordSegment",
    optional: false,
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
    name: "ProviderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "CertificateKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsymmetricKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PasswordKeywordSegment",
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
Grammar::Ref {
    name: "Must_changeKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SidKeywordSegment",
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
    name: "HexadecimalLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Default_databaseKeywordSegment",
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
    name: "Default_languageKeywordSegment",
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
    name: "Check_expirationKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "Check_policyKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "CredentialKeywordSegment",
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

// name='CreateMasterKeySegment'
pub static CREATE_MASTER_KEY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MasterKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EncryptionKeywordSegment",
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
    name: "PasswordKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreatePartitionFunctionSegment'
pub static CREATE_PARTITION_FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
    name: "ObjectReferenceSegment",
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
    name: "AsKeywordSegment",
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
Grammar::Ref {
    name: "ForKeywordSegment",
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

// name='CreatePartitionSchemeSegment'
pub static CREATE_PARTITION_SCHEME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemeKeywordSegment",
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
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionKeywordSegment",
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
    name: "AllKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PrimaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateProcedureStatementSegment'
pub static CREATE_PROCEDURE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "ProcKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SemicolonSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "ProcedureParameterListGrammar",
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
Grammar::Delimited {
    elements: vec![
// Missing elements match_grammar=<AnySetOf: [<Ref: 'EncryptionKeywordSegment'>, <Ref: 'RecompileKeywordSegment'>, <Ref: 'Native_compilationKeywor...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReplicationKeywordSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Dedent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProcedureDefinitionGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='CreateSecurityPolicySegment'
pub static CREATE_SECURITY_POLICY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecurityKeywordSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FilterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BlockKeywordSegment",
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
    name: "PredicateKeywordSegment",
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
Grammar::Ref {
    name: "OnKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "BeforeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
    name: "StateKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "SchemabindingKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "NotKeywordSegment",
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
Grammar::Ref {
    name: "ReplicationKeywordSegment",
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

// name='CreateSynonymStatementSegment'
pub static CREATE_SYNONYM_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SynonymKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SynonymReferenceSegment",
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

// name='CreateTableAsSelectStatementSegment'
pub static CREATE_TABLE_AS_SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
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
Grammar::Ref {
    name: "TableDistributionIndexClause",
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
Grammar::OptionallyBracketed()
,
Grammar::Ref {
    name: "OptionClauseSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='CreateTableGraphStatementSegment'
pub static CREATE_TABLE_GRAPH_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "GraphTableConstraintSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ComputedColumnDefinitionSegment",
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
Grammar::Ref {
    name: "TableIndexSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PeriodSegment",
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
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NodeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "EdgeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "OnPartitionOrFilegroupOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='CreateTypeStatementSegment'
pub static CREATE_TYPE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
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
    name: "FromKeywordSegment",
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
    name: "AsKeywordSegment",
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
Grammar::Ref {
    name: "TableIndexSegment",
    optional: false,
    allow_gaps: true,
}
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
    allow_trailing: true,
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DeallocateCursorStatementSegment'
pub static DEALLOCATE_CURSOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeallocateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CursorNameGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DeclareCursorStatementSegment'
pub static DECLARE_CURSOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeclareKeywordSegment",
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
    name: "CursorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LocalKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GlobalKeywordSegment",
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
    name: "Forward_onlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScrollKeywordSegment",
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
    name: "StaticKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeysetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DynamicKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Fast_forwardKeywordSegment",
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
    name: "Read_onlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Scroll_locksKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OptimisticKeywordSegment",
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
    name: "Type_warningKeywordSegment",
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
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DeclareStatementSegment'
pub static DECLARE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeclareKeywordSegment",
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
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
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
    name: "DatatypeSegment",
    optional: false,
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
    name: "TableKeywordSegment",
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
    allow_trailing: true,
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
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='DisableTriggerStatementSegment'
pub static DISABLE_TRIGGER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DisableKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TriggerReferenceSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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

// name='DivisionAssignmentSegment'
pub static DIVISION_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DivideComparisonSegment",
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
    allow_gaps: true,
}
);

// name='DropExternalTableStatementSegment'
pub static DROP_EXTERNAL_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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

// name='DropMasterKeySegment'
pub static DROP_MASTER_KEY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MasterKeywordSegment",
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

// name='DropProcedureStatementSegment'
pub static DROP_PROCEDURE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProcKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "DelimiterGrammar",
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

// name='DropSecurityPolicySegment'
pub static DROP_SECURITY_POLICY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SecurityKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='DropStatisticsStatementSegment'
pub static DROP_STATISTICS_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
,
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='DropSynonymStatementSegment'
pub static DROP_SYNONYM_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SynonymKeywordSegment",
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
    name: "SynonymReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='EditionSegment'
pub static EDITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EditionKeywordSegment",
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
);

// name='EncryptedWithGrammar'
pub static ENCRYPTED_WITH_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EncryptedKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Column_encryption_keyKeywordSegment",
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
    name: "Encryption_typeKeywordSegment",
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
    name: "DeterministicKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RandomizedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "AlgorithmKeywordSegment",
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

// name='EqualAliasOperatorSegment'
pub static EQUAL_ALIAS_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
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
    allow_gaps: true,
}
);

// name='ExecuteAsClause'
pub static EXECUTE_AS_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
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
);

// name='ExecuteAsClauseSegment'
pub static EXECUTE_AS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecKeywordSegment",
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
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CallerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SelfKeywordSegment",
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
);

// name='ExecuteOptionSegment'
pub static EXECUTE_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RecompileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ResultKeywordSegment",
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
Grammar::Ref {
    name: "UndefinedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ResultKeywordSegment",
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
Grammar::Ref {
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ResultKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
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
    name: "DatatypeSegment",
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
Grammar::Ref {
    name: "NullKeywordSegment",
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
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
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
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
    name: "AsKeywordSegment",
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
Grammar::Ref {
    name: "XmlKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
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
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SemicolonSegment",
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
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
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
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
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ExecuteOptionSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
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
    name: "PlusSegment",
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
    name: "LoginUserSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
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
    name: "PlusSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
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
    name: "LoginUserSegment",
    optional: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Data_sourceKeywordSegment",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='ExternalFileFormatDelimitedTextClause'
pub static EXTERNAL_FILE_FORMAT_DELIMITED_TEXT_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "DelimitedtextKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Format_optionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExternalFileFormatDelimitedTextFormatOptionClause",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Data_compressionKeywordSegment",
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
    name: "FileCompressionSegment",
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

// name='ExternalFileFormatDelimitedTextFormatOptionClause'
pub static EXTERNAL_FILE_FORMAT_DELIMITED_TEXT_FORMAT_OPTION_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Field_terminatorKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "String_delimiterKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Date_formatKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Parser_versionKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "First_rowKeywordSegment",
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
    name: "Use_type_defaultKeywordSegment",
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
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "EncodingKeywordSegment",
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
    name: "FileEncodingSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExternalFileFormatDeltaClause'
pub static EXTERNAL_FILE_FORMAT_DELTA_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "DeltaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ExternalFileFormatJsonClause'
pub static EXTERNAL_FILE_FORMAT_JSON_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "JsonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "FileCompressionSegment",
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

// name='ExternalFileFormatOrcClause'
pub static EXTERNAL_FILE_FORMAT_ORC_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "OrcKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "FileCompressionSegment",
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

// name='ExternalFileFormatParquetClause'
pub static EXTERNAL_FILE_FORMAT_PARQUET_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "ParquetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "FileCompressionSegment",
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

// name='ExternalFileFormatRcClause'
pub static EXTERNAL_FILE_FORMAT_RC_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Format_typeKeywordSegment",
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
    name: "RcfileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Serde_methodKeywordSegment",
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
    name: "SerdeMethodSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "FileCompressionSegment",
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

// name='FetchCursorStatementSegment'
pub static FETCH_CURSOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "NextKeywordSegment",
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
    optional: true,
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
    name: "CursorNameGrammar",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
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
);

// name='FileSpecFileGrowthSegment'
pub static FILE_SPEC_FILE_GROWTH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilegrowthKeywordSegment",
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
    name: "SizeLiteralSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "KbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PercentSegment",
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

// name='FileSpecFileNameSegment'
pub static FILE_SPEC_FILE_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilenameKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FileSpecMaxSizeSegment'
pub static FILE_SPEC_MAX_SIZE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxsizeKeywordSegment",
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
    name: "SizeLiteralSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "KbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TbKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FileSpecNewNameSegment'
pub static FILE_SPEC_NEW_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NewnameKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FileSpecSegment'
pub static FILE_SPEC_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "UnbracketedFileSpecSegment",
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

// name='FileSpecSegmentInAlterDatabase'
pub static FILE_SPEC_SEGMENT_IN_ALTER_DATABASE: Lazy<Grammar> = Lazy::new(||
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LogicalFileNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecNewNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecFileNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecSizeSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecMaxSizeSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecFileGrowthSegment",
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

// name='FileSpecSizeSegment'
pub static FILE_SPEC_SIZE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
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
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SizeLiteralSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "KbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "GbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TbKeywordSegment",
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

// name='FilegroupClause'
pub static FILEGROUP_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilegroupNameSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FilegroupNameSegment'
pub static FILEGROUP_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
);

// name='FilestreamOnOptionSegment'
pub static FILESTREAM_ON_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Filestream_onKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FilegroupNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionSchemeNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ForClauseSegment'
pub static FOR_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "BrowseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "JsonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AutoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PathKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "RootKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Include_null_valuesKeywordSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Without_array_wrapperKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "XmlKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PathKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BinaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Base64KeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RootKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ElementsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "XsinilKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AbsentKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExplicitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BinaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Base64KeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RootKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "XmldataKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AutoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BinaryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Base64KeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RootKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ElementsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "XsinilKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AbsentKeywordSegment",
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
    name: "XmldataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "XmlschemaKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='FunctionOptionSegment'
pub static FUNCTION_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "EncryptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SchemabindingKeywordSegment",
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
    name: "ReturnsKeywordSegment",
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
Grammar::Ref {
    name: "CalledKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InputKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ExecuteAsClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InlineKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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

// name='GoStatementSegment'
pub static GO_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IntegerLiteralSegment",
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

// name='GotoStatement'
pub static GOTO_STATEMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GotoKeywordSegment",
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

// name='GraphTableConstraintSegment'
pub static GRAPH_TABLE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "BracketedIndexColumnListGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RelationalIndexOptionsSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
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
    name: "ReferencesConstraintGrammar",
    optional: false,
    allow_gaps: true,
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
    name: "ConnectionConstraintGrammar",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CheckConstraintGrammar",
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

// name='IdentityGrammar'
pub static IDENTITY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IdentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
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

// name='IfClauseSegment'
pub static IF_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
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

// name='IfExpressionStatement'
pub static IF_EXPRESSION_STATEMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IfClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
    optional: false,
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
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IfClauseSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
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
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
    optional: false,
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

// name='JsonFunctionContentsSegment'
pub static JSON_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
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
    name: "ColumnReferenceSegment",
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
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
    name: "AbsentKeywordSegment",
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
    optional: true,
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
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
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
Grammar::Ref {
    name: "ColonSegment",
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
    name: "LiteralGrammar",
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
    name: "ColumnReferenceSegment",
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
    name: "FunctionSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
    name: "AbsentKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullKeywordSegment",
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
    name: "AbsentKeywordSegment",
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
    optional: true,
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='JsonFunctionNameSegment'
pub static JSON_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Json_arrayKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Json_objectKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LabelStatementSegment'
pub static LABEL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NakedIdentifierSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: false,
}
);

// name='LogicalFileNameSegment'
pub static LOGICAL_FILE_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NameKeywordSegment",
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
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='LoginUserSegment'
pub static LOGIN_USER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LoginKeywordSegment",
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
Grammar::Ref {
    name: "RawEqualsSegment",
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

// name='MasterKeyEncryptionSegment'
pub static MASTER_KEY_ENCRYPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ServiceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MasterKeywordSegment",
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
);

// name='MaxDurationSegment'
pub static MAX_DURATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Max_durationKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MinutesKeywordSegment",
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

// name='ModulusAssignmentSegment'
pub static MODULUS_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ModuloComparisonSegment",
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
    allow_gaps: true,
}
);

// name='MultiplicationAssignmentSegment'
pub static MULTIPLICATION_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MultiplyComparisonSegment",
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
    allow_gaps: true,
}
);

// name='NextValueSequenceSegment'
pub static NEXT_VALUE_SEQUENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NextKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ValueKeywordSegment",
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

// name='OnPartitionOrFilegroupOptionSegment'
pub static ON_PARTITION_OR_FILEGROUP_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PartitionSchemeClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilegroupClause",
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
);

// name='OnPartitionsSegment'
pub static ON_PARTITIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
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
    name: "ToKeywordSegment",
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

// name='OpenCursorStatementSegment'
pub static OPEN_CURSOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CursorNameGrammar",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='OpenJsonSegment'
pub static OPEN_JSON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenjsonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
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
    name: "ParameterNameSegment",
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
    name: "OpenJsonWithClauseSegment",
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

// name='OpenJsonWithClauseSegment'
pub static OPEN_JSON_WITH_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: true,
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
    name: "JsonKeywordSegment",
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

// name='OpenQuerySegment'
pub static OPEN_QUERY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenqueryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
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

// name='OpenRowSetSegment'
pub static OPEN_ROW_SET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenrowsetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
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
    name: "QuotedLiteralSegment",
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
Grammar::Ref {
    name: "CommaSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BulkKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FormatfileKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
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
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatasourceKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ErrorfileKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Errorfile_data_sourceKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "MaxerrorsKeywordSegment",
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
    name: "FirstrowKeywordSegment",
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
    name: "LastrowKeywordSegment",
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
    name: "CodepageKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FieldquoteKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "FormatfileKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "Formatfile_data_sourceKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
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
    name: "Single_blobKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Single_clobKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Single_nclobKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
    name: "OpenRowSetWithClauseSegment",
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

// name='OpenRowSetWithClauseSegment'
pub static OPEN_ROW_SET_WITH_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
    name: "DatatypeSegment",
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
Grammar::Ref {
    name: "CollateGrammar",
    optional: true,
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

// name='OpenSymmetricKeySegment'
pub static OPEN_SYMMETRIC_KEY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OpenKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SymmetricKeywordSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DecryptionKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CertificateKeywordSegment",
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
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PasswordKeywordSegment",
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
    name: "AsymmetricKeywordSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
    name: "PasswordKeywordSegment",
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
    name: "SymmetricKeywordSegment",
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
    name: "PasswordKeywordSegment",
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
);

// name='OptionClauseSegment'
pub static OPTION_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "QueryHintSegment",
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

// name='OutputClauseSegment'
pub static OUTPUT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OutputKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
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
Grammar::Ref {
    name: "SingleIdentifierGrammar",
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
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "IntoKeywordSegment",
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
    min_times: 0,
    max_times: None,
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PartitionSchemeClause'
pub static PARTITION_SCHEME_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionSchemeNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
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

// name='PartitionSchemeNameSegment'
pub static PARTITION_SCHEME_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
);

// name='PeriodSegment'
pub static PERIOD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PeriodKeywordSegment",
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
Grammar::Ref {
    name: "System_timeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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

// name='PivotColumnReferenceSegment'
pub static PIVOT_COLUMN_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(3),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='PivotUnpivotStatementSegment'
pub static PIVOT_UNPIVOT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PivotKeywordSegment",
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
    name: "UnpivotKeywordSegment",
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
);

// name='PrintStatementSegment'
pub static PRINT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrintKeywordSegment",
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
    name: "DelimiterGrammar",
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

// name='ProcedureDefinitionGrammar'
pub static PROCEDURE_DEFINITION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AtomicBeginEndSegment",
    optional: false,
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
    name: "NameKeywordSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ProcedureParameterListGrammar'
pub static PROCEDURE_PARAMETER_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OptionallyBracketed()
);

// name='QueryHintSegment'
pub static QUERY_HINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LabelKeywordSegment",
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
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "HashKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MergeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HashKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ConcatKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "UnionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "LoopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MergeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HashKeywordSegment",
    optional: false,
    allow_gaps: true,
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExpandKeywordSegment",
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
    name: "FastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxdopKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MaxrecursionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuerytraceonKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Max_grant_percentKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Min_grant_percentKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "ForceKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ForceKeywordSegment",
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
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExternalpushdownKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ScaleoutexecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "KeepKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeepfixedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RobustKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "PlanKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "Ignore_nonclustered_columnstore_indexKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "No_performance_spoolKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OptimizeKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UnknownKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UnknownKeywordSegment",
    optional: false,
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UnknownKeywordSegment",
    optional: false,
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
    min_times: 0,
    max_times: None,
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ParameterizationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SimpleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForcedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "RecompileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HintKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
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
    min_times: 0,
    max_times: None,
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
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PlanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HintKeywordSegment",
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
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableHintSegment",
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
);

// name='RaiserrorStatementSegment'
pub static RAISERROR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RaiserrorKeywordSegment",
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
    name: "NumericLiteralSegment",
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
    name: "QuotedLiteralSegmentWithN",
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
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "LogKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NowaitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SeterrorKeywordSegment",
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
);

// name='RankFunctionContentsSegment'
pub static RANK_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
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

// name='RankFunctionNameSegment'
pub static RANK_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Dense_rankKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NtileKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RankKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Row_numberKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReconfigureStatementSegment'
pub static RECONFIGURE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReconfigureKeywordSegment",
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
    name: "OverrideKeywordSegment",
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

// name='ReferencesConstraintGrammar'
pub static REFERENCES_CONSTRAINT_GRAMMAR: Lazy<Grammar> = Lazy::new(||
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
// Missing elements match_grammar=<AnySetOf: [<Sequence: [<Ref: 'OnKeywordSegment'>, <..., <Sequence: [<Ref: 'OnKeywordSegment'>, <..., <Sequence:...]>, type:<class 'sqlfluff.core.parser.grammar.anyof.AnySetOf'>
todo!()
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='RelationalIndexOptionsSegment'
pub static RELATIONAL_INDEX_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
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
Grammar::Ref {
    name: "ObjectKeywordSegment",
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
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='ReplicateFunctionContentsSegment'
pub static REPLICATE_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
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
    name: "HexadecimalLiteralSegment",
    optional: false,
    allow_gaps: true,
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
);

// name='ReplicateFunctionNameSegment'
pub static REPLICATE_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReplicateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReservedKeywordBareFunctionNameSegment'
pub static RESERVED_KEYWORD_BARE_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Current_timestampKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "System_userKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='ReservedKeywordFunctionNameSegment'
pub static RESERVED_KEYWORD_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CoalesceKeywordSegment",
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
    name: "NullifKeywordSegment",
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
);

// name='ReturnStatementSegment'
pub static RETURN_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReturnKeywordSegment",
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
    name: "DelimiterGrammar",
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

// name='ServiceObjectiveSegment'
pub static SERVICE_OBJECTIVE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Service_objectiveKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Elastic_poolKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NameKeywordSegment",
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
    name: "NakedOrQuotedIdentifierGrammar",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetContextInfoSegment'
pub static SET_CONTEXT_INFO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Context_infoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "HexadecimalLiteralSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SetStatementSegment'
pub static SET_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
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
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TransactionKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "IsolationKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "LevelKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SnapshotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SerializableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RepeatableKeywordSegment",
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
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CommittedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UncommittedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "DatefirstKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DateformatKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Deadlock_priorityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Lock_timeoutKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Concat_null_yields_nullKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Cursor_close_on_commitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Fips_flaggerKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Identity_insertKeywordSegment",
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
Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OffsetsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Quoted_identifierKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArithabortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ArithignoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FmtonlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NocountKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NoexecKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Numeric_roundabortKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ParseonlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Query_governor_cost_limitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Result_set_cachingKeywordSegment",
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
Grammar::Ref {
    name: "TextsizeKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_defaultsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_null_dflt_offKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_null_dflt_onKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_nullsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_paddingKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ansi_warningsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ForceplanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Showplan_allKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Showplan_textKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Showplan_xmlKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StatisticsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IoKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ProfileKeywordSegment",
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
    name: "XmlKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
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
    name: "Implicit_transactionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Remote_proc_transactionsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Xact_abortKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
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
Grammar::Sequence {
    elements: vec![
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
Grammar::Ref {
    name: "LowKeywordSegment",
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
    name: "HighKeywordSegment",
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
    name: "NumericLiteralSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AssignmentOperatorSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
Grammar::Ref {
    name: "DelimiterGrammar",
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

// name='SqlcmdCommandSegment'
pub static SQLCMD_COMMAND_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SqlcmdOperatorSegment",
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
Grammar::Ref {
    name: "SqlcmdFilePathSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SqlcmdOperatorSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CodeSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='StorageLocationSegment'
pub static STORAGE_LOCATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AzureBlobStoragePath",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "AzureDataLakeStorageGen2Path",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='SubtractionAssignmentSegment'
pub static SUBTRACTION_ASSIGNMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MinusComparisonSegment",
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
    allow_gaps: true,
}
);

// name='SynonymReferenceSegment'
pub static SYNONYM_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
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
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    min_times: 0,
    max_times: Some(1),
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableDistributionClause'
pub static TABLE_DISTRIBUTION_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistributionKeywordSegment",
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
    name: "ReplicateKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Round_robinKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "HashKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableDistributionIndexClause'
pub static TABLE_DISTRIBUTION_INDEX_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableDistributionClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableIndexClause",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TableLocationClause",
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

// name='TableHintSegment'
pub static TABLE_HINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NoexpandKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IndexKeywordSegment",
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
    name: "IndexReferenceSegment",
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
    name: "IndexKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "IndexReferenceSegment",
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
    name: "KeepidentityKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "KeepdefaultsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForceseekKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
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
    min_times: 0,
    max_times: None,
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
    name: "ForcescanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "HoldlockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ignore_constraintsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Ignore_triggersKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NolockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NowaitKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PaglockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReadcommittedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReadcommittedlockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReadpastKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ReaduncommittedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RepeatablereadKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RowlockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SerializableKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "SnapshotKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Spatial_window_max_cellsKeywordSegment",
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
    name: "TablockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TablockxKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "UpdlockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "XlockKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableIndexClause'
pub static TABLE_INDEX_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "HeapKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnstoreKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ClusteredKeywordSegment",
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableIndexSegment'
pub static TABLE_INDEX_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IndexKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UniqueKeywordSegment",
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
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "NonclusteredKeywordSegment",
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
    name: "BracketedIndexColumnListGrammar",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "ClusteredKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ColumnstoreKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "NonclusteredKeywordSegment",
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
    name: "ColumnstoreKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RelationalIndexOptionsSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "OnPartitionOrFilegroupOptionSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FilestreamOnOptionSegment",
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

// name='TableLocationClause'
pub static TABLE_LOCATION_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LocationKeywordSegment",
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
    name: "User_dbKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegmentOptWithN",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TableOptionSegment'
pub static TABLE_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Memory_optimizedKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "DurabilityKeywordSegment",
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
    name: "Schema_onlyKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Schema_and_dataKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
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
    name: "System_versioningKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "History_tableKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "History_retention_periodKeywordSegment",
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
    name: "InfiniteKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DaysKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "WeeksKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "MonthsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "YearsKeywordSegment",
    optional: false,
    allow_gaps: true,
}
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Data_consistency_checkKeywordSegment",
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
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
,
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
    name: "Data_compressionKeywordSegment",
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
    name: "NoneKeywordSegment",
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
    name: "PageKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Xml_compressionKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PartitionsKeywordSegment",
    optional: false,
    allow_gaps: true,
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
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
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Filetable_directoryKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Filetable_collate_filenameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Filetable_primary_key_constraint_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Filetable_streamid_unique_constraint_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Filetable_fullpath_unique_constraint_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "Remote_data_archiveKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
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
    name: "Filter_predicateKeywordSegment",
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
    name: "NullKeywordSegment",
    optional: false,
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
    name: "Migration_stateKeywordSegment",
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
    name: "OutboundKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "InboundKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "PausedKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "Migration_stateKeywordSegment",
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
    name: "PausedKeywordSegment",
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
,
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
    name: "Data_deletionKeywordSegment",
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
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "Filter_columnKeywordSegment",
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
    name: "ColumnReferenceSegment",
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
    name: "Retention_periodKeywordSegment",
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
    name: "NumericLiteralSegment",
    optional: true,
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
    name: "LedgerKeywordSegment",
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
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
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
    name: "Ledger_viewKeywordSegment",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Transaction_id_column_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Sequence_number_column_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Operation_type_column_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Operation_type_desc_column_nameKeywordSegment",
    optional: false,
    allow_gaps: true,
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
    name: "ColumnReferenceSegment",
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
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Append_onlyKeywordSegment",
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
Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
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
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='TextimageOnOptionSegment'
pub static TEXTIMAGE_ON_OPTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "Textimage_onKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FilegroupNameSegment",
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
);

// name='ThrowStatementSegment'
pub static THROW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ThrowKeywordSegment",
    optional: false,
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
Grammar::Ref {
    name: "CommaSegment",
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
    name: "QuotedLiteralSegmentWithN",
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
Grammar::Ref {
    name: "CommaSegment",
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

// name='TryCatchSegment'
pub static TRY_CATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "TryKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "OneOrMoreStatementsGrammar",
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
    name: "TryKeywordSegment",
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
    name: "CatchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: true,
    allow_gaps: true,
}
,
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
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
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "CatchKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='UnbracketedFileSpecSegment'
pub static UNBRACKETED_FILE_SPEC_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LogicalFileNameSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecFileNameSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecSizeSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecMaxSizeSegment",
    optional: true,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "FileSpecFileGrowthSegment",
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

// name='UpdateStatisticsStatementSegment'
pub static UPDATE_STATISTICS_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
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
Grammar::Ref {
    name: "ObjectReferenceSegment",
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
    ],
    optional: true,
    terminators: vec![
    ],
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
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
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FullscanKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "ResampleKeywordSegment",
    optional: false,
    allow_gaps: true,
}
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

// name='WaitForStatementSegment'
pub static WAIT_FOR_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WaitforKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DelayKeywordSegment",
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
    name: "TimeKeywordSegment",
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
    name: "TimeoutKeywordSegment",
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

// name='WhileExpressionStatement'
pub static WHILE_EXPRESSION_STATEMENT: Lazy<Grammar> = Lazy::new(||
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
// Missing elements match_grammar=<class 'sqlfluff.core.parser.segments.meta.Indent'>, type:<class 'sqlfluff.core.parser.segments.base.SegmentMetaclass'>
todo!()
,
Grammar::Ref {
    name: "StatementAndDelimiterGrammar",
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

// name='WithRollupClauseSegment'
pub static WITH_ROLLUP_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "RollupKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='WithinGroupClause'
pub static WITHIN_GROUP_CLAUSE: Lazy<Grammar> = Lazy::new(||
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithinKeywordSegment",
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
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "OrderByClauseSegment",
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
Grammar::Ref {
    name: "OverKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "PartitionClauseSegment",
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

// name='WithinGroupFunctionNameSegment'
pub static WITHIN_GROUP_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "String_aggKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Percentile_contKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
Grammar::Ref {
    name: "Percentile_discKeywordSegment",
    optional: false,
    allow_gaps: true,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    allow_gaps: true,
}
);

// name='Single_nclobKeywordSegment'
pub static SINGLE_NCLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Use_type_defaultKeywordSegment'
pub static USE_TYPE_DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmldocumentKeywordSegment'
pub static XMLDOCUMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Reject_sample_valueKeywordSegment'
pub static REJECT_SAMPLE_VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Pad_indexKeywordSegment'
pub static PAD_INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SnapshotKeywordSegment'
pub static SNAPSHOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_languageKeywordSegment'
pub static DEFAULT_LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConnectionKeywordSegment'
pub static CONNECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HeapKeywordSegment'
pub static HEAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ignore_dup_keyKeywordSegment'
pub static IGNORE_DUP_KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FulltextKeywordSegment'
pub static FULLTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilenameKeywordSegment'
pub static FILENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CodepageKeywordSegment'
pub static CODEPAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IoKeywordSegment'
pub static IO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProfileKeywordSegment'
pub static PROFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RKeywordSegment'
pub static R_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Must_changeKeywordSegment'
pub static MUST_CHANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PredicateKeywordSegment'
pub static PREDICATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartialKeywordSegment'
pub static PARTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncrementalKeywordSegment'
pub static INCREMENTAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Retention_periodKeywordSegment'
pub static RETENTION_PERIOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='QuerytraceonKeywordSegment'
pub static QUERYTRACEON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenjsonKeywordSegment'
pub static OPENJSON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForcescanKeywordSegment'
pub static FORCESCAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LanguageKeywordSegment'
pub static LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Round_robinKeywordSegment'
pub static ROUND_ROBIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaskedKeywordSegment'
pub static MASKED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoginKeywordSegment'
pub static LOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EdgeKeywordSegment'
pub static EDGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GbKeywordSegment'
pub static GB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Elastic_poolKeywordSegment'
pub static ELASTIC_POOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_syyKeywordSegment'
pub static REGR_SYY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_null_dflt_offKeywordSegment'
pub static ANSI_NULL_DFLT_OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InboundKeywordSegment'
pub static INBOUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_create_tableKeywordSegment'
pub static AUTO_CREATE_TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ApplyKeywordSegment'
pub static APPLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutputKeywordSegment'
pub static OUTPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WindowsKeywordSegment'
pub static WINDOWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Row_numberKeywordSegment'
pub static ROW_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_nullsKeywordSegment'
pub static ANSI_NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatableKeywordSegment'
pub static REPEATABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Force_failover_allow_data_lossKeywordSegment'
pub static FORCE_FAILOVER_ALLOW_DATA_LOSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Rejected_row_locationKeywordSegment'
pub static REJECTED_ROW_LOCATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlaggKeywordSegment'
pub static XMLAGG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForceseekKeywordSegment'
pub static FORCESEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BernoulliKeywordSegment'
pub static BERNOULLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LowKeywordSegment'
pub static LOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Persistent_version_store_filegroupKeywordSegment'
pub static PERSISTENT_VERSION_STORE_FILEGROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Errorfile_data_sourceKeywordSegment'
pub static ERRORFILE_DATA_SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnlyKeywordSegment'
pub static ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlvalidateKeywordSegment'
pub static XMLVALIDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ArithabortKeywordSegment'
pub static ARITHABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DiskKeywordSegment'
pub static DISK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ControlKeywordSegment'
pub static CONTROL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SynonymKeywordSegment'
pub static SYNONYM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EditionKeywordSegment'
pub static EDITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PriorKeywordSegment'
pub static PRIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlconcatKeywordSegment'
pub static XMLCONCAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlforestKeywordSegment'
pub static XMLFOREST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WeekKeywordSegment'
pub static WEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Implicit_transactionsKeywordSegment'
pub static IMPLICIT_TRANSACTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filestream_onKeywordSegment'
pub static FILESTREAM_ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Include_null_valuesKeywordSegment'
pub static INCLUDE_NULL_VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FastKeywordSegment'
pub static FAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForceplanKeywordSegment'
pub static FORCEPLAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatefirstKeywordSegment'
pub static DATEFIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgyKeywordSegment'
pub static REGR_AVGY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilterKeywordSegment'
pub static FILTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Truncate_targetKeywordSegment'
pub static TRUNCATE_TARGET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemabindingKeywordSegment'
pub static SCHEMABINDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PolicyKeywordSegment'
pub static POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_schemaKeywordSegment'
pub static DEFAULT_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='User_dbKeywordSegment'
pub static USER_DB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutboundKeywordSegment'
pub static OUTBOUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Directory_nameKeywordSegment'
pub static DIRECTORY_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Restricted_userKeywordSegment'
pub static RESTRICTED_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithinKeywordSegment'
pub static WITHIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HiddenKeywordSegment'
pub static HIDDEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlserializeKeywordSegment'
pub static XMLSERIALIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplicateKeywordSegment'
pub static REPLICATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Service_objectiveKeywordSegment'
pub static SERVICE_OBJECTIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Manual_cutoverKeywordSegment'
pub static MANUAL_CUTOVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinutesKeywordSegment'
pub static MINUTES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlqueryKeywordSegment'
pub static XMLQUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PeriodKeywordSegment'
pub static PERIOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HighKeywordSegment'
pub static HIGH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadonlyKeywordSegment'
pub static READONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetsKeywordSegment'
pub static SETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MinvalueKeywordSegment'
pub static MINVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CycleKeywordSegment'
pub static CYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FormatKeywordSegment'
pub static FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PersistedKeywordSegment'
pub static PERSISTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeltaKeywordSegment'
pub static DELTA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Memory_optimized_dataKeywordSegment'
pub static MEMORY_OPTIMIZED_DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Format_typeKeywordSegment'
pub static FORMAT_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SKeywordSegment'
pub static S_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filetable_directoryKeywordSegment'
pub static FILETABLE_DIRECTORY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecurityKeywordSegment'
pub static SECURITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Min_grant_percentKeywordSegment'
pub static MIN_GRANT_PERCENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Query_governor_cost_limitKeywordSegment'
pub static QUERY_GOVERNOR_COST_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilestreamKeywordSegment'
pub static FILESTREAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sequence_numberKeywordSegment'
pub static SEQUENCE_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablockKeywordSegment'
pub static TABLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='New_brokerKeywordSegment'
pub static NEW_BROKER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_countKeywordSegment'
pub static REGR_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ignore_triggersKeywordSegment'
pub static IGNORE_TRIGGERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlockersKeywordSegment'
pub static BLOCKERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MasterKeywordSegment'
pub static MASTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OutKeywordSegment'
pub static OUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_slopeKeywordSegment'
pub static REGR_SLOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='First_rowKeywordSegment'
pub static FIRST_ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='View_metadataKeywordSegment'
pub static VIEW_METADATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtomicKeywordSegment'
pub static ATOMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filetable_collate_filenameKeywordSegment'
pub static FILETABLE_COLLATE_FILENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DayKeywordSegment'
pub static DAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Abort_after_waitKeywordSegment'
pub static ABORT_AFTER_WAIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Remote_data_archiveKeywordSegment'
pub static REMOTE_DATA_ARCHIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Data_compressionKeywordSegment'
pub static DATA_COMPRESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Context_infoKeywordSegment'
pub static CONTEXT_INFO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ManualKeywordSegment'
pub static MANUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForcedKeywordSegment'
pub static FORCED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_warningsKeywordSegment'
pub static ANSI_WARNINGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncryptionKeywordSegment'
pub static ENCRYPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PropertyKeywordSegment'
pub static PROPERTY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadpastKeywordSegment'
pub static READPAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DataKeywordSegment'
pub static DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Allow_row_locksKeywordSegment'
pub static ALLOW_ROW_LOCKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_contKeywordSegment'
pub static PERCENTILE_CONT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlattributesKeywordSegment'
pub static XMLATTRIBUTES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncodingKeywordSegment'
pub static ENCODING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='File_formatKeywordSegment'
pub static FILE_FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhileKeywordSegment'
pub static WHILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ledger_viewKeywordSegment'
pub static LEDGER_VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Nested_triggersKeywordSegment'
pub static NESTED_TRIGGERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Error_broker_conversationsKeywordSegment'
pub static ERROR_BROKER_CONVERSATIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Format_optionsKeywordSegment'
pub static FORMAT_OPTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReorganizeKeywordSegment'
pub static REORGANIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Connection_optionsKeywordSegment'
pub static CONNECTION_OPTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonthKeywordSegment'
pub static MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlKeywordSegment'
pub static XML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InlineKeywordSegment'
pub static INLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecondaryKeywordSegment'
pub static SECONDARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Operation_type_column_nameKeywordSegment'
pub static OPERATION_TYPE_COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RawKeywordSegment'
pub static RAW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RepeatablereadKeywordSegment'
pub static REPEATABLEREAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RobustKeywordSegment'
pub static ROBUST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Without_array_wrapperKeywordSegment'
pub static WITHOUT_ARRAY_WRAPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ArithignoreKeywordSegment'
pub static ARITHIGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CacheKeywordSegment'
pub static CACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FmtonlyKeywordSegment'
pub static FMTONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Max_durationKeywordSegment'
pub static MAX_DURATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Showplan_allKeywordSegment'
pub static SHOWPLAN_ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Data_sourceKeywordSegment'
pub static DATA_SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WorkKeywordSegment'
pub static WORK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FieldterminatorKeywordSegment'
pub static FIELDTERMINATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Lob_compactionKeywordSegment'
pub static LOB_COMPACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlpiKeywordSegment'
pub static XMLPI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxxKeywordSegment'
pub static REGR_SXX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrcKeywordSegment'
pub static ORC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsolationKeywordSegment'
pub static ISOLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_interceptKeywordSegment'
pub static REGR_INTERCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='File_typeKeywordSegment'
pub static FILE_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsedKeywordSegment'
pub static USED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CallerKeywordSegment'
pub static CALLER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filter_predicateKeywordSegment'
pub static FILTER_PREDICATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LogKeywordSegment'
pub static LOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Compression_delayKeywordSegment'
pub static COMPRESSION_DELAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElementKeywordSegment'
pub static ELEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FailoverKeywordSegment'
pub static FAILOVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PartitionsKeywordSegment'
pub static PARTITIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepdefaultsKeywordSegment'
pub static KEEPDEFAULTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SplitKeywordSegment'
pub static SPLIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Spatial_window_max_cellsKeywordSegment'
pub static SPATIAL_WINDOW_MAX_CELLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Concat_null_yields_nullKeywordSegment'
pub static CONCAT_NULL_YIELDS_NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxvalueKeywordSegment'
pub static MAXVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResumableKeywordSegment'
pub static RESUMABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConcatKeywordSegment'
pub static CONCAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_avgxKeywordSegment'
pub static REGR_AVGX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_sxyKeywordSegment'
pub static REGR_SXY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AtKeywordSegment'
pub static AT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Textimage_onKeywordSegment'
pub static TEXTIMAGE_ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RebuildKeywordSegment'
pub static REBUILD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Remote_proc_transactionsKeywordSegment'
pub static REMOTE_PROC_TRANSACTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NolockKeywordSegment'
pub static NOLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlcastKeywordSegment'
pub static XMLCAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CatchKeywordSegment'
pub static CATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxsizeKeywordSegment'
pub static MAXSIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelfKeywordSegment'
pub static SELF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Change_trackingKeywordSegment'
pub static CHANGE_TRACKING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResultKeywordSegment'
pub static RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnstoreKeywordSegment'
pub static COLUMNSTORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RespectKeywordSegment'
pub static RESPECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TakeKeywordSegment'
pub static TAKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlbinaryKeywordSegment'
pub static XMLBINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnlimitedKeywordSegment'
pub static UNLIMITED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Encryption_typeKeywordSegment'
pub static ENCRYPTION_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JsonKeywordSegment'
pub static JSON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_shrinkKeywordSegment'
pub static AUTO_SHRINK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Legacy_cardinality_estimationKeywordSegment'
pub static LEGACY_CARDINALITY_ESTIMATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlcommentKeywordSegment'
pub static XMLCOMMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatafiletypeKeywordSegment'
pub static DATAFILETYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowlockKeywordSegment'
pub static ROWLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Max_grant_percentKeywordSegment'
pub static MAX_GRANT_PERCENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Xact_abortKeywordSegment'
pub static XACT_ABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AttachKeywordSegment'
pub static ATTACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_create_statisticsKeywordSegment'
pub static AUTO_CREATE_STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CompressionKeywordSegment'
pub static COMPRESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Parser_versionKeywordSegment'
pub static PARSER_VERSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TryKeywordSegment'
pub static TRY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TargetKeywordSegment'
pub static TARGET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElementsKeywordSegment'
pub static ELEMENTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncrementKeywordSegment'
pub static INCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimestampKeywordSegment'
pub static TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YearKeywordSegment'
pub static YEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='String_aggKeywordSegment'
pub static STRING_AGG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NowaitKeywordSegment'
pub static NOWAIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Rows_per_batchKeywordSegment'
pub static ROWS_PER_BATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PageKeywordSegment'
pub static PAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimeKeywordSegment'
pub static TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbortKeywordSegment'
pub static ABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmldataKeywordSegment'
pub static XMLDATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Accelerated_database_recoveryKeywordSegment'
pub static ACCELERATED_DATABASE_RECOVERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForceKeywordSegment'
pub static FORCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Fire_triggersKeywordSegment'
pub static FIRE_TRIGGERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Drop_existingKeywordSegment'
pub static DROP_EXISTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StartKeywordSegment'
pub static START_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='No_performance_spoolKeywordSegment'
pub static NO_PERFORMANCE_SPOOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoexecKeywordSegment'
pub static NOEXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RankKeywordSegment'
pub static RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LastrowKeywordSegment'
pub static LASTROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Columnstore_archiveKeywordSegment'
pub static COLUMNSTORE_ARCHIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Compatibility_levelKeywordSegment'
pub static COMPATIBILITY_LEVEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CredentialKeywordSegment'
pub static CREDENTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlschemaKeywordSegment'
pub static XMLSCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainmentKeywordSegment'
pub static CONTAINMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sort_in_tempdbKeywordSegment'
pub static SORT_IN_TEMPDB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProviderKeywordSegment'
pub static PROVIDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LevelKeywordSegment'
pub static LEVEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmltableKeywordSegment'
pub static XMLTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MbKeywordSegment'
pub static MB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UndefinedKeywordSegment'
pub static UNDEFINED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_databaseKeywordSegment'
pub static DEFAULT_DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeozoneKeywordSegment'
pub static GEOZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NameKeywordSegment'
pub static NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='System_timeKeywordSegment'
pub static SYSTEM_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PausedKeywordSegment'
pub static PAUSED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenqueryKeywordSegment'
pub static OPENQUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SeterrorKeywordSegment'
pub static SETERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Migration_stateKeywordSegment'
pub static MIGRATION_STATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Db_chainingKeywordSegment'
pub static DB_CHAINING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilegroupKeywordSegment'
pub static FILEGROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablockxKeywordSegment'
pub static TABLOCKX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NtileKeywordSegment'
pub static NTILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelimitedtextKeywordSegment'
pub static DELIMITEDTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnlineKeywordSegment'
pub static ONLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ignore_nonclustered_columnstore_indexKeywordSegment'
pub static IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PasswordKeywordSegment'
pub static PASSWORD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PercentageKeywordSegment'
pub static PERCENTAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Allow_encrypted_value_modificationsKeywordSegment'
pub static ALLOW_ENCRYPTED_VALUE_MODIFICATIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PushdownKeywordSegment'
pub static PUSHDOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowterminatorKeywordSegment'
pub static ROWTERMINATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SidKeywordSegment'
pub static SID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Xml_compressionKeywordSegment'
pub static XML_COMPRESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExternalpushdownKeywordSegment'
pub static EXTERNALPUSHDOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LedgerKeywordSegment'
pub static LEDGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GeoKeywordSegment'
pub static GEO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FormatfileKeywordSegment'
pub static FORMATFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transaction_idKeywordSegment'
pub static TRANSACTION_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetvarKeywordSegment'
pub static SETVAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContinueKeywordSegment'
pub static CONTINUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SizeKeywordSegment'
pub static SIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverrideKeywordSegment'
pub static OVERRIDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsymmetricKeywordSegment'
pub static ASYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InputKeywordSegment'
pub static INPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CalledKeywordSegment'
pub static CALLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Operation_type_desc_column_nameKeywordSegment'
pub static OPERATION_TYPE_DESC_COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepKeywordSegment'
pub static KEEP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlparseKeywordSegment'
pub static XMLPARSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SearchKeywordSegment'
pub static SEARCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WaitforKeywordSegment'
pub static WAITFOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnsKeywordSegment'
pub static RETURNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Compress_all_row_groupsKeywordSegment'
pub static COMPRESS_ALL_ROW_GROUPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SourceKeywordSegment'
pub static SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TypeKeywordSegment'
pub static TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NoexpandKeywordSegment'
pub static NOEXPAND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReaduncommittedKeywordSegment'
pub static READUNCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlgorithmKeywordSegment'
pub static ALGORITHM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SequenceKeywordSegment'
pub static SEQUENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScaleoutexecutionKeywordSegment'
pub static SCALEOUTEXECUTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoadKeywordSegment'
pub static LOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PauseKeywordSegment'
pub static PAUSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Reject_typeKeywordSegment'
pub static REJECT_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ObjectKeywordSegment'
pub static OBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxKeywordSegment'
pub static MAX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecurityauditKeywordSegment'
pub static SECURITYAUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HintKeywordSegment'
pub static HINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Database_defaultKeywordSegment'
pub static DATABASE_DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Json_objectKeywordSegment'
pub static JSON_OBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CopyKeywordSegment'
pub static COPY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Kilobytes_per_batchKeywordSegment'
pub static KILOBYTES_PER_BATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RegenerateKeywordSegment'
pub static REGENERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LoopKeywordSegment'
pub static LOOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadcommittedlockKeywordSegment'
pub static READCOMMITTEDLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TrustworthyKeywordSegment'
pub static TRUSTWORTHY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DumpKeywordSegment'
pub static DUMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SparseKeywordSegment'
pub static SPARSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Check_policyKeywordSegment'
pub static CHECK_POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='History_tableKeywordSegment'
pub static HISTORY_TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsteadKeywordSegment'
pub static INSTEAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StateKeywordSegment'
pub static STATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ModifyKeywordSegment'
pub static MODIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdlockKeywordSegment'
pub static UPDLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommittedKeywordSegment'
pub static COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Backup_storage_redundancyKeywordSegment'
pub static BACKUP_STORAGE_REDUNDANCY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PaglockKeywordSegment'
pub static PAGLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParametersKeywordSegment'
pub static PARAMETERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnknownKeywordSegment'
pub static UNKNOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Perform_cutoverKeywordSegment'
pub static PERFORM_CUTOVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Default_fulltext_languageKeywordSegment'
pub static DEFAULT_FULLTEXT_LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainedKeywordSegment'
pub static CONTAINED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_null_dflt_onKeywordSegment'
pub static ANSI_NULL_DFLT_ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StoplistKeywordSegment'
pub static STOPLIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepidentityKeywordSegment'
pub static KEEPIDENTITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScopedKeywordSegment'
pub static SCOPED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UncommittedKeywordSegment'
pub static UNCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatasourceKeywordSegment'
pub static DATASOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InfiniteKeywordSegment'
pub static INFINITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Persistent_log_bufferKeywordSegment'
pub static PERSISTENT_LOG_BUFFER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LabelKeywordSegment'
pub static LABEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Single_clobKeywordSegment'
pub static SINGLE_CLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmliterateKeywordSegment'
pub static XMLITERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SystemKeywordSegment'
pub static SYSTEM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KbKeywordSegment'
pub static KB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxerrorsKeywordSegment'
pub static MAXERRORS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SerializableKeywordSegment'
pub static SERIALIZABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Allow_page_locksKeywordSegment'
pub static ALLOW_PAGE_LOCKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BreakKeywordSegment'
pub static BREAK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistributionKeywordSegment'
pub static DISTRIBUTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DelayKeywordSegment'
pub static DELAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Formatfile_data_sourceKeywordSegment'
pub static FORMATFILE_DATA_SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AutoKeywordSegment'
pub static AUTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Allow_connectionsKeywordSegment'
pub static ALLOW_CONNECTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Reject_valueKeywordSegment'
pub static REJECT_VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PopulationKeywordSegment'
pub static POPULATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeterministicKeywordSegment'
pub static DETERMINISTIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MatchedKeywordSegment'
pub static MATCHED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntervalKeywordSegment'
pub static INTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Statistical_semanticsKeywordSegment'
pub static STATISTICAL_SEMANTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SecretKeywordSegment'
pub static SECRET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Statistics_norecomputeKeywordSegment'
pub static STATISTICS_NORECOMPUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Enable_brokerKeywordSegment'
pub static ENABLE_BROKER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RandomizedKeywordSegment'
pub static RANDOMIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TbKeywordSegment'
pub static TB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NextKeywordSegment'
pub static NEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllowedKeywordSegment'
pub static ALLOWED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Attach_rebuild_logKeywordSegment'
pub static ATTACH_REBUILD_LOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PathKeywordSegment'
pub static PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MonthsKeywordSegment'
pub static MONTHS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Serde_methodKeywordSegment'
pub static SERDE_METHOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transaction_id_column_nameKeywordSegment'
pub static TRANSACTION_ID_COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Numeric_roundabortKeywordSegment'
pub static NUMERIC_ROUNDABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WeeksKeywordSegment'
pub static WEEKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Dense_rankKeywordSegment'
pub static DENSE_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemeKeywordSegment'
pub static SCHEME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxdopKeywordSegment'
pub static MAXDOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlelementKeywordSegment'
pub static XMLELEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AbsentKeywordSegment'
pub static ABSENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadcommittedKeywordSegment'
pub static READCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Quoted_identifierKeywordSegment'
pub static QUOTED_IDENTIFIER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlnamespacesKeywordSegment'
pub static XMLNAMESPACES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NewnameKeywordSegment'
pub static NEWNAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ErrorfileKeywordSegment'
pub static ERRORFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_closeKeywordSegment'
pub static AUTO_CLOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptimizeKeywordSegment'
pub static OPTIMIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MaxrecursionKeywordSegment'
pub static MAXRECURSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExpandKeywordSegment'
pub static EXPAND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Cursor_close_on_commitKeywordSegment'
pub static CURSOR_CLOSE_ON_COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DaysKeywordSegment'
pub static DAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BlockKeywordSegment'
pub static BLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='String_delimiterKeywordSegment'
pub static STRING_DELIMITER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParameterKeywordSegment'
pub static PARAMETER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Deadlock_priorityKeywordSegment'
pub static DEADLOCK_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Catalog_collationKeywordSegment'
pub static CATALOG_COLLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepnullsKeywordSegment'
pub static KEEPNULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Showplan_xmlKeywordSegment'
pub static SHOWPLAN_XML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_paddingKeywordSegment'
pub static ANSI_PADDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Optimize_for_sequential_keyKeywordSegment'
pub static OPTIMIZE_FOR_SEQUENTIAL_KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Sequence_number_column_nameKeywordSegment'
pub static SEQUENCE_NUMBER_COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Result_set_cachingKeywordSegment'
pub static RESULT_SET_CACHING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocountKeywordSegment'
pub static NOCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Append_onlyKeywordSegment'
pub static APPEND_ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_update_statisticsKeywordSegment'
pub static AUTO_UPDATE_STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Date_formatKeywordSegment'
pub static DATE_FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DateformatKeywordSegment'
pub static DATEFORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Errorfile_credentialKeywordSegment'
pub static ERRORFILE_CREDENTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='System_versioningKeywordSegment'
pub static SYSTEM_VERSIONING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Schema_and_dataKeywordSegment'
pub static SCHEMA_AND_DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ServiceKeywordSegment'
pub static SERVICE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OwnerKeywordSegment'
pub static OWNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollupKeywordSegment'
pub static ROLLUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XlockKeywordSegment'
pub static XLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ansi_defaultsKeywordSegment'
pub static ANSI_DEFAULTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Two_digit_year_cutoffKeywordSegment'
pub static TWO_DIGIT_YEAR_CUTOFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DisableKeywordSegment'
pub static DISABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='History_retention_periodKeywordSegment'
pub static HISTORY_RETENTION_PERIOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecompileKeywordSegment'
pub static RECOMPILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RootKeywordSegment'
pub static ROOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Data_deletionKeywordSegment'
pub static DATA_DELETION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filetable_primary_key_constraint_nameKeywordSegment'
pub static FILETABLE_PRIMARY_KEY_CONSTRAINT_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Schema_onlyKeywordSegment'
pub static SCHEMA_ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeepfixedKeywordSegment'
pub static KEEPFIXED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IncludeKeywordSegment'
pub static INCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filter_columnKeywordSegment'
pub static FILTER_COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Ignore_constraintsKeywordSegment'
pub static IGNORE_CONSTRAINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParseonlyKeywordSegment'
pub static PARSEONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FieldquoteKeywordSegment'
pub static FIELDQUOTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Lock_timeoutKeywordSegment'
pub static LOCK_TIMEOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RcfileKeywordSegment'
pub static RCFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RemoveKeywordSegment'
pub static REMOVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XsinilKeywordSegment'
pub static XSINIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValueKeywordSegment'
pub static VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Fips_flaggerKeywordSegment'
pub static FIPS_FLAGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmltextKeywordSegment'
pub static XMLTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParquetKeywordSegment'
pub static PARQUET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RoleKeywordSegment'
pub static ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DurabilityKeywordSegment'
pub static DURABILITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SwitchKeywordSegment'
pub static SWITCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NodeKeywordSegment'
pub static NODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Auto_update_statistics_asyncKeywordSegment'
pub static AUTO_UPDATE_STATISTICS_ASYNC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Memory_optimizedKeywordSegment'
pub static MEMORY_OPTIMIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ZoneKeywordSegment'
pub static ZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Statistics_incrementalKeywordSegment'
pub static STATISTICS_INCREMENTAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Field_terminatorKeywordSegment'
pub static FIELD_TERMINATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FilegrowthKeywordSegment'
pub static FILEGROWTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReceiveKeywordSegment'
pub static RECEIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExplicitKeywordSegment'
pub static EXPLICIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Read_writeKeywordSegment'
pub static READ_WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='XmlexistsKeywordSegment'
pub static XMLEXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Showplan_textKeywordSegment'
pub static SHOWPLAN_TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Json_arrayKeywordSegment'
pub static JSON_ARRAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Single_blobKeywordSegment'
pub static SINGLE_BLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filetable_fullpath_unique_constraint_nameKeywordSegment'
pub static FILETABLE_FULLPATH_UNIQUE_CONSTRAINT_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Filetable_streamid_unique_constraint_nameKeywordSegment'
pub static FILETABLE_STREAMID_UNIQUE_CONSTRAINT_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Wait_at_low_priorityKeywordSegment'
pub static WAIT_AT_LOW_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Data_consistency_checkKeywordSegment'
pub static DATA_CONSISTENCY_CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='YearsKeywordSegment'
pub static YEARS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Percentile_discKeywordSegment'
pub static PERCENTILE_DISC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowguidcolKeywordSegment'
pub static ROWGUIDCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ParameterizationKeywordSegment'
pub static PARAMETERIZATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TimeoutKeywordSegment'
pub static TIMEOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocationKeywordSegment'
pub static LOCATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Non_transacted_accessKeywordSegment'
pub static NON_TRANSACTED_ACCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResumeKeywordSegment'
pub static RESUME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HashKeywordSegment'
pub static HASH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FirstrowKeywordSegment'
pub static FIRSTROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CertificateKeywordSegment'
pub static CERTIFICATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ServerKeywordSegment'
pub static SERVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Transform_noise_wordsKeywordSegment'
pub static TRANSFORM_NOISE_WORDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EncryptedKeywordSegment'
pub static ENCRYPTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Column_encryption_keyKeywordSegment'
pub static COLUMN_ENCRYPTION_KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Delayed_durabilityKeywordSegment'
pub static DELAYED_DURABILITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Check_expirationKeywordSegment'
pub static CHECK_EXPIRATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NormalKeywordSegment'
pub static NORMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Regr_r2KeywordSegment'
pub static REGR_R2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UserKeywordSegment'
pub static USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ClusteredKeywordSegment'
pub static CLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeclareKeywordSegment'
pub static DECLARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PublicKeywordSegment'
pub static PUBLIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Identity_insertKeywordSegment'
pub static IDENTITY_INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SchemaKeywordSegment'
pub static SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LinenoKeywordSegment'
pub static LINENO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_transform_group_for_typeKeywordSegment'
pub static CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_pathKeywordSegment'
pub static CURRENT_PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Fast_forwardKeywordSegment'
pub static FAST_FORWARD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreetexttableKeywordSegment'
pub static FREETEXTTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExternalKeywordSegment'
pub static EXTERNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Session_userKeywordSegment'
pub static SESSION_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CloseKeywordSegment'
pub static CLOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AnyKeywordSegment'
pub static ANY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ShutdownKeywordSegment'
pub static SHUTDOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RevokeKeywordSegment'
pub static REVOKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecKeywordSegment'
pub static EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FunctionKeywordSegment'
pub static FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenrowsetKeywordSegment'
pub static OPENROWSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ScrollKeywordSegment'
pub static SCROLL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CoalesceKeywordSegment'
pub static COALESCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Scroll_locksKeywordSegment'
pub static SCROLL_LOCKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DynamicKeywordSegment'
pub static DYNAMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RaiserrorKeywordSegment'
pub static RAISERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadKeywordSegment'
pub static READ_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentitycolKeywordSegment'
pub static IDENTITYCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RuleKeywordSegment'
pub static RULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReadtextKeywordSegment'
pub static READTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GoKeywordSegment'
pub static GO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CursorKeywordSegment'
pub static CURSOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_default_transform_groupKeywordSegment'
pub static CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PlanKeywordSegment'
pub static PLAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TextsizeKeywordSegment'
pub static TEXTSIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KillKeywordSegment'
pub static KILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TopKeywordSegment'
pub static TOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='System_userKeywordSegment'
pub static SYSTEM_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DenyKeywordSegment'
pub static DENY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UnpivotKeywordSegment'
pub static UNPIVOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_catalogKeywordSegment'
pub static CURRENT_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FreetextKeywordSegment'
pub static FREETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GotoKeywordSegment'
pub static GOTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffsetsKeywordSegment'
pub static OFFSETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FullscanKeywordSegment'
pub static FULLSCAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Read_onlyKeywordSegment'
pub static READ_ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AppendKeywordSegment'
pub static APPEND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SaveKeywordSegment'
pub static SAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Check_constraintsKeywordSegment'
pub static CHECK_CONSTRAINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BrowseKeywordSegment'
pub static BROWSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SomeKeywordSegment'
pub static SOME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SymmetricKeywordSegment'
pub static SYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SemanticsimilaritydetailstableKeywordSegment'
pub static SEMANTICSIMILARITYDETAILSTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LocalKeywordSegment'
pub static LOCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NonclusteredKeywordSegment'
pub static NONCLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeysetKeywordSegment'
pub static KEYSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckpointKeywordSegment'
pub static CHECKPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcKeywordSegment'
pub static PROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Forward_onlyKeywordSegment'
pub static FORWARD_ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReplicationKeywordSegment'
pub static REPLICATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GrantKeywordSegment'
pub static GRANT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='MergeKeywordSegment'
pub static MERGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RowcountKeywordSegment'
pub static ROWCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StatisticsKeywordSegment'
pub static STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenKeywordSegment'
pub static OPEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OverlayKeywordSegment'
pub static OVERLAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BackupKeywordSegment'
pub static BACKUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SemantickeyphrasetableKeywordSegment'
pub static SEMANTICKEYPHRASETABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptionKeywordSegment'
pub static OPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ThrowKeywordSegment'
pub static THROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
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

// name='Try_convertKeywordSegment'
pub static TRY_CONVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpenxmlKeywordSegment'
pub static OPENXML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullifKeywordSegment'
pub static NULLIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='HoldlockKeywordSegment'
pub static HOLDLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TranKeywordSegment'
pub static TRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='StaticKeywordSegment'
pub static STATIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FillfactorKeywordSegment'
pub static FILLFACTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeallocateKeywordSegment'
pub static DEALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BulkKeywordSegment'
pub static BULK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PivotKeywordSegment'
pub static PIVOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetuserKeywordSegment'
pub static SETUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ComputeKeywordSegment'
pub static COMPUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_schemaKeywordSegment'
pub static CURRENT_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WritetextKeywordSegment'
pub static WRITETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='FetchKeywordSegment'
pub static FETCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ResampleKeywordSegment'
pub static RESAMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Type_warningKeywordSegment'
pub static TYPE_WARNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistributedKeywordSegment'
pub static DISTRIBUTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExitKeywordSegment'
pub static EXIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ErrlvlKeywordSegment'
pub static ERRLVL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrintKeywordSegment'
pub static PRINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='GlobalKeywordSegment'
pub static GLOBAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainsKeywordSegment'
pub static CONTAINS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Native_compilationKeywordSegment'
pub static NATIVE_COMPILATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NocheckKeywordSegment'
pub static NOCHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TablesampleKeywordSegment'
pub static TABLESAMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OptimisticKeywordSegment'
pub static OPTIMISTIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DecryptionKeywordSegment'
pub static DECRYPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='BatchsizeKeywordSegment'
pub static BATCHSIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReconfigureKeywordSegment'
pub static RECONFIGURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ConvertKeywordSegment'
pub static CONVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RevertKeywordSegment'
pub static REVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TsequalKeywordSegment'
pub static TSEQUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_roleKeywordSegment'
pub static CURRENT_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ListKeywordSegment'
pub static LIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='UpdatetextKeywordSegment'
pub static UPDATETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ProcedureKeywordSegment'
pub static PROCEDURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ContainstableKeywordSegment'
pub static CONTAINSTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PercentKeywordSegment'
pub static PERCENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IdentityKeywordSegment'
pub static IDENTITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AuthorizationKeywordSegment'
pub static AUTHORIZATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ExecuteKeywordSegment'
pub static EXECUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OpendatasourceKeywordSegment'
pub static OPENDATASOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='NationalKeywordSegment'
pub static NATIONAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='ReturnKeywordSegment'
pub static RETURN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='RestoreKeywordSegment'
pub static RESTORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='SemanticsimilaritytableKeywordSegment'
pub static SEMANTICSIMILARITYTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

// name='Current_userKeywordSegment'
pub static CURRENT_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser()
);

pub fn get_tsql_segment_grammar(name: &str) -> Option<&'static Grammar> {
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
            "PercentSegment" => Some(&PERCENT_SEGMENT),
            "BracketedIdentifierSegment" => Some(&BRACKETED_IDENTIFIER_SEGMENT),
            "HashIdentifierSegment" => Some(&HASH_IDENTIFIER_SEGMENT),
            "VariableIdentifierSegment" => Some(&VARIABLE_IDENTIFIER_SEGMENT),
            "BatchDelimiterGrammar" => Some(&BATCH_DELIMITER_GRAMMAR),
            "QuotedLiteralSegmentWithN" => Some(&QUOTED_LITERAL_SEGMENT_WITH_N),
            "QuotedLiteralSegmentOptWithN" => Some(&QUOTED_LITERAL_SEGMENT_OPT_WITH_N),
            "IntegerLiteralSegment" => Some(&INTEGER_LITERAL_SEGMENT),
            "BinaryLiteralSegment" => Some(&BINARY_LITERAL_SEGMENT),
            "TransactionGrammar" => Some(&TRANSACTION_GRAMMAR),
            "SystemVariableSegment" => Some(&SYSTEM_VARIABLE_SEGMENT),
            "StatementAndDelimiterGrammar" => Some(&STATEMENT_AND_DELIMITER_GRAMMAR),
            "OneOrMoreStatementsGrammar" => Some(&ONE_OR_MORE_STATEMENTS_GRAMMAR),
            "TopPercentGrammar" => Some(&TOP_PERCENT_GRAMMAR),
            "CursorNameGrammar" => Some(&CURSOR_NAME_GRAMMAR),
            "CredentialGrammar" => Some(&CREDENTIAL_GRAMMAR),
            "AzureBlobStoragePath" => Some(&AZURE_BLOB_STORAGE_PATH),
            "AzureDataLakeStorageGen2Path" => Some(&AZURE_DATA_LAKE_STORAGE_GEN2_PATH),
            "SqlcmdOperatorSegment" => Some(&SQLCMD_OPERATOR_SEGMENT),
            "SqlcmdFilePathSegment" => Some(&SQLCMD_FILE_PATH_SEGMENT),
            "FileCompressionSegment" => Some(&FILE_COMPRESSION_SEGMENT),
            "FileEncodingSegment" => Some(&FILE_ENCODING_SEGMENT),
            "SerdeMethodSegment" => Some(&SERDE_METHOD_SEGMENT),
            "ProcedureParameterGrammar" => Some(&PROCEDURE_PARAMETER_GRAMMAR),
            "DateFormatSegment" => Some(&DATE_FORMAT_SEGMENT),
            "LeadingDotSegment" => Some(&LEADING_DOT_SEGMENT),
            "HexadecimalLiteralSegment" => Some(&HEXADECIMAL_LITERAL_SEGMENT),
            "PlusComparisonSegment" => Some(&PLUS_COMPARISON_SEGMENT),
            "MinusComparisonSegment" => Some(&MINUS_COMPARISON_SEGMENT),
            "MultiplyComparisonSegment" => Some(&MULTIPLY_COMPARISON_SEGMENT),
            "DivideComparisonSegment" => Some(&DIVIDE_COMPARISON_SEGMENT),
            "ModuloComparisonSegment" => Some(&MODULO_COMPARISON_SEGMENT),
            "SizeLiteralSegment" => Some(&SIZE_LITERAL_SEGMENT),
            "NakedOrQuotedIdentifierGrammar" => Some(&NAKED_OR_QUOTED_IDENTIFIER_GRAMMAR),
            "AdditionAssignmentSegment" => Some(&ADDITION_ASSIGNMENT_SEGMENT),
            "AllowConnectionsSegment" => Some(&ALLOW_CONNECTIONS_SEGMENT),
            "AltAliasExpressionSegment" => Some(&ALT_ALIAS_EXPRESSION_SEGMENT),
            "AlterDatabaseStatementSegment" => Some(&ALTER_DATABASE_STATEMENT_SEGMENT),
            "AlterIndexStatementSegment" => Some(&ALTER_INDEX_STATEMENT_SEGMENT),
            "AlterMasterKeySegment" => Some(&ALTER_MASTER_KEY_SEGMENT),
            "AlterPartitionFunctionSegment" => Some(&ALTER_PARTITION_FUNCTION_SEGMENT),
            "AlterPartitionSchemeSegment" => Some(&ALTER_PARTITION_SCHEME_SEGMENT),
            "AlterSecurityPolicySegment" => Some(&ALTER_SECURITY_POLICY_SEGMENT),
            "AlterTableSwitchStatementSegment" => Some(&ALTER_TABLE_SWITCH_STATEMENT_SEGMENT),
            "AssignmentOperatorSegment" => Some(&ASSIGNMENT_OPERATOR_SEGMENT),
            "AtomicBeginEndSegment" => Some(&ATOMIC_BEGIN_END_SEGMENT),
            "AutoOptionSegment" => Some(&AUTO_OPTION_SEGMENT),
            "BackupStorageRedundancySegment" => Some(&BACKUP_STORAGE_REDUNDANCY_SEGMENT),
            "BatchSegment" => Some(&BATCH_SEGMENT),
            "BeginEndSegment" => Some(&BEGIN_END_SEGMENT),
            "BracketedIndexColumnListGrammar" => Some(&BRACKETED_INDEX_COLUMN_LIST_GRAMMAR),
            "BreakStatement" => Some(&BREAK_STATEMENT),
            "BulkInsertStatementSegment" => Some(&BULK_INSERT_STATEMENT_SEGMENT),
            "BulkInsertStatementWithSegment" => Some(&BULK_INSERT_STATEMENT_WITH_SEGMENT),
            "CastFunctionContentsSegment" => Some(&CAST_FUNCTION_CONTENTS_SEGMENT),
            "CastFunctionNameSegment" => Some(&CAST_FUNCTION_NAME_SEGMENT),
            "CheckConstraintGrammar" => Some(&CHECK_CONSTRAINT_GRAMMAR),
            "CloseCursorStatementSegment" => Some(&CLOSE_CURSOR_STATEMENT_SEGMENT),
            "CompatibilityLevelSegment" => Some(&COMPATIBILITY_LEVEL_SEGMENT),
            "ComputedColumnDefinitionSegment" => Some(&COMPUTED_COLUMN_DEFINITION_SEGMENT),
            "ConnectionConstraintGrammar" => Some(&CONNECTION_CONSTRAINT_GRAMMAR),
            "ContinueStatement" => Some(&CONTINUE_STATEMENT),
            "ConvertFunctionContentsSegment" => Some(&CONVERT_FUNCTION_CONTENTS_SEGMENT),
            "ConvertFunctionNameSegment" => Some(&CONVERT_FUNCTION_NAME_SEGMENT),
            "CopyIntoTableStatementSegment" => Some(&COPY_INTO_TABLE_STATEMENT_SEGMENT),
            "CreateColumnstoreIndexStatementSegment" => Some(&CREATE_COLUMNSTORE_INDEX_STATEMENT_SEGMENT),
            "CreateDatabaseScopedCredentialStatementSegment" => Some(&CREATE_DATABASE_SCOPED_CREDENTIAL_STATEMENT_SEGMENT),
            "CreateExternalDataSourceStatementSegment" => Some(&CREATE_EXTERNAL_DATA_SOURCE_STATEMENT_SEGMENT),
            "CreateExternalFileFormat" => Some(&CREATE_EXTERNAL_FILE_FORMAT),
            "CreateExternalTableStatementSegment" => Some(&CREATE_EXTERNAL_TABLE_STATEMENT_SEGMENT),
            "CreateFullTextIndexStatementSegment" => Some(&CREATE_FULL_TEXT_INDEX_STATEMENT_SEGMENT),
            "CreateLoginStatementSegment" => Some(&CREATE_LOGIN_STATEMENT_SEGMENT),
            "CreateMasterKeySegment" => Some(&CREATE_MASTER_KEY_SEGMENT),
            "CreatePartitionFunctionSegment" => Some(&CREATE_PARTITION_FUNCTION_SEGMENT),
            "CreatePartitionSchemeSegment" => Some(&CREATE_PARTITION_SCHEME_SEGMENT),
            "CreateProcedureStatementSegment" => Some(&CREATE_PROCEDURE_STATEMENT_SEGMENT),
            "CreateSecurityPolicySegment" => Some(&CREATE_SECURITY_POLICY_SEGMENT),
            "CreateSynonymStatementSegment" => Some(&CREATE_SYNONYM_STATEMENT_SEGMENT),
            "CreateTableAsSelectStatementSegment" => Some(&CREATE_TABLE_AS_SELECT_STATEMENT_SEGMENT),
            "CreateTableGraphStatementSegment" => Some(&CREATE_TABLE_GRAPH_STATEMENT_SEGMENT),
            "CreateTypeStatementSegment" => Some(&CREATE_TYPE_STATEMENT_SEGMENT),
            "DeallocateCursorStatementSegment" => Some(&DEALLOCATE_CURSOR_STATEMENT_SEGMENT),
            "DeclareCursorStatementSegment" => Some(&DECLARE_CURSOR_STATEMENT_SEGMENT),
            "DeclareStatementSegment" => Some(&DECLARE_STATEMENT_SEGMENT),
            "DisableTriggerStatementSegment" => Some(&DISABLE_TRIGGER_STATEMENT_SEGMENT),
            "DivisionAssignmentSegment" => Some(&DIVISION_ASSIGNMENT_SEGMENT),
            "DropExternalTableStatementSegment" => Some(&DROP_EXTERNAL_TABLE_STATEMENT_SEGMENT),
            "DropMasterKeySegment" => Some(&DROP_MASTER_KEY_SEGMENT),
            "DropProcedureStatementSegment" => Some(&DROP_PROCEDURE_STATEMENT_SEGMENT),
            "DropSecurityPolicySegment" => Some(&DROP_SECURITY_POLICY_SEGMENT),
            "DropStatisticsStatementSegment" => Some(&DROP_STATISTICS_STATEMENT_SEGMENT),
            "DropSynonymStatementSegment" => Some(&DROP_SYNONYM_STATEMENT_SEGMENT),
            "EditionSegment" => Some(&EDITION_SEGMENT),
            "EncryptedWithGrammar" => Some(&ENCRYPTED_WITH_GRAMMAR),
            "EqualAliasOperatorSegment" => Some(&EQUAL_ALIAS_OPERATOR_SEGMENT),
            "ExecuteAsClause" => Some(&EXECUTE_AS_CLAUSE),
            "ExecuteAsClauseSegment" => Some(&EXECUTE_AS_CLAUSE_SEGMENT),
            "ExecuteOptionSegment" => Some(&EXECUTE_OPTION_SEGMENT),
            "ExecuteScriptSegment" => Some(&EXECUTE_SCRIPT_SEGMENT),
            "ExternalFileFormatDelimitedTextClause" => Some(&EXTERNAL_FILE_FORMAT_DELIMITED_TEXT_CLAUSE),
            "ExternalFileFormatDelimitedTextFormatOptionClause" => Some(&EXTERNAL_FILE_FORMAT_DELIMITED_TEXT_FORMAT_OPTION_CLAUSE),
            "ExternalFileFormatDeltaClause" => Some(&EXTERNAL_FILE_FORMAT_DELTA_CLAUSE),
            "ExternalFileFormatJsonClause" => Some(&EXTERNAL_FILE_FORMAT_JSON_CLAUSE),
            "ExternalFileFormatOrcClause" => Some(&EXTERNAL_FILE_FORMAT_ORC_CLAUSE),
            "ExternalFileFormatParquetClause" => Some(&EXTERNAL_FILE_FORMAT_PARQUET_CLAUSE),
            "ExternalFileFormatRcClause" => Some(&EXTERNAL_FILE_FORMAT_RC_CLAUSE),
            "FetchCursorStatementSegment" => Some(&FETCH_CURSOR_STATEMENT_SEGMENT),
            "FileSpecFileGrowthSegment" => Some(&FILE_SPEC_FILE_GROWTH_SEGMENT),
            "FileSpecFileNameSegment" => Some(&FILE_SPEC_FILE_NAME_SEGMENT),
            "FileSpecMaxSizeSegment" => Some(&FILE_SPEC_MAX_SIZE_SEGMENT),
            "FileSpecNewNameSegment" => Some(&FILE_SPEC_NEW_NAME_SEGMENT),
            "FileSpecSegment" => Some(&FILE_SPEC_SEGMENT),
            "FileSpecSegmentInAlterDatabase" => Some(&FILE_SPEC_SEGMENT_IN_ALTER_DATABASE),
            "FileSpecSizeSegment" => Some(&FILE_SPEC_SIZE_SEGMENT),
            "FilegroupClause" => Some(&FILEGROUP_CLAUSE),
            "FilegroupNameSegment" => Some(&FILEGROUP_NAME_SEGMENT),
            "FilestreamOnOptionSegment" => Some(&FILESTREAM_ON_OPTION_SEGMENT),
            "ForClauseSegment" => Some(&FOR_CLAUSE_SEGMENT),
            "FunctionOptionSegment" => Some(&FUNCTION_OPTION_SEGMENT),
            "GoStatementSegment" => Some(&GO_STATEMENT_SEGMENT),
            "GotoStatement" => Some(&GOTO_STATEMENT),
            "GraphTableConstraintSegment" => Some(&GRAPH_TABLE_CONSTRAINT_SEGMENT),
            "IdentityGrammar" => Some(&IDENTITY_GRAMMAR),
            "IfClauseSegment" => Some(&IF_CLAUSE_SEGMENT),
            "IfExpressionStatement" => Some(&IF_EXPRESSION_STATEMENT),
            "IntoTableSegment" => Some(&INTO_TABLE_SEGMENT),
            "JsonFunctionContentsSegment" => Some(&JSON_FUNCTION_CONTENTS_SEGMENT),
            "JsonFunctionNameSegment" => Some(&JSON_FUNCTION_NAME_SEGMENT),
            "LabelStatementSegment" => Some(&LABEL_STATEMENT_SEGMENT),
            "LogicalFileNameSegment" => Some(&LOGICAL_FILE_NAME_SEGMENT),
            "LoginUserSegment" => Some(&LOGIN_USER_SEGMENT),
            "MasterKeyEncryptionSegment" => Some(&MASTER_KEY_ENCRYPTION_SEGMENT),
            "MaxDurationSegment" => Some(&MAX_DURATION_SEGMENT),
            "ModulusAssignmentSegment" => Some(&MODULUS_ASSIGNMENT_SEGMENT),
            "MultiplicationAssignmentSegment" => Some(&MULTIPLICATION_ASSIGNMENT_SEGMENT),
            "NextValueSequenceSegment" => Some(&NEXT_VALUE_SEQUENCE_SEGMENT),
            "OnPartitionOrFilegroupOptionSegment" => Some(&ON_PARTITION_OR_FILEGROUP_OPTION_SEGMENT),
            "OnPartitionsSegment" => Some(&ON_PARTITIONS_SEGMENT),
            "OpenCursorStatementSegment" => Some(&OPEN_CURSOR_STATEMENT_SEGMENT),
            "OpenJsonSegment" => Some(&OPEN_JSON_SEGMENT),
            "OpenJsonWithClauseSegment" => Some(&OPEN_JSON_WITH_CLAUSE_SEGMENT),
            "OpenQuerySegment" => Some(&OPEN_QUERY_SEGMENT),
            "OpenRowSetSegment" => Some(&OPEN_ROW_SET_SEGMENT),
            "OpenRowSetWithClauseSegment" => Some(&OPEN_ROW_SET_WITH_CLAUSE_SEGMENT),
            "OpenSymmetricKeySegment" => Some(&OPEN_SYMMETRIC_KEY_SEGMENT),
            "OptionClauseSegment" => Some(&OPTION_CLAUSE_SEGMENT),
            "OutputClauseSegment" => Some(&OUTPUT_CLAUSE_SEGMENT),
            "PartitionSchemeClause" => Some(&PARTITION_SCHEME_CLAUSE),
            "PartitionSchemeNameSegment" => Some(&PARTITION_SCHEME_NAME_SEGMENT),
            "PeriodSegment" => Some(&PERIOD_SEGMENT),
            "PivotColumnReferenceSegment" => Some(&PIVOT_COLUMN_REFERENCE_SEGMENT),
            "PivotUnpivotStatementSegment" => Some(&PIVOT_UNPIVOT_STATEMENT_SEGMENT),
            "PrintStatementSegment" => Some(&PRINT_STATEMENT_SEGMENT),
            "ProcedureDefinitionGrammar" => Some(&PROCEDURE_DEFINITION_GRAMMAR),
            "ProcedureParameterListGrammar" => Some(&PROCEDURE_PARAMETER_LIST_GRAMMAR),
            "QueryHintSegment" => Some(&QUERY_HINT_SEGMENT),
            "RaiserrorStatementSegment" => Some(&RAISERROR_STATEMENT_SEGMENT),
            "RankFunctionContentsSegment" => Some(&RANK_FUNCTION_CONTENTS_SEGMENT),
            "RankFunctionNameSegment" => Some(&RANK_FUNCTION_NAME_SEGMENT),
            "ReconfigureStatementSegment" => Some(&RECONFIGURE_STATEMENT_SEGMENT),
            "ReferencesConstraintGrammar" => Some(&REFERENCES_CONSTRAINT_GRAMMAR),
            "RelationalIndexOptionsSegment" => Some(&RELATIONAL_INDEX_OPTIONS_SEGMENT),
            "RenameStatementSegment" => Some(&RENAME_STATEMENT_SEGMENT),
            "ReplicateFunctionContentsSegment" => Some(&REPLICATE_FUNCTION_CONTENTS_SEGMENT),
            "ReplicateFunctionNameSegment" => Some(&REPLICATE_FUNCTION_NAME_SEGMENT),
            "ReservedKeywordBareFunctionNameSegment" => Some(&RESERVED_KEYWORD_BARE_FUNCTION_NAME_SEGMENT),
            "ReservedKeywordFunctionNameSegment" => Some(&RESERVED_KEYWORD_FUNCTION_NAME_SEGMENT),
            "ReturnStatementSegment" => Some(&RETURN_STATEMENT_SEGMENT),
            "ServiceObjectiveSegment" => Some(&SERVICE_OBJECTIVE_SEGMENT),
            "SetContextInfoSegment" => Some(&SET_CONTEXT_INFO_SEGMENT),
            "SetStatementSegment" => Some(&SET_STATEMENT_SEGMENT),
            "SqlcmdCommandSegment" => Some(&SQLCMD_COMMAND_SEGMENT),
            "StorageLocationSegment" => Some(&STORAGE_LOCATION_SEGMENT),
            "SubtractionAssignmentSegment" => Some(&SUBTRACTION_ASSIGNMENT_SEGMENT),
            "SynonymReferenceSegment" => Some(&SYNONYM_REFERENCE_SEGMENT),
            "TableDistributionClause" => Some(&TABLE_DISTRIBUTION_CLAUSE),
            "TableDistributionIndexClause" => Some(&TABLE_DISTRIBUTION_INDEX_CLAUSE),
            "TableHintSegment" => Some(&TABLE_HINT_SEGMENT),
            "TableIndexClause" => Some(&TABLE_INDEX_CLAUSE),
            "TableIndexSegment" => Some(&TABLE_INDEX_SEGMENT),
            "TableLocationClause" => Some(&TABLE_LOCATION_CLAUSE),
            "TableOptionSegment" => Some(&TABLE_OPTION_SEGMENT),
            "TextimageOnOptionSegment" => Some(&TEXTIMAGE_ON_OPTION_SEGMENT),
            "ThrowStatementSegment" => Some(&THROW_STATEMENT_SEGMENT),
            "TryCatchSegment" => Some(&TRY_CATCH_SEGMENT),
            "UnbracketedFileSpecSegment" => Some(&UNBRACKETED_FILE_SPEC_SEGMENT),
            "UpdateStatisticsStatementSegment" => Some(&UPDATE_STATISTICS_STATEMENT_SEGMENT),
            "WaitForStatementSegment" => Some(&WAIT_FOR_STATEMENT_SEGMENT),
            "WhileExpressionStatement" => Some(&WHILE_EXPRESSION_STATEMENT),
            "WithRollupClauseSegment" => Some(&WITH_ROLLUP_CLAUSE_SEGMENT),
            "WithinGroupClause" => Some(&WITHIN_GROUP_CLAUSE),
            "WithinGroupFunctionNameSegment" => Some(&WITHIN_GROUP_FUNCTION_NAME_SEGMENT),
            "Single_nclobKeywordSegment" => Some(&SINGLE_NCLOB_KEYWORD_SEGMENT),
            "Use_type_defaultKeywordSegment" => Some(&USE_TYPE_DEFAULT_KEYWORD_SEGMENT),
            "XmldocumentKeywordSegment" => Some(&XMLDOCUMENT_KEYWORD_SEGMENT),
            "Reject_sample_valueKeywordSegment" => Some(&REJECT_SAMPLE_VALUE_KEYWORD_SEGMENT),
            "Pad_indexKeywordSegment" => Some(&PAD_INDEX_KEYWORD_SEGMENT),
            "SnapshotKeywordSegment" => Some(&SNAPSHOT_KEYWORD_SEGMENT),
            "Default_languageKeywordSegment" => Some(&DEFAULT_LANGUAGE_KEYWORD_SEGMENT),
            "ConnectionKeywordSegment" => Some(&CONNECTION_KEYWORD_SEGMENT),
            "HeapKeywordSegment" => Some(&HEAP_KEYWORD_SEGMENT),
            "Ignore_dup_keyKeywordSegment" => Some(&IGNORE_DUP_KEY_KEYWORD_SEGMENT),
            "FulltextKeywordSegment" => Some(&FULLTEXT_KEYWORD_SEGMENT),
            "FilenameKeywordSegment" => Some(&FILENAME_KEYWORD_SEGMENT),
            "CodepageKeywordSegment" => Some(&CODEPAGE_KEYWORD_SEGMENT),
            "IoKeywordSegment" => Some(&IO_KEYWORD_SEGMENT),
            "ProfileKeywordSegment" => Some(&PROFILE_KEYWORD_SEGMENT),
            "RKeywordSegment" => Some(&R_KEYWORD_SEGMENT),
            "PrecisionKeywordSegment" => Some(&PRECISION_KEYWORD_SEGMENT),
            "Must_changeKeywordSegment" => Some(&MUST_CHANGE_KEYWORD_SEGMENT),
            "PredicateKeywordSegment" => Some(&PREDICATE_KEYWORD_SEGMENT),
            "PartialKeywordSegment" => Some(&PARTIAL_KEYWORD_SEGMENT),
            "IncrementalKeywordSegment" => Some(&INCREMENTAL_KEYWORD_SEGMENT),
            "Retention_periodKeywordSegment" => Some(&RETENTION_PERIOD_KEYWORD_SEGMENT),
            "QuerytraceonKeywordSegment" => Some(&QUERYTRACEON_KEYWORD_SEGMENT),
            "OpenjsonKeywordSegment" => Some(&OPENJSON_KEYWORD_SEGMENT),
            "ForcescanKeywordSegment" => Some(&FORCESCAN_KEYWORD_SEGMENT),
            "UnboundedKeywordSegment" => Some(&UNBOUNDED_KEYWORD_SEGMENT),
            "LanguageKeywordSegment" => Some(&LANGUAGE_KEYWORD_SEGMENT),
            "Round_robinKeywordSegment" => Some(&ROUND_ROBIN_KEYWORD_SEGMENT),
            "MaskedKeywordSegment" => Some(&MASKED_KEYWORD_SEGMENT),
            "LoginKeywordSegment" => Some(&LOGIN_KEYWORD_SEGMENT),
            "EdgeKeywordSegment" => Some(&EDGE_KEYWORD_SEGMENT),
            "GbKeywordSegment" => Some(&GB_KEYWORD_SEGMENT),
            "Elastic_poolKeywordSegment" => Some(&ELASTIC_POOL_KEYWORD_SEGMENT),
            "Regr_syyKeywordSegment" => Some(&REGR_SYY_KEYWORD_SEGMENT),
            "FollowingKeywordSegment" => Some(&FOLLOWING_KEYWORD_SEGMENT),
            "Ansi_null_dflt_offKeywordSegment" => Some(&ANSI_NULL_DFLT_OFF_KEYWORD_SEGMENT),
            "InboundKeywordSegment" => Some(&INBOUND_KEYWORD_SEGMENT),
            "Auto_create_tableKeywordSegment" => Some(&AUTO_CREATE_TABLE_KEYWORD_SEGMENT),
            "ApplyKeywordSegment" => Some(&APPLY_KEYWORD_SEGMENT),
            "OutputKeywordSegment" => Some(&OUTPUT_KEYWORD_SEGMENT),
            "WindowsKeywordSegment" => Some(&WINDOWS_KEYWORD_SEGMENT),
            "Row_numberKeywordSegment" => Some(&ROW_NUMBER_KEYWORD_SEGMENT),
            "Ansi_nullsKeywordSegment" => Some(&ANSI_NULLS_KEYWORD_SEGMENT),
            "RepeatableKeywordSegment" => Some(&REPEATABLE_KEYWORD_SEGMENT),
            "Force_failover_allow_data_lossKeywordSegment" => Some(&FORCE_FAILOVER_ALLOW_DATA_LOSS_KEYWORD_SEGMENT),
            "Rejected_row_locationKeywordSegment" => Some(&REJECTED_ROW_LOCATION_KEYWORD_SEGMENT),
            "XmlaggKeywordSegment" => Some(&XMLAGG_KEYWORD_SEGMENT),
            "ForceseekKeywordSegment" => Some(&FORCESEEK_KEYWORD_SEGMENT),
            "BernoulliKeywordSegment" => Some(&BERNOULLI_KEYWORD_SEGMENT),
            "LowKeywordSegment" => Some(&LOW_KEYWORD_SEGMENT),
            "Persistent_version_store_filegroupKeywordSegment" => Some(&PERSISTENT_VERSION_STORE_FILEGROUP_KEYWORD_SEGMENT),
            "Errorfile_data_sourceKeywordSegment" => Some(&ERRORFILE_DATA_SOURCE_KEYWORD_SEGMENT),
            "OnlyKeywordSegment" => Some(&ONLY_KEYWORD_SEGMENT),
            "XmlvalidateKeywordSegment" => Some(&XMLVALIDATE_KEYWORD_SEGMENT),
            "ArithabortKeywordSegment" => Some(&ARITHABORT_KEYWORD_SEGMENT),
            "DiskKeywordSegment" => Some(&DISK_KEYWORD_SEGMENT),
            "ControlKeywordSegment" => Some(&CONTROL_KEYWORD_SEGMENT),
            "SynonymKeywordSegment" => Some(&SYNONYM_KEYWORD_SEGMENT),
            "EditionKeywordSegment" => Some(&EDITION_KEYWORD_SEGMENT),
            "PriorKeywordSegment" => Some(&PRIOR_KEYWORD_SEGMENT),
            "XmlconcatKeywordSegment" => Some(&XMLCONCAT_KEYWORD_SEGMENT),
            "XmlforestKeywordSegment" => Some(&XMLFOREST_KEYWORD_SEGMENT),
            "WeekKeywordSegment" => Some(&WEEK_KEYWORD_SEGMENT),
            "Implicit_transactionsKeywordSegment" => Some(&IMPLICIT_TRANSACTIONS_KEYWORD_SEGMENT),
            "Filestream_onKeywordSegment" => Some(&FILESTREAM_ON_KEYWORD_SEGMENT),
            "CastKeywordSegment" => Some(&CAST_KEYWORD_SEGMENT),
            "Include_null_valuesKeywordSegment" => Some(&INCLUDE_NULL_VALUES_KEYWORD_SEGMENT),
            "FastKeywordSegment" => Some(&FAST_KEYWORD_SEGMENT),
            "ForceplanKeywordSegment" => Some(&FORCEPLAN_KEYWORD_SEGMENT),
            "DatefirstKeywordSegment" => Some(&DATEFIRST_KEYWORD_SEGMENT),
            "Regr_avgyKeywordSegment" => Some(&REGR_AVGY_KEYWORD_SEGMENT),
            "FilterKeywordSegment" => Some(&FILTER_KEYWORD_SEGMENT),
            "Truncate_targetKeywordSegment" => Some(&TRUNCATE_TARGET_KEYWORD_SEGMENT),
            "SchemabindingKeywordSegment" => Some(&SCHEMABINDING_KEYWORD_SEGMENT),
            "PolicyKeywordSegment" => Some(&POLICY_KEYWORD_SEGMENT),
            "Default_schemaKeywordSegment" => Some(&DEFAULT_SCHEMA_KEYWORD_SEGMENT),
            "User_dbKeywordSegment" => Some(&USER_DB_KEYWORD_SEGMENT),
            "OutboundKeywordSegment" => Some(&OUTBOUND_KEYWORD_SEGMENT),
            "Directory_nameKeywordSegment" => Some(&DIRECTORY_NAME_KEYWORD_SEGMENT),
            "Restricted_userKeywordSegment" => Some(&RESTRICTED_USER_KEYWORD_SEGMENT),
            "WithinKeywordSegment" => Some(&WITHIN_KEYWORD_SEGMENT),
            "HiddenKeywordSegment" => Some(&HIDDEN_KEYWORD_SEGMENT),
            "XmlserializeKeywordSegment" => Some(&XMLSERIALIZE_KEYWORD_SEGMENT),
            "ReplicateKeywordSegment" => Some(&REPLICATE_KEYWORD_SEGMENT),
            "Service_objectiveKeywordSegment" => Some(&SERVICE_OBJECTIVE_KEYWORD_SEGMENT),
            "Manual_cutoverKeywordSegment" => Some(&MANUAL_CUTOVER_KEYWORD_SEGMENT),
            "MinutesKeywordSegment" => Some(&MINUTES_KEYWORD_SEGMENT),
            "XmlqueryKeywordSegment" => Some(&XMLQUERY_KEYWORD_SEGMENT),
            "PeriodKeywordSegment" => Some(&PERIOD_KEYWORD_SEGMENT),
            "HighKeywordSegment" => Some(&HIGH_KEYWORD_SEGMENT),
            "PartitionKeywordSegment" => Some(&PARTITION_KEYWORD_SEGMENT),
            "ReadonlyKeywordSegment" => Some(&READONLY_KEYWORD_SEGMENT),
            "SetsKeywordSegment" => Some(&SETS_KEYWORD_SEGMENT),
            "MinvalueKeywordSegment" => Some(&MINVALUE_KEYWORD_SEGMENT),
            "CycleKeywordSegment" => Some(&CYCLE_KEYWORD_SEGMENT),
            "FormatKeywordSegment" => Some(&FORMAT_KEYWORD_SEGMENT),
            "PersistedKeywordSegment" => Some(&PERSISTED_KEYWORD_SEGMENT),
            "DeltaKeywordSegment" => Some(&DELTA_KEYWORD_SEGMENT),
            "Memory_optimized_dataKeywordSegment" => Some(&MEMORY_OPTIMIZED_DATA_KEYWORD_SEGMENT),
            "Format_typeKeywordSegment" => Some(&FORMAT_TYPE_KEYWORD_SEGMENT),
            "SKeywordSegment" => Some(&S_KEYWORD_SEGMENT),
            "Filetable_directoryKeywordSegment" => Some(&FILETABLE_DIRECTORY_KEYWORD_SEGMENT),
            "SecurityKeywordSegment" => Some(&SECURITY_KEYWORD_SEGMENT),
            "Min_grant_percentKeywordSegment" => Some(&MIN_GRANT_PERCENT_KEYWORD_SEGMENT),
            "Query_governor_cost_limitKeywordSegment" => Some(&QUERY_GOVERNOR_COST_LIMIT_KEYWORD_SEGMENT),
            "FilestreamKeywordSegment" => Some(&FILESTREAM_KEYWORD_SEGMENT),
            "Sequence_numberKeywordSegment" => Some(&SEQUENCE_NUMBER_KEYWORD_SEGMENT),
            "TablockKeywordSegment" => Some(&TABLOCK_KEYWORD_SEGMENT),
            "New_brokerKeywordSegment" => Some(&NEW_BROKER_KEYWORD_SEGMENT),
            "Regr_countKeywordSegment" => Some(&REGR_COUNT_KEYWORD_SEGMENT),
            "Ignore_triggersKeywordSegment" => Some(&IGNORE_TRIGGERS_KEYWORD_SEGMENT),
            "BlockersKeywordSegment" => Some(&BLOCKERS_KEYWORD_SEGMENT),
            "MasterKeywordSegment" => Some(&MASTER_KEYWORD_SEGMENT),
            "OutKeywordSegment" => Some(&OUT_KEYWORD_SEGMENT),
            "Regr_slopeKeywordSegment" => Some(&REGR_SLOPE_KEYWORD_SEGMENT),
            "First_rowKeywordSegment" => Some(&FIRST_ROW_KEYWORD_SEGMENT),
            "View_metadataKeywordSegment" => Some(&VIEW_METADATA_KEYWORD_SEGMENT),
            "AtomicKeywordSegment" => Some(&ATOMIC_KEYWORD_SEGMENT),
            "Filetable_collate_filenameKeywordSegment" => Some(&FILETABLE_COLLATE_FILENAME_KEYWORD_SEGMENT),
            "DayKeywordSegment" => Some(&DAY_KEYWORD_SEGMENT),
            "Abort_after_waitKeywordSegment" => Some(&ABORT_AFTER_WAIT_KEYWORD_SEGMENT),
            "Remote_data_archiveKeywordSegment" => Some(&REMOTE_DATA_ARCHIVE_KEYWORD_SEGMENT),
            "TiesKeywordSegment" => Some(&TIES_KEYWORD_SEGMENT),
            "Data_compressionKeywordSegment" => Some(&DATA_COMPRESSION_KEYWORD_SEGMENT),
            "Context_infoKeywordSegment" => Some(&CONTEXT_INFO_KEYWORD_SEGMENT),
            "ManualKeywordSegment" => Some(&MANUAL_KEYWORD_SEGMENT),
            "ForcedKeywordSegment" => Some(&FORCED_KEYWORD_SEGMENT),
            "Ansi_warningsKeywordSegment" => Some(&ANSI_WARNINGS_KEYWORD_SEGMENT),
            "EncryptionKeywordSegment" => Some(&ENCRYPTION_KEYWORD_SEGMENT),
            "PropertyKeywordSegment" => Some(&PROPERTY_KEYWORD_SEGMENT),
            "ReadpastKeywordSegment" => Some(&READPAST_KEYWORD_SEGMENT),
            "DataKeywordSegment" => Some(&DATA_KEYWORD_SEGMENT),
            "Allow_row_locksKeywordSegment" => Some(&ALLOW_ROW_LOCKS_KEYWORD_SEGMENT),
            "Percentile_contKeywordSegment" => Some(&PERCENTILE_CONT_KEYWORD_SEGMENT),
            "NoKeywordSegment" => Some(&NO_KEYWORD_SEGMENT),
            "XmlattributesKeywordSegment" => Some(&XMLATTRIBUTES_KEYWORD_SEGMENT),
            "EncodingKeywordSegment" => Some(&ENCODING_KEYWORD_SEGMENT),
            "File_formatKeywordSegment" => Some(&FILE_FORMAT_KEYWORD_SEGMENT),
            "WhileKeywordSegment" => Some(&WHILE_KEYWORD_SEGMENT),
            "GeneratedKeywordSegment" => Some(&GENERATED_KEYWORD_SEGMENT),
            "Ledger_viewKeywordSegment" => Some(&LEDGER_VIEW_KEYWORD_SEGMENT),
            "Nested_triggersKeywordSegment" => Some(&NESTED_TRIGGERS_KEYWORD_SEGMENT),
            "Error_broker_conversationsKeywordSegment" => Some(&ERROR_BROKER_CONVERSATIONS_KEYWORD_SEGMENT),
            "Format_optionsKeywordSegment" => Some(&FORMAT_OPTIONS_KEYWORD_SEGMENT),
            "ReorganizeKeywordSegment" => Some(&REORGANIZE_KEYWORD_SEGMENT),
            "Connection_optionsKeywordSegment" => Some(&CONNECTION_OPTIONS_KEYWORD_SEGMENT),
            "MonthKeywordSegment" => Some(&MONTH_KEYWORD_SEGMENT),
            "XmlKeywordSegment" => Some(&XML_KEYWORD_SEGMENT),
            "InlineKeywordSegment" => Some(&INLINE_KEYWORD_SEGMENT),
            "SecondaryKeywordSegment" => Some(&SECONDARY_KEYWORD_SEGMENT),
            "Operation_type_column_nameKeywordSegment" => Some(&OPERATION_TYPE_COLUMN_NAME_KEYWORD_SEGMENT),
            "RawKeywordSegment" => Some(&RAW_KEYWORD_SEGMENT),
            "RepeatablereadKeywordSegment" => Some(&REPEATABLEREAD_KEYWORD_SEGMENT),
            "RobustKeywordSegment" => Some(&ROBUST_KEYWORD_SEGMENT),
            "Without_array_wrapperKeywordSegment" => Some(&WITHOUT_ARRAY_WRAPPER_KEYWORD_SEGMENT),
            "ArithignoreKeywordSegment" => Some(&ARITHIGNORE_KEYWORD_SEGMENT),
            "CacheKeywordSegment" => Some(&CACHE_KEYWORD_SEGMENT),
            "FmtonlyKeywordSegment" => Some(&FMTONLY_KEYWORD_SEGMENT),
            "Max_durationKeywordSegment" => Some(&MAX_DURATION_KEYWORD_SEGMENT),
            "Showplan_allKeywordSegment" => Some(&SHOWPLAN_ALL_KEYWORD_SEGMENT),
            "Data_sourceKeywordSegment" => Some(&DATA_SOURCE_KEYWORD_SEGMENT),
            "WorkKeywordSegment" => Some(&WORK_KEYWORD_SEGMENT),
            "FieldterminatorKeywordSegment" => Some(&FIELDTERMINATOR_KEYWORD_SEGMENT),
            "Lob_compactionKeywordSegment" => Some(&LOB_COMPACTION_KEYWORD_SEGMENT),
            "XmlpiKeywordSegment" => Some(&XMLPI_KEYWORD_SEGMENT),
            "Regr_sxxKeywordSegment" => Some(&REGR_SXX_KEYWORD_SEGMENT),
            "OrcKeywordSegment" => Some(&ORC_KEYWORD_SEGMENT),
            "IsolationKeywordSegment" => Some(&ISOLATION_KEYWORD_SEGMENT),
            "Regr_interceptKeywordSegment" => Some(&REGR_INTERCEPT_KEYWORD_SEGMENT),
            "File_typeKeywordSegment" => Some(&FILE_TYPE_KEYWORD_SEGMENT),
            "UsedKeywordSegment" => Some(&USED_KEYWORD_SEGMENT),
            "CallerKeywordSegment" => Some(&CALLER_KEYWORD_SEGMENT),
            "Filter_predicateKeywordSegment" => Some(&FILTER_PREDICATE_KEYWORD_SEGMENT),
            "LogKeywordSegment" => Some(&LOG_KEYWORD_SEGMENT),
            "Compression_delayKeywordSegment" => Some(&COMPRESSION_DELAY_KEYWORD_SEGMENT),
            "ElementKeywordSegment" => Some(&ELEMENT_KEYWORD_SEGMENT),
            "FailoverKeywordSegment" => Some(&FAILOVER_KEYWORD_SEGMENT),
            "PartitionsKeywordSegment" => Some(&PARTITIONS_KEYWORD_SEGMENT),
            "KeepdefaultsKeywordSegment" => Some(&KEEPDEFAULTS_KEYWORD_SEGMENT),
            "SplitKeywordSegment" => Some(&SPLIT_KEYWORD_SEGMENT),
            "Spatial_window_max_cellsKeywordSegment" => Some(&SPATIAL_WINDOW_MAX_CELLS_KEYWORD_SEGMENT),
            "Concat_null_yields_nullKeywordSegment" => Some(&CONCAT_NULL_YIELDS_NULL_KEYWORD_SEGMENT),
            "MaxvalueKeywordSegment" => Some(&MAXVALUE_KEYWORD_SEGMENT),
            "ResumableKeywordSegment" => Some(&RESUMABLE_KEYWORD_SEGMENT),
            "ConcatKeywordSegment" => Some(&CONCAT_KEYWORD_SEGMENT),
            "Regr_avgxKeywordSegment" => Some(&REGR_AVGX_KEYWORD_SEGMENT),
            "Regr_sxyKeywordSegment" => Some(&REGR_SXY_KEYWORD_SEGMENT),
            "AtKeywordSegment" => Some(&AT_KEYWORD_SEGMENT),
            "RowsKeywordSegment" => Some(&ROWS_KEYWORD_SEGMENT),
            "Textimage_onKeywordSegment" => Some(&TEXTIMAGE_ON_KEYWORD_SEGMENT),
            "RebuildKeywordSegment" => Some(&REBUILD_KEYWORD_SEGMENT),
            "Remote_proc_transactionsKeywordSegment" => Some(&REMOTE_PROC_TRANSACTIONS_KEYWORD_SEGMENT),
            "NolockKeywordSegment" => Some(&NOLOCK_KEYWORD_SEGMENT),
            "XmlcastKeywordSegment" => Some(&XMLCAST_KEYWORD_SEGMENT),
            "CatchKeywordSegment" => Some(&CATCH_KEYWORD_SEGMENT),
            "MaxsizeKeywordSegment" => Some(&MAXSIZE_KEYWORD_SEGMENT),
            "SelfKeywordSegment" => Some(&SELF_KEYWORD_SEGMENT),
            "Change_trackingKeywordSegment" => Some(&CHANGE_TRACKING_KEYWORD_SEGMENT),
            "ResultKeywordSegment" => Some(&RESULT_KEYWORD_SEGMENT),
            "ColumnstoreKeywordSegment" => Some(&COLUMNSTORE_KEYWORD_SEGMENT),
            "RespectKeywordSegment" => Some(&RESPECT_KEYWORD_SEGMENT),
            "NoneKeywordSegment" => Some(&NONE_KEYWORD_SEGMENT),
            "TakeKeywordSegment" => Some(&TAKE_KEYWORD_SEGMENT),
            "XmlbinaryKeywordSegment" => Some(&XMLBINARY_KEYWORD_SEGMENT),
            "UnlimitedKeywordSegment" => Some(&UNLIMITED_KEYWORD_SEGMENT),
            "Encryption_typeKeywordSegment" => Some(&ENCRYPTION_TYPE_KEYWORD_SEGMENT),
            "JsonKeywordSegment" => Some(&JSON_KEYWORD_SEGMENT),
            "Auto_shrinkKeywordSegment" => Some(&AUTO_SHRINK_KEYWORD_SEGMENT),
            "Legacy_cardinality_estimationKeywordSegment" => Some(&LEGACY_CARDINALITY_ESTIMATION_KEYWORD_SEGMENT),
            "XmlcommentKeywordSegment" => Some(&XMLCOMMENT_KEYWORD_SEGMENT),
            "DatafiletypeKeywordSegment" => Some(&DATAFILETYPE_KEYWORD_SEGMENT),
            "RowlockKeywordSegment" => Some(&ROWLOCK_KEYWORD_SEGMENT),
            "Max_grant_percentKeywordSegment" => Some(&MAX_GRANT_PERCENT_KEYWORD_SEGMENT),
            "Xact_abortKeywordSegment" => Some(&XACT_ABORT_KEYWORD_SEGMENT),
            "AttachKeywordSegment" => Some(&ATTACH_KEYWORD_SEGMENT),
            "Auto_create_statisticsKeywordSegment" => Some(&AUTO_CREATE_STATISTICS_KEYWORD_SEGMENT),
            "CompressionKeywordSegment" => Some(&COMPRESSION_KEYWORD_SEGMENT),
            "ActionKeywordSegment" => Some(&ACTION_KEYWORD_SEGMENT),
            "Parser_versionKeywordSegment" => Some(&PARSER_VERSION_KEYWORD_SEGMENT),
            "TryKeywordSegment" => Some(&TRY_KEYWORD_SEGMENT),
            "TargetKeywordSegment" => Some(&TARGET_KEYWORD_SEGMENT),
            "ElementsKeywordSegment" => Some(&ELEMENTS_KEYWORD_SEGMENT),
            "IncrementKeywordSegment" => Some(&INCREMENT_KEYWORD_SEGMENT),
            "TimestampKeywordSegment" => Some(&TIMESTAMP_KEYWORD_SEGMENT),
            "YearKeywordSegment" => Some(&YEAR_KEYWORD_SEGMENT),
            "String_aggKeywordSegment" => Some(&STRING_AGG_KEYWORD_SEGMENT),
            "NowaitKeywordSegment" => Some(&NOWAIT_KEYWORD_SEGMENT),
            "Rows_per_batchKeywordSegment" => Some(&ROWS_PER_BATCH_KEYWORD_SEGMENT),
            "PageKeywordSegment" => Some(&PAGE_KEYWORD_SEGMENT),
            "RowKeywordSegment" => Some(&ROW_KEYWORD_SEGMENT),
            "TimeKeywordSegment" => Some(&TIME_KEYWORD_SEGMENT),
            "UsingKeywordSegment" => Some(&USING_KEYWORD_SEGMENT),
            "AbortKeywordSegment" => Some(&ABORT_KEYWORD_SEGMENT),
            "XmldataKeywordSegment" => Some(&XMLDATA_KEYWORD_SEGMENT),
            "Accelerated_database_recoveryKeywordSegment" => Some(&ACCELERATED_DATABASE_RECOVERY_KEYWORD_SEGMENT),
            "ForceKeywordSegment" => Some(&FORCE_KEYWORD_SEGMENT),
            "Fire_triggersKeywordSegment" => Some(&FIRE_TRIGGERS_KEYWORD_SEGMENT),
            "Drop_existingKeywordSegment" => Some(&DROP_EXISTING_KEYWORD_SEGMENT),
            "StartKeywordSegment" => Some(&START_KEYWORD_SEGMENT),
            "No_performance_spoolKeywordSegment" => Some(&NO_PERFORMANCE_SPOOL_KEYWORD_SEGMENT),
            "NoexecKeywordSegment" => Some(&NOEXEC_KEYWORD_SEGMENT),
            "RankKeywordSegment" => Some(&RANK_KEYWORD_SEGMENT),
            "RangeKeywordSegment" => Some(&RANGE_KEYWORD_SEGMENT),
            "LastrowKeywordSegment" => Some(&LASTROW_KEYWORD_SEGMENT),
            "Columnstore_archiveKeywordSegment" => Some(&COLUMNSTORE_ARCHIVE_KEYWORD_SEGMENT),
            "Compatibility_levelKeywordSegment" => Some(&COMPATIBILITY_LEVEL_KEYWORD_SEGMENT),
            "CredentialKeywordSegment" => Some(&CREDENTIAL_KEYWORD_SEGMENT),
            "XmlschemaKeywordSegment" => Some(&XMLSCHEMA_KEYWORD_SEGMENT),
            "ContainmentKeywordSegment" => Some(&CONTAINMENT_KEYWORD_SEGMENT),
            "Sort_in_tempdbKeywordSegment" => Some(&SORT_IN_TEMPDB_KEYWORD_SEGMENT),
            "ProviderKeywordSegment" => Some(&PROVIDER_KEYWORD_SEGMENT),
            "LevelKeywordSegment" => Some(&LEVEL_KEYWORD_SEGMENT),
            "XmltableKeywordSegment" => Some(&XMLTABLE_KEYWORD_SEGMENT),
            "MbKeywordSegment" => Some(&MB_KEYWORD_SEGMENT),
            "UndefinedKeywordSegment" => Some(&UNDEFINED_KEYWORD_SEGMENT),
            "AfterKeywordSegment" => Some(&AFTER_KEYWORD_SEGMENT),
            "Default_databaseKeywordSegment" => Some(&DEFAULT_DATABASE_KEYWORD_SEGMENT),
            "GeozoneKeywordSegment" => Some(&GEOZONE_KEYWORD_SEGMENT),
            "NameKeywordSegment" => Some(&NAME_KEYWORD_SEGMENT),
            "System_timeKeywordSegment" => Some(&SYSTEM_TIME_KEYWORD_SEGMENT),
            "PausedKeywordSegment" => Some(&PAUSED_KEYWORD_SEGMENT),
            "DateKeywordSegment" => Some(&DATE_KEYWORD_SEGMENT),
            "OpenqueryKeywordSegment" => Some(&OPENQUERY_KEYWORD_SEGMENT),
            "SeterrorKeywordSegment" => Some(&SETERROR_KEYWORD_SEGMENT),
            "Migration_stateKeywordSegment" => Some(&MIGRATION_STATE_KEYWORD_SEGMENT),
            "Db_chainingKeywordSegment" => Some(&DB_CHAINING_KEYWORD_SEGMENT),
            "FilegroupKeywordSegment" => Some(&FILEGROUP_KEYWORD_SEGMENT),
            "TablockxKeywordSegment" => Some(&TABLOCKX_KEYWORD_SEGMENT),
            "NtileKeywordSegment" => Some(&NTILE_KEYWORD_SEGMENT),
            "DelimitedtextKeywordSegment" => Some(&DELIMITEDTEXT_KEYWORD_SEGMENT),
            "OnlineKeywordSegment" => Some(&ONLINE_KEYWORD_SEGMENT),
            "Ignore_nonclustered_columnstore_indexKeywordSegment" => Some(&IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX_KEYWORD_SEGMENT),
            "NullsKeywordSegment" => Some(&NULLS_KEYWORD_SEGMENT),
            "PasswordKeywordSegment" => Some(&PASSWORD_KEYWORD_SEGMENT),
            "PercentageKeywordSegment" => Some(&PERCENTAGE_KEYWORD_SEGMENT),
            "Allow_encrypted_value_modificationsKeywordSegment" => Some(&ALLOW_ENCRYPTED_VALUE_MODIFICATIONS_KEYWORD_SEGMENT),
            "PushdownKeywordSegment" => Some(&PUSHDOWN_KEYWORD_SEGMENT),
            "RowterminatorKeywordSegment" => Some(&ROWTERMINATOR_KEYWORD_SEGMENT),
            "SidKeywordSegment" => Some(&SID_KEYWORD_SEGMENT),
            "ExplainKeywordSegment" => Some(&EXPLAIN_KEYWORD_SEGMENT),
            "Xml_compressionKeywordSegment" => Some(&XML_COMPRESSION_KEYWORD_SEGMENT),
            "ExternalpushdownKeywordSegment" => Some(&EXTERNALPUSHDOWN_KEYWORD_SEGMENT),
            "LedgerKeywordSegment" => Some(&LEDGER_KEYWORD_SEGMENT),
            "GeoKeywordSegment" => Some(&GEO_KEYWORD_SEGMENT),
            "FormatfileKeywordSegment" => Some(&FORMATFILE_KEYWORD_SEGMENT),
            "Transaction_idKeywordSegment" => Some(&TRANSACTION_ID_KEYWORD_SEGMENT),
            "SetvarKeywordSegment" => Some(&SETVAR_KEYWORD_SEGMENT),
            "ContinueKeywordSegment" => Some(&CONTINUE_KEYWORD_SEGMENT),
            "SizeKeywordSegment" => Some(&SIZE_KEYWORD_SEGMENT),
            "OverrideKeywordSegment" => Some(&OVERRIDE_KEYWORD_SEGMENT),
            "AsymmetricKeywordSegment" => Some(&ASYMMETRIC_KEYWORD_SEGMENT),
            "InputKeywordSegment" => Some(&INPUT_KEYWORD_SEGMENT),
            "CalledKeywordSegment" => Some(&CALLED_KEYWORD_SEGMENT),
            "Operation_type_desc_column_nameKeywordSegment" => Some(&OPERATION_TYPE_DESC_COLUMN_NAME_KEYWORD_SEGMENT),
            "KeepKeywordSegment" => Some(&KEEP_KEYWORD_SEGMENT),
            "XmlparseKeywordSegment" => Some(&XMLPARSE_KEYWORD_SEGMENT),
            "SearchKeywordSegment" => Some(&SEARCH_KEYWORD_SEGMENT),
            "WaitforKeywordSegment" => Some(&WAITFOR_KEYWORD_SEGMENT),
            "ReturnsKeywordSegment" => Some(&RETURNS_KEYWORD_SEGMENT),
            "Compress_all_row_groupsKeywordSegment" => Some(&COMPRESS_ALL_ROW_GROUPS_KEYWORD_SEGMENT),
            "SourceKeywordSegment" => Some(&SOURCE_KEYWORD_SEGMENT),
            "TypeKeywordSegment" => Some(&TYPE_KEYWORD_SEGMENT),
            "NoexpandKeywordSegment" => Some(&NOEXPAND_KEYWORD_SEGMENT),
            "ReaduncommittedKeywordSegment" => Some(&READUNCOMMITTED_KEYWORD_SEGMENT),
            "AlgorithmKeywordSegment" => Some(&ALGORITHM_KEYWORD_SEGMENT),
            "SequenceKeywordSegment" => Some(&SEQUENCE_KEYWORD_SEGMENT),
            "ScaleoutexecutionKeywordSegment" => Some(&SCALEOUTEXECUTION_KEYWORD_SEGMENT),
            "LoadKeywordSegment" => Some(&LOAD_KEYWORD_SEGMENT),
            "PauseKeywordSegment" => Some(&PAUSE_KEYWORD_SEGMENT),
            "Reject_typeKeywordSegment" => Some(&REJECT_TYPE_KEYWORD_SEGMENT),
            "ObjectKeywordSegment" => Some(&OBJECT_KEYWORD_SEGMENT),
            "MaxKeywordSegment" => Some(&MAX_KEYWORD_SEGMENT),
            "SecurityauditKeywordSegment" => Some(&SECURITYAUDIT_KEYWORD_SEGMENT),
            "HintKeywordSegment" => Some(&HINT_KEYWORD_SEGMENT),
            "RenameKeywordSegment" => Some(&RENAME_KEYWORD_SEGMENT),
            "Database_defaultKeywordSegment" => Some(&DATABASE_DEFAULT_KEYWORD_SEGMENT),
            "Json_objectKeywordSegment" => Some(&JSON_OBJECT_KEYWORD_SEGMENT),
            "CopyKeywordSegment" => Some(&COPY_KEYWORD_SEGMENT),
            "Kilobytes_per_batchKeywordSegment" => Some(&KILOBYTES_PER_BATCH_KEYWORD_SEGMENT),
            "RegenerateKeywordSegment" => Some(&REGENERATE_KEYWORD_SEGMENT),
            "LoopKeywordSegment" => Some(&LOOP_KEYWORD_SEGMENT),
            "ReadcommittedlockKeywordSegment" => Some(&READCOMMITTEDLOCK_KEYWORD_SEGMENT),
            "TrustworthyKeywordSegment" => Some(&TRUSTWORTHY_KEYWORD_SEGMENT),
            "DumpKeywordSegment" => Some(&DUMP_KEYWORD_SEGMENT),
            "SparseKeywordSegment" => Some(&SPARSE_KEYWORD_SEGMENT),
            "Check_policyKeywordSegment" => Some(&CHECK_POLICY_KEYWORD_SEGMENT),
            "History_tableKeywordSegment" => Some(&HISTORY_TABLE_KEYWORD_SEGMENT),
            "InsteadKeywordSegment" => Some(&INSTEAD_KEYWORD_SEGMENT),
            "StateKeywordSegment" => Some(&STATE_KEYWORD_SEGMENT),
            "ModifyKeywordSegment" => Some(&MODIFY_KEYWORD_SEGMENT),
            "UpdlockKeywordSegment" => Some(&UPDLOCK_KEYWORD_SEGMENT),
            "CommittedKeywordSegment" => Some(&COMMITTED_KEYWORD_SEGMENT),
            "PrecedingKeywordSegment" => Some(&PRECEDING_KEYWORD_SEGMENT),
            "Backup_storage_redundancyKeywordSegment" => Some(&BACKUP_STORAGE_REDUNDANCY_KEYWORD_SEGMENT),
            "PaglockKeywordSegment" => Some(&PAGLOCK_KEYWORD_SEGMENT),
            "ParametersKeywordSegment" => Some(&PARAMETERS_KEYWORD_SEGMENT),
            "UnknownKeywordSegment" => Some(&UNKNOWN_KEYWORD_SEGMENT),
            "Perform_cutoverKeywordSegment" => Some(&PERFORM_CUTOVER_KEYWORD_SEGMENT),
            "Default_fulltext_languageKeywordSegment" => Some(&DEFAULT_FULLTEXT_LANGUAGE_KEYWORD_SEGMENT),
            "ContainedKeywordSegment" => Some(&CONTAINED_KEYWORD_SEGMENT),
            "Ansi_null_dflt_onKeywordSegment" => Some(&ANSI_NULL_DFLT_ON_KEYWORD_SEGMENT),
            "StoplistKeywordSegment" => Some(&STOPLIST_KEYWORD_SEGMENT),
            "OffsetKeywordSegment" => Some(&OFFSET_KEYWORD_SEGMENT),
            "KeepidentityKeywordSegment" => Some(&KEEPIDENTITY_KEYWORD_SEGMENT),
            "ScopedKeywordSegment" => Some(&SCOPED_KEYWORD_SEGMENT),
            "UncommittedKeywordSegment" => Some(&UNCOMMITTED_KEYWORD_SEGMENT),
            "FirstKeywordSegment" => Some(&FIRST_KEYWORD_SEGMENT),
            "DatasourceKeywordSegment" => Some(&DATASOURCE_KEYWORD_SEGMENT),
            "InfiniteKeywordSegment" => Some(&INFINITE_KEYWORD_SEGMENT),
            "Persistent_log_bufferKeywordSegment" => Some(&PERSISTENT_LOG_BUFFER_KEYWORD_SEGMENT),
            "LabelKeywordSegment" => Some(&LABEL_KEYWORD_SEGMENT),
            "Single_clobKeywordSegment" => Some(&SINGLE_CLOB_KEYWORD_SEGMENT),
            "XmliterateKeywordSegment" => Some(&XMLITERATE_KEYWORD_SEGMENT),
            "SystemKeywordSegment" => Some(&SYSTEM_KEYWORD_SEGMENT),
            "KbKeywordSegment" => Some(&KB_KEYWORD_SEGMENT),
            "MaxerrorsKeywordSegment" => Some(&MAXERRORS_KEYWORD_SEGMENT),
            "SerializableKeywordSegment" => Some(&SERIALIZABLE_KEYWORD_SEGMENT),
            "Allow_page_locksKeywordSegment" => Some(&ALLOW_PAGE_LOCKS_KEYWORD_SEGMENT),
            "BreakKeywordSegment" => Some(&BREAK_KEYWORD_SEGMENT),
            "DistributionKeywordSegment" => Some(&DISTRIBUTION_KEYWORD_SEGMENT),
            "DelayKeywordSegment" => Some(&DELAY_KEYWORD_SEGMENT),
            "Formatfile_data_sourceKeywordSegment" => Some(&FORMATFILE_DATA_SOURCE_KEYWORD_SEGMENT),
            "AutoKeywordSegment" => Some(&AUTO_KEYWORD_SEGMENT),
            "Allow_connectionsKeywordSegment" => Some(&ALLOW_CONNECTIONS_KEYWORD_SEGMENT),
            "Reject_valueKeywordSegment" => Some(&REJECT_VALUE_KEYWORD_SEGMENT),
            "PopulationKeywordSegment" => Some(&POPULATION_KEYWORD_SEGMENT),
            "DeterministicKeywordSegment" => Some(&DETERMINISTIC_KEYWORD_SEGMENT),
            "MatchedKeywordSegment" => Some(&MATCHED_KEYWORD_SEGMENT),
            "IntervalKeywordSegment" => Some(&INTERVAL_KEYWORD_SEGMENT),
            "Statistical_semanticsKeywordSegment" => Some(&STATISTICAL_SEMANTICS_KEYWORD_SEGMENT),
            "SecretKeywordSegment" => Some(&SECRET_KEYWORD_SEGMENT),
            "Statistics_norecomputeKeywordSegment" => Some(&STATISTICS_NORECOMPUTE_KEYWORD_SEGMENT),
            "Enable_brokerKeywordSegment" => Some(&ENABLE_BROKER_KEYWORD_SEGMENT),
            "RandomizedKeywordSegment" => Some(&RANDOMIZED_KEYWORD_SEGMENT),
            "TbKeywordSegment" => Some(&TB_KEYWORD_SEGMENT),
            "NextKeywordSegment" => Some(&NEXT_KEYWORD_SEGMENT),
            "AllowedKeywordSegment" => Some(&ALLOWED_KEYWORD_SEGMENT),
            "Attach_rebuild_logKeywordSegment" => Some(&ATTACH_REBUILD_LOG_KEYWORD_SEGMENT),
            "PathKeywordSegment" => Some(&PATH_KEYWORD_SEGMENT),
            "MonthsKeywordSegment" => Some(&MONTHS_KEYWORD_SEGMENT),
            "Serde_methodKeywordSegment" => Some(&SERDE_METHOD_KEYWORD_SEGMENT),
            "Transaction_id_column_nameKeywordSegment" => Some(&TRANSACTION_ID_COLUMN_NAME_KEYWORD_SEGMENT),
            "Numeric_roundabortKeywordSegment" => Some(&NUMERIC_ROUNDABORT_KEYWORD_SEGMENT),
            "WeeksKeywordSegment" => Some(&WEEKS_KEYWORD_SEGMENT),
            "Dense_rankKeywordSegment" => Some(&DENSE_RANK_KEYWORD_SEGMENT),
            "SchemeKeywordSegment" => Some(&SCHEME_KEYWORD_SEGMENT),
            "MaxdopKeywordSegment" => Some(&MAXDOP_KEYWORD_SEGMENT),
            "XmlelementKeywordSegment" => Some(&XMLELEMENT_KEYWORD_SEGMENT),
            "AbsentKeywordSegment" => Some(&ABSENT_KEYWORD_SEGMENT),
            "ReadcommittedKeywordSegment" => Some(&READCOMMITTED_KEYWORD_SEGMENT),
            "Quoted_identifierKeywordSegment" => Some(&QUOTED_IDENTIFIER_KEYWORD_SEGMENT),
            "XmlnamespacesKeywordSegment" => Some(&XMLNAMESPACES_KEYWORD_SEGMENT),
            "NewnameKeywordSegment" => Some(&NEWNAME_KEYWORD_SEGMENT),
            "ErrorfileKeywordSegment" => Some(&ERRORFILE_KEYWORD_SEGMENT),
            "Auto_closeKeywordSegment" => Some(&AUTO_CLOSE_KEYWORD_SEGMENT),
            "OptimizeKeywordSegment" => Some(&OPTIMIZE_KEYWORD_SEGMENT),
            "MaxrecursionKeywordSegment" => Some(&MAXRECURSION_KEYWORD_SEGMENT),
            "ExpandKeywordSegment" => Some(&EXPAND_KEYWORD_SEGMENT),
            "Cursor_close_on_commitKeywordSegment" => Some(&CURSOR_CLOSE_ON_COMMIT_KEYWORD_SEGMENT),
            "DaysKeywordSegment" => Some(&DAYS_KEYWORD_SEGMENT),
            "BinaryKeywordSegment" => Some(&BINARY_KEYWORD_SEGMENT),
            "BlockKeywordSegment" => Some(&BLOCK_KEYWORD_SEGMENT),
            "String_delimiterKeywordSegment" => Some(&STRING_DELIMITER_KEYWORD_SEGMENT),
            "ParameterKeywordSegment" => Some(&PARAMETER_KEYWORD_SEGMENT),
            "Deadlock_priorityKeywordSegment" => Some(&DEADLOCK_PRIORITY_KEYWORD_SEGMENT),
            "Catalog_collationKeywordSegment" => Some(&CATALOG_COLLATION_KEYWORD_SEGMENT),
            "KeepnullsKeywordSegment" => Some(&KEEPNULLS_KEYWORD_SEGMENT),
            "Showplan_xmlKeywordSegment" => Some(&SHOWPLAN_XML_KEYWORD_SEGMENT),
            "Ansi_paddingKeywordSegment" => Some(&ANSI_PADDING_KEYWORD_SEGMENT),
            "Optimize_for_sequential_keyKeywordSegment" => Some(&OPTIMIZE_FOR_SEQUENTIAL_KEY_KEYWORD_SEGMENT),
            "Sequence_number_column_nameKeywordSegment" => Some(&SEQUENCE_NUMBER_COLUMN_NAME_KEYWORD_SEGMENT),
            "WithoutKeywordSegment" => Some(&WITHOUT_KEYWORD_SEGMENT),
            "Result_set_cachingKeywordSegment" => Some(&RESULT_SET_CACHING_KEYWORD_SEGMENT),
            "AlwaysKeywordSegment" => Some(&ALWAYS_KEYWORD_SEGMENT),
            "NocountKeywordSegment" => Some(&NOCOUNT_KEYWORD_SEGMENT),
            "BeforeKeywordSegment" => Some(&BEFORE_KEYWORD_SEGMENT),
            "ReplaceKeywordSegment" => Some(&REPLACE_KEYWORD_SEGMENT),
            "Append_onlyKeywordSegment" => Some(&APPEND_ONLY_KEYWORD_SEGMENT),
            "Auto_update_statisticsKeywordSegment" => Some(&AUTO_UPDATE_STATISTICS_KEYWORD_SEGMENT),
            "Date_formatKeywordSegment" => Some(&DATE_FORMAT_KEYWORD_SEGMENT),
            "DateformatKeywordSegment" => Some(&DATEFORMAT_KEYWORD_SEGMENT),
            "Errorfile_credentialKeywordSegment" => Some(&ERRORFILE_CREDENTIAL_KEYWORD_SEGMENT),
            "System_versioningKeywordSegment" => Some(&SYSTEM_VERSIONING_KEYWORD_SEGMENT),
            "Schema_and_dataKeywordSegment" => Some(&SCHEMA_AND_DATA_KEYWORD_SEGMENT),
            "ServiceKeywordSegment" => Some(&SERVICE_KEYWORD_SEGMENT),
            "OwnerKeywordSegment" => Some(&OWNER_KEYWORD_SEGMENT),
            "RollupKeywordSegment" => Some(&ROLLUP_KEYWORD_SEGMENT),
            "XlockKeywordSegment" => Some(&XLOCK_KEYWORD_SEGMENT),
            "Ansi_defaultsKeywordSegment" => Some(&ANSI_DEFAULTS_KEYWORD_SEGMENT),
            "Two_digit_year_cutoffKeywordSegment" => Some(&TWO_DIGIT_YEAR_CUTOFF_KEYWORD_SEGMENT),
            "DisableKeywordSegment" => Some(&DISABLE_KEYWORD_SEGMENT),
            "History_retention_periodKeywordSegment" => Some(&HISTORY_RETENTION_PERIOD_KEYWORD_SEGMENT),
            "RecompileKeywordSegment" => Some(&RECOMPILE_KEYWORD_SEGMENT),
            "RootKeywordSegment" => Some(&ROOT_KEYWORD_SEGMENT),
            "Data_deletionKeywordSegment" => Some(&DATA_DELETION_KEYWORD_SEGMENT),
            "Filetable_primary_key_constraint_nameKeywordSegment" => Some(&FILETABLE_PRIMARY_KEY_CONSTRAINT_NAME_KEYWORD_SEGMENT),
            "RecursiveKeywordSegment" => Some(&RECURSIVE_KEYWORD_SEGMENT),
            "Schema_onlyKeywordSegment" => Some(&SCHEMA_ONLY_KEYWORD_SEGMENT),
            "KeepfixedKeywordSegment" => Some(&KEEPFIXED_KEYWORD_SEGMENT),
            "IncludeKeywordSegment" => Some(&INCLUDE_KEYWORD_SEGMENT),
            "Filter_columnKeywordSegment" => Some(&FILTER_COLUMN_KEYWORD_SEGMENT),
            "Ignore_constraintsKeywordSegment" => Some(&IGNORE_CONSTRAINTS_KEYWORD_SEGMENT),
            "ParseonlyKeywordSegment" => Some(&PARSEONLY_KEYWORD_SEGMENT),
            "FieldquoteKeywordSegment" => Some(&FIELDQUOTE_KEYWORD_SEGMENT),
            "Lock_timeoutKeywordSegment" => Some(&LOCK_TIMEOUT_KEYWORD_SEGMENT),
            "RcfileKeywordSegment" => Some(&RCFILE_KEYWORD_SEGMENT),
            "RemoveKeywordSegment" => Some(&REMOVE_KEYWORD_SEGMENT),
            "XsinilKeywordSegment" => Some(&XSINIL_KEYWORD_SEGMENT),
            "ValueKeywordSegment" => Some(&VALUE_KEYWORD_SEGMENT),
            "Fips_flaggerKeywordSegment" => Some(&FIPS_FLAGGER_KEYWORD_SEGMENT),
            "XmltextKeywordSegment" => Some(&XMLTEXT_KEYWORD_SEGMENT),
            "ParquetKeywordSegment" => Some(&PARQUET_KEYWORD_SEGMENT),
            "RoleKeywordSegment" => Some(&ROLE_KEYWORD_SEGMENT),
            "DurabilityKeywordSegment" => Some(&DURABILITY_KEYWORD_SEGMENT),
            "SwitchKeywordSegment" => Some(&SWITCH_KEYWORD_SEGMENT),
            "NodeKeywordSegment" => Some(&NODE_KEYWORD_SEGMENT),
            "Auto_update_statistics_asyncKeywordSegment" => Some(&AUTO_UPDATE_STATISTICS_ASYNC_KEYWORD_SEGMENT),
            "Memory_optimizedKeywordSegment" => Some(&MEMORY_OPTIMIZED_KEYWORD_SEGMENT),
            "ZoneKeywordSegment" => Some(&ZONE_KEYWORD_SEGMENT),
            "Statistics_incrementalKeywordSegment" => Some(&STATISTICS_INCREMENTAL_KEYWORD_SEGMENT),
            "Field_terminatorKeywordSegment" => Some(&FIELD_TERMINATOR_KEYWORD_SEGMENT),
            "FilegrowthKeywordSegment" => Some(&FILEGROWTH_KEYWORD_SEGMENT),
            "ReceiveKeywordSegment" => Some(&RECEIVE_KEYWORD_SEGMENT),
            "ExplicitKeywordSegment" => Some(&EXPLICIT_KEYWORD_SEGMENT),
            "IgnoreKeywordSegment" => Some(&IGNORE_KEYWORD_SEGMENT),
            "Read_writeKeywordSegment" => Some(&READ_WRITE_KEYWORD_SEGMENT),
            "XmlexistsKeywordSegment" => Some(&XMLEXISTS_KEYWORD_SEGMENT),
            "Showplan_textKeywordSegment" => Some(&SHOWPLAN_TEXT_KEYWORD_SEGMENT),
            "Json_arrayKeywordSegment" => Some(&JSON_ARRAY_KEYWORD_SEGMENT),
            "Single_blobKeywordSegment" => Some(&SINGLE_BLOB_KEYWORD_SEGMENT),
            "Filetable_fullpath_unique_constraint_nameKeywordSegment" => Some(&FILETABLE_FULLPATH_UNIQUE_CONSTRAINT_NAME_KEYWORD_SEGMENT),
            "Filetable_streamid_unique_constraint_nameKeywordSegment" => Some(&FILETABLE_STREAMID_UNIQUE_CONSTRAINT_NAME_KEYWORD_SEGMENT),
            "Wait_at_low_priorityKeywordSegment" => Some(&WAIT_AT_LOW_PRIORITY_KEYWORD_SEGMENT),
            "Data_consistency_checkKeywordSegment" => Some(&DATA_CONSISTENCY_CHECK_KEYWORD_SEGMENT),
            "YearsKeywordSegment" => Some(&YEARS_KEYWORD_SEGMENT),
            "Percentile_discKeywordSegment" => Some(&PERCENTILE_DISC_KEYWORD_SEGMENT),
            "RowguidcolKeywordSegment" => Some(&ROWGUIDCOL_KEYWORD_SEGMENT),
            "ParameterizationKeywordSegment" => Some(&PARAMETERIZATION_KEYWORD_SEGMENT),
            "TimeoutKeywordSegment" => Some(&TIMEOUT_KEYWORD_SEGMENT),
            "LocationKeywordSegment" => Some(&LOCATION_KEYWORD_SEGMENT),
            "LastKeywordSegment" => Some(&LAST_KEYWORD_SEGMENT),
            "Non_transacted_accessKeywordSegment" => Some(&NON_TRANSACTED_ACCESS_KEYWORD_SEGMENT),
            "ResumeKeywordSegment" => Some(&RESUME_KEYWORD_SEGMENT),
            "HashKeywordSegment" => Some(&HASH_KEYWORD_SEGMENT),
            "FirstrowKeywordSegment" => Some(&FIRSTROW_KEYWORD_SEGMENT),
            "CertificateKeywordSegment" => Some(&CERTIFICATE_KEYWORD_SEGMENT),
            "ServerKeywordSegment" => Some(&SERVER_KEYWORD_SEGMENT),
            "Transform_noise_wordsKeywordSegment" => Some(&TRANSFORM_NOISE_WORDS_KEYWORD_SEGMENT),
            "EncryptedKeywordSegment" => Some(&ENCRYPTED_KEYWORD_SEGMENT),
            "Column_encryption_keyKeywordSegment" => Some(&COLUMN_ENCRYPTION_KEY_KEYWORD_SEGMENT),
            "Delayed_durabilityKeywordSegment" => Some(&DELAYED_DURABILITY_KEYWORD_SEGMENT),
            "Check_expirationKeywordSegment" => Some(&CHECK_EXPIRATION_KEYWORD_SEGMENT),
            "NormalKeywordSegment" => Some(&NORMAL_KEYWORD_SEGMENT),
            "Regr_r2KeywordSegment" => Some(&REGR_R2_KEYWORD_SEGMENT),
            "DatabaseKeywordSegment" => Some(&DATABASE_KEYWORD_SEGMENT),
            "UserKeywordSegment" => Some(&USER_KEYWORD_SEGMENT),
            "ClusteredKeywordSegment" => Some(&CLUSTERED_KEYWORD_SEGMENT),
            "DeclareKeywordSegment" => Some(&DECLARE_KEYWORD_SEGMENT),
            "PublicKeywordSegment" => Some(&PUBLIC_KEYWORD_SEGMENT),
            "Identity_insertKeywordSegment" => Some(&IDENTITY_INSERT_KEYWORD_SEGMENT),
            "Current_dateKeywordSegment" => Some(&CURRENT_DATE_KEYWORD_SEGMENT),
            "RestrictKeywordSegment" => Some(&RESTRICT_KEYWORD_SEGMENT),
            "SelectKeywordSegment" => Some(&SELECT_KEYWORD_SEGMENT),
            "SchemaKeywordSegment" => Some(&SCHEMA_KEYWORD_SEGMENT),
            "FromKeywordSegment" => Some(&FROM_KEYWORD_SEGMENT),
            "DefaultKeywordSegment" => Some(&DEFAULT_KEYWORD_SEGMENT),
            "LinenoKeywordSegment" => Some(&LINENO_KEYWORD_SEGMENT),
            "ValuesKeywordSegment" => Some(&VALUES_KEYWORD_SEGMENT),
            "Current_transform_group_for_typeKeywordSegment" => Some(&CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT),
            "Current_pathKeywordSegment" => Some(&CURRENT_PATH_KEYWORD_SEGMENT),
            "Fast_forwardKeywordSegment" => Some(&FAST_FORWARD_KEYWORD_SEGMENT),
            "FreetexttableKeywordSegment" => Some(&FREETEXTTABLE_KEYWORD_SEGMENT),
            "WhenKeywordSegment" => Some(&WHEN_KEYWORD_SEGMENT),
            "OverKeywordSegment" => Some(&OVER_KEYWORD_SEGMENT),
            "ExternalKeywordSegment" => Some(&EXTERNAL_KEYWORD_SEGMENT),
            "RightKeywordSegment" => Some(&RIGHT_KEYWORD_SEGMENT),
            "InnerKeywordSegment" => Some(&INNER_KEYWORD_SEGMENT),
            "Session_userKeywordSegment" => Some(&SESSION_USER_KEYWORD_SEGMENT),
            "CloseKeywordSegment" => Some(&CLOSE_KEYWORD_SEGMENT),
            "DropKeywordSegment" => Some(&DROP_KEYWORD_SEGMENT),
            "AnyKeywordSegment" => Some(&ANY_KEYWORD_SEGMENT),
            "ShutdownKeywordSegment" => Some(&SHUTDOWN_KEYWORD_SEGMENT),
            "OfKeywordSegment" => Some(&OF_KEYWORD_SEGMENT),
            "RevokeKeywordSegment" => Some(&REVOKE_KEYWORD_SEGMENT),
            "ExecKeywordSegment" => Some(&EXEC_KEYWORD_SEGMENT),
            "FunctionKeywordSegment" => Some(&FUNCTION_KEYWORD_SEGMENT),
            "OpenrowsetKeywordSegment" => Some(&OPENROWSET_KEYWORD_SEGMENT),
            "IndexKeywordSegment" => Some(&INDEX_KEYWORD_SEGMENT),
            "OrKeywordSegment" => Some(&OR_KEYWORD_SEGMENT),
            "ScrollKeywordSegment" => Some(&SCROLL_KEYWORD_SEGMENT),
            "TruncateKeywordSegment" => Some(&TRUNCATE_KEYWORD_SEGMENT),
            "CoalesceKeywordSegment" => Some(&COALESCE_KEYWORD_SEGMENT),
            "ExistsKeywordSegment" => Some(&EXISTS_KEYWORD_SEGMENT),
            "ConstraintKeywordSegment" => Some(&CONSTRAINT_KEYWORD_SEGMENT),
            "Scroll_locksKeywordSegment" => Some(&SCROLL_LOCKS_KEYWORD_SEGMENT),
            "DynamicKeywordSegment" => Some(&DYNAMIC_KEYWORD_SEGMENT),
            "RaiserrorKeywordSegment" => Some(&RAISERROR_KEYWORD_SEGMENT),
            "BetweenKeywordSegment" => Some(&BETWEEN_KEYWORD_SEGMENT),
            "ReadKeywordSegment" => Some(&READ_KEYWORD_SEGMENT),
            "IdentitycolKeywordSegment" => Some(&IDENTITYCOL_KEYWORD_SEGMENT),
            "RuleKeywordSegment" => Some(&RULE_KEYWORD_SEGMENT),
            "ReadtextKeywordSegment" => Some(&READTEXT_KEYWORD_SEGMENT),
            "ThenKeywordSegment" => Some(&THEN_KEYWORD_SEGMENT),
            "GoKeywordSegment" => Some(&GO_KEYWORD_SEGMENT),
            "UpdateKeywordSegment" => Some(&UPDATE_KEYWORD_SEGMENT),
            "CursorKeywordSegment" => Some(&CURSOR_KEYWORD_SEGMENT),
            "Current_default_transform_groupKeywordSegment" => Some(&CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT),
            "PlanKeywordSegment" => Some(&PLAN_KEYWORD_SEGMENT),
            "WhereKeywordSegment" => Some(&WHERE_KEYWORD_SEGMENT),
            "TextsizeKeywordSegment" => Some(&TEXTSIZE_KEYWORD_SEGMENT),
            "KillKeywordSegment" => Some(&KILL_KEYWORD_SEGMENT),
            "TopKeywordSegment" => Some(&TOP_KEYWORD_SEGMENT),
            "CreateKeywordSegment" => Some(&CREATE_KEYWORD_SEGMENT),
            "InsertKeywordSegment" => Some(&INSERT_KEYWORD_SEGMENT),
            "System_userKeywordSegment" => Some(&SYSTEM_USER_KEYWORD_SEGMENT),
            "DenyKeywordSegment" => Some(&DENY_KEYWORD_SEGMENT),
            "UnionKeywordSegment" => Some(&UNION_KEYWORD_SEGMENT),
            "FileKeywordSegment" => Some(&FILE_KEYWORD_SEGMENT),
            "CurrentKeywordSegment" => Some(&CURRENT_KEYWORD_SEGMENT),
            "HavingKeywordSegment" => Some(&HAVING_KEYWORD_SEGMENT),
            "UnpivotKeywordSegment" => Some(&UNPIVOT_KEYWORD_SEGMENT),
            "Current_catalogKeywordSegment" => Some(&CURRENT_CATALOG_KEYWORD_SEGMENT),
            "FreetextKeywordSegment" => Some(&FREETEXT_KEYWORD_SEGMENT),
            "AsKeywordSegment" => Some(&AS_KEYWORD_SEGMENT),
            "GotoKeywordSegment" => Some(&GOTO_KEYWORD_SEGMENT),
            "IfKeywordSegment" => Some(&IF_KEYWORD_SEGMENT),
            "OffsetsKeywordSegment" => Some(&OFFSETS_KEYWORD_SEGMENT),
            "FullscanKeywordSegment" => Some(&FULLSCAN_KEYWORD_SEGMENT),
            "Current_timestampKeywordSegment" => Some(&CURRENT_TIMESTAMP_KEYWORD_SEGMENT),
            "Read_onlyKeywordSegment" => Some(&READ_ONLY_KEYWORD_SEGMENT),
            "GroupKeywordSegment" => Some(&GROUP_KEYWORD_SEGMENT),
            "LikeKeywordSegment" => Some(&LIKE_KEYWORD_SEGMENT),
            "AppendKeywordSegment" => Some(&APPEND_KEYWORD_SEGMENT),
            "SaveKeywordSegment" => Some(&SAVE_KEYWORD_SEGMENT),
            "OrderKeywordSegment" => Some(&ORDER_KEYWORD_SEGMENT),
            "Check_constraintsKeywordSegment" => Some(&CHECK_CONSTRAINTS_KEYWORD_SEGMENT),
            "BrowseKeywordSegment" => Some(&BROWSE_KEYWORD_SEGMENT),
            "AllKeywordSegment" => Some(&ALL_KEYWORD_SEGMENT),
            "IntoKeywordSegment" => Some(&INTO_KEYWORD_SEGMENT),
            "DescKeywordSegment" => Some(&DESC_KEYWORD_SEGMENT),
            "SomeKeywordSegment" => Some(&SOME_KEYWORD_SEGMENT),
            "SymmetricKeywordSegment" => Some(&SYMMETRIC_KEYWORD_SEGMENT),
            "SemanticsimilaritydetailstableKeywordSegment" => Some(&SEMANTICSIMILARITYDETAILSTABLE_KEYWORD_SEGMENT),
            "FullKeywordSegment" => Some(&FULL_KEYWORD_SEGMENT),
            "LocalKeywordSegment" => Some(&LOCAL_KEYWORD_SEGMENT),
            "NonclusteredKeywordSegment" => Some(&NONCLUSTERED_KEYWORD_SEGMENT),
            "KeysetKeywordSegment" => Some(&KEYSET_KEYWORD_SEGMENT),
            "WindowKeywordSegment" => Some(&WINDOW_KEYWORD_SEGMENT),
            "BeginKeywordSegment" => Some(&BEGIN_KEYWORD_SEGMENT),
            "CheckpointKeywordSegment" => Some(&CHECKPOINT_KEYWORD_SEGMENT),
            "ProcKeywordSegment" => Some(&PROC_KEYWORD_SEGMENT),
            "ToKeywordSegment" => Some(&TO_KEYWORD_SEGMENT),
            "Forward_onlyKeywordSegment" => Some(&FORWARD_ONLY_KEYWORD_SEGMENT),
            "CollateKeywordSegment" => Some(&COLLATE_KEYWORD_SEGMENT),
            "ReplicationKeywordSegment" => Some(&REPLICATION_KEYWORD_SEGMENT),
            "GrantKeywordSegment" => Some(&GRANT_KEYWORD_SEGMENT),
            "MergeKeywordSegment" => Some(&MERGE_KEYWORD_SEGMENT),
            "KeyKeywordSegment" => Some(&KEY_KEYWORD_SEGMENT),
            "RowcountKeywordSegment" => Some(&ROWCOUNT_KEYWORD_SEGMENT),
            "StatisticsKeywordSegment" => Some(&STATISTICS_KEYWORD_SEGMENT),
            "OpenKeywordSegment" => Some(&OPEN_KEYWORD_SEGMENT),
            "OverlayKeywordSegment" => Some(&OVERLAY_KEYWORD_SEGMENT),
            "Current_timeKeywordSegment" => Some(&CURRENT_TIME_KEYWORD_SEGMENT),
            "BackupKeywordSegment" => Some(&BACKUP_KEYWORD_SEGMENT),
            "SemantickeyphrasetableKeywordSegment" => Some(&SEMANTICKEYPHRASETABLE_KEYWORD_SEGMENT),
            "OptionKeywordSegment" => Some(&OPTION_KEYWORD_SEGMENT),
            "ThrowKeywordSegment" => Some(&THROW_KEYWORD_SEGMENT),
            "UseKeywordSegment" => Some(&USE_KEYWORD_SEGMENT),
            "DbccKeywordSegment" => Some(&DBCC_KEYWORD_SEGMENT),
            "Try_convertKeywordSegment" => Some(&TRY_CONVERT_KEYWORD_SEGMENT),
            "OpenxmlKeywordSegment" => Some(&OPENXML_KEYWORD_SEGMENT),
            "NullifKeywordSegment" => Some(&NULLIF_KEYWORD_SEGMENT),
            "CommitKeywordSegment" => Some(&COMMIT_KEYWORD_SEGMENT),
            "AndKeywordSegment" => Some(&AND_KEYWORD_SEGMENT),
            "HoldlockKeywordSegment" => Some(&HOLDLOCK_KEYWORD_SEGMENT),
            "TranKeywordSegment" => Some(&TRAN_KEYWORD_SEGMENT),
            "StaticKeywordSegment" => Some(&STATIC_KEYWORD_SEGMENT),
            "FillfactorKeywordSegment" => Some(&FILLFACTOR_KEYWORD_SEGMENT),
            "DeallocateKeywordSegment" => Some(&DEALLOCATE_KEYWORD_SEGMENT),
            "CascadeKeywordSegment" => Some(&CASCADE_KEYWORD_SEGMENT),
            "ExceptKeywordSegment" => Some(&EXCEPT_KEYWORD_SEGMENT),
            "NotKeywordSegment" => Some(&NOT_KEYWORD_SEGMENT),
            "ViewKeywordSegment" => Some(&VIEW_KEYWORD_SEGMENT),
            "ColumnKeywordSegment" => Some(&COLUMN_KEYWORD_SEGMENT),
            "BulkKeywordSegment" => Some(&BULK_KEYWORD_SEGMENT),
            "PivotKeywordSegment" => Some(&PIVOT_KEYWORD_SEGMENT),
            "SetuserKeywordSegment" => Some(&SETUSER_KEYWORD_SEGMENT),
            "TransactionKeywordSegment" => Some(&TRANSACTION_KEYWORD_SEGMENT),
            "ComputeKeywordSegment" => Some(&COMPUTE_KEYWORD_SEGMENT),
            "Current_schemaKeywordSegment" => Some(&CURRENT_SCHEMA_KEYWORD_SEGMENT),
            "RollbackKeywordSegment" => Some(&ROLLBACK_KEYWORD_SEGMENT),
            "WritetextKeywordSegment" => Some(&WRITETEXT_KEYWORD_SEGMENT),
            "FetchKeywordSegment" => Some(&FETCH_KEYWORD_SEGMENT),
            "ResampleKeywordSegment" => Some(&RESAMPLE_KEYWORD_SEGMENT),
            "Type_warningKeywordSegment" => Some(&TYPE_WARNING_KEYWORD_SEGMENT),
            "DistributedKeywordSegment" => Some(&DISTRIBUTED_KEYWORD_SEGMENT),
            "InKeywordSegment" => Some(&IN_KEYWORD_SEGMENT),
            "SetKeywordSegment" => Some(&SET_KEYWORD_SEGMENT),
            "ExitKeywordSegment" => Some(&EXIT_KEYWORD_SEGMENT),
            "ErrlvlKeywordSegment" => Some(&ERRLVL_KEYWORD_SEGMENT),
            "PrintKeywordSegment" => Some(&PRINT_KEYWORD_SEGMENT),
            "UniqueKeywordSegment" => Some(&UNIQUE_KEYWORD_SEGMENT),
            "GlobalKeywordSegment" => Some(&GLOBAL_KEYWORD_SEGMENT),
            "ByKeywordSegment" => Some(&BY_KEYWORD_SEGMENT),
            "ContainsKeywordSegment" => Some(&CONTAINS_KEYWORD_SEGMENT),
            "ForKeywordSegment" => Some(&FOR_KEYWORD_SEGMENT),
            "Native_compilationKeywordSegment" => Some(&NATIVE_COMPILATION_KEYWORD_SEGMENT),
            "NocheckKeywordSegment" => Some(&NOCHECK_KEYWORD_SEGMENT),
            "TablesampleKeywordSegment" => Some(&TABLESAMPLE_KEYWORD_SEGMENT),
            "DeleteKeywordSegment" => Some(&DELETE_KEYWORD_SEGMENT),
            "OptimisticKeywordSegment" => Some(&OPTIMISTIC_KEYWORD_SEGMENT),
            "DecryptionKeywordSegment" => Some(&DECRYPTION_KEYWORD_SEGMENT),
            "BatchsizeKeywordSegment" => Some(&BATCHSIZE_KEYWORD_SEGMENT),
            "ReconfigureKeywordSegment" => Some(&RECONFIGURE_KEYWORD_SEGMENT),
            "ConvertKeywordSegment" => Some(&CONVERT_KEYWORD_SEGMENT),
            "RevertKeywordSegment" => Some(&REVERT_KEYWORD_SEGMENT),
            "AscKeywordSegment" => Some(&ASC_KEYWORD_SEGMENT),
            "CrossKeywordSegment" => Some(&CROSS_KEYWORD_SEGMENT),
            "ForeignKeywordSegment" => Some(&FOREIGN_KEYWORD_SEGMENT),
            "TsequalKeywordSegment" => Some(&TSEQUAL_KEYWORD_SEGMENT),
            "Current_roleKeywordSegment" => Some(&CURRENT_ROLE_KEYWORD_SEGMENT),
            "ListKeywordSegment" => Some(&LIST_KEYWORD_SEGMENT),
            "UpdatetextKeywordSegment" => Some(&UPDATETEXT_KEYWORD_SEGMENT),
            "ProcedureKeywordSegment" => Some(&PROCEDURE_KEYWORD_SEGMENT),
            "OnKeywordSegment" => Some(&ON_KEYWORD_SEGMENT),
            "OuterKeywordSegment" => Some(&OUTER_KEYWORD_SEGMENT),
            "NullKeywordSegment" => Some(&NULL_KEYWORD_SEGMENT),
            "CheckKeywordSegment" => Some(&CHECK_KEYWORD_SEGMENT),
            "ContainstableKeywordSegment" => Some(&CONTAINSTABLE_KEYWORD_SEGMENT),
            "WithKeywordSegment" => Some(&WITH_KEYWORD_SEGMENT),
            "LeftKeywordSegment" => Some(&LEFT_KEYWORD_SEGMENT),
            "DoubleKeywordSegment" => Some(&DOUBLE_KEYWORD_SEGMENT),
            "IsKeywordSegment" => Some(&IS_KEYWORD_SEGMENT),
            "PercentKeywordSegment" => Some(&PERCENT_KEYWORD_SEGMENT),
            "IdentityKeywordSegment" => Some(&IDENTITY_KEYWORD_SEGMENT),
            "AddKeywordSegment" => Some(&ADD_KEYWORD_SEGMENT),
            "ReferencesKeywordSegment" => Some(&REFERENCES_KEYWORD_SEGMENT),
            "ElseKeywordSegment" => Some(&ELSE_KEYWORD_SEGMENT),
            "TriggerKeywordSegment" => Some(&TRIGGER_KEYWORD_SEGMENT),
            "TableKeywordSegment" => Some(&TABLE_KEYWORD_SEGMENT),
            "AuthorizationKeywordSegment" => Some(&AUTHORIZATION_KEYWORD_SEGMENT),
            "ExecuteKeywordSegment" => Some(&EXECUTE_KEYWORD_SEGMENT),
            "OpendatasourceKeywordSegment" => Some(&OPENDATASOURCE_KEYWORD_SEGMENT),
            "JoinKeywordSegment" => Some(&JOIN_KEYWORD_SEGMENT),
            "NationalKeywordSegment" => Some(&NATIONAL_KEYWORD_SEGMENT),
            "OffKeywordSegment" => Some(&OFF_KEYWORD_SEGMENT),
            "ReturnKeywordSegment" => Some(&RETURN_KEYWORD_SEGMENT),
            "PrimaryKeywordSegment" => Some(&PRIMARY_KEYWORD_SEGMENT),
            "DistinctKeywordSegment" => Some(&DISTINCT_KEYWORD_SEGMENT),
            "IntersectKeywordSegment" => Some(&INTERSECT_KEYWORD_SEGMENT),
            "AlterKeywordSegment" => Some(&ALTER_KEYWORD_SEGMENT),
            "CaseKeywordSegment" => Some(&CASE_KEYWORD_SEGMENT),
            "EscapeKeywordSegment" => Some(&ESCAPE_KEYWORD_SEGMENT),
            "RestoreKeywordSegment" => Some(&RESTORE_KEYWORD_SEGMENT),
            "VaryingKeywordSegment" => Some(&VARYING_KEYWORD_SEGMENT),
            "EndKeywordSegment" => Some(&END_KEYWORD_SEGMENT),
            "SemanticsimilaritytableKeywordSegment" => Some(&SEMANTICSIMILARITYTABLE_KEYWORD_SEGMENT),
            "Current_userKeywordSegment" => Some(&CURRENT_USER_KEYWORD_SEGMENT),
            _ => None,
    }
}
