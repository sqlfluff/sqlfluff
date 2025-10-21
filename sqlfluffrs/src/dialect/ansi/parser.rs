/* This is a generated file! */
use once_cell::sync::Lazy;
use crate::parser::{Grammar, ParseMode};

// name='AbortKeywordSegment'
pub static ABORT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ABORT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AbsKeywordSegment'
pub static ABS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ABS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AbsoluteKeywordSegment'
pub static ABSOLUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ABSOLUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AccessKeywordSegment'
pub static ACCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ACCESS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AccessStatementSegment'
pub static ACCESS_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AccessStatementSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ManageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "PipeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Reference_usageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AccountKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TablespaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ShareKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PublicKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AdminKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CopyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Current_userKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Session_userKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RevokeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ManageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "PipeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Reference_usageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AccountKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TablespaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ShareKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AccountKeywordSegment'
pub static ACCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ACCOUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AccountsKeywordSegment'
pub static ACCOUNTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ACCOUNTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ACTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AdaKeywordSegment'
pub static ADA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ADA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ADD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AdminKeywordSegment'
pub static ADMIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ADMIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AFTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AggregateKeywordSegment'
pub static AGGREGATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AGGREGATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AggregateOrderByClause'
pub static AGGREGATE_ORDER_BY_CLAUSE: Lazy<Grammar> = Lazy::new(||
// AggregateOrderByClause
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='AliasExpressionSegment'
pub static ALIAS_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AliasExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "AsAliasOperatorSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SingleQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AliasKeywordSegment'
pub static ALIAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALIAS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AllocateKeywordSegment'
pub static ALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALLOCATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AlsoKeywordSegment'
pub static ALSO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALSO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AlterSequenceOptionsSegment'
pub static ALTER_SEQUENCE_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AlterSequenceOptionsSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AlterSequenceStatementSegment'
pub static ALTER_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AlterSequenceStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "AlterSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AlterTableDropColumnGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AlterTableStatementSegment'
pub static ALTER_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AlterTableStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "AlterTableOptionsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ALWAYS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AmpersandSegment'
pub static AMPERSAND_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "&",
    token_type: "ampersand",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='AnalyseKeywordSegment'
pub static ANALYSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ANALYSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AnalyzeKeywordSegment'
pub static ANALYZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ANALYZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AndOperatorGrammar'
pub static AND_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AND",
    token_type: "binary_operator",
    raw_class: "BinaryOperatorSegment",
    optional: false,
}
);

// name='AnyKeywordSegment'
pub static ANY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ANY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ApplyKeywordSegment'
pub static APPLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "APPLY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AreKeywordSegment'
pub static ARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ARE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MinusSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DivideSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MultiplySegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModuloSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BitwiseAndSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BitwiseOrSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BitwiseXorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BitwiseLShiftSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BitwiseRShiftSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ArrayAccessorSegment'
pub static ARRAY_ACCESSOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ArrayAccessorSegment
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "SliceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
);

// name='ArrayExpressionSegment'
pub static ARRAY_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ArrayExpressionSegment
Grammar::Nothing()
);

// name='ArrayKeywordSegment'
pub static ARRAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ARRAY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ArrayLiteralSegment'
pub static ARRAY_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ArrayLiteralSegment
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ArrayTypeSegment'
pub static ARRAY_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ArrayTypeSegment
Grammar::Nothing()
);

// name='AsAliasOperatorSegment'
pub static AS_ALIAS_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// AsAliasOperatorSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ASC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AsensitiveKeywordSegment'
pub static ASENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ASENSITIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AssertionKeywordSegment'
pub static ASSERTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ASSERTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AssignmentKeywordSegment'
pub static ASSIGNMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ASSIGNMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AsymmetricKeywordSegment'
pub static ASYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ASYMMETRIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AtKeywordSegment'
pub static AT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AtomicKeywordSegment'
pub static ATOMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ATOMIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AttributeKeywordSegment'
pub static ATTRIBUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ATTRIBUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AttributesKeywordSegment'
pub static ATTRIBUTES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ATTRIBUTES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AuditKeywordSegment'
pub static AUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AUDIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AuthorizationKeywordSegment'
pub static AUTHORIZATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AUTHORIZATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Auto_incrementKeywordSegment'
pub static AUTO_INCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AUTO_INCREMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='AvgKeywordSegment'
pub static AVG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AVG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Avg_row_lengthKeywordSegment'
pub static AVG_ROW_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "AVG_ROW_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BackupKeywordSegment'
pub static BACKUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BACKUP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BackwardKeywordSegment'
pub static BACKWARD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BACKWARD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BareFunctionSegment'
pub static BARE_FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser {
    templates: vec!["CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP"],
    token_type: "bare_function",
    raw_class: "CodeSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BaseFileSegment'
pub static BASE_FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "file",
//    token_type: "BaseFileSegment",
}
);

// name='BaseSegment'
pub static BASE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "base",
//    token_type: "BaseSegment",
}
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BEFORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BEGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BernoulliKeywordSegment'
pub static BERNOULLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BERNOULLI",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BETWEEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BigintKeywordSegment'
pub static BIGINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BIGINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BINARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BooleanBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BinaryOperatorSegment'
pub static BINARY_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "binary_operator",
//    token_type: "BinaryOperatorSegment",
}
);

// name='BindingKeywordSegment'
pub static BINDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BINDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BitKeywordSegment'
pub static BIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Bit_lengthKeywordSegment'
pub static BIT_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BIT_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BitvarKeywordSegment'
pub static BITVAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BITVAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BitwiseAndSegment'
pub static BITWISE_AND_SEGMENT: Lazy<Grammar> = Lazy::new(||
// BitwiseAndSegment
Grammar::Ref {
    name: "AmpersandSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='BitwiseLShiftSegment'
pub static BITWISE_L_SHIFT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// BitwiseLShiftSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='BitwiseOrSegment'
pub static BITWISE_OR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// BitwiseOrSegment
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='BitwiseRShiftSegment'
pub static BITWISE_R_SHIFT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// BitwiseRShiftSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='BitwiseXorSegment'
pub static BITWISE_XOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "^",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='BlobKeywordSegment'
pub static BLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BoolKeywordSegment'
pub static BOOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BOOL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BooleanKeywordSegment'
pub static BOOLEAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BOOLEAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FalseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BothKeywordSegment'
pub static BOTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BOTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BracketedArguments'
pub static BRACKETED_ARGUMENTS: Lazy<Grammar> = Lazy::new(||
// BracketedArguments
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BracketedSegment'
pub static BRACKETED_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "bracketed",
//    token_type: "BracketedSegment",
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='BreadthKeywordSegment'
pub static BREADTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BREADTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BreakKeywordSegment'
pub static BREAK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BREAK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BrowseKeywordSegment'
pub static BROWSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BROWSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='BulkKeywordSegment'
pub static BULK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BULK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "BY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CTEColumnList'
pub static C_T_E_COLUMN_LIST: Lazy<Grammar> = Lazy::new(||
// CTEColumnList
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CTEDefinitionSegment'
pub static C_T_E_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CTEDefinitionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CTEColumnList",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CacheKeywordSegment'
pub static CACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CACHE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CallKeywordSegment'
pub static CALL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CALL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CalledKeywordSegment'
pub static CALLED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CALLED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CardinalityKeywordSegment'
pub static CARDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CARDINALITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CASCADE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CascadedKeywordSegment'
pub static CASCADED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CASCADED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CaseExpressionSegment'
pub static CASE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CaseExpressionSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: true,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: true,
}
,
Grammar::Meta("dedent")
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: true,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: true,
}
,
Grammar::Meta("dedent")
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CastOperatorSegment'
pub static CAST_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "::",
    token_type: "casting_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='CatalogKeywordSegment'
pub static CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Catalog_nameKeywordSegment'
pub static CATALOG_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CATALOG_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CeilKeywordSegment'
pub static CEIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CEIL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CeilingKeywordSegment'
pub static CEILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CEILING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ChainKeywordSegment'
pub static CHAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHAIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ChangeKeywordSegment'
pub static CHANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHANGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CharCharacterSetGrammar'
pub static CHAR_CHARACTER_SET_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='CharKeywordSegment'
pub static CHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Char_lengthKeywordSegment'
pub static CHAR_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHAR_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CharacterKeywordSegment'
pub static CHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Character_lengthKeywordSegment'
pub static CHARACTER_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTER_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Character_set_catalogKeywordSegment'
pub static CHARACTER_SET_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTER_SET_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Character_set_nameKeywordSegment'
pub static CHARACTER_SET_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTER_SET_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Character_set_schemaKeywordSegment'
pub static CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTER_SET_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CharacteristicsKeywordSegment'
pub static CHARACTERISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTERISTICS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CharactersKeywordSegment'
pub static CHARACTERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHARACTERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHECK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CheckedKeywordSegment'
pub static CHECKED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHECKED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CheckpointKeywordSegment'
pub static CHECKPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHECKPOINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ChecksumKeywordSegment'
pub static CHECKSUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CHECKSUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ClassKeywordSegment'
pub static CLASS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLASS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Class_originKeywordSegment'
pub static CLASS_ORIGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLASS_ORIGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ClobKeywordSegment'
pub static CLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CloseKeywordSegment'
pub static CLOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLOSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ClusterKeywordSegment'
pub static CLUSTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLUSTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ClusteredKeywordSegment'
pub static CLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CLUSTERED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CoalesceKeywordSegment'
pub static COALESCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COALESCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CobolKeywordSegment'
pub static COBOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COBOL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CodeSegment'
pub static CODE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "raw",
//    token_type: "CodeSegment",
}
);

// name='CollateGrammar'
pub static COLLATE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CollationKeywordSegment'
pub static COLLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CollationReferenceSegment'
pub static COLLATION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CollationReferenceSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Collation_catalogKeywordSegment'
pub static COLLATION_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLATION_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Collation_nameKeywordSegment'
pub static COLLATION_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLATION_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Collation_schemaKeywordSegment'
pub static COLLATION_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLATION_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CollectKeywordSegment'
pub static COLLECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLLECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ColonDelimiterSegment'
pub static COLON_DELIMITER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ":",
    token_type: "colon_delimiter",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='ColonPrefixSegment'
pub static COLON_PREFIX_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ":",
    token_type: "colon_prefix",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='ColonSegment'
pub static COLON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ":",
    token_type: "colon",
    raw_class: "SymbolSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ColumnConstraintSegment'
pub static COLUMN_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ColumnConstraintSegment
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CheckKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnConstraintDefaultGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotEnforcedGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "UniqueKeyGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AutoIncrementGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotEnforcedGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CollateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CollationReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ColumnGeneratedGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ColumnDefinitionSegment'
pub static COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ColumnDefinitionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Anything
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "ColumnConstraintSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ColumnGeneratedGrammar'
pub static COLUMN_GENERATED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLUMN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ColumnReferenceSegment'
pub static COLUMN_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ColumnReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='Column_nameKeywordSegment'
pub static COLUMN_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLUMN_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ColumnsExpressionFunctionContentsSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ColumnsExpressionFunctionContentsSegment
Grammar::Nothing()
);

// name='ColumnsExpressionFunctionNameSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ColumnsExpressionFunctionNameSegment
Grammar::Ref {
    name: "ColumnsExpressionNameGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='ColumnsExpressionGrammar'
pub static COLUMNS_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ColumnsExpressionNameGrammar'
pub static COLUMNS_EXPRESSION_NAME_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ColumnsKeywordSegment'
pub static COLUMNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COLUMNS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CommaSegment'
pub static COMMA_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ",",
    token_type: "comma",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='Command_functionKeywordSegment'
pub static COMMAND_FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMMAND_FUNCTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Command_function_codeKeywordSegment'
pub static COMMAND_FUNCTION_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMMAND_FUNCTION_CODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CommentClauseSegment'
pub static COMMENT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CommentClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommentKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CommentKeywordSegment'
pub static COMMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CommentSegment'
pub static COMMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "comment",
//    token_type: "CommentSegment",
}
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMMIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CommittedKeywordSegment'
pub static COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMMITTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GreaterThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LessThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotEqualToSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LikeOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IsDistinctFromGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ComparisonOperatorSegment'
pub static COMPARISON_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "comparison_operator",
//    token_type: "ComparisonOperatorSegment",
}
);

// name='CompletionKeywordSegment'
pub static COMPLETION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMPLETION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CompositeBinaryOperatorSegment'
pub static COMPOSITE_BINARY_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "binary_operator",
//    token_type: "CompositeBinaryOperatorSegment",
}
);

// name='CompositeComparisonOperatorSegment'
pub static COMPOSITE_COMPARISON_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "comparison_operator",
//    token_type: "CompositeComparisonOperatorSegment",
}
);

// name='CompressKeywordSegment'
pub static COMPRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMPRESS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ComputeKeywordSegment'
pub static COMPUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COMPUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConcatSegment'
pub static CONCAT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ConcatSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='ConditionKeywordSegment'
pub static CONDITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONDITION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Condition_numberKeywordSegment'
pub static CONDITION_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONDITION_NUMBER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConditionalCrossJoinKeywordsGrammar'
pub static CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "CrossKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='ConditionalJoinKeywordsGrammar'
pub static CONDITIONAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ConditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NonStandardJoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ConnectKeywordSegment'
pub static CONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONNECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConnectionKeywordSegment'
pub static CONNECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONNECTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Connection_nameKeywordSegment'
pub static CONNECTION_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONNECTION_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRAINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Constraint_catalogKeywordSegment'
pub static CONSTRAINT_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRAINT_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Constraint_nameKeywordSegment'
pub static CONSTRAINT_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRAINT_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Constraint_schemaKeywordSegment'
pub static CONSTRAINT_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRAINT_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConstraintsKeywordSegment'
pub static CONSTRAINTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRAINTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConstructorKeywordSegment'
pub static CONSTRUCTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONSTRUCTOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ContainsKeywordSegment'
pub static CONTAINS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONTAINS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ContainstableKeywordSegment'
pub static CONTAINSTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONTAINSTABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ContinueKeywordSegment'
pub static CONTINUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONTINUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConversionKeywordSegment'
pub static CONVERSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONVERSION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ConvertKeywordSegment'
pub static CONVERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CONVERT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CopyKeywordSegment'
pub static COPY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COPY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CorrKeywordSegment'
pub static CORR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CORR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CorrespondingKeywordSegment'
pub static CORRESPONDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CORRESPONDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CountKeywordSegment'
pub static COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Covar_popKeywordSegment'
pub static COVAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COVAR_POP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Covar_sampKeywordSegment'
pub static COVAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "COVAR_SAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CreateCastStatementSegment'
pub static CREATE_CAST_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateCastStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SpecificKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StaticKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ConstructorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "MethodKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AssignmentKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateDatabaseStatementSegment'
pub static CREATE_DATABASE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateDatabaseStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateFunctionStatementSegment'
pub static CREATE_FUNCTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateFunctionStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ReturnsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "FunctionDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateIndexStatementSegment'
pub static CREATE_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateIndexStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CREATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CreateModelStatementSegment'
pub static CREATE_MODEL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateModelStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OptionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateRoleStatementSegment'
pub static CREATE_ROLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateRoleStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateSchemaStatementSegment'
pub static CREATE_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateSchemaStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateSequenceOptionsSegment'
pub static CREATE_SEQUENCE_OPTIONS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateSequenceOptionsSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateSequenceStatementSegment'
pub static CREATE_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateSequenceStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "CreateSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateTableStatementSegment'
pub static CREATE_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateTableStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryTransientGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TableEndClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateTriggerStatementSegment'
pub static CREATE_TRIGGER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateTriggerStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BeforeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsteadKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OldKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ImmediateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeferredKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EachKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StatementKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionNameIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionContentsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateUserStatementSegment'
pub static CREATE_USER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateUserStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreateViewStatementSegment'
pub static CREATE_VIEW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CreateViewStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='CreatedbKeywordSegment'
pub static CREATEDB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CREATEDB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CreateroleKeywordSegment'
pub static CREATEROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CREATEROLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CreateuserKeywordSegment'
pub static CREATEUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CREATEUSER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CROSS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CsvKeywordSegment'
pub static CSV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CSV",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CubeFunctionNameSegment'
pub static CUBE_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CubeFunctionNameSegment
Grammar::StringParser {
    template: "CUBE",
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
}
);

