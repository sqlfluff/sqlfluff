use sqlfluffrs_types::RootGrammar;

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
        !ANSI_TABLES.instructions.is_empty(),
        "Instructions table should be present"
    );
    assert!(
        !ANSI_TABLES.strings.is_empty(),
        "Strings table should be present"
    );

    // Get the root grammar and ensure it is table-driven with a valid id
    let ansi_root = ansi.get_root_grammar();
    let ctx = GrammarContext::new(ansi_root.tables);
    let rule_name = ctx.get_name(ansi_root.grammar_id).unwrap_or("<unknown>");
    println!("Root grammar: {}", rule_name);

    // Ensure a known segment maps to a grammar id (table-driven RootGrammar expected)
    if let Some(root) = ansi.get_segment_grammar("SelectStatementSegment") {
        let ctx = GrammarContext::new(root.tables);
        let rule_name = ctx.get_name(root.grammar_id).unwrap_or("<unknown>");
        println!("SelectStatementSegment grammar: {}", rule_name);
    }
}
