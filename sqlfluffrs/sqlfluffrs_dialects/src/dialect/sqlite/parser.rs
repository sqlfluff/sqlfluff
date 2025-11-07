/* This is a generated file! */
#![cfg_attr(rustfmt, rustfmt_skip)]
use std::sync::Arc;
use once_cell::sync::Lazy;
use sqlfluffrs_types::{Grammar, ParseMode, SimpleHint};
use sqlfluffrs_types::regex::RegexMode;

// name='AbortKeywordSegment'
pub static ABORT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ABORT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AccessStatementSegment'
pub static ACCESS_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AccessStatementSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ManageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PipeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "Reference_usageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRIGGER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AccountKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ResourceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TablespaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ShareKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PublicKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AdminKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CopyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GrantedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Current_userKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "Session_userKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RevokeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GrantKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OptionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ManageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "GrantsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExecutionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaskingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PolicyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PipeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ImportedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ApplyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ConnectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExecuteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ModifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OperateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ReadKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "Reference_usageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRIGGER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UsageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "Use_any_roleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WriteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrivilegesKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AccountKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ResourceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MonitorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WarehouseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DomainKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IntegrationKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CatalogKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TablespaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ServerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WrapperKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SchemasKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TaskKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaterializedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATERIALIZED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExternalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FormatKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FutureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TablesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ViewsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StagesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProceduresKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoutinesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StreamsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TasksKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LargeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OwnershipKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ShareKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='AccessorGrammar'
pub static ACCESSOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ArrayAccessorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ActionKeywordSegment'
pub static ACTION_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ACTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AddKeywordSegment'
pub static ADD_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ADD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AfterKeywordSegment'
pub static AFTER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "AFTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AggregateOrderByClause'
pub static AGGREGATE_ORDER_BY_CLAUSE: Lazy<Arc<Grammar>> = Lazy::new(||
// AggregateOrderByClause
Arc::new(Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AliasExpressionSegment'
pub static ALIAS_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AliasExpressionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "AsAliasOperatorSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SingleQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='AliasedTableReferenceGrammar'
pub static ALIASED_TABLE_REFERENCE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='AllKeywordSegment'
pub static ALL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ALL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AlterKeywordSegment'
pub static ALTER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ALTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AlterSequenceOptionsSegment'
pub static ALTER_SEQUENCE_OPTIONS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AlterSequenceOptionsSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='AlterSequenceStatementSegment'
pub static ALTER_SEQUENCE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AlterSequenceStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AlterSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AlterTableDropColumnGrammar'
pub static ALTER_TABLE_DROP_COLUMN_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AlterTableOptionsGrammar'
pub static ALTER_TABLE_OPTIONS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RenameKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AddKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLUMN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ADD".to_string(), "DROP".to_string(), "RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AlterTableStatementSegment'
pub static ALTER_TABLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AlterTableStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AlterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AlterTableOptionsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ADD".to_string(), "DROP".to_string(), "RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ADD".to_string(), "DROP".to_string(), "RENAME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AlwaysKeywordSegment'
pub static ALWAYS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ALWAYS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AmpersandSegment'
pub static AMPERSAND_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "&",
    token_type: "ampersand",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='AnalyzeKeywordSegment'
pub static ANALYZE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ANALYZE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AndKeywordSegment'
pub static AND_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "AND",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AndOperatorGrammar'
pub static AND_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "AND",
    token_type: "binary_operator",
    raw_class: "BinaryOperatorSegment",
    optional: false,
})
);

// name='ArithmeticBinaryOperatorGrammar'
pub static ARITHMETIC_BINARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PlusSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MinusSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DivideSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["/".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MultiplySegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ModuloSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["%".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BitwiseAndSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["&".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BitwiseOrSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BitwiseXorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["^".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BitwiseLShiftSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BitwiseRShiftSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), ">".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ArrayAccessorSegment'
pub static ARRAY_ACCESSOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ArrayAccessorSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "SliceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([":".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ArrayExpressionSegment'
pub static ARRAY_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ArrayExpressionSegment
Arc::new(Grammar::Nothing())
);

// name='ArrayLiteralSegment'
pub static ARRAY_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ArrayLiteralSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: true,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ArrayTypeSegment'
pub static ARRAY_TYPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ArrayTypeSegment
Arc::new(Grammar::Nothing())
);

// name='AsAliasOperatorSegment'
pub static AS_ALIAS_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// AsAliasOperatorSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='AsKeywordSegment'
pub static AS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "AS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AscKeywordSegment'
pub static ASC_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ASC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AtSignLiteralSegment'
pub static AT_SIGN_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "at_sign_literal",
    token_type: "at_sign_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
);

// name='AttachKeywordSegment'
pub static ATTACH_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ATTACH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='AutoIncrementGrammar'
pub static AUTO_INCREMENT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='AutoincrementKeywordSegment'
pub static AUTOINCREMENT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "AUTOINCREMENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BackQuotedIdentifierSegment'
pub static BACK_QUOTED_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "back_quote",
    token_type: "quoted_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
})
);

// name='BareFunctionSegment'
pub static BARE_FUNCTION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::MultiStringParser {
    templates: vec!["CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP"],
    token_type: "bare_function",
    raw_class: "CodeSegment",
    optional: false,
})
);

// name='BaseExpressionElementGrammar'
pub static BASE_EXPRESSION_ELEMENT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT_DATE".to_string(), "CURRENT_TIME".to_string(), "CURRENT_TIMESTAMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='BaseFileSegment'
pub static BASE_FILE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "file",
//    token_type: "BaseFileSegment",
})
);

// name='BaseSegment'
pub static BASE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "base",
//    token_type: "BaseSegment",
})
);

// name='BeforeKeywordSegment'
pub static BEFORE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BEFORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BeginKeywordSegment'
pub static BEGIN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BEGIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BetweenKeywordSegment'
pub static BETWEEN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BETWEEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BigKeywordSegment'
pub static BIG_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BIG",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BigintKeywordSegment'
pub static BIGINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BIGINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BinaryKeywordSegment'
pub static BINARY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BINARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BinaryOperatorGrammar'
pub static BINARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ArithmeticBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), ">".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BooleanBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string(), "OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnPathOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["->".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InlinePathOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["->>".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
);

// name='BinaryOperatorSegment'
pub static BINARY_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "binary_operator",
//    token_type: "BinaryOperatorSegment",
})
);

// name='BitwiseAndSegment'
pub static BITWISE_AND_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// BitwiseAndSegment
Arc::new(Grammar::Ref {
    name: "AmpersandSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["&".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BitwiseLShiftSegment'
pub static BITWISE_L_SHIFT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// BitwiseLShiftSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BitwiseOrSegment'
pub static BITWISE_OR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// BitwiseOrSegment
Arc::new(Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BitwiseRShiftSegment'
pub static BITWISE_R_SHIFT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// BitwiseRShiftSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BitwiseXorSegment'
pub static BITWISE_XOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "^",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='BlobKeywordSegment'
pub static BLOB_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BooleanBinaryOperatorGrammar'
pub static BOOLEAN_BINARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AndOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string(), "OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BooleanKeywordSegment'
pub static BOOLEAN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BOOLEAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='BooleanLiteralGrammar'
pub static BOOLEAN_LITERAL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TrueSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FalseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BracketedArguments'
pub static BRACKETED_ARGUMENTS: Lazy<Arc<Grammar>> = Lazy::new(||
// BracketedArguments
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: true,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BracketedColumnReferenceListGrammar'
pub static BRACKETED_COLUMN_REFERENCE_LIST_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='BracketedSegment'
pub static BRACKETED_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "bracketed",
//    token_type: "BracketedSegment",
})
);

// name='BracketedSetExpressionGrammar'
pub static BRACKETED_SET_EXPRESSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnorderedSetExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ByKeywordSegment'
pub static BY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "BY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CTEColumnList'
pub static C_T_E_COLUMN_LIST: Lazy<Arc<Grammar>> = Lazy::new(||
// CTEColumnList
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierListSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CTEDefinitionSegment'
pub static C_T_E_DEFINITION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CTEDefinitionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CTEColumnList",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='CascadeKeywordSegment'
pub static CASCADE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CASCADE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CaseExpressionSegment'
pub static CASE_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CaseExpressionSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: true,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: true,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: true,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ElseClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: true,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CaseKeywordSegment'
pub static CASE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CastKeywordSegment'
pub static CAST_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CastOperatorSegment'
pub static CAST_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "::",
    token_type: "casting_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='CharCharacterSetGrammar'
pub static CHAR_CHARACTER_SET_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='CharacterKeywordSegment'
pub static CHARACTER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CHARACTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CheckKeywordSegment'
pub static CHECK_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CHECK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ClobKeywordSegment'
pub static CLOB_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CodeSegment'
pub static CODE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "raw",
//    token_type: "CodeSegment",
})
);

// name='CollateGrammar'
pub static COLLATE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='CollateKeywordSegment'
pub static COLLATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "COLLATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CollationReferenceSegment'
pub static COLLATION_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CollationReferenceSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ColonDelimiterSegment'
pub static COLON_DELIMITER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ":",
    token_type: "colon_delimiter",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ColonLiteralSegment'
pub static COLON_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "colon_literal",
    token_type: "colon_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
);

// name='ColonPrefixSegment'
pub static COLON_PREFIX_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ":",
    token_type: "colon_prefix",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ColonSegment'
pub static COLON_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ":",
    token_type: "colon",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ColumnConstraintDefaultGrammar'
pub static COLUMN_CONSTRAINT_DEFAULT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
);

// name='ColumnConstraintSegment'
pub static COLUMN_CONSTRAINT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ColumnConstraintSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONSTRAINT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONSTRAINT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string(), "NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CheckKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnConstraintDefaultGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRIMARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UniqueKeyGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AutoIncrementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommentClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CollateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLLATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CollationReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COLLATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GeneratedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GENERATED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AlwaysKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALWAYS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GENERATED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StoredKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["STORED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIRTUAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["STORED".to_string(), "VIRTUAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string(), "GENERATED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeferredKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ImmediateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IMMEDIATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ColumnDefinitionSegment'
pub static COLUMN_DEFINITION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ColumnDefinitionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Anything)
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnConstraintSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ColumnGeneratedGrammar'
pub static COLUMN_GENERATED_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='ColumnKeywordSegment'
pub static COLUMN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "COLUMN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ColumnPathOperatorSegment'
pub static COLUMN_PATH_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "->",
    token_type: "column_path_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ColumnReferenceSegment'
pub static COLUMN_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ColumnReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT_DATE".to_string(), "CURRENT_TIME".to_string(), "CURRENT_TIMESTAMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ColumnsExpressionFunctionContentsSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ColumnsExpressionFunctionContentsSegment
Arc::new(Grammar::Nothing())
);

// name='ColumnsExpressionFunctionNameSegment'
pub static COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ColumnsExpressionFunctionNameSegment
Arc::new(Grammar::Ref {
    name: "ColumnsExpressionNameGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
);

// name='ColumnsExpressionGrammar'
pub static COLUMNS_EXPRESSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='ColumnsExpressionNameGrammar'
pub static COLUMNS_EXPRESSION_NAME_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='CommaSegment'
pub static COMMA_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ",",
    token_type: "comma",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='CommentClauseSegment'
pub static COMMENT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='CommentSegment'
pub static COMMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "comment",
//    token_type: "CommentSegment",
})
);

// name='CommitKeywordSegment'
pub static COMMIT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "COMMIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ComparisonOperatorGrammar'
pub static COMPARISON_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GreaterThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LessThanOrEqualToSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotEqualToSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LikeOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IsDistinctFromGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
);

// name='ComparisonOperatorSegment'
pub static COMPARISON_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "comparison_operator",
//    token_type: "ComparisonOperatorSegment",
})
);

// name='CompositeBinaryOperatorSegment'
pub static COMPOSITE_BINARY_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "binary_operator",
//    token_type: "CompositeBinaryOperatorSegment",
})
);

// name='CompositeComparisonOperatorSegment'
pub static COMPOSITE_COMPARISON_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "comparison_operator",
//    token_type: "CompositeComparisonOperatorSegment",
})
);

