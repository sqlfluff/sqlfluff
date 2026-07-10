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

/// One file's machine-readable (json/yaml) result. Collected across all
/// inputs and serialized as a single valid document by [`machine_output`] —
/// per-file documents concatenated into one stream would not parse.
pub enum MachineDoc {
    /// A `{filepath, segments}` mapping (Python's `parse` envelope entry).
    Parse(serde_yaml_ng::Value),
    /// A file's token records.
    Lex {
        filepath: String,
        tokens: serde_json::Value,
    },
}

/// Lex output: the human-readable token stream.
pub fn lex_human(tokens: &[Token]) -> String {
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
    out
}

/// Lex output: one file's token records for json/yaml.
pub fn lex_records(tokens: &[Token]) -> serde_json::Value {
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
    serde_json::Value::Array(records)
}

/// Parse output: the human-readable indented tree (not byte-identical to
/// Python's `stringify`).
pub fn parse_human(node: &Node, code_only: bool) -> String {
    let mut out = String::new();
    stringify_node(node, 0, code_only, &mut out);
    out
}

/// Parse output: one file's `{filepath, segments}` record via
/// `Node::as_record`, which mirrors Python's `BaseSegment.as_record` (the
/// format `sqlfluff parse` emits).
pub fn parse_record(
    node: &Node,
    fname: &str,
    code_only: bool,
    include_meta: bool,
) -> Result<serde_yaml_ng::Value> {
    let record = node
        .as_record(code_only, true, include_meta)
        .context("serializing parse tree")?;
    use serde_yaml_ng::Value;
    let mut mapping = serde_yaml_ng::Mapping::new();
    mapping.insert(Value::from("filepath"), Value::from(fname));
    mapping.insert(Value::from("segments"), record);
    Ok(Value::Mapping(mapping))
}

/// Serialize all collected per-file docs as one valid json/yaml document.
///
/// `parse` docs form a list of `{filepath, segments}` (Python's multi-file
/// envelope). `lex` keeps its bare token list for a single input and wraps
/// multiple inputs as a list of `{filepath, tokens}`.
pub fn machine_output(docs: Vec<MachineDoc>, format: OutputFormat) -> Result<Option<String>> {
    if !matches!(format, OutputFormat::Json | OutputFormat::Yaml) || docs.is_empty() {
        return Ok(None);
    }
    match &docs[0] {
        MachineDoc::Parse(_) => {
            let seq: Vec<serde_yaml_ng::Value> = docs
                .into_iter()
                .map(|d| match d {
                    MachineDoc::Parse(v) => v,
                    MachineDoc::Lex { .. } => unreachable!("one command per run"),
                })
                .collect();
            let doc = serde_yaml_ng::Value::Sequence(seq);
            match format {
                OutputFormat::Yaml => serde_yaml_ng::to_string(&doc)
                    .context("yaml serialization")
                    .map(Some),
                _ => serde_json::to_string(&doc)
                    .context("json serialization")
                    .map(Some),
            }
        }
        MachineDoc::Lex { .. } => {
            let single = docs.len() == 1;
            let value = if single {
                match docs.into_iter().next().unwrap() {
                    MachineDoc::Lex { tokens, .. } => tokens,
                    MachineDoc::Parse(_) => unreachable!("one command per run"),
                }
            } else {
                serde_json::Value::Array(
                    docs.into_iter()
                        .map(|d| match d {
                            MachineDoc::Lex { filepath, tokens } => {
                                json!({"filepath": filepath, "tokens": tokens})
                            }
                            MachineDoc::Parse(_) => unreachable!("one command per run"),
                        })
                        .collect(),
                )
            };
            match format {
                OutputFormat::Yaml => serde_yaml_ng::to_string(&value)
                    .context("yaml serialization")
                    .map(Some),
                _ => serde_json::to_string_pretty(&value)
                    .context("json serialization")
                    .map(Some),
            }
        }
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
