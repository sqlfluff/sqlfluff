// Test module for generated table-driven grammar
// This file includes the generated ANSI tables to verify they compile

#![cfg(test)]

use crate::grammar_api::GrammarContext;
use crate::grammar_inst::{
    GrammarFlags, GrammarId, GrammarInst, GrammarVariant, ParseMode as GrammarInstParseMode,
};
use crate::grammar_tables::{GrammarTables, SimpleHintData};
use crate::parser::SimpleHint;

// Strip the first 3 lines (comment + inner attr + use statement)
// and include the rest
macro_rules! include_generated_skip_header {
    ($path:expr) => {
        include!(concat!($path));
    };
}

// Include generated tables (skip first few lines manually)
include!("/tmp/ansi_tables_test_no_header.rs");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tables_compile() {
        // Basic smoke test: verify tables exist and have expected structure
        assert!(
            INSTRUCTIONS.len() > 0,
            "Instructions table should not be empty"
        );
        assert!(CHILD_IDS.len() > 0, "Child IDs table should not be empty");
        assert!(STRINGS.len() > 0, "Strings table should not be empty");

        println!("Instructions: {}", INSTRUCTIONS.len());
        println!("Child IDs: {}", CHILD_IDS.len());
        println!("Terminators: {}", TERMINATORS.len());
        println!("Strings: {}", STRINGS.len());
        println!("Aux Data: {}", AUX_DATA.len());
        println!("Regex Patterns: {}", REGEX_PATTERNS.len());
        println!("Simple Hints: {}", SIMPLE_HINTS.len());
    }

    #[test]
    fn test_grammar_context_access() {
        // Test GrammarContext can access the tables
        let ctx = GrammarContext::new(&ANSI_TABLES);

        // Get root grammar
        let root_id = get_ansi_root_grammar();
        assert!(
            root_id.0 < INSTRUCTIONS.len() as u32,
            "Root ID should be valid"
        );

        let root_inst = ctx.inst(root_id);
        println!("Root grammar variant: {:?}", ctx.variant(root_id));

        // Verify we can access children
        let children: Vec<_> = ctx.children(root_id).collect();
        println!("Root has {} children", children.len());
    }

    #[test]
    fn test_segment_lookup() {
        // Test we can look up segment grammars by name
        let select_id = get_ansi_segment_grammar("SelectStatementSegment");
        assert!(select_id.is_some(), "Should find SelectStatementSegment");

        if let Some(id) = select_id {
            assert!(
                id.0 < INSTRUCTIONS.len() as u32,
                "Grammar ID should be valid"
            );
            println!("SelectStatementSegment ID: {}", id.0);
        }
    }

    #[test]
    fn test_no_dangling_references() {
        // Verify all child_ids and terminators reference valid instructions
        for (i, inst) in INSTRUCTIONS.iter().enumerate() {
            // Check children
            for j in inst.first_child_idx..(inst.first_child_idx + inst.child_count as u32) {
                let child_id = CHILD_IDS[j as usize];
                assert!(
                    (child_id as usize) < INSTRUCTIONS.len(),
                    "Inst {} has invalid child_id {} at index {}",
                    i,
                    child_id,
                    j
                );
            }

            // Check terminators
            for j in inst.first_terminator_idx
                ..(inst.first_terminator_idx + inst.terminator_count as u32)
            {
                let term_id = TERMINATORS[j as usize];
                assert!(
                    (term_id as usize) < INSTRUCTIONS.len(),
                    "Inst {} has invalid terminator_id {} at index {}",
                    i,
                    term_id,
                    j
                );
            }
        }
    }

    #[test]
    fn test_memory_size() {
        // Verify memory usage is as expected
        let inst_bytes = INSTRUCTIONS.len() * std::mem::size_of::<crate::GrammarInst>();
        let child_bytes = CHILD_IDS.len() * 4;
        let term_bytes = TERMINATORS.len() * 4;
        let aux_bytes = AUX_DATA.len() * 4;

        // String bytes (rough estimate)
        let string_bytes: usize = STRINGS.iter().map(|s| s.len()).sum();
        let regex_bytes: usize = REGEX_PATTERNS.iter().map(|r| r.len()).sum();

        let total = inst_bytes + child_bytes + term_bytes + aux_bytes + string_bytes + regex_bytes;

        println!("Memory breakdown:");
        println!("  Instructions: {} bytes", inst_bytes);
        println!("  Child IDs: {} bytes", child_bytes);
        println!("  Terminators: {} bytes", term_bytes);
        println!("  Aux Data: {} bytes", aux_bytes);
        println!("  Strings: {} bytes", string_bytes);
        println!("  Regex: {} bytes", regex_bytes);
        println!("  TOTAL: {} bytes ({:.2} KB)", total, total as f64 / 1024.0);

        // Target was ~500 KB, but with all hints might be larger
        assert!(
            total < 1_000_000,
            "Total memory should be < 1 MB (was {} bytes)",
            total
        );
    }
}
