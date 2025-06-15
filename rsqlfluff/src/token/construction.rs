use super::Token;
use crate::{marker::PositionMarker, slice::Slice, templater::templatefile::TemplatedFile};

use std::sync::Arc;

use hashbrown::HashSet;
use uuid::Uuid;

impl Token {
    pub fn base_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        segments: Vec<Token>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_types, class_types) = iter_base_types("base", class_types.clone());
        Self {
            token_type: token_types,
            instance_types,
            class_types,
            comment_separate: false,
            is_meta: false,
            allow_empty: false,
            pos_marker: Some(pos_marker),
            raw,
            is_whitespace: false,
            is_code: true,
            is_comment: false,
            _default_raw: "".to_string(),
            indent_value: 0,
            is_templated: false,
            block_uuid: None,
            source_str: None,
            block_type: None,
            parent: None.into(),
            parent_idx: None.into(),
            segments,
            preface_modifier: "".to_string(),
            suffix: "".to_string(),
            uuid: Uuid::new_v4().as_u128(),
            source_fixes: None,
            trim_start,
            trim_chars,
            cache_key,
        }
    }

    pub fn raw_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("raw", class_types);
        Self {
            token_type,
            // Match python's string
            suffix: format!("'{}'", raw.escape_debug().to_string().trim_matches('"')),
            ..Token::base_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                vec![],
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn code_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        Self {
            ..Self::raw_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn symbol_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("symbol", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn identifier_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("identifier", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn literal_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("literal", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn binary_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("binary_operator", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn comparison_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("comparison_operator", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn word_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("word", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn unlexable_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("unlexable", class_types);
        Self {
            token_type,
            ..Self::code_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn whitespace_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("whitespace", class_types);
        Self {
            token_type,
            is_whitespace: true,
            is_code: false,
            is_comment: false,
            _default_raw: " ".to_string(),
            ..Self::raw_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn newline_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("newline", class_types);
        Self {
            token_type,
            is_whitespace: true,
            is_code: false,
            is_comment: false,
            _default_raw: "\n".to_string(),
            ..Self::raw_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn comment_token(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("comment", class_types);
        Self {
            token_type,
            is_code: false,
            is_comment: true,
            ..Self::raw_token(
                raw,
                pos_marker,
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                cache_key,
            )
        }
    }

    pub fn meta_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
        cache_key: String,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("meta", class_types);
        Self {
            token_type,
            is_code: false,
            is_meta: true,
            is_templated,
            block_uuid,
            preface_modifier: "[META] ".to_string(),
            suffix: String::new(),
            ..Self::raw_token(
                "".to_string(),
                pos_marker,
                class_types,
                vec![],
                None,
                None,
                cache_key,
            )
        }
    }

    pub fn end_of_file_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("end_of_file", class_types);
        Self {
            token_type,
            ..Self::meta_token(
                pos_marker,
                is_templated,
                block_uuid,
                class_types,
                "eof_token".to_string(),
            )
        }
    }

    pub fn indent_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
        cache_key: Option<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("indent", class_types);
        Self {
            token_type,
            indent_value: 1,
            suffix: block_uuid
                .map(|u| u.as_hyphenated().to_string())
                .unwrap_or_default(),
            ..Self::meta_token(
                pos_marker,
                is_templated,
                block_uuid,
                class_types,
                cache_key.unwrap_or("indent".to_string()),
            )
        }
    }

    pub fn dedent_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("dedent", class_types);
        Self {
            token_type,
            indent_value: -1,
            ..Self::indent_token(
                pos_marker,
                is_templated,
                block_uuid,
                class_types,
                Some("dedent".to_string()),
            )
        }
    }

    pub fn template_loop_token(
        pos_marker: PositionMarker,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("template_loop", class_types);
        Self {
            token_type,
            ..Self::meta_token(
                pos_marker,
                false,
                block_uuid,
                class_types,
                "loop_token".to_string(),
            )
        }
    }

    pub fn template_placeholder_token(
        pos_marker: PositionMarker,
        source_string: String,
        block_type: String,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("placeholder", class_types);
        Self {
            token_type,
            block_type: Some(block_type),
            source_str: Some(source_string),
            ..Self::meta_token(
                pos_marker,
                false,
                block_uuid,
                class_types,
                "placeholder_token".to_string(),
            )
        }
    }

    pub fn template_placeholder_token_from_slice(
        source_slice: Slice,
        templated_slice: Slice,
        block_type: String,
        templated_file: &Arc<TemplatedFile>,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let pos_marker = PositionMarker::new(
            source_slice.clone(),
            templated_slice,
            templated_file,
            None,
            None,
        );
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

fn iter_base_types(
    token_type: &str,
    class_types: HashSet<String>,
) -> (String, HashSet<String>) {
    let mut class_types = class_types;
    let token_type = token_type.to_string();
    class_types.insert(token_type.clone());
    (token_type, class_types)
}