// name='CubeKeywordSegment'
pub static CUBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CUBE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CubeRollupClauseSegment'
pub static CUBE_ROLLUP_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// CubeRollupClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "CubeFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RollupFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "GroupingExpressionList",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Cume_distKeywordSegment'
pub static CUME_DIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CUME_DIST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_DATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_default_transform_groupKeywordSegment'
pub static CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_DEFAULT_TRANSFORM_GROUP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_pathKeywordSegment'
pub static CURRENT_PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_PATH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_roleKeywordSegment'
pub static CURRENT_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_ROLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_TIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_TIMESTAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_transform_group_for_typeKeywordSegment'
pub static CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_TRANSFORM_GROUP_FOR_TYPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Current_userKeywordSegment'
pub static CURRENT_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURRENT_USER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CursorKeywordSegment'
pub static CURSOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURSOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Cursor_nameKeywordSegment'
pub static CURSOR_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CURSOR_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='CycleKeywordSegment'
pub static CYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "CYCLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DataKeywordSegment'
pub static DATA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATABASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DatabaseReferenceSegment'
pub static DATABASE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DatabaseReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='DatabasesKeywordSegment'
pub static DATABASES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATABASES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DatatypeIdentifierSegment'
pub static DATATYPE_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::RegexParser {
    template: r#"[A-Z_][A-Z0-9_]*"#,
    token_type: "data_type_identifier",
    raw_class: "CodeSegment",
    optional: false,
    anti_template: Some(r#"^(NOT)$"#),
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DatatypeSegment'
pub static DATATYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DatatypeSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TimeWithTZGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DoubleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PrecisionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BinaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DatatypeIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "UnsignedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CharCharacterSetGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DatePartFunctionName'
pub static DATE_PART_FUNCTION_NAME: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser {
    templates: vec!["DATEADD"],
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
}
);

// name='DatePartFunctionNameSegment'
pub static DATE_PART_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DatePartFunctionNameSegment
Grammar::Ref {
    name: "DatePartFunctionName",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='DateTimeFunctionContentsSegment'
pub static DATE_TIME_FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DateTimeFunctionContentsSegment
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::TypedParser {
    template: "single_quote",
    token_type: "date_constructor_literal",
    raw_class: "LiteralSegment",
    optional: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DatetimeKeywordSegment'
pub static DATETIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATETIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DatetimeUnitSegment'
pub static DATETIME_UNIT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::MultiStringParser {
    templates: vec!["DAY", "DAYOFYEAR", "HOUR", "MILLISECOND", "MINUTE", "MONTH", "QUARTER", "SECOND", "WEEK", "WEEKDAY", "YEAR"],
    token_type: "date_part",
    raw_class: "CodeSegment",
    optional: false,
}
);

// name='Datetime_interval_codeKeywordSegment'
pub static DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATETIME_INTERVAL_CODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Datetime_interval_precisionKeywordSegment'
pub static DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DATETIME_INTERVAL_PRECISION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DayKeywordSegment'
pub static DAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Day_hourKeywordSegment'
pub static DAY_HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAY_HOUR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Day_microsecondKeywordSegment'
pub static DAY_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAY_MICROSECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Day_minuteKeywordSegment'
pub static DAY_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAY_MINUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Day_secondKeywordSegment'
pub static DAY_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAY_SECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DayofmonthKeywordSegment'
pub static DAYOFMONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAYOFMONTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DayofweekKeywordSegment'
pub static DAYOFWEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAYOFWEEK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DayofyearKeywordSegment'
pub static DAYOFYEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAYOFYEAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DaysKeywordSegment'
pub static DAYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DAYS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DbccKeywordSegment'
pub static DBCC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DBCC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeallocateKeywordSegment'
pub static DEALLOCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEALLOCATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DecKeywordSegment'
pub static DEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DecimalKeywordSegment'
pub static DECIMAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DECIMAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeclareKeywordSegment'
pub static DECLARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DECLARE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Dedent'
pub static DEDENT: Lazy<Grammar> = Lazy::new(||
Grammar::Meta("dedent")
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFAULT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DefaultsKeywordSegment'
pub static DEFAULTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFAULTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeferrableKeywordSegment'
pub static DEFERRABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFERRABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeferredKeywordSegment'
pub static DEFERRED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFERRED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DefinedKeywordSegment'
pub static DEFINED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFINED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DefinerKeywordSegment'
pub static DEFINER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEFINER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DegreeKeywordSegment'
pub static DEGREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEGREE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Delay_key_writeKeywordSegment'
pub static DELAY_KEY_WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DELAY_KEY_WRITE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DelayedKeywordSegment'
pub static DELAYED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DELAYED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DELETE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeleteStatementSegment'
pub static DELETE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DeleteStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DelimiterGrammar'
pub static DELIMITER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='DelimiterKeywordSegment'
pub static DELIMITER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DELIMITER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DelimitersKeywordSegment'
pub static DELIMITERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DELIMITERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Dense_rankKeywordSegment'
pub static DENSE_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DENSE_RANK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DenyKeywordSegment'
pub static DENY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DENY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DepthKeywordSegment'
pub static DEPTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEPTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DerefKeywordSegment'
pub static DEREF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DEREF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DerivedKeywordSegment'
pub static DERIVED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DERIVED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DESC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DescribeKeywordSegment'
pub static DESCRIBE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DESCRIBE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DescribeStatementSegment'
pub static DESCRIBE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DescribeStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DescribeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DescriptorKeywordSegment'
pub static DESCRIPTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DESCRIPTOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DestroyKeywordSegment'
pub static DESTROY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DESTROY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DestructorKeywordSegment'
pub static DESTRUCTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DESTRUCTOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DeterministicKeywordSegment'
pub static DETERMINISTIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DETERMINISTIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DiagnosticsKeywordSegment'
pub static DIAGNOSTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DIAGNOSTICS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DictionaryKeywordSegment'
pub static DICTIONARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DICTIONARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DisableKeywordSegment'
pub static DISABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DisconnectKeywordSegment'
pub static DISCONNECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISCONNECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DiskKeywordSegment'
pub static DISK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DispatchKeywordSegment'
pub static DISPATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISPATCH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISTINCT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DistinctrowKeywordSegment'
pub static DISTINCTROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISTINCTROW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DistributedKeywordSegment'
pub static DISTRIBUTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DISTRIBUTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DivKeywordSegment'
pub static DIV_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DIV",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DivideSegment'
pub static DIVIDE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "/",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='DoKeywordSegment'
pub static DO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DomainKeywordSegment'
pub static DOMAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DOMAIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DotSegment'
pub static DOT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ".",
    token_type: "dot",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DOUBLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropCastStatementSegment'
pub static DROP_CAST_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropCastStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropDatabaseStatementSegment'
pub static DROP_DATABASE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropDatabaseStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropFunctionStatementSegment'
pub static DROP_FUNCTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropFunctionStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropIndexStatementSegment'
pub static DROP_INDEX_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropIndexStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DROP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DropModelStatementSegment'
pub static DROP_MODEL_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropModelStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropRoleStatementSegment'
pub static DROP_ROLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropRoleStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropSchemaStatementSegment'
pub static DROP_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropSchemaStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropSequenceStatementSegment'
pub static DROP_SEQUENCE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropSequenceStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropTableStatementSegment'
pub static DROP_TABLE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropTableStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropTriggerStatementSegment'
pub static DROP_TRIGGER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropTriggerStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropTypeStatementSegment'
pub static DROP_TYPE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropTypeStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropUserStatementSegment'
pub static DROP_USER_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropUserStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DropViewStatementSegment'
pub static DROP_VIEW_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// DropViewStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='DummyKeywordSegment'
pub static DUMMY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DUMMY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DumpKeywordSegment'
pub static DUMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DUMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='DynamicKeywordSegment'
pub static DYNAMIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DYNAMIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Dynamic_functionKeywordSegment'
pub static DYNAMIC_FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DYNAMIC_FUNCTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Dynamic_function_codeKeywordSegment'
pub static DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "DYNAMIC_FUNCTION_CODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EachKeywordSegment'
pub static EACH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EACH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ElementKeywordSegment'
pub static ELEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ELEMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ElseClauseSegment'
pub static ELSE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ElseClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ELSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ElseifKeywordSegment'
pub static ELSEIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ELSEIF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EmptyStructLiteralBracketsSegment'
pub static EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// EmptyStructLiteralBracketsSegment
Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='EmptyStructLiteralSegment'
pub static EMPTY_STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// EmptyStructLiteralSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EmptyStructLiteralBracketsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='EnableKeywordSegment'
pub static ENABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ENABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EnclosedKeywordSegment'
pub static ENCLOSED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ENCLOSED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EncodingKeywordSegment'
pub static ENCODING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ENCODING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EncryptedKeywordSegment'
pub static ENCRYPTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ENCRYPTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='End-execKeywordSegment'
pub static END_EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "END-EXEC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EndBracketSegment'
pub static END_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='EndCurlyBracketSegment'
pub static END_CURLY_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "}",
    token_type: "end_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "END",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EndSquareBracketSegment'
pub static END_SQUARE_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='EnumKeywordSegment'
pub static ENUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ENUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EqualsKeywordSegment'
pub static EQUALS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EQUALS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EqualsSegment'
pub static EQUALS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// EqualsSegment
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='ErrlvlKeywordSegment'
pub static ERRLVL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ERRLVL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ESCAPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EscapedKeywordSegment'
pub static ESCAPED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ESCAPED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='EveryKeywordSegment'
pub static EVERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EVERY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXCEPT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExceptionKeywordSegment'
pub static EXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXCEPTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExcludeKeywordSegment'
pub static EXCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXCLUDE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExcludingKeywordSegment'
pub static EXCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXCLUDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExclusiveKeywordSegment'
pub static EXCLUSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXCLUSIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExecKeywordSegment'
pub static EXEC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXEC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExecuteKeywordSegment'
pub static EXECUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXECUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExecutionKeywordSegment'
pub static EXECUTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXECUTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExistingKeywordSegment'
pub static EXISTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXISTING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXISTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExitKeywordSegment'
pub static EXIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExpKeywordSegment'
pub static EXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXPLAIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExplainStatementSegment'
pub static EXPLAIN_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ExplainStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExplainKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ExpressionSegment'
pub static EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ExpressionSegment
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IsClauseGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "IsNullGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotNullGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CollateGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PatternMatchingGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Expression_A_Unary_Operator_Grammar'
pub static EXPRESSION_A_UNARY_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PriorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ShorthandCastSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
Grammar::Ref {
    name: "Expression_D_Potential_Select_Statement_Without_Brackets",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MapTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ListComprehensionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AccessorGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypedStructLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ArrayExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ExtendedNaturalJoinKeywordsGrammar'
pub static EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ExtensionKeywordSegment'
pub static EXTENSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXTENSION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExtensionReferenceSegment'
pub static EXTENSION_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ExtensionReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='ExternalKeywordSegment'
pub static EXTERNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXTERNAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ExtractKeywordSegment'
pub static EXTRACT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "EXTRACT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FalseKeywordSegment'
pub static FALSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FALSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FalseSegment'
pub static FALSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FALSE",
    token_type: "boolean_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
}
);

// name='FetchClauseSegment'
pub static FETCH_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FetchClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NextKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "OnlyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TiesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FetchKeywordSegment'
pub static FETCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FETCH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FieldsKeywordSegment'
pub static FIELDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FIELDS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FileSegment'
pub static FILE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FileSegment
Grammar::Sequence {
    elements: vec![
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 1,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FillfactorKeywordSegment'
pub static FILLFACTOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FILLFACTOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FilterKeywordSegment'
pub static FILTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FILTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FinalKeywordSegment'
pub static FINAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FINAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FIRST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Float4KeywordSegment'
pub static FLOAT4_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FLOAT4",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Float8KeywordSegment'
pub static FLOAT8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FLOAT8",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FloatKeywordSegment'
pub static FLOAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FLOAT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FloorKeywordSegment'
pub static FLOOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FLOOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FlushKeywordSegment'
pub static FLUSH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FLUSH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FOLLOWING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ForceKeywordSegment'
pub static FORCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FORCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FOREIGN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FormatKeywordSegment'
pub static FORMAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FORMAT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FortranKeywordSegment'
pub static FORTRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FORTRAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ForwardKeywordSegment'
pub static FORWARD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FORWARD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FoundKeywordSegment'
pub static FOUND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FOUND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FrameClauseSegment'
pub static FRAME_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FrameClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RangeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FreeKeywordSegment'
pub static FREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FREE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FreetextKeywordSegment'
pub static FREETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FREETEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FreetexttableKeywordSegment'
pub static FREETEXTTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FREETEXTTABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FreezeKeywordSegment'
pub static FREEZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FREEZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FromClauseSegment'
pub static FROM_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FromClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FromExpressionElementSegment'
pub static FROM_EXPRESSION_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FromExpressionElementSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PreTableFunctionKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FromExpressionSegment'
pub static FROM_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FromExpressionSegment
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MLTableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
Grammar::Meta("conditional")
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MLTableExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
Grammar::Meta("conditional")
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FROM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FulltextKeywordSegment'
pub static FULLTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FULLTEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FunctionContentsExpressionGrammar'
pub static FUNCTION_CONTENTS_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TrimParametersGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionContentsExpressionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AggregateOrderByClause",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "IgnoreRespectNullsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EmptyStructLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionContentsSegment'
pub static FUNCTION_CONTENTS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FunctionContentsSegment
Grammar::Sequence {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionDefinitionGrammar'
pub static FUNCTION_DEFINITION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
// FunctionDefinitionGrammar
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionKeywordSegment'
pub static FUNCTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FUNCTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FunctionNameIdentifierSegment'
pub static FUNCTION_NAME_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "word",
    token_type: "function_name_identifier",
    raw_class: "WordSegment",
    optional: false,
}
);

// name='FunctionNameSegment'
pub static FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FunctionNameSegment
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FunctionNameIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionParameterListGrammar'
pub static FUNCTION_PARAMETER_LIST_GRAMMAR: Lazy<Grammar> = Lazy::new(||
// FunctionParameterListGrammar
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "FunctionParameterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionSegment'
pub static FUNCTION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// FunctionSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DatePartFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DateTimeFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ColumnsExpressionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionContentsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "PostFunctionGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='FunctionsKeywordSegment'
pub static FUNCTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FUNCTIONS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FusionKeywordSegment'
pub static FUSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FUSION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='FutureKeywordSegment'
pub static FUTURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "FUTURE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GKeywordSegment'
pub static G_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "G",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GeneralKeywordSegment'
pub static GENERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GENERAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GENERATED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GetKeywordSegment'
pub static GET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GlobOperatorSegment'
pub static GLOB_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "glob_operator",
    token_type: "glob_operator",
    raw_class: "ComparisonOperatorSegment",
    optional: false,
}
);

// name='GlobalKeywordSegment'
pub static GLOBAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GLOBAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GoKeywordSegment'
pub static GO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GotoKeywordSegment'
pub static GOTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GOTO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GrantKeywordSegment'
pub static GRANT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GRANT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GrantedKeywordSegment'
pub static GRANTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GRANTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GrantsKeywordSegment'
pub static GRANTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GRANTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GreaterThanOrEqualToSegment'
pub static GREATER_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
// GreaterThanOrEqualToSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='GreaterThanSegment'
pub static GREATER_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
// GreaterThanSegment
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='GreatestKeywordSegment'
pub static GREATEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GREATEST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GroupByClauseSegment'
pub static GROUP_BY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// GroupByClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GroupingSetsClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CubeRollupClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "GroupByClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GROUP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GroupingExpressionList'
pub static GROUPING_EXPRESSION_LIST: Lazy<Grammar> = Lazy::new(||
// GroupingExpressionList
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "GroupByClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='GroupingKeywordSegment'
pub static GROUPING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "GROUPING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='GroupingSetsClauseSegment'
pub static GROUPING_SETS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// GroupingSetsClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SetsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GroupingExpressionList",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='HandlerKeywordSegment'
pub static HANDLER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HANDLER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HavingClauseSegment'
pub static HAVING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// HavingClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HAVING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HeaderKeywordSegment'
pub static HEADER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HEADER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HeapKeywordSegment'
pub static HEAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HEAP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HierarchyKeywordSegment'
pub static HIERARCHY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HIERARCHY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='High_priorityKeywordSegment'
pub static HIGH_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HIGH_PRIORITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HoldKeywordSegment'
pub static HOLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOLD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HoldlockKeywordSegment'
pub static HOLDLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOLDLOCK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HorizontalJoinKeywordsGrammar'
pub static HORIZONTAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='HostKeywordSegment'
pub static HOST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HostsKeywordSegment'
pub static HOSTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOSTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='HourKeywordSegment'
pub static HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOUR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Hour_microsecondKeywordSegment'
pub static HOUR_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOUR_MICROSECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Hour_minuteKeywordSegment'
pub static HOUR_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOUR_MINUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Hour_secondKeywordSegment'
pub static HOUR_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "HOUR_SECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IdentifiedKeywordSegment'
pub static IDENTIFIED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IDENTIFIED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IdentifierSegment'
pub static IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "identifier",
//    token_type: "IdentifierSegment",
}
);

// name='IdentityKeywordSegment'
pub static IDENTITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IDENTITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Identity_insertKeywordSegment'
pub static IDENTITY_INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IDENTITY_INSERT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IdentitycolKeywordSegment'
pub static IDENTITYCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IDENTITYCOL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IGNORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RespectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IlikeKeywordSegment'
pub static ILIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ILIKE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ImmediateKeywordSegment'
pub static IMMEDIATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IMMEDIATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ImmutableKeywordSegment'
pub static IMMUTABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IMMUTABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ImplementationKeywordSegment'
pub static IMPLEMENTATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IMPLEMENTATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ImplicitIndent'
pub static IMPLICIT_INDENT: Lazy<Grammar> = Lazy::new(||
Grammar::Meta("indent")
);

// name='ImplicitKeywordSegment'
pub static IMPLICIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IMPLICIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ImportedKeywordSegment'
pub static IMPORTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IMPORTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IncludeKeywordSegment'
pub static INCLUDE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INCLUDE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IncludingKeywordSegment'
pub static INCLUDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INCLUDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IncrementKeywordSegment'
pub static INCREMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INCREMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Indent'
pub static INDENT: Lazy<Grammar> = Lazy::new(||
Grammar::Meta("indent")
);

// name='IndexColumnDefinitionSegment'
pub static INDEX_COLUMN_DEFINITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// IndexColumnDefinitionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INDEX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IndexReferenceSegment'
pub static INDEX_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// IndexReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='IndicatorKeywordSegment'
pub static INDICATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INDICATOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InfileKeywordSegment'
pub static INFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INFILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InfixKeywordSegment'
pub static INFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INFIX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InheritKeywordSegment'
pub static INHERIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INHERIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InheritsKeywordSegment'
pub static INHERITS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INHERITS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InitialKeywordSegment'
pub static INITIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INITIAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InitializeKeywordSegment'
pub static INITIALIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INITIALIZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InitiallyKeywordSegment'
pub static INITIALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INITIALLY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INNER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InoutKeywordSegment'
pub static INOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INOUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InputKeywordSegment'
pub static INPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INPUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InsensitiveKeywordSegment'
pub static INSENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSENSITIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSERT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InsertStatementSegment'
pub static INSERT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// InsertStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverwriteKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DefaultValuesGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Insert_idKeywordSegment'
pub static INSERT_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSERT_ID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InstanceKeywordSegment'
pub static INSTANCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSTANCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InstantiableKeywordSegment'
pub static INSTANTIABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSTANTIABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InsteadKeywordSegment'
pub static INSTEAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INSTEAD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Int1KeywordSegment'
pub static INT1_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT1",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Int2KeywordSegment'
pub static INT2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT2",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Int3KeywordSegment'
pub static INT3_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT3",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Int4KeywordSegment'
pub static INT4_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT4",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Int8KeywordSegment'
pub static INT8_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT8",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntKeywordSegment'
pub static INT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntegerKeywordSegment'
pub static INTEGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTEGER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntegrationKeywordSegment'
pub static INTEGRATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTEGRATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntegrationsKeywordSegment'
pub static INTEGRATIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTEGRATIONS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTERSECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntersectionKeywordSegment'
pub static INTERSECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTERSECTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntervalExpressionSegment'
pub static INTERVAL_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// IntervalExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "IntervalKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IntervalKeywordSegment'
pub static INTERVAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTERVAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INTO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='InvokerKeywordSegment'
pub static INVOKER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "INVOKER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NanLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnknownLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NormalizedGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "IS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IsNullGrammar'
pub static IS_NULL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='IsamKeywordSegment'
pub static ISAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ISAM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IsnullKeywordSegment'
pub static ISNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ISNULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IsolationKeywordSegment'
pub static ISOLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ISOLATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='IterateKeywordSegment'
pub static ITERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ITERATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='JoinClauseSegment'
pub static JOIN_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// JoinClauseSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConditionalJoinKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "NestedJoinGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
Grammar::Sequence {
    elements: vec![
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinUsingConditionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UnconditionalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExtendedNaturalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "JOIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='JoinLikeClauseGrammar'
pub static JOIN_LIKE_CLAUSE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='JoinOnConditionSegment'
pub static JOIN_ON_CONDITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// JoinOnConditionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LeftKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RightKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OuterKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='JsonKeywordSegment'
pub static JSON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "JSON",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='KKeywordSegment'
pub static K_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "K",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "KEY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Key_memberKeywordSegment'
pub static KEY_MEMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "KEY_MEMBER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Key_typeKeywordSegment'
pub static KEY_TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "KEY_TYPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='KeysKeywordSegment'
pub static KEYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "KEYS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='KeywordSegment'
pub static KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "keyword",
//    token_type: "KeywordSegment",
}
);

// name='KillKeywordSegment'
pub static KILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "KILL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LancompilerKeywordSegment'
pub static LANCOMPILER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LANCOMPILER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LanguageKeywordSegment'
pub static LANGUAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LANGUAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LargeKeywordSegment'
pub static LARGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LARGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Last_insert_idKeywordSegment'
pub static LAST_INSERT_ID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LAST_INSERT_ID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LateralKeywordSegment'
pub static LATERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LATERAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LeadingKeywordSegment'
pub static LEADING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LEADING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LeastKeywordSegment'
pub static LEAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LEAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LeaveKeywordSegment'
pub static LEAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LEAVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LEFT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LengthKeywordSegment'
pub static LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LessKeywordSegment'
pub static LESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LESS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LessThanOrEqualToSegment'
pub static LESS_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
// LessThanOrEqualToSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='LessThanSegment'
pub static LESS_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
// LessThanSegment
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='LevelKeywordSegment'
pub static LEVEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LEVEL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LikeGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "EscapeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RlikeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IlikeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LIKE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LikeOperatorSegment'
pub static LIKE_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "like_operator",
    token_type: "like_operator",
    raw_class: "ComparisonOperatorSegment",
    optional: false,
}
);

// name='LimitClauseSegment'
pub static LIMIT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// LimitClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='LimitKeywordSegment'
pub static LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LIMIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LinenoKeywordSegment'
pub static LINENO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LINENO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LinesKeywordSegment'
pub static LINES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LINES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ListComprehensionGrammar'
pub static LIST_COMPREHENSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='ListenKeywordSegment'
pub static LISTEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LISTEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifiedNumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TypedArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='LiteralKeywordSegment'
pub static LITERAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "literal",
//    token_type: "LiteralKeywordSegment",
}
);

// name='LiteralSegment'
pub static LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "literal",
//    token_type: "LiteralSegment",
}
);

// name='LnKeywordSegment'
pub static LN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LoadKeywordSegment'
pub static LOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOAD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocalAliasSegment'
pub static LOCAL_ALIAS_SEGMENT: Lazy<Grammar> = Lazy::new(||
// LocalAliasSegment
Grammar::Nothing()
);

// name='LocalKeywordSegment'
pub static LOCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocaltimeKeywordSegment'
pub static LOCALTIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCALTIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocaltimestampKeywordSegment'
pub static LOCALTIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCALTIMESTAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocationKeywordSegment'
pub static LOCATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocatorKeywordSegment'
pub static LOCATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCATOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LockKeywordSegment'
pub static LOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LocksKeywordSegment'
pub static LOCKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOCKS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LoginKeywordSegment'
pub static LOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LogsKeywordSegment'
pub static LOGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOGS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LongKeywordSegment'
pub static LONG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LONG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LongblobKeywordSegment'
pub static LONGBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LONGBLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LongtextKeywordSegment'
pub static LONGTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LONGTEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LoopKeywordSegment'
pub static LOOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOOP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Low_priorityKeywordSegment'
pub static LOW_PRIORITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOW_PRIORITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='LowerKeywordSegment'
pub static LOWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "LOWER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MKeywordSegment'
pub static M_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "M",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MLTableExpressionSegment'
pub static M_L_TABLE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MLTableExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MlKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ManageKeywordSegment'
pub static MANAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MANAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MapKeywordSegment'
pub static MAP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MAP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MapTypeSegment'
pub static MAP_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MapTypeSegment
Grammar::Nothing()
);

// name='MaskingKeywordSegment'
pub static MASKING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MASKING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MatchConditionSegment'
pub static MATCH_CONDITION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MatchConditionSegment
Grammar::Nothing()
);

// name='MatchKeywordSegment'
pub static MATCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MATCH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MatchedKeywordSegment'
pub static MATCHED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MATCHED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MaterializedKeywordSegment'
pub static MATERIALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MATERIALIZED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MaxKeywordSegment'
pub static MAX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MAX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Max_rowsKeywordSegment'
pub static MAX_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MAX_ROWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MaxextentsKeywordSegment'
pub static MAXEXTENTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MAXEXTENTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MaxvalueKeywordSegment'
pub static MAXVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MAXVALUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MediumblobKeywordSegment'
pub static MEDIUMBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MEDIUMBLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MediumintKeywordSegment'
pub static MEDIUMINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MEDIUMINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MediumtextKeywordSegment'
pub static MEDIUMTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MEDIUMTEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MemberKeywordSegment'
pub static MEMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MEMBER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MergeDeleteClauseSegment'
pub static MERGE_DELETE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeDeleteClauseSegment
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='MergeInsertClauseSegment'
pub static MERGE_INSERT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeInsertClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='MergeKeywordSegment'
pub static MERGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MERGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MergeMatchSegment'
pub static MERGE_MATCH_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeMatchSegment
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Ref {
    name: "MergeMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MergeNotMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 1,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='MergeMatchedClauseSegment'
pub static MERGE_MATCHED_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeMatchedClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "MergeUpdateClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MergeDeleteClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='MergeNotMatchedClauseSegment'
pub static MERGE_NOT_MATCHED_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeNotMatchedClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "MergeInsertClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='MergeStatementSegment'
pub static MERGE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "MergeIntoLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "MergeMatchSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='MergeUpdateClauseSegment'
pub static MERGE_UPDATE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// MergeUpdateClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Message_lengthKeywordSegment'
pub static MESSAGE_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MESSAGE_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Message_octet_lengthKeywordSegment'
pub static MESSAGE_OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MESSAGE_OCTET_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Message_textKeywordSegment'
pub static MESSAGE_TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MESSAGE_TEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MethodKeywordSegment'
pub static METHOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "METHOD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MiddleintKeywordSegment'
pub static MIDDLEINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MIDDLEINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MillisecondKeywordSegment'
pub static MILLISECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MILLISECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MinKeywordSegment'
pub static MIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Min_rowsKeywordSegment'
pub static MIN_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MIN_ROWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MinusKeywordSegment'
pub static MINUS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MINUS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MinusSegment'
pub static MINUS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "-",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='MinuteKeywordSegment'
pub static MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MINUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Minute_microsecondKeywordSegment'
pub static MINUTE_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MINUTE_MICROSECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Minute_secondKeywordSegment'
pub static MINUTE_SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MINUTE_SECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MinvalueKeywordSegment'
pub static MINVALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MINVALUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MlKeywordSegment'
pub static ML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ML",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MlslabelKeywordSegment'
pub static MLSLABEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MLSLABEL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModKeywordSegment'
pub static MOD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MOD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModeKeywordSegment'
pub static MODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModelKeywordSegment'
pub static MODEL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MODEL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModifiesKeywordSegment'
pub static MODIFIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MODIFIES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModifyKeywordSegment'
pub static MODIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MODIFY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModuleKeywordSegment'
pub static MODULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MODULE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ModuloSegment'
pub static MODULO_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "%",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='MonitorKeywordSegment'
pub static MONITOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MONITOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MonthKeywordSegment'
pub static MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MONTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MonthnameKeywordSegment'
pub static MONTHNAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MONTHNAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MoreKeywordSegment'
pub static MORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MoveKeywordSegment'
pub static MOVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MOVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MultiplySegment'
pub static MULTIPLY_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "*",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='MultisetKeywordSegment'
pub static MULTISET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MULTISET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MumpsKeywordSegment'
pub static MUMPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MUMPS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='MyisamKeywordSegment'
pub static MYISAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "MYISAM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NakedIdentifierSegment'
pub static NAKED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser {
    template: r#"[A-Z0-9_]*[A-Z][A-Z0-9_]*"#,
    token_type: "naked_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
    anti_template: Some(r#"^(INNER|INTERVAL|JOIN|ON|NOT|PARTITION|CASE|CROSS|RESPECT|OUTER|ROWS|IGNORE|ORDER|RIGHT|SET|FULL|NATURAL|SELECT|LEFT|UNION|USING|NULL)$"#),
}
);

// name='NameKeywordSegment'
pub static NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NamedWindowExpressionSegment'
pub static NAMED_WINDOW_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// NamedWindowExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NamedWindowSegment'
pub static NAMED_WINDOW_SEGMENT: Lazy<Grammar> = Lazy::new(||
// NamedWindowSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "NamedWindowExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NamesKeywordSegment'
pub static NAMES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NAMES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NanKeywordSegment'
pub static NAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NanLiteralSegment'
pub static NAN_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NAN",
    token_type: "null_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
}
);

// name='NationalKeywordSegment'
pub static NATIONAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NATIONAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NaturalKeywordSegment'
pub static NATURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NATURAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NcharKeywordSegment'
pub static NCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NCHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NclobKeywordSegment'
pub static NCLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NCLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NegativeSegment'
pub static NEGATIVE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "-",
    token_type: "sign_indicator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='NestedJoinGrammar'
pub static NESTED_JOIN_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NestingKeywordSegment'
pub static NESTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NESTING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NewKeywordSegment'
pub static NEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NEW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NewlineSegment'
pub static NEWLINE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "newline",
//    token_type: "NewlineSegment",
}
);

// name='NextKeywordSegment'
pub static NEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='No_write_to_binlogKeywordSegment'
pub static NO_WRITE_TO_BINLOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NO_WRITE_TO_BINLOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NoauditKeywordSegment'
pub static NOAUDIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOAUDIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocacheKeywordSegment'
pub static NOCACHE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCACHE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocheckKeywordSegment'
pub static NOCHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCHECK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocompressKeywordSegment'
pub static NOCOMPRESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCOMPRESS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocreatedbKeywordSegment'
pub static NOCREATEDB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCREATEDB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocreateroleKeywordSegment'
pub static NOCREATEROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCREATEROLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocreateuserKeywordSegment'
pub static NOCREATEUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCREATEUSER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NocycleKeywordSegment'
pub static NOCYCLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOCYCLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NoinheritKeywordSegment'
pub static NOINHERIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOINHERIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NologinKeywordSegment'
pub static NOLOGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOLOGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnorderedSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedSetExpressionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NonStandardJoinTypeKeywordsGrammar'
pub static NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NonWithNonSelectableGrammar'
pub static NON_WITH_NON_SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NonclusteredKeywordSegment'
pub static NONCLUSTERED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NONCLUSTERED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NONE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NoorderKeywordSegment'
pub static NOORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOORDER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NormalizeKeywordSegment'
pub static NORMALIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NORMALIZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NormalizedGrammar'
pub static NORMALIZED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NormalizedKeywordSegment'
pub static NORMALIZED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NORMALIZED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NosuperuserKeywordSegment'
pub static NOSUPERUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOSUPERUSER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NotEnforcedGrammar'
pub static NOT_ENFORCED_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NotEqualToSegment'
pub static NOT_EQUAL_TO_SEGMENT: Lazy<Grammar> = Lazy::new(||
// NotEqualToSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawNotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NotNullGrammar'
pub static NOT_NULL_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='NotOperatorGrammar'
pub static NOT_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NothingKeywordSegment'
pub static NOTHING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOTHING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NotifyKeywordSegment'
pub static NOTIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOTIFY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NotnullKeywordSegment'
pub static NOTNULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOTNULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NowaitKeywordSegment'
pub static NOWAIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NOWAIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NullLiteralSegment'
pub static NULL_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NULL",
    token_type: "null_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
}
);

// name='NullableKeywordSegment'
pub static NULLABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NULLABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NullifKeywordSegment'
pub static NULLIF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NULLIF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NULLS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NumberKeywordSegment'
pub static NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NUMBER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NumericKeywordSegment'
pub static NUMERIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "NUMERIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='NumericLiteralSegment'
pub static NUMERIC_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "numeric_literal",
    token_type: "numeric_literal",
    raw_class: "LiteralSegment",
    optional: false,
}
);

// name='ObjectKeywordSegment'
pub static OBJECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OBJECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ObjectLiteralElementSegment'
pub static OBJECT_LITERAL_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ObjectLiteralElementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ObjectLiteralSegment'
pub static OBJECT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ObjectLiteralSegment
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ObjectLiteralElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "{",
    token_type: "start_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: "}",
    token_type: "end_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ObjectReferenceSegment'
pub static OBJECT_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ObjectReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CastOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StartSquareBracketSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StartBracketSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Token{
    token_type: "bracketed",
//    token_type: "BracketedSegment",
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ObjectsKeywordSegment'
pub static OBJECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OBJECTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Octet_lengthKeywordSegment'
pub static OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OCTET_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OctetsKeywordSegment'
pub static OCTETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OCTETS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OFF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OfflineKeywordSegment'
pub static OFFLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OFFLINE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OffsetClauseSegment'
pub static OFFSET_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// OffsetClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OFFSET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OffsetsKeywordSegment'
pub static OFFSETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OFFSETS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OidsKeywordSegment'
pub static OIDS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OIDS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OldKeywordSegment'
pub static OLD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OLD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ON",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OnlineKeywordSegment'
pub static ONLINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ONLINE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OnlyKeywordSegment'
pub static ONLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ONLY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OpenKeywordSegment'
pub static OPEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OpendatasourceKeywordSegment'
pub static OPENDATASOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPENDATASOURCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OpenqueryKeywordSegment'
pub static OPENQUERY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPENQUERY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OpenrowsetKeywordSegment'
pub static OPENROWSET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPENROWSET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OpenxmlKeywordSegment'
pub static OPENXML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPENXML",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OperateKeywordSegment'
pub static OPERATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPERATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OperationKeywordSegment'
pub static OPERATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPERATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OperatorKeywordSegment'
pub static OPERATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPERATOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OptimizeKeywordSegment'
pub static OPTIMIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPTIMIZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OptionKeywordSegment'
pub static OPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OptionallyKeywordSegment'
pub static OPTIONALLY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPTIONALLY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OptionsKeywordSegment'
pub static OPTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OPTIONS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OrOperatorGrammar'
pub static OR_OPERATOR_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OR",
    token_type: "binary_operator",
    raw_class: "BinaryOperatorSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OrderByClauseSegment'
pub static ORDER_BY_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// OrderByClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LastKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WithFillSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SeparatorKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ORDER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NoorderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OrderingKeywordSegment'
pub static ORDERING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ORDERING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OrdinalityKeywordSegment'
pub static ORDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ORDINALITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OthersKeywordSegment'
pub static OTHERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OTHERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OutKeywordSegment'
pub static OUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OUTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OutfileKeywordSegment'
pub static OUTFILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OUTFILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OutputKeywordSegment'
pub static OUTPUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OUTPUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OverClauseSegment'
pub static OVER_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// OverClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "IgnoreRespectNullsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OVER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OverlapsClauseSegment'
pub static OVERLAPS_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// OverlapsClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OverlapsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='OverlapsKeywordSegment'
pub static OVERLAPS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OVERLAPS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OverlayKeywordSegment'
pub static OVERLAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OVERLAY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OverridingKeywordSegment'
pub static OVERRIDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OVERRIDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OverwriteKeywordSegment'
pub static OVERWRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OVERWRITE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OwnerKeywordSegment'
pub static OWNER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OWNER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='OwnershipKeywordSegment'
pub static OWNERSHIP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "OWNERSHIP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Pack_keysKeywordSegment'
pub static PACK_KEYS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PACK_KEYS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PadKeywordSegment'
pub static PAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PAD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ParameterKeywordSegment'
pub static PARAMETER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ParameterNameSegment'
pub static PARAMETER_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::RegexParser {
    template: r#"\"?[A-Z][A-Z0-9_]*\"?"#,
    token_type: "parameter",
    raw_class: "CodeSegment",
    optional: false,
    anti_template: None,
}
);

// name='ParameterSegment'
pub static PARAMETER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "?",
    token_type: "parameter",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='Parameter_modeKeywordSegment'
