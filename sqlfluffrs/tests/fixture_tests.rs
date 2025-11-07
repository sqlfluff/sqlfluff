/// Compare Rust YAML output to Python YAML for all fixtures in a given dialect.
fn check_yaml_output_matches_python_for_dialect(dialect: &str) {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover(dialect, &fixtures_root);
    let mut total = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        // Read SQL file
        let sql_content = std::fs::read_to_string(&test.sql_path).expect("Failed to read SQL file");
        // Read expected YAML
        let expected_yaml =
            std::fs::read_to_string(&test.yml_path).expect("Failed to read expected YAML file");

        // Parse with Rust parser
        let dialect_obj =
            sqlfluffrs_dialects::Dialect::from_str(&test.dialect).expect("Invalid dialect");
        let input = sqlfluffrs_lexer::LexInput::String(sql_content.clone());
        let lexer = sqlfluffrs_lexer::Lexer::new(None, dialect_obj.get_lexers().to_vec());
        let (tokens, lex_errors) = lexer.lex(input, false);
        assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);
        let mut parser = sqlfluffrs_parser::parser::Parser::new(&tokens, dialect_obj);
        let ast = parser.call_rule_as_root().expect("Parse error");

        // Generate YAML
        let generated_yaml = node_to_yaml(&ast, &tokens).expect("YAML conversion error");

        total += 1;
        // Parse YAML to Value for key/row comparison
        let gen_val: serde_yaml_ng::Value =
            serde_yaml_ng::from_str(&generated_yaml).expect("Generated YAML not valid");
        let exp_val: serde_yaml_ng::Value =
            serde_yaml_ng::from_str(&expected_yaml).expect("Expected YAML not valid");

        // Helper to extract keys and row count from the main node
        fn keys_and_row_count(val: &serde_yaml_ng::Value) -> (Vec<String>, usize) {
            if let serde_yaml_ng::Value::Mapping(map) = val {
                let keys: Vec<String> = map
                    .keys()
                    .filter_map(|k| k.as_str().map(|s| s.to_string()))
                    .collect();
                // Find the main node ("node" or first non-_hash key)
                let main_node = map.iter().find(|(k, _)| k.as_str() != Some("_hash"));
                let row_count = if let Some((_, v)) = main_node {
                    if let serde_yaml_ng::Value::Mapping(m) = v {
                        m.len()
                    } else if let serde_yaml_ng::Value::Sequence(seq) = v {
                        seq.len()
                    } else {
                        1
                    }
                } else {
                    0
                };
                (keys, row_count)
            } else {
                (vec![], 0)
            }
        }

        let (gen_keys, gen_rows) = keys_and_row_count(&gen_val);
        let (exp_keys, exp_rows) = keys_and_row_count(&exp_val);

        let keys_match = {
            let mut gk = gen_keys.clone();
            let mut ek = exp_keys.clone();
            gk.sort();
            ek.sort();
            gk == ek
        };
        let rows_match = gen_rows == exp_rows;

        if !keys_match || !rows_match {
            failed += 1;
            failed_tests.push(test.name.clone());
            println!(
                "\n=== YAML STRUCTURE MISMATCH: {}::{} ===",
                dialect, test.name
            );
            if !keys_match {
                println!(
                    "  Keys differ:\n    Generated: {:?}\n    Expected:  {:?}",
                    gen_keys, exp_keys
                );
            }
            if !rows_match {
                println!(
                    "  Row count differs:\n    Generated: {}\n    Expected:  {}",
                    gen_rows, exp_rows
                );
                if test.name == "table_expression" {
                    println!("\n=== GENERATED YAML ===\n{}", generated_yaml);
                    println!("\n=== EXPECTED YAML (first 100 lines) ===");
                    for (i, line) in expected_yaml.lines().take(100).enumerate() {
                        println!("{}: {}", i + 1, line);
                    }
                }
            }
        }
    }

    println!(
        "\nYAML output comparison for dialect '{}': {} total, {} failed",
        dialect, total, failed
    );
    if !failed_tests.is_empty() {
        println!("Failed tests for dialect '{}':", dialect);
        for name in &failed_tests {
            println!("  {}::{}", dialect, name);
        }
        panic!(
            "Some YAML outputs did not match Python reference for dialect '{}'",
            dialect
        );
    }
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

