/// Command-line utility to parse a fixture SQL file and output YAML
///
/// Usage: cargo run --example parse_fixture -- <path_to_sql_file> [--compare]
///
/// Examples:
///   cargo run --example parse_fixture -- test/fixtures/dialects/ansi/select_simple_a.sql
///   cargo run --example parse_fixture -- test/fixtures/dialects/ansi/select_simple_a.sql --compare
use sqlfluffrs::lexer::{LexInput, Lexer};
use sqlfluffrs::parser::Parser;
use sqlfluffrs::Dialect;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process;

fn main() {
    env_logger::init();

    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        log::debug!("Usage: {} <sql_file> [--compare]", args[0]);
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
        process::exit(1);
    }

    let sql_path = PathBuf::from(&args[1]);
    let compare_mode = args.len() > 2 && args[2] == "--compare";

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

    // Infer dialect from path (default to ANSI)
    let dialect = infer_dialect(&sql_path);
    println!("=== DIALECT: {:?} ===", dialect);
    println!();

    // Lex
    let input = LexInput::String(sql_content);
    let lexer = Lexer::new(None, dialect);
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

    parser.print_cache_stats();
    println!();

    // Print match tree
    println!("=== MATCH TREE ===");
    print_match_tree(&ast, &tokens, 0);
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
}

/// Infer dialect from file path
fn infer_dialect(path: &Path) -> Dialect {
    if let Some(parent) = path.parent() {
        if let Some(dialect_name) = parent.file_name().and_then(|s| s.to_str()) {
            return match dialect_name {
                "ansi" => Dialect::Ansi,
                // Add more dialects as needed
                _ => Dialect::Ansi,
            };
        }
    }
    Dialect::Ansi
}

