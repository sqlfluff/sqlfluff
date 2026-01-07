use hashbrown::HashSet;
use serde_yaml_ng::{Mapping, Value};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
/// Test harness for parsing SQL fixtures and comparing with YAML expectations
///
/// This module provides functionality to:
/// 1. Parse SQL files from test/fixtures/dialects/
/// 2. Generate YAML output in the format used by SQLFluff
/// 3. Compare parsed results against expected YAML files
use sqlfluffrs_parser::parser::{Node, Parser};
use sqlfluffrs_types::Token;
use std::fs;
use std::path::{Path, PathBuf};
use std::str::FromStr;

/// Represents a test case from the fixtures directory
#[derive(Debug, Clone)]
pub struct FixtureTest {
    pub dialect: String,
    pub name: String,
    pub sql_path: PathBuf,
    pub yml_path: PathBuf,
}

/// Result of parsing and comparing a fixture test
#[derive(Debug)]
pub struct TestResult {
    pub test: FixtureTest,
    pub success: bool,
    pub error: Option<String>,
    pub generated_yaml: Option<String>,
    pub expected_yaml: Option<String>,
}

impl FixtureTest {
    /// Find all fixture tests in a given dialect directory
    pub fn discover(dialect: &str, fixtures_root: &Path) -> Vec<Self> {
        let dialect_dir = fixtures_root.join("dialects").join(dialect);
        if !dialect_dir.exists() {
            return Vec::new();
        }

        let mut tests = Vec::new();
        if let Ok(entries) = fs::read_dir(&dialect_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|s| s.to_str()) == Some("sql") {
                    let name = path.file_stem().unwrap().to_string_lossy().to_string();
                    let yml_path = path.with_extension("yml");

                    tests.push(FixtureTest {
                        dialect: dialect.to_string(),
                        name,
                        sql_path: path,
                        yml_path,
                    });
                }
            }
        }
        tests.sort_by(|a, b| a.name.cmp(&b.name));
        tests
    }

    /// Parse the SQL file and generate YAML output
    pub fn run(&self) -> TestResult {
        // Read SQL file
        let sql_content = match fs::read_to_string(&self.sql_path) {
            Ok(content) => content,
            Err(e) => {
                return TestResult {
                    test: self.clone(),
                    success: false,
                    error: Some(format!("Failed to read SQL file: {}", e)),
                    generated_yaml: None,
                    expected_yaml: None,
                }
            }
        };

        // Parse with Rust parser
        let dialect = Dialect::from_str(self.dialect.as_str()).expect("Invalid dialect");

        let input = LexInput::String(sql_content.clone());
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, lex_errors) = lexer.lex(input, false);

        if !lex_errors.is_empty() {
            return TestResult {
                test: self.clone(),
                success: false,
                error: Some(format!("Lexer errors: {:?}", lex_errors)),
                generated_yaml: None,
                expected_yaml: None,
            };
        }

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());

        // Try to parse as a file (top-level rule)
        // FileSegment always has segment_type "file"
        let ast = match parser.call_rule_as_root() {
            Ok(node) => node,
            Err(e) => {
                return TestResult {
                    test: self.clone(),
                    success: false,
                    error: Some(format!("Parse error: {:?}", e)),
                    generated_yaml: None,
                    expected_yaml: None,
                }
            }
        };

        // Convert AST to YAML
        let generated_yaml = match node_to_yaml(&ast, &tokens) {
            Ok(yaml) => yaml,
            Err(e) => {
                return TestResult {
                    test: self.clone(),
                    success: false,
                    error: Some(format!("YAML conversion error: {}", e)),
                    generated_yaml: None,
                    expected_yaml: None,
                }
            }
        };

        // Read expected YAML if it exists
        let expected_yaml = fs::read_to_string(&self.yml_path).ok();

        // Compare (simple string comparison for now)
        let success = if let Some(ref expected) = expected_yaml {
            compare_yaml(&generated_yaml, expected)
        } else {
            false
        };

        TestResult {
            test: self.clone(),
            success,
            error: None,
            generated_yaml: Some(generated_yaml),
            expected_yaml,
        }
    }
}

/// Convert a Node to YAML format matching Python SQLFluff output
fn node_to_yaml(node: &Node, tokens: &[Token]) -> Result<String, Box<dyn std::error::Error>> {
    // Use code_only=true to match Python's behavior
    let yaml_value = node_to_yaml_value(node, tokens, true)?;

    // Add hash placeholder (would need to compute actual hash)
    let mut root_map = Mapping::new();
    root_map.insert(
        Value::String("_hash".to_string()),
        Value::String("PLACEHOLDER_HASH".to_string()),
    );

    // Merge the node's YAML into the root
    if let Value::Mapping(node_map) = yaml_value {
        for (k, v) in node_map {
            root_map.insert(k, v);
        }
    }

    // Add header comments
    let header = "# YML test files are auto-generated from SQL files and should not be edited by\n\
                  # hand. To help enforce this, the \"hash\" field in the file must match a hash\n\
                  # computed by SQLFluff when running the tests. Please run\n\
                  # `python test/generate_parse_fixture_yml.py`  to generate them after adding or\n\
                  # altering SQL files.\n";

    let yaml_str = serde_yaml_ng::to_string(&Value::Mapping(root_map))?;
    Ok(format!("{}{}", header, yaml_str))
}