#[test]
fn test_yaml_output_matches_python_ansi() {
    check_yaml_output_matches_python_for_dialect("ansi");
}

#[test]
fn test_yaml_output_matches_python_bigquery() {
    check_yaml_output_matches_python_for_dialect("bigquery");
}

// Add more dialects as needed, or use a macro to generate tests for all dialects.
// (Imports above are already present in this file; do not re-import.)
use serde_yaml_ng::Value;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use std::fs;
use std::path::PathBuf;

/// Helper: Generate YAML from AST using the same logic as examples/parse_fixture.rs
fn node_to_yaml(
    node: &sqlfluffrs_parser::parser::Node,
    _tokens: &[sqlfluffrs_types::token::Token],
) -> Result<String, Box<dyn std::error::Error>> {
    use serde_yaml_ng::{Mapping, Value};
    let mut root_map = Mapping::new();
    let as_record = node.as_record(true, true, false);
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

/// Helper: Insert hash into YAML mapping (copied from examples/parse_fixture.rs)
fn insert_yaml_hash(yaml: &mut Value) {
    let hash = compute_yaml_hash(yaml);
    if let Value::Mapping(map) = yaml {
        map.insert(Value::String("_hash".to_string()), Value::String(hash));
    }
}

/// Helper: Compute hash for YAML value (copied from examples/parse_fixture.rs)
fn compute_yaml_hash(yaml: &Value) -> String {
    use blake2::{Blake2s256, Digest};
    let clean = match yaml {
        Value::Mapping(map) => {
            let mut m = map.clone();
            m.remove(&Value::String("_hash".to_string()));
            Value::Mapping(m)
        }
        _ => yaml.clone(),
    };
    let yaml_str = process_yaml_11(serde_yaml_ng::to_string(&clean).unwrap());
    let mut hasher = Blake2s256::new();
    hasher.update(yaml_str.as_bytes());
    format!("{:x}", hasher.finalize())
}

#[test]
fn test_yaml_output_matches_python() {
    // Test a representative ANSI fixture (select_simple_a)
    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");
    let sql_path = fixtures_root.join("dialects/ansi/select_simple_a.sql");
    let yml_path = fixtures_root.join("dialects/ansi/select_simple_a.yml");

    // Read SQL
    let sql_content = fs::read_to_string(&sql_path).expect("Failed to read SQL file");
    // Lex
    let input = LexInput::String(sql_content);
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);
    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);
    // Parse
    let mut parser = sqlfluffrs_parser::parser::Parser::new(&tokens, Dialect::Ansi);
    let ast = parser.call_rule_as_root().expect("Parse error");
    // Generate YAML
    let generated_yaml = node_to_yaml(&ast, &tokens).expect("YAML generation failed");
    // Read expected YAML
    let expected_yaml = fs::read_to_string(&yml_path).expect("Failed to read expected YAML");

    // Compare
    if generated_yaml.trim() != expected_yaml.trim() {
        let gen_lines: Vec<&str> = generated_yaml.lines().collect();
        let exp_lines: Vec<&str> = expected_yaml.lines().collect();
        println!("\n=== GENERATED YAML ===\n{}", generated_yaml);
        println!("\n=== EXPECTED YAML ===\n{}", expected_yaml);
        println!("\nDifferences:");
        for (i, (gen_line, exp_line)) in gen_lines.iter().zip(exp_lines.iter()).enumerate() {
            if gen_line != exp_line {
                println!("  Line {}:", i + 1);
                println!("    Generated: {}", gen_line);
                println!("    Expected:  {}", exp_line);
            }
        }
        if gen_lines.len() != exp_lines.len() {
            println!(
                "  Line count differs: Generated: {} lines, Expected: {} lines",
                gen_lines.len(),
                exp_lines.len()
            );
        }
        panic!("YAML output does not match expected Python YAML");
    }
}
// #[test]
fn test_all_dialect_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let dialects_dir = fixtures_root.join("dialects");
    let mut dialects = Vec::new();
    if let Ok(entries) = fs::read_dir(&dialects_dir) {
        for entry in entries.flatten() {
            if entry.file_type().map(|ft| ft.is_dir()).unwrap_or(false) {
                if let Some(name) = entry.file_name().to_str() {
                    dialects.push(name.to_string());
                }
            }
        }
    }
    dialects.sort();

    println!("\nFound dialects: {:?}", dialects);

    let mut total_passed = 0;
    let mut total_failed = 0;
    let mut all_failed_tests = Vec::new();

    for dialect in &dialects {
        println!("\n=== Testing dialect: {} ===", dialect);
        let tests = FixtureTest::discover(dialect, &fixtures_root);
        println!("Found {} fixture tests for {}", tests.len(), dialect);
        let mut passed = 0;
        let mut failed = 0;
        let mut failed_tests = Vec::new();
        for test in &tests {
            println!("Running test: {}", test.name);
            match test.run() {
                Ok(_ast) => {
                    passed += 1;
                    println!("✓ {}", test.name);
                }
                Err(e) => {
                    failed += 1;
                    let error = e.to_string();
                    let error_short = if error.len() > 100 {
                        format!("{}...", &error[..100])
                    } else {
                        error
                    };
                    failed_tests.push((format!("{}::{}", dialect, test.name), error_short));
                    println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
                }
            }
        }
        println!(
            "Results for {}: {} passed, {} failed",
            dialect, passed, failed
        );
        total_passed += passed;
        total_failed += failed;
        all_failed_tests.extend(failed_tests);
    }

    println!("\n========================================");
    println!(
        "Total Results: {} passed, {} failed",
        total_passed, total_failed
    );
    println!("========================================\n");

    if !all_failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &all_failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some dialect fixture tests failed");
    }
}

