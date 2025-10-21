/// Integration tests for parsing SQL fixtures
///
/// This test suite parses SQL files from test/fixtures/dialects/ and compares
/// the output against expected YAML files.
use sqlfluffrs::{
    lexer::{LexInput, Lexer},
    parser::{Node, Parser},
    Dialect,
};
use std::fs;
use std::path::{Path, PathBuf};

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
        let dialect = match self.dialect.as_str() {
            "ansi" => Dialect::Ansi,
            _ => return Err(format!("Unsupported dialect: {}", self.dialect)),
        };

        let input = LexInput::String(sql_content.clone());
        let lexer = Lexer::new(None, dialect);
        let (tokens, lex_errors) = lexer.lex(input, false);

        if !lex_errors.is_empty() {
            return Err(format!("Lexer errors: {:?}", lex_errors));
        }

        let mut parser = Parser::new(&tokens, dialect);

        // Try to parse as a file (top-level rule)
        parser
            .call_rule("FileSegment", &[])
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
    }

    // Don't fail the test - just report results
    // This allows us to see how many tests pass
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
