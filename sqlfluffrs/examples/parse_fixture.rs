use sqlfluffrs_dialects::Dialect;
/// Command-line utility to parse a fixture SQL file and output YAML
///
/// Usage: cargo run --example parse_fixture -- <path_to_sql_file> [--compare]
///
/// Examples:
///   cargo run --example parse_fixture -- test/fixtures/dialects/ansi/select_simple_a.sql
///   cargo run --example parse_fixture -- test/fixtures/dialects/ansi/select_simple_a.sql --compare
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process;
use std::str::FromStr;

use blake2::{Blake2s256, Digest};
use serde_yaml_ng::Value;

fn main() {
    env_logger::init();

    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        log::debug!("Usage: {} <sql_file> [--compare] [--dialect <dialect>] [--out <file>] [--code-only]", args[0]);
        log::debug!("");
        log::debug!("Examples:");
        log::debug!(
            "  {} test/fixtures/dialects/ansi/select_simple_a.sql",
            args[0]
        );
        log::debug!(
            "  {} test/fixtures/dialects/ansi/create_table.sql --compare",
            args[0]
        );
        log::debug!(
            "  {} test.sql --dialect bigquery",
            args[0]
        );
        process::exit(1);
    }

    let sql_path = PathBuf::from(&args[1]);
    let mut compare_mode = false;
    let mut out_path: Option<PathBuf> = None;
    let mut code_only = false;
    let mut dialect_override: Option<String> = None;
    let mut i = 2;
    while i < args.len() {
        match args[i].as_str() {
            "--compare" => compare_mode = true,
            "--dialect" => {
                if i + 1 < args.len() {
                    dialect_override = Some(args[i + 1].clone());
                    i += 1;
                } else {
                    eprintln!("Missing dialect name after --dialect");
                    process::exit(1);
                }
            }
            "--out" => {
                if i + 1 < args.len() {
                    out_path = Some(PathBuf::from(&args[i + 1]));
                    i += 1;
                } else {
                    eprintln!("Missing filename after --out");
                    process::exit(1);
                }
            }
            "--code-only" => code_only = true,
            _ => {}
        }
        i += 1;
    }

    if !sql_path.exists() {
        log::debug!("Error: File not found: {}", sql_path.display());
        process::exit(1);
    }

    // Read SQL content
    let sql_content = match fs::read_to_string(&sql_path) {
        Ok(content) => content,
        Err(e) => {
            log::debug!("Error reading SQL file: {}", e);
            process::exit(1);
        }
    };

    println!("=== SQL FILE: {} ===", sql_path.display());
    println!("{}", sql_content);
    println!();

    // Determine dialect: use override if provided, otherwise infer from path
    let dialect = if let Some(ref dialect_name) = dialect_override {
        match Dialect::from_str(dialect_name) {
            Ok(d) => d,
            Err(_) => {
                eprintln!("Error: Invalid dialect '{}'. Using ANSI instead.", dialect_name);
                Dialect::Ansi
            }
        }
    } else {
        infer_dialect(&sql_path)
    };
    println!("=== DIALECT: {:?} ===", dialect);
    println!();

    // Lex
    let input = LexInput::String(sql_content);
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    if !lex_errors.is_empty() {
        log::debug!("=== LEXER ERRORS ===");
        for error in lex_errors {
            log::debug!("  {:?}", error);
        }
        process::exit(1);
    }

    println!("=== TOKENS ({} total) ===", tokens.len());
    for (idx, token) in tokens.iter().enumerate() {
        println!("  [{}] {:?} (type: {})", idx, token.raw(), token.get_type());
    }
    println!();

    // Parse
    let mut parser = Parser::new(&tokens, dialect);
    parser.set_cache_enabled(true);
    let ast = match parser.call_rule_as_root() {
        Ok(node) => node,
        Err(e) => {
            eprintln!("=== PARSE ERROR ===");
            eprintln!("{:?}", e);
            process::exit(1);
        }
    };

    println!("DEBUG: AST node type: {:?}", ast);
    println!("=== PARSE SUCCESS ===");
    println!();

    // Print match tree (optional, can be removed if not needed)
    println!("=== MATCH TREE ===");
    print_match_tree(&ast, 0);
    println!();

    println!("=== AS RECORD ===");
    println!("{:?}", ast.as_record(true, true, false));
    println!();

    // Generate YAML
    let generated_yaml = match node_to_yaml(&ast, &tokens) {
        Ok(yaml) => yaml,
        Err(e) => {
            log::debug!("=== YAML CONVERSION ERROR ===");
            log::debug!("{}", e);
            process::exit(1);
        }
    };

    println!("=== GENERATED YAML ===");
    println!("{}", generated_yaml);

    // Compare mode
    if compare_mode {
        let yml_path = sql_path.with_extension("yml");

        if !yml_path.exists() {
            log::debug!("");
            log::debug!("=== COMPARE MODE: Expected YAML not found ===");
            log::debug!("Expected file: {}", yml_path.display());
            process::exit(1);
        }

        let expected_yaml = match fs::read_to_string(&yml_path) {
            Ok(content) => content,
            Err(e) => {
                log::debug!("Error reading expected YAML: {}", e);
                process::exit(1);
            }
        };

        println!();
        println!("=== EXPECTED YAML ===");
        println!("{}", expected_yaml);
        println!();

        // Simple comparison
        if generated_yaml.trim() == expected_yaml.trim() {
            println!("=== COMPARISON: MATCH ✓ ===");
            process::exit(0);
        } else {
            println!("=== COMPARISON: MISMATCH ✗ ===");

            // Show differences
            let gen_lines: Vec<&str> = generated_yaml.lines().collect();
            let exp_lines: Vec<&str> = expected_yaml.lines().collect();

            println!();
            println!("Differences:");
            for (i, (gen_line, exp_line)) in gen_lines.iter().zip(exp_lines.iter()).enumerate() {
                if gen_line != exp_line {
                    println!("  Line {}: ", i + 1);
                    println!("    Generated: {}", gen_line);
                    println!("    Expected:  {}", exp_line);
                }
            }

            if gen_lines.len() != exp_lines.len() {
                println!();
                println!("  Line count differs:");
                println!("    Generated: {} lines", gen_lines.len());
                println!("    Expected:  {} lines", exp_lines.len());
            }

            process::exit(1);
        }
    }

    parser.print_cache_stats();
    println!();
}