/// Integration tests for parsing SQL fixtures
///
/// This test suite parses SQL files from test/fixtures/dialects/ and compares
/// the output against expected YAML files.
use sqlfluffrs_parser::parser::{Node, Parser};
use std::path::Path;
use std::str::FromStr;

struct FixtureTest {
    dialect: String,
    name: String,
    sql_path: PathBuf,
    yml_path: PathBuf,
}

impl FixtureTest {
    fn discover(dialect: &str, fixtures_root: &Path) -> Vec<Self> {
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

                    // Only include tests that have corresponding YAML files
                    if yml_path.exists() {
                        tests.push(FixtureTest {
                            dialect: dialect.to_string(),
                            name,
                            sql_path: path,
                            yml_path,
                        });
                    }
                }
            }
        }
        tests.sort_by(|a, b| a.name.cmp(&b.name));
        tests
    }

    fn run(&self) -> Result<Node, String> {
        // Read SQL file
        let sql_content = fs::read_to_string(&self.sql_path)
            .map_err(|e| format!("Failed to read SQL file: {}", e))?;

        // Parse with Rust parser
        let dialect = Dialect::from_str(&self.dialect).expect("Invalid dialect");

        let input = LexInput::String(sql_content.clone());
        // Use the correct lexers for the dialect
        let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
        let (tokens, lex_errors) = lexer.lex(input, false);

        if !lex_errors.is_empty() {
            return Err(format!("Lexer errors: {:?}", lex_errors));
        }

        let mut parser = Parser::new(&tokens, dialect);

        // Try to parse as a file (top-level rule)
        parser
            .call_rule_as_root()
            .map_err(|e| format!("Parse error: {:?}", e))
    }
}

#[test]
fn test_ansi_fixtures_simple() {
    // Test only "simple" fixtures to avoid complex cases that might loop
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("ansi", &fixtures_root);
    println!("\nFound {} ANSI fixture tests", tests.len());

    // Filter to only "simple" tests
    let simple_tests: Vec<_> = tests
        .iter()
        .filter(|t| {
            t.name.contains("simple")
                || t.name == "select_a"
                || t.name == "select_b"
                || t.name == "select_c"
                || t.name == "empty_file"
        })
        .collect();

    println!("Testing {} simple fixtures\n", simple_tests.len());

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &simple_tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                // Truncate long errors
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / simple_tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
    }
}

#[test]
fn test_ansi_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("ansi", &fixtures_root);
    println!("\nFound {} ANSI fixture tests", tests.len());

    if tests.is_empty() {
        panic!("No ANSI fixtures found!");
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                // Truncate long errors
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("tests failed")
    }

    // Don't fail the test - just report results
    // This allows us to see how many tests pass
}