// name='ConcatSegment'
pub static CONCAT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ConcatSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PipeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ConditionalCrossJoinKeywordsGrammar'
pub static CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Ref {
    name: "CrossKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CROSS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ConditionalJoinKeywordsGrammar'
pub static CONDITIONAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string(), "INNER".to_string(), "LEFT".to_string(), "RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CROSS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NonStandardJoinTypeKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ConflictClauseSegment'
pub static CONFLICT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ConflictClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONFLICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAIL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IGNORE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "IGNORE".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ConflictKeywordSegment'
pub static CONFLICT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CONFLICT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ConflictTargetSegment'
pub static CONFLICT_TARGET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ConflictTargetSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ConstraintKeywordSegment'
pub static CONSTRAINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CONSTRAINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CreateCastStatementSegment'
pub static CREATE_CAST_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateCastStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SpecificKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RoutineKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ProcedureKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InstanceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StaticKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ConstructorKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MethodKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AssignmentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateDatabaseStatementSegment'
pub static CREATE_DATABASE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateDatabaseStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateFunctionStatementSegment'
pub static CREATE_FUNCTION_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateFunctionStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionParameterListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ReturnsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateIndexStatementSegment'
pub static CREATE_INDEX_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateIndexStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INDEX".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateKeywordSegment'
pub static CREATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CREATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CreateModelStatementSegment'
pub static CREATE_MODEL_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateModelStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OptionsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ParameterNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateRoleStatementSegment'
pub static CREATE_ROLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateRoleStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateSchemaStatementSegment'
pub static CREATE_SCHEMA_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateSchemaStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateSequenceOptionsSegment'
pub static CREATE_SEQUENCE_OPTIONS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateSequenceOptionsSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IncrementKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StartKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceMinValueGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceMaxValueGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NocacheKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NocycleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OrderNoOrderGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='CreateSequenceStatementSegment'
pub static CREATE_SEQUENCE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateSequenceStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateSequenceOptionsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateTableStatementSegment'
pub static CREATE_TABLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateTableStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrReplaceGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryTransientGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableConstraintSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string(), "CONSTRAINT".to_string(), "FOREIGN".to_string(), "PRIMARY".to_string(), "UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommentClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "AS".to_string(), "LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableEndClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["STRICT".to_string(), "WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateTriggerStatementSegment'
pub static CREATE_TRIGGER_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateTriggerStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRIGGER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BeforeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEFORE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AfterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AFTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InsteadKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSTEAD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSTEAD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AFTER".to_string(), "BEFORE".to_string(), "INSTEAD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OfKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string(), "INSERT".to_string(), "UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "EachKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EACH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEGIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: true,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "DELETE".to_string(), "INSERT".to_string(), "REPLACE".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateUserStatementSegment'
pub static CREATE_USER_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateUserStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateViewStatementSegment'
pub static CREATE_VIEW_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateViewStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CreateVirtualTableStatementSegment'
pub static CREATE_VIRTUAL_TABLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CreateVirtualTableStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CreateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "VirtualKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIRTUAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CrossKeywordSegment'
pub static CROSS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CROSS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='CubeFunctionNameSegment'
pub static CUBE_FUNCTION_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CubeFunctionNameSegment
Arc::new(Grammar::StringParser {
    template: "CUBE",
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
})
);

// name='CubeRollupClauseSegment'
pub static CUBE_ROLLUP_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// CubeRollupClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CubeFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CUBE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RollupFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CUBE".to_string(), "ROLLUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupingExpressionList",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CUBE".to_string(), "ROLLUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='CurrentKeywordSegment'
pub static CURRENT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CURRENT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Current_dateKeywordSegment'
pub static CURRENT_DATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CURRENT_DATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Current_timeKeywordSegment'
pub static CURRENT_TIME_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CURRENT_TIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Current_timestampKeywordSegment'
pub static CURRENT_TIMESTAMP_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "CURRENT_TIMESTAMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DatabaseKeywordSegment'
pub static DATABASE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DATABASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DatabaseReferenceSegment'
pub static DATABASE_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DatabaseReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='DatatypeIdentifierSegment'
pub static DATATYPE_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::RegexParser {
    template: RegexMode::new(r#"[A-Z_][A-Z0-9_]*"#),
    token_type: "data_type_identifier",
    raw_class: "CodeSegment",
    optional: false,
    anti_template: Some(RegexMode::new(r#"^(NOT)$"#)),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='DatatypeSegment'
pub static DATATYPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DatatypeSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DoubleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DOUBLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrecisionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECISION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DOUBLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnsignedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNSIGNED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BigKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BIG".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IntKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNSIGNED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VARYING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NativeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATIVE".to_string(), "VARYING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHARACTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHARACTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATIVE".to_string(), "VARYING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CharacterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHARACTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHARACTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "VaryingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VARYING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NativeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATIVE".to_string(), "VARYING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHARACTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnsignedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNSIGNED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNSIGNED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='DateKeywordSegment'
pub static DATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DatePartFunctionName'
pub static DATE_PART_FUNCTION_NAME: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::MultiStringParser {
    templates: vec!["DATEADD"],
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
})
);

// name='DatePartFunctionNameSegment'
pub static DATE_PART_FUNCTION_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DatePartFunctionNameSegment
Arc::new(Grammar::Ref {
    name: "DatePartFunctionName",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATEADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DateTimeFunctionContentsSegment'
pub static DATE_TIME_FUNCTION_CONTENTS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DateTimeFunctionContentsSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DAY".to_string(), "DAYOFYEAR".to_string(), "HOUR".to_string(), "MILLISECOND".to_string(), "MINUTE".to_string(), "MONTH".to_string(), "QUARTER".to_string(), "SECOND".to_string(), "WEEK".to_string(), "WEEKDAY".to_string(), "YEAR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DateTimeLiteralGrammar'
pub static DATE_TIME_LITERAL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatetimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATETIME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATE".to_string(), "DATETIME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::TypedParser {
    template: "single_quote",
    token_type: "date_constructor_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATE".to_string(), "DATETIME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DatetimeKeywordSegment'
pub static DATETIME_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DATETIME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DatetimeUnitSegment'
pub static DATETIME_UNIT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::MultiStringParser {
    templates: vec!["DAY", "DAYOFYEAR", "HOUR", "MILLISECOND", "MINUTE", "MONTH", "QUARTER", "SECOND", "WEEK", "WEEKDAY", "YEAR"],
    token_type: "date_part",
    raw_class: "CodeSegment",
    optional: false,
})
);

// name='DecimalKeywordSegment'
pub static DECIMAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DECIMAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Dedent'
pub static DEDENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Meta("dedent"))
);

// name='DefaultKeywordSegment'
pub static DEFAULT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DEFAULT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DefaultValuesGrammar'
pub static DEFAULT_VALUES_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DeferrableKeywordSegment'
pub static DEFERRABLE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DEFERRABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DeferredKeywordSegment'
pub static DEFERRED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DEFERRED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DeleteKeywordSegment'
pub static DELETE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DELETE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DeleteStatementSegment'
pub static DELETE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DeleteStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReturningClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RETURNING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DelimiterGrammar'
pub static DELIMITER_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Ref {
    name: "SemicolonSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DescKeywordSegment'
pub static DESC_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DESC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DescribeStatementSegment'
pub static DESCRIBE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DescribeStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DescribeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='DetachKeywordSegment'
pub static DETACH_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DETACH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DistinctKeywordSegment'
pub static DISTINCT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DISTINCT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DivideSegment'
pub static DIVIDE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "/",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='DoKeywordSegment'
pub static DO_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DollarLiteralSegment'
pub static DOLLAR_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "dollar_literal",
    token_type: "dollar_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
);

// name='DotSegment'
pub static DOT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ".",
    token_type: "dot",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='DoubleKeywordSegment'
pub static DOUBLE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DOUBLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DropBehaviorGrammar'
pub static DROP_BEHAVIOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RestrictKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropCastStatementSegment'
pub static DROP_CAST_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropCastStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropDatabaseStatementSegment'
pub static DROP_DATABASE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropDatabaseStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATABASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropFunctionStatementSegment'
pub static DROP_FUNCTION_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropFunctionStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropIndexStatementSegment'
pub static DROP_INDEX_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropIndexStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IndexKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INDEX".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IndexReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropKeywordSegment'
pub static DROP_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "DROP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='DropModelStatementSegment'
pub static DROP_MODEL_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropModelStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ModelKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropRoleStatementSegment'
pub static DROP_ROLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropRoleStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RoleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropSchemaStatementSegment'
pub static DROP_SCHEMA_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropSchemaStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropSequenceStatementSegment'
pub static DROP_SEQUENCE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropSequenceStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SequenceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SequenceReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropTableStatementSegment'
pub static DROP_TABLE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropTableStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropTriggerStatementSegment'
pub static DROP_TRIGGER_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropTriggerStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRIGGER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TriggerReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropTypeStatementSegment'
pub static DROP_TYPE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropTypeStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropUserStatementSegment'
pub static DROP_USER_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropUserStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UserKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RoleReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='DropViewStatementSegment'
pub static DROP_VIEW_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// DropViewStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DropKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ViewKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VIEW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IfExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DropBehaviorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='EachKeywordSegment'
pub static EACH_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EACH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ElseClauseSegment'
pub static ELSE_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ElseClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ElseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ELSE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ElseKeywordSegment'
pub static ELSE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ELSE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='EmptyStructLiteralBracketsSegment'
pub static EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// EmptyStructLiteralBracketsSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='EmptyStructLiteralSegment'
pub static EMPTY_STRUCT_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// EmptyStructLiteralSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "EmptyStructLiteralBracketsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='EndBracketSegment'
pub static END_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='EndCurlyBracketSegment'
pub static END_CURLY_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "}",
    token_type: "end_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='EndKeywordSegment'
pub static END_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "END",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='EndSquareBracketSegment'
pub static END_SQUARE_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "]",
    token_type: "end_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='EqualsSegment'
pub static EQUALS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// EqualsSegment
Arc::new(Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='EscapeKeywordSegment'
pub static ESCAPE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ESCAPE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExceptKeywordSegment'
pub static EXCEPT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXCEPT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExcludeKeywordSegment'
pub static EXCLUDE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXCLUDE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExclusiveKeywordSegment'
pub static EXCLUSIVE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXCLUSIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExistsKeywordSegment'
pub static EXISTS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXISTS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExplainKeywordSegment'
pub static EXPLAIN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXPLAIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ExplainStatementSegment'
pub static EXPLAIN_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ExplainStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExplainKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXPLAIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "DELETE".to_string(), "INSERT".to_string(), "REPLACE".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXPLAIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ExpressionSegment'
pub static EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ExpressionSegment
Arc::new(Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
);

// name='Expression_A_Grammar'
pub static EXPRESSION_A_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LikeExpressionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IsClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IsNullGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NotNullGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CollateGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BETWEEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BETWEEN".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PatternMatchingGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GLOB".to_string(), "MATCH".to_string(), "NOT".to_string(), "REGEXP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GLOB".to_string(), "MATCH".to_string(), "NOT".to_string(), "REGEXP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Expression_A_Unary_Operator_Grammar'
pub static EXPRESSION_A_UNARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QualifiedNumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "NOT".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='Expression_B_Grammar'
pub static EXPRESSION_B_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ArithmeticBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), ">".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StringBinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ComparisonOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_B_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "IS".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Expression_B_Unary_Operator_Grammar'
pub static EXPRESSION_B_UNARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QualifiedNumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TildeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='Expression_C_Grammar'
pub static EXPRESSION_C_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXISTS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXISTS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Expression_D_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ShorthandCastSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Expression_D_Grammar'
pub static EXPRESSION_D_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT_DATE".to_string(), "CURRENT_TIME".to_string(), "CURRENT_TIMESTAMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_D_Potential_Select_Statement_Without_Brackets",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MapTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATE".to_string(), "DATETIME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string(), "DATE".to_string(), "DATETIME".to_string(), "FALSE".to_string(), "NULL".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string(), "single_quote".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LocalAliasSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ListComprehensionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AccessorGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Expression_D_Potential_Select_Statement_Without_Brackets'
pub static EXPRESSION_D_POTENTIAL_SELECT_STATEMENT_WITHOUT_BRACKETS: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IntervalExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TypedStructLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ArrayExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ExtendedNaturalJoinKeywordsGrammar'
pub static EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='ExtensionReferenceSegment'
pub static EXTENSION_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ExtensionReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ExtraKeywordSegment'
pub static EXTRA_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "EXTRA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FailKeywordSegment'
pub static FAIL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FAIL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FalseSegment'
pub static FALSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FALSE",
    token_type: "boolean_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
})
);

// name='FastKeywordSegment'
pub static FAST_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FetchClauseSegment'
pub static FETCH_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='FileKeywordSegment'
pub static FILE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FILE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FileSegment'
pub static FILE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FileSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "ALTER".to_string(), "BEGIN".to_string(), "COMMIT".to_string(), "CREATE".to_string(), "DELETE".to_string(), "DROP".to_string(), "END".to_string(), "EXPLAIN".to_string(), "INSERT".to_string(), "PRAGMA".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: true,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "ALTER".to_string(), "BEGIN".to_string(), "COMMIT".to_string(), "CREATE".to_string(), "DELETE".to_string(), "DROP".to_string(), "END".to_string(), "EXPLAIN".to_string(), "INSERT".to_string(), "PRAGMA".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), ";".to_string(), "ALTER".to_string(), "BEGIN".to_string(), "COMMIT".to_string(), "CREATE".to_string(), "DELETE".to_string(), "DROP".to_string(), "END".to_string(), "EXPLAIN".to_string(), "INSERT".to_string(), "PRAGMA".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FilterClauseGrammar'
pub static FILTER_CLAUSE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FilterKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FilterKeywordSegment'
pub static FILTER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FILTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FirstKeywordSegment'
pub static FIRST_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FIRST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FloatKeywordSegment'
pub static FLOAT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FLOAT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FollowingKeywordSegment'
pub static FOLLOWING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FOLLOWING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ForKeywordSegment'
pub static FOR_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FOR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ForeignKeyGrammar'
pub static FOREIGN_KEY_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForeignKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["KEY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ForeignKeywordSegment'
pub static FOREIGN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FOREIGN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FrameClauseSegment'
pub static FRAME_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FrameClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECEDING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECEDING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BetweenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BETWEEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECEDING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOLLOWING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECEDING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnboundedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOLLOWING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNBOUNDED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FollowingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOLLOWING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PrecedingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRECEDING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BETWEEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExcludeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCLUDE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OthersKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OTHERS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CurrentKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TiesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TIES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT".to_string(), "GROUP".to_string(), "NO".to_string(), "TIES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCLUDE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FrameClauseUnitGrammar'
pub static FRAME_CLAUSE_UNIT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RangeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RANGE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GroupsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FromClauseSegment'
pub static FROM_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FromClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FromClauseTerminatorGrammar'
pub static FROM_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithNoSchemaBindingClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithDataClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "GROUP".to_string(), "INTERSECT".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "UNION".to_string(), "WHERE".to_string(), "WINDOW".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FromExpressionElementSegment'
pub static FROM_EXPRESSION_ELEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FromExpressionElementSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PreTableFunctionKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "GROUP".to_string(), "INTERSECT".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "UNION".to_string(), "WHERE".to_string(), "WINDOW".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PreTableFunctionKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TemporalQuerySegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "GROUP".to_string(), "INTERSECT".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "UNION".to_string(), "WHERE".to_string(), "WINDOW".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SamplingExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PostTableExpressionGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='FromExpressionSegment'
pub static FROM_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FromExpressionSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MLTableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MLTableExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='FromKeywordSegment'
pub static FROM_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FROM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FullKeywordSegment'
pub static FULL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "FULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='FunctionContentsExpressionGrammar'
pub static FUNCTION_CONTENTS_EXPRESSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
);

// name='FunctionContentsGrammar'
pub static FUNCTION_CONTENTS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TrimParametersGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatetimeUnitSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DAY".to_string(), "DAYOFYEAR".to_string(), "HOUR".to_string(), "MILLISECOND".to_string(), "MINUTE".to_string(), "MONTH".to_string(), "QUARTER".to_string(), "SECOND".to_string(), "WEEK".to_string(), "WEEKDAY".to_string(), "YEAR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionContentsExpressionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IndexColumnDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IGNORE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAIL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "IGNORE".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: None,
})
);

// name='FunctionContentsSegment'
pub static FUNCTION_CONTENTS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FunctionContentsSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionContentsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FunctionDefinitionGrammar'
pub static FUNCTION_DEFINITION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
// FunctionDefinitionGrammar
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LanguageKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FunctionNameIdentifierSegment'
pub static FUNCTION_NAME_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "word",
    token_type: "function_name_identifier",
    raw_class: "WordSegment",
    optional: false,
})
);

// name='FunctionNameSegment'
pub static FUNCTION_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FunctionNameSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionNameIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["word".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["double_quote".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "BracketedSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["double_quote".to_string(), "word".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='FunctionParameterGrammar'
pub static FUNCTION_PARAMETER_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ParameterNameSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AnyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TypeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='FunctionParameterListGrammar'
pub static FUNCTION_PARAMETER_LIST_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
// FunctionParameterListGrammar
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionParameterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: true,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='FunctionSegment'
pub static FUNCTION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// FunctionSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatePartFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATEADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DateTimeFunctionContentsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATEADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnsExpressionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DatePartFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATEADD".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColumnsExpressionFunctionNameSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "FunctionContentsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PostFunctionGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='GeneratedKeywordSegment'
pub static GENERATED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "GENERATED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='GlobKeywordSegment'
pub static GLOB_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "GLOB",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='GlobOperatorSegment'
pub static GLOB_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "glob_operator",
    token_type: "glob_operator",
    raw_class: "ComparisonOperatorSegment",
    optional: false,
})
);

// name='GreaterThanOrEqualToSegment'
pub static GREATER_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// GreaterThanOrEqualToSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='GreaterThanSegment'
pub static GREATER_THAN_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// GreaterThanSegment
Arc::new(Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='GroupByClauseSegment'
pub static GROUP_BY_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// GroupByClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GroupingSetsClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CubeRollupClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CUBE".to_string(), "ROLLUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "GroupByClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='GroupByClauseTerminatorGrammar'
pub static GROUP_BY_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='GroupKeywordSegment'
pub static GROUP_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "GROUP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='GroupingExpressionList'
pub static GROUPING_EXPRESSION_LIST: Lazy<Arc<Grammar>> = Lazy::new(||
// GroupingExpressionList
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "GroupByClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='GroupingSetsClauseSegment'
pub static GROUPING_SETS_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// GroupingSetsClauseSegment
Arc::new(Grammar::Nothing())
);

// name='GroupsKeywordSegment'
pub static GROUPS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "GROUPS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='HavingClauseSegment'
pub static HAVING_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// HavingClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "HavingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='HavingClauseTerminatorGrammar'
pub static HAVING_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QualifyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FetchKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='HavingKeywordSegment'
pub static HAVING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "HAVING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='HorizontalJoinKeywordsGrammar'
pub static HORIZONTAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='IdentifierSegment'
pub static IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "identifier",
//    token_type: "IdentifierSegment",
})
);

// name='IfExistsGrammar'
pub static IF_EXISTS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXISTS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='IfKeywordSegment'
pub static IF_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "IF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IfNotExistsGrammar'
pub static IF_NOT_EXISTS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IfKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExistsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXISTS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='IgnoreKeywordSegment'
pub static IGNORE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "IGNORE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IgnoreRespectNullsGrammar'
pub static IGNORE_RESPECT_NULLS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='ImmediateKeywordSegment'
pub static IMMEDIATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "IMMEDIATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ImplicitIndent'
pub static IMPLICIT_INDENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Meta("indent"))
);

// name='InKeywordSegment'
pub static IN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "IN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='InOperatorGrammar'
pub static IN_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IN".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='IncrementalKeywordSegment'
pub static INCREMENTAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INCREMENTAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Indent'
pub static INDENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Meta("indent"))
);

// name='IndexColumnDefinitionSegment'
pub static INDEX_COLUMN_DEFINITION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// IndexColumnDefinitionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string(), "DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='IndexKeywordSegment'
pub static INDEX_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INDEX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IndexReferenceSegment'
pub static INDEX_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// IndexReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='IndexedKeywordSegment'
pub static INDEXED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INDEXED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='InitiallyKeywordSegment'
pub static INITIALLY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INITIALLY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='InlinePathOperatorSegment'
pub static INLINE_PATH_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "->>",
    token_type: "column_path_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='InnerKeywordSegment'
