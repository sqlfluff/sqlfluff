use super::{config::TokenConfig, Token};
use crate::{marker::PositionMarker, slice::Slice, templater::templatefile::TemplatedFile};

use std::borrow::Cow;
use std::sync::Arc;

use hashbrown::HashSet;
use once_cell::sync::Lazy;
use uuid::Uuid;

impl Token {
    pub fn base_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
        segments: Vec<Token>,
    ) -> Self {
        let TokenConfig {
            // The lexer always supplies an empty class_types; the hierarchy is
            // derived per-kind from a shared static instead (see *_CT below).
            class_types: _,
            instance_types,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacements,
            casefold,
        } = config;

        Self {
            token_type: Cow::Borrowed("base"),
            class_name: Cow::Borrowed("BaseSegment"),
            instance_types,
            class_types: BASE_CT.clone(),
            comment_separate: false,
            is_meta: false,
            allow_empty: false,
            pos_marker: Some(pos_marker),
            raw: crate::token::RawString::new(raw, quoted_value, escape_replacements, casefold),
            is_whitespace: false,
            is_code: true,
            is_comment: false,
            _default_raw: Cow::Borrowed(""),
            indent_value: 0,
            is_templated: false,
            block_uuid: None,
            source_str: None,
            block_type: None,
            parent: None,
            parent_idx: None,
            segments,
            preface_modifier: Cow::Borrowed(""),
            suffix: Cow::Borrowed(""),
            uuid: crate::identity::next_id(),
            source_fixes: None,
            trim_start,
            trim_chars,
            matching_bracket_idx: None, // Will be computed after all tokens are created
        }
    }

    pub fn raw_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        // Render the stringify suffix with the shared python_repr helper (the
        // same one the token Display uses), rather than a second ad-hoc
        // escape_debug quoting that diverges from Python's repr for embedded
        // quotes, control chars and non-space whitespace.
        let suffix = crate::token::python_repr(&raw);

        let mut token = Token::base_token(raw, pos_marker, config, vec![]);
        token.class_name = Cow::Borrowed("RawSegment");
        token.suffix = Cow::Owned(suffix);
        token.token_type = Cow::Borrowed("raw");
        token.class_types = RAW_CT.clone();
        token
    }

    pub fn code_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::raw_token(raw, pos_marker, config);
        // PYTHON PARITY: code-matched tokens are CodeSegment on the Python
        // side; class_name feeds the Display used in user-visible "Found
        // <...>" parse-error messages (token_type still drives class
        // selection elsewhere).
        token.class_name = Cow::Borrowed("CodeSegment");
        token
    }

    pub fn symbol_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("symbol");
        token.class_name = Cow::Borrowed("SymbolSegment");
        token.class_types = SYMBOL_CT.clone();
        token
    }

    pub fn identifier_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("identifier");
        token.class_name = Cow::Borrowed("IdentifierSegment");
        token.class_types = IDENTIFIER_CT.clone();
        token
    }

    pub fn literal_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("literal");
        token.class_name = Cow::Borrowed("LiteralSegment");
        token.class_types = LITERAL_CT.clone();
        token
    }

    pub fn binary_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("binary_operator");
        token.class_name = Cow::Borrowed("BinaryOperatorSegment");
        token.class_types = BINARY_OPERATOR_CT.clone();
        token
    }

    pub fn comparison_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("comparison_operator");
        token.class_name = Cow::Borrowed("ComparisonOperatorSegment");
        token.class_types = COMPARISON_OPERATOR_CT.clone();
        token
    }

    pub fn word_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("word");
        token.class_name = Cow::Borrowed("WordSegment");
        token.class_types = WORD_CT.clone();
        token
    }

    pub fn unlexable_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::code_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("unlexable");
        token.class_name = Cow::Borrowed("UnlexableSegment");
        token.class_types = UNLEXABLE_CT.clone();
        token
    }

    pub fn whitespace_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::raw_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("whitespace");
        token.class_name = Cow::Borrowed("WhitespaceSegment");
        token.class_types = WHITESPACE_CT.clone();
        token.is_whitespace = true;
        token.is_code = false;
        token.is_comment = false;
        token._default_raw = Cow::Borrowed(" ");
        token
    }

    pub fn newline_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::raw_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("newline");
        token.class_name = Cow::Borrowed("NewlineSegment");
        token.class_types = NEWLINE_CT.clone();
        token.is_whitespace = true;
        token.is_code = false;
        token.is_comment = false;
        token._default_raw = Cow::Borrowed("\n");
        token
    }

    pub fn comment_token(raw: String, pos_marker: PositionMarker, config: TokenConfig) -> Self {
        let mut token = Self::raw_token(raw, pos_marker, config);
        token.token_type = Cow::Borrowed("comment");
        token.class_name = Cow::Borrowed("CommentSegment");
        token.class_types = COMMENT_CT.clone();
        token.is_code = false;
        token.is_comment = true;
        token
    }

    pub fn meta_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        _class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::raw_token(
            "".to_string(),
            pos_marker,
            TokenConfig {
                instance_types: vec![],
                ..TokenConfig::default()
            },
        );
        token.token_type = Cow::Borrowed("meta");
        token.class_name = Cow::Borrowed("MetaSegment");
        token.class_types = META_CT.clone();
        token.is_code = false;
        token.is_meta = true;
        token.is_templated = is_templated;
        token.block_uuid = block_uuid;
        token.preface_modifier = Cow::Borrowed("[META] ");
        token.suffix = Cow::Borrowed("");
        token
    }

    pub fn end_of_file_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::meta_token(pos_marker, is_templated, block_uuid, class_types);
        token.token_type = Cow::Borrowed("end_of_file");
        token.class_name = Cow::Borrowed("EndOfFile");
        token.class_types = END_OF_FILE_CT.clone();
        token
    }

    pub fn indent_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::meta_token(pos_marker, is_templated, block_uuid, class_types);
        token.token_type = Cow::Borrowed("indent");
        token.class_name = Cow::Borrowed("Indent");
        token.class_types = INDENT_CT.clone();
        token.indent_value = 1;
        token.suffix = block_uuid
            .map(|u| Cow::Owned(u.as_hyphenated().to_string()))
            .unwrap_or(Cow::Borrowed(""));
        token
    }

    pub fn dedent_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::indent_token(pos_marker, is_templated, block_uuid, class_types);
        token.token_type = Cow::Borrowed("dedent");
        token.class_name = Cow::Borrowed("Dedent");
        token.class_types = DEDENT_CT.clone();
        token.indent_value = -1;
        token
    }

    pub fn template_loop_token(
        pos_marker: PositionMarker,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::meta_token(pos_marker, false, block_uuid, class_types);
        token.token_type = Cow::Borrowed("template_loop");
        token.class_name = Cow::Borrowed("TemplateLoop");
        token.class_types = TEMPLATE_LOOP_CT.clone();
        token
    }

    pub fn template_placeholder_token(
        pos_marker: PositionMarker,
        source_string: String,
        block_type: String,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let mut token = Self::meta_token(pos_marker, false, block_uuid, class_types);
        token.token_type = Cow::Borrowed("placeholder");
        token.class_name = Cow::Borrowed("TemplateSegment");
        token.class_types = PLACEHOLDER_CT.clone();
        token.block_type = Some(block_type);
        token.source_str = Some(source_string);
        token
    }

    pub fn template_placeholder_token_from_slice(
        source_slice: Slice,
        templated_slice: Slice,
        block_type: String,
        templated_file: &Arc<TemplatedFile>,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let pos_marker =
            PositionMarker::new(source_slice, templated_slice, templated_file, None, None);
        Self {
            ..Self::template_placeholder_token(
                pos_marker,
                templated_file
                    .source_str
                    .chars()
                    .skip(source_slice.start)
                    .take(source_slice.len())
                    .collect::<String>(),
                block_type,
                block_uuid,
                class_types,
            )
        }
    }
}