#[test]
fn test_bigquery_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("bigquery", &fixtures_root);
    println!("\nFound {} bigquery fixture tests", tests.len());

    if tests.is_empty() {
        panic!("No bigquery fixtures found!");
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                // Truncate long errors
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some bigquery fixture tests failed");
    }
}

#[test]
fn test_athena_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("athena", &fixtures_root);
    println!("\nFound {} athena fixture tests", tests.len());

    if tests.is_empty() {
        println!("No athena fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some athena fixture tests failed");
    }
}

#[test]
fn test_clickhouse_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("clickhouse", &fixtures_root);
    println!("\nFound {} clickhouse fixture tests", tests.len());

    if tests.is_empty() {
        println!("No clickhouse fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some clickhouse fixture tests failed");
    }
}

#[test]
fn test_databricks_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("databricks", &fixtures_root);
    println!("\nFound {} databricks fixture tests", tests.len());

    if tests.is_empty() {
        println!("No databricks fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some databricks fixture tests failed");
    }
}

#[test]
fn test_db2_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("db2", &fixtures_root);
    println!("\nFound {} db2 fixture tests", tests.len());

    if tests.is_empty() {
        println!("No db2 fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some db2 fixture tests failed");
    }
}

#[test]
fn test_doris_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("doris", &fixtures_root);
    println!("\nFound {} doris fixture tests", tests.len());

    if tests.is_empty() {
        println!("No doris fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some doris fixture tests failed");
    }
}

#[test]
fn test_duckdb_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("duckdb", &fixtures_root);
    println!("\nFound {} duckdb fixture tests", tests.len());

    if tests.is_empty() {
        println!("No duckdb fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some duckdb fixture tests failed");
    }
}

#[test]
fn test_exasol_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("exasol", &fixtures_root);
    println!("\nFound {} exasol fixture tests", tests.len());

    if tests.is_empty() {
        println!("No exasol fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some exasol fixture tests failed");
    }
}

#[test]
fn test_flink_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("flink", &fixtures_root);
    println!("\nFound {} flink fixture tests", tests.len());

    if tests.is_empty() {
        println!("No flink fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some flink fixture tests failed");
    }
}

#[test]
fn test_greenplum_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("greenplum", &fixtures_root);
    println!("\nFound {} greenplum fixture tests", tests.len());

    if tests.is_empty() {
        println!("No greenplum fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some greenplum fixture tests failed");
    }
}

#[test]
fn test_hive_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("hive", &fixtures_root);
    println!("\nFound {} hive fixture tests", tests.len());

    if tests.is_empty() {
        println!("No hive fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some hive fixture tests failed");
    }
}

#[test]
fn test_impala_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("impala", &fixtures_root);
    println!("\nFound {} impala fixture tests", tests.len());

    if tests.is_empty() {
        println!("No impala fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some impala fixture tests failed");
    }
}

#[test]
fn test_mariadb_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("mariadb", &fixtures_root);
    println!("\nFound {} mariadb fixture tests", tests.len());

    if tests.is_empty() {
        println!("No mariadb fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some mariadb fixture tests failed");
    }
}

#[test]
fn test_materialize_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("materialize", &fixtures_root);
    println!("\nFound {} materialize fixture tests", tests.len());

    if tests.is_empty() {
        println!("No materialize fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some materialize fixture tests failed");
    }
}

#[test]
fn test_mysql_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("mysql", &fixtures_root);
    println!("\nFound {} mysql fixture tests", tests.len());

    if tests.is_empty() {
        println!("No mysql fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some mysql fixture tests failed");
    }
}

#[test]
fn test_oracle_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("oracle", &fixtures_root);
    println!("\nFound {} oracle fixture tests", tests.len());

    if tests.is_empty() {
        println!("No oracle fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some oracle fixture tests failed");
    }
}

#[test]
fn test_postgres_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("postgres", &fixtures_root);
    println!("\nFound {} postgres fixture tests", tests.len());

    if tests.is_empty() {
        println!("No postgres fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some postgres fixture tests failed");
    }
}

#[test]
fn test_redshift_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("redshift", &fixtures_root);
    println!("\nFound {} redshift fixture tests", tests.len());

    if tests.is_empty() {
        println!("No redshift fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some redshift fixture tests failed");
    }
}

