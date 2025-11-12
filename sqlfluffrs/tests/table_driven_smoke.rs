use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use sqlfluffrs_types::{GrammarContext, RootGrammar};

#[test]
fn table_driven_smoke() {
    // Basic sanity checks on generated ANSI tables and segment lookup.
    // We don't attempt a full parse here because some table-driven handlers
    // (e.g. Ref expansion into iterative parser) are not yet migrated.

    // Access the generated tables and root accessor
    use sqlfluffrs_dialects::dialect::ansi::parser::{
        get_ansi_root_grammar, get_ansi_segment_grammar, ANSI_TABLES,
    };

    // Verify tables are non-empty
    assert!(
        ANSI_TABLES.instructions.len() > 0,
        "Instructions table should be present"
    );
    assert!(
        ANSI_TABLES.strings.len() > 0,
        "Strings table should be present"
    );

    // Get the root grammar and ensure it is table-driven with a valid id
    let root = get_ansi_root_grammar();
    match root {
        RootGrammar::TableDriven { grammar_id, tables } => {
            assert!(
                grammar_id.0 < tables.instructions.len() as u32,
                "Root grammar id should be in range"
            );
        }
        RootGrammar::Arc(_) => panic!("Expected table-driven root for ansi in this test"),
    }

    // Ensure a known segment maps to a grammar id (table-driven RootGrammar expected)
    if let Some(seg_root) = get_ansi_segment_grammar("SelectStatementSegment") {
        match seg_root {
            RootGrammar::TableDriven { grammar_id, tables } => {
                assert!(
                    grammar_id.0 < tables.instructions.len() as u32,
                    "SelectStatementSegment id should be valid"
                );
            }
            RootGrammar::Arc(_) => panic!("Expected table-driven segment for ansi in this test"),
        }
    } else {
        panic!("SelectStatementSegment not found in generated tables");
    }
}