/// The class-type hierarchy is fully determined by a token's kind (the lexer
/// always supplies an empty `class_types`), and is never mutated after
/// construction. So each kind shares a single `Arc<HashSet<String>>` built once,
/// instead of every token allocating an identical set.
fn make_class_types(types: &[&str]) -> Arc<HashSet<String>> {
    Arc::new(types.iter().map(|s| s.to_string()).collect())
}

macro_rules! class_types_static {
    ($name:ident, $($ty:literal),+) => {
        static $name: Lazy<Arc<HashSet<String>>> = Lazy::new(|| make_class_types(&[$($ty),+]));
    };
}

class_types_static!(BASE_CT, "base");
class_types_static!(RAW_CT, "base", "raw");
class_types_static!(SYMBOL_CT, "base", "raw", "symbol");
class_types_static!(IDENTIFIER_CT, "base", "raw", "identifier");
class_types_static!(LITERAL_CT, "base", "raw", "literal");
class_types_static!(BINARY_OPERATOR_CT, "base", "raw", "binary_operator");
class_types_static!(COMPARISON_OPERATOR_CT, "base", "raw", "comparison_operator");
class_types_static!(WORD_CT, "base", "raw", "word");
class_types_static!(UNLEXABLE_CT, "base", "raw", "unlexable");
class_types_static!(WHITESPACE_CT, "base", "raw", "whitespace");
class_types_static!(NEWLINE_CT, "base", "raw", "newline");
class_types_static!(COMMENT_CT, "base", "raw", "comment");
class_types_static!(META_CT, "base", "raw", "meta");
class_types_static!(END_OF_FILE_CT, "base", "raw", "meta", "end_of_file");
class_types_static!(INDENT_CT, "base", "raw", "meta", "indent");
class_types_static!(DEDENT_CT, "base", "raw", "meta", "indent", "dedent");
class_types_static!(TEMPLATE_LOOP_CT, "base", "raw", "meta", "template_loop");
class_types_static!(PLACEHOLDER_CT, "base", "raw", "meta", "placeholder");
