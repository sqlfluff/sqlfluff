/// Utility to compare YAML 1.1 fixture files with Rust-generated YAML
/// by normalizing both through serde_yaml_ng round-trip.
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::path::PathBuf;

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
    let yaml_string = serde_yaml_ng::to_string(&Value::Mapping(root_map))?;
    Ok(format!("{}{}", header, yaml_string))
}

fn calculate_hash<T: Hash>(t: &T) -> u64 {
    let mut s = DefaultHasher::new();
    t.hash(&mut s);
    s.finish()
}

fn normalize_yaml_through_serde(yaml_str: &str) -> Result<String, String> {
    // Parse YAML 1.1 and re-serialize with serde_yaml_ng
    let value: serde_yaml_ng::Value = serde_yaml_ng::from_str(yaml_str)
        .map_err(|e| format!("Failed to parse YAML: {}", e))?;

    let normalized = serde_yaml_ng::to_string(&value)
        .map_err(|e| format!("Failed to serialize YAML: {}", e))?;

    Ok(normalized)
}

fn compare_yaml_files(expected_path: &PathBuf, generated_yaml: &str) -> Result<(), String> {
    // Read expected YAML from file
    let expected_yaml = std::fs::read_to_string(expected_path)
        .map_err(|e| format!("Failed to read expected YAML: {}", e))?;

    // Normalize both YAMLs
    let normalized_expected = normalize_yaml_through_serde(&expected_yaml)?;
    let normalized_generated = normalize_yaml_through_serde(generated_yaml)?;

    // Calculate hashes
    let expected_hash = calculate_hash(&normalized_expected);
    let generated_hash = calculate_hash(&normalized_generated);

    println!("=== YAML Comparison ===");
    println!("Expected hash:  {:016x}", expected_hash);
    println!("Generated hash: {:016x}", generated_hash);

    if expected_hash != generated_hash {
        println!("\n⚠️  Hashes differ!");

        // Line-by-line comparison
        let expected_lines: Vec<&str> = normalized_expected.lines().collect();
        let generated_lines: Vec<&str> = normalized_generated.lines().collect();

        println!("\n=== Line-by-Line Comparison ===");
        println!("Expected lines:  {}", expected_lines.len());
        println!("Generated lines: {}", generated_lines.len());

        let max_lines = expected_lines.len().max(generated_lines.len());
        let mut diff_count = 0;

        for i in 0..max_lines {
            let exp_line = expected_lines.get(i).unwrap_or(&"<missing>");
            let gen_line = generated_lines.get(i).unwrap_or(&"<missing>");

            if exp_line != gen_line {
                diff_count += 1;
                if diff_count <= 50 { // Show first 50 differences
                    println!("\nLine {}:", i + 1);
                    println!("  Expected:  {}", exp_line);
                    println!("  Generated: {}", gen_line);
                }
            }
        }

        if diff_count > 50 {
            println!("\n... and {} more differences", diff_count - 50);
        }

        println!("\nTotal differences: {} lines", diff_count);

        // Show first 20 lines of each for context
        println!("\n=== First 20 Lines of Expected (Normalized) ===");
        for (i, line) in expected_lines.iter().take(20).enumerate() {
            println!("{:3}: {}", i + 1, line);
        }

        println!("\n=== First 20 Lines of Generated (Normalized) ===");
        for (i, line) in generated_lines.iter().take(20).enumerate() {
            println!("{:3}: {}", i + 1, line);
        }

        Err("YAML structures differ".to_string())
    } else {
        println!("✅ YAMLs match!");
        Ok(())
    }
}

#[test]
fn test_yaml_comparison_ansi_arithmetic_a() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures/dialects/ansi");

    let sql_path = fixtures_root.join("arithmetic_a.sql");
    let yml_path = fixtures_root.join("arithmetic_a.yml");

    // Read SQL
    let sql_content = std::fs::read_to_string(&sql_path).expect("Failed to read SQL file");

    // Parse with Rust
    let dialect = sqlfluffrs_dialects::Dialect::Ansi;
    let input = sqlfluffrs_lexer::LexInput::String(sql_content);
    let lexer = sqlfluffrs_lexer::Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);
    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    let mut parser = sqlfluffrs_parser::parser::Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root().expect("Parse error");

    // Generate YAML
    let generated_yaml = node_to_yaml(&ast, &tokens)
        .expect("YAML conversion error");

    // Compare
    compare_yaml_files(&yml_path, &generated_yaml).expect("YAML comparison failed");
}

#[test]
fn test_yaml_comparison_tsql_sqlcmd_command() {
    env_logger::try_init().ok();

    let fixtures_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures/dialects/tsql");

    let sql_path = fixtures_root.join("sqlcmd_command.sql");
    let yml_path = fixtures_root.join("sqlcmd_command.yml");

    // Read SQL
    let sql_content = std::fs::read_to_string(&sql_path).expect("Failed to read SQL file");

    // Parse with Rust
    let dialect = sqlfluffrs_dialects::Dialect::Tsql;
    let input = sqlfluffrs_lexer::LexInput::String(sql_content);
    let lexer = sqlfluffrs_lexer::Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);
    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    let mut parser = sqlfluffrs_parser::parser::Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root().expect("Parse error");

    // Generate YAML
    let generated_yaml = node_to_yaml(&ast, &tokens)
        .expect("YAML conversion error");

    // Compare
    compare_yaml_files(&yml_path, &generated_yaml).expect("YAML comparison failed");
}