/// Print the match tree in a format similar to Python SQLFluff
fn print_match_tree(
    node: &sqlfluffrs::parser::Node,
    tokens: &[sqlfluffrs::token::Token],
    depth: usize,
) {
    use sqlfluffrs::parser::Node;

    let indent = "  ".repeat(depth);
    let prefix = if depth == 0 { "" } else { "+" };

    match node {
        Node::Token(token_type, raw, pos) => {
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
        Node::Whitespace(raw, pos) => {
            println!(
                "{}{}<whitespace>: slice({}, {}, None)",
                indent,
                prefix,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::Newline(raw, pos) => {
            println!(
                "{}{}<newline>: slice({}, {}, None)",
                indent,
                prefix,
                pos,
                pos + 1
            );
            println!("{}  -raw: {:?}", indent, raw);
        }
        Node::EndOfFile(raw, pos) => {
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
                let (start, end) = get_node_slice(child, tokens);
                println!(
                    "{}{}Match <{}>: slice({}, {}, None)",
                    indent, prefix, seg_type, start, end
                );
            }
            print_match_tree(child, tokens, depth + 1);
        }
        Node::Sequence(children) | Node::DelimitedList(children) | Node::File(children) => {
            // Container nodes - print children
            for child in children {
                print_match_tree(child, tokens, depth);
            }
        }
        Node::Bracketed(children) => {
            let (start, end) = get_node_slice(node, tokens);
            println!(
                "{}{}Match <bracketed>: slice({}, {}, None)",
                indent, prefix, start, end
            );
            for child in children {
                print_match_tree(child, tokens, depth + 1);
            }
        }
        Node::Unparsable(_msg, children) => {
            let (start, end) = get_node_slice(node, tokens);
            println!(
                "{}{}Match <unparsable>: slice({}, {}, None)",
                indent, prefix, start, end
            );
            for child in children {
                print_match_tree(child, tokens, depth + 1);
            }
        }
        Node::Empty => {
            // Don't print empty nodes
        }
        Node::Meta(meta_type) => {
            println!("{}+Meta: {}", indent, meta_type);
        }
    }
}

/// Get the start and end position (token indices) for a node
fn get_node_slice(
    node: &sqlfluffrs::parser::Node,
    tokens: &[sqlfluffrs::token::Token],
) -> (usize, usize) {
    use sqlfluffrs::parser::Node;

    match node {
        Node::Token(_, _, pos)
        | Node::Whitespace(_, pos)
        | Node::Newline(_, pos)
        | Node::EndOfFile(_, pos) => (*pos, *pos + 1),
        Node::Ref { child, .. } => get_node_slice(child, tokens),
        Node::Sequence(children)
        | Node::DelimitedList(children)
        | Node::File(children)
        | Node::Bracketed(children)
        | Node::Unparsable(_, children) => {
            if children.is_empty() {
                (0, 0)
            } else {
                let first = get_node_slice(&children[0], tokens);
                let last = get_node_slice(&children[children.len() - 1], tokens);
                (first.0, last.1)
            }
        }
        Node::Empty | Node::Meta(_) => (0, 0),
    }
}

/// Convert a Node to YAML format matching Python SQLFluff output
fn node_to_yaml(
    node: &sqlfluffrs::parser::Node,
    tokens: &[sqlfluffrs::token::Token],
) -> Result<String, Box<dyn std::error::Error>> {
    use serde_yaml::{Mapping, Value};

    // Use code_only=true to match Python's behavior
    let yaml_value = node_to_yaml_value(node, tokens, true)?;

    // Add hash placeholder (would need to compute actual hash)
    let mut root_map = Mapping::new();
    root_map.insert(
        Value::String("_hash".to_string()),
        Value::String("PLACEHOLDER_HASH".to_string()),
    );

    // Special case: if node is Empty, represent as "file: null"
    if matches!(node, sqlfluffrs::parser::Node::Empty) {
        root_map.insert(
            Value::String("file".to_string()),
            Value::Null,
        );
    } else {
        // Merge the node's YAML into the root
        if let Value::Mapping(node_map) = yaml_value {
            for (k, v) in node_map {
                root_map.insert(k, v);
            }
        }
    }

    // Add header comments
    let header = "# YML test files are auto-generated from SQL files and should not be edited by\n\
                  # hand. To help enforce this, the \"hash\" field in the file must match a hash\n\
                  # computed by SQLFluff when running the tests. Please run\n\
                  # `python test/generate_parse_fixture_yml.py`  to generate them after adding or\n\
                  # altering SQL files.\n";

    let yaml_str = serde_yaml::to_string(&Value::Mapping(root_map))?;
    Ok(format!("{}{}", header, yaml_str))
}

/// Recursively convert a Node to a YAML Value
fn node_to_yaml_value(
    node: &sqlfluffrs::parser::Node,
    tokens: &[sqlfluffrs::token::Token],
    code_only: bool,
) -> Result<serde_yaml::Value, Box<dyn std::error::Error>> {
    use serde_yaml::{Mapping, Value};
    use sqlfluffrs::parser::Node;

    match node {
        Node::Token(token_type, raw, _pos) => {
            let mut map = Mapping::new();
            map.insert(
                Value::String(token_type.clone()),
                Value::String(raw.clone()),
            );
            Ok(Value::Mapping(map))
        }
        Node::Whitespace(_raw, _pos) | Node::Newline(_raw, _pos) | Node::EndOfFile(_raw, _pos) => {
            // These are filtered in code_only mode
            if code_only {
                Ok(Value::Sequence(vec![]))
            } else {
                let mut map = Mapping::new();
                match node {
                    Node::Whitespace(raw, _) => {
                        map.insert(
                            Value::String("whitespace".to_string()),
                            Value::String(raw.clone()),
                        );
                    }
                    Node::Newline(raw, _) => {
                        map.insert(
                            Value::String("newline".to_string()),
                            Value::String(raw.clone()),
                        );
                    }
                    Node::EndOfFile(raw, _) => {
                        map.insert(
                            Value::String("end_of_file".to_string()),
                            Value::String(raw.clone()),
                        );
                    }
                    _ => {}
                }
                Ok(Value::Mapping(map))
            }
        }
        Node::Ref {
            name: _,
            segment_type,
            child,
        } => {
            // Get child YAML first
            let child_yaml = node_to_yaml_value(child, tokens, code_only)?;

            // If we have a segment_type, wrap it
            if let Some(seg_type) = segment_type {
                if let Value::Sequence(items) = child_yaml {
                    let mut map = Mapping::new();
                    map.insert(Value::String(seg_type.clone()), Value::Sequence(items));
                    Ok(Value::Mapping(map))
                } else {
                    // Child is already a mapping or other value, wrap it in sequence
                    let mut map = Mapping::new();
                    map.insert(
                        Value::String(seg_type.clone()),
                        Value::Sequence(vec![child_yaml]),
                    );
                    Ok(Value::Mapping(map))
                }
            } else {
                // No segment type, just pass through
                Ok(child_yaml)
            }
        }
        Node::Sequence(children) | Node::DelimitedList(children) | Node::File(children) => {
            let mut items = Vec::new();
            for child in children {
                // Filter out non-code elements if code_only is true
                if code_only && !child.is_code() {
                    continue;
                }
                let child_yaml = node_to_yaml_value(child, tokens, code_only)?;
                // Skip empty sequences
                if matches!(child_yaml, Value::Sequence(ref v) if v.is_empty()) {
                    continue;
                }
                items.push(child_yaml);
            }
            Ok(Value::Sequence(items))
        }
        Node::Bracketed(children) => {
            // Bracketed node - create a mapping with "bracketed" key
            let mut items = Vec::new();
            for child in children {
                if code_only && !child.is_code() {
                    continue;
                }
                let child_yaml = node_to_yaml_value(child, tokens, code_only)?;
                // Skip empty sequences
                if matches!(child_yaml, Value::Sequence(ref v) if v.is_empty()) {
                    continue;
                }
                items.push(child_yaml);
            }

            let mut map = Mapping::new();
            map.insert(
                Value::String("bracketed".to_string()),
                Value::Sequence(items),
            );
            Ok(Value::Mapping(map))
        }
        Node::Unparsable(_msg, children) => {
            let mut items = Vec::new();
            for child in children {
                if code_only && !child.is_code() {
                    continue;
                }
                let child_yaml = node_to_yaml_value(child, tokens, code_only)?;
                items.push(child_yaml);
            }

            let mut map = Mapping::new();
            map.insert(
                Value::String("unparsable".to_string()),
                Value::Sequence(items),
            );
            Ok(Value::Mapping(map))
        }
        Node::Empty | Node::Meta(_) => {
            // Empty nodes and meta nodes are typically filtered out
            Ok(Value::Sequence(vec![]))
        }
    }
}