/// Recursively convert a Node to a YAML Value
///
/// # Arguments
/// * `node` - The node to convert
/// * `tokens` - Token array for looking up raw values
/// * `code_only` - If true, filter out whitespace and meta nodes (matches Python's behavior)
fn node_to_yaml_value(
    node: &Node,
    tokens: &[Token],
    code_only: bool,
) -> Result<Value, Box<dyn std::error::Error>> {
    // Filter out nodes that shouldn't be included in code_only mode
    if code_only && !node.should_include_in_code_only() {
        return Ok(Value::Null);
    }

    match node {
        Node::Empty => Ok(Value::Null),

        Node::Meta { .. } => Ok(Value::Null), // Meta nodes are not in YAML

        Node::Whitespace {
            raw: _,
            token_idx: _,
        }
        | Node::Newline {
            raw: _,
            token_idx: _,
        }
        | Node::Comment {
            raw: _,
            token_idx: _,
        }
        | Node::EndOfFile {
            raw: _,
            token_idx: _,
        } => {
            // Whitespace/newlines/EOF are filtered out in code_only mode
            // Comments are kept in code_only mode (handled in node.to_tuple_tree)
            Ok(Value::Null)
        }

        Node::Token {
            token_type,
            raw,
            token_idx: _,
        } => {
            // Filter whitespace tokens in code_only mode
            if code_only && matches!(token_type.as_str(), "whitespace" | "newline") {
                Ok(Value::Null)
            } else {
                // Create a mapping: { token_type: raw_value }
                // Use the token type directly without normalization
                let mut map = Mapping::new();
                map.insert(
                    Value::String(token_type.clone()),
                    Value::String(raw.clone()),
                );
                Ok(Value::Mapping(map))
            }
        }

        Node::Unparsable {
            expected_message: msg,
            children,
        } => {
            let mut map = Mapping::new();
            map.insert(
                Value::String("unparsable".to_string()),
                Value::String(msg.clone()),
            );

            if !children.is_empty() {
                let children_values: Vec<Value> = children
                    .iter()
                    .filter_map(|c| node_to_yaml_value(c, tokens, code_only).ok())
                    .filter(|v| !matches!(v, Value::Null))
                    .collect();

                if !children_values.is_empty() {
                    map.insert(
                        Value::String("children".to_string()),
                        Value::Sequence(children_values),
                    );
                }
            }

            Ok(Value::Mapping(map))
        }

        Node::Ref {
            name: _,
            segment_type,
            child,
        } => {
            // Check if this Ref should be transparent (not add a layer)

            // 1. Refs without segment_type are internal constructs - always transparent
            //    These include: Grammar rules, KeywordSegment/LiteralSegment wrappers,
            //    internal constructs with __ naming, base_/tail_/Expression_/Tail_ prefixes
            let is_internal_construct = segment_type.is_none();

            // 2. Refs with segment_type "expression" are wrappers - make transparent
            let is_wrapper_segment = segment_type.as_ref().map_or(false, |st| st == "expression");

            // If it's transparent, pass through to child without adding a layer
            if is_internal_construct || is_wrapper_segment {
                return node_to_yaml_value(child, tokens, code_only);
            }

            // Use segment_type directly (it's always present for non-transparent nodes)
            let key = segment_type.as_ref().unwrap().to_string();

            let child_value = node_to_yaml_value(child, tokens, code_only)?;

            // If child returned Null, this whole Ref should be filtered
            if matches!(child_value, Value::Null) {
                return Ok(Value::Null);
            }

            // Create a mapping with this segment's key
            let mut map = Mapping::new();
            map.insert(Value::String(key), child_value);
            Ok(Value::Mapping(map))
        }

        Node::Bracketed { children, .. } => {
            // Bracketed nodes are already properly structured, just convert to YAML
            let mut bracketed_children = Vec::new();

            for child in children {
                if !code_only || child.should_include_in_code_only() {
                    let child_value = node_to_yaml_value(child, tokens, code_only)?;
                    if !matches!(child_value, Value::Null) {
                        bracketed_children.push(child_value);
                    }
                }
            }

            if bracketed_children.is_empty() {
                return Ok(Value::Null);
            }

            let mut map = Mapping::new();
            map.insert(
                Value::String("bracketed".to_string()),
                Value::Sequence(bracketed_children),
            );
            Ok(Value::Mapping(map))
        }

        Node::Sequence { children } | Node::DelimitedList { children } => {
            // Collect all code-only children
            let filtered_children: Vec<&Node> = children
                .iter()
                .filter(|child| !code_only || child.should_include_in_code_only())
                .collect();

            if filtered_children.is_empty() {
                return Ok(Value::Null);
            }

            // Try to flatten the structure by collecting child mappings and non-mapping values
            let mut all_keys = Vec::new();
            let mut child_values = Vec::new();

            for child in &filtered_children {
                let child_value = node_to_yaml_value(child, tokens, code_only)?;

                // Skip Null values
                if matches!(child_value, Value::Null) {
                    continue;
                }

                if let Value::Mapping(ref child_map) = child_value {
                    // Track keys to detect duplicates
                    let keys: Vec<String> = child_map
                        .keys()
                        .filter_map(|k| {
                            if let Value::String(s) = k {
                                Some(s.clone())
                            } else {
                                None
                            }
                        })
                        .collect();

                    all_keys.extend(keys);
                }

                child_values.push(child_value);
            }

            if child_values.is_empty() {
                return Ok(Value::Null);
            }

            // Check for duplicate keys in mappings
            let unique_keys: HashSet<_> = all_keys.iter().collect();
            let has_duplicates = unique_keys.len() != all_keys.len();

            // If we have only mappings and no duplicates, try to merge them
            let all_are_mappings = child_values.iter().all(|v| matches!(v, Value::Mapping(_)));

            if all_are_mappings && !has_duplicates {
                // Merge all mappings into one
                let mut merged_map = Mapping::new();
                for child_value in child_values {
                    if let Value::Mapping(child_map) = child_value {
                        for (k, v) in child_map {
                            merged_map.insert(k, v);
                        }
                    }
                }
                Ok(Value::Mapping(merged_map))
            } else {
                // Return as a list (either because of duplicates or non-mapping values)
                Ok(Value::Sequence(child_values))
            }
        }
    }
}

