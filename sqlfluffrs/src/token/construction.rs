use super::{config::TokenConfig, Token};
use crate::{marker::PositionMarker, slice::Slice, templater::templatefile::TemplatedFile};

use std::sync::Arc;

use hashbrown::HashSet;
use uuid::Uuid;

impl Token {
    pub fn base_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
        segments: Vec<Token>,
    ) -> Self {
        let TokenConfig {
            class_types,
            instance_types,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacement,
            casefold,
        } = config;

        let (token_types, class_types) = iter_base_types("base", class_types.clone());
        let raw_value = Token::normalize(&raw, quoted_value.clone(), escape_replacement.clone());
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
            parent: None,
            parent_idx: None,
            segments,
            preface_modifier: "".to_string(),
            suffix: "".to_string(),
            uuid: Uuid::new_v4().as_u128(),
            source_fixes: None,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacement,
            casefold,
            raw_value,
            matching_bracket_idx: None, // Will be computed after all tokens are created
        }
    }

    pub fn raw_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("raw", config.class_types.clone());
        let suffix = format!("'{}'", raw.escape_debug().to_string().trim_matches('"'));

        let mut token = Token::base_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
            vec![],
        );
        token.suffix = suffix;
        token.token_type = token_type;
        token
    }

    pub fn code_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        Self::raw_token(raw, pos_marker, config)
    }

    pub fn symbol_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("symbol", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn identifier_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("identifier", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn literal_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("literal", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn binary_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("binary_operator", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn comparison_operator_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("comparison_operator", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn word_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("word", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn unlexable_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("unlexable", config.class_types.clone());
        let mut token = Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token
    }

    pub fn whitespace_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("whitespace", config.class_types.clone());
        let mut token = Self::raw_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token.is_whitespace = true;
        token.is_code = false;
        token.is_comment = false;
        token._default_raw = " ".to_string();
        token
    }

    pub fn newline_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("newline", config.class_types.clone());
        let mut token = Self::raw_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token.is_whitespace = true;
        token.is_code = false;
        token.is_comment = false;
        token._default_raw = "\n".to_string();
        token
    }

    pub fn comment_token(
        raw: String,
        pos_marker: PositionMarker,
        config: TokenConfig,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("comment", config.class_types.clone());
        let mut token = Self::raw_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                ..config
            },
        );
        token.token_type = token_type;
        token.is_code = false;
        token.is_comment = true;
        token
    }

    pub fn meta_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
    ) -> Self {
        let (token_type, class_types) = iter_base_types("meta", class_types.clone());
        let mut token = Self::raw_token(
            "".to_string(),
            pos_marker,
            TokenConfig {
                class_types,
                instance_types: vec![],
                ..TokenConfig::default()
            },
        );
        token.token_type = token_type;
        token.is_code = false;
        token.is_meta = true;
        token.is_templated = is_templated;
        token.block_uuid = block_uuid;
        token.preface_modifier = "[META] ".to_string();
        token.suffix = String::new();
        token
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
            )
        }
    }

    pub fn indent_token(
        pos_marker: PositionMarker,
        is_templated: bool,
        block_uuid: Option<Uuid>,
        class_types: HashSet<String>,
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
            source_slice,
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

fn iter_base_types(token_type: &str, class_types: HashSet<String>) -> (String, HashSet<String>) {
    let mut class_types = class_types;
    let token_type = token_type.to_string();
    class_types.insert(token_type.clone());
    (token_type, class_types)
}