pub static PARAMETER_MODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_MODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Parameter_nameKeywordSegment'
pub static PARAMETER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Parameter_ordinal_positionKeywordSegment'
pub static PARAMETER_ORDINAL_POSITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_ORDINAL_POSITION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Parameter_specific_catalogKeywordSegment'
pub static PARAMETER_SPECIFIC_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_SPECIFIC_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Parameter_specific_nameKeywordSegment'
pub static PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_SPECIFIC_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Parameter_specific_schemaKeywordSegment'
pub static PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETER_SPECIFIC_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ParametersKeywordSegment'
pub static PARAMETERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARAMETERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PartialKeywordSegment'
pub static PARTIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARTIAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PartitionClauseSegment'
pub static PARTITION_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// PartitionClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PARTITION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PascalKeywordSegment'
pub static PASCAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PASCAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PasswordKeywordSegment'
pub static PASSWORD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PASSWORD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PathKeywordSegment'
pub static PATH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PATH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PathSegment'
pub static PATH_SEGMENT: Lazy<Grammar> = Lazy::new(||
// PathSegment
Grammar::OneOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Delimited {
    elements: vec![
Grammar::TypedParser {
    template: "word",
    token_type: "path_segment",
    raw_class: "WordSegment",
    optional: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='PatternMatchingGrammar'
pub static PATTERN_MATCHING_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='PctfreeKeywordSegment'
pub static PCTFREE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PCTFREE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PercentKeywordSegment'
pub static PERCENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PERCENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Percent_rankKeywordSegment'
pub static PERCENT_RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PERCENT_RANK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Percentile_contKeywordSegment'
pub static PERCENTILE_CONT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PERCENTILE_CONT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Percentile_discKeywordSegment'
pub static PERCENTILE_DISC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PERCENTILE_DISC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PipeKeywordSegment'
pub static PIPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PIPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PipeSegment'
pub static PIPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "|",
    token_type: "pipe",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='PlacingKeywordSegment'
pub static PLACING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PLACING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PlanKeywordSegment'
pub static PLAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PLAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PliKeywordSegment'
pub static PLI_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PLI",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PlusSegment'
pub static PLUS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "+",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='PolicyKeywordSegment'
pub static POLICY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "POLICY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PositionKeywordSegment'
pub static POSITION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "POSITION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PositiveSegment'
pub static POSITIVE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "+",
    token_type: "sign_indicator",
    raw_class: "SymbolSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FilterClauseGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='PostTableExpressionGrammar'
pub static POST_TABLE_EXPRESSION_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='PostfixKeywordSegment'
pub static POSTFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "POSTFIX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PowerKeywordSegment'
pub static POWER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "POWER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PreTableFunctionKeywordsGrammar'
pub static PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRECEDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRECISION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PrefixKeywordSegment'
pub static PREFIX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PREFIX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PreorderKeywordSegment'
pub static PREORDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PREORDER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PrepareKeywordSegment'
pub static PREPARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PREPARE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PreparedKeywordSegment'
pub static PREPARED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PREPARED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PreserveKeywordSegment'
pub static PRESERVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRESERVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRIMARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PrintKeywordSegment'
pub static PRINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PriorKeywordSegment'
pub static PRIOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRIOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PrivilegesKeywordSegment'
pub static PRIVILEGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PRIVILEGES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProcKeywordSegment'
pub static PROC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProceduralKeywordSegment'
pub static PROCEDURAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROCEDURAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProcedureKeywordSegment'
pub static PROCEDURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROCEDURE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProceduresKeywordSegment'
pub static PROCEDURES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROCEDURES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProcessKeywordSegment'
pub static PROCESS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROCESS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ProcesslistKeywordSegment'
pub static PROCESSLIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PROCESSLIST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PublicKeywordSegment'
pub static PUBLIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PUBLIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='PurgeKeywordSegment'
pub static PURGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "PURGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='QualifiedNumericLiteralSegment'
pub static QUALIFIED_NUMERIC_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// QualifiedNumericLiteralSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='QualifyKeywordSegment'
pub static QUALIFY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "QUALIFY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='QuarterKeywordSegment'
pub static QUARTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "QUARTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='QuoteKeywordSegment'
pub static QUOTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "QUOTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='QuotedIdentifierSegment'
pub static QUOTED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "double_quote",
    token_type: "quoted_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
}
);

// name='QuotedLiteralSegment'
pub static QUOTED_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "single_quote",
    token_type: "quoted_literal",
    raw_class: "LiteralSegment",
    optional: false,
}
);

// name='Raid0KeywordSegment'
pub static RAID0_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RAID0",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RaiserrorKeywordSegment'
pub static RAISERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RAISERROR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RANGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RankKeywordSegment'
pub static RANK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RANK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RawEqualsSegment'
pub static RAW_EQUALS_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "=",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='RawGreaterThanSegment'
pub static RAW_GREATER_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ">",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='RawKeywordSegment'
pub static RAW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RAW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RawLessThanSegment'
pub static RAW_LESS_THAN_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "<",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='RawNotSegment'
pub static RAW_NOT_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "!",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='RawSegment'
pub static RAW_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "raw",
//    token_type: "RawSegment",
}
);

// name='ReadKeywordSegment'
pub static READ_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "READ",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReadsKeywordSegment'
pub static READS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "READS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReadtextKeywordSegment'
pub static READTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "READTEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RealKeywordSegment'
pub static REAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RecheckKeywordSegment'
pub static RECHECK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RECHECK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReconfigureKeywordSegment'
pub static RECONFIGURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RECONFIGURE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RECURSIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RefKeywordSegment'
pub static REF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferenceMatchGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::AnySetOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferentialActionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferentialActionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PartialKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SimpleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Reference_usageKeywordSegment'
pub static REFERENCE_USAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REFERENCE_USAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REFERENCES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReferencingKeywordSegment'
pub static REFERENCING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REFERENCING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ActionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='RegexpKeywordSegment'
pub static REGEXP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGEXP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_avgxKeywordSegment'
pub static REGR_AVGX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_AVGX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_avgyKeywordSegment'
pub static REGR_AVGY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_AVGY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_countKeywordSegment'
pub static REGR_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_COUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_interceptKeywordSegment'
pub static REGR_INTERCEPT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_INTERCEPT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_r2KeywordSegment'
pub static REGR_R2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_R2",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_slopeKeywordSegment'
pub static REGR_SLOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_SLOPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_sxxKeywordSegment'
pub static REGR_SXX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_SXX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_sxyKeywordSegment'
pub static REGR_SXY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_SXY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Regr_syyKeywordSegment'
pub static REGR_SYY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REGR_SYY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReindexKeywordSegment'
pub static REINDEX_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REINDEX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RelativeKeywordSegment'
pub static RELATIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RELATIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReleaseKeywordSegment'
pub static RELEASE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RELEASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReloadKeywordSegment'
pub static RELOAD_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RELOAD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RENAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RepeatKeywordSegment'
pub static REPEAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REPEAT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RepeatableKeywordSegment'
pub static REPEATABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REPEATABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REPLACE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReplicationKeywordSegment'
pub static REPLICATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REPLICATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RequireKeywordSegment'
pub static REQUIRE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REQUIRE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ResetKeywordSegment'
pub static RESET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ResignalKeywordSegment'
pub static RESIGNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESIGNAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ResourceKeywordSegment'
pub static RESOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESOURCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RespectKeywordSegment'
pub static RESPECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESPECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RestartKeywordSegment'
pub static RESTART_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESTART",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RestoreKeywordSegment'
pub static RESTORE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESTORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESTRICT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ResultKeywordSegment'
pub static RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RESULT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReturnKeywordSegment'
pub static RETURN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Returned_cardinalityKeywordSegment'
pub static RETURNED_CARDINALITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURNED_CARDINALITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Returned_lengthKeywordSegment'
pub static RETURNED_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURNED_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Returned_octet_lengthKeywordSegment'
pub static RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURNED_OCTET_LENGTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Returned_sqlstateKeywordSegment'
pub static RETURNED_SQLSTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURNED_SQLSTATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ReturnsKeywordSegment'
pub static RETURNS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RETURNS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RevokeKeywordSegment'
pub static REVOKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "REVOKE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RIGHT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RlikeKeywordSegment'
pub static RLIKE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RLIKE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RoleKeywordSegment'
pub static ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RoleReferenceSegment'
pub static ROLE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// RoleReferenceSegment
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
);

// name='RolesKeywordSegment'
pub static ROLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROLES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROLLBACK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RollupFunctionNameSegment'
pub static ROLLUP_FUNCTION_NAME_SEGMENT: Lazy<Grammar> = Lazy::new(||
// RollupFunctionNameSegment
Grammar::StringParser {
    template: "ROLLUP",
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
}
);

// name='RollupKeywordSegment'
pub static ROLLUP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROLLUP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RoutineKeywordSegment'
pub static ROUTINE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROUTINE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Routine_catalogKeywordSegment'
pub static ROUTINE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROUTINE_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Routine_nameKeywordSegment'
pub static ROUTINE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROUTINE_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Routine_schemaKeywordSegment'
pub static ROUTINE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROUTINE_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RoutinesKeywordSegment'
pub static ROUTINES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROUTINES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Row_countKeywordSegment'
pub static ROW_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROW_COUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Row_numberKeywordSegment'
pub static ROW_NUMBER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROW_NUMBER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RowcountKeywordSegment'
pub static ROWCOUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROWCOUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RowguidcolKeywordSegment'
pub static ROWGUIDCOL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROWGUIDCOL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RowidKeywordSegment'
pub static ROWID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROWID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RownumKeywordSegment'
pub static ROWNUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROWNUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ROWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='RuleKeywordSegment'
pub static RULE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "RULE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SamplingExpressionSegment'
pub static SAMPLING_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SamplingExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TablesampleKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "BernoulliKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SystemKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SaveKeywordSegment'
pub static SAVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SAVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SavepointKeywordSegment'
pub static SAVEPOINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SAVEPOINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ScaleKeywordSegment'
pub static SCALE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCALE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SchemaKeywordSegment'
pub static SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SchemaReferenceSegment'
pub static SCHEMA_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SchemaReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='Schema_nameKeywordSegment'
pub static SCHEMA_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCHEMA_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SchemasKeywordSegment'
pub static SCHEMAS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCHEMAS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ScopeKeywordSegment'
pub static SCOPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCOPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Scope_catalogKeywordSegment'
pub static SCOPE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCOPE_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Scope_nameKeywordSegment'
pub static SCOPE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCOPE_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Scope_schemaKeywordSegment'
pub static SCOPE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCOPE_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ScrollKeywordSegment'
pub static SCROLL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SCROLL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SearchKeywordSegment'
pub static SEARCH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SEARCH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SecondKeywordSegment'
pub static SECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Second_microsecondKeywordSegment'
pub static SECOND_MICROSECOND_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SECOND_MICROSECOND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SectionKeywordSegment'
pub static SECTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SECTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SecurityKeywordSegment'
pub static SECURITY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SECURITY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SelectClauseElementSegment'
pub static SELECT_CLAUSE_ELEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SelectClauseElementSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "WildcardExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SelectClauseModifierSegment'
pub static SELECT_CLAUSE_MODIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SelectClauseModifierSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SelectClauseSegment'
pub static SELECT_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SelectClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SelectClauseModifierSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseElementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::GreedyOnceStarted,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverlapsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SELECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SelectStatementSegment'
pub static SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SelectStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OffsetClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::GreedyOnceStarted,
}
);

// name='SelectableGrammar'
pub static SELECTABLE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "WithCompoundNonSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "WithCompoundNonSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SelfKeywordSegment'
pub static SELF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SELF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SemicolonSegment'
pub static SEMICOLON_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ";",
    token_type: "statement_terminator",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='SensitiveKeywordSegment'
pub static SENSITIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SENSITIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SeparatorKeywordSegment'
pub static SEPARATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SEPARATOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SequenceKeywordSegment'
pub static SEQUENCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SEQUENCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MaxvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MinvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SequenceReferenceSegment'
pub static SEQUENCE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SequenceReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='SequencesKeywordSegment'
pub static SEQUENCES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SEQUENCES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SerializableKeywordSegment'
pub static SERIALIZABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SERIALIZABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ServerKeywordSegment'
pub static SERVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SERVER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Server_nameKeywordSegment'
pub static SERVER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SERVER_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SessionKeywordSegment'
pub static SESSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SESSION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Session_userKeywordSegment'
pub static SESSION_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SESSION_USER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SetClauseListSegment'
pub static SET_CLAUSE_LIST_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SetClauseListSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SetClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SetClauseSegment'
pub static SET_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SetClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SetExpressionSegment'
pub static SET_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SetExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 1,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SetOperatorSegment'
pub static SET_OPERATOR_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SetOperatorSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "UnionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExceptKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "MinusKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: Some(Box::new(
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ExceptKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Anything
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
    )),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SetSchemaStatementSegment'
pub static SET_SCHEMA_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SetSchemaStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SetofKeywordSegment'
pub static SETOF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SETOF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SetsKeywordSegment'
pub static SETS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SETS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SetuserKeywordSegment'
pub static SETUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SETUSER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ShareKeywordSegment'
pub static SHARE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SHARE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SharesKeywordSegment'
pub static SHARES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SHARES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ShorthandCastSegment'
pub static SHORTHAND_CAST_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ShorthandCastSegment
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "Expression_D_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 1,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ShowKeywordSegment'
pub static SHOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SHOW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ShutdownKeywordSegment'
pub static SHUTDOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SHUTDOWN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SignalKeywordSegment'
pub static SIGNAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SIGNAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NegativeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SimilarKeywordSegment'
pub static SIMILAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SIMILAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SimpleKeywordSegment'
pub static SIMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SIMPLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SingleIdentifierGrammar'
pub static SINGLE_IDENTIFIER_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SingleIdentifierListSegment'
pub static SINGLE_IDENTIFIER_LIST_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SingleIdentifierListSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='SingleQuotedIdentifierSegment'
pub static SINGLE_QUOTED_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::TypedParser {
    template: "single_quote",
    token_type: "quoted_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
}
);

// name='SizeKeywordSegment'
pub static SIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SIZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SizedArrayTypeSegment'
pub static SIZED_ARRAY_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// SizedArrayTypeSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ArrayAccessorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='SlashSegment'
pub static SLASH_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "/",
    token_type: "slash",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='SliceSegment'
pub static SLICE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: ":",
    token_type: "slice",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='SmallintKeywordSegment'
pub static SMALLINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SMALLINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SomeKeywordSegment'
pub static SOME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SOME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SonameKeywordSegment'
pub static SONAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SONAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SourceKeywordSegment'
pub static SOURCE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SOURCE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SpaceKeywordSegment'
pub static SPACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SPACE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SpatialKeywordSegment'
pub static SPATIAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SPATIAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SpecificKeywordSegment'
pub static SPECIFIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SPECIFIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Specific_nameKeywordSegment'
pub static SPECIFIC_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SPECIFIC_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SpecifictypeKeywordSegment'
pub static SPECIFICTYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SPECIFICTYPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlKeywordSegment'
pub static SQL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_big_resultKeywordSegment'
pub static SQL_BIG_RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_BIG_RESULT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_big_selectsKeywordSegment'
pub static SQL_BIG_SELECTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_BIG_SELECTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_big_tablesKeywordSegment'
pub static SQL_BIG_TABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_BIG_TABLES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_calc_found_rowsKeywordSegment'
pub static SQL_CALC_FOUND_ROWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_CALC_FOUND_ROWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_log_offKeywordSegment'
pub static SQL_LOG_OFF_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_LOG_OFF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_log_updateKeywordSegment'
pub static SQL_LOG_UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_LOG_UPDATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_low_priority_updatesKeywordSegment'
pub static SQL_LOW_PRIORITY_UPDATES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_LOW_PRIORITY_UPDATES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_select_limitKeywordSegment'
pub static SQL_SELECT_LIMIT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_SELECT_LIMIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_small_resultKeywordSegment'
pub static SQL_SMALL_RESULT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_SMALL_RESULT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Sql_warningsKeywordSegment'
pub static SQL_WARNINGS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQL_WARNINGS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlcaKeywordSegment'
pub static SQLCA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLCA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlcodeKeywordSegment'
pub static SQLCODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLCODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlerrorKeywordSegment'
pub static SQLERROR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLERROR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlexceptionKeywordSegment'
pub static SQLEXCEPTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLEXCEPTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlstateKeywordSegment'
pub static SQLSTATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLSTATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqlwarningKeywordSegment'
pub static SQLWARNING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQLWARNING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SqrtKeywordSegment'
pub static SQRT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SQRT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SslKeywordSegment'
pub static SSL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SSL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StableKeywordSegment'
pub static STABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StageKeywordSegment'
pub static STAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StagesKeywordSegment'
pub static STAGES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STAGES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StarSegment'
pub static STAR_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "*",
    token_type: "star",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='StartBracketSegment'
pub static START_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='StartCurlyBracketSegment'
pub static START_CURLY_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "{",
    token_type: "start_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='StartKeywordSegment'
pub static START_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "START",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StartSquareBracketSegment'
pub static START_SQUARE_BRACKET_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='StartingKeywordSegment'
pub static STARTING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STARTING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StartsKeywordSegment'
pub static STARTS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STARTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StateKeywordSegment'
pub static STATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StatementKeywordSegment'
pub static STATEMENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STATEMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StatementSegment'
pub static STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// StatementSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TransactionStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropTableStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropViewStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateUserStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropUserStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TruncateStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AccessStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateTableStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateRoleStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropRoleStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AlterTableStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SetSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropSchemaStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropTypeStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateDatabaseStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropDatabaseStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateIndexStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropIndexStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateViewStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateCastStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropCastStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateFunctionStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropFunctionStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateModelStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropModelStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DescribeStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UseStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExplainStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateSequenceStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AlterSequenceStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropSequenceStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CreateTriggerStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DropTriggerStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='StaticKeywordSegment'
pub static STATIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STATIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StatisticsKeywordSegment'
pub static STATISTICS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STATISTICS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Stddev_popKeywordSegment'
pub static STDDEV_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STDDEV_POP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Stddev_sampKeywordSegment'
pub static STDDEV_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STDDEV_SAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StdinKeywordSegment'
pub static STDIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STDIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StdoutKeywordSegment'
pub static STDOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STDOUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StorageKeywordSegment'
pub static STORAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STORAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Straight_joinKeywordSegment'
pub static STRAIGHT_JOIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STRAIGHT_JOIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StreamKeywordSegment'
pub static STREAM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STREAM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StreamsKeywordSegment'
pub static STREAMS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STREAMS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StrictKeywordSegment'
pub static STRICT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STRICT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='StringKeywordSegment'
pub static STRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STRING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StructLiteralSegment'
pub static STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// StructLiteralSegment
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='StructTypeSegment'
pub static STRUCT_TYPE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// StructTypeSegment
Grammar::Nothing()
);

// name='StructureKeywordSegment'
pub static STRUCTURE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STRUCTURE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='StyleKeywordSegment'
pub static STYLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "STYLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Subclass_originKeywordSegment'
pub static SUBCLASS_ORIGIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUBCLASS_ORIGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SublistKeywordSegment'
pub static SUBLIST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUBLIST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SubmultisetKeywordSegment'
pub static SUBMULTISET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUBMULTISET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SubstringKeywordSegment'
pub static SUBSTRING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUBSTRING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SuccessfulKeywordSegment'
pub static SUCCESSFUL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUCCESSFUL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SumKeywordSegment'
pub static SUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SuperuserKeywordSegment'
pub static SUPERUSER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SUPERUSER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SymbolSegment'
pub static SYMBOL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "symbol",
//    token_type: "SymbolSegment",
}
);

// name='SymmetricKeywordSegment'
pub static SYMMETRIC_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYMMETRIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SynonymKeywordSegment'
pub static SYNONYM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYNONYM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SysdateKeywordSegment'
pub static SYSDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYSDATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SysidKeywordSegment'
pub static SYSID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYSID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='SystemKeywordSegment'
pub static SYSTEM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYSTEM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='System_userKeywordSegment'
pub static SYSTEM_USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "SYSTEM_USER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TableConstraintSegment'
pub static TABLE_CONSTRAINT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TableConstraintSegment
Grammar::Sequence {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ForeignKeyGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TableEndClauseSegment'
pub static TABLE_END_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TableEndClauseSegment
Grammar::Nothing()
);

// name='TableExpressionSegment'
pub static TABLE_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TableExpressionSegment
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TableReferenceSegment'
pub static TABLE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TableReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='Table_nameKeywordSegment'
pub static TABLE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TABLE_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TablesKeywordSegment'
pub static TABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TABLES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TablesampleKeywordSegment'
pub static TABLESAMPLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TABLESAMPLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TablespaceKeywordSegment'
pub static TABLESPACE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TABLESPACE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TablespaceReferenceSegment'
pub static TABLESPACE_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TablespaceReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='TagReferenceSegment'
pub static TAG_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TagReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TaskKeywordSegment'
pub static TASK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TASK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TasksKeywordSegment'
pub static TASKS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TASKS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TempKeywordSegment'
pub static TEMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TEMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TemplateKeywordSegment'
pub static TEMPLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TEMPLATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TemporalQuerySegment'
pub static TEMPORAL_QUERY_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TemporalQuerySegment
Grammar::Nothing()
);

// name='TemporaryGrammar'
pub static TEMPORARY_GRAMMAR: Lazy<Grammar> = Lazy::new(||
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TemporaryKeywordSegment'
pub static TEMPORARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TEMPORARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TemporaryGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TerminateKeywordSegment'
pub static TERMINATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TERMINATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TerminatedKeywordSegment'
pub static TERMINATED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TERMINATED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TextKeywordSegment'
pub static TEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TextsizeKeywordSegment'
pub static TEXTSIZE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TEXTSIZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ThanKeywordSegment'
pub static THAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "THAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "THEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TIES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TildeSegment'
pub static TILDE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "~",
    token_type: "tilde",
    raw_class: "SymbolSegment",
    optional: false,
}
);