/// Compare two YAML strings (ignoring hash and comments)
fn compare_yaml(generated: &str, expected: &str) -> bool {
    // Parse both as YAML
    let gen_yaml: Result<Value, _> = serde_yaml_ng::from_str(generated);
    let exp_yaml: Result<Value, _> = serde_yaml_ng::from_str(expected);

    match (gen_yaml, exp_yaml) {
        (Ok(gen), Ok(exp)) => {
            // Remove _hash fields for comparison by creating new mappings
            let gen_clean = if let Value::Mapping(gen_map) = gen {
                let mut clean = gen_map.clone();
                clean.remove(&Value::String("_hash".to_string()));
                Value::Mapping(clean)
            } else {
                gen
            };

            let exp_clean = if let Value::Mapping(exp_map) = exp {
                let mut clean = exp_map.clone();
                clean.remove(&Value::String("_hash".to_string()));
                Value::Mapping(clean)
            } else {
                exp
            };

            gen_clean == exp_clean
        }
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discover_ansi_fixtures() {
        let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .join("test/fixtures");

        let tests = FixtureTest::discover("ansi", &fixtures_root);
        println!("Found {} ANSI fixture tests", tests.len());

        // Should find multiple tests
        assert!(!tests.is_empty(), "No ANSI fixtures found");

        // Check that we found select_simple_a.sql
        let select_simple_a = tests.iter().find(|t| t.name == "create_table_a_c1_c2");
        assert!(
            select_simple_a.is_some(),
            "Expected to find create_table_a_c1_c2.sql"
        );
    }

    #[test]
    fn test_parse_simple_select() {
        let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .join("test/fixtures");

        let tests = FixtureTest::discover("ansi", &fixtures_root);
        let select_simple_a = tests
            .iter()
            .find(|t| t.name == "create_table_a_c1_c2")
            .expect("create_table_a_c1_c2.sql not found");

        let result = select_simple_a.run();

        if let Some(ref error) = result.error {
            println!("Error: {}", error);
        }

        if let Some(ref generated) = result.generated_yaml {
            println!("Generated YAML:\n{}", generated);
        }

        // This test might not pass yet, but it will show us what's generated
        println!("Test success: {}", result.success);
    }

    #[test]
    fn test_node_types() {
        use sqlfluffrs_dialects::Dialect;
        use sqlfluffrs_lexer::{LexInput, Lexer};

        let sql = "SELECT 1";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        let _ast = parser.call_rule_as_root().expect("Parse failed");

        // Print pruning statistics
        parser.print_cache_stats();
    }

    #[test]
    fn test_complex_query_cache() {
        use sqlfluffrs_dialects::Dialect;
        use sqlfluffrs_lexer::{LexInput, Lexer};

        // A more complex query to exercise the cache better
        let sql = "SELECT a, b, c FROM table1 WHERE a = 1 AND b = 2 ORDER BY c";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        let _ast = parser.call_rule_as_root().expect("Parse failed");

        // Print cache statistics for complex query
        println!("\n=== Complex Query Cache Stats ===");
        parser.print_cache_stats();
    }
}

#[cfg(test)]
mod whitespace_tests {
    use super::*;
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};
    use std::collections::HashSet;

    fn collect_token_positions(node: &Node, positions: &mut HashSet<usize>) {
        match node {
            Node::Token { token_idx, .. }
            | Node::Whitespace { token_idx, .. }
            | Node::Newline { token_idx, .. }
            | Node::Comment { token_idx, .. }
            | Node::EndOfFile { token_idx, .. } => {
                positions.insert(*token_idx);
            }
            Node::Ref { child, .. } => {
                collect_token_positions(child, positions);
            }
            Node::Sequence { children, .. }
            | Node::DelimitedList { children, .. }
            | Node::Bracketed { children, .. } => {
                for c in children {
                    collect_token_positions(c, positions);
                }
            }
            Node::Unparsable { children, .. } => {
                for c in children {
                    collect_token_positions(c, positions);
                }
            }
            Node::Meta { .. } | Node::Empty => {}
        }
    }

    #[test]
    fn test_select_from_alias() {
        let _ = env_logger::builder().is_test(true).try_init();

        let sql = "SELECT x FROM foo AS t";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\n=== TOKENS ===");
        for (idx, token) in tokens.iter().enumerate() {
            println!(
                "Token {}: {:?} (type: {})",
                idx,
                token.raw(),
                token.get_type()
            );
        }

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        let ast = parser.call_rule_as_root().expect("Parse failed");

        println!("\n=== AST STRUCTURE ===");
        println!("{:#?}", ast);

        let mut ast_positions = HashSet::new();
        collect_token_positions(&ast, &mut ast_positions);

        println!("\n=== AST POSITIONS ===");
        let mut sorted: Vec<_> = ast_positions.iter().copied().collect();
        sorted.sort();
        println!("{:?}", sorted);

        println!("\n=== MISSING POSITIONS ===");
        for (idx, token) in tokens.iter().enumerate() {
            if !ast_positions.contains(&idx) && token.get_type() != "end_of_file" {
                println!(
                    "Missing {}: {:?} (type: {})",
                    idx,
                    token.raw(),
                    token.get_type()
                );
            }
        }

        // Reconstruct raw text from tokens in AST
        let mut raw_parts: Vec<(usize, String)> = vec![];
        for idx in &sorted {
            raw_parts.push((*idx, tokens[*idx].raw().to_string()));
        }
        raw_parts.sort_by_key(|(idx, _)| *idx);
        let raw_text: String = raw_parts.iter().map(|(_, s)| s.as_str()).collect();

        println!("\nReconstructed: {:?}", raw_text);
        println!("Original: {:?}", sql);

        assert_eq!(raw_text, sql, "Whitespace mismatch in reconstructed SQL");
    }

    #[test]
    fn test_select_function_alias() {
        let _ = env_logger::builder().is_test(true).try_init();

        let sql = "SELECT a (x) AS y";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).clone());
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\n=== TOKENS ===");
        for (idx, token) in tokens.iter().enumerate() {
            println!(
                "Token {}: {:?} (type: {})",
                idx,
                token.raw(),
                token.get_type()
            );
        }

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        let ast = parser.call_rule_as_root().expect("Parse failed");

        let mut ast_positions = HashSet::new();
        collect_token_positions(&ast, &mut ast_positions);

        println!("\n=== AST POSITIONS ===");
        let mut sorted: Vec<_> = ast_positions.iter().copied().collect();
        sorted.sort();
        println!("{:?}", sorted);

        println!("\n=== MISSING POSITIONS ===");
        for (idx, token) in tokens.iter().enumerate() {
            if !ast_positions.contains(&idx) && token.get_type() != "end_of_file" {
                println!(
                    "Missing {}: {:?} (type: {})",
                    idx,
                    token.raw(),
                    token.get_type()
                );
            }
        }

        // Reconstruct raw text from tokens in AST
        let mut raw_parts: Vec<(usize, String)> = vec![];
        for idx in &sorted {
            raw_parts.push((*idx, tokens[*idx].raw().to_string()));
        }
        raw_parts.sort_by_key(|(idx, _)| *idx);
        let raw_text: String = raw_parts.iter().map(|(_, s)| s.as_str()).collect();

        println!("\nReconstructed: {:?}", raw_text);
        println!("Original: {:?}", sql);

        assert_eq!(raw_text, sql, "Whitespace mismatch in reconstructed SQL");
    }
}