pub static INNER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INNER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='InsertKeywordSegment'
pub static INSERT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INSERT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='InsertStatementSegment'
pub static INSERT_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// InsertStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAIL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IGNORE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "IGNORE".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IntoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INTO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpsertClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpsertClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DefaultValuesGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "DEFAULT".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReturningClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RETURNING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='InsteadKeywordSegment'
pub static INSTEAD_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INSTEAD",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Int2KeywordSegment'
pub static INT2_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INT2",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='Int8KeywordSegment'
pub static INT8_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INT8",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IntKeywordSegment'
pub static INT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IntegerKeywordSegment'
pub static INTEGER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INTEGER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IntersectKeywordSegment'
pub static INTERSECT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INTERSECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IntervalExpressionSegment'
pub static INTERVAL_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='IntoKeywordSegment'
pub static INTO_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "INTO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IsClauseGrammar'
pub static IS_CLAUSE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NanLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "UnknownLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NormalizedGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='IsDistinctFromGrammar'
pub static IS_DISTINCT_FROM_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='IsKeywordSegment'
pub static IS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "IS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='IsNullGrammar'
pub static IS_NULL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='IsnullKeywordSegment'
pub static ISNULL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ISNULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='JoinClauseSegment'
pub static JOIN_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// JoinClauseSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ConditionalJoinKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["JOIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NestedJoinGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "JoinUsingConditionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string(), "USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnconditionalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "JoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["JOIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "MatchConditionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExtendedNaturalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "FromExpressionElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='JoinKeywordSegment'
pub static JOIN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "JOIN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='JoinKeywordsGrammar'
pub static JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "JoinKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["JOIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["JOIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='JoinLikeClauseGrammar'
pub static JOIN_LIKE_CLAUSE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='JoinOnConditionSegment'
pub static JOIN_ON_CONDITION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// JoinOnConditionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='JoinTypeKeywordsGrammar'
pub static JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InnerKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INNER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LeftKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LEFT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RightKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string(), "LEFT".to_string(), "RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OuterKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OUTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string(), "LEFT".to_string(), "RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string(), "INNER".to_string(), "LEFT".to_string(), "RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='JoinUsingConditionGrammar'
pub static JOIN_USING_CONDITION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='KeyKeywordSegment'
pub static KEY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "KEY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='KeywordSegment'
pub static KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "keyword",
//    token_type: "KeywordSegment",
})
);

// name='LastKeywordSegment'
pub static LAST_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "LAST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='LeftKeywordSegment'
pub static LEFT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "LEFT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='LessThanOrEqualToSegment'
pub static LESS_THAN_OR_EQUAL_TO_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// LessThanOrEqualToSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='LessThanSegment'
pub static LESS_THAN_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// LessThanSegment
Arc::new(Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='LikeExpressionGrammar'
pub static LIKE_EXPRESSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LikeGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "EscapeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ESCAPE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Tail_Recurse_Expression_A_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ESCAPE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='LikeGrammar'
pub static LIKE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LikeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIKE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='LikeKeywordSegment'
pub static LIKE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "LIKE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='LikeOperatorSegment'
pub static LIKE_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "like_operator",
    token_type: "like_operator",
    raw_class: "ComparisonOperatorSegment",
    optional: false,
})
);

// name='LimitClauseSegment'
pub static LIMIT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// LimitClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string(), "OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='LimitKeywordSegment'
pub static LIMIT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "LIMIT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ListComprehensionGrammar'
pub static LIST_COMPREHENSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='LiteralGrammar'
pub static LITERAL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QualifiedNumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NullLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DateTimeLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DATE".to_string(), "DATETIME".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TypedArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["{".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ParameterizedSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='LiteralKeywordSegment'
pub static LITERAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "literal",
//    token_type: "LiteralKeywordSegment",
})
);

// name='LiteralSegment'
pub static LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "literal",
//    token_type: "LiteralSegment",
})
);

// name='LocalAliasSegment'
pub static LOCAL_ALIAS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// LocalAliasSegment
Arc::new(Grammar::Nothing())
);

// name='MLTableExpressionSegment'
pub static M_L_TABLE_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='MapTypeSegment'
pub static MAP_TYPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MapTypeSegment
Arc::new(Grammar::Nothing())
);

// name='MatchConditionSegment'
pub static MATCH_CONDITION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MatchConditionSegment
Arc::new(Grammar::Nothing())
);

// name='MatchKeywordSegment'
pub static MATCH_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "MATCH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='MaterializedKeywordSegment'
pub static MATERIALIZED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "MATERIALIZED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='MediumintKeywordSegment'
pub static MEDIUMINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "MEDIUMINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='MemoryKeywordSegment'
pub static MEMORY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "MEMORY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='MergeDeleteClauseSegment'
pub static MERGE_DELETE_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeDeleteClauseSegment
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MergeInsertClauseSegment'
pub static MERGE_INSERT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeInsertClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InsertKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MergeIntoLiteralGrammar'
pub static MERGE_INTO_LITERAL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='MergeMatchSegment'
pub static MERGE_MATCH_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeMatchSegment
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MergeMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MergeNotMatchedClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MergeMatchedClauseSegment'
pub static MERGE_MATCHED_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeMatchedClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["THEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MergeUpdateClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MergeDeleteClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string(), "UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MergeNotMatchedClauseSegment'
pub static MERGE_NOT_MATCHED_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeNotMatchedClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MatchedKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AND".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["THEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "MergeInsertClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MergeStatementSegment'
pub static MERGE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MergeIntoLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasedTableReferenceGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "JoinOnConditionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "MergeMatchSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='MergeUpdateClauseSegment'
pub static MERGE_UPDATE_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// MergeUpdateClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='MinusSegment'
pub static MINUS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "-",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ModuloSegment'
pub static MODULO_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "%",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='MultiplySegment'
pub static MULTIPLY_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "*",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='NakedIdentifierSegment'
pub static NAKED_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::RegexParser {
    template: RegexMode::new(r#"[A-Z0-9_]*[A-Z][A-Z0-9_]*"#),
    token_type: "naked_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
    anti_template: Some(RegexMode::new(r#"^(OTHERS|TRANSACTION|SELECT|CURRENT_TIMESTAMP|HAVING|NULL|REPLACE|CAST|UNIQUE|FIRST|RECURSIVE|ROLLBACK|MATCH|BEFORE|DROP|ROWS|SET|LAST|INDEXED|FOREIGN|ROW|CONFLICT|PRIMARY|THEN|COLLATE|UNBOUNDED|FULL|MATERIALIZED|OFFSET|AUTOINCREMENT|OF|ADD|IF|TEMP|NOTNULL|PARTITION|IMMEDIATE|WINDOW|PLAN|EXPLAIN|TO|VIRTUAL|LEFT|TEMPORARY|REGEXP|INSERT|DESC|WITHOUT|CURRENT_DATE|CASCADE|INITIALLY|INTO|DETACH|RAISE|RESTRICT|GENERATED|IGNORE|EXISTS|PRAGMA|NULLS|ANALYZE|COLUMN|NATURAL|WHERE|GROUPS|DISTINCT|ELSE|CASE|OVER|IN|DEFERRED|FROM|ESCAPE|ORDER|RANGE|REINDEX|FOR|FILTER|CURRENT_TIME|IS|AS|CURRENT|GROUP|BEGIN|LIMIT|ON|DELETE|DEFAULT|EXCLUSIVE|WITH|DATABASE|RETURNING|RIGHT|JOIN|INTERSECT|INSTEAD|ISNULL|ALTER|ATTACH|OR|SAVEPOINT|ALWAYS|TABLE|DEFERRABLE|END|WHEN|CHECK|NOTHING|VIEW|BETWEEN|EACH|RENAME|AFTER|EXCEPT|EXCLUDE|GLOB|UPDATE|AND|FAIL|NOT|DO|LIKE|INDEX|ALL|FOLLOWING|CREATE|REFERENCES|COMMIT|PRECEDING|TRIGGER|UNION|BY|VACUUM|INNER|NO|VALUES|USING|RELEASE|ABORT|ASC|CONSTRAINT|OUTER|QUERY|CROSS)$"#)),
})
);

// name='NamedWindowExpressionSegment'
pub static NAMED_WINDOW_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// NamedWindowExpressionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='NamedWindowSegment'
pub static NAMED_WINDOW_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// NamedWindowSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NamedWindowExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='NanLiteralSegment'
pub static NAN_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NativeKeywordSegment'
pub static NATIVE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NATIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NaturalJoinKeywordsGrammar'
pub static NATURAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NaturalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATURAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "JoinTypeKeywordsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string(), "INNER".to_string(), "LEFT".to_string(), "RIGHT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATURAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='NaturalKeywordSegment'
pub static NATURAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NATURAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NcharKeywordSegment'
pub static NCHAR_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NCHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NegativeSegment'
pub static NEGATIVE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "-",
    token_type: "sign_indicator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='NestedJoinGrammar'
pub static NESTED_JOIN_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NewlineSegment'
pub static NEWLINE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "newline",
//    token_type: "NewlineSegment",
})
);

// name='NoKeywordSegment'
pub static NO_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NocaseKeywordSegment'
pub static NOCASE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NOCASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NonSetSelectableGrammar'
pub static NON_SET_SELECTABLE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UnorderedSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BracketedSetExpressionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='NonStandardJoinTypeKeywordsGrammar'
pub static NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NonWithNonSelectableGrammar'
pub static NON_WITH_NON_SELECTABLE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='NonWithSelectableGrammar'
pub static NON_WITH_SELECTABLE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='NoneKeywordSegment'
pub static NONE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NONE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NormalKeywordSegment'
pub static NORMAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NORMAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NormalizedGrammar'
pub static NORMALIZED_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NotEnforcedGrammar'
pub static NOT_ENFORCED_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NotEqualToSegment'
pub static NOT_EQUAL_TO_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// NotEqualToSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawNotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawEqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RawLessThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RawGreaterThanSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([">".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "<".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='NotKeywordSegment'
pub static NOT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NOT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NotNullGrammar'
pub static NOT_NULL_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='NotOperatorGrammar'
pub static NOT_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NOT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NothingKeywordSegment'
pub static NOTHING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NOTHING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NotnullKeywordSegment'
pub static NOTNULL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NOTNULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NullKeywordSegment'
pub static NULL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NULL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NullLiteralSegment'
pub static NULL_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NULL",
    token_type: "null_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
})
);

// name='NullsKeywordSegment'
pub static NULLS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NULLS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NumericKeywordSegment'
pub static NUMERIC_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NUMERIC",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='NumericLiteralSegment'
pub static NUMERIC_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::TypedParser {
    template: "numeric_literal",
    token_type: "numeric_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
,
Arc::new(Grammar::Ref {
    name: "ParameterizedSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
);

// name='NvarcharKeywordSegment'
pub static NVARCHAR_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "NVARCHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ObjectLiteralElementSegment'
pub static OBJECT_LITERAL_ELEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ObjectLiteralElementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([":".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
);

// name='ObjectLiteralSegment'
pub static OBJECT_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ObjectLiteralSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ObjectLiteralElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: true,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "{",
    token_type: "start_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: "}",
    token_type: "end_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["{".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ObjectReferenceDelimiterGrammar'
pub static OBJECT_REFERENCE_DELIMITER_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ObjectReferenceSegment'
pub static OBJECT_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ObjectReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='ObjectReferenceTerminatorGrammar'
pub static OBJECT_REFERENCE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UsingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["USING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CastOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["::".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StartSquareBracketSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StartBracketSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColonSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([":".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([";".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "JoinLikeClauseGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Token{
    token_type: "bracketed",
//    token_type: "BracketedSegment",
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='OfKeywordSegment'
pub static OF_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OffKeywordSegment'
pub static OFF_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OFF",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OffsetClauseSegment'
pub static OFFSET_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// OffsetClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OffsetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROW".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFFSET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='OffsetKeywordSegment'
pub static OFFSET_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OFFSET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OnKeywordSegment'
pub static ON_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ON",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OrKeywordSegment'
pub static OR_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OrOperatorGrammar'
pub static OR_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OR",
    token_type: "binary_operator",
    raw_class: "BinaryOperatorSegment",
    optional: false,
})
);

// name='OrReplaceGrammar'
pub static OR_REPLACE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='OrderByClauseSegment'
pub static ORDER_BY_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// OrderByClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string(), "DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NullsKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULLS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FirstKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FIRST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FIRST".to_string(), "LAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULLS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithFillSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "LimitClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='OrderByClauseTerminators'
pub static ORDER_BY_CLAUSE_TERMINATORS: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FrameClauseUnitGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "LIMIT".to_string(), "RANGE".to_string(), "ROWS".to_string(), "WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='OrderKeywordSegment'
pub static ORDER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ORDER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OrderNoOrderGrammar'
pub static ORDER_NO_ORDER_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoorderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='OthersKeywordSegment'
pub static OTHERS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OTHERS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OuterKeywordSegment'
pub static OUTER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OUTER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OverClauseSegment'
pub static OVER_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// OverClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "IgnoreRespectNullsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "OverKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OVER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WindowSpecificationSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='OverKeywordSegment'
pub static OVER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "OVER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='OverlapsClauseSegment'
pub static OVERLAPS_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='ParameterNameSegment'
pub static PARAMETER_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::RegexParser {
    template: RegexMode::new(r#"\"?[A-Z][A-Z0-9_]*\"?"#),
    token_type: "parameter",
    raw_class: "CodeSegment",
    optional: false,
    anti_template: None,
})
);

// name='ParameterSegment'
pub static PARAMETER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "?",
    token_type: "parameter",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='ParameterizedSegment'
pub static PARAMETERIZED_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ParameterizedSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AtSignLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuestionMarkSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ColonLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["colon_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuestionLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["question_literal".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DollarLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["dollar_literal".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "question_literal".to_string()]),
        }),
})
);

// name='PartitionClauseSegment'
pub static PARTITION_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// PartitionClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PARTITION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PARTITION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='PartitionKeywordSegment'
pub static PARTITION_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PARTITION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PassiveKeywordSegment'
pub static PASSIVE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PASSIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PathSegment'
pub static PATH_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// PathSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["/".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::TypedParser {
    template: "word",
    token_type: "path_segment",
    raw_class: "WordSegment",
    optional: false,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "SlashSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["/".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["word".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["/".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuotedLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["/".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
);

// name='PatternMatchingGrammar'
pub static PATTERN_MATCHING_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GlobKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GLOB".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RegexpKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REGEXP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MatchKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATCH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GLOB".to_string(), "MATCH".to_string(), "REGEXP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GLOB".to_string(), "MATCH".to_string(), "NOT".to_string(), "REGEXP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='PersistKeywordSegment'
pub static PERSIST_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PERSIST",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PipeSegment'
pub static PIPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "|",
    token_type: "pipe",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='PlanKeywordSegment'
pub static PLAN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PLAN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PlusSegment'
pub static PLUS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "+",
    token_type: "binary_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='PositiveSegment'
pub static POSITIVE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "+",
    token_type: "sign_indicator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='PostFunctionGrammar'
pub static POST_FUNCTION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FilterClauseGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OverClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='PostTableExpressionGrammar'
pub static POST_TABLE_EXPRESSION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='PragmaKeywordSegment'
pub static PRAGMA_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PRAGMA",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PragmaReferenceSegment'
pub static PRAGMA_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// PragmaReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='PragmaStatementSegment'
pub static PRAGMA_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// PragmaStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PragmaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRAGMA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PragmaReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "YesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["YES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NONE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IncrementalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INCREMENTAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PersistKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PERSIST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MemoryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MEMORY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NormalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NORMAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExclusiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCLUSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExtraKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXTRA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PassiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PASSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RestartKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESTART".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ResetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "YesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["YES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NONE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IncrementalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INCREMENTAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PersistKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PERSIST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MemoryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MEMORY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NormalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NORMAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExclusiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCLUSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExtraKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXTRA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PassiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PASSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RestartKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESTART".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ResetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BooleanLiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FALSE".to_string(), "TRUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "YesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["YES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OffKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OFF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NONE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IncrementalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INCREMENTAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PersistKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PERSIST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MemoryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MEMORY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NormalKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NORMAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExclusiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCLUSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FastKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAST".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExtraKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXTRA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FileKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FILE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PassiveKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PASSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RestartKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESTART".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ResetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRAGMA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='PreTableFunctionKeywordsGrammar'
pub static PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='PrecedingKeywordSegment'
pub static PRECEDING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PRECEDING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PrecisionKeywordSegment'
pub static PRECISION_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PRECISION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='PrimaryKeyGrammar'
pub static PRIMARY_KEY_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PrimaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRIMARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "KeyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["KEY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AscKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DescKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ASC".to_string(), "DESC".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AutoincrementKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AUTOINCREMENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["AUTOINCREMENT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRIMARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='PrimaryKeywordSegment'
pub static PRIMARY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "PRIMARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='QualifiedNumericLiteralSegment'
pub static QUALIFIED_NUMERIC_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// QualifiedNumericLiteralSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SignedSegmentGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='QueryKeywordSegment'
pub static QUERY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "QUERY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='QuestionLiteralSegment'
pub static QUESTION_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "question_literal",
    token_type: "question_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
);

