//! Per-file orchestration: template → lex → parse, reusing the existing Rust
//! lexer and parser crates.

use std::collections::BTreeMap;
use std::str::FromStr;
use std::sync::Arc;

use anyhow::{anyhow, Result};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::{Node, Parser};
use sqlfluffrs_types::{TemplatedFile, Token};

/// Resolve a dialect by name, erroring if `None` or unknown.
pub fn resolve_dialect_by_name(name: Option<&str>) -> Result<Dialect> {
    let name = name.ok_or_else(|| {
        anyhow!(
            "no dialect specified; set --dialect, a `dialect` config value, or an \
             inline `-- sqlfluff:dialect:...` directive"
        )
    })?;
    Dialect::from_str(name).map_err(|_| anyhow!("unknown dialect: {name}"))
}

/// Lex a single templated variant, returning tokens and formatted lex errors.
/// `template_blocks_indent` mirrors the `[sqlfluff:indentation]` flag of the
/// same name (default true).
pub fn lex_variant(
    variant: &Arc<TemplatedFile>,
    dialect: Dialect,
    template_blocks_indent: bool,
) -> (Vec<Token>, Vec<String>) {
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, violations) = lexer.lex(
        LexInput::TemplatedFile(variant.clone()),
        template_blocks_indent,
    );
    let errors = violations
        .iter()
        .map(|v| {
            format!(
                "L{}:{}: {}",
                v.line_no,
                v.line_pos,
                v.description
                    .clone()
                    .unwrap_or_else(|| "lex error".to_string())
            )
        })
        .collect();
    (tokens, errors)
}

/// Parse a token stream into the Rust `Node` tree.
/// Parser resource limits, mirroring the config values `RustParser` threads into
/// the Rust parser (`rust_parser_max_iterations`, `rust_parser_warn_threshold`,
/// `max_parse_depth`, `max_parse_nodes`). Defaults match `default_config.cfg`.
#[derive(Debug, Clone, Copy)]
pub struct ParseLimits {
    pub max_parser_iterations: usize,
    pub parser_warn_threshold: usize,
    pub max_parse_depth: usize,
    pub max_parse_nodes: usize,
}

impl Default for ParseLimits {
    fn default() -> Self {
        ParseLimits {
            max_parser_iterations: 3_000_000,
            parser_warn_threshold: 2_000_000,
            max_parse_depth: 600,
            max_parse_nodes: 100_000,
        }
    }
}

pub fn parse_tokens(
    tokens: &[Token],
    dialect: Dialect,
    indent_config: BTreeMap<String, bool>,
    limits: ParseLimits,
) -> Result<Node> {
    // The parser keeps `&'static str` keys; leak the owned strings (these live
    // for the duration of the process, matching the PyParser binding's approach).
    let indent: hashbrown::HashMap<&'static str, bool> = indent_config
        .into_iter()
        .map(|(k, v)| {
            let static_key: &'static str = Box::leak(k.into_boxed_str());
            (static_key, v)
        })
        .collect();

    // Thread the configured limits, exactly as the `PyParser` binding does.
    let mut parser =
        Parser::new_with_max_parse_depth(tokens, dialect, indent, limits.max_parse_depth)
            .with_parser_limits(limits.max_parser_iterations, limits.parser_warn_threshold)
            .with_node_limit(limits.max_parse_nodes);
    parser
        .root_parse()
        .map_err(|e| anyhow!("parse error: {e:?}"))
}
