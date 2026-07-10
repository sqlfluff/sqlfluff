//! Output formatting for the `render`, `lex`, and `parse` commands.

use std::sync::Arc;

use anyhow::{Context, Result};
use serde_json::json;
use sqlfluffrs_parser::parser::Node;
use sqlfluffrs_types::{TemplatedFile, Token};

use crate::cli::OutputFormat;

/// Render output: the templated string(s). Mirrors `sqlfluff render`, including
/// the multi-variant preamble.
pub fn render_output(variants: &[Arc<TemplatedFile>]) -> String {
    if variants.len() > 1 {
        let mut out = format!(
            "SQLFluff rendered {} variants of this file\n",
            variants.len()
        );
        for (idx, v) in variants.iter().enumerate() {
            out.push_str(&format!("Variant {}:\n", idx + 1));
            out.push_str(&v.templated_str);
            out.push('\n');
        }
        out
    } else if let Some(v) = variants.first() {
        v.templated_str.clone()
    } else {
        String::new()
    }
}

/// Lex output: the token stream.
pub fn lex_output(tokens: &[Token], format: OutputFormat) -> Result<String> {
    match format {
        OutputFormat::None => Ok(String::new()),
        OutputFormat::Human => {
            let mut out = String::new();
            for tok in tokens {
                let (line, pos) = tok
                    .pos_marker
                    .as_ref()
                    .map(|pm| (pm.line_no(), pm.line_pos()))
                    .unwrap_or((0, 0));
                out.push_str(&format!(
                    "[L{:>3}:{:<3}] {:<24} {:?}\n",
                    line,
                    pos,
                    tok.get_type(),
                    tok.raw()
                ));
            }
            Ok(out)
        }
        OutputFormat::Json | OutputFormat::Yaml => {
            let records: Vec<_> = tokens
                .iter()
                .map(|tok| {
                    let (line, pos) = tok
                        .pos_marker
                        .as_ref()
                        .map(|pm| (pm.line_no(), pm.line_pos()))
                        .unwrap_or((0, 0));
                    json!({
                        "type": tok.get_type(),
                        "raw": tok.raw(),
                        "line_no": line,
                        "line_pos": pos,
                    })
                })
                .collect();
            serialize(&records, format)
        }
    }
}

/// Parse output: the parse tree. For `json`/`yaml` this uses `Node::as_record`,
/// which mirrors Python's `BaseSegment.as_record` (the format `sqlfluff parse`
/// emits). The `human` form is a readable indented tree.
pub fn parse_output(
    node: &Node,
    fname: &str,
    format: OutputFormat,
    code_only: bool,
    include_meta: bool,
) -> Result<String> {
    match format {
        OutputFormat::None => Ok(String::new()),
        OutputFormat::Human => {
            let mut out = String::new();
            stringify_node(node, 0, code_only, &mut out);
            Ok(out)
        }
        OutputFormat::Json | OutputFormat::Yaml => {
            let record = node
                .as_record(code_only, true, include_meta)
                .context("serializing parse tree")?;
            // Match Python's `parse` envelope: a list of `{filepath, segments}`.
            use serde_yaml_ng::Value;
            let mut mapping = serde_yaml_ng::Mapping::new();
            mapping.insert(Value::from("filepath"), Value::from(fname));
            mapping.insert(Value::from("segments"), record);
            let doc = Value::Sequence(vec![Value::Mapping(mapping)]);
            match format {
                OutputFormat::Yaml => serde_yaml_ng::to_string(&doc).context("yaml serialization"),
                OutputFormat::Json => serde_json::to_string(&doc).context("json serialization"),
                _ => unreachable!(),
            }
        }
    }
}

fn serialize<T: serde::Serialize>(value: &T, format: OutputFormat) -> Result<String> {
    match format {
        OutputFormat::Yaml => serde_yaml_ng::to_string(value).context("yaml serialization"),
        OutputFormat::Json => serde_json::to_string_pretty(value).context("json serialization"),
        _ => Ok(String::new()),
    }
}

/// Render a `Node` as an indented tree (human-readable; not byte-identical to
/// Python's `stringify`). As in Python's `stringify`, `code_only` skips
/// non-code segments — whitespace, comments and metas — while `--include-meta`
/// only affects the record (json/yaml) forms.
fn stringify_node(node: &Node, depth: usize, code_only: bool, out: &mut String) {
    if code_only && !node.is_code() {
        return;
    }
    let indent = "  ".repeat(depth);
    match node {
        Node::Raw {
            segment_type, raw, ..
        } => {
            out.push_str(&format!("{indent}{segment_type}: {raw:?}\n"));
        }
        Node::Segment {
            segment_type,
            children,
            ..
        } => {
            let name = segment_type.clone().unwrap_or_else(|| "segment".into());
            out.push_str(&format!("{indent}[{name}]\n"));
            for child in children {
                stringify_node(child, depth + 1, code_only, out);
            }
        }
        Node::Meta { .. } => {
            out.push_str(&format!("{indent}{}\n", node.get_type()));
        }
        Node::Unparsable { children, .. } => {
            out.push_str(&format!("{indent}[unparsable]\n"));
            for child in children {
                stringify_node(child, depth + 1, code_only, out);
            }
        }
        Node::Empty => {}
    }
}