// name='QuestionMarkSegment'
pub static QUESTION_MARK_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "?",
    token_type: "question_mark",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='QuotedIdentifierSegment'
pub static QUOTED_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "double_quote",
    token_type: "quoted_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
})
);

// name='QuotedLiteralSegment'
pub static QUOTED_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "single_quote",
    token_type: "quoted_literal",
    raw_class: "LiteralSegment",
    optional: false,
})
);

// name='RaiseKeywordSegment'
pub static RAISE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RAISE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RangeKeywordSegment'
pub static RANGE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RANGE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RawEqualsSegment'
pub static RAW_EQUALS_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "=",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='RawGreaterThanSegment'
pub static RAW_GREATER_THAN_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ">",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='RawLessThanSegment'
pub static RAW_LESS_THAN_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "<",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='RawNotSegment'
pub static RAW_NOT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "!",
    token_type: "raw_comparison_operator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='RawSegment'
pub static RAW_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "raw",
//    token_type: "RawSegment",
})
);

// name='RealKeywordSegment'
pub static REAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "REAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RecursiveKeywordSegment'
pub static RECURSIVE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RECURSIVE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReferenceDefinitionGrammar'
pub static REFERENCE_DEFINITION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ReferencesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReferenceMatchGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATCH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::AnySetOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReferentialActionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "NO".to_string(), "RESTRICT".to_string(), "SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReferentialActionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "NO".to_string(), "RESTRICT".to_string(), "SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ReferenceMatchGrammar'
pub static REFERENCE_MATCH_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MatchKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATCH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PartialKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SimpleKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["MATCH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ReferencesKeywordSegment'
pub static REFERENCES_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "REFERENCES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReferentialActionGrammar'
pub static REFERENTIAL_ACTION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "RestrictKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RESTRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CascadeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NullKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NULL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ActionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ACTION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASCADE".to_string(), "NO".to_string(), "RESTRICT".to_string(), "SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='RegexpKeywordSegment'
pub static REGEXP_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "REGEXP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReindexKeywordSegment'
pub static REINDEX_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "REINDEX",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReleaseKeywordSegment'
pub static RELEASE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RELEASE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RenameKeywordSegment'
pub static RENAME_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RENAME",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReplaceKeywordSegment'
pub static REPLACE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "REPLACE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ResetKeywordSegment'
pub static RESET_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RESET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RestartKeywordSegment'
pub static RESTART_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RESTART",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RestrictKeywordSegment'
pub static RESTRICT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RESTRICT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ReturningClauseSegment'
pub static RETURNING_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ReturningClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ReturningKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RETURNING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WildcardExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RETURNING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ReturningKeywordSegment'
pub static RETURNING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RETURNING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RightKeywordSegment'
pub static RIGHT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RIGHT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RoleReferenceSegment'
pub static ROLE_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// RoleReferenceSegment
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
);

// name='RollbackKeywordSegment'
pub static ROLLBACK_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ROLLBACK",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RollupFunctionNameSegment'
pub static ROLLUP_FUNCTION_NAME_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// RollupFunctionNameSegment
Arc::new(Grammar::StringParser {
    template: "ROLLUP",
    token_type: "function_name_identifier",
    raw_class: "CodeSegment",
    optional: false,
})
);

// name='RowKeywordSegment'
pub static ROW_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ROW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RowidKeywordSegment'
pub static ROWID_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ROWID",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RowsKeywordSegment'
pub static ROWS_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "ROWS",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='RtrimKeywordSegment'
pub static RTRIM_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "RTRIM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='SamplingExpressionSegment'
pub static SAMPLING_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='SavepointKeywordSegment'
pub static SAVEPOINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "SAVEPOINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='SchemaReferenceSegment'
pub static SCHEMA_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SchemaReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SelectClauseElementSegment'
pub static SELECT_CLAUSE_ELEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SelectClauseElementSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WildcardExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SelectClauseModifierSegment'
pub static SELECT_CLAUSE_MODIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SelectClauseModifierSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string(), "DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SelectClauseSegment'
pub static SELECT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SelectClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectClauseModifierSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string(), "DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectClauseElementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: true,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "SelectClauseTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "FROM".to_string(), "INTERSECT".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "UNION".to_string(), "WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::GreedyOnceStarted,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SelectClauseTerminatorGrammar'
pub static SELECT_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "FromKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "FROM".to_string(), "INTERSECT".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "UNION".to_string(), "WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SelectKeywordSegment'
pub static SELECT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "SELECT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='SelectStatementSegment'
pub static SELECT_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SelectStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FetchClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SelectableGrammar'
pub static SELECTABLE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithCompoundStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithCompoundNonSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithCompoundNonSelectStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SemicolonSegment'
pub static SEMICOLON_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ";",
    token_type: "statement_terminator",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='SequenceMaxValueGrammar'
pub static SEQUENCE_MAX_VALUE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MaxvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MaxvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SequenceMinValueGrammar'
pub static SEQUENCE_MIN_VALUE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MinvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NumericLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["?".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["at_sign_literal".to_string(), "colon_literal".to_string(), "dollar_literal".to_string(), "numeric_literal".to_string(), "question_literal".to_string()]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "MinvalueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SequenceReferenceSegment'
pub static SEQUENCE_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SequenceReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SetClauseListSegment'
pub static SET_CLAUSE_LIST_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SetClauseListSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SetClauseSegment'
pub static SET_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SetClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SetExpressionSegment'
pub static SET_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SetExpressionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "LimitClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SetKeywordSegment'
pub static SET_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "SET",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='SetOperatorSegment'
pub static SET_OPERATOR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SetOperatorSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string(), "DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "IntersectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INTERSECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExceptKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: Some(Box::new(
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExceptKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Anything)
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SetSchemaStatementSegment'
pub static SET_SCHEMA_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SetSchemaStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "IfNotExistsGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IF".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ShorthandCastSegment'
pub static SHORTHAND_CAST_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ShorthandCastSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Expression_D_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "CaseExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CASE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CastOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["::".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DatatypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TimeZoneGrammar",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["::".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["::".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SignedSegmentGrammar'
pub static SIGNED_SEGMENT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PositiveSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NegativeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='SingleIdentifierGrammar'
pub static SINGLE_IDENTIFIER_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NakedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "SingleQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["single_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "QuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["double_quote".to_string()]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BackQuotedIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([]),
            token_types: hashbrown::HashSet::from_iter(["back_quote".to_string()]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SingleIdentifierListSegment'
pub static SINGLE_IDENTIFIER_LIST_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SingleIdentifierListSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SingleQuotedIdentifierSegment'
pub static SINGLE_QUOTED_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::TypedParser {
    template: "single_quote",
    token_type: "quoted_identifier",
    raw_class: "IdentifierSegment",
    optional: false,
})
);

// name='SizedArrayTypeSegment'
pub static SIZED_ARRAY_TYPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// SizedArrayTypeSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ArrayAccessorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='SlashSegment'
pub static SLASH_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "/",
    token_type: "slash",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='SliceSegment'
pub static SLICE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: ":",
    token_type: "slice",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='SmallintKeywordSegment'
pub static SMALLINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "SMALLINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='StarSegment'
pub static STAR_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "*",
    token_type: "star",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='StartBracketSegment'
pub static START_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='StartCurlyBracketSegment'
pub static START_CURLY_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "{",
    token_type: "start_curly_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='StartSquareBracketSegment'
pub static START_SQUARE_BRACKET_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "[",
    token_type: "start_square_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='StatementSegment'
pub static STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// StatementSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AlterTableStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALTER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CreateIndexStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CreateTableStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CreateVirtualTableStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CreateTriggerStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CreateViewStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CREATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeleteStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DELETE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DropIndexStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DropTableStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DropTriggerStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DropViewStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DROP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExplainStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXPLAIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InsertStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INSERT".to_string(), "REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "PragmaStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRAGMA".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TransactionStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEGIN".to_string(), "COMMIT".to_string(), "END".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UpdateStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "ALTER".to_string(), "BEGIN".to_string(), "COMMIT".to_string(), "CREATE".to_string(), "DELETE".to_string(), "DROP".to_string(), "END".to_string(), "EXPLAIN".to_string(), "INSERT".to_string(), "PRAGMA".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "ALTER".to_string(), "BEGIN".to_string(), "COMMIT".to_string(), "CREATE".to_string(), "DELETE".to_string(), "DROP".to_string(), "END".to_string(), "EXPLAIN".to_string(), "INSERT".to_string(), "PRAGMA".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string(), "SELECT".to_string(), "UPDATE".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='StoredKeywordSegment'
pub static STORED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "STORED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='StrictKeywordSegment'
pub static STRICT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "STRICT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='StringBinaryOperatorGrammar'
pub static STRING_BINARY_OPERATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ConcatSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["|".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='StructLiteralSegment'
pub static STRUCT_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// StructLiteralSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='StructTypeSegment'
pub static STRUCT_TYPE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// StructTypeSegment
Arc::new(Grammar::Nothing())
);

// name='SymbolSegment'
pub static SYMBOL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "symbol",
//    token_type: "SymbolSegment",
})
);

// name='TableConstraintSegment'
pub static TABLE_CONSTRAINT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TableConstraintSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ConstraintKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONSTRAINT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONSTRAINT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CheckKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PrimaryKeyGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRIMARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PRIMARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ForeignKeyGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReferenceDefinitionGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REFERENCES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FOREIGN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string(), "FOREIGN".to_string(), "PRIMARY".to_string(), "UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NotKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeferrableKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRABLE".to_string(), "NOT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DeferredKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFERRED".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "InitiallyKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ImmediateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IMMEDIATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["INITIALLY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CHECK".to_string(), "CONSTRAINT".to_string(), "FOREIGN".to_string(), "PRIMARY".to_string(), "UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TableEndClauseSegment'
pub static TABLE_END_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TableEndClauseSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithoutKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RowidKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROWID".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "StrictKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["STRICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["STRICT".to_string(), "WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TableExpressionSegment'
pub static TABLE_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TableExpressionSegment
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ValuesClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "BareFunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CURRENT_DATE".to_string(), "CURRENT_TIME".to_string(), "CURRENT_TIMESTAMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FunctionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string(), "WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "MergeStatementSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TableKeywordSegment'
pub static TABLE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TABLE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TableReferenceSegment'
pub static TABLE_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TableReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ColumnPathOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["->".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "InlinePathOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["->>".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["->".to_string(), "->>".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LiteralGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TablespaceReferenceSegment'
pub static TABLESPACE_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TablespaceReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TagReferenceSegment'
pub static TAG_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TagReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Tail_Recurse_Expression_A_Grammar'
pub static TAIL_RECURSE_EXPRESSION_A_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Expression_A_Unary_Operator_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "NOT".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    min_times: 0,
    max_times: None,
    max_times_per_element: None,
    exclude: None,
    optional: true,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "BinaryOperatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["!".to_string(), "%".to_string(), "&".to_string(), "*".to_string(), "+".to_string(), "-".to_string(), "->".to_string(), "->>".to_string(), "/".to_string(), "<".to_string(), "=".to_string(), ">".to_string(), "AND".to_string(), "IS".to_string(), "OR".to_string(), "^".to_string(), "|".to_string()]),
            token_types: hashbrown::HashSet::from_iter(["like_operator".to_string()]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "NOT".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='Tail_Recurse_Expression_B_Grammar'
pub static TAIL_RECURSE_EXPRESSION_B_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "Expression_B_Unary_Operator_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["+".to_string(), "-".to_string(), "~".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "Expression_C_Grammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TempKeywordSegment'
pub static TEMP_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TEMP",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TemporalQuerySegment'
pub static TEMPORAL_QUERY_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TemporalQuerySegment
Arc::new(Grammar::Nothing())
);

// name='TemporaryGrammar'
pub static TEMPORARY_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TempKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TemporaryKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TemporaryKeywordSegment'
pub static TEMPORARY_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TEMPORARY",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TemporaryTransientGrammar'
pub static TEMPORARY_TRANSIENT_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Ref {
    name: "TemporaryGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TEMP".to_string(), "TEMPORARY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TextKeywordSegment'
pub static TEXT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TEXT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ThenKeywordSegment'
pub static THEN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "THEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TiesKeywordSegment'
pub static TIES_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TIES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TildeSegment'
pub static TILDE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "~",
    token_type: "tilde",
    raw_class: "SymbolSegment",
    optional: false,
})
);

// name='TimeWithTZGrammar'
pub static TIME_WITH_T_Z_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "TimestampKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedArguments",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WithoutKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string(), "WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TimeKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ZoneKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string(), "WITHOUT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TimeZoneGrammar'
pub static TIME_ZONE_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='TinyintKeywordSegment'
pub static TINYINT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TINYINT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ToKeywordSegment'
pub static TO_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TO",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TransactionKeywordSegment'
pub static TRANSACTION_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TRANSACTION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TransactionStatementSegment'
pub static TRANSACTION_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TransactionStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BeginKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEGIN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "CommitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["COMMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "EndKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["END".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEGIN".to_string(), "COMMIT".to_string(), "END".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TransactionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRANSACTION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRANSACTION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ToKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SavepointKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SAVEPOINT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BEGIN".to_string(), "COMMIT".to_string(), "END".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TriggerKeywordSegment'
pub static TRIGGER_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TRIGGER",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TriggerReferenceSegment'
pub static TRIGGER_REFERENCE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TriggerReferenceSegment
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "ObjectReferenceTerminatorGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    reset_terminators: false,
    allow_gaps: false,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TrimParametersGrammar'
pub static TRIM_PARAMETERS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='TrueSegment'
pub static TRUE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TRUE",
    token_type: "boolean_literal",
    raw_class: "LiteralKeywordSegment",
    optional: false,
})
);

// name='TruncateKeywordSegment'
pub static TRUNCATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "TRUNCATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='TruncateStatementSegment'
pub static TRUNCATE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TruncateStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "TruncateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TABLE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["TRUNCATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TupleSegment'
pub static TUPLE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TupleSegment
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "BaseExpressionElementGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='TypedArrayLiteralSegment'
pub static TYPED_ARRAY_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TypedArrayLiteralSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ArrayTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ArrayLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["[".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='TypedStructLiteralSegment'
pub static TYPED_STRUCT_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// TypedStructLiteralSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StructTypeSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StructLiteralSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='UnboundedKeywordSegment'
pub static UNBOUNDED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "UNBOUNDED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='UnconditionalCrossJoinKeywordsGrammar'
pub static UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='UnconditionalJoinKeywordsGrammar'
pub static UNCONDITIONAL_JOIN_KEYWORDS_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NaturalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NATURAL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "UnconditionalCrossJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "HorizontalJoinKeywordsGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='UnionGrammar'
pub static UNION_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UnionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DistinctKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "AllKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ALL".to_string(), "DISTINCT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UnionKeywordSegment'
pub static UNION_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "UNION",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='UniqueKeyGrammar'
pub static UNIQUE_KEY_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UniqueKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UNIQUE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UniqueKeywordSegment'
pub static UNIQUE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "UNIQUE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='UnknownLiteralSegment'
pub static UNKNOWN_LITERAL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Nothing())
);