/// Infer dialect from file path
fn infer_dialect(path: &Path) -> Dialect {
    if let Some(parent) = path.parent() {
        if let Some(dialect_name) = parent.file_name().and_then(|s| s.to_str()) {
            return Dialect::from_str(dialect_name).unwrap_or(Dialect::Ansi);
        }
    }
    Dialect::Ansi
}

/// Print the match tree in a format similar to Python SQLFluff
fn print_match_tree(node: &sqlfluffrs_parser::parser::Node, depth: usize) {
    use sqlfluffrs_parser::parser::Node;

    let indent = "  ".repeat(depth);
    let prefix = if depth == 0 { "" } else { "+" };

    match node {
        Node::Token {
            token_type,
            raw,
            token_idx: pos,
        } => {
            // Leaf token - show type and raw value
            println!(
                "{}{}Match <{}>: slice({}, {}, None)",
                indent,
                prefix,
                token_type,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::Whitespace {
            raw,
            token_idx: pos,
        } => {
            println!(
                "{}{}<whitespace>: slice({}, {}, None)",
                indent,
                prefix,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::Newline {
            raw,
            token_idx: pos,
        } => {
            println!(
                "{}{}<newline>: slice({}, {}, None)",
                indent,
                prefix,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::EndOfFile {
            raw,
            token_idx: pos,
        } => {
            println!(
                "{}{}<end_of_file>: slice({}, {}, None)",
                indent,
                prefix,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::Ref {
            name: _,
            segment_type,
            child,
        } => {
            // Ref node - show segment type if present
            if let Some(seg_type) = segment_type {
                let (start, end) = get_node_slice(child);
                println!(
                    "{}{}Match <{}>: slice({}, {}, None)",
                    indent, prefix, seg_type, start, end
                );
            }
            print_match_tree(child, depth + 1);
        }
        Node::Sequence { children } | Node::DelimitedList { children } => {
            // Container nodes - print children
            for child in children {
                print_match_tree(child, depth);
            }
        }
        Node::Bracketed { children } => {
            let (start, end) = get_node_slice(node);
            println!(
                "{}{}Match <bracketed>: slice({}, {}, None)",
                indent, prefix, start, end
            );
            for child in children {
                print_match_tree(child, depth + 1);
            }
        }
        Node::Unparsable {
            expected_message: _msg,
            children,
        } => {
            let (start, end) = get_node_slice(node);
            println!(
                "{}{}Match <unparsable>: slice({}, {}, None)",
                indent, prefix, start, end
            );
            for child in children {
                print_match_tree(child, depth + 1);
            }
        }
        Node::Empty => {
            // Don't print empty nodes
        }
        Node::Meta {
            token_type: meta_type,
            ..
        } => {
            println!("{}+Meta: {}", indent, meta_type);
        }
    }
}

/// Get the start and end position (token indices) for a node
fn get_node_slice(node: &sqlfluffrs_parser::parser::Node) -> (usize, usize) {
    use sqlfluffrs_parser::parser::Node;

    match node {
        Node::Token {
            token_type: _,
            raw: _,
            token_idx: pos,
        }
        | Node::Whitespace {
            raw: _,
            token_idx: pos,
        }
        | Node::Newline {
            raw: _,
            token_idx: pos,
        }
        | Node::EndOfFile {
            raw: _,
            token_idx: pos,
        } => (*pos, *pos + 1),
        Node::Ref { child, .. } => get_node_slice(child),
        Node::Sequence { children }
        | Node::DelimitedList { children }
        | Node::Bracketed { children }
        | Node::Unparsable {
            expected_message: _,
            children,
        } => {
            if children.is_empty() {
                (0, 0)
            } else {
                let first = get_node_slice(&children[0]);
                let last = get_node_slice(&children[children.len() - 1]);
                (first.0, last.1)
            }
        }
        Node::Empty | Node::Meta { .. } => (0, 0),
    }
}

/// Convert a Node to YAML format matching Python SQLFluff output
fn node_to_yaml(
    node: &sqlfluffrs_parser::parser::Node,
    tokens: &[sqlfluffrs_types::token::Token],
) -> Result<String, Box<dyn std::error::Error>> {
    use serde_yaml_ng::{Mapping, Value};

    // Use code_only=true to match Python's behavior
    let mut root_map = Mapping::new();
    let as_record = node.as_record(true, true, false);
    // Add hash placeholder
    root_map.insert(
        Value::String("_hash".to_string()),
        Value::String("PLACEHOLDER_HASH".to_string()),
    );

    if let Some(Value::Mapping(m)) = as_record {
        for (k, v) in m {
            root_map.insert(k, v);
        }
    } else {
        root_map.insert(
            Value::String("node".to_string()),
            as_record.expect("Node as_record should not be None"),
        );
    }

    // Add header comments
    let header = "# YML test files are auto-generated from SQL files and should not be edited by\n\
                  # hand. To help enforce this, the \"hash\" field in the file must match a hash\n\
                  # computed by SQLFluff when running the tests. Please run\n\
                  # `python test/generate_parse_fixture_yml.py`  to generate them after adding or\n\
                  # altering SQL files.\n";

    let mut yaml_val = Value::Mapping(root_map);
    insert_yaml_hash(&mut yaml_val);
    let yaml_str = serde_yaml_ng::to_string(&yaml_val)?;
    let quoted = process_yaml_11(yaml_str);
    Ok(format!("{}{}", header, quoted))
}

fn process_yaml_11(yaml_str: String) -> String {
    // Post-process: quote values in the given list in single quotes to match pyyaml safe_dump
    let unquoted_keywords = ["NO", "YES", "ON", "OFF", "NULL", "TRUE", "FALSE", "="];
    let quoted = yaml_str
        .lines()
        .map(|line| {
            if let Some((k, v)) = line.split_once(": ") {
                // Convert triple single quoted strings to single quoted
                let v = if v.starts_with("'''") && v.ends_with("'''") && v.len() > 6 {
                    let inner = &v[3..v.len() - 3];
                    format!("'{}'", inner.replace("'", "''"))
                } else {
                    v.to_string()
                };
                // Only quote if value is in the list and not already quoted
                if unquoted_keywords.contains(&v.to_uppercase().as_str())
                    && !v.starts_with('"')
                    && !v.starts_with('\'')
                {
                    format!("{}: '{}'", k, v)
                } else {
                    format!("{}: {}", k, v)
                }
            } else {
                line.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join("\n");
    format!("{}\n", quoted)
}

// /// Recursively convert a Node to a YAML Value
// pub fn node_to_yaml_value(
//     node: &sqlfluffrs_parser::parser::Node,
//     code_only: bool,
// ) -> Result<serde_yaml_ng::Value, Box<dyn std::error::Error>> {
//     use serde_yaml_ng::{Mapping, Value};
//     use sqlfluffrs_parser::parser::Node;

//     match node {
//         Node::Token {
//             token_type,
//             raw,
//             token_idx: _pos,
//         } => {
//             let mut map = Mapping::new();
//             map.insert(
//                 Value::String(token_type.clone()),
//                 Value::String(raw.clone()),
//             );
//             Ok(Value::Mapping(map))
//         }
//         Node::Whitespace {
//             raw: _raw,
//             token_idx: _pos,
//         }
//         | Node::Newline {
//             raw: _raw,
//             token_idx: _pos,
//         }
//         | Node::EndOfFile {
//             raw: _raw,
//             token_idx: _pos,
//         } => {
//             // These are filtered in code_only mode
//             if code_only {
//                 Ok(Value::Sequence(vec![]))
//             } else {
//                 let mut map = Mapping::new();
//                 match node {
//                     Node::Whitespace { raw, token_idx: _ } => {
//                         map.insert(
//                             Value::String("whitespace".to_string()),
//                             Value::String(raw.clone()),
//                         );
//                     }
//                     Node::Newline { raw, token_idx: _ } => {
//                         map.insert(
//                             Value::String("newline".to_string()),
//                             Value::String(raw.clone()),
//                         );
//                     }
//                     Node::EndOfFile { raw, token_idx: _ } => {
//                         map.insert(
//                             Value::String("end_of_file".to_string()),
//                             Value::String(raw.clone()),
//                         );
//                     }
//                     _ => {}
//                 }
//                 Ok(Value::Mapping(map))
//             }
//         }
//         Node::Ref {
//             name: _,
//             segment_type,
//             child,
//         } => {
//             // Get child YAML first
//             let child_yaml = node_to_yaml_value(child, code_only)?;

//             // If we have a segment_type, wrap it
//             if let Some(seg_type) = segment_type {
//                 if let Value::Sequence(items) = child_yaml {
//                     let mut map = Mapping::new();
//                     map.insert(Value::String(seg_type.clone()), Value::Sequence(items));
//                     Ok(Value::Mapping(map))
//                 } else {
//                     // Child is already a mapping or other value, wrap it in sequence
//                     let mut map = Mapping::new();
//                     map.insert(
//                         Value::String(seg_type.clone()),
//                         Value::Sequence(vec![child_yaml]),
//                     );
//                     Ok(Value::Mapping(map))
//                 }
//             } else {
//                 // No segment type, just pass through
//                 Ok(child_yaml)
//             }
//         }
//         Node::Sequence { children } | Node::DelimitedList { children } => {
//             let mut items = Vec::new();
//             for child in children {
//                 // Filter out non-code elements if code_only is true
//                 if code_only && !child.is_code() {
//                     continue;
//                 }
//                 let child_yaml = node_to_yaml_value(child, code_only)?;
//                 // Skip empty sequences
//                 if matches!(child_yaml, Value::Sequence(ref v) if v.is_empty()) {
//                     continue;
//                 }
//                 items.push(child_yaml);
//             }
//             Ok(Value::Sequence(items))
//         }
//         Node::Bracketed { children } => {
//             // Bracketed node - create a mapping with "bracketed" key
//             let mut items = Vec::new();
//             for child in children {
//                 if code_only && !child.is_code() {
//                     continue;
//                 }
//                 let child_yaml = node_to_yaml_value(child, code_only)?;
//                 // Skip empty sequences
//                 if matches!(child_yaml, Value::Sequence(ref v) if v.is_empty()) {
//                     continue;
//                 }
//                 items.push(child_yaml);
//             }

//             let mut map = Mapping::new();
//             map.insert(
//                 Value::String("bracketed".to_string()),
//                 Value::Sequence(items),
//             );
//             Ok(Value::Mapping(map))
//         }
//         Node::Unparsable {
//             expected_message: _msg,
//             children,
//         } => {
//             let mut items = Vec::new();
//             for child in children {
//                 if code_only && !child.is_code() {
//                     continue;
//                 }
//                 let child_yaml = node_to_yaml_value(child, code_only)?;
//                 items.push(child_yaml);
//             }

//             let mut map = Mapping::new();
//             map.insert(
//                 Value::String("unparsable".to_string()),
//                 Value::Sequence(items),
//             );
//             Ok(Value::Mapping(map))
//         }
//         Node::Empty | Node::Meta { .. } => {
//             // Empty nodes and meta nodes are typically filtered out
//             Ok(Value::Sequence(vec![]))
//         }
//     }
// }

/// Compute a hash for a serde_yaml_ng::Value, excluding the _hash field.
/// Returns a lowercase hex string (SHA256).
pub fn compute_yaml_hash(yaml: &Value) -> String {
    // Remove _hash field if present
    let clean = match yaml {
        Value::Mapping(map) => {
            let mut m = map.clone();
            m.remove(Value::String("_hash".to_string()));
            Value::Mapping(m)
        }
        _ => yaml.clone(),
    };
    // Dump to canonical YAML string (no comments)
    let yaml_str = process_yaml_11(serde_yaml_ng::to_string(&clean).unwrap());
    // Compute SHA256 hash
    let mut hasher = blake2::Blake2s256::new();
    hasher.update(yaml_str.as_bytes());
    format!("{:x}", hasher.finalize())
}

/// Insert the hash into the _hash field of a YAML mapping
pub fn insert_yaml_hash(yaml: &mut Value) {
    let hash = compute_yaml_hash(yaml);
    if let Value::Mapping(map) = yaml {
        map.insert(Value::String("_hash".to_string()), Value::String(hash));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_yaml_ng::Value;
    use std::collections::BTreeMap;

    #[test]
    fn test_hash_insertion() {
        let mut map = serde_yaml_ng::Mapping::new();
        map.insert(
            Value::String("foo".to_string()),
            Value::String("bar".to_string()),
        );
        let mut yaml = Value::Mapping(map);
        insert_yaml_hash(&mut yaml);
        if let Value::Mapping(m) = &yaml {
            assert!(m.contains_key(&Value::String("_hash".to_string())));
        }
    }
}
