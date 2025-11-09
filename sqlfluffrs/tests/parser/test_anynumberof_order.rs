//! Test that AnyNumberOf tries elements in order and returns on the first match.
#[test]
fn test_anynumberof_trim_function() {
    // Lex the input using the ANSI dialect
    let sql = "TRIM(BOTH FROM foo)";
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    // Load the FunctionSegment from the ANSI dialect
    let grammar =
        get_ansi_segment_grammar("FunctionSegment").expect("FunctionContentsGrammar not found");

    let mut parser = Parser::new(&tokens, sqlfluffrs_dialects::Dialect::Ansi);
    let _ = env_logger::builder().is_test(true).try_init();
    let node = parser.parse_with_grammar_cached(&grammar, &[]).unwrap();
    println!("{:#?}", node);
    // The result should match the TRIM grammar, not the EXTRACT/SUBSTRING grammar
    assert!(
        contains_trim_parameters_grammar(&node),
        "Should contain TrimParametersGrammar"
    );
}

#[test]
fn test_anynumberof_trim_function_with_expression() {
    // Lex the input using the ANSI dialect
    let sql = "TRIM(BOTH foo FROM bar)";
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    // Load the FunctionSegment from the ANSI dialect
    let grammar =
        get_ansi_segment_grammar("FunctionSegment").expect("FunctionContentsGrammar not found");

    let mut parser = Parser::new(&tokens, sqlfluffrs_dialects::Dialect::Ansi);
    let _ = env_logger::builder().is_test(true).try_init();
    let node = parser.parse_with_grammar_cached(&grammar, &[]).unwrap();
    println!("{:#?}", node);
    // The result should match the TRIM grammar, not the EXTRACT/SUBSTRING grammar
    assert!(
        contains_trim_parameters_grammar(&node),
        "Should contain TrimParametersGrammar"
    );
}

use sqlfluffrs_parser::parser::{Node, Parser};
fn contains_trim_parameters_grammar(node: &Node) -> bool {
    match node {
        Node::Ref { name, .. } if name == "TrimParametersGrammar" => true,
        Node::Sequence { children }
        | Node::DelimitedList { children }
        | Node::Bracketed { children, .. }
        | Node::Unparsable { children, .. } => {
            children.iter().any(contains_trim_parameters_grammar)
        }
        Node::Ref { child, .. } => contains_trim_parameters_grammar(child),
        _ => false,
    }
}
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::dialect::ansi::parser::get_ansi_segment_grammar;
use sqlfluffrs_lexer::{LexInput, Lexer};

#[test]
fn test_anynumberof_order_and_earliest_match() {
    // Lex the input using the ANSI dialect
    let sql = "BOTH FROM foo";
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    // Load grammars from the ANSI dialect
    let grammar = get_ansi_segment_grammar("FunctionContentsGrammar")
        .expect("FunctionContentsGrammar not found");

    let mut parser = Parser::new(&tokens, sqlfluffrs_dialects::Dialect::Ansi);
    let _ = env_logger::builder().is_test(true).try_init();
    let node = parser.parse_with_grammar_cached(&grammar, &[]).unwrap();
    // The result should match the TRIM grammar, not the EXTRACT/SUBSTRING grammar
    println!("{:#?}", node);
    assert!(
        contains_trim_parameters_grammar(&node),
        "Should contain TrimParametersGrammar"
    );
}

#[test]
fn test_anynumberof_order_and_earliest_match_with_expression() {
    // Enable debug logging and redirect to a file
    std::env::set_var("RUST_LOG", "debug");
    let log_file = std::fs::File::create("parser_debug.log").expect("Failed to create log file");
    let log_file = std::sync::Arc::new(std::sync::Mutex::new(log_file));
    //
    // Use env_logger if available, else fallback
    let _ = env_logger::builder()
        .format(move |_buf, record| {
            use std::io::Write;
            let mut log_file = log_file.lock().unwrap();
            writeln!(log_file, "{} - {}", record.level(), record.args())
        })
        .is_test(true)
        .try_init();

    // Lex the input using the ANSI dialect
    let sql = "BOTH 'foo' FROM bar";
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);

    // Load grammars from the ANSI dialect
    let grammar = get_ansi_segment_grammar("FunctionContentsGrammar")
        .expect("FunctionContentsGrammar not found");

    let mut parser = Parser::new(&tokens, sqlfluffrs_dialects::Dialect::Ansi);
    let node = parser.parse_with_grammar_cached(&grammar, &[]).unwrap();
    // The result should match the TRIM grammar, not the EXTRACT/SUBSTRING grammar
    println!("{:#?}", node);
    assert!(
        contains_trim_parameters_grammar(&node),
        "Should contain TrimParametersGrammar"
    );
}
