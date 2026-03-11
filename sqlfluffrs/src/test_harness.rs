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
        let mr_ast = match parser.call_rule_as_root() {
            Ok(match_result) => match_result,
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

        println!("=== Parsed AST for {} ===", self.name);
        println!("{}", mr_ast.stringify(0));

        // Use apply_as_root so the AST is wrapped in a file-level node, matching
        // the expected YAML which has `file:` at the top level.
        let ast = mr_ast.apply_as_root(&tokens, &[], &[]);

        // Convert AST to YAML using as_record, the canonical serialization path
        // that mirrors Python's BaseSegment.as_record().
        let generated_yaml = match node_to_yaml_via_as_record(&ast) {
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

/// Convert a Node to YAML using the canonical `as_record` serialization path,
/// which mirrors Python's `BaseSegment.as_record()`.  Used by `FixtureTest::run`.
fn node_to_yaml_via_as_record(node: &Node) -> Result<String, Box<dyn std::error::Error>> {
    let mut root_map = Mapping::new();
    root_map.insert(
        Value::String("_hash".to_string()),
        Value::String("PLACEHOLDER_HASH".to_string()),
    );

    let as_record = node.as_record(true, true, false);
    if let Some(serde_yaml_ng::Value::Mapping(m)) = as_record {
        for (k, v) in m {
            root_map.insert(k, v);
        }
    } else if let Some(v) = as_record {
        root_map.insert(Value::String("node".to_string()), v);
    }

    let header = "# YML test files are auto-generated from SQL files and should not be edited by\n\
                  # hand. To help enforce this, the \"hash\" field in the file must match a hash\n\
                  # computed by SQLFluff when running the tests. Please run\n\
                  # `python test/generate_parse_fixture_yml.py`  to generate them after adding or\n\
                  # altering SQL files.\n";

    let yaml_str = serde_yaml_ng::to_string(&Value::Mapping(root_map))?;
    Ok(format!("{}{}", header, yaml_str))
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
                clean.remove(Value::String("_hash".to_string()));
                Value::Mapping(clean)
            } else {
                gen
            };

            let exp_clean = if let Value::Mapping(exp_map) = exp {
                let mut clean = exp_map.clone();
                clean.remove(Value::String("_hash".to_string()));
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
        let mr = parser.call_rule_as_root().expect("Parse failed");
        let ast = mr.apply_as_root(&tokens, &[], &[]);

        println!("\n=== AST STRUCTURE ===");
        println!("{:#?}", ast);

        let raw_text = ast.raw();
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
        let mr = parser.call_rule_as_root().expect("Parse failed");
        let ast = mr.apply_as_root(&tokens, &[], &[]);

        println!("\n=== AST STRUCTURE ===");
        println!("{:#?}", ast);

        let raw_text = ast.raw();
        println!("\nReconstructed: {:?}", raw_text);
        println!("Original: {:?}", sql);

        assert_eq!(raw_text, sql, "Whitespace mismatch in reconstructed SQL");
    }
}