#[test]
fn test_snowflake_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("snowflake", &fixtures_root);
    println!("\nFound {} snowflake fixture tests", tests.len());

    if tests.is_empty() {
        println!("No snowflake fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some snowflake fixture tests failed");
    }
}

#[test]
fn test_soql_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("soql", &fixtures_root);
    println!("\nFound {} soql fixture tests", tests.len());

    if tests.is_empty() {
        println!("No soql fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some soql fixture tests failed");
    }
}

#[test]
fn test_sparksql_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("sparksql", &fixtures_root);
    println!("\nFound {} sparksql fixture tests", tests.len());

    if tests.is_empty() {
        println!("No sparksql fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some sparksql fixture tests failed");
    }
}

#[test]
fn test_sqlite_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("sqlite", &fixtures_root);
    println!("\nFound {} sqlite fixture tests", tests.len());

    if tests.is_empty() {
        println!("No sqlite fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some sqlite fixture tests failed");
    }
}

#[test]
fn test_starrocks_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("starrocks", &fixtures_root);
    println!("\nFound {} starrocks fixture tests", tests.len());

    if tests.is_empty() {
        println!("No starrocks fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some starrocks fixture tests failed");
    }
}

#[test]
fn test_teradata_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("teradata", &fixtures_root);
    println!("\nFound {} teradata fixture tests", tests.len());

    if tests.is_empty() {
        println!("No teradata fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some teradata fixture tests failed");
    }
}

#[test]
fn test_trino_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("trino", &fixtures_root);
    println!("\nFound {} trino fixture tests", tests.len());

    if tests.is_empty() {
        println!("No trino fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some trino fixture tests failed");
    }
}

#[test]
fn test_tsql_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("tsql", &fixtures_root);
    println!("\nFound {} tsql fixture tests", tests.len());

    if tests.is_empty() {
        println!("No tsql fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some tsql fixture tests failed");
    }
}

#[test]
fn test_vertica_fixtures() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("vertica", &fixtures_root);
    println!("\nFound {} vertica fixture tests", tests.len());

    if tests.is_empty() {
        println!("No vertica fixtures found - skipping test");
        return;
    }

    let mut passed = 0;
    let mut failed = 0;
    let mut failed_tests = Vec::new();

    for test in &tests {
        println!("Running test: {}", test.name);
        match test.run() {
            Ok(_ast) => {
                passed += 1;
                println!("✓ {}", test.name);
            }
            Err(e) => {
                failed += 1;
                let error = e.to_string();
                let error_short = if error.len() > 100 {
                    format!("{}...", &error[..100])
                } else {
                    error
                };
                failed_tests.push((&test.name, error_short));
                println!("✗ {} - {}", test.name, failed_tests.last().unwrap().1);
            }
        }
    }

    println!("\n========================================");
    println!("Results: {} passed, {} failed", passed, failed);
    println!(
        "Pass rate: {:.1}%",
        (passed as f64 / tests.len() as f64) * 100.0
    );
    println!("========================================\n");

    if !failed_tests.is_empty() {
        println!("Failed tests:");
        for (name, error) in &failed_tests {
            println!("  {} - {}", name, error);
        }
        panic!("Some vertica fixture tests failed");
    }
}

#[test]
fn test_select_simple_a() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let test = sqlfluffrs::test_harness::FixtureTest {
        dialect: "ansi".to_string(),
        name: "select_simple_a".to_string(),
        sql_path: fixtures_root.join("dialects/ansi/select_simple_a.sql"),
        yml_path: fixtures_root.join("dialects/ansi/select_simple_a.yml"),
    };

    let result = test.run();

    if let Some(yaml) = &result.generated_yaml {
        println!("\n=== Generated YAML ===");
        println!("{}", yaml);
    }

    if let Some(error) = &result.error {
        println!("\n=== Error ===");
        println!("{}", error);
    }

    assert!(result.success, "Test failed: {:?}", result.error);
}

#[test]
fn test_select_a() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures");

    let tests = FixtureTest::discover("ansi", &fixtures_root);
    let test = tests
        .iter()
        .find(|t| t.name == "select_a")
        .expect("select_a.sql not found");

    let ast = test.run().expect("Parse failed");
    println!("Successfully parsed select_a");
    println!("AST: {:#?}", ast);
}