// name='TimeKeywordSegment'
pub static TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithoutKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TimeZoneGrammar'
pub static TIME_ZONE_GRAMMAR: Lazy<Grammar> = Lazy::new(||
// TimeZoneGrammar
Grammar::AnyNumberOf {
    elements: vec![
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AtKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TimestampKeywordSegment'
pub static TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TIMESTAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Timezone_hourKeywordSegment'
pub static TIMEZONE_HOUR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TIMEZONE_HOUR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Timezone_minuteKeywordSegment'
pub static TIMEZONE_MINUTE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TIMEZONE_MINUTE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TinyblobKeywordSegment'
pub static TINYBLOB_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TINYBLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TinyintKeywordSegment'
pub static TINYINT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TINYINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TinytextKeywordSegment'
pub static TINYTEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TINYTEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ToastKeywordSegment'
pub static TOAST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TOAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TopKeywordSegment'
pub static TOP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TOP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Top_level_countKeywordSegment'
pub static TOP_LEVEL_COUNT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TOP_LEVEL_COUNT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TrailingKeywordSegment'
pub static TRAILING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRAILING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TranKeywordSegment'
pub static TRAN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSACTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransactionStatementSegment'
pub static TRANSACTION_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TransactionStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "CommitKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "TransactionKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WorkKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NameKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ChainKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Transaction_activeKeywordSegment'
pub static TRANSACTION_ACTIVE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSACTION_ACTIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransactionsKeywordSegment'
pub static TRANSACTIONS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSACTIONS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Transactions_committedKeywordSegment'
pub static TRANSACTIONS_COMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSACTIONS_COMMITTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Transactions_rolled_backKeywordSegment'
pub static TRANSACTIONS_ROLLED_BACK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSACTIONS_ROLLED_BACK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransformKeywordSegment'
pub static TRANSFORM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSFORM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransformsKeywordSegment'
pub static TRANSFORMS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSFORMS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TransientKeywordSegment'
pub static TRANSIENT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSIENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TranslateKeywordSegment'
pub static TRANSLATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSLATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TranslationKeywordSegment'
pub static TRANSLATION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRANSLATION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TreatKeywordSegment'
pub static TREAT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TREAT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRIGGER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TriggerReferenceSegment'
pub static TRIGGER_REFERENCE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TriggerReferenceSegment
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
);

// name='Trigger_catalogKeywordSegment'
pub static TRIGGER_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRIGGER_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Trigger_nameKeywordSegment'
pub static TRIGGER_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRIGGER_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Trigger_schemaKeywordSegment'
pub static TRIGGER_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRIGGER_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TrimKeywordSegment'
pub static TRIM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRIM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LeadingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TrailingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TrueKeywordSegment'
pub static TRUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TrueSegment'
pub static TRUE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRUE",
    token_type: "boolean_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
}
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRUNCATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TruncateStatementSegment'
pub static TRUNCATE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TruncateStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TrustedKeywordSegment'
pub static TRUSTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TRUSTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TsequalKeywordSegment'
pub static TSEQUAL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TSEQUAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TupleSegment'
pub static TUPLE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TupleSegment
Grammar::Bracketed {
    elements: vec![
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TypeKeywordSegment'
pub static TYPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "TYPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='TypedArrayLiteralSegment'
pub static TYPED_ARRAY_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TypedArrayLiteralSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='TypedStructLiteralSegment'
pub static TYPED_STRUCT_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// TypedStructLiteralSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "StructLiteralSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UescapeKeywordSegment'
pub static UESCAPE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UESCAPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UidKeywordSegment'
pub static UID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNBOUNDED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UncommittedKeywordSegment'
pub static UNCOMMITTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNCOMMITTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnconditionalCrossJoinKeywordsGrammar'
pub static UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Grammar> = Lazy::new(||
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "UnconditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "HorizontalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UnderKeywordSegment'
pub static UNDER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNDER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UndoKeywordSegment'
pub static UNDO_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNDO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnencryptedKeywordSegment'
pub static UNENCRYPTED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNENCRYPTED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNIQUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnknownKeywordSegment'
pub static UNKNOWN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNKNOWN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnknownLiteralSegment'
pub static UNKNOWN_LITERAL_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Nothing()
);

// name='UnlistenKeywordSegment'
pub static UNLISTEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNLISTEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnlockKeywordSegment'
pub static UNLOCK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNLOCK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnnamedKeywordSegment'
pub static UNNAMED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNNAMED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnnestKeywordSegment'
pub static UNNEST_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNNEST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UnorderedSelectStatementSegment'
pub static UNORDERED_SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// UnorderedSelectStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::GreedyOnceStarted,
}
);

// name='UnorderedSetExpressionSegment'
pub static UNORDERED_SET_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// UnorderedSetExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 1,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UnsignedKeywordSegment'
pub static UNSIGNED_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNSIGNED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UntilKeywordSegment'
pub static UNTIL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UNTIL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UPDATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UpdateStatementSegment'
pub static UPDATE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// UpdateStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='UpdatetextKeywordSegment'
pub static UPDATETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UPDATETEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UpperKeywordSegment'
pub static UPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UPPER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UsageKeywordSegment'
pub static USAGE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USAGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UseKeywordSegment'
pub static USE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UseStatementSegment'
pub static USE_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// UseStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='Use_any_roleKeywordSegment'
pub static USE_ANY_ROLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USE_ANY_ROLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UserKeywordSegment'
pub static USER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='User_defined_type_catalogKeywordSegment'
pub static USER_DEFINED_TYPE_CATALOG_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USER_DEFINED_TYPE_CATALOG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='User_defined_type_codeKeywordSegment'
pub static USER_DEFINED_TYPE_CODE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USER_DEFINED_TYPE_CODE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='User_defined_type_nameKeywordSegment'
pub static USER_DEFINED_TYPE_NAME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USER_DEFINED_TYPE_NAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='User_defined_type_schemaKeywordSegment'
pub static USER_DEFINED_TYPE_SCHEMA_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USER_DEFINED_TYPE_SCHEMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UsersKeywordSegment'
pub static USERS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "USING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Utc_dateKeywordSegment'
pub static UTC_DATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UTC_DATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Utc_timeKeywordSegment'
pub static UTC_TIME_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UTC_TIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Utc_timestampKeywordSegment'
pub static UTC_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "UTC_TIMESTAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VacuumKeywordSegment'
pub static VACUUM_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VACUUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ValidKeywordSegment'
pub static VALID_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VALID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ValidateKeywordSegment'
pub static VALIDATE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VALIDATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ValidatorKeywordSegment'
pub static VALIDATOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VALIDATOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ValueKeywordSegment'
pub static VALUE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VALUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ValuesClauseSegment'
pub static VALUES_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// ValuesClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::OneOf {
    elements: vec![
Grammar::Ref {
    name: "ValueKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: false,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VALUES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Var_popKeywordSegment'
pub static VAR_POP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VAR_POP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Var_sampKeywordSegment'
pub static VAR_SAMP_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VAR_SAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VarbinaryKeywordSegment'
pub static VARBINARY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARBINARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Varchar2KeywordSegment'
pub static VARCHAR2_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARCHAR2",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VarcharKeywordSegment'
pub static VARCHAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARCHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VarcharacterKeywordSegment'
pub static VARCHARACTER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARCHARACTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VariableKeywordSegment'
pub static VARIABLE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARIABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VariablesKeywordSegment'
pub static VARIABLES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARIABLES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VARYING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VerboseKeywordSegment'
pub static VERBOSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VERBOSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VersionKeywordSegment'
pub static VERSION_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VERSION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VIEW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ViewsKeywordSegment'
pub static VIEWS_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VIEWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='VolatileKeywordSegment'
pub static VOLATILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "VOLATILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WaitforKeywordSegment'
pub static WAITFOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WAITFOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WarehouseKeywordSegment'
pub static WAREHOUSE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WAREHOUSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WarehousesKeywordSegment'
pub static WAREHOUSES_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WAREHOUSES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WeekKeywordSegment'
pub static WEEK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WEEK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WeekdayKeywordSegment'
pub static WEEKDAY_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WEEKDAY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WhenClauseSegment'
pub static WHEN_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WhenClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Meta("indent")
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::Meta("conditional")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WHEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WheneverKeywordSegment'
pub static WHENEVER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WHENEVER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WhereClauseSegment'
pub static WHERE_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WhereClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("indent")
,
Grammar::OneOf {
    elements: vec![
Grammar::Bracketed {
    elements: vec![
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    bracket_pairs: (
        Box::new(
Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        ),
        Box::new(
Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
}
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("dedent")
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OverlapsKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WHERE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WhileKeywordSegment'
pub static WHILE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WHILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WhitespaceSegment'
pub static WHITESPACE_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "whitespace",
//    token_type: "WhitespaceSegment",
}
);

// name='Width_bucketKeywordSegment'
pub static WIDTH_BUCKET_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WIDTH_BUCKET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WildcardExpressionSegment'
pub static WILDCARD_EXPRESSION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WildcardExpressionSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WildcardIdentifierSegment'
pub static WILDCARD_IDENTIFIER_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WildcardIdentifierSegment
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
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
}
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WINDOW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WindowSpecificationSegment'
pub static WINDOW_SPECIFICATION_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WindowSpecificationSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "PartitionClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "FrameClauseSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WithCompoundNonSelectStatementSegment'
pub static WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WithCompoundNonSelectStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "NonWithNonSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WithCompoundStatementSegment'
pub static WITH_COMPOUND_STATEMENT_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WithCompoundStatementSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Meta("conditional")
,
Grammar::Delimited {
    elements: vec![
Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    delimiter: Box::new(
Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
    ),
    allow_trailing: true,
    optional: false,
    terminators: vec![
Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Meta("conditional")
,
Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WithDataClauseSegment'
pub static WITH_DATA_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WithDataClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
,
Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WithFillSegment'
pub static WITH_FILL_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WithFillSegment
Grammar::Nothing()
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WITH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WithNoSchemaBindingClauseSegment'
pub static WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT: Lazy<Grammar> = Lazy::new(||
// WithNoSchemaBindingClauseSegment
Grammar::Sequence {
    elements: vec![
Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
Grammar::Ref {
    name: "BindingKeywordSegment",
    optional: false,
    allow_gaps: true,
    terminators: vec![
    ],
    reset_terminators: false,
}
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
}
);

// name='WithinKeywordSegment'
pub static WITHIN_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WITHIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WITHOUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WordSegment'
pub static WORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::Token{
    token_type: "word",
//    token_type: "WordSegment",
}
);

// name='WorkKeywordSegment'
pub static WORK_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WORK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WrapperKeywordSegment'
pub static WRAPPER_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WRAPPER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WriteKeywordSegment'
pub static WRITE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WRITE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='WritetextKeywordSegment'
pub static WRITETEXT_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "WRITETEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='X509KeywordSegment'
pub static X509_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "X509",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='XmlKeywordSegment'
pub static XML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "XML",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='XorKeywordSegment'
pub static XOR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "XOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='YamlKeywordSegment'
pub static YAML_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "YAML",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='YearKeywordSegment'
pub static YEAR_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "YEAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='Year_monthKeywordSegment'
pub static YEAR_MONTH_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "YEAR_MONTH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ZerofillKeywordSegment'
pub static ZEROFILL_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ZEROFILL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

// name='ZoneKeywordSegment'
pub static ZONE_KEYWORD_SEGMENT: Lazy<Grammar> = Lazy::new(||
Grammar::StringParser {
    template: "ZONE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
}
);

pub fn get_ansi_segment_grammar(name: &str) -> Option<&'static Grammar> {
    match name {
            "AbortKeywordSegment" => Some(&ABORT_KEYWORD_SEGMENT),
            "AbsKeywordSegment" => Some(&ABS_KEYWORD_SEGMENT),
            "AbsoluteKeywordSegment" => Some(&ABSOLUTE_KEYWORD_SEGMENT),
            "AccessKeywordSegment" => Some(&ACCESS_KEYWORD_SEGMENT),
            "AccessStatementSegment" => Some(&ACCESS_STATEMENT_SEGMENT),
            "AccessorGrammar" => Some(&ACCESSOR_GRAMMAR),
            "AccountKeywordSegment" => Some(&ACCOUNT_KEYWORD_SEGMENT),
            "AccountsKeywordSegment" => Some(&ACCOUNTS_KEYWORD_SEGMENT),
            "ActionKeywordSegment" => Some(&ACTION_KEYWORD_SEGMENT),
            "AdaKeywordSegment" => Some(&ADA_KEYWORD_SEGMENT),
            "AddKeywordSegment" => Some(&ADD_KEYWORD_SEGMENT),
            "AdminKeywordSegment" => Some(&ADMIN_KEYWORD_SEGMENT),
            "AfterKeywordSegment" => Some(&AFTER_KEYWORD_SEGMENT),
            "AggregateKeywordSegment" => Some(&AGGREGATE_KEYWORD_SEGMENT),
            "AggregateOrderByClause" => Some(&AGGREGATE_ORDER_BY_CLAUSE),
            "AliasExpressionSegment" => Some(&ALIAS_EXPRESSION_SEGMENT),
            "AliasKeywordSegment" => Some(&ALIAS_KEYWORD_SEGMENT),
            "AliasedTableReferenceGrammar" => Some(&ALIASED_TABLE_REFERENCE_GRAMMAR),
            "AllKeywordSegment" => Some(&ALL_KEYWORD_SEGMENT),
            "AllocateKeywordSegment" => Some(&ALLOCATE_KEYWORD_SEGMENT),
            "AlsoKeywordSegment" => Some(&ALSO_KEYWORD_SEGMENT),
            "AlterKeywordSegment" => Some(&ALTER_KEYWORD_SEGMENT),
            "AlterSequenceOptionsSegment" => Some(&ALTER_SEQUENCE_OPTIONS_SEGMENT),
            "AlterSequenceStatementSegment" => Some(&ALTER_SEQUENCE_STATEMENT_SEGMENT),
            "AlterTableDropColumnGrammar" => Some(&ALTER_TABLE_DROP_COLUMN_GRAMMAR),
            "AlterTableOptionsGrammar" => Some(&ALTER_TABLE_OPTIONS_GRAMMAR),
            "AlterTableStatementSegment" => Some(&ALTER_TABLE_STATEMENT_SEGMENT),
            "AlwaysKeywordSegment" => Some(&ALWAYS_KEYWORD_SEGMENT),
            "AmpersandSegment" => Some(&AMPERSAND_SEGMENT),
            "AnalyseKeywordSegment" => Some(&ANALYSE_KEYWORD_SEGMENT),
            "AnalyzeKeywordSegment" => Some(&ANALYZE_KEYWORD_SEGMENT),
            "AndKeywordSegment" => Some(&AND_KEYWORD_SEGMENT),
            "AndOperatorGrammar" => Some(&AND_OPERATOR_GRAMMAR),
            "AnyKeywordSegment" => Some(&ANY_KEYWORD_SEGMENT),
            "ApplyKeywordSegment" => Some(&APPLY_KEYWORD_SEGMENT),
            "AreKeywordSegment" => Some(&ARE_KEYWORD_SEGMENT),
            "ArithmeticBinaryOperatorGrammar" => Some(&ARITHMETIC_BINARY_OPERATOR_GRAMMAR),
            "ArrayAccessorSegment" => Some(&ARRAY_ACCESSOR_SEGMENT),
            "ArrayExpressionSegment" => Some(&ARRAY_EXPRESSION_SEGMENT),
            "ArrayKeywordSegment" => Some(&ARRAY_KEYWORD_SEGMENT),
            "ArrayLiteralSegment" => Some(&ARRAY_LITERAL_SEGMENT),
            "ArrayTypeSegment" => Some(&ARRAY_TYPE_SEGMENT),
            "AsAliasOperatorSegment" => Some(&AS_ALIAS_OPERATOR_SEGMENT),
            "AsKeywordSegment" => Some(&AS_KEYWORD_SEGMENT),
            "AscKeywordSegment" => Some(&ASC_KEYWORD_SEGMENT),
            "AsensitiveKeywordSegment" => Some(&ASENSITIVE_KEYWORD_SEGMENT),
            "AssertionKeywordSegment" => Some(&ASSERTION_KEYWORD_SEGMENT),
            "AssignmentKeywordSegment" => Some(&ASSIGNMENT_KEYWORD_SEGMENT),
            "AsymmetricKeywordSegment" => Some(&ASYMMETRIC_KEYWORD_SEGMENT),
            "AtKeywordSegment" => Some(&AT_KEYWORD_SEGMENT),
            "AtomicKeywordSegment" => Some(&ATOMIC_KEYWORD_SEGMENT),
            "AttributeKeywordSegment" => Some(&ATTRIBUTE_KEYWORD_SEGMENT),
            "AttributesKeywordSegment" => Some(&ATTRIBUTES_KEYWORD_SEGMENT),
            "AuditKeywordSegment" => Some(&AUDIT_KEYWORD_SEGMENT),
            "AuthorizationKeywordSegment" => Some(&AUTHORIZATION_KEYWORD_SEGMENT),
            "AutoIncrementGrammar" => Some(&AUTO_INCREMENT_GRAMMAR),
            "Auto_incrementKeywordSegment" => Some(&AUTO_INCREMENT_KEYWORD_SEGMENT),
            "AvgKeywordSegment" => Some(&AVG_KEYWORD_SEGMENT),
            "Avg_row_lengthKeywordSegment" => Some(&AVG_ROW_LENGTH_KEYWORD_SEGMENT),
            "BackupKeywordSegment" => Some(&BACKUP_KEYWORD_SEGMENT),
            "BackwardKeywordSegment" => Some(&BACKWARD_KEYWORD_SEGMENT),
            "BareFunctionSegment" => Some(&BARE_FUNCTION_SEGMENT),
            "BaseExpressionElementGrammar" => Some(&BASE_EXPRESSION_ELEMENT_GRAMMAR),
            "BaseFileSegment" => Some(&BASE_FILE_SEGMENT),
            "BaseSegment" => Some(&BASE_SEGMENT),
            "BeforeKeywordSegment" => Some(&BEFORE_KEYWORD_SEGMENT),
            "BeginKeywordSegment" => Some(&BEGIN_KEYWORD_SEGMENT),
            "BernoulliKeywordSegment" => Some(&BERNOULLI_KEYWORD_SEGMENT),
            "BetweenKeywordSegment" => Some(&BETWEEN_KEYWORD_SEGMENT),
            "BigintKeywordSegment" => Some(&BIGINT_KEYWORD_SEGMENT),
            "BinaryKeywordSegment" => Some(&BINARY_KEYWORD_SEGMENT),
            "BinaryOperatorGrammar" => Some(&BINARY_OPERATOR_GRAMMAR),
            "BinaryOperatorSegment" => Some(&BINARY_OPERATOR_SEGMENT),
            "BindingKeywordSegment" => Some(&BINDING_KEYWORD_SEGMENT),
            "BitKeywordSegment" => Some(&BIT_KEYWORD_SEGMENT),
            "Bit_lengthKeywordSegment" => Some(&BIT_LENGTH_KEYWORD_SEGMENT),
            "BitvarKeywordSegment" => Some(&BITVAR_KEYWORD_SEGMENT),
            "BitwiseAndSegment" => Some(&BITWISE_AND_SEGMENT),
            "BitwiseLShiftSegment" => Some(&BITWISE_L_SHIFT_SEGMENT),
            "BitwiseOrSegment" => Some(&BITWISE_OR_SEGMENT),
            "BitwiseRShiftSegment" => Some(&BITWISE_R_SHIFT_SEGMENT),
            "BitwiseXorSegment" => Some(&BITWISE_XOR_SEGMENT),
            "BlobKeywordSegment" => Some(&BLOB_KEYWORD_SEGMENT),
            "BoolKeywordSegment" => Some(&BOOL_KEYWORD_SEGMENT),
            "BooleanBinaryOperatorGrammar" => Some(&BOOLEAN_BINARY_OPERATOR_GRAMMAR),
            "BooleanKeywordSegment" => Some(&BOOLEAN_KEYWORD_SEGMENT),
            "BooleanLiteralGrammar" => Some(&BOOLEAN_LITERAL_GRAMMAR),
            "BothKeywordSegment" => Some(&BOTH_KEYWORD_SEGMENT),
            "BracketedArguments" => Some(&BRACKETED_ARGUMENTS),
            "BracketedColumnReferenceListGrammar" => Some(&BRACKETED_COLUMN_REFERENCE_LIST_GRAMMAR),
            "BracketedSegment" => Some(&BRACKETED_SEGMENT),
            "BracketedSetExpressionGrammar" => Some(&BRACKETED_SET_EXPRESSION_GRAMMAR),
            "BreadthKeywordSegment" => Some(&BREADTH_KEYWORD_SEGMENT),
            "BreakKeywordSegment" => Some(&BREAK_KEYWORD_SEGMENT),
            "BrowseKeywordSegment" => Some(&BROWSE_KEYWORD_SEGMENT),
            "BulkKeywordSegment" => Some(&BULK_KEYWORD_SEGMENT),
            "ByKeywordSegment" => Some(&BY_KEYWORD_SEGMENT),
            "CTEColumnList" => Some(&C_T_E_COLUMN_LIST),
            "CTEDefinitionSegment" => Some(&C_T_E_DEFINITION_SEGMENT),
            "CacheKeywordSegment" => Some(&CACHE_KEYWORD_SEGMENT),
            "CallKeywordSegment" => Some(&CALL_KEYWORD_SEGMENT),
            "CalledKeywordSegment" => Some(&CALLED_KEYWORD_SEGMENT),
            "CardinalityKeywordSegment" => Some(&CARDINALITY_KEYWORD_SEGMENT),
            "CascadeKeywordSegment" => Some(&CASCADE_KEYWORD_SEGMENT),
            "CascadedKeywordSegment" => Some(&CASCADED_KEYWORD_SEGMENT),
            "CaseExpressionSegment" => Some(&CASE_EXPRESSION_SEGMENT),
            "CaseKeywordSegment" => Some(&CASE_KEYWORD_SEGMENT),
            "CastKeywordSegment" => Some(&CAST_KEYWORD_SEGMENT),
            "CastOperatorSegment" => Some(&CAST_OPERATOR_SEGMENT),
            "CatalogKeywordSegment" => Some(&CATALOG_KEYWORD_SEGMENT),
            "Catalog_nameKeywordSegment" => Some(&CATALOG_NAME_KEYWORD_SEGMENT),
            "CeilKeywordSegment" => Some(&CEIL_KEYWORD_SEGMENT),
            "CeilingKeywordSegment" => Some(&CEILING_KEYWORD_SEGMENT),
            "ChainKeywordSegment" => Some(&CHAIN_KEYWORD_SEGMENT),
            "ChangeKeywordSegment" => Some(&CHANGE_KEYWORD_SEGMENT),
            "CharCharacterSetGrammar" => Some(&CHAR_CHARACTER_SET_GRAMMAR),
            "CharKeywordSegment" => Some(&CHAR_KEYWORD_SEGMENT),
            "Char_lengthKeywordSegment" => Some(&CHAR_LENGTH_KEYWORD_SEGMENT),
            "CharacterKeywordSegment" => Some(&CHARACTER_KEYWORD_SEGMENT),
            "Character_lengthKeywordSegment" => Some(&CHARACTER_LENGTH_KEYWORD_SEGMENT),
            "Character_set_catalogKeywordSegment" => Some(&CHARACTER_SET_CATALOG_KEYWORD_SEGMENT),
            "Character_set_nameKeywordSegment" => Some(&CHARACTER_SET_NAME_KEYWORD_SEGMENT),
            "Character_set_schemaKeywordSegment" => Some(&CHARACTER_SET_SCHEMA_KEYWORD_SEGMENT),
            "CharacteristicsKeywordSegment" => Some(&CHARACTERISTICS_KEYWORD_SEGMENT),
            "CharactersKeywordSegment" => Some(&CHARACTERS_KEYWORD_SEGMENT),
            "CheckKeywordSegment" => Some(&CHECK_KEYWORD_SEGMENT),
            "CheckedKeywordSegment" => Some(&CHECKED_KEYWORD_SEGMENT),
            "CheckpointKeywordSegment" => Some(&CHECKPOINT_KEYWORD_SEGMENT),
            "ChecksumKeywordSegment" => Some(&CHECKSUM_KEYWORD_SEGMENT),
            "ClassKeywordSegment" => Some(&CLASS_KEYWORD_SEGMENT),
            "Class_originKeywordSegment" => Some(&CLASS_ORIGIN_KEYWORD_SEGMENT),
            "ClobKeywordSegment" => Some(&CLOB_KEYWORD_SEGMENT),
            "CloseKeywordSegment" => Some(&CLOSE_KEYWORD_SEGMENT),
            "ClusterKeywordSegment" => Some(&CLUSTER_KEYWORD_SEGMENT),
            "ClusteredKeywordSegment" => Some(&CLUSTERED_KEYWORD_SEGMENT),
            "CoalesceKeywordSegment" => Some(&COALESCE_KEYWORD_SEGMENT),
            "CobolKeywordSegment" => Some(&COBOL_KEYWORD_SEGMENT),
            "CodeSegment" => Some(&CODE_SEGMENT),
            "CollateGrammar" => Some(&COLLATE_GRAMMAR),
            "CollateKeywordSegment" => Some(&COLLATE_KEYWORD_SEGMENT),
            "CollationKeywordSegment" => Some(&COLLATION_KEYWORD_SEGMENT),
            "CollationReferenceSegment" => Some(&COLLATION_REFERENCE_SEGMENT),
            "Collation_catalogKeywordSegment" => Some(&COLLATION_CATALOG_KEYWORD_SEGMENT),
            "Collation_nameKeywordSegment" => Some(&COLLATION_NAME_KEYWORD_SEGMENT),
            "Collation_schemaKeywordSegment" => Some(&COLLATION_SCHEMA_KEYWORD_SEGMENT),
            "CollectKeywordSegment" => Some(&COLLECT_KEYWORD_SEGMENT),
            "ColonDelimiterSegment" => Some(&COLON_DELIMITER_SEGMENT),
            "ColonPrefixSegment" => Some(&COLON_PREFIX_SEGMENT),
            "ColonSegment" => Some(&COLON_SEGMENT),
            "ColumnConstraintDefaultGrammar" => Some(&COLUMN_CONSTRAINT_DEFAULT_GRAMMAR),
            "ColumnConstraintSegment" => Some(&COLUMN_CONSTRAINT_SEGMENT),
            "ColumnDefinitionSegment" => Some(&COLUMN_DEFINITION_SEGMENT),
            "ColumnGeneratedGrammar" => Some(&COLUMN_GENERATED_GRAMMAR),
            "ColumnKeywordSegment" => Some(&COLUMN_KEYWORD_SEGMENT),
            "ColumnReferenceSegment" => Some(&COLUMN_REFERENCE_SEGMENT),
            "Column_nameKeywordSegment" => Some(&COLUMN_NAME_KEYWORD_SEGMENT),
            "ColumnsExpressionFunctionContentsSegment" => Some(&COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT),
            "ColumnsExpressionFunctionNameSegment" => Some(&COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT),
            "ColumnsExpressionGrammar" => Some(&COLUMNS_EXPRESSION_GRAMMAR),
            "ColumnsExpressionNameGrammar" => Some(&COLUMNS_EXPRESSION_NAME_GRAMMAR),
            "ColumnsKeywordSegment" => Some(&COLUMNS_KEYWORD_SEGMENT),
            "CommaSegment" => Some(&COMMA_SEGMENT),
            "Command_functionKeywordSegment" => Some(&COMMAND_FUNCTION_KEYWORD_SEGMENT),
            "Command_function_codeKeywordSegment" => Some(&COMMAND_FUNCTION_CODE_KEYWORD_SEGMENT),
            "CommentClauseSegment" => Some(&COMMENT_CLAUSE_SEGMENT),
            "CommentKeywordSegment" => Some(&COMMENT_KEYWORD_SEGMENT),
            "CommentSegment" => Some(&COMMENT_SEGMENT),
            "CommitKeywordSegment" => Some(&COMMIT_KEYWORD_SEGMENT),
            "CommittedKeywordSegment" => Some(&COMMITTED_KEYWORD_SEGMENT),
            "ComparisonOperatorGrammar" => Some(&COMPARISON_OPERATOR_GRAMMAR),
            "ComparisonOperatorSegment" => Some(&COMPARISON_OPERATOR_SEGMENT),
            "CompletionKeywordSegment" => Some(&COMPLETION_KEYWORD_SEGMENT),
            "CompositeBinaryOperatorSegment" => Some(&COMPOSITE_BINARY_OPERATOR_SEGMENT),
            "CompositeComparisonOperatorSegment" => Some(&COMPOSITE_COMPARISON_OPERATOR_SEGMENT),
            "CompressKeywordSegment" => Some(&COMPRESS_KEYWORD_SEGMENT),
            "ComputeKeywordSegment" => Some(&COMPUTE_KEYWORD_SEGMENT),
            "ConcatSegment" => Some(&CONCAT_SEGMENT),
            "ConditionKeywordSegment" => Some(&CONDITION_KEYWORD_SEGMENT),
            "Condition_numberKeywordSegment" => Some(&CONDITION_NUMBER_KEYWORD_SEGMENT),
            "ConditionalCrossJoinKeywordsGrammar" => Some(&CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR),
            "ConditionalJoinKeywordsGrammar" => Some(&CONDITIONAL_JOIN_KEYWORDS_GRAMMAR),
            "ConnectKeywordSegment" => Some(&CONNECT_KEYWORD_SEGMENT),
            "ConnectionKeywordSegment" => Some(&CONNECTION_KEYWORD_SEGMENT),
            "Connection_nameKeywordSegment" => Some(&CONNECTION_NAME_KEYWORD_SEGMENT),
            "ConstraintKeywordSegment" => Some(&CONSTRAINT_KEYWORD_SEGMENT),
            "Constraint_catalogKeywordSegment" => Some(&CONSTRAINT_CATALOG_KEYWORD_SEGMENT),
            "Constraint_nameKeywordSegment" => Some(&CONSTRAINT_NAME_KEYWORD_SEGMENT),
            "Constraint_schemaKeywordSegment" => Some(&CONSTRAINT_SCHEMA_KEYWORD_SEGMENT),
            "ConstraintsKeywordSegment" => Some(&CONSTRAINTS_KEYWORD_SEGMENT),
            "ConstructorKeywordSegment" => Some(&CONSTRUCTOR_KEYWORD_SEGMENT),
            "ContainsKeywordSegment" => Some(&CONTAINS_KEYWORD_SEGMENT),
            "ContainstableKeywordSegment" => Some(&CONTAINSTABLE_KEYWORD_SEGMENT),
            "ContinueKeywordSegment" => Some(&CONTINUE_KEYWORD_SEGMENT),
            "ConversionKeywordSegment" => Some(&CONVERSION_KEYWORD_SEGMENT),
            "ConvertKeywordSegment" => Some(&CONVERT_KEYWORD_SEGMENT),
            "CopyKeywordSegment" => Some(&COPY_KEYWORD_SEGMENT),
            "CorrKeywordSegment" => Some(&CORR_KEYWORD_SEGMENT),
            "CorrespondingKeywordSegment" => Some(&CORRESPONDING_KEYWORD_SEGMENT),
            "CountKeywordSegment" => Some(&COUNT_KEYWORD_SEGMENT),
            "Covar_popKeywordSegment" => Some(&COVAR_POP_KEYWORD_SEGMENT),
            "Covar_sampKeywordSegment" => Some(&COVAR_SAMP_KEYWORD_SEGMENT),
            "CreateCastStatementSegment" => Some(&CREATE_CAST_STATEMENT_SEGMENT),
            "CreateDatabaseStatementSegment" => Some(&CREATE_DATABASE_STATEMENT_SEGMENT),
            "CreateFunctionStatementSegment" => Some(&CREATE_FUNCTION_STATEMENT_SEGMENT),
            "CreateIndexStatementSegment" => Some(&CREATE_INDEX_STATEMENT_SEGMENT),
            "CreateKeywordSegment" => Some(&CREATE_KEYWORD_SEGMENT),
            "CreateModelStatementSegment" => Some(&CREATE_MODEL_STATEMENT_SEGMENT),
            "CreateRoleStatementSegment" => Some(&CREATE_ROLE_STATEMENT_SEGMENT),
            "CreateSchemaStatementSegment" => Some(&CREATE_SCHEMA_STATEMENT_SEGMENT),
            "CreateSequenceOptionsSegment" => Some(&CREATE_SEQUENCE_OPTIONS_SEGMENT),
            "CreateSequenceStatementSegment" => Some(&CREATE_SEQUENCE_STATEMENT_SEGMENT),
            "CreateTableStatementSegment" => Some(&CREATE_TABLE_STATEMENT_SEGMENT),
            "CreateTriggerStatementSegment" => Some(&CREATE_TRIGGER_STATEMENT_SEGMENT),
            "CreateUserStatementSegment" => Some(&CREATE_USER_STATEMENT_SEGMENT),
            "CreateViewStatementSegment" => Some(&CREATE_VIEW_STATEMENT_SEGMENT),
            "CreatedbKeywordSegment" => Some(&CREATEDB_KEYWORD_SEGMENT),
            "CreateroleKeywordSegment" => Some(&CREATEROLE_KEYWORD_SEGMENT),
            "CreateuserKeywordSegment" => Some(&CREATEUSER_KEYWORD_SEGMENT),
            "CrossKeywordSegment" => Some(&CROSS_KEYWORD_SEGMENT),
            "CsvKeywordSegment" => Some(&CSV_KEYWORD_SEGMENT),
            "CubeFunctionNameSegment" => Some(&CUBE_FUNCTION_NAME_SEGMENT),
            "CubeKeywordSegment" => Some(&CUBE_KEYWORD_SEGMENT),
            "CubeRollupClauseSegment" => Some(&CUBE_ROLLUP_CLAUSE_SEGMENT),
            "Cume_distKeywordSegment" => Some(&CUME_DIST_KEYWORD_SEGMENT),
            "CurrentKeywordSegment" => Some(&CURRENT_KEYWORD_SEGMENT),
            "Current_dateKeywordSegment" => Some(&CURRENT_DATE_KEYWORD_SEGMENT),
            "Current_default_transform_groupKeywordSegment" => Some(&CURRENT_DEFAULT_TRANSFORM_GROUP_KEYWORD_SEGMENT),
            "Current_pathKeywordSegment" => Some(&CURRENT_PATH_KEYWORD_SEGMENT),
            "Current_roleKeywordSegment" => Some(&CURRENT_ROLE_KEYWORD_SEGMENT),
            "Current_timeKeywordSegment" => Some(&CURRENT_TIME_KEYWORD_SEGMENT),
            "Current_timestampKeywordSegment" => Some(&CURRENT_TIMESTAMP_KEYWORD_SEGMENT),
            "Current_transform_group_for_typeKeywordSegment" => Some(&CURRENT_TRANSFORM_GROUP_FOR_TYPE_KEYWORD_SEGMENT),
            "Current_userKeywordSegment" => Some(&CURRENT_USER_KEYWORD_SEGMENT),
            "CursorKeywordSegment" => Some(&CURSOR_KEYWORD_SEGMENT),
            "Cursor_nameKeywordSegment" => Some(&CURSOR_NAME_KEYWORD_SEGMENT),
            "CycleKeywordSegment" => Some(&CYCLE_KEYWORD_SEGMENT),
            "DataKeywordSegment" => Some(&DATA_KEYWORD_SEGMENT),
            "DatabaseKeywordSegment" => Some(&DATABASE_KEYWORD_SEGMENT),
            "DatabaseReferenceSegment" => Some(&DATABASE_REFERENCE_SEGMENT),
            "DatabasesKeywordSegment" => Some(&DATABASES_KEYWORD_SEGMENT),
            "DatatypeIdentifierSegment" => Some(&DATATYPE_IDENTIFIER_SEGMENT),
            "DatatypeSegment" => Some(&DATATYPE_SEGMENT),
            "DateKeywordSegment" => Some(&DATE_KEYWORD_SEGMENT),
            "DatePartFunctionName" => Some(&DATE_PART_FUNCTION_NAME),
            "DatePartFunctionNameSegment" => Some(&DATE_PART_FUNCTION_NAME_SEGMENT),
            "DateTimeFunctionContentsSegment" => Some(&DATE_TIME_FUNCTION_CONTENTS_SEGMENT),
            "DateTimeLiteralGrammar" => Some(&DATE_TIME_LITERAL_GRAMMAR),
            "DatetimeKeywordSegment" => Some(&DATETIME_KEYWORD_SEGMENT),
            "DatetimeUnitSegment" => Some(&DATETIME_UNIT_SEGMENT),
            "Datetime_interval_codeKeywordSegment" => Some(&DATETIME_INTERVAL_CODE_KEYWORD_SEGMENT),
            "Datetime_interval_precisionKeywordSegment" => Some(&DATETIME_INTERVAL_PRECISION_KEYWORD_SEGMENT),
            "DayKeywordSegment" => Some(&DAY_KEYWORD_SEGMENT),
            "Day_hourKeywordSegment" => Some(&DAY_HOUR_KEYWORD_SEGMENT),
            "Day_microsecondKeywordSegment" => Some(&DAY_MICROSECOND_KEYWORD_SEGMENT),
            "Day_minuteKeywordSegment" => Some(&DAY_MINUTE_KEYWORD_SEGMENT),
            "Day_secondKeywordSegment" => Some(&DAY_SECOND_KEYWORD_SEGMENT),
            "DayofmonthKeywordSegment" => Some(&DAYOFMONTH_KEYWORD_SEGMENT),
            "DayofweekKeywordSegment" => Some(&DAYOFWEEK_KEYWORD_SEGMENT),
            "DayofyearKeywordSegment" => Some(&DAYOFYEAR_KEYWORD_SEGMENT),
            "DaysKeywordSegment" => Some(&DAYS_KEYWORD_SEGMENT),
            "DbccKeywordSegment" => Some(&DBCC_KEYWORD_SEGMENT),
            "DeallocateKeywordSegment" => Some(&DEALLOCATE_KEYWORD_SEGMENT),
            "DecKeywordSegment" => Some(&DEC_KEYWORD_SEGMENT),
            "DecimalKeywordSegment" => Some(&DECIMAL_KEYWORD_SEGMENT),
            "DeclareKeywordSegment" => Some(&DECLARE_KEYWORD_SEGMENT),
            "Dedent" => Some(&DEDENT),
            "DefaultKeywordSegment" => Some(&DEFAULT_KEYWORD_SEGMENT),
            "DefaultValuesGrammar" => Some(&DEFAULT_VALUES_GRAMMAR),
            "DefaultsKeywordSegment" => Some(&DEFAULTS_KEYWORD_SEGMENT),
            "DeferrableKeywordSegment" => Some(&DEFERRABLE_KEYWORD_SEGMENT),
            "DeferredKeywordSegment" => Some(&DEFERRED_KEYWORD_SEGMENT),
            "DefinedKeywordSegment" => Some(&DEFINED_KEYWORD_SEGMENT),
            "DefinerKeywordSegment" => Some(&DEFINER_KEYWORD_SEGMENT),
            "DegreeKeywordSegment" => Some(&DEGREE_KEYWORD_SEGMENT),
            "Delay_key_writeKeywordSegment" => Some(&DELAY_KEY_WRITE_KEYWORD_SEGMENT),
            "DelayedKeywordSegment" => Some(&DELAYED_KEYWORD_SEGMENT),
            "DeleteKeywordSegment" => Some(&DELETE_KEYWORD_SEGMENT),
            "DeleteStatementSegment" => Some(&DELETE_STATEMENT_SEGMENT),
            "DelimiterGrammar" => Some(&DELIMITER_GRAMMAR),
            "DelimiterKeywordSegment" => Some(&DELIMITER_KEYWORD_SEGMENT),
            "DelimitersKeywordSegment" => Some(&DELIMITERS_KEYWORD_SEGMENT),
            "Dense_rankKeywordSegment" => Some(&DENSE_RANK_KEYWORD_SEGMENT),
            "DenyKeywordSegment" => Some(&DENY_KEYWORD_SEGMENT),
            "DepthKeywordSegment" => Some(&DEPTH_KEYWORD_SEGMENT),
            "DerefKeywordSegment" => Some(&DEREF_KEYWORD_SEGMENT),
            "DerivedKeywordSegment" => Some(&DERIVED_KEYWORD_SEGMENT),
            "DescKeywordSegment" => Some(&DESC_KEYWORD_SEGMENT),
            "DescribeKeywordSegment" => Some(&DESCRIBE_KEYWORD_SEGMENT),
            "DescribeStatementSegment" => Some(&DESCRIBE_STATEMENT_SEGMENT),
            "DescriptorKeywordSegment" => Some(&DESCRIPTOR_KEYWORD_SEGMENT),
            "DestroyKeywordSegment" => Some(&DESTROY_KEYWORD_SEGMENT),
            "DestructorKeywordSegment" => Some(&DESTRUCTOR_KEYWORD_SEGMENT),
            "DeterministicKeywordSegment" => Some(&DETERMINISTIC_KEYWORD_SEGMENT),
            "DiagnosticsKeywordSegment" => Some(&DIAGNOSTICS_KEYWORD_SEGMENT),
            "DictionaryKeywordSegment" => Some(&DICTIONARY_KEYWORD_SEGMENT),
            "DisableKeywordSegment" => Some(&DISABLE_KEYWORD_SEGMENT),
            "DisconnectKeywordSegment" => Some(&DISCONNECT_KEYWORD_SEGMENT),
            "DiskKeywordSegment" => Some(&DISK_KEYWORD_SEGMENT),
            "DispatchKeywordSegment" => Some(&DISPATCH_KEYWORD_SEGMENT),
            "DistinctKeywordSegment" => Some(&DISTINCT_KEYWORD_SEGMENT),
            "DistinctrowKeywordSegment" => Some(&DISTINCTROW_KEYWORD_SEGMENT),
            "DistributedKeywordSegment" => Some(&DISTRIBUTED_KEYWORD_SEGMENT),
            "DivKeywordSegment" => Some(&DIV_KEYWORD_SEGMENT),
            "DivideSegment" => Some(&DIVIDE_SEGMENT),
            "DoKeywordSegment" => Some(&DO_KEYWORD_SEGMENT),
            "DomainKeywordSegment" => Some(&DOMAIN_KEYWORD_SEGMENT),
            "DotSegment" => Some(&DOT_SEGMENT),
            "DoubleKeywordSegment" => Some(&DOUBLE_KEYWORD_SEGMENT),
            "DropBehaviorGrammar" => Some(&DROP_BEHAVIOR_GRAMMAR),
            "DropCastStatementSegment" => Some(&DROP_CAST_STATEMENT_SEGMENT),
            "DropDatabaseStatementSegment" => Some(&DROP_DATABASE_STATEMENT_SEGMENT),
            "DropFunctionStatementSegment" => Some(&DROP_FUNCTION_STATEMENT_SEGMENT),
            "DropIndexStatementSegment" => Some(&DROP_INDEX_STATEMENT_SEGMENT),
            "DropKeywordSegment" => Some(&DROP_KEYWORD_SEGMENT),
            "DropModelStatementSegment" => Some(&DROP_MODEL_STATEMENT_SEGMENT),
            "DropRoleStatementSegment" => Some(&DROP_ROLE_STATEMENT_SEGMENT),
            "DropSchemaStatementSegment" => Some(&DROP_SCHEMA_STATEMENT_SEGMENT),
            "DropSequenceStatementSegment" => Some(&DROP_SEQUENCE_STATEMENT_SEGMENT),
            "DropTableStatementSegment" => Some(&DROP_TABLE_STATEMENT_SEGMENT),
            "DropTriggerStatementSegment" => Some(&DROP_TRIGGER_STATEMENT_SEGMENT),
            "DropTypeStatementSegment" => Some(&DROP_TYPE_STATEMENT_SEGMENT),
            "DropUserStatementSegment" => Some(&DROP_USER_STATEMENT_SEGMENT),
            "DropViewStatementSegment" => Some(&DROP_VIEW_STATEMENT_SEGMENT),
            "DummyKeywordSegment" => Some(&DUMMY_KEYWORD_SEGMENT),
            "DumpKeywordSegment" => Some(&DUMP_KEYWORD_SEGMENT),
            "DynamicKeywordSegment" => Some(&DYNAMIC_KEYWORD_SEGMENT),
            "Dynamic_functionKeywordSegment" => Some(&DYNAMIC_FUNCTION_KEYWORD_SEGMENT),
            "Dynamic_function_codeKeywordSegment" => Some(&DYNAMIC_FUNCTION_CODE_KEYWORD_SEGMENT),
            "EachKeywordSegment" => Some(&EACH_KEYWORD_SEGMENT),
            "ElementKeywordSegment" => Some(&ELEMENT_KEYWORD_SEGMENT),
            "ElseClauseSegment" => Some(&ELSE_CLAUSE_SEGMENT),
            "ElseKeywordSegment" => Some(&ELSE_KEYWORD_SEGMENT),
            "ElseifKeywordSegment" => Some(&ELSEIF_KEYWORD_SEGMENT),
            "EmptyStructLiteralBracketsSegment" => Some(&EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT),
            "EmptyStructLiteralSegment" => Some(&EMPTY_STRUCT_LITERAL_SEGMENT),
            "EnableKeywordSegment" => Some(&ENABLE_KEYWORD_SEGMENT),
            "EnclosedKeywordSegment" => Some(&ENCLOSED_KEYWORD_SEGMENT),
            "EncodingKeywordSegment" => Some(&ENCODING_KEYWORD_SEGMENT),
            "EncryptedKeywordSegment" => Some(&ENCRYPTED_KEYWORD_SEGMENT),
            "End-execKeywordSegment" => Some(&END_EXEC_KEYWORD_SEGMENT),
            "EndBracketSegment" => Some(&END_BRACKET_SEGMENT),
            "EndCurlyBracketSegment" => Some(&END_CURLY_BRACKET_SEGMENT),
            "EndKeywordSegment" => Some(&END_KEYWORD_SEGMENT),
            "EndSquareBracketSegment" => Some(&END_SQUARE_BRACKET_SEGMENT),
            "EnumKeywordSegment" => Some(&ENUM_KEYWORD_SEGMENT),
            "EqualsKeywordSegment" => Some(&EQUALS_KEYWORD_SEGMENT),
            "EqualsSegment" => Some(&EQUALS_SEGMENT),
            "ErrlvlKeywordSegment" => Some(&ERRLVL_KEYWORD_SEGMENT),
            "EscapeKeywordSegment" => Some(&ESCAPE_KEYWORD_SEGMENT),
            "EscapedKeywordSegment" => Some(&ESCAPED_KEYWORD_SEGMENT),
            "EveryKeywordSegment" => Some(&EVERY_KEYWORD_SEGMENT),
            "ExceptKeywordSegment" => Some(&EXCEPT_KEYWORD_SEGMENT),
            "ExceptionKeywordSegment" => Some(&EXCEPTION_KEYWORD_SEGMENT),
            "ExcludeKeywordSegment" => Some(&EXCLUDE_KEYWORD_SEGMENT),
            "ExcludingKeywordSegment" => Some(&EXCLUDING_KEYWORD_SEGMENT),
            "ExclusiveKeywordSegment" => Some(&EXCLUSIVE_KEYWORD_SEGMENT),
            "ExecKeywordSegment" => Some(&EXEC_KEYWORD_SEGMENT),
            "ExecuteKeywordSegment" => Some(&EXECUTE_KEYWORD_SEGMENT),
            "ExecutionKeywordSegment" => Some(&EXECUTION_KEYWORD_SEGMENT),
            "ExistingKeywordSegment" => Some(&EXISTING_KEYWORD_SEGMENT),
            "ExistsKeywordSegment" => Some(&EXISTS_KEYWORD_SEGMENT),
            "ExitKeywordSegment" => Some(&EXIT_KEYWORD_SEGMENT),
            "ExpKeywordSegment" => Some(&EXP_KEYWORD_SEGMENT),
            "ExplainKeywordSegment" => Some(&EXPLAIN_KEYWORD_SEGMENT),
            "ExplainStatementSegment" => Some(&EXPLAIN_STATEMENT_SEGMENT),
            "ExpressionSegment" => Some(&EXPRESSION_SEGMENT),
            "Expression_A_Grammar" => Some(&EXPRESSION_A_GRAMMAR),
            "Expression_A_Unary_Operator_Grammar" => Some(&EXPRESSION_A_UNARY_OPERATOR_GRAMMAR),
            "Expression_B_Grammar" => Some(&EXPRESSION_B_GRAMMAR),
            "Expression_B_Unary_Operator_Grammar" => Some(&EXPRESSION_B_UNARY_OPERATOR_GRAMMAR),
            "Expression_C_Grammar" => Some(&EXPRESSION_C_GRAMMAR),
            "Expression_D_Grammar" => Some(&EXPRESSION_D_GRAMMAR),
            "Expression_D_Potential_Select_Statement_Without_Brackets" => Some(&EXPRESSION_D_POTENTIAL_SELECT_STATEMENT_WITHOUT_BRACKETS),
            "ExtendedNaturalJoinKeywordsGrammar" => Some(&EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR),
            "ExtensionKeywordSegment" => Some(&EXTENSION_KEYWORD_SEGMENT),
            "ExtensionReferenceSegment" => Some(&EXTENSION_REFERENCE_SEGMENT),
            "ExternalKeywordSegment" => Some(&EXTERNAL_KEYWORD_SEGMENT),
            "ExtractKeywordSegment" => Some(&EXTRACT_KEYWORD_SEGMENT),
            "FalseKeywordSegment" => Some(&FALSE_KEYWORD_SEGMENT),
            "FalseSegment" => Some(&FALSE_SEGMENT),
            "FetchClauseSegment" => Some(&FETCH_CLAUSE_SEGMENT),
            "FetchKeywordSegment" => Some(&FETCH_KEYWORD_SEGMENT),
            "FieldsKeywordSegment" => Some(&FIELDS_KEYWORD_SEGMENT),
            "FileKeywordSegment" => Some(&FILE_KEYWORD_SEGMENT),
            "FileSegment" => Some(&FILE_SEGMENT),
            "FillfactorKeywordSegment" => Some(&FILLFACTOR_KEYWORD_SEGMENT),
            "FilterClauseGrammar" => Some(&FILTER_CLAUSE_GRAMMAR),
            "FilterKeywordSegment" => Some(&FILTER_KEYWORD_SEGMENT),
            "FinalKeywordSegment" => Some(&FINAL_KEYWORD_SEGMENT),
            "FirstKeywordSegment" => Some(&FIRST_KEYWORD_SEGMENT),
            "Float4KeywordSegment" => Some(&FLOAT4_KEYWORD_SEGMENT),
            "Float8KeywordSegment" => Some(&FLOAT8_KEYWORD_SEGMENT),
            "FloatKeywordSegment" => Some(&FLOAT_KEYWORD_SEGMENT),
            "FloorKeywordSegment" => Some(&FLOOR_KEYWORD_SEGMENT),
            "FlushKeywordSegment" => Some(&FLUSH_KEYWORD_SEGMENT),
            "FollowingKeywordSegment" => Some(&FOLLOWING_KEYWORD_SEGMENT),
            "ForKeywordSegment" => Some(&FOR_KEYWORD_SEGMENT),
            "ForceKeywordSegment" => Some(&FORCE_KEYWORD_SEGMENT),
            "ForeignKeyGrammar" => Some(&FOREIGN_KEY_GRAMMAR),
            "ForeignKeywordSegment" => Some(&FOREIGN_KEYWORD_SEGMENT),
            "FormatKeywordSegment" => Some(&FORMAT_KEYWORD_SEGMENT),
            "FortranKeywordSegment" => Some(&FORTRAN_KEYWORD_SEGMENT),
            "ForwardKeywordSegment" => Some(&FORWARD_KEYWORD_SEGMENT),
            "FoundKeywordSegment" => Some(&FOUND_KEYWORD_SEGMENT),
            "FrameClauseSegment" => Some(&FRAME_CLAUSE_SEGMENT),
            "FrameClauseUnitGrammar" => Some(&FRAME_CLAUSE_UNIT_GRAMMAR),
            "FreeKeywordSegment" => Some(&FREE_KEYWORD_SEGMENT),
            "FreetextKeywordSegment" => Some(&FREETEXT_KEYWORD_SEGMENT),
            "FreetexttableKeywordSegment" => Some(&FREETEXTTABLE_KEYWORD_SEGMENT),
            "FreezeKeywordSegment" => Some(&FREEZE_KEYWORD_SEGMENT),
            "FromClauseSegment" => Some(&FROM_CLAUSE_SEGMENT),
            "FromClauseTerminatorGrammar" => Some(&FROM_CLAUSE_TERMINATOR_GRAMMAR),
            "FromExpressionElementSegment" => Some(&FROM_EXPRESSION_ELEMENT_SEGMENT),
            "FromExpressionSegment" => Some(&FROM_EXPRESSION_SEGMENT),
            "FromKeywordSegment" => Some(&FROM_KEYWORD_SEGMENT),
            "FullKeywordSegment" => Some(&FULL_KEYWORD_SEGMENT),
            "FulltextKeywordSegment" => Some(&FULLTEXT_KEYWORD_SEGMENT),
            "FunctionContentsExpressionGrammar" => Some(&FUNCTION_CONTENTS_EXPRESSION_GRAMMAR),
            "FunctionContentsGrammar" => Some(&FUNCTION_CONTENTS_GRAMMAR),
            "FunctionContentsSegment" => Some(&FUNCTION_CONTENTS_SEGMENT),
            "FunctionDefinitionGrammar" => Some(&FUNCTION_DEFINITION_GRAMMAR),
            "FunctionKeywordSegment" => Some(&FUNCTION_KEYWORD_SEGMENT),
            "FunctionNameIdentifierSegment" => Some(&FUNCTION_NAME_IDENTIFIER_SEGMENT),
            "FunctionNameSegment" => Some(&FUNCTION_NAME_SEGMENT),
            "FunctionParameterGrammar" => Some(&FUNCTION_PARAMETER_GRAMMAR),
            "FunctionParameterListGrammar" => Some(&FUNCTION_PARAMETER_LIST_GRAMMAR),
            "FunctionSegment" => Some(&FUNCTION_SEGMENT),
            "FunctionsKeywordSegment" => Some(&FUNCTIONS_KEYWORD_SEGMENT),
            "FusionKeywordSegment" => Some(&FUSION_KEYWORD_SEGMENT),
            "FutureKeywordSegment" => Some(&FUTURE_KEYWORD_SEGMENT),
            "GKeywordSegment" => Some(&G_KEYWORD_SEGMENT),
            "GeneralKeywordSegment" => Some(&GENERAL_KEYWORD_SEGMENT),
            "GeneratedKeywordSegment" => Some(&GENERATED_KEYWORD_SEGMENT),
            "GetKeywordSegment" => Some(&GET_KEYWORD_SEGMENT),
            "GlobOperatorSegment" => Some(&GLOB_OPERATOR_SEGMENT),
            "GlobalKeywordSegment" => Some(&GLOBAL_KEYWORD_SEGMENT),
            "GoKeywordSegment" => Some(&GO_KEYWORD_SEGMENT),
            "GotoKeywordSegment" => Some(&GOTO_KEYWORD_SEGMENT),
            "GrantKeywordSegment" => Some(&GRANT_KEYWORD_SEGMENT),
            "GrantedKeywordSegment" => Some(&GRANTED_KEYWORD_SEGMENT),
            "GrantsKeywordSegment" => Some(&GRANTS_KEYWORD_SEGMENT),
            "GreaterThanOrEqualToSegment" => Some(&GREATER_THAN_OR_EQUAL_TO_SEGMENT),
            "GreaterThanSegment" => Some(&GREATER_THAN_SEGMENT),
            "GreatestKeywordSegment" => Some(&GREATEST_KEYWORD_SEGMENT),
            "GroupByClauseSegment" => Some(&GROUP_BY_CLAUSE_SEGMENT),
            "GroupByClauseTerminatorGrammar" => Some(&GROUP_BY_CLAUSE_TERMINATOR_GRAMMAR),
            "GroupKeywordSegment" => Some(&GROUP_KEYWORD_SEGMENT),
            "GroupingExpressionList" => Some(&GROUPING_EXPRESSION_LIST),
            "GroupingKeywordSegment" => Some(&GROUPING_KEYWORD_SEGMENT),
            "GroupingSetsClauseSegment" => Some(&GROUPING_SETS_CLAUSE_SEGMENT),
            "HandlerKeywordSegment" => Some(&HANDLER_KEYWORD_SEGMENT),
            "HavingClauseSegment" => Some(&HAVING_CLAUSE_SEGMENT),
            "HavingClauseTerminatorGrammar" => Some(&HAVING_CLAUSE_TERMINATOR_GRAMMAR),
            "HavingKeywordSegment" => Some(&HAVING_KEYWORD_SEGMENT),
            "HeaderKeywordSegment" => Some(&HEADER_KEYWORD_SEGMENT),
            "HeapKeywordSegment" => Some(&HEAP_KEYWORD_SEGMENT),
            "HierarchyKeywordSegment" => Some(&HIERARCHY_KEYWORD_SEGMENT),
            "High_priorityKeywordSegment" => Some(&HIGH_PRIORITY_KEYWORD_SEGMENT),
            "HoldKeywordSegment" => Some(&HOLD_KEYWORD_SEGMENT),
            "HoldlockKeywordSegment" => Some(&HOLDLOCK_KEYWORD_SEGMENT),
            "HorizontalJoinKeywordsGrammar" => Some(&HORIZONTAL_JOIN_KEYWORDS_GRAMMAR),
            "HostKeywordSegment" => Some(&HOST_KEYWORD_SEGMENT),
            "HostsKeywordSegment" => Some(&HOSTS_KEYWORD_SEGMENT),
            "HourKeywordSegment" => Some(&HOUR_KEYWORD_SEGMENT),
            "Hour_microsecondKeywordSegment" => Some(&HOUR_MICROSECOND_KEYWORD_SEGMENT),
            "Hour_minuteKeywordSegment" => Some(&HOUR_MINUTE_KEYWORD_SEGMENT),
            "Hour_secondKeywordSegment" => Some(&HOUR_SECOND_KEYWORD_SEGMENT),
            "IdentifiedKeywordSegment" => Some(&IDENTIFIED_KEYWORD_SEGMENT),
            "IdentifierSegment" => Some(&IDENTIFIER_SEGMENT),
            "IdentityKeywordSegment" => Some(&IDENTITY_KEYWORD_SEGMENT),
            "Identity_insertKeywordSegment" => Some(&IDENTITY_INSERT_KEYWORD_SEGMENT),
            "IdentitycolKeywordSegment" => Some(&IDENTITYCOL_KEYWORD_SEGMENT),
            "IfExistsGrammar" => Some(&IF_EXISTS_GRAMMAR),
            "IfKeywordSegment" => Some(&IF_KEYWORD_SEGMENT),
            "IfNotExistsGrammar" => Some(&IF_NOT_EXISTS_GRAMMAR),
            "IgnoreKeywordSegment" => Some(&IGNORE_KEYWORD_SEGMENT),
            "IgnoreRespectNullsGrammar" => Some(&IGNORE_RESPECT_NULLS_GRAMMAR),
            "IlikeKeywordSegment" => Some(&ILIKE_KEYWORD_SEGMENT),
            "ImmediateKeywordSegment" => Some(&IMMEDIATE_KEYWORD_SEGMENT),
            "ImmutableKeywordSegment" => Some(&IMMUTABLE_KEYWORD_SEGMENT),
            "ImplementationKeywordSegment" => Some(&IMPLEMENTATION_KEYWORD_SEGMENT),
            "ImplicitIndent" => Some(&IMPLICIT_INDENT),
            "ImplicitKeywordSegment" => Some(&IMPLICIT_KEYWORD_SEGMENT),
            "ImportedKeywordSegment" => Some(&IMPORTED_KEYWORD_SEGMENT),
            "InKeywordSegment" => Some(&IN_KEYWORD_SEGMENT),
            "InOperatorGrammar" => Some(&IN_OPERATOR_GRAMMAR),
            "IncludeKeywordSegment" => Some(&INCLUDE_KEYWORD_SEGMENT),
            "IncludingKeywordSegment" => Some(&INCLUDING_KEYWORD_SEGMENT),
            "IncrementKeywordSegment" => Some(&INCREMENT_KEYWORD_SEGMENT),
            "Indent" => Some(&INDENT),
            "IndexColumnDefinitionSegment" => Some(&INDEX_COLUMN_DEFINITION_SEGMENT),
            "IndexKeywordSegment" => Some(&INDEX_KEYWORD_SEGMENT),
            "IndexReferenceSegment" => Some(&INDEX_REFERENCE_SEGMENT),
            "IndicatorKeywordSegment" => Some(&INDICATOR_KEYWORD_SEGMENT),
            "InfileKeywordSegment" => Some(&INFILE_KEYWORD_SEGMENT),
            "InfixKeywordSegment" => Some(&INFIX_KEYWORD_SEGMENT),
            "InheritKeywordSegment" => Some(&INHERIT_KEYWORD_SEGMENT),
            "InheritsKeywordSegment" => Some(&INHERITS_KEYWORD_SEGMENT),
            "InitialKeywordSegment" => Some(&INITIAL_KEYWORD_SEGMENT),
            "InitializeKeywordSegment" => Some(&INITIALIZE_KEYWORD_SEGMENT),
            "InitiallyKeywordSegment" => Some(&INITIALLY_KEYWORD_SEGMENT),
            "InnerKeywordSegment" => Some(&INNER_KEYWORD_SEGMENT),
            "InoutKeywordSegment" => Some(&INOUT_KEYWORD_SEGMENT),
            "InputKeywordSegment" => Some(&INPUT_KEYWORD_SEGMENT),
            "InsensitiveKeywordSegment" => Some(&INSENSITIVE_KEYWORD_SEGMENT),
            "InsertKeywordSegment" => Some(&INSERT_KEYWORD_SEGMENT),
            "InsertStatementSegment" => Some(&INSERT_STATEMENT_SEGMENT),
            "Insert_idKeywordSegment" => Some(&INSERT_ID_KEYWORD_SEGMENT),
            "InstanceKeywordSegment" => Some(&INSTANCE_KEYWORD_SEGMENT),
            "InstantiableKeywordSegment" => Some(&INSTANTIABLE_KEYWORD_SEGMENT),
            "InsteadKeywordSegment" => Some(&INSTEAD_KEYWORD_SEGMENT),
            "Int1KeywordSegment" => Some(&INT1_KEYWORD_SEGMENT),
            "Int2KeywordSegment" => Some(&INT2_KEYWORD_SEGMENT),
            "Int3KeywordSegment" => Some(&INT3_KEYWORD_SEGMENT),
            "Int4KeywordSegment" => Some(&INT4_KEYWORD_SEGMENT),
            "Int8KeywordSegment" => Some(&INT8_KEYWORD_SEGMENT),
            "IntKeywordSegment" => Some(&INT_KEYWORD_SEGMENT),
            "IntegerKeywordSegment" => Some(&INTEGER_KEYWORD_SEGMENT),
            "IntegrationKeywordSegment" => Some(&INTEGRATION_KEYWORD_SEGMENT),
            "IntegrationsKeywordSegment" => Some(&INTEGRATIONS_KEYWORD_SEGMENT),
            "IntersectKeywordSegment" => Some(&INTERSECT_KEYWORD_SEGMENT),
            "IntersectionKeywordSegment" => Some(&INTERSECTION_KEYWORD_SEGMENT),
            "IntervalExpressionSegment" => Some(&INTERVAL_EXPRESSION_SEGMENT),
            "IntervalKeywordSegment" => Some(&INTERVAL_KEYWORD_SEGMENT),
            "IntoKeywordSegment" => Some(&INTO_KEYWORD_SEGMENT),
            "InvokerKeywordSegment" => Some(&INVOKER_KEYWORD_SEGMENT),
            "IsClauseGrammar" => Some(&IS_CLAUSE_GRAMMAR),
            "IsDistinctFromGrammar" => Some(&IS_DISTINCT_FROM_GRAMMAR),
            "IsKeywordSegment" => Some(&IS_KEYWORD_SEGMENT),
            "IsNullGrammar" => Some(&IS_NULL_GRAMMAR),
            "IsamKeywordSegment" => Some(&ISAM_KEYWORD_SEGMENT),
            "IsnullKeywordSegment" => Some(&ISNULL_KEYWORD_SEGMENT),
            "IsolationKeywordSegment" => Some(&ISOLATION_KEYWORD_SEGMENT),
            "IterateKeywordSegment" => Some(&ITERATE_KEYWORD_SEGMENT),
            "JoinClauseSegment" => Some(&JOIN_CLAUSE_SEGMENT),
            "JoinKeywordSegment" => Some(&JOIN_KEYWORD_SEGMENT),
            "JoinKeywordsGrammar" => Some(&JOIN_KEYWORDS_GRAMMAR),
            "JoinLikeClauseGrammar" => Some(&JOIN_LIKE_CLAUSE_GRAMMAR),
            "JoinOnConditionSegment" => Some(&JOIN_ON_CONDITION_SEGMENT),
            "JoinTypeKeywordsGrammar" => Some(&JOIN_TYPE_KEYWORDS_GRAMMAR),
            "JoinUsingConditionGrammar" => Some(&JOIN_USING_CONDITION_GRAMMAR),
            "JsonKeywordSegment" => Some(&JSON_KEYWORD_SEGMENT),
            "KKeywordSegment" => Some(&K_KEYWORD_SEGMENT),
            "KeyKeywordSegment" => Some(&KEY_KEYWORD_SEGMENT),
            "Key_memberKeywordSegment" => Some(&KEY_MEMBER_KEYWORD_SEGMENT),
            "Key_typeKeywordSegment" => Some(&KEY_TYPE_KEYWORD_SEGMENT),
            "KeysKeywordSegment" => Some(&KEYS_KEYWORD_SEGMENT),
            "KeywordSegment" => Some(&KEYWORD_SEGMENT),
            "KillKeywordSegment" => Some(&KILL_KEYWORD_SEGMENT),
            "LancompilerKeywordSegment" => Some(&LANCOMPILER_KEYWORD_SEGMENT),
            "LanguageKeywordSegment" => Some(&LANGUAGE_KEYWORD_SEGMENT),
            "LargeKeywordSegment" => Some(&LARGE_KEYWORD_SEGMENT),
            "LastKeywordSegment" => Some(&LAST_KEYWORD_SEGMENT),
            "Last_insert_idKeywordSegment" => Some(&LAST_INSERT_ID_KEYWORD_SEGMENT),
            "LateralKeywordSegment" => Some(&LATERAL_KEYWORD_SEGMENT),
            "LeadingKeywordSegment" => Some(&LEADING_KEYWORD_SEGMENT),
            "LeastKeywordSegment" => Some(&LEAST_KEYWORD_SEGMENT),
            "LeaveKeywordSegment" => Some(&LEAVE_KEYWORD_SEGMENT),
            "LeftKeywordSegment" => Some(&LEFT_KEYWORD_SEGMENT),
            "LengthKeywordSegment" => Some(&LENGTH_KEYWORD_SEGMENT),
            "LessKeywordSegment" => Some(&LESS_KEYWORD_SEGMENT),
            "LessThanOrEqualToSegment" => Some(&LESS_THAN_OR_EQUAL_TO_SEGMENT),
            "LessThanSegment" => Some(&LESS_THAN_SEGMENT),
            "LevelKeywordSegment" => Some(&LEVEL_KEYWORD_SEGMENT),
            "LikeExpressionGrammar" => Some(&LIKE_EXPRESSION_GRAMMAR),
            "LikeGrammar" => Some(&LIKE_GRAMMAR),
            "LikeKeywordSegment" => Some(&LIKE_KEYWORD_SEGMENT),
            "LikeOperatorSegment" => Some(&LIKE_OPERATOR_SEGMENT),
            "LimitClauseSegment" => Some(&LIMIT_CLAUSE_SEGMENT),
            "LimitKeywordSegment" => Some(&LIMIT_KEYWORD_SEGMENT),
            "LinenoKeywordSegment" => Some(&LINENO_KEYWORD_SEGMENT),
            "LinesKeywordSegment" => Some(&LINES_KEYWORD_SEGMENT),
            "ListComprehensionGrammar" => Some(&LIST_COMPREHENSION_GRAMMAR),
            "ListenKeywordSegment" => Some(&LISTEN_KEYWORD_SEGMENT),
            "LiteralGrammar" => Some(&LITERAL_GRAMMAR),
            "LiteralKeywordSegment" => Some(&LITERAL_KEYWORD_SEGMENT),
            "LiteralSegment" => Some(&LITERAL_SEGMENT),
            "LnKeywordSegment" => Some(&LN_KEYWORD_SEGMENT),
            "LoadKeywordSegment" => Some(&LOAD_KEYWORD_SEGMENT),
            "LocalAliasSegment" => Some(&LOCAL_ALIAS_SEGMENT),
            "LocalKeywordSegment" => Some(&LOCAL_KEYWORD_SEGMENT),
            "LocaltimeKeywordSegment" => Some(&LOCALTIME_KEYWORD_SEGMENT),
            "LocaltimestampKeywordSegment" => Some(&LOCALTIMESTAMP_KEYWORD_SEGMENT),
            "LocationKeywordSegment" => Some(&LOCATION_KEYWORD_SEGMENT),
            "LocatorKeywordSegment" => Some(&LOCATOR_KEYWORD_SEGMENT),
            "LockKeywordSegment" => Some(&LOCK_KEYWORD_SEGMENT),
            "LocksKeywordSegment" => Some(&LOCKS_KEYWORD_SEGMENT),
            "LoginKeywordSegment" => Some(&LOGIN_KEYWORD_SEGMENT),
            "LogsKeywordSegment" => Some(&LOGS_KEYWORD_SEGMENT),
            "LongKeywordSegment" => Some(&LONG_KEYWORD_SEGMENT),
            "LongblobKeywordSegment" => Some(&LONGBLOB_KEYWORD_SEGMENT),
            "LongtextKeywordSegment" => Some(&LONGTEXT_KEYWORD_SEGMENT),
            "LoopKeywordSegment" => Some(&LOOP_KEYWORD_SEGMENT),
            "Low_priorityKeywordSegment" => Some(&LOW_PRIORITY_KEYWORD_SEGMENT),
            "LowerKeywordSegment" => Some(&LOWER_KEYWORD_SEGMENT),
            "MKeywordSegment" => Some(&M_KEYWORD_SEGMENT),
            "MLTableExpressionSegment" => Some(&M_L_TABLE_EXPRESSION_SEGMENT),
            "ManageKeywordSegment" => Some(&MANAGE_KEYWORD_SEGMENT),
            "MapKeywordSegment" => Some(&MAP_KEYWORD_SEGMENT),
            "MapTypeSegment" => Some(&MAP_TYPE_SEGMENT),
            "MaskingKeywordSegment" => Some(&MASKING_KEYWORD_SEGMENT),
            "MatchConditionSegment" => Some(&MATCH_CONDITION_SEGMENT),
            "MatchKeywordSegment" => Some(&MATCH_KEYWORD_SEGMENT),
            "MatchedKeywordSegment" => Some(&MATCHED_KEYWORD_SEGMENT),
            "MaterializedKeywordSegment" => Some(&MATERIALIZED_KEYWORD_SEGMENT),
            "MaxKeywordSegment" => Some(&MAX_KEYWORD_SEGMENT),
            "Max_rowsKeywordSegment" => Some(&MAX_ROWS_KEYWORD_SEGMENT),
            "MaxextentsKeywordSegment" => Some(&MAXEXTENTS_KEYWORD_SEGMENT),
            "MaxvalueKeywordSegment" => Some(&MAXVALUE_KEYWORD_SEGMENT),
            "MediumblobKeywordSegment" => Some(&MEDIUMBLOB_KEYWORD_SEGMENT),
            "MediumintKeywordSegment" => Some(&MEDIUMINT_KEYWORD_SEGMENT),
            "MediumtextKeywordSegment" => Some(&MEDIUMTEXT_KEYWORD_SEGMENT),
            "MemberKeywordSegment" => Some(&MEMBER_KEYWORD_SEGMENT),
            "MergeDeleteClauseSegment" => Some(&MERGE_DELETE_CLAUSE_SEGMENT),
            "MergeInsertClauseSegment" => Some(&MERGE_INSERT_CLAUSE_SEGMENT),
            "MergeIntoLiteralGrammar" => Some(&MERGE_INTO_LITERAL_GRAMMAR),
            "MergeKeywordSegment" => Some(&MERGE_KEYWORD_SEGMENT),
            "MergeMatchSegment" => Some(&MERGE_MATCH_SEGMENT),
            "MergeMatchedClauseSegment" => Some(&MERGE_MATCHED_CLAUSE_SEGMENT),
            "MergeNotMatchedClauseSegment" => Some(&MERGE_NOT_MATCHED_CLAUSE_SEGMENT),
            "MergeStatementSegment" => Some(&MERGE_STATEMENT_SEGMENT),
            "MergeUpdateClauseSegment" => Some(&MERGE_UPDATE_CLAUSE_SEGMENT),
            "Message_lengthKeywordSegment" => Some(&MESSAGE_LENGTH_KEYWORD_SEGMENT),
            "Message_octet_lengthKeywordSegment" => Some(&MESSAGE_OCTET_LENGTH_KEYWORD_SEGMENT),
            "Message_textKeywordSegment" => Some(&MESSAGE_TEXT_KEYWORD_SEGMENT),
            "MethodKeywordSegment" => Some(&METHOD_KEYWORD_SEGMENT),
            "MiddleintKeywordSegment" => Some(&MIDDLEINT_KEYWORD_SEGMENT),
            "MillisecondKeywordSegment" => Some(&MILLISECOND_KEYWORD_SEGMENT),
            "MinKeywordSegment" => Some(&MIN_KEYWORD_SEGMENT),
            "Min_rowsKeywordSegment" => Some(&MIN_ROWS_KEYWORD_SEGMENT),
            "MinusKeywordSegment" => Some(&MINUS_KEYWORD_SEGMENT),
            "MinusSegment" => Some(&MINUS_SEGMENT),
            "MinuteKeywordSegment" => Some(&MINUTE_KEYWORD_SEGMENT),
            "Minute_microsecondKeywordSegment" => Some(&MINUTE_MICROSECOND_KEYWORD_SEGMENT),
            "Minute_secondKeywordSegment" => Some(&MINUTE_SECOND_KEYWORD_SEGMENT),
            "MinvalueKeywordSegment" => Some(&MINVALUE_KEYWORD_SEGMENT),
            "MlKeywordSegment" => Some(&ML_KEYWORD_SEGMENT),
            "MlslabelKeywordSegment" => Some(&MLSLABEL_KEYWORD_SEGMENT),
            "ModKeywordSegment" => Some(&MOD_KEYWORD_SEGMENT),
            "ModeKeywordSegment" => Some(&MODE_KEYWORD_SEGMENT),
            "ModelKeywordSegment" => Some(&MODEL_KEYWORD_SEGMENT),
            "ModifiesKeywordSegment" => Some(&MODIFIES_KEYWORD_SEGMENT),
            "ModifyKeywordSegment" => Some(&MODIFY_KEYWORD_SEGMENT),
            "ModuleKeywordSegment" => Some(&MODULE_KEYWORD_SEGMENT),
            "ModuloSegment" => Some(&MODULO_SEGMENT),
            "MonitorKeywordSegment" => Some(&MONITOR_KEYWORD_SEGMENT),
            "MonthKeywordSegment" => Some(&MONTH_KEYWORD_SEGMENT),
            "MonthnameKeywordSegment" => Some(&MONTHNAME_KEYWORD_SEGMENT),
            "MoreKeywordSegment" => Some(&MORE_KEYWORD_SEGMENT),
            "MoveKeywordSegment" => Some(&MOVE_KEYWORD_SEGMENT),
            "MultiplySegment" => Some(&MULTIPLY_SEGMENT),
            "MultisetKeywordSegment" => Some(&MULTISET_KEYWORD_SEGMENT),
            "MumpsKeywordSegment" => Some(&MUMPS_KEYWORD_SEGMENT),
            "MyisamKeywordSegment" => Some(&MYISAM_KEYWORD_SEGMENT),
            "NakedIdentifierSegment" => Some(&NAKED_IDENTIFIER_SEGMENT),
            "NameKeywordSegment" => Some(&NAME_KEYWORD_SEGMENT),
            "NamedWindowExpressionSegment" => Some(&NAMED_WINDOW_EXPRESSION_SEGMENT),
            "NamedWindowSegment" => Some(&NAMED_WINDOW_SEGMENT),
            "NamesKeywordSegment" => Some(&NAMES_KEYWORD_SEGMENT),
            "NanKeywordSegment" => Some(&NAN_KEYWORD_SEGMENT),
            "NanLiteralSegment" => Some(&NAN_LITERAL_SEGMENT),
            "NationalKeywordSegment" => Some(&NATIONAL_KEYWORD_SEGMENT),
            "NaturalJoinKeywordsGrammar" => Some(&NATURAL_JOIN_KEYWORDS_GRAMMAR),
            "NaturalKeywordSegment" => Some(&NATURAL_KEYWORD_SEGMENT),
            "NcharKeywordSegment" => Some(&NCHAR_KEYWORD_SEGMENT),
            "NclobKeywordSegment" => Some(&NCLOB_KEYWORD_SEGMENT),
            "NegativeSegment" => Some(&NEGATIVE_SEGMENT),
            "NestedJoinGrammar" => Some(&NESTED_JOIN_GRAMMAR),
            "NestingKeywordSegment" => Some(&NESTING_KEYWORD_SEGMENT),
            "NewKeywordSegment" => Some(&NEW_KEYWORD_SEGMENT),
            "NewlineSegment" => Some(&NEWLINE_SEGMENT),
            "NextKeywordSegment" => Some(&NEXT_KEYWORD_SEGMENT),
            "NoKeywordSegment" => Some(&NO_KEYWORD_SEGMENT),
            "No_write_to_binlogKeywordSegment" => Some(&NO_WRITE_TO_BINLOG_KEYWORD_SEGMENT),
            "NoauditKeywordSegment" => Some(&NOAUDIT_KEYWORD_SEGMENT),
            "NocacheKeywordSegment" => Some(&NOCACHE_KEYWORD_SEGMENT),
            "NocheckKeywordSegment" => Some(&NOCHECK_KEYWORD_SEGMENT),
            "NocompressKeywordSegment" => Some(&NOCOMPRESS_KEYWORD_SEGMENT),
            "NocreatedbKeywordSegment" => Some(&NOCREATEDB_KEYWORD_SEGMENT),
            "NocreateroleKeywordSegment" => Some(&NOCREATEROLE_KEYWORD_SEGMENT),
            "NocreateuserKeywordSegment" => Some(&NOCREATEUSER_KEYWORD_SEGMENT),
            "NocycleKeywordSegment" => Some(&NOCYCLE_KEYWORD_SEGMENT),
            "NoinheritKeywordSegment" => Some(&NOINHERIT_KEYWORD_SEGMENT),
            "NologinKeywordSegment" => Some(&NOLOGIN_KEYWORD_SEGMENT),
            "NonSetSelectableGrammar" => Some(&NON_SET_SELECTABLE_GRAMMAR),
            "NonStandardJoinTypeKeywordsGrammar" => Some(&NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR),
            "NonWithNonSelectableGrammar" => Some(&NON_WITH_NON_SELECTABLE_GRAMMAR),
            "NonWithSelectableGrammar" => Some(&NON_WITH_SELECTABLE_GRAMMAR),
            "NonclusteredKeywordSegment" => Some(&NONCLUSTERED_KEYWORD_SEGMENT),
            "NoneKeywordSegment" => Some(&NONE_KEYWORD_SEGMENT),
            "NoorderKeywordSegment" => Some(&NOORDER_KEYWORD_SEGMENT),
            "NormalizeKeywordSegment" => Some(&NORMALIZE_KEYWORD_SEGMENT),
            "NormalizedGrammar" => Some(&NORMALIZED_GRAMMAR),
            "NormalizedKeywordSegment" => Some(&NORMALIZED_KEYWORD_SEGMENT),
            "NosuperuserKeywordSegment" => Some(&NOSUPERUSER_KEYWORD_SEGMENT),
            "NotEnforcedGrammar" => Some(&NOT_ENFORCED_GRAMMAR),
            "NotEqualToSegment" => Some(&NOT_EQUAL_TO_SEGMENT),
            "NotKeywordSegment" => Some(&NOT_KEYWORD_SEGMENT),
            "NotNullGrammar" => Some(&NOT_NULL_GRAMMAR),
            "NotOperatorGrammar" => Some(&NOT_OPERATOR_GRAMMAR),
            "NothingKeywordSegment" => Some(&NOTHING_KEYWORD_SEGMENT),
            "NotifyKeywordSegment" => Some(&NOTIFY_KEYWORD_SEGMENT),
            "NotnullKeywordSegment" => Some(&NOTNULL_KEYWORD_SEGMENT),
            "NowaitKeywordSegment" => Some(&NOWAIT_KEYWORD_SEGMENT),
            "NullKeywordSegment" => Some(&NULL_KEYWORD_SEGMENT),
            "NullLiteralSegment" => Some(&NULL_LITERAL_SEGMENT),
            "NullableKeywordSegment" => Some(&NULLABLE_KEYWORD_SEGMENT),
            "NullifKeywordSegment" => Some(&NULLIF_KEYWORD_SEGMENT),
            "NullsKeywordSegment" => Some(&NULLS_KEYWORD_SEGMENT),
            "NumberKeywordSegment" => Some(&NUMBER_KEYWORD_SEGMENT),
            "NumericKeywordSegment" => Some(&NUMERIC_KEYWORD_SEGMENT),
            "NumericLiteralSegment" => Some(&NUMERIC_LITERAL_SEGMENT),
            "ObjectKeywordSegment" => Some(&OBJECT_KEYWORD_SEGMENT),
            "ObjectLiteralElementSegment" => Some(&OBJECT_LITERAL_ELEMENT_SEGMENT),
            "ObjectLiteralSegment" => Some(&OBJECT_LITERAL_SEGMENT),
            "ObjectReferenceDelimiterGrammar" => Some(&OBJECT_REFERENCE_DELIMITER_GRAMMAR),
            "ObjectReferenceSegment" => Some(&OBJECT_REFERENCE_SEGMENT),
            "ObjectReferenceTerminatorGrammar" => Some(&OBJECT_REFERENCE_TERMINATOR_GRAMMAR),
            "ObjectsKeywordSegment" => Some(&OBJECTS_KEYWORD_SEGMENT),
            "Octet_lengthKeywordSegment" => Some(&OCTET_LENGTH_KEYWORD_SEGMENT),
            "OctetsKeywordSegment" => Some(&OCTETS_KEYWORD_SEGMENT),
            "OfKeywordSegment" => Some(&OF_KEYWORD_SEGMENT),
            "OffKeywordSegment" => Some(&OFF_KEYWORD_SEGMENT),
            "OfflineKeywordSegment" => Some(&OFFLINE_KEYWORD_SEGMENT),
            "OffsetClauseSegment" => Some(&OFFSET_CLAUSE_SEGMENT),
            "OffsetKeywordSegment" => Some(&OFFSET_KEYWORD_SEGMENT),
            "OffsetsKeywordSegment" => Some(&OFFSETS_KEYWORD_SEGMENT),
            "OidsKeywordSegment" => Some(&OIDS_KEYWORD_SEGMENT),
            "OldKeywordSegment" => Some(&OLD_KEYWORD_SEGMENT),
            "OnKeywordSegment" => Some(&ON_KEYWORD_SEGMENT),
            "OnlineKeywordSegment" => Some(&ONLINE_KEYWORD_SEGMENT),
            "OnlyKeywordSegment" => Some(&ONLY_KEYWORD_SEGMENT),
            "OpenKeywordSegment" => Some(&OPEN_KEYWORD_SEGMENT),
            "OpendatasourceKeywordSegment" => Some(&OPENDATASOURCE_KEYWORD_SEGMENT),
            "OpenqueryKeywordSegment" => Some(&OPENQUERY_KEYWORD_SEGMENT),
            "OpenrowsetKeywordSegment" => Some(&OPENROWSET_KEYWORD_SEGMENT),
            "OpenxmlKeywordSegment" => Some(&OPENXML_KEYWORD_SEGMENT),
            "OperateKeywordSegment" => Some(&OPERATE_KEYWORD_SEGMENT),
            "OperationKeywordSegment" => Some(&OPERATION_KEYWORD_SEGMENT),
            "OperatorKeywordSegment" => Some(&OPERATOR_KEYWORD_SEGMENT),
            "OptimizeKeywordSegment" => Some(&OPTIMIZE_KEYWORD_SEGMENT),
            "OptionKeywordSegment" => Some(&OPTION_KEYWORD_SEGMENT),
            "OptionallyKeywordSegment" => Some(&OPTIONALLY_KEYWORD_SEGMENT),
            "OptionsKeywordSegment" => Some(&OPTIONS_KEYWORD_SEGMENT),
            "OrKeywordSegment" => Some(&OR_KEYWORD_SEGMENT),
            "OrOperatorGrammar" => Some(&OR_OPERATOR_GRAMMAR),
            "OrReplaceGrammar" => Some(&OR_REPLACE_GRAMMAR),
            "OrderByClauseSegment" => Some(&ORDER_BY_CLAUSE_SEGMENT),
            "OrderByClauseTerminators" => Some(&ORDER_BY_CLAUSE_TERMINATORS),
            "OrderKeywordSegment" => Some(&ORDER_KEYWORD_SEGMENT),
            "OrderNoOrderGrammar" => Some(&ORDER_NO_ORDER_GRAMMAR),
            "OrderingKeywordSegment" => Some(&ORDERING_KEYWORD_SEGMENT),
            "OrdinalityKeywordSegment" => Some(&ORDINALITY_KEYWORD_SEGMENT),
            "OthersKeywordSegment" => Some(&OTHERS_KEYWORD_SEGMENT),
            "OutKeywordSegment" => Some(&OUT_KEYWORD_SEGMENT),
            "OuterKeywordSegment" => Some(&OUTER_KEYWORD_SEGMENT),
            "OutfileKeywordSegment" => Some(&OUTFILE_KEYWORD_SEGMENT),
            "OutputKeywordSegment" => Some(&OUTPUT_KEYWORD_SEGMENT),
            "OverClauseSegment" => Some(&OVER_CLAUSE_SEGMENT),
            "OverKeywordSegment" => Some(&OVER_KEYWORD_SEGMENT),
            "OverlapsClauseSegment" => Some(&OVERLAPS_CLAUSE_SEGMENT),
            "OverlapsKeywordSegment" => Some(&OVERLAPS_KEYWORD_SEGMENT),
            "OverlayKeywordSegment" => Some(&OVERLAY_KEYWORD_SEGMENT),
            "OverridingKeywordSegment" => Some(&OVERRIDING_KEYWORD_SEGMENT),
            "OverwriteKeywordSegment" => Some(&OVERWRITE_KEYWORD_SEGMENT),
            "OwnerKeywordSegment" => Some(&OWNER_KEYWORD_SEGMENT),
            "OwnershipKeywordSegment" => Some(&OWNERSHIP_KEYWORD_SEGMENT),
            "Pack_keysKeywordSegment" => Some(&PACK_KEYS_KEYWORD_SEGMENT),
            "PadKeywordSegment" => Some(&PAD_KEYWORD_SEGMENT),
            "ParameterKeywordSegment" => Some(&PARAMETER_KEYWORD_SEGMENT),
            "ParameterNameSegment" => Some(&PARAMETER_NAME_SEGMENT),
            "ParameterSegment" => Some(&PARAMETER_SEGMENT),
            "Parameter_modeKeywordSegment" => Some(&PARAMETER_MODE_KEYWORD_SEGMENT),
            "Parameter_nameKeywordSegment" => Some(&PARAMETER_NAME_KEYWORD_SEGMENT),
            "Parameter_ordinal_positionKeywordSegment" => Some(&PARAMETER_ORDINAL_POSITION_KEYWORD_SEGMENT),
            "Parameter_specific_catalogKeywordSegment" => Some(&PARAMETER_SPECIFIC_CATALOG_KEYWORD_SEGMENT),
            "Parameter_specific_nameKeywordSegment" => Some(&PARAMETER_SPECIFIC_NAME_KEYWORD_SEGMENT),
            "Parameter_specific_schemaKeywordSegment" => Some(&PARAMETER_SPECIFIC_SCHEMA_KEYWORD_SEGMENT),
            "ParametersKeywordSegment" => Some(&PARAMETERS_KEYWORD_SEGMENT),
            "PartialKeywordSegment" => Some(&PARTIAL_KEYWORD_SEGMENT),
            "PartitionClauseSegment" => Some(&PARTITION_CLAUSE_SEGMENT),
            "PartitionKeywordSegment" => Some(&PARTITION_KEYWORD_SEGMENT),
            "PascalKeywordSegment" => Some(&PASCAL_KEYWORD_SEGMENT),
            "PasswordKeywordSegment" => Some(&PASSWORD_KEYWORD_SEGMENT),
            "PathKeywordSegment" => Some(&PATH_KEYWORD_SEGMENT),
            "PathSegment" => Some(&PATH_SEGMENT),
            "PatternMatchingGrammar" => Some(&PATTERN_MATCHING_GRAMMAR),
            "PctfreeKeywordSegment" => Some(&PCTFREE_KEYWORD_SEGMENT),
            "PercentKeywordSegment" => Some(&PERCENT_KEYWORD_SEGMENT),
            "Percent_rankKeywordSegment" => Some(&PERCENT_RANK_KEYWORD_SEGMENT),
            "Percentile_contKeywordSegment" => Some(&PERCENTILE_CONT_KEYWORD_SEGMENT),
            "Percentile_discKeywordSegment" => Some(&PERCENTILE_DISC_KEYWORD_SEGMENT),
            "PipeKeywordSegment" => Some(&PIPE_KEYWORD_SEGMENT),
            "PipeSegment" => Some(&PIPE_SEGMENT),
            "PlacingKeywordSegment" => Some(&PLACING_KEYWORD_SEGMENT),
            "PlanKeywordSegment" => Some(&PLAN_KEYWORD_SEGMENT),
            "PliKeywordSegment" => Some(&PLI_KEYWORD_SEGMENT),
            "PlusSegment" => Some(&PLUS_SEGMENT),
            "PolicyKeywordSegment" => Some(&POLICY_KEYWORD_SEGMENT),
            "PositionKeywordSegment" => Some(&POSITION_KEYWORD_SEGMENT),
            "PositiveSegment" => Some(&POSITIVE_SEGMENT),
            "PostFunctionGrammar" => Some(&POST_FUNCTION_GRAMMAR),
            "PostTableExpressionGrammar" => Some(&POST_TABLE_EXPRESSION_GRAMMAR),
            "PostfixKeywordSegment" => Some(&POSTFIX_KEYWORD_SEGMENT),
            "PowerKeywordSegment" => Some(&POWER_KEYWORD_SEGMENT),
            "PreTableFunctionKeywordsGrammar" => Some(&PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR),
            "PrecedingKeywordSegment" => Some(&PRECEDING_KEYWORD_SEGMENT),
            "PrecisionKeywordSegment" => Some(&PRECISION_KEYWORD_SEGMENT),
            "PrefixKeywordSegment" => Some(&PREFIX_KEYWORD_SEGMENT),
            "PreorderKeywordSegment" => Some(&PREORDER_KEYWORD_SEGMENT),
            "PrepareKeywordSegment" => Some(&PREPARE_KEYWORD_SEGMENT),
            "PreparedKeywordSegment" => Some(&PREPARED_KEYWORD_SEGMENT),
            "PreserveKeywordSegment" => Some(&PRESERVE_KEYWORD_SEGMENT),
            "PrimaryKeyGrammar" => Some(&PRIMARY_KEY_GRAMMAR),
            "PrimaryKeywordSegment" => Some(&PRIMARY_KEYWORD_SEGMENT),
            "PrintKeywordSegment" => Some(&PRINT_KEYWORD_SEGMENT),
            "PriorKeywordSegment" => Some(&PRIOR_KEYWORD_SEGMENT),
            "PrivilegesKeywordSegment" => Some(&PRIVILEGES_KEYWORD_SEGMENT),
            "ProcKeywordSegment" => Some(&PROC_KEYWORD_SEGMENT),
            "ProceduralKeywordSegment" => Some(&PROCEDURAL_KEYWORD_SEGMENT),
            "ProcedureKeywordSegment" => Some(&PROCEDURE_KEYWORD_SEGMENT),
            "ProceduresKeywordSegment" => Some(&PROCEDURES_KEYWORD_SEGMENT),
            "ProcessKeywordSegment" => Some(&PROCESS_KEYWORD_SEGMENT),
            "ProcesslistKeywordSegment" => Some(&PROCESSLIST_KEYWORD_SEGMENT),
            "PublicKeywordSegment" => Some(&PUBLIC_KEYWORD_SEGMENT),
            "PurgeKeywordSegment" => Some(&PURGE_KEYWORD_SEGMENT),
            "QualifiedNumericLiteralSegment" => Some(&QUALIFIED_NUMERIC_LITERAL_SEGMENT),
            "QualifyKeywordSegment" => Some(&QUALIFY_KEYWORD_SEGMENT),
            "QuarterKeywordSegment" => Some(&QUARTER_KEYWORD_SEGMENT),
            "QuoteKeywordSegment" => Some(&QUOTE_KEYWORD_SEGMENT),
            "QuotedIdentifierSegment" => Some(&QUOTED_IDENTIFIER_SEGMENT),
            "QuotedLiteralSegment" => Some(&QUOTED_LITERAL_SEGMENT),
            "Raid0KeywordSegment" => Some(&RAID0_KEYWORD_SEGMENT),
            "RaiserrorKeywordSegment" => Some(&RAISERROR_KEYWORD_SEGMENT),
            "RangeKeywordSegment" => Some(&RANGE_KEYWORD_SEGMENT),
            "RankKeywordSegment" => Some(&RANK_KEYWORD_SEGMENT),
            "RawEqualsSegment" => Some(&RAW_EQUALS_SEGMENT),
            "RawGreaterThanSegment" => Some(&RAW_GREATER_THAN_SEGMENT),
            "RawKeywordSegment" => Some(&RAW_KEYWORD_SEGMENT),
            "RawLessThanSegment" => Some(&RAW_LESS_THAN_SEGMENT),
            "RawNotSegment" => Some(&RAW_NOT_SEGMENT),
            "RawSegment" => Some(&RAW_SEGMENT),
            "ReadKeywordSegment" => Some(&READ_KEYWORD_SEGMENT),
            "ReadsKeywordSegment" => Some(&READS_KEYWORD_SEGMENT),
            "ReadtextKeywordSegment" => Some(&READTEXT_KEYWORD_SEGMENT),
            "RealKeywordSegment" => Some(&REAL_KEYWORD_SEGMENT),
            "RecheckKeywordSegment" => Some(&RECHECK_KEYWORD_SEGMENT),
            "ReconfigureKeywordSegment" => Some(&RECONFIGURE_KEYWORD_SEGMENT),
            "RecursiveKeywordSegment" => Some(&RECURSIVE_KEYWORD_SEGMENT),
            "RefKeywordSegment" => Some(&REF_KEYWORD_SEGMENT),
            "ReferenceDefinitionGrammar" => Some(&REFERENCE_DEFINITION_GRAMMAR),
            "ReferenceMatchGrammar" => Some(&REFERENCE_MATCH_GRAMMAR),
            "Reference_usageKeywordSegment" => Some(&REFERENCE_USAGE_KEYWORD_SEGMENT),
            "ReferencesKeywordSegment" => Some(&REFERENCES_KEYWORD_SEGMENT),
            "ReferencingKeywordSegment" => Some(&REFERENCING_KEYWORD_SEGMENT),
            "ReferentialActionGrammar" => Some(&REFERENTIAL_ACTION_GRAMMAR),
            "RegexpKeywordSegment" => Some(&REGEXP_KEYWORD_SEGMENT),
            "Regr_avgxKeywordSegment" => Some(&REGR_AVGX_KEYWORD_SEGMENT),
            "Regr_avgyKeywordSegment" => Some(&REGR_AVGY_KEYWORD_SEGMENT),
            "Regr_countKeywordSegment" => Some(&REGR_COUNT_KEYWORD_SEGMENT),
            "Regr_interceptKeywordSegment" => Some(&REGR_INTERCEPT_KEYWORD_SEGMENT),
            "Regr_r2KeywordSegment" => Some(&REGR_R2_KEYWORD_SEGMENT),
            "Regr_slopeKeywordSegment" => Some(&REGR_SLOPE_KEYWORD_SEGMENT),
            "Regr_sxxKeywordSegment" => Some(&REGR_SXX_KEYWORD_SEGMENT),
            "Regr_sxyKeywordSegment" => Some(&REGR_SXY_KEYWORD_SEGMENT),
            "Regr_syyKeywordSegment" => Some(&REGR_SYY_KEYWORD_SEGMENT),
            "ReindexKeywordSegment" => Some(&REINDEX_KEYWORD_SEGMENT),
            "RelativeKeywordSegment" => Some(&RELATIVE_KEYWORD_SEGMENT),
            "ReleaseKeywordSegment" => Some(&RELEASE_KEYWORD_SEGMENT),
            "ReloadKeywordSegment" => Some(&RELOAD_KEYWORD_SEGMENT),
            "RenameKeywordSegment" => Some(&RENAME_KEYWORD_SEGMENT),
            "RepeatKeywordSegment" => Some(&REPEAT_KEYWORD_SEGMENT),
            "RepeatableKeywordSegment" => Some(&REPEATABLE_KEYWORD_SEGMENT),
            "ReplaceKeywordSegment" => Some(&REPLACE_KEYWORD_SEGMENT),
            "ReplicationKeywordSegment" => Some(&REPLICATION_KEYWORD_SEGMENT),
            "RequireKeywordSegment" => Some(&REQUIRE_KEYWORD_SEGMENT),
            "ResetKeywordSegment" => Some(&RESET_KEYWORD_SEGMENT),
            "ResignalKeywordSegment" => Some(&RESIGNAL_KEYWORD_SEGMENT),
            "ResourceKeywordSegment" => Some(&RESOURCE_KEYWORD_SEGMENT),
            "RespectKeywordSegment" => Some(&RESPECT_KEYWORD_SEGMENT),
            "RestartKeywordSegment" => Some(&RESTART_KEYWORD_SEGMENT),
            "RestoreKeywordSegment" => Some(&RESTORE_KEYWORD_SEGMENT),
            "RestrictKeywordSegment" => Some(&RESTRICT_KEYWORD_SEGMENT),
            "ResultKeywordSegment" => Some(&RESULT_KEYWORD_SEGMENT),
            "ReturnKeywordSegment" => Some(&RETURN_KEYWORD_SEGMENT),
            "Returned_cardinalityKeywordSegment" => Some(&RETURNED_CARDINALITY_KEYWORD_SEGMENT),
            "Returned_lengthKeywordSegment" => Some(&RETURNED_LENGTH_KEYWORD_SEGMENT),
            "Returned_octet_lengthKeywordSegment" => Some(&RETURNED_OCTET_LENGTH_KEYWORD_SEGMENT),
            "Returned_sqlstateKeywordSegment" => Some(&RETURNED_SQLSTATE_KEYWORD_SEGMENT),
            "ReturnsKeywordSegment" => Some(&RETURNS_KEYWORD_SEGMENT),
            "RevokeKeywordSegment" => Some(&REVOKE_KEYWORD_SEGMENT),
            "RightKeywordSegment" => Some(&RIGHT_KEYWORD_SEGMENT),
            "RlikeKeywordSegment" => Some(&RLIKE_KEYWORD_SEGMENT),
            "RoleKeywordSegment" => Some(&ROLE_KEYWORD_SEGMENT),
            "RoleReferenceSegment" => Some(&ROLE_REFERENCE_SEGMENT),
            "RolesKeywordSegment" => Some(&ROLES_KEYWORD_SEGMENT),
            "RollbackKeywordSegment" => Some(&ROLLBACK_KEYWORD_SEGMENT),
            "RollupFunctionNameSegment" => Some(&ROLLUP_FUNCTION_NAME_SEGMENT),
            "RollupKeywordSegment" => Some(&ROLLUP_KEYWORD_SEGMENT),
            "RoutineKeywordSegment" => Some(&ROUTINE_KEYWORD_SEGMENT),
            "Routine_catalogKeywordSegment" => Some(&ROUTINE_CATALOG_KEYWORD_SEGMENT),
            "Routine_nameKeywordSegment" => Some(&ROUTINE_NAME_KEYWORD_SEGMENT),
            "Routine_schemaKeywordSegment" => Some(&ROUTINE_SCHEMA_KEYWORD_SEGMENT),
            "RoutinesKeywordSegment" => Some(&ROUTINES_KEYWORD_SEGMENT),
            "RowKeywordSegment" => Some(&ROW_KEYWORD_SEGMENT),
            "Row_countKeywordSegment" => Some(&ROW_COUNT_KEYWORD_SEGMENT),
            "Row_numberKeywordSegment" => Some(&ROW_NUMBER_KEYWORD_SEGMENT),
            "RowcountKeywordSegment" => Some(&ROWCOUNT_KEYWORD_SEGMENT),
            "RowguidcolKeywordSegment" => Some(&ROWGUIDCOL_KEYWORD_SEGMENT),
            "RowidKeywordSegment" => Some(&ROWID_KEYWORD_SEGMENT),
            "RownumKeywordSegment" => Some(&ROWNUM_KEYWORD_SEGMENT),
            "RowsKeywordSegment" => Some(&ROWS_KEYWORD_SEGMENT),
            "RuleKeywordSegment" => Some(&RULE_KEYWORD_SEGMENT),
            "SamplingExpressionSegment" => Some(&SAMPLING_EXPRESSION_SEGMENT),
            "SaveKeywordSegment" => Some(&SAVE_KEYWORD_SEGMENT),
            "SavepointKeywordSegment" => Some(&SAVEPOINT_KEYWORD_SEGMENT),
            "ScaleKeywordSegment" => Some(&SCALE_KEYWORD_SEGMENT),
            "SchemaKeywordSegment" => Some(&SCHEMA_KEYWORD_SEGMENT),
            "SchemaReferenceSegment" => Some(&SCHEMA_REFERENCE_SEGMENT),
            "Schema_nameKeywordSegment" => Some(&SCHEMA_NAME_KEYWORD_SEGMENT),
            "SchemasKeywordSegment" => Some(&SCHEMAS_KEYWORD_SEGMENT),
            "ScopeKeywordSegment" => Some(&SCOPE_KEYWORD_SEGMENT),
            "Scope_catalogKeywordSegment" => Some(&SCOPE_CATALOG_KEYWORD_SEGMENT),
            "Scope_nameKeywordSegment" => Some(&SCOPE_NAME_KEYWORD_SEGMENT),
            "Scope_schemaKeywordSegment" => Some(&SCOPE_SCHEMA_KEYWORD_SEGMENT),
            "ScrollKeywordSegment" => Some(&SCROLL_KEYWORD_SEGMENT),
            "SearchKeywordSegment" => Some(&SEARCH_KEYWORD_SEGMENT),
            "SecondKeywordSegment" => Some(&SECOND_KEYWORD_SEGMENT),
            "Second_microsecondKeywordSegment" => Some(&SECOND_MICROSECOND_KEYWORD_SEGMENT),
            "SectionKeywordSegment" => Some(&SECTION_KEYWORD_SEGMENT),
            "SecurityKeywordSegment" => Some(&SECURITY_KEYWORD_SEGMENT),
            "SelectClauseElementSegment" => Some(&SELECT_CLAUSE_ELEMENT_SEGMENT),
            "SelectClauseModifierSegment" => Some(&SELECT_CLAUSE_MODIFIER_SEGMENT),
            "SelectClauseSegment" => Some(&SELECT_CLAUSE_SEGMENT),
            "SelectClauseTerminatorGrammar" => Some(&SELECT_CLAUSE_TERMINATOR_GRAMMAR),
            "SelectKeywordSegment" => Some(&SELECT_KEYWORD_SEGMENT),
            "SelectStatementSegment" => Some(&SELECT_STATEMENT_SEGMENT),
            "SelectableGrammar" => Some(&SELECTABLE_GRAMMAR),
            "SelfKeywordSegment" => Some(&SELF_KEYWORD_SEGMENT),
            "SemicolonSegment" => Some(&SEMICOLON_SEGMENT),
            "SensitiveKeywordSegment" => Some(&SENSITIVE_KEYWORD_SEGMENT),
            "SeparatorKeywordSegment" => Some(&SEPARATOR_KEYWORD_SEGMENT),
            "SequenceKeywordSegment" => Some(&SEQUENCE_KEYWORD_SEGMENT),
            "SequenceMaxValueGrammar" => Some(&SEQUENCE_MAX_VALUE_GRAMMAR),
            "SequenceMinValueGrammar" => Some(&SEQUENCE_MIN_VALUE_GRAMMAR),
            "SequenceReferenceSegment" => Some(&SEQUENCE_REFERENCE_SEGMENT),
            "SequencesKeywordSegment" => Some(&SEQUENCES_KEYWORD_SEGMENT),
            "SerializableKeywordSegment" => Some(&SERIALIZABLE_KEYWORD_SEGMENT),
            "ServerKeywordSegment" => Some(&SERVER_KEYWORD_SEGMENT),
            "Server_nameKeywordSegment" => Some(&SERVER_NAME_KEYWORD_SEGMENT),
            "SessionKeywordSegment" => Some(&SESSION_KEYWORD_SEGMENT),
            "Session_userKeywordSegment" => Some(&SESSION_USER_KEYWORD_SEGMENT),
            "SetClauseListSegment" => Some(&SET_CLAUSE_LIST_SEGMENT),
            "SetClauseSegment" => Some(&SET_CLAUSE_SEGMENT),
            "SetExpressionSegment" => Some(&SET_EXPRESSION_SEGMENT),
            "SetKeywordSegment" => Some(&SET_KEYWORD_SEGMENT),
            "SetOperatorSegment" => Some(&SET_OPERATOR_SEGMENT),
            "SetSchemaStatementSegment" => Some(&SET_SCHEMA_STATEMENT_SEGMENT),
            "SetofKeywordSegment" => Some(&SETOF_KEYWORD_SEGMENT),
            "SetsKeywordSegment" => Some(&SETS_KEYWORD_SEGMENT),
            "SetuserKeywordSegment" => Some(&SETUSER_KEYWORD_SEGMENT),
            "ShareKeywordSegment" => Some(&SHARE_KEYWORD_SEGMENT),
            "SharesKeywordSegment" => Some(&SHARES_KEYWORD_SEGMENT),
            "ShorthandCastSegment" => Some(&SHORTHAND_CAST_SEGMENT),
            "ShowKeywordSegment" => Some(&SHOW_KEYWORD_SEGMENT),
            "ShutdownKeywordSegment" => Some(&SHUTDOWN_KEYWORD_SEGMENT),
            "SignalKeywordSegment" => Some(&SIGNAL_KEYWORD_SEGMENT),
            "SignedSegmentGrammar" => Some(&SIGNED_SEGMENT_GRAMMAR),
            "SimilarKeywordSegment" => Some(&SIMILAR_KEYWORD_SEGMENT),
            "SimpleKeywordSegment" => Some(&SIMPLE_KEYWORD_SEGMENT),
            "SingleIdentifierGrammar" => Some(&SINGLE_IDENTIFIER_GRAMMAR),
            "SingleIdentifierListSegment" => Some(&SINGLE_IDENTIFIER_LIST_SEGMENT),
            "SingleQuotedIdentifierSegment" => Some(&SINGLE_QUOTED_IDENTIFIER_SEGMENT),
            "SizeKeywordSegment" => Some(&SIZE_KEYWORD_SEGMENT),
            "SizedArrayTypeSegment" => Some(&SIZED_ARRAY_TYPE_SEGMENT),
            "SlashSegment" => Some(&SLASH_SEGMENT),
            "SliceSegment" => Some(&SLICE_SEGMENT),
            "SmallintKeywordSegment" => Some(&SMALLINT_KEYWORD_SEGMENT),
            "SomeKeywordSegment" => Some(&SOME_KEYWORD_SEGMENT),
            "SonameKeywordSegment" => Some(&SONAME_KEYWORD_SEGMENT),
            "SourceKeywordSegment" => Some(&SOURCE_KEYWORD_SEGMENT),
            "SpaceKeywordSegment" => Some(&SPACE_KEYWORD_SEGMENT),
            "SpatialKeywordSegment" => Some(&SPATIAL_KEYWORD_SEGMENT),
            "SpecificKeywordSegment" => Some(&SPECIFIC_KEYWORD_SEGMENT),
            "Specific_nameKeywordSegment" => Some(&SPECIFIC_NAME_KEYWORD_SEGMENT),
            "SpecifictypeKeywordSegment" => Some(&SPECIFICTYPE_KEYWORD_SEGMENT),
            "SqlKeywordSegment" => Some(&SQL_KEYWORD_SEGMENT),
            "Sql_big_resultKeywordSegment" => Some(&SQL_BIG_RESULT_KEYWORD_SEGMENT),
            "Sql_big_selectsKeywordSegment" => Some(&SQL_BIG_SELECTS_KEYWORD_SEGMENT),
            "Sql_big_tablesKeywordSegment" => Some(&SQL_BIG_TABLES_KEYWORD_SEGMENT),
            "Sql_calc_found_rowsKeywordSegment" => Some(&SQL_CALC_FOUND_ROWS_KEYWORD_SEGMENT),
            "Sql_log_offKeywordSegment" => Some(&SQL_LOG_OFF_KEYWORD_SEGMENT),
            "Sql_log_updateKeywordSegment" => Some(&SQL_LOG_UPDATE_KEYWORD_SEGMENT),
            "Sql_low_priority_updatesKeywordSegment" => Some(&SQL_LOW_PRIORITY_UPDATES_KEYWORD_SEGMENT),
            "Sql_select_limitKeywordSegment" => Some(&SQL_SELECT_LIMIT_KEYWORD_SEGMENT),
            "Sql_small_resultKeywordSegment" => Some(&SQL_SMALL_RESULT_KEYWORD_SEGMENT),
            "Sql_warningsKeywordSegment" => Some(&SQL_WARNINGS_KEYWORD_SEGMENT),
            "SqlcaKeywordSegment" => Some(&SQLCA_KEYWORD_SEGMENT),
            "SqlcodeKeywordSegment" => Some(&SQLCODE_KEYWORD_SEGMENT),
            "SqlerrorKeywordSegment" => Some(&SQLERROR_KEYWORD_SEGMENT),
            "SqlexceptionKeywordSegment" => Some(&SQLEXCEPTION_KEYWORD_SEGMENT),
            "SqlstateKeywordSegment" => Some(&SQLSTATE_KEYWORD_SEGMENT),
            "SqlwarningKeywordSegment" => Some(&SQLWARNING_KEYWORD_SEGMENT),
            "SqrtKeywordSegment" => Some(&SQRT_KEYWORD_SEGMENT),
            "SslKeywordSegment" => Some(&SSL_KEYWORD_SEGMENT),
            "StableKeywordSegment" => Some(&STABLE_KEYWORD_SEGMENT),
            "StageKeywordSegment" => Some(&STAGE_KEYWORD_SEGMENT),
            "StagesKeywordSegment" => Some(&STAGES_KEYWORD_SEGMENT),
            "StarSegment" => Some(&STAR_SEGMENT),
            "StartBracketSegment" => Some(&START_BRACKET_SEGMENT),
            "StartCurlyBracketSegment" => Some(&START_CURLY_BRACKET_SEGMENT),
            "StartKeywordSegment" => Some(&START_KEYWORD_SEGMENT),
            "StartSquareBracketSegment" => Some(&START_SQUARE_BRACKET_SEGMENT),
            "StartingKeywordSegment" => Some(&STARTING_KEYWORD_SEGMENT),
            "StartsKeywordSegment" => Some(&STARTS_KEYWORD_SEGMENT),
            "StateKeywordSegment" => Some(&STATE_KEYWORD_SEGMENT),
            "StatementKeywordSegment" => Some(&STATEMENT_KEYWORD_SEGMENT),
            "StatementSegment" => Some(&STATEMENT_SEGMENT),
            "StaticKeywordSegment" => Some(&STATIC_KEYWORD_SEGMENT),
            "StatisticsKeywordSegment" => Some(&STATISTICS_KEYWORD_SEGMENT),
            "Stddev_popKeywordSegment" => Some(&STDDEV_POP_KEYWORD_SEGMENT),
            "Stddev_sampKeywordSegment" => Some(&STDDEV_SAMP_KEYWORD_SEGMENT),
            "StdinKeywordSegment" => Some(&STDIN_KEYWORD_SEGMENT),
            "StdoutKeywordSegment" => Some(&STDOUT_KEYWORD_SEGMENT),
            "StorageKeywordSegment" => Some(&STORAGE_KEYWORD_SEGMENT),
            "Straight_joinKeywordSegment" => Some(&STRAIGHT_JOIN_KEYWORD_SEGMENT),
            "StreamKeywordSegment" => Some(&STREAM_KEYWORD_SEGMENT),
            "StreamsKeywordSegment" => Some(&STREAMS_KEYWORD_SEGMENT),
            "StrictKeywordSegment" => Some(&STRICT_KEYWORD_SEGMENT),
            "StringBinaryOperatorGrammar" => Some(&STRING_BINARY_OPERATOR_GRAMMAR),
            "StringKeywordSegment" => Some(&STRING_KEYWORD_SEGMENT),
            "StructLiteralSegment" => Some(&STRUCT_LITERAL_SEGMENT),
            "StructTypeSegment" => Some(&STRUCT_TYPE_SEGMENT),
            "StructureKeywordSegment" => Some(&STRUCTURE_KEYWORD_SEGMENT),
            "StyleKeywordSegment" => Some(&STYLE_KEYWORD_SEGMENT),
            "Subclass_originKeywordSegment" => Some(&SUBCLASS_ORIGIN_KEYWORD_SEGMENT),
            "SublistKeywordSegment" => Some(&SUBLIST_KEYWORD_SEGMENT),
            "SubmultisetKeywordSegment" => Some(&SUBMULTISET_KEYWORD_SEGMENT),
            "SubstringKeywordSegment" => Some(&SUBSTRING_KEYWORD_SEGMENT),
            "SuccessfulKeywordSegment" => Some(&SUCCESSFUL_KEYWORD_SEGMENT),
            "SumKeywordSegment" => Some(&SUM_KEYWORD_SEGMENT),
            "SuperuserKeywordSegment" => Some(&SUPERUSER_KEYWORD_SEGMENT),
            "SymbolSegment" => Some(&SYMBOL_SEGMENT),
            "SymmetricKeywordSegment" => Some(&SYMMETRIC_KEYWORD_SEGMENT),
            "SynonymKeywordSegment" => Some(&SYNONYM_KEYWORD_SEGMENT),
            "SysdateKeywordSegment" => Some(&SYSDATE_KEYWORD_SEGMENT),
            "SysidKeywordSegment" => Some(&SYSID_KEYWORD_SEGMENT),
            "SystemKeywordSegment" => Some(&SYSTEM_KEYWORD_SEGMENT),
            "System_userKeywordSegment" => Some(&SYSTEM_USER_KEYWORD_SEGMENT),
            "TableConstraintSegment" => Some(&TABLE_CONSTRAINT_SEGMENT),
            "TableEndClauseSegment" => Some(&TABLE_END_CLAUSE_SEGMENT),
            "TableExpressionSegment" => Some(&TABLE_EXPRESSION_SEGMENT),
            "TableKeywordSegment" => Some(&TABLE_KEYWORD_SEGMENT),
            "TableReferenceSegment" => Some(&TABLE_REFERENCE_SEGMENT),
            "Table_nameKeywordSegment" => Some(&TABLE_NAME_KEYWORD_SEGMENT),
            "TablesKeywordSegment" => Some(&TABLES_KEYWORD_SEGMENT),
            "TablesampleKeywordSegment" => Some(&TABLESAMPLE_KEYWORD_SEGMENT),
            "TablespaceKeywordSegment" => Some(&TABLESPACE_KEYWORD_SEGMENT),
            "TablespaceReferenceSegment" => Some(&TABLESPACE_REFERENCE_SEGMENT),
            "TagReferenceSegment" => Some(&TAG_REFERENCE_SEGMENT),
            "Tail_Recurse_Expression_A_Grammar" => Some(&TAIL_RECURSE_EXPRESSION_A_GRAMMAR),
            "Tail_Recurse_Expression_B_Grammar" => Some(&TAIL_RECURSE_EXPRESSION_B_GRAMMAR),
            "TaskKeywordSegment" => Some(&TASK_KEYWORD_SEGMENT),
            "TasksKeywordSegment" => Some(&TASKS_KEYWORD_SEGMENT),
            "TempKeywordSegment" => Some(&TEMP_KEYWORD_SEGMENT),
            "TemplateKeywordSegment" => Some(&TEMPLATE_KEYWORD_SEGMENT),
            "TemporalQuerySegment" => Some(&TEMPORAL_QUERY_SEGMENT),
            "TemporaryGrammar" => Some(&TEMPORARY_GRAMMAR),
            "TemporaryKeywordSegment" => Some(&TEMPORARY_KEYWORD_SEGMENT),
            "TemporaryTransientGrammar" => Some(&TEMPORARY_TRANSIENT_GRAMMAR),
            "TerminateKeywordSegment" => Some(&TERMINATE_KEYWORD_SEGMENT),
            "TerminatedKeywordSegment" => Some(&TERMINATED_KEYWORD_SEGMENT),
            "TextKeywordSegment" => Some(&TEXT_KEYWORD_SEGMENT),
            "TextsizeKeywordSegment" => Some(&TEXTSIZE_KEYWORD_SEGMENT),
            "ThanKeywordSegment" => Some(&THAN_KEYWORD_SEGMENT),
            "ThenKeywordSegment" => Some(&THEN_KEYWORD_SEGMENT),
            "TiesKeywordSegment" => Some(&TIES_KEYWORD_SEGMENT),
            "TildeSegment" => Some(&TILDE_SEGMENT),
            "TimeKeywordSegment" => Some(&TIME_KEYWORD_SEGMENT),
            "TimeWithTZGrammar" => Some(&TIME_WITH_T_Z_GRAMMAR),
            "TimeZoneGrammar" => Some(&TIME_ZONE_GRAMMAR),
            "TimestampKeywordSegment" => Some(&TIMESTAMP_KEYWORD_SEGMENT),
            "Timezone_hourKeywordSegment" => Some(&TIMEZONE_HOUR_KEYWORD_SEGMENT),
            "Timezone_minuteKeywordSegment" => Some(&TIMEZONE_MINUTE_KEYWORD_SEGMENT),
            "TinyblobKeywordSegment" => Some(&TINYBLOB_KEYWORD_SEGMENT),
            "TinyintKeywordSegment" => Some(&TINYINT_KEYWORD_SEGMENT),
            "TinytextKeywordSegment" => Some(&TINYTEXT_KEYWORD_SEGMENT),
            "ToKeywordSegment" => Some(&TO_KEYWORD_SEGMENT),
            "ToastKeywordSegment" => Some(&TOAST_KEYWORD_SEGMENT),
            "TopKeywordSegment" => Some(&TOP_KEYWORD_SEGMENT),
            "Top_level_countKeywordSegment" => Some(&TOP_LEVEL_COUNT_KEYWORD_SEGMENT),
            "TrailingKeywordSegment" => Some(&TRAILING_KEYWORD_SEGMENT),
            "TranKeywordSegment" => Some(&TRAN_KEYWORD_SEGMENT),
            "TransactionKeywordSegment" => Some(&TRANSACTION_KEYWORD_SEGMENT),
            "TransactionStatementSegment" => Some(&TRANSACTION_STATEMENT_SEGMENT),
            "Transaction_activeKeywordSegment" => Some(&TRANSACTION_ACTIVE_KEYWORD_SEGMENT),
            "TransactionsKeywordSegment" => Some(&TRANSACTIONS_KEYWORD_SEGMENT),
            "Transactions_committedKeywordSegment" => Some(&TRANSACTIONS_COMMITTED_KEYWORD_SEGMENT),
            "Transactions_rolled_backKeywordSegment" => Some(&TRANSACTIONS_ROLLED_BACK_KEYWORD_SEGMENT),
            "TransformKeywordSegment" => Some(&TRANSFORM_KEYWORD_SEGMENT),
            "TransformsKeywordSegment" => Some(&TRANSFORMS_KEYWORD_SEGMENT),
            "TransientKeywordSegment" => Some(&TRANSIENT_KEYWORD_SEGMENT),
            "TranslateKeywordSegment" => Some(&TRANSLATE_KEYWORD_SEGMENT),
            "TranslationKeywordSegment" => Some(&TRANSLATION_KEYWORD_SEGMENT),
            "TreatKeywordSegment" => Some(&TREAT_KEYWORD_SEGMENT),
            "TriggerKeywordSegment" => Some(&TRIGGER_KEYWORD_SEGMENT),
            "TriggerReferenceSegment" => Some(&TRIGGER_REFERENCE_SEGMENT),
            "Trigger_catalogKeywordSegment" => Some(&TRIGGER_CATALOG_KEYWORD_SEGMENT),
            "Trigger_nameKeywordSegment" => Some(&TRIGGER_NAME_KEYWORD_SEGMENT),
            "Trigger_schemaKeywordSegment" => Some(&TRIGGER_SCHEMA_KEYWORD_SEGMENT),
            "TrimKeywordSegment" => Some(&TRIM_KEYWORD_SEGMENT),
            "TrimParametersGrammar" => Some(&TRIM_PARAMETERS_GRAMMAR),
            "TrueKeywordSegment" => Some(&TRUE_KEYWORD_SEGMENT),
            "TrueSegment" => Some(&TRUE_SEGMENT),
            "TruncateKeywordSegment" => Some(&TRUNCATE_KEYWORD_SEGMENT),
            "TruncateStatementSegment" => Some(&TRUNCATE_STATEMENT_SEGMENT),
            "TrustedKeywordSegment" => Some(&TRUSTED_KEYWORD_SEGMENT),
            "TsequalKeywordSegment" => Some(&TSEQUAL_KEYWORD_SEGMENT),
            "TupleSegment" => Some(&TUPLE_SEGMENT),
            "TypeKeywordSegment" => Some(&TYPE_KEYWORD_SEGMENT),
            "TypedArrayLiteralSegment" => Some(&TYPED_ARRAY_LITERAL_SEGMENT),
            "TypedStructLiteralSegment" => Some(&TYPED_STRUCT_LITERAL_SEGMENT),
            "UescapeKeywordSegment" => Some(&UESCAPE_KEYWORD_SEGMENT),
            "UidKeywordSegment" => Some(&UID_KEYWORD_SEGMENT),
            "UnboundedKeywordSegment" => Some(&UNBOUNDED_KEYWORD_SEGMENT),
            "UncommittedKeywordSegment" => Some(&UNCOMMITTED_KEYWORD_SEGMENT),
            "UnconditionalCrossJoinKeywordsGrammar" => Some(&UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR),
            "UnconditionalJoinKeywordsGrammar" => Some(&UNCONDITIONAL_JOIN_KEYWORDS_GRAMMAR),
            "UnderKeywordSegment" => Some(&UNDER_KEYWORD_SEGMENT),
            "UndoKeywordSegment" => Some(&UNDO_KEYWORD_SEGMENT),
            "UnencryptedKeywordSegment" => Some(&UNENCRYPTED_KEYWORD_SEGMENT),
            "UnionGrammar" => Some(&UNION_GRAMMAR),
            "UnionKeywordSegment" => Some(&UNION_KEYWORD_SEGMENT),
            "UniqueKeyGrammar" => Some(&UNIQUE_KEY_GRAMMAR),
            "UniqueKeywordSegment" => Some(&UNIQUE_KEYWORD_SEGMENT),
            "UnknownKeywordSegment" => Some(&UNKNOWN_KEYWORD_SEGMENT),
            "UnknownLiteralSegment" => Some(&UNKNOWN_LITERAL_SEGMENT),
            "UnlistenKeywordSegment" => Some(&UNLISTEN_KEYWORD_SEGMENT),
            "UnlockKeywordSegment" => Some(&UNLOCK_KEYWORD_SEGMENT),
            "UnnamedKeywordSegment" => Some(&UNNAMED_KEYWORD_SEGMENT),
            "UnnestKeywordSegment" => Some(&UNNEST_KEYWORD_SEGMENT),
            "UnorderedSelectStatementSegment" => Some(&UNORDERED_SELECT_STATEMENT_SEGMENT),
            "UnorderedSetExpressionSegment" => Some(&UNORDERED_SET_EXPRESSION_SEGMENT),
            "UnsignedKeywordSegment" => Some(&UNSIGNED_KEYWORD_SEGMENT),
            "UntilKeywordSegment" => Some(&UNTIL_KEYWORD_SEGMENT),
            "UpdateKeywordSegment" => Some(&UPDATE_KEYWORD_SEGMENT),
            "UpdateStatementSegment" => Some(&UPDATE_STATEMENT_SEGMENT),
            "UpdatetextKeywordSegment" => Some(&UPDATETEXT_KEYWORD_SEGMENT),
            "UpperKeywordSegment" => Some(&UPPER_KEYWORD_SEGMENT),
            "UsageKeywordSegment" => Some(&USAGE_KEYWORD_SEGMENT),
            "UseKeywordSegment" => Some(&USE_KEYWORD_SEGMENT),
            "UseStatementSegment" => Some(&USE_STATEMENT_SEGMENT),
            "Use_any_roleKeywordSegment" => Some(&USE_ANY_ROLE_KEYWORD_SEGMENT),
            "UserKeywordSegment" => Some(&USER_KEYWORD_SEGMENT),
            "User_defined_type_catalogKeywordSegment" => Some(&USER_DEFINED_TYPE_CATALOG_KEYWORD_SEGMENT),
            "User_defined_type_codeKeywordSegment" => Some(&USER_DEFINED_TYPE_CODE_KEYWORD_SEGMENT),
            "User_defined_type_nameKeywordSegment" => Some(&USER_DEFINED_TYPE_NAME_KEYWORD_SEGMENT),
            "User_defined_type_schemaKeywordSegment" => Some(&USER_DEFINED_TYPE_SCHEMA_KEYWORD_SEGMENT),
            "UsersKeywordSegment" => Some(&USERS_KEYWORD_SEGMENT),
            "UsingKeywordSegment" => Some(&USING_KEYWORD_SEGMENT),
            "Utc_dateKeywordSegment" => Some(&UTC_DATE_KEYWORD_SEGMENT),
            "Utc_timeKeywordSegment" => Some(&UTC_TIME_KEYWORD_SEGMENT),
            "Utc_timestampKeywordSegment" => Some(&UTC_TIMESTAMP_KEYWORD_SEGMENT),
            "VacuumKeywordSegment" => Some(&VACUUM_KEYWORD_SEGMENT),
            "ValidKeywordSegment" => Some(&VALID_KEYWORD_SEGMENT),
            "ValidateKeywordSegment" => Some(&VALIDATE_KEYWORD_SEGMENT),
            "ValidatorKeywordSegment" => Some(&VALIDATOR_KEYWORD_SEGMENT),
            "ValueKeywordSegment" => Some(&VALUE_KEYWORD_SEGMENT),
            "ValuesClauseSegment" => Some(&VALUES_CLAUSE_SEGMENT),
            "ValuesKeywordSegment" => Some(&VALUES_KEYWORD_SEGMENT),
            "Var_popKeywordSegment" => Some(&VAR_POP_KEYWORD_SEGMENT),
            "Var_sampKeywordSegment" => Some(&VAR_SAMP_KEYWORD_SEGMENT),
            "VarbinaryKeywordSegment" => Some(&VARBINARY_KEYWORD_SEGMENT),
            "Varchar2KeywordSegment" => Some(&VARCHAR2_KEYWORD_SEGMENT),
            "VarcharKeywordSegment" => Some(&VARCHAR_KEYWORD_SEGMENT),
            "VarcharacterKeywordSegment" => Some(&VARCHARACTER_KEYWORD_SEGMENT),
            "VariableKeywordSegment" => Some(&VARIABLE_KEYWORD_SEGMENT),
            "VariablesKeywordSegment" => Some(&VARIABLES_KEYWORD_SEGMENT),
            "VaryingKeywordSegment" => Some(&VARYING_KEYWORD_SEGMENT),
            "VerboseKeywordSegment" => Some(&VERBOSE_KEYWORD_SEGMENT),
            "VersionKeywordSegment" => Some(&VERSION_KEYWORD_SEGMENT),
            "ViewKeywordSegment" => Some(&VIEW_KEYWORD_SEGMENT),
            "ViewsKeywordSegment" => Some(&VIEWS_KEYWORD_SEGMENT),
            "VolatileKeywordSegment" => Some(&VOLATILE_KEYWORD_SEGMENT),
            "WaitforKeywordSegment" => Some(&WAITFOR_KEYWORD_SEGMENT),
            "WarehouseKeywordSegment" => Some(&WAREHOUSE_KEYWORD_SEGMENT),
            "WarehousesKeywordSegment" => Some(&WAREHOUSES_KEYWORD_SEGMENT),
            "WeekKeywordSegment" => Some(&WEEK_KEYWORD_SEGMENT),
            "WeekdayKeywordSegment" => Some(&WEEKDAY_KEYWORD_SEGMENT),
            "WhenClauseSegment" => Some(&WHEN_CLAUSE_SEGMENT),
            "WhenKeywordSegment" => Some(&WHEN_KEYWORD_SEGMENT),
            "WheneverKeywordSegment" => Some(&WHENEVER_KEYWORD_SEGMENT),
            "WhereClauseSegment" => Some(&WHERE_CLAUSE_SEGMENT),
            "WhereClauseTerminatorGrammar" => Some(&WHERE_CLAUSE_TERMINATOR_GRAMMAR),
            "WhereKeywordSegment" => Some(&WHERE_KEYWORD_SEGMENT),
            "WhileKeywordSegment" => Some(&WHILE_KEYWORD_SEGMENT),
            "WhitespaceSegment" => Some(&WHITESPACE_SEGMENT),
            "Width_bucketKeywordSegment" => Some(&WIDTH_BUCKET_KEYWORD_SEGMENT),
            "WildcardExpressionSegment" => Some(&WILDCARD_EXPRESSION_SEGMENT),
            "WildcardIdentifierSegment" => Some(&WILDCARD_IDENTIFIER_SEGMENT),
            "WindowKeywordSegment" => Some(&WINDOW_KEYWORD_SEGMENT),
            "WindowSpecificationSegment" => Some(&WINDOW_SPECIFICATION_SEGMENT),
            "WithCompoundNonSelectStatementSegment" => Some(&WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT),
            "WithCompoundStatementSegment" => Some(&WITH_COMPOUND_STATEMENT_SEGMENT),
            "WithDataClauseSegment" => Some(&WITH_DATA_CLAUSE_SEGMENT),
            "WithFillSegment" => Some(&WITH_FILL_SEGMENT),
            "WithKeywordSegment" => Some(&WITH_KEYWORD_SEGMENT),
            "WithNoSchemaBindingClauseSegment" => Some(&WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT),
            "WithinKeywordSegment" => Some(&WITHIN_KEYWORD_SEGMENT),
            "WithoutKeywordSegment" => Some(&WITHOUT_KEYWORD_SEGMENT),
            "WordSegment" => Some(&WORD_SEGMENT),
            "WorkKeywordSegment" => Some(&WORK_KEYWORD_SEGMENT),
            "WrapperKeywordSegment" => Some(&WRAPPER_KEYWORD_SEGMENT),
            "WriteKeywordSegment" => Some(&WRITE_KEYWORD_SEGMENT),
            "WritetextKeywordSegment" => Some(&WRITETEXT_KEYWORD_SEGMENT),
            "X509KeywordSegment" => Some(&X509_KEYWORD_SEGMENT),
            "XmlKeywordSegment" => Some(&XML_KEYWORD_SEGMENT),
            "XorKeywordSegment" => Some(&XOR_KEYWORD_SEGMENT),
            "YamlKeywordSegment" => Some(&YAML_KEYWORD_SEGMENT),
            "YearKeywordSegment" => Some(&YEAR_KEYWORD_SEGMENT),
            "Year_monthKeywordSegment" => Some(&YEAR_MONTH_KEYWORD_SEGMENT),
            "ZerofillKeywordSegment" => Some(&ZEROFILL_KEYWORD_SEGMENT),
            "ZoneKeywordSegment" => Some(&ZONE_KEYWORD_SEGMENT),
            _ => None,
    }
}

pub fn get_ansi_segment_type(name: &str) -> Option<&'static str> {
    match name {
            "AccessStatementSegment" => Some("access_statement"),
            "AggregateOrderByClause" => Some("aggregate_order_by"),
            "AliasExpressionSegment" => Some("alias_expression"),
            "AlterSequenceOptionsSegment" => Some("alter_sequence_options_segment"),
            "AlterSequenceStatementSegment" => Some("alter_sequence_statement"),
            "AlterTableStatementSegment" => Some("alter_table_statement"),
            "ArrayAccessorSegment" => Some("array_accessor"),
            "ArrayExpressionSegment" => Some("array_expression"),
            "ArrayLiteralSegment" => Some("array_literal"),
            "ArrayTypeSegment" => Some("array_type"),
            "AsAliasOperatorSegment" => Some("alias_operator"),
            "BaseFileSegment" => Some("file"),
            "BaseSegment" => Some("base"),
            "BinaryOperatorSegment" => Some("binary_operator"),
            "BitwiseAndSegment" => Some("binary_operator"),
            "BitwiseLShiftSegment" => Some("binary_operator"),
            "BitwiseOrSegment" => Some("binary_operator"),
            "BitwiseRShiftSegment" => Some("binary_operator"),
            "BracketedArguments" => Some("bracketed_arguments"),
            "BracketedSegment" => Some("bracketed"),
            "CTEColumnList" => Some("cte_column_list"),
            "CTEDefinitionSegment" => Some("common_table_expression"),
            "CaseExpressionSegment" => Some("case_expression"),
            "CodeSegment" => Some("raw"),
            "CollationReferenceSegment" => Some("collation_reference"),
            "ColumnConstraintSegment" => Some("column_constraint_segment"),
            "ColumnDefinitionSegment" => Some("column_definition"),
            "ColumnReferenceSegment" => Some("column_reference"),
            "ColumnsExpressionFunctionContentsSegment" => Some("columns_expression"),
            "ColumnsExpressionFunctionNameSegment" => Some("function_name"),
            "CommentClauseSegment" => Some("comment_clause"),
            "CommentSegment" => Some("comment"),
            "ComparisonOperatorSegment" => Some("comparison_operator"),
            "CompositeBinaryOperatorSegment" => Some("binary_operator"),
            "CompositeComparisonOperatorSegment" => Some("comparison_operator"),
            "ConcatSegment" => Some("binary_operator"),
            "CreateCastStatementSegment" => Some("create_cast_statement"),
            "CreateDatabaseStatementSegment" => Some("create_database_statement"),
            "CreateFunctionStatementSegment" => Some("create_function_statement"),
            "CreateIndexStatementSegment" => Some("create_index_statement"),
            "CreateModelStatementSegment" => Some("create_model_statement"),
            "CreateRoleStatementSegment" => Some("create_role_statement"),
            "CreateSchemaStatementSegment" => Some("create_schema_statement"),
            "CreateSequenceOptionsSegment" => Some("create_sequence_options_segment"),
            "CreateSequenceStatementSegment" => Some("create_sequence_statement"),
            "CreateTableStatementSegment" => Some("create_table_statement"),
            "CreateTriggerStatementSegment" => Some("create_trigger"),
            "CreateUserStatementSegment" => Some("create_user_statement"),
            "CreateViewStatementSegment" => Some("create_view_statement"),
            "CubeFunctionNameSegment" => Some("function_name"),
            "CubeRollupClauseSegment" => Some("cube_rollup_clause"),
            "DatabaseReferenceSegment" => Some("database_reference"),
            "DatatypeSegment" => Some("data_type"),
            "DatePartFunctionNameSegment" => Some("function_name"),
            "DateTimeFunctionContentsSegment" => Some("function_contents"),
            "Dedent" => Some("dedent"),
            "DeleteStatementSegment" => Some("delete_statement"),
            "DescribeStatementSegment" => Some("describe_statement"),
            "DropCastStatementSegment" => Some("drop_cast_statement"),
            "DropDatabaseStatementSegment" => Some("drop_database_statement"),
            "DropFunctionStatementSegment" => Some("drop_function_statement"),
            "DropIndexStatementSegment" => Some("drop_index_statement"),
            "DropModelStatementSegment" => Some("drop_MODELstatement"),
            "DropRoleStatementSegment" => Some("drop_role_statement"),
            "DropSchemaStatementSegment" => Some("drop_schema_statement"),
            "DropSequenceStatementSegment" => Some("drop_sequence_statement"),
            "DropTableStatementSegment" => Some("drop_table_statement"),
            "DropTriggerStatementSegment" => Some("drop_trigger"),
            "DropTypeStatementSegment" => Some("drop_type_statement"),
            "DropUserStatementSegment" => Some("drop_user_statement"),
            "DropViewStatementSegment" => Some("drop_view_statement"),
            "ElseClauseSegment" => Some("else_clause"),
            "EmptyStructLiteralBracketsSegment" => Some("struct_literal"),
            "EmptyStructLiteralSegment" => Some("typed_struct_literal"),
            "EqualsSegment" => Some("comparison_operator"),
            "ExplainStatementSegment" => Some("explain_statement"),
            "ExpressionSegment" => Some("expression"),
            "ExtensionReferenceSegment" => Some("extension_reference"),
            "FetchClauseSegment" => Some("fetch_clause"),
            "FileSegment" => Some("file"),
            "FrameClauseSegment" => Some("frame_clause"),
            "FromClauseSegment" => Some("from_clause"),
            "FromExpressionElementSegment" => Some("from_expression_element"),
            "FromExpressionSegment" => Some("from_expression"),
            "FunctionContentsSegment" => Some("function_contents"),
            "FunctionDefinitionGrammar" => Some("function_definition"),
            "FunctionNameSegment" => Some("function_name"),
            "FunctionParameterListGrammar" => Some("function_parameter_list"),
            "FunctionSegment" => Some("function"),
            "GreaterThanOrEqualToSegment" => Some("comparison_operator"),
            "GreaterThanSegment" => Some("comparison_operator"),
            "GroupByClauseSegment" => Some("groupby_clause"),
            "GroupingExpressionList" => Some("grouping_expression_list"),
            "GroupingSetsClauseSegment" => Some("grouping_sets_clause"),
            "HavingClauseSegment" => Some("having_clause"),
            "IdentifierSegment" => Some("identifier"),
            "ImplicitIndent" => Some("indent"),
            "Indent" => Some("indent"),
            "IndexColumnDefinitionSegment" => Some("index_column_definition"),
            "IndexReferenceSegment" => Some("index_reference"),
            "InsertStatementSegment" => Some("insert_statement"),
            "IntervalExpressionSegment" => Some("interval_expression"),
            "JoinClauseSegment" => Some("join_clause"),
            "JoinOnConditionSegment" => Some("join_on_condition"),
            "KeywordSegment" => Some("keyword"),
            "LessThanOrEqualToSegment" => Some("comparison_operator"),
            "LessThanSegment" => Some("comparison_operator"),
            "LimitClauseSegment" => Some("limit_clause"),
            "LiteralKeywordSegment" => Some("literal"),
            "LiteralSegment" => Some("literal"),
            "LocalAliasSegment" => Some("local_alias_segment"),
            "MLTableExpressionSegment" => Some("ml_table_expression"),
            "MapTypeSegment" => Some("map_type"),
            "MatchConditionSegment" => Some("match_condition"),
            "MergeDeleteClauseSegment" => Some("merge_delete_clause"),
            "MergeInsertClauseSegment" => Some("merge_insert_clause"),
            "MergeMatchSegment" => Some("merge_match"),
            "MergeMatchedClauseSegment" => Some("merge_when_matched_clause"),
            "MergeNotMatchedClauseSegment" => Some("merge_when_not_matched_clause"),
            "MergeStatementSegment" => Some("merge_statement"),
            "MergeUpdateClauseSegment" => Some("merge_update_clause"),
            "NamedWindowExpressionSegment" => Some("named_window_expression"),
            "NamedWindowSegment" => Some("named_window"),
            "NewlineSegment" => Some("newline"),
            "NotEqualToSegment" => Some("comparison_operator"),
            "ObjectLiteralElementSegment" => Some("object_literal_element"),
            "ObjectLiteralSegment" => Some("object_literal"),
            "ObjectReferenceSegment" => Some("object_reference"),
            "OffsetClauseSegment" => Some("offset_clause"),
            "OrderByClauseSegment" => Some("orderby_clause"),
            "OverClauseSegment" => Some("over_clause"),
            "OverlapsClauseSegment" => Some("overlaps_clause"),
            "PartitionClauseSegment" => Some("partitionby_clause"),
            "PathSegment" => Some("path_segment"),
            "QualifiedNumericLiteralSegment" => Some("numeric_literal"),
            "RawSegment" => Some("raw"),
            "RoleReferenceSegment" => Some("role_reference"),
            "RollupFunctionNameSegment" => Some("function_name"),
            "SamplingExpressionSegment" => Some("sample_expression"),
            "SchemaReferenceSegment" => Some("schema_reference"),
            "SelectClauseElementSegment" => Some("select_clause_element"),
            "SelectClauseModifierSegment" => Some("select_clause_modifier"),
            "SelectClauseSegment" => Some("select_clause"),
            "SelectStatementSegment" => Some("select_statement"),
            "SequenceReferenceSegment" => Some("sequence_reference"),
            "SetClauseListSegment" => Some("set_clause_list"),
            "SetClauseSegment" => Some("set_clause"),
            "SetExpressionSegment" => Some("set_expression"),
            "SetOperatorSegment" => Some("set_operator"),
            "SetSchemaStatementSegment" => Some("set_schema_statement"),
            "ShorthandCastSegment" => Some("cast_expression"),
            "SingleIdentifierListSegment" => Some("identifier_list"),
            "SizedArrayTypeSegment" => Some("sized_array_type"),
            "StatementSegment" => Some("statement"),
            "StructLiteralSegment" => Some("struct_literal"),
            "StructTypeSegment" => Some("struct_type"),
            "SymbolSegment" => Some("symbol"),
            "TableConstraintSegment" => Some("table_constraint"),
            "TableEndClauseSegment" => Some("table_end_clause_segment"),
            "TableExpressionSegment" => Some("table_expression"),
            "TableReferenceSegment" => Some("table_reference"),
            "TablespaceReferenceSegment" => Some("tablespace_reference"),
            "TagReferenceSegment" => Some("tag_reference"),
            "TemporalQuerySegment" => Some("temporal_query"),
            "TimeZoneGrammar" => Some("time_zone_grammar"),
            "TransactionStatementSegment" => Some("transaction_statement"),
            "TriggerReferenceSegment" => Some("trigger_reference"),
            "TruncateStatementSegment" => Some("truncate_table"),
            "TupleSegment" => Some("tuple"),
            "TypedArrayLiteralSegment" => Some("typed_array_literal"),
            "TypedStructLiteralSegment" => Some("typed_struct_literal"),
            "UnorderedSelectStatementSegment" => Some("select_statement"),
            "UnorderedSetExpressionSegment" => Some("set_expression"),
            "UpdateStatementSegment" => Some("update_statement"),
            "UseStatementSegment" => Some("use_statement"),
            "ValuesClauseSegment" => Some("values_clause"),
            "WhenClauseSegment" => Some("when_clause"),
            "WhereClauseSegment" => Some("where_clause"),
            "WhitespaceSegment" => Some("whitespace"),
            "WildcardExpressionSegment" => Some("wildcard_expression"),
            "WildcardIdentifierSegment" => Some("wildcard_identifier"),
            "WindowSpecificationSegment" => Some("window_specification"),
            "WithCompoundNonSelectStatementSegment" => Some("with_compound_statement"),
            "WithCompoundStatementSegment" => Some("with_compound_statement"),
            "WithDataClauseSegment" => Some("with_data_clause"),
            "WithFillSegment" => Some("with_fill"),
            "WithNoSchemaBindingClauseSegment" => Some("with_no_schema_binding_clause"),
            "WordSegment" => Some("word"),
            _ => None,
    }
}