// name='UnorderedSelectStatementSegment'
pub static UNORDERED_SELECT_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// UnorderedSelectStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SelectClauseSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "GroupByClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "HavingClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["HAVING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OverlapsClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "NamedWindowSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UnorderedSetExpressionSegment'
pub static UNORDERED_SET_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// UnorderedSetExpressionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SetOperatorSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NonSetSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
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
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["EXCEPT".to_string(), "INTERSECT".to_string(), "UNION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UnsignedKeywordSegment'
pub static UNSIGNED_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "UNSIGNED",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='UpdateKeywordSegment'
pub static UPDATE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "UPDATE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='UpdateStatementSegment'
pub static UPDATE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// UpdateStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "AbortKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FailKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FAIL".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "IgnoreKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["IGNORE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReplaceKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["REPLACE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RollbackKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ABORT".to_string(), "FAIL".to_string(), "IGNORE".to_string(), "REPLACE".to_string(), "ROLLBACK".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["OR".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "TableReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "AliasExpressionSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Ref {
    name: "SetClauseListSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FromClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["FROM".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WhereClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ReturningClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RETURNING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UpsertClauseSegment'
pub static UPSERT_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// UpsertClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OnKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["CONFLICT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ConflictTargetSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NothingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOTHING".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UpdateKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SetKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SET".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BracketedColumnReferenceListGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "EqualsSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["=".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NOTHING".to_string(), "UPDATE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ON".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='UseStatementSegment'
pub static USE_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// UseStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "UseKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "DatabaseReferenceSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='UsingKeywordSegment'
pub static USING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "USING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='VacuumKeywordSegment'
pub static VACUUM_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VACUUM",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ValuesClauseSegment'
pub static VALUES_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// ValuesClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ValuesKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "DefaultKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["DEFAULT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Greedy,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: false,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='ValuesKeywordSegment'
pub static VALUES_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VALUES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='VarcharKeywordSegment'
pub static VARCHAR_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VARCHAR",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='VaryingKeywordSegment'
pub static VARYING_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VARYING",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='ViewKeywordSegment'
pub static VIEW_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VIEW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='VirtualKeywordSegment'
pub static VIRTUAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "VIRTUAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WalKeywordSegment'
pub static WAL_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WAL",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WhenClauseSegment'
pub static WHEN_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WhenClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "ThenKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["THEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Meta("conditional"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHEN".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WhenKeywordSegment'
pub static WHEN_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WHEN",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WhereClauseSegment'
pub static WHERE_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WhereClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WhereKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("indent"))
,
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Bracketed {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    bracket_pairs: (
        Box::new(
Arc::new(Grammar::StringParser {
    template: "(",
    token_type: "start_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        ),
        Box::new(
Arc::new(Grammar::StringParser {
    template: ")",
    token_type: "end_bracket",
    raw_class: "SymbolSegment",
    optional: false,
})
        )
    ),
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ExpressionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("dedent"))
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WHERE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WhereClauseTerminatorGrammar'
pub static WHERE_CLAUSE_TERMINATOR_GRAMMAR: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "LimitKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["LIMIT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "GroupKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "ByKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["BY".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "WindowKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUP".to_string(), "LIMIT".to_string(), "ORDER".to_string(), "WINDOW".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WhereKeywordSegment'
pub static WHERE_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WHERE",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WhitespaceSegment'
pub static WHITESPACE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "whitespace",
//    token_type: "WhitespaceSegment",
})
);

// name='WildcardExpressionSegment'
pub static WILDCARD_EXPRESSION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WildcardExpressionSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WildcardIdentifierSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='WildcardIdentifierSegment'
pub static WILDCARD_IDENTIFIER_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WildcardIdentifierSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::AnyNumberOf {
    elements: vec![
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "ObjectReferenceDelimiterGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DotSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([".".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
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
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "StarSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["*".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: false,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='WindowKeywordSegment'
pub static WINDOW_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WINDOW",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WindowSpecificationSegment'
pub static WINDOW_SPECIFICATION_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WindowSpecificationSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "SingleIdentifierGrammar",
    optional: true,
    allow_gaps: true,
    exclude: Some(Box::new(
Arc::new(Grammar::OneOf {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "PartitionKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PARTITION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrderKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    exclude: None,
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string(), "PARTITION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    )),
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "PartitionClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["PARTITION".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "OrderByClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["ORDER".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "FrameClauseSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["GROUPS".to_string(), "RANGE".to_string(), "ROWS".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
);

// name='WithCompoundNonSelectStatementSegment'
pub static WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WithCompoundNonSelectStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RECURSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: true,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "NonWithNonSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WithCompoundStatementSegment'
pub static WITH_COMPOUND_STATEMENT_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WithCompoundStatementSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "RecursiveKeywordSegment",
    optional: true,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["RECURSIVE".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Delimited {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "CTEDefinitionSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    delimiter: Box::new(
Arc::new(Grammar::Ref {
    name: "CommaSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter([",".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
    ),
    allow_trailing: true,
    optional: false,
    optional_delimiter: false,
    terminators: vec![
Arc::new(Grammar::Ref {
    name: "SelectKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["SELECT".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    reset_terminators: false,
    allow_gaps: true,
    min_delimiters: 0,
    parse_mode: ParseMode::Strict,
    simple_hint: None,
})
,
Arc::new(Grammar::Meta("conditional"))
,
Arc::new(Grammar::Ref {
    name: "NonWithSelectableGrammar",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["(".to_string(), "SELECT".to_string(), "VALUES".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WithDataClauseSegment'
pub static WITH_DATA_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WithDataClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
    ],
    optional: true,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "DataKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WithFillSegment'
pub static WITH_FILL_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WithFillSegment
Arc::new(Grammar::Nothing())
);

// name='WithKeywordSegment'
pub static WITH_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WITH",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WithNoSchemaBindingClauseSegment'
pub static WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
// WithNoSchemaBindingClauseSegment
Arc::new(Grammar::Sequence {
    elements: vec![
Arc::new(Grammar::Ref {
    name: "WithKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "NoKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["NO".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
,
Arc::new(Grammar::Ref {
    name: "SchemaKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
Arc::new(Grammar::Ref {
    name: "BindingKeywordSegment",
    optional: false,
    allow_gaps: true,
    exclude: None,
    terminators: vec![
    ],
    reset_terminators: false,
    simple_hint: None,
})
,
    ],
    optional: false,
    terminators: vec![
    ],
    reset_terminators: false,
    allow_gaps: true,
    parse_mode: ParseMode::Strict,
    simple_hint: Some(SimpleHint {
            raw_values: hashbrown::HashSet::from_iter(["WITH".to_string()]),
            token_types: hashbrown::HashSet::from_iter([]),
        }),
})
);

// name='WithoutKeywordSegment'
pub static WITHOUT_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "WITHOUT",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

// name='WordSegment'
pub static WORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::Token{
    token_type: "word",
//    token_type: "WordSegment",
})
);

// name='YesKeywordSegment'
pub static YES_KEYWORD_SEGMENT: Lazy<Arc<Grammar>> = Lazy::new(||
Arc::new(Grammar::StringParser {
    template: "YES",
    token_type: "keyword",
    raw_class: "KeywordSegment",
    optional: false,
})
);

pub fn get_sqlite_segment_grammar(name: &str) -> Option<Arc<Grammar>> {
    match name {
            "AbortKeywordSegment" => Some(ABORT_KEYWORD_SEGMENT.clone()),
            "AccessStatementSegment" => Some(ACCESS_STATEMENT_SEGMENT.clone()),
            "AccessorGrammar" => Some(ACCESSOR_GRAMMAR.clone()),
            "ActionKeywordSegment" => Some(ACTION_KEYWORD_SEGMENT.clone()),
            "AddKeywordSegment" => Some(ADD_KEYWORD_SEGMENT.clone()),
            "AfterKeywordSegment" => Some(AFTER_KEYWORD_SEGMENT.clone()),
            "AggregateOrderByClause" => Some(AGGREGATE_ORDER_BY_CLAUSE.clone()),
            "AliasExpressionSegment" => Some(ALIAS_EXPRESSION_SEGMENT.clone()),
            "AliasedTableReferenceGrammar" => Some(ALIASED_TABLE_REFERENCE_GRAMMAR.clone()),
            "AllKeywordSegment" => Some(ALL_KEYWORD_SEGMENT.clone()),
            "AlterKeywordSegment" => Some(ALTER_KEYWORD_SEGMENT.clone()),
            "AlterSequenceOptionsSegment" => Some(ALTER_SEQUENCE_OPTIONS_SEGMENT.clone()),
            "AlterSequenceStatementSegment" => Some(ALTER_SEQUENCE_STATEMENT_SEGMENT.clone()),
            "AlterTableDropColumnGrammar" => Some(ALTER_TABLE_DROP_COLUMN_GRAMMAR.clone()),
            "AlterTableOptionsGrammar" => Some(ALTER_TABLE_OPTIONS_GRAMMAR.clone()),
            "AlterTableStatementSegment" => Some(ALTER_TABLE_STATEMENT_SEGMENT.clone()),
            "AlwaysKeywordSegment" => Some(ALWAYS_KEYWORD_SEGMENT.clone()),
            "AmpersandSegment" => Some(AMPERSAND_SEGMENT.clone()),
            "AnalyzeKeywordSegment" => Some(ANALYZE_KEYWORD_SEGMENT.clone()),
            "AndKeywordSegment" => Some(AND_KEYWORD_SEGMENT.clone()),
            "AndOperatorGrammar" => Some(AND_OPERATOR_GRAMMAR.clone()),
            "ArithmeticBinaryOperatorGrammar" => Some(ARITHMETIC_BINARY_OPERATOR_GRAMMAR.clone()),
            "ArrayAccessorSegment" => Some(ARRAY_ACCESSOR_SEGMENT.clone()),
            "ArrayExpressionSegment" => Some(ARRAY_EXPRESSION_SEGMENT.clone()),
            "ArrayLiteralSegment" => Some(ARRAY_LITERAL_SEGMENT.clone()),
            "ArrayTypeSegment" => Some(ARRAY_TYPE_SEGMENT.clone()),
            "AsAliasOperatorSegment" => Some(AS_ALIAS_OPERATOR_SEGMENT.clone()),
            "AsKeywordSegment" => Some(AS_KEYWORD_SEGMENT.clone()),
            "AscKeywordSegment" => Some(ASC_KEYWORD_SEGMENT.clone()),
            "AtSignLiteralSegment" => Some(AT_SIGN_LITERAL_SEGMENT.clone()),
            "AttachKeywordSegment" => Some(ATTACH_KEYWORD_SEGMENT.clone()),
            "AutoIncrementGrammar" => Some(AUTO_INCREMENT_GRAMMAR.clone()),
            "AutoincrementKeywordSegment" => Some(AUTOINCREMENT_KEYWORD_SEGMENT.clone()),
            "BackQuotedIdentifierSegment" => Some(BACK_QUOTED_IDENTIFIER_SEGMENT.clone()),
            "BareFunctionSegment" => Some(BARE_FUNCTION_SEGMENT.clone()),
            "BaseExpressionElementGrammar" => Some(BASE_EXPRESSION_ELEMENT_GRAMMAR.clone()),
            "BaseFileSegment" => Some(BASE_FILE_SEGMENT.clone()),
            "BaseSegment" => Some(BASE_SEGMENT.clone()),
            "BeforeKeywordSegment" => Some(BEFORE_KEYWORD_SEGMENT.clone()),
            "BeginKeywordSegment" => Some(BEGIN_KEYWORD_SEGMENT.clone()),
            "BetweenKeywordSegment" => Some(BETWEEN_KEYWORD_SEGMENT.clone()),
            "BigKeywordSegment" => Some(BIG_KEYWORD_SEGMENT.clone()),
            "BigintKeywordSegment" => Some(BIGINT_KEYWORD_SEGMENT.clone()),
            "BinaryKeywordSegment" => Some(BINARY_KEYWORD_SEGMENT.clone()),
            "BinaryOperatorGrammar" => Some(BINARY_OPERATOR_GRAMMAR.clone()),
            "BinaryOperatorSegment" => Some(BINARY_OPERATOR_SEGMENT.clone()),
            "BitwiseAndSegment" => Some(BITWISE_AND_SEGMENT.clone()),
            "BitwiseLShiftSegment" => Some(BITWISE_L_SHIFT_SEGMENT.clone()),
            "BitwiseOrSegment" => Some(BITWISE_OR_SEGMENT.clone()),
            "BitwiseRShiftSegment" => Some(BITWISE_R_SHIFT_SEGMENT.clone()),
            "BitwiseXorSegment" => Some(BITWISE_XOR_SEGMENT.clone()),
            "BlobKeywordSegment" => Some(BLOB_KEYWORD_SEGMENT.clone()),
            "BooleanBinaryOperatorGrammar" => Some(BOOLEAN_BINARY_OPERATOR_GRAMMAR.clone()),
            "BooleanKeywordSegment" => Some(BOOLEAN_KEYWORD_SEGMENT.clone()),
            "BooleanLiteralGrammar" => Some(BOOLEAN_LITERAL_GRAMMAR.clone()),
            "BracketedArguments" => Some(BRACKETED_ARGUMENTS.clone()),
            "BracketedColumnReferenceListGrammar" => Some(BRACKETED_COLUMN_REFERENCE_LIST_GRAMMAR.clone()),
            "BracketedSegment" => Some(BRACKETED_SEGMENT.clone()),
            "BracketedSetExpressionGrammar" => Some(BRACKETED_SET_EXPRESSION_GRAMMAR.clone()),
            "ByKeywordSegment" => Some(BY_KEYWORD_SEGMENT.clone()),
            "CTEColumnList" => Some(C_T_E_COLUMN_LIST.clone()),
            "CTEDefinitionSegment" => Some(C_T_E_DEFINITION_SEGMENT.clone()),
            "CascadeKeywordSegment" => Some(CASCADE_KEYWORD_SEGMENT.clone()),
            "CaseExpressionSegment" => Some(CASE_EXPRESSION_SEGMENT.clone()),
            "CaseKeywordSegment" => Some(CASE_KEYWORD_SEGMENT.clone()),
            "CastKeywordSegment" => Some(CAST_KEYWORD_SEGMENT.clone()),
            "CastOperatorSegment" => Some(CAST_OPERATOR_SEGMENT.clone()),
            "CharCharacterSetGrammar" => Some(CHAR_CHARACTER_SET_GRAMMAR.clone()),
            "CharacterKeywordSegment" => Some(CHARACTER_KEYWORD_SEGMENT.clone()),
            "CheckKeywordSegment" => Some(CHECK_KEYWORD_SEGMENT.clone()),
            "ClobKeywordSegment" => Some(CLOB_KEYWORD_SEGMENT.clone()),
            "CodeSegment" => Some(CODE_SEGMENT.clone()),
            "CollateGrammar" => Some(COLLATE_GRAMMAR.clone()),
            "CollateKeywordSegment" => Some(COLLATE_KEYWORD_SEGMENT.clone()),
            "CollationReferenceSegment" => Some(COLLATION_REFERENCE_SEGMENT.clone()),
            "ColonDelimiterSegment" => Some(COLON_DELIMITER_SEGMENT.clone()),
            "ColonLiteralSegment" => Some(COLON_LITERAL_SEGMENT.clone()),
            "ColonPrefixSegment" => Some(COLON_PREFIX_SEGMENT.clone()),
            "ColonSegment" => Some(COLON_SEGMENT.clone()),
            "ColumnConstraintDefaultGrammar" => Some(COLUMN_CONSTRAINT_DEFAULT_GRAMMAR.clone()),
            "ColumnConstraintSegment" => Some(COLUMN_CONSTRAINT_SEGMENT.clone()),
            "ColumnDefinitionSegment" => Some(COLUMN_DEFINITION_SEGMENT.clone()),
            "ColumnGeneratedGrammar" => Some(COLUMN_GENERATED_GRAMMAR.clone()),
            "ColumnKeywordSegment" => Some(COLUMN_KEYWORD_SEGMENT.clone()),
            "ColumnPathOperatorSegment" => Some(COLUMN_PATH_OPERATOR_SEGMENT.clone()),
            "ColumnReferenceSegment" => Some(COLUMN_REFERENCE_SEGMENT.clone()),
            "ColumnsExpressionFunctionContentsSegment" => Some(COLUMNS_EXPRESSION_FUNCTION_CONTENTS_SEGMENT.clone()),
            "ColumnsExpressionFunctionNameSegment" => Some(COLUMNS_EXPRESSION_FUNCTION_NAME_SEGMENT.clone()),
            "ColumnsExpressionGrammar" => Some(COLUMNS_EXPRESSION_GRAMMAR.clone()),
            "ColumnsExpressionNameGrammar" => Some(COLUMNS_EXPRESSION_NAME_GRAMMAR.clone()),
            "CommaSegment" => Some(COMMA_SEGMENT.clone()),
            "CommentClauseSegment" => Some(COMMENT_CLAUSE_SEGMENT.clone()),
            "CommentSegment" => Some(COMMENT_SEGMENT.clone()),
            "CommitKeywordSegment" => Some(COMMIT_KEYWORD_SEGMENT.clone()),
            "ComparisonOperatorGrammar" => Some(COMPARISON_OPERATOR_GRAMMAR.clone()),
            "ComparisonOperatorSegment" => Some(COMPARISON_OPERATOR_SEGMENT.clone()),
            "CompositeBinaryOperatorSegment" => Some(COMPOSITE_BINARY_OPERATOR_SEGMENT.clone()),
            "CompositeComparisonOperatorSegment" => Some(COMPOSITE_COMPARISON_OPERATOR_SEGMENT.clone()),
            "ConcatSegment" => Some(CONCAT_SEGMENT.clone()),
            "ConditionalCrossJoinKeywordsGrammar" => Some(CONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR.clone()),
            "ConditionalJoinKeywordsGrammar" => Some(CONDITIONAL_JOIN_KEYWORDS_GRAMMAR.clone()),
            "ConflictClauseSegment" => Some(CONFLICT_CLAUSE_SEGMENT.clone()),
            "ConflictKeywordSegment" => Some(CONFLICT_KEYWORD_SEGMENT.clone()),
            "ConflictTargetSegment" => Some(CONFLICT_TARGET_SEGMENT.clone()),
            "ConstraintKeywordSegment" => Some(CONSTRAINT_KEYWORD_SEGMENT.clone()),
            "CreateCastStatementSegment" => Some(CREATE_CAST_STATEMENT_SEGMENT.clone()),
            "CreateDatabaseStatementSegment" => Some(CREATE_DATABASE_STATEMENT_SEGMENT.clone()),
            "CreateFunctionStatementSegment" => Some(CREATE_FUNCTION_STATEMENT_SEGMENT.clone()),
            "CreateIndexStatementSegment" => Some(CREATE_INDEX_STATEMENT_SEGMENT.clone()),
            "CreateKeywordSegment" => Some(CREATE_KEYWORD_SEGMENT.clone()),
            "CreateModelStatementSegment" => Some(CREATE_MODEL_STATEMENT_SEGMENT.clone()),
            "CreateRoleStatementSegment" => Some(CREATE_ROLE_STATEMENT_SEGMENT.clone()),
            "CreateSchemaStatementSegment" => Some(CREATE_SCHEMA_STATEMENT_SEGMENT.clone()),
            "CreateSequenceOptionsSegment" => Some(CREATE_SEQUENCE_OPTIONS_SEGMENT.clone()),
            "CreateSequenceStatementSegment" => Some(CREATE_SEQUENCE_STATEMENT_SEGMENT.clone()),
            "CreateTableStatementSegment" => Some(CREATE_TABLE_STATEMENT_SEGMENT.clone()),
            "CreateTriggerStatementSegment" => Some(CREATE_TRIGGER_STATEMENT_SEGMENT.clone()),
            "CreateUserStatementSegment" => Some(CREATE_USER_STATEMENT_SEGMENT.clone()),
            "CreateViewStatementSegment" => Some(CREATE_VIEW_STATEMENT_SEGMENT.clone()),
            "CreateVirtualTableStatementSegment" => Some(CREATE_VIRTUAL_TABLE_STATEMENT_SEGMENT.clone()),
            "CrossKeywordSegment" => Some(CROSS_KEYWORD_SEGMENT.clone()),
            "CubeFunctionNameSegment" => Some(CUBE_FUNCTION_NAME_SEGMENT.clone()),
            "CubeRollupClauseSegment" => Some(CUBE_ROLLUP_CLAUSE_SEGMENT.clone()),
            "CurrentKeywordSegment" => Some(CURRENT_KEYWORD_SEGMENT.clone()),
            "Current_dateKeywordSegment" => Some(CURRENT_DATE_KEYWORD_SEGMENT.clone()),
            "Current_timeKeywordSegment" => Some(CURRENT_TIME_KEYWORD_SEGMENT.clone()),
            "Current_timestampKeywordSegment" => Some(CURRENT_TIMESTAMP_KEYWORD_SEGMENT.clone()),
            "DatabaseKeywordSegment" => Some(DATABASE_KEYWORD_SEGMENT.clone()),
            "DatabaseReferenceSegment" => Some(DATABASE_REFERENCE_SEGMENT.clone()),
            "DatatypeIdentifierSegment" => Some(DATATYPE_IDENTIFIER_SEGMENT.clone()),
            "DatatypeSegment" => Some(DATATYPE_SEGMENT.clone()),
            "DateKeywordSegment" => Some(DATE_KEYWORD_SEGMENT.clone()),
            "DatePartFunctionName" => Some(DATE_PART_FUNCTION_NAME.clone()),
            "DatePartFunctionNameSegment" => Some(DATE_PART_FUNCTION_NAME_SEGMENT.clone()),
            "DateTimeFunctionContentsSegment" => Some(DATE_TIME_FUNCTION_CONTENTS_SEGMENT.clone()),
            "DateTimeLiteralGrammar" => Some(DATE_TIME_LITERAL_GRAMMAR.clone()),
            "DatetimeKeywordSegment" => Some(DATETIME_KEYWORD_SEGMENT.clone()),
            "DatetimeUnitSegment" => Some(DATETIME_UNIT_SEGMENT.clone()),
            "DecimalKeywordSegment" => Some(DECIMAL_KEYWORD_SEGMENT.clone()),
            "Dedent" => Some(DEDENT.clone()),
            "DefaultKeywordSegment" => Some(DEFAULT_KEYWORD_SEGMENT.clone()),
            "DefaultValuesGrammar" => Some(DEFAULT_VALUES_GRAMMAR.clone()),
            "DeferrableKeywordSegment" => Some(DEFERRABLE_KEYWORD_SEGMENT.clone()),
            "DeferredKeywordSegment" => Some(DEFERRED_KEYWORD_SEGMENT.clone()),
            "DeleteKeywordSegment" => Some(DELETE_KEYWORD_SEGMENT.clone()),
            "DeleteStatementSegment" => Some(DELETE_STATEMENT_SEGMENT.clone()),
            "DelimiterGrammar" => Some(DELIMITER_GRAMMAR.clone()),
            "DescKeywordSegment" => Some(DESC_KEYWORD_SEGMENT.clone()),
            "DescribeStatementSegment" => Some(DESCRIBE_STATEMENT_SEGMENT.clone()),
            "DetachKeywordSegment" => Some(DETACH_KEYWORD_SEGMENT.clone()),
            "DistinctKeywordSegment" => Some(DISTINCT_KEYWORD_SEGMENT.clone()),
            "DivideSegment" => Some(DIVIDE_SEGMENT.clone()),
            "DoKeywordSegment" => Some(DO_KEYWORD_SEGMENT.clone()),
            "DollarLiteralSegment" => Some(DOLLAR_LITERAL_SEGMENT.clone()),
            "DotSegment" => Some(DOT_SEGMENT.clone()),
            "DoubleKeywordSegment" => Some(DOUBLE_KEYWORD_SEGMENT.clone()),
            "DropBehaviorGrammar" => Some(DROP_BEHAVIOR_GRAMMAR.clone()),
            "DropCastStatementSegment" => Some(DROP_CAST_STATEMENT_SEGMENT.clone()),
            "DropDatabaseStatementSegment" => Some(DROP_DATABASE_STATEMENT_SEGMENT.clone()),
            "DropFunctionStatementSegment" => Some(DROP_FUNCTION_STATEMENT_SEGMENT.clone()),
            "DropIndexStatementSegment" => Some(DROP_INDEX_STATEMENT_SEGMENT.clone()),
            "DropKeywordSegment" => Some(DROP_KEYWORD_SEGMENT.clone()),
            "DropModelStatementSegment" => Some(DROP_MODEL_STATEMENT_SEGMENT.clone()),
            "DropRoleStatementSegment" => Some(DROP_ROLE_STATEMENT_SEGMENT.clone()),
            "DropSchemaStatementSegment" => Some(DROP_SCHEMA_STATEMENT_SEGMENT.clone()),
            "DropSequenceStatementSegment" => Some(DROP_SEQUENCE_STATEMENT_SEGMENT.clone()),
            "DropTableStatementSegment" => Some(DROP_TABLE_STATEMENT_SEGMENT.clone()),
            "DropTriggerStatementSegment" => Some(DROP_TRIGGER_STATEMENT_SEGMENT.clone()),
            "DropTypeStatementSegment" => Some(DROP_TYPE_STATEMENT_SEGMENT.clone()),
            "DropUserStatementSegment" => Some(DROP_USER_STATEMENT_SEGMENT.clone()),
            "DropViewStatementSegment" => Some(DROP_VIEW_STATEMENT_SEGMENT.clone()),
            "EachKeywordSegment" => Some(EACH_KEYWORD_SEGMENT.clone()),
            "ElseClauseSegment" => Some(ELSE_CLAUSE_SEGMENT.clone()),
            "ElseKeywordSegment" => Some(ELSE_KEYWORD_SEGMENT.clone()),
            "EmptyStructLiteralBracketsSegment" => Some(EMPTY_STRUCT_LITERAL_BRACKETS_SEGMENT.clone()),
            "EmptyStructLiteralSegment" => Some(EMPTY_STRUCT_LITERAL_SEGMENT.clone()),
            "EndBracketSegment" => Some(END_BRACKET_SEGMENT.clone()),
            "EndCurlyBracketSegment" => Some(END_CURLY_BRACKET_SEGMENT.clone()),
            "EndKeywordSegment" => Some(END_KEYWORD_SEGMENT.clone()),
            "EndSquareBracketSegment" => Some(END_SQUARE_BRACKET_SEGMENT.clone()),
            "EqualsSegment" => Some(EQUALS_SEGMENT.clone()),
            "EscapeKeywordSegment" => Some(ESCAPE_KEYWORD_SEGMENT.clone()),
            "ExceptKeywordSegment" => Some(EXCEPT_KEYWORD_SEGMENT.clone()),
            "ExcludeKeywordSegment" => Some(EXCLUDE_KEYWORD_SEGMENT.clone()),
            "ExclusiveKeywordSegment" => Some(EXCLUSIVE_KEYWORD_SEGMENT.clone()),
            "ExistsKeywordSegment" => Some(EXISTS_KEYWORD_SEGMENT.clone()),
            "ExplainKeywordSegment" => Some(EXPLAIN_KEYWORD_SEGMENT.clone()),
            "ExplainStatementSegment" => Some(EXPLAIN_STATEMENT_SEGMENT.clone()),
            "ExpressionSegment" => Some(EXPRESSION_SEGMENT.clone()),
            "Expression_A_Grammar" => Some(EXPRESSION_A_GRAMMAR.clone()),
            "Expression_A_Unary_Operator_Grammar" => Some(EXPRESSION_A_UNARY_OPERATOR_GRAMMAR.clone()),
            "Expression_B_Grammar" => Some(EXPRESSION_B_GRAMMAR.clone()),
            "Expression_B_Unary_Operator_Grammar" => Some(EXPRESSION_B_UNARY_OPERATOR_GRAMMAR.clone()),
            "Expression_C_Grammar" => Some(EXPRESSION_C_GRAMMAR.clone()),
            "Expression_D_Grammar" => Some(EXPRESSION_D_GRAMMAR.clone()),
            "Expression_D_Potential_Select_Statement_Without_Brackets" => Some(EXPRESSION_D_POTENTIAL_SELECT_STATEMENT_WITHOUT_BRACKETS.clone()),
            "ExtendedNaturalJoinKeywordsGrammar" => Some(EXTENDED_NATURAL_JOIN_KEYWORDS_GRAMMAR.clone()),
            "ExtensionReferenceSegment" => Some(EXTENSION_REFERENCE_SEGMENT.clone()),
            "ExtraKeywordSegment" => Some(EXTRA_KEYWORD_SEGMENT.clone()),
            "FailKeywordSegment" => Some(FAIL_KEYWORD_SEGMENT.clone()),
            "FalseSegment" => Some(FALSE_SEGMENT.clone()),
            "FastKeywordSegment" => Some(FAST_KEYWORD_SEGMENT.clone()),
            "FetchClauseSegment" => Some(FETCH_CLAUSE_SEGMENT.clone()),
            "FileKeywordSegment" => Some(FILE_KEYWORD_SEGMENT.clone()),
            "FileSegment" => Some(FILE_SEGMENT.clone()),
            "FilterClauseGrammar" => Some(FILTER_CLAUSE_GRAMMAR.clone()),
            "FilterKeywordSegment" => Some(FILTER_KEYWORD_SEGMENT.clone()),
            "FirstKeywordSegment" => Some(FIRST_KEYWORD_SEGMENT.clone()),
            "FloatKeywordSegment" => Some(FLOAT_KEYWORD_SEGMENT.clone()),
            "FollowingKeywordSegment" => Some(FOLLOWING_KEYWORD_SEGMENT.clone()),
            "ForKeywordSegment" => Some(FOR_KEYWORD_SEGMENT.clone()),
            "ForeignKeyGrammar" => Some(FOREIGN_KEY_GRAMMAR.clone()),
            "ForeignKeywordSegment" => Some(FOREIGN_KEYWORD_SEGMENT.clone()),
            "FrameClauseSegment" => Some(FRAME_CLAUSE_SEGMENT.clone()),
            "FrameClauseUnitGrammar" => Some(FRAME_CLAUSE_UNIT_GRAMMAR.clone()),
            "FromClauseSegment" => Some(FROM_CLAUSE_SEGMENT.clone()),
            "FromClauseTerminatorGrammar" => Some(FROM_CLAUSE_TERMINATOR_GRAMMAR.clone()),
            "FromExpressionElementSegment" => Some(FROM_EXPRESSION_ELEMENT_SEGMENT.clone()),
            "FromExpressionSegment" => Some(FROM_EXPRESSION_SEGMENT.clone()),
            "FromKeywordSegment" => Some(FROM_KEYWORD_SEGMENT.clone()),
            "FullKeywordSegment" => Some(FULL_KEYWORD_SEGMENT.clone()),
            "FunctionContentsExpressionGrammar" => Some(FUNCTION_CONTENTS_EXPRESSION_GRAMMAR.clone()),
            "FunctionContentsGrammar" => Some(FUNCTION_CONTENTS_GRAMMAR.clone()),
            "FunctionContentsSegment" => Some(FUNCTION_CONTENTS_SEGMENT.clone()),
            "FunctionDefinitionGrammar" => Some(FUNCTION_DEFINITION_GRAMMAR.clone()),
            "FunctionNameIdentifierSegment" => Some(FUNCTION_NAME_IDENTIFIER_SEGMENT.clone()),
            "FunctionNameSegment" => Some(FUNCTION_NAME_SEGMENT.clone()),
            "FunctionParameterGrammar" => Some(FUNCTION_PARAMETER_GRAMMAR.clone()),
            "FunctionParameterListGrammar" => Some(FUNCTION_PARAMETER_LIST_GRAMMAR.clone()),
            "FunctionSegment" => Some(FUNCTION_SEGMENT.clone()),
            "GeneratedKeywordSegment" => Some(GENERATED_KEYWORD_SEGMENT.clone()),
            "GlobKeywordSegment" => Some(GLOB_KEYWORD_SEGMENT.clone()),
            "GlobOperatorSegment" => Some(GLOB_OPERATOR_SEGMENT.clone()),
            "GreaterThanOrEqualToSegment" => Some(GREATER_THAN_OR_EQUAL_TO_SEGMENT.clone()),
            "GreaterThanSegment" => Some(GREATER_THAN_SEGMENT.clone()),
            "GroupByClauseSegment" => Some(GROUP_BY_CLAUSE_SEGMENT.clone()),
            "GroupByClauseTerminatorGrammar" => Some(GROUP_BY_CLAUSE_TERMINATOR_GRAMMAR.clone()),
            "GroupKeywordSegment" => Some(GROUP_KEYWORD_SEGMENT.clone()),
            "GroupingExpressionList" => Some(GROUPING_EXPRESSION_LIST.clone()),
            "GroupingSetsClauseSegment" => Some(GROUPING_SETS_CLAUSE_SEGMENT.clone()),
            "GroupsKeywordSegment" => Some(GROUPS_KEYWORD_SEGMENT.clone()),
            "HavingClauseSegment" => Some(HAVING_CLAUSE_SEGMENT.clone()),
            "HavingClauseTerminatorGrammar" => Some(HAVING_CLAUSE_TERMINATOR_GRAMMAR.clone()),
            "HavingKeywordSegment" => Some(HAVING_KEYWORD_SEGMENT.clone()),
            "HorizontalJoinKeywordsGrammar" => Some(HORIZONTAL_JOIN_KEYWORDS_GRAMMAR.clone()),
            "IdentifierSegment" => Some(IDENTIFIER_SEGMENT.clone()),
            "IfExistsGrammar" => Some(IF_EXISTS_GRAMMAR.clone()),
            "IfKeywordSegment" => Some(IF_KEYWORD_SEGMENT.clone()),
            "IfNotExistsGrammar" => Some(IF_NOT_EXISTS_GRAMMAR.clone()),
            "IgnoreKeywordSegment" => Some(IGNORE_KEYWORD_SEGMENT.clone()),
            "IgnoreRespectNullsGrammar" => Some(IGNORE_RESPECT_NULLS_GRAMMAR.clone()),
            "ImmediateKeywordSegment" => Some(IMMEDIATE_KEYWORD_SEGMENT.clone()),
            "ImplicitIndent" => Some(IMPLICIT_INDENT.clone()),
            "InKeywordSegment" => Some(IN_KEYWORD_SEGMENT.clone()),
            "InOperatorGrammar" => Some(IN_OPERATOR_GRAMMAR.clone()),
            "IncrementalKeywordSegment" => Some(INCREMENTAL_KEYWORD_SEGMENT.clone()),
            "Indent" => Some(INDENT.clone()),
            "IndexColumnDefinitionSegment" => Some(INDEX_COLUMN_DEFINITION_SEGMENT.clone()),
            "IndexKeywordSegment" => Some(INDEX_KEYWORD_SEGMENT.clone()),
            "IndexReferenceSegment" => Some(INDEX_REFERENCE_SEGMENT.clone()),
            "IndexedKeywordSegment" => Some(INDEXED_KEYWORD_SEGMENT.clone()),
            "InitiallyKeywordSegment" => Some(INITIALLY_KEYWORD_SEGMENT.clone()),
            "InlinePathOperatorSegment" => Some(INLINE_PATH_OPERATOR_SEGMENT.clone()),
            "InnerKeywordSegment" => Some(INNER_KEYWORD_SEGMENT.clone()),
            "InsertKeywordSegment" => Some(INSERT_KEYWORD_SEGMENT.clone()),
            "InsertStatementSegment" => Some(INSERT_STATEMENT_SEGMENT.clone()),
            "InsteadKeywordSegment" => Some(INSTEAD_KEYWORD_SEGMENT.clone()),
            "Int2KeywordSegment" => Some(INT2_KEYWORD_SEGMENT.clone()),
            "Int8KeywordSegment" => Some(INT8_KEYWORD_SEGMENT.clone()),
            "IntKeywordSegment" => Some(INT_KEYWORD_SEGMENT.clone()),
            "IntegerKeywordSegment" => Some(INTEGER_KEYWORD_SEGMENT.clone()),
            "IntersectKeywordSegment" => Some(INTERSECT_KEYWORD_SEGMENT.clone()),
            "IntervalExpressionSegment" => Some(INTERVAL_EXPRESSION_SEGMENT.clone()),
            "IntoKeywordSegment" => Some(INTO_KEYWORD_SEGMENT.clone()),
            "IsClauseGrammar" => Some(IS_CLAUSE_GRAMMAR.clone()),
            "IsDistinctFromGrammar" => Some(IS_DISTINCT_FROM_GRAMMAR.clone()),
            "IsKeywordSegment" => Some(IS_KEYWORD_SEGMENT.clone()),
            "IsNullGrammar" => Some(IS_NULL_GRAMMAR.clone()),
            "IsnullKeywordSegment" => Some(ISNULL_KEYWORD_SEGMENT.clone()),
            "JoinClauseSegment" => Some(JOIN_CLAUSE_SEGMENT.clone()),
            "JoinKeywordSegment" => Some(JOIN_KEYWORD_SEGMENT.clone()),
            "JoinKeywordsGrammar" => Some(JOIN_KEYWORDS_GRAMMAR.clone()),
            "JoinLikeClauseGrammar" => Some(JOIN_LIKE_CLAUSE_GRAMMAR.clone()),
            "JoinOnConditionSegment" => Some(JOIN_ON_CONDITION_SEGMENT.clone()),
            "JoinTypeKeywordsGrammar" => Some(JOIN_TYPE_KEYWORDS_GRAMMAR.clone()),
            "JoinUsingConditionGrammar" => Some(JOIN_USING_CONDITION_GRAMMAR.clone()),
            "KeyKeywordSegment" => Some(KEY_KEYWORD_SEGMENT.clone()),
            "KeywordSegment" => Some(KEYWORD_SEGMENT.clone()),
            "LastKeywordSegment" => Some(LAST_KEYWORD_SEGMENT.clone()),
            "LeftKeywordSegment" => Some(LEFT_KEYWORD_SEGMENT.clone()),
            "LessThanOrEqualToSegment" => Some(LESS_THAN_OR_EQUAL_TO_SEGMENT.clone()),
            "LessThanSegment" => Some(LESS_THAN_SEGMENT.clone()),
            "LikeExpressionGrammar" => Some(LIKE_EXPRESSION_GRAMMAR.clone()),
            "LikeGrammar" => Some(LIKE_GRAMMAR.clone()),
            "LikeKeywordSegment" => Some(LIKE_KEYWORD_SEGMENT.clone()),
            "LikeOperatorSegment" => Some(LIKE_OPERATOR_SEGMENT.clone()),
            "LimitClauseSegment" => Some(LIMIT_CLAUSE_SEGMENT.clone()),
            "LimitKeywordSegment" => Some(LIMIT_KEYWORD_SEGMENT.clone()),
            "ListComprehensionGrammar" => Some(LIST_COMPREHENSION_GRAMMAR.clone()),
            "LiteralGrammar" => Some(LITERAL_GRAMMAR.clone()),
            "LiteralKeywordSegment" => Some(LITERAL_KEYWORD_SEGMENT.clone()),
            "LiteralSegment" => Some(LITERAL_SEGMENT.clone()),
            "LocalAliasSegment" => Some(LOCAL_ALIAS_SEGMENT.clone()),
            "MLTableExpressionSegment" => Some(M_L_TABLE_EXPRESSION_SEGMENT.clone()),
            "MapTypeSegment" => Some(MAP_TYPE_SEGMENT.clone()),
            "MatchConditionSegment" => Some(MATCH_CONDITION_SEGMENT.clone()),
            "MatchKeywordSegment" => Some(MATCH_KEYWORD_SEGMENT.clone()),
            "MaterializedKeywordSegment" => Some(MATERIALIZED_KEYWORD_SEGMENT.clone()),
            "MediumintKeywordSegment" => Some(MEDIUMINT_KEYWORD_SEGMENT.clone()),
            "MemoryKeywordSegment" => Some(MEMORY_KEYWORD_SEGMENT.clone()),
            "MergeDeleteClauseSegment" => Some(MERGE_DELETE_CLAUSE_SEGMENT.clone()),
            "MergeInsertClauseSegment" => Some(MERGE_INSERT_CLAUSE_SEGMENT.clone()),
            "MergeIntoLiteralGrammar" => Some(MERGE_INTO_LITERAL_GRAMMAR.clone()),
            "MergeMatchSegment" => Some(MERGE_MATCH_SEGMENT.clone()),
            "MergeMatchedClauseSegment" => Some(MERGE_MATCHED_CLAUSE_SEGMENT.clone()),
            "MergeNotMatchedClauseSegment" => Some(MERGE_NOT_MATCHED_CLAUSE_SEGMENT.clone()),
            "MergeStatementSegment" => Some(MERGE_STATEMENT_SEGMENT.clone()),
            "MergeUpdateClauseSegment" => Some(MERGE_UPDATE_CLAUSE_SEGMENT.clone()),
            "MinusSegment" => Some(MINUS_SEGMENT.clone()),
            "ModuloSegment" => Some(MODULO_SEGMENT.clone()),
            "MultiplySegment" => Some(MULTIPLY_SEGMENT.clone()),
            "NakedIdentifierSegment" => Some(NAKED_IDENTIFIER_SEGMENT.clone()),
            "NamedWindowExpressionSegment" => Some(NAMED_WINDOW_EXPRESSION_SEGMENT.clone()),
            "NamedWindowSegment" => Some(NAMED_WINDOW_SEGMENT.clone()),
            "NanLiteralSegment" => Some(NAN_LITERAL_SEGMENT.clone()),
            "NativeKeywordSegment" => Some(NATIVE_KEYWORD_SEGMENT.clone()),
            "NaturalJoinKeywordsGrammar" => Some(NATURAL_JOIN_KEYWORDS_GRAMMAR.clone()),
            "NaturalKeywordSegment" => Some(NATURAL_KEYWORD_SEGMENT.clone()),
            "NcharKeywordSegment" => Some(NCHAR_KEYWORD_SEGMENT.clone()),
            "NegativeSegment" => Some(NEGATIVE_SEGMENT.clone()),
            "NestedJoinGrammar" => Some(NESTED_JOIN_GRAMMAR.clone()),
            "NewlineSegment" => Some(NEWLINE_SEGMENT.clone()),
            "NoKeywordSegment" => Some(NO_KEYWORD_SEGMENT.clone()),
            "NocaseKeywordSegment" => Some(NOCASE_KEYWORD_SEGMENT.clone()),
            "NonSetSelectableGrammar" => Some(NON_SET_SELECTABLE_GRAMMAR.clone()),
            "NonStandardJoinTypeKeywordsGrammar" => Some(NON_STANDARD_JOIN_TYPE_KEYWORDS_GRAMMAR.clone()),
            "NonWithNonSelectableGrammar" => Some(NON_WITH_NON_SELECTABLE_GRAMMAR.clone()),
            "NonWithSelectableGrammar" => Some(NON_WITH_SELECTABLE_GRAMMAR.clone()),
            "NoneKeywordSegment" => Some(NONE_KEYWORD_SEGMENT.clone()),
            "NormalKeywordSegment" => Some(NORMAL_KEYWORD_SEGMENT.clone()),
            "NormalizedGrammar" => Some(NORMALIZED_GRAMMAR.clone()),
            "NotEnforcedGrammar" => Some(NOT_ENFORCED_GRAMMAR.clone()),
            "NotEqualToSegment" => Some(NOT_EQUAL_TO_SEGMENT.clone()),
            "NotKeywordSegment" => Some(NOT_KEYWORD_SEGMENT.clone()),
            "NotNullGrammar" => Some(NOT_NULL_GRAMMAR.clone()),
            "NotOperatorGrammar" => Some(NOT_OPERATOR_GRAMMAR.clone()),
            "NothingKeywordSegment" => Some(NOTHING_KEYWORD_SEGMENT.clone()),
            "NotnullKeywordSegment" => Some(NOTNULL_KEYWORD_SEGMENT.clone()),
            "NullKeywordSegment" => Some(NULL_KEYWORD_SEGMENT.clone()),
            "NullLiteralSegment" => Some(NULL_LITERAL_SEGMENT.clone()),
            "NullsKeywordSegment" => Some(NULLS_KEYWORD_SEGMENT.clone()),
            "NumericKeywordSegment" => Some(NUMERIC_KEYWORD_SEGMENT.clone()),
            "NumericLiteralSegment" => Some(NUMERIC_LITERAL_SEGMENT.clone()),
            "NvarcharKeywordSegment" => Some(NVARCHAR_KEYWORD_SEGMENT.clone()),
            "ObjectLiteralElementSegment" => Some(OBJECT_LITERAL_ELEMENT_SEGMENT.clone()),
            "ObjectLiteralSegment" => Some(OBJECT_LITERAL_SEGMENT.clone()),
            "ObjectReferenceDelimiterGrammar" => Some(OBJECT_REFERENCE_DELIMITER_GRAMMAR.clone()),
            "ObjectReferenceSegment" => Some(OBJECT_REFERENCE_SEGMENT.clone()),
            "ObjectReferenceTerminatorGrammar" => Some(OBJECT_REFERENCE_TERMINATOR_GRAMMAR.clone()),
            "OfKeywordSegment" => Some(OF_KEYWORD_SEGMENT.clone()),
            "OffKeywordSegment" => Some(OFF_KEYWORD_SEGMENT.clone()),
            "OffsetClauseSegment" => Some(OFFSET_CLAUSE_SEGMENT.clone()),
            "OffsetKeywordSegment" => Some(OFFSET_KEYWORD_SEGMENT.clone()),
            "OnKeywordSegment" => Some(ON_KEYWORD_SEGMENT.clone()),
            "OrKeywordSegment" => Some(OR_KEYWORD_SEGMENT.clone()),
            "OrOperatorGrammar" => Some(OR_OPERATOR_GRAMMAR.clone()),
            "OrReplaceGrammar" => Some(OR_REPLACE_GRAMMAR.clone()),
            "OrderByClauseSegment" => Some(ORDER_BY_CLAUSE_SEGMENT.clone()),
            "OrderByClauseTerminators" => Some(ORDER_BY_CLAUSE_TERMINATORS.clone()),
            "OrderKeywordSegment" => Some(ORDER_KEYWORD_SEGMENT.clone()),
            "OrderNoOrderGrammar" => Some(ORDER_NO_ORDER_GRAMMAR.clone()),
            "OthersKeywordSegment" => Some(OTHERS_KEYWORD_SEGMENT.clone()),
            "OuterKeywordSegment" => Some(OUTER_KEYWORD_SEGMENT.clone()),
            "OverClauseSegment" => Some(OVER_CLAUSE_SEGMENT.clone()),
            "OverKeywordSegment" => Some(OVER_KEYWORD_SEGMENT.clone()),
            "OverlapsClauseSegment" => Some(OVERLAPS_CLAUSE_SEGMENT.clone()),
            "ParameterNameSegment" => Some(PARAMETER_NAME_SEGMENT.clone()),
            "ParameterSegment" => Some(PARAMETER_SEGMENT.clone()),
            "ParameterizedSegment" => Some(PARAMETERIZED_SEGMENT.clone()),
            "PartitionClauseSegment" => Some(PARTITION_CLAUSE_SEGMENT.clone()),
            "PartitionKeywordSegment" => Some(PARTITION_KEYWORD_SEGMENT.clone()),
            "PassiveKeywordSegment" => Some(PASSIVE_KEYWORD_SEGMENT.clone()),
            "PathSegment" => Some(PATH_SEGMENT.clone()),
            "PatternMatchingGrammar" => Some(PATTERN_MATCHING_GRAMMAR.clone()),
            "PersistKeywordSegment" => Some(PERSIST_KEYWORD_SEGMENT.clone()),
            "PipeSegment" => Some(PIPE_SEGMENT.clone()),
            "PlanKeywordSegment" => Some(PLAN_KEYWORD_SEGMENT.clone()),
            "PlusSegment" => Some(PLUS_SEGMENT.clone()),
            "PositiveSegment" => Some(POSITIVE_SEGMENT.clone()),
            "PostFunctionGrammar" => Some(POST_FUNCTION_GRAMMAR.clone()),
            "PostTableExpressionGrammar" => Some(POST_TABLE_EXPRESSION_GRAMMAR.clone()),
            "PragmaKeywordSegment" => Some(PRAGMA_KEYWORD_SEGMENT.clone()),
            "PragmaReferenceSegment" => Some(PRAGMA_REFERENCE_SEGMENT.clone()),
            "PragmaStatementSegment" => Some(PRAGMA_STATEMENT_SEGMENT.clone()),
            "PreTableFunctionKeywordsGrammar" => Some(PRE_TABLE_FUNCTION_KEYWORDS_GRAMMAR.clone()),
            "PrecedingKeywordSegment" => Some(PRECEDING_KEYWORD_SEGMENT.clone()),
            "PrecisionKeywordSegment" => Some(PRECISION_KEYWORD_SEGMENT.clone()),
            "PrimaryKeyGrammar" => Some(PRIMARY_KEY_GRAMMAR.clone()),
            "PrimaryKeywordSegment" => Some(PRIMARY_KEYWORD_SEGMENT.clone()),
            "QualifiedNumericLiteralSegment" => Some(QUALIFIED_NUMERIC_LITERAL_SEGMENT.clone()),
            "QueryKeywordSegment" => Some(QUERY_KEYWORD_SEGMENT.clone()),
            "QuestionLiteralSegment" => Some(QUESTION_LITERAL_SEGMENT.clone()),
            "QuestionMarkSegment" => Some(QUESTION_MARK_SEGMENT.clone()),
            "QuotedIdentifierSegment" => Some(QUOTED_IDENTIFIER_SEGMENT.clone()),
            "QuotedLiteralSegment" => Some(QUOTED_LITERAL_SEGMENT.clone()),
            "RaiseKeywordSegment" => Some(RAISE_KEYWORD_SEGMENT.clone()),
            "RangeKeywordSegment" => Some(RANGE_KEYWORD_SEGMENT.clone()),
            "RawEqualsSegment" => Some(RAW_EQUALS_SEGMENT.clone()),
            "RawGreaterThanSegment" => Some(RAW_GREATER_THAN_SEGMENT.clone()),
            "RawLessThanSegment" => Some(RAW_LESS_THAN_SEGMENT.clone()),
            "RawNotSegment" => Some(RAW_NOT_SEGMENT.clone()),
            "RawSegment" => Some(RAW_SEGMENT.clone()),
            "RealKeywordSegment" => Some(REAL_KEYWORD_SEGMENT.clone()),
            "RecursiveKeywordSegment" => Some(RECURSIVE_KEYWORD_SEGMENT.clone()),
            "ReferenceDefinitionGrammar" => Some(REFERENCE_DEFINITION_GRAMMAR.clone()),
            "ReferenceMatchGrammar" => Some(REFERENCE_MATCH_GRAMMAR.clone()),
            "ReferencesKeywordSegment" => Some(REFERENCES_KEYWORD_SEGMENT.clone()),
            "ReferentialActionGrammar" => Some(REFERENTIAL_ACTION_GRAMMAR.clone()),
            "RegexpKeywordSegment" => Some(REGEXP_KEYWORD_SEGMENT.clone()),
            "ReindexKeywordSegment" => Some(REINDEX_KEYWORD_SEGMENT.clone()),
            "ReleaseKeywordSegment" => Some(RELEASE_KEYWORD_SEGMENT.clone()),
            "RenameKeywordSegment" => Some(RENAME_KEYWORD_SEGMENT.clone()),
            "ReplaceKeywordSegment" => Some(REPLACE_KEYWORD_SEGMENT.clone()),
            "ResetKeywordSegment" => Some(RESET_KEYWORD_SEGMENT.clone()),
            "RestartKeywordSegment" => Some(RESTART_KEYWORD_SEGMENT.clone()),
            "RestrictKeywordSegment" => Some(RESTRICT_KEYWORD_SEGMENT.clone()),
            "ReturningClauseSegment" => Some(RETURNING_CLAUSE_SEGMENT.clone()),
            "ReturningKeywordSegment" => Some(RETURNING_KEYWORD_SEGMENT.clone()),
            "RightKeywordSegment" => Some(RIGHT_KEYWORD_SEGMENT.clone()),
            "RoleReferenceSegment" => Some(ROLE_REFERENCE_SEGMENT.clone()),
            "RollbackKeywordSegment" => Some(ROLLBACK_KEYWORD_SEGMENT.clone()),
            "RollupFunctionNameSegment" => Some(ROLLUP_FUNCTION_NAME_SEGMENT.clone()),
            "RowKeywordSegment" => Some(ROW_KEYWORD_SEGMENT.clone()),
            "RowidKeywordSegment" => Some(ROWID_KEYWORD_SEGMENT.clone()),
            "RowsKeywordSegment" => Some(ROWS_KEYWORD_SEGMENT.clone()),
            "RtrimKeywordSegment" => Some(RTRIM_KEYWORD_SEGMENT.clone()),
            "SamplingExpressionSegment" => Some(SAMPLING_EXPRESSION_SEGMENT.clone()),
            "SavepointKeywordSegment" => Some(SAVEPOINT_KEYWORD_SEGMENT.clone()),
            "SchemaReferenceSegment" => Some(SCHEMA_REFERENCE_SEGMENT.clone()),
            "SelectClauseElementSegment" => Some(SELECT_CLAUSE_ELEMENT_SEGMENT.clone()),
            "SelectClauseModifierSegment" => Some(SELECT_CLAUSE_MODIFIER_SEGMENT.clone()),
            "SelectClauseSegment" => Some(SELECT_CLAUSE_SEGMENT.clone()),
            "SelectClauseTerminatorGrammar" => Some(SELECT_CLAUSE_TERMINATOR_GRAMMAR.clone()),
            "SelectKeywordSegment" => Some(SELECT_KEYWORD_SEGMENT.clone()),
            "SelectStatementSegment" => Some(SELECT_STATEMENT_SEGMENT.clone()),
            "SelectableGrammar" => Some(SELECTABLE_GRAMMAR.clone()),
            "SemicolonSegment" => Some(SEMICOLON_SEGMENT.clone()),
            "SequenceMaxValueGrammar" => Some(SEQUENCE_MAX_VALUE_GRAMMAR.clone()),
            "SequenceMinValueGrammar" => Some(SEQUENCE_MIN_VALUE_GRAMMAR.clone()),
            "SequenceReferenceSegment" => Some(SEQUENCE_REFERENCE_SEGMENT.clone()),
            "SetClauseListSegment" => Some(SET_CLAUSE_LIST_SEGMENT.clone()),
            "SetClauseSegment" => Some(SET_CLAUSE_SEGMENT.clone()),
            "SetExpressionSegment" => Some(SET_EXPRESSION_SEGMENT.clone()),
            "SetKeywordSegment" => Some(SET_KEYWORD_SEGMENT.clone()),
            "SetOperatorSegment" => Some(SET_OPERATOR_SEGMENT.clone()),
            "SetSchemaStatementSegment" => Some(SET_SCHEMA_STATEMENT_SEGMENT.clone()),
            "ShorthandCastSegment" => Some(SHORTHAND_CAST_SEGMENT.clone()),
            "SignedSegmentGrammar" => Some(SIGNED_SEGMENT_GRAMMAR.clone()),
            "SingleIdentifierGrammar" => Some(SINGLE_IDENTIFIER_GRAMMAR.clone()),
            "SingleIdentifierListSegment" => Some(SINGLE_IDENTIFIER_LIST_SEGMENT.clone()),
            "SingleQuotedIdentifierSegment" => Some(SINGLE_QUOTED_IDENTIFIER_SEGMENT.clone()),
            "SizedArrayTypeSegment" => Some(SIZED_ARRAY_TYPE_SEGMENT.clone()),
            "SlashSegment" => Some(SLASH_SEGMENT.clone()),
            "SliceSegment" => Some(SLICE_SEGMENT.clone()),
            "SmallintKeywordSegment" => Some(SMALLINT_KEYWORD_SEGMENT.clone()),
            "StarSegment" => Some(STAR_SEGMENT.clone()),
            "StartBracketSegment" => Some(START_BRACKET_SEGMENT.clone()),
            "StartCurlyBracketSegment" => Some(START_CURLY_BRACKET_SEGMENT.clone()),
            "StartSquareBracketSegment" => Some(START_SQUARE_BRACKET_SEGMENT.clone()),
            "StatementSegment" => Some(STATEMENT_SEGMENT.clone()),
            "StoredKeywordSegment" => Some(STORED_KEYWORD_SEGMENT.clone()),
            "StrictKeywordSegment" => Some(STRICT_KEYWORD_SEGMENT.clone()),
            "StringBinaryOperatorGrammar" => Some(STRING_BINARY_OPERATOR_GRAMMAR.clone()),
            "StructLiteralSegment" => Some(STRUCT_LITERAL_SEGMENT.clone()),
            "StructTypeSegment" => Some(STRUCT_TYPE_SEGMENT.clone()),
            "SymbolSegment" => Some(SYMBOL_SEGMENT.clone()),
            "TableConstraintSegment" => Some(TABLE_CONSTRAINT_SEGMENT.clone()),
            "TableEndClauseSegment" => Some(TABLE_END_CLAUSE_SEGMENT.clone()),
            "TableExpressionSegment" => Some(TABLE_EXPRESSION_SEGMENT.clone()),
            "TableKeywordSegment" => Some(TABLE_KEYWORD_SEGMENT.clone()),
            "TableReferenceSegment" => Some(TABLE_REFERENCE_SEGMENT.clone()),
            "TablespaceReferenceSegment" => Some(TABLESPACE_REFERENCE_SEGMENT.clone()),
            "TagReferenceSegment" => Some(TAG_REFERENCE_SEGMENT.clone()),
            "Tail_Recurse_Expression_A_Grammar" => Some(TAIL_RECURSE_EXPRESSION_A_GRAMMAR.clone()),
            "Tail_Recurse_Expression_B_Grammar" => Some(TAIL_RECURSE_EXPRESSION_B_GRAMMAR.clone()),
            "TempKeywordSegment" => Some(TEMP_KEYWORD_SEGMENT.clone()),
            "TemporalQuerySegment" => Some(TEMPORAL_QUERY_SEGMENT.clone()),
            "TemporaryGrammar" => Some(TEMPORARY_GRAMMAR.clone()),
            "TemporaryKeywordSegment" => Some(TEMPORARY_KEYWORD_SEGMENT.clone()),
            "TemporaryTransientGrammar" => Some(TEMPORARY_TRANSIENT_GRAMMAR.clone()),
            "TextKeywordSegment" => Some(TEXT_KEYWORD_SEGMENT.clone()),
            "ThenKeywordSegment" => Some(THEN_KEYWORD_SEGMENT.clone()),
            "TiesKeywordSegment" => Some(TIES_KEYWORD_SEGMENT.clone()),
            "TildeSegment" => Some(TILDE_SEGMENT.clone()),
            "TimeWithTZGrammar" => Some(TIME_WITH_T_Z_GRAMMAR.clone()),
            "TimeZoneGrammar" => Some(TIME_ZONE_GRAMMAR.clone()),
            "TinyintKeywordSegment" => Some(TINYINT_KEYWORD_SEGMENT.clone()),
            "ToKeywordSegment" => Some(TO_KEYWORD_SEGMENT.clone()),
            "TransactionKeywordSegment" => Some(TRANSACTION_KEYWORD_SEGMENT.clone()),
            "TransactionStatementSegment" => Some(TRANSACTION_STATEMENT_SEGMENT.clone()),
            "TriggerKeywordSegment" => Some(TRIGGER_KEYWORD_SEGMENT.clone()),
            "TriggerReferenceSegment" => Some(TRIGGER_REFERENCE_SEGMENT.clone()),
            "TrimParametersGrammar" => Some(TRIM_PARAMETERS_GRAMMAR.clone()),
            "TrueSegment" => Some(TRUE_SEGMENT.clone()),
            "TruncateKeywordSegment" => Some(TRUNCATE_KEYWORD_SEGMENT.clone()),
            "TruncateStatementSegment" => Some(TRUNCATE_STATEMENT_SEGMENT.clone()),
            "TupleSegment" => Some(TUPLE_SEGMENT.clone()),
            "TypedArrayLiteralSegment" => Some(TYPED_ARRAY_LITERAL_SEGMENT.clone()),
            "TypedStructLiteralSegment" => Some(TYPED_STRUCT_LITERAL_SEGMENT.clone()),
            "UnboundedKeywordSegment" => Some(UNBOUNDED_KEYWORD_SEGMENT.clone()),
            "UnconditionalCrossJoinKeywordsGrammar" => Some(UNCONDITIONAL_CROSS_JOIN_KEYWORDS_GRAMMAR.clone()),
            "UnconditionalJoinKeywordsGrammar" => Some(UNCONDITIONAL_JOIN_KEYWORDS_GRAMMAR.clone()),
            "UnionGrammar" => Some(UNION_GRAMMAR.clone()),
            "UnionKeywordSegment" => Some(UNION_KEYWORD_SEGMENT.clone()),
            "UniqueKeyGrammar" => Some(UNIQUE_KEY_GRAMMAR.clone()),
            "UniqueKeywordSegment" => Some(UNIQUE_KEYWORD_SEGMENT.clone()),
            "UnknownLiteralSegment" => Some(UNKNOWN_LITERAL_SEGMENT.clone()),
            "UnorderedSelectStatementSegment" => Some(UNORDERED_SELECT_STATEMENT_SEGMENT.clone()),
            "UnorderedSetExpressionSegment" => Some(UNORDERED_SET_EXPRESSION_SEGMENT.clone()),
            "UnsignedKeywordSegment" => Some(UNSIGNED_KEYWORD_SEGMENT.clone()),
            "UpdateKeywordSegment" => Some(UPDATE_KEYWORD_SEGMENT.clone()),
            "UpdateStatementSegment" => Some(UPDATE_STATEMENT_SEGMENT.clone()),
            "UpsertClauseSegment" => Some(UPSERT_CLAUSE_SEGMENT.clone()),
            "UseStatementSegment" => Some(USE_STATEMENT_SEGMENT.clone()),
            "UsingKeywordSegment" => Some(USING_KEYWORD_SEGMENT.clone()),
            "VacuumKeywordSegment" => Some(VACUUM_KEYWORD_SEGMENT.clone()),
            "ValuesClauseSegment" => Some(VALUES_CLAUSE_SEGMENT.clone()),
            "ValuesKeywordSegment" => Some(VALUES_KEYWORD_SEGMENT.clone()),
            "VarcharKeywordSegment" => Some(VARCHAR_KEYWORD_SEGMENT.clone()),
            "VaryingKeywordSegment" => Some(VARYING_KEYWORD_SEGMENT.clone()),
            "ViewKeywordSegment" => Some(VIEW_KEYWORD_SEGMENT.clone()),
            "VirtualKeywordSegment" => Some(VIRTUAL_KEYWORD_SEGMENT.clone()),
            "WalKeywordSegment" => Some(WAL_KEYWORD_SEGMENT.clone()),
            "WhenClauseSegment" => Some(WHEN_CLAUSE_SEGMENT.clone()),
            "WhenKeywordSegment" => Some(WHEN_KEYWORD_SEGMENT.clone()),
            "WhereClauseSegment" => Some(WHERE_CLAUSE_SEGMENT.clone()),
            "WhereClauseTerminatorGrammar" => Some(WHERE_CLAUSE_TERMINATOR_GRAMMAR.clone()),
            "WhereKeywordSegment" => Some(WHERE_KEYWORD_SEGMENT.clone()),
            "WhitespaceSegment" => Some(WHITESPACE_SEGMENT.clone()),
            "WildcardExpressionSegment" => Some(WILDCARD_EXPRESSION_SEGMENT.clone()),
            "WildcardIdentifierSegment" => Some(WILDCARD_IDENTIFIER_SEGMENT.clone()),
            "WindowKeywordSegment" => Some(WINDOW_KEYWORD_SEGMENT.clone()),
            "WindowSpecificationSegment" => Some(WINDOW_SPECIFICATION_SEGMENT.clone()),
            "WithCompoundNonSelectStatementSegment" => Some(WITH_COMPOUND_NON_SELECT_STATEMENT_SEGMENT.clone()),
            "WithCompoundStatementSegment" => Some(WITH_COMPOUND_STATEMENT_SEGMENT.clone()),
            "WithDataClauseSegment" => Some(WITH_DATA_CLAUSE_SEGMENT.clone()),
            "WithFillSegment" => Some(WITH_FILL_SEGMENT.clone()),
            "WithKeywordSegment" => Some(WITH_KEYWORD_SEGMENT.clone()),
            "WithNoSchemaBindingClauseSegment" => Some(WITH_NO_SCHEMA_BINDING_CLAUSE_SEGMENT.clone()),
            "WithoutKeywordSegment" => Some(WITHOUT_KEYWORD_SEGMENT.clone()),
            "WordSegment" => Some(WORD_SEGMENT.clone()),
            "YesKeywordSegment" => Some(YES_KEYWORD_SEGMENT.clone()),
            _ => None,
    }
}

pub fn get_sqlite_segment_type(name: &str) -> Option<&'static str> {
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
            "CommentSegment" => Some("comment"),
            "ComparisonOperatorSegment" => Some("comparison_operator"),
            "CompositeBinaryOperatorSegment" => Some("binary_operator"),
            "CompositeComparisonOperatorSegment" => Some("comparison_operator"),
            "ConcatSegment" => Some("binary_operator"),
            "ConflictClauseSegment" => Some("conflict_clause"),
            "ConflictTargetSegment" => Some("conflict_target"),
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
            "CreateVirtualTableStatementSegment" => Some("create_virtual_table_statement"),
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
            "JoinClauseSegment" => Some("join_clause"),
            "JoinOnConditionSegment" => Some("join_on_condition"),
            "KeywordSegment" => Some("keyword"),
            "LessThanOrEqualToSegment" => Some("comparison_operator"),
            "LessThanSegment" => Some("comparison_operator"),
            "LimitClauseSegment" => Some("limit_clause"),
            "LiteralKeywordSegment" => Some("literal"),
            "LiteralSegment" => Some("literal"),
            "LocalAliasSegment" => Some("local_alias_segment"),
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
            "ParameterizedSegment" => Some("parameterized_expression"),
            "PartitionClauseSegment" => Some("partitionby_clause"),
            "PathSegment" => Some("path_segment"),
            "PragmaReferenceSegment" => Some("pragma_reference"),
            "PragmaStatementSegment" => Some("pragma_statement"),
            "QualifiedNumericLiteralSegment" => Some("numeric_literal"),
            "RawSegment" => Some("raw"),
            "ReturningClauseSegment" => Some("returning_clause"),
            "RoleReferenceSegment" => Some("role_reference"),
            "RollupFunctionNameSegment" => Some("function_name"),
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
            "TransactionStatementSegment" => Some("transaction_statement"),
            "TriggerReferenceSegment" => Some("trigger_reference"),
            "TruncateStatementSegment" => Some("truncate_table"),
            "TupleSegment" => Some("tuple"),
            "TypedArrayLiteralSegment" => Some("typed_array_literal"),
            "TypedStructLiteralSegment" => Some("typed_struct_literal"),
            "UnorderedSelectStatementSegment" => Some("select_statement"),
            "UnorderedSetExpressionSegment" => Some("set_expression"),
            "UpdateStatementSegment" => Some("update_statement"),
            "UpsertClauseSegment" => Some("upsert_clause"),
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

pub fn get_sqlite_root_grammar() -> Arc<Grammar> {
    get_sqlite_segment_grammar(
        "FileSegment"
    ).expect("Root grammar missing.")
}
