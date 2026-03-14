// Wrapper functions that maintain the old TokenGenerator signature for backward compatibility
// These are used by the generated dialect matcher code

use super::{config::TokenConfig, CaseFold, Token};
use crate::{marker::PositionMarker, regex::RegexModeGroup};
use hashbrown::HashSet;

impl Token {
    // Wrapper functions that convert from the old 9-parameter signature to TokenConfig

    pub fn whitespace_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::whitespace_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn newline_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::newline_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn comment_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::comment_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn code_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::code_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn symbol_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::symbol_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn identifier_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::identifier_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn literal_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::literal_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn binary_operator_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::binary_operator_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn comparison_operator_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::comparison_operator_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn word_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::word_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }

    pub fn unlexable_token_compat(
        raw: String,
        pos_marker: PositionMarker,
        class_types: HashSet<String>,
        instance_types: Vec<String>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
        casefold: CaseFold,
    ) -> Self {
        Self::unlexable_token(
            raw,
            pos_marker,
            TokenConfig {
                class_types,
                instance_types,
                trim_start,
                trim_chars,
                quoted_value,
                escape_replacement,
                casefold,
            },
        )
    }
}
