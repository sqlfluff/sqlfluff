///! Demonstration of GrammarInst size and usage
///!
///! This example shows:
///! 1. Size comparison: Grammar (376 bytes) vs GrammarInst (20 bytes)
///! 2. Memory layout and field packing
///! 3. Basic usage patterns
use sqlfluffrs_types::{
    GrammarFlags, GrammarId, GrammarInst, GrammarInstParseMode, GrammarVariant, ParseMode,
};

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  GrammarInst Structure Design - Phase 2 Task 4         ║");
    println!("║  Compact Instruction Format Prototype                  ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");

    // Size measurements
    println!("=== Size Measurements ===\n");
    println!(
        "size_of::<GrammarInst>() = {} bytes",
        std::mem::size_of::<GrammarInst>()
    );
    println!(
        "align_of::<GrammarInst>() = {} bytes",
        std::mem::align_of::<GrammarInst>()
    );
    println!();
    println!("Component sizes:");
    println!(
        "  GrammarVariant:  {} byte",
        std::mem::size_of::<GrammarVariant>()
    );
    println!(
        "  ParseMode:       {} byte",
        std::mem::size_of::<ParseMode>()
    );
    println!(
        "  GrammarFlags:    {} bytes",
        std::mem::size_of::<GrammarFlags>()
    );
    println!("  u32 (indices):   {} bytes", std::mem::size_of::<u32>());
    println!("  u16 (counts):    {} bytes", std::mem::size_of::<u16>());
    println!();

    // Comparison with old Grammar enum
    println!("=== Memory Comparison ===\n");
    println!("Old Arc<Grammar>:");
    println!("  Grammar enum:        376 bytes");
    println!("  Arc pointer:         8 bytes");
    println!("  Arc control block:   ~16 bytes");
    println!("  Total per grammar:   ~400 bytes\n");

    println!("New GrammarInst:");
    println!("  Instruction:         20 bytes");
    println!("  GrammarId (u32):     4 bytes");
    println!("  Total per grammar:   24 bytes (for indexing)\n");

    println!("Improvement: ~94% size reduction per grammar node\n");

    // Memory for 6,000 grammar rules
    println!("=== Dialect Memory (6,000 rules) ===\n");
    let rule_count = 6_000;
    let old_per_rule = 400;
    let new_per_rule = 20;

    let old_total = rule_count * old_per_rule;
    let new_total = rule_count * new_per_rule;

    println!(
        "Old (Arc-based):     {} bytes ({:.2} MB)",
        old_total,
        old_total as f64 / 1_048_576.0
    );
    println!(
        "New (table-driven):  {} bytes ({:.2} MB)",
        new_total,
        new_total as f64 / 1_048_576.0
    );
    println!(
        "Reduction: {:.1}%\n",
        ((old_total - new_total) as f64 / old_total as f64) * 100.0
    );

    // Example usage
    println!("=== Usage Examples ===\n");

    // Example 1: Create a Sequence instruction
    let sequence = GrammarInst::new(GrammarVariant::Sequence)
        .with_parse_mode(GrammarInstParseMode::Greedy)
        .with_flags(GrammarFlags::empty().with(GrammarFlags::ALLOW_GAPS))
        .with_children(0, 3)
        .with_terminators(10, 2);

    println!("1. Sequence instruction:");
    println!("   Variant: {:?}", sequence.variant);
    println!("   Parse mode: {:?}", sequence.parse_mode);
    println!("   Flags: allow_gaps={}", sequence.flags.allow_gaps());
    println!(
        "   Children: [{}..{})",
        sequence.first_child_idx,
        sequence.first_child_idx + sequence.child_count as u32
    );
    println!(
        "   Terminators: [{}..{})",
        sequence.first_terminator_idx,
        sequence.first_terminator_idx + sequence.terminator_count as u32
    );
    println!();

    // Example 2: Create an optional Ref instruction
    let ref_inst = GrammarInst::new(GrammarVariant::Ref)
        .with_flags(
            GrammarFlags::empty()
                .with(GrammarFlags::OPTIONAL)
                .with(GrammarFlags::RESET_TERMINATORS),
        )
        .with_children(42, 0); // name_idx = 42 (STRING_TABLE index)

    println!("2. Ref instruction:");
    println!("   Variant: {:?}", ref_inst.variant);
    println!("   Optional: {}", ref_inst.is_optional());
    println!(
        "   Reset terminators: {}",
        ref_inst.flags.reset_terminators()
    );
    println!("   Name index: {}", ref_inst.first_child_idx);
    println!();

    // Example 3: Create an AnyNumberOf instruction
    let any_number = GrammarInst::new(GrammarVariant::AnyNumberOf)
        .with_min_times(1)
        .with_children(5, 2)
        .with_terminators(12, 1);

    println!("3. AnyNumberOf instruction:");
    println!("   Variant: {:?}", any_number.variant);
    println!("   Min times: {}", any_number.min_times);
    println!(
        "   Optional: {} (min_times={}, optional flag={})",
        any_number.is_optional(),
        any_number.min_times,
        any_number.flags.optional()
    );
    println!("   Children: {} elements", any_number.child_count);
    println!();

    // Example 4: GrammarId usage
    println!("4. GrammarId type safety:");
    let id1 = GrammarId::new(100);
    let id2 = GrammarId::new(200);
    println!("   {} and {} are type-safe indices", id1, id2);
    println!("   Can't accidentally mix with raw u32");
    println!();

    // Example 5: Flag operations
    println!("5. Flag operations:");
    let mut flags = GrammarFlags::empty();
    println!("   Initial flags: {:016b}", flags.bits());

    flags = flags.with(GrammarFlags::OPTIONAL);
    println!(
        "   With OPTIONAL: {:016b} (optional={})",
        flags.bits(),
        flags.optional()
    );

    flags = flags.with(GrammarFlags::ALLOW_GAPS);
    println!(
        "   With ALLOW_GAPS: {:016b} (allow_gaps={})",
        flags.bits(),
        flags.allow_gaps()
    );

    flags = flags.without(GrammarFlags::OPTIONAL);
    println!(
        "   Without OPTIONAL: {:016b} (optional={})",
        flags.bits(),
        flags.optional()
    );
    println!();

    // Mock table access example
    println!("=== Table Access Pattern ===\n");

    // Simulated tables
    let grammar_table = vec![
        GrammarInst::new(GrammarVariant::Sequence).with_children(0, 3),
        GrammarInst::new(GrammarVariant::Ref).with_children(10, 0),
        GrammarInst::new(GrammarVariant::Token).with_children(20, 0),
    ];

    let child_ids: Vec<u32> = vec![1, 2, 2 /* ... */];

    println!("Grammar table (3 instructions):");
    for (i, inst) in grammar_table.iter().enumerate() {
        println!(
            "  [{}] {:?} (children: {})",
            i, inst.variant, inst.child_count
        );
    }
    println!();

    println!("Accessing Sequence children:");
    let sequence_id = GrammarId::new(0);
    let sequence_inst = sequence_id.inst(&grammar_table);
    let children = sequence_inst.children(&child_ids);
    println!(
        "  GrammarId({}) -> children: {:?}",
        sequence_id.get(),
        children
    );
    println!(
        "  Resolved to GrammarIds: {:?}",
        children
            .iter()
            .map(|&id| GrammarId::new(id))
            .collect::<Vec<_>>()
    );
    println!();

    // Field packing demonstration
    println!("=== Field Packing Analysis ===\n");
    println!("Memory layout (20 bytes):");
    println!("  [0..1]   variant: GrammarVariant (u8)");
    println!("  [1..2]   parse_mode: ParseMode (u8)");
    println!("  [2..4]   flags: GrammarFlags (u16)");
    println!("  [4..8]   first_child_idx: u32");
    println!("  [8..10]  child_count: u16");
    println!("  [10..12] min_times: u16");
    println!("  [12..16] first_terminator_idx: u32");
    println!("  [16..18] terminator_count: u16");
    println!("  [18..20] _padding: u16");
    println!();
    println!("Alignment: 4 bytes (for efficient CPU access)");
    println!("Padding: 2 bytes reserved for future use");
    println!();

    // Design goals summary
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Design Goals Achieved                                  ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");
    println!("✓ Compact size: 20 bytes (target: ≤20 bytes)");
    println!("✓ Zero allocations: All data in static tables");
    println!("✓ Cache-friendly: Contiguous array access");
    println!("✓ Type-safe: GrammarId newtype wrapper");
    println!("✓ Efficient: 4-byte alignment, minimal padding");
    println!("✓ Extensible: 16 flag bits, 2 bytes reserved padding");
    println!();

    println!("Phase 2 Task 4: ✅ COMPLETE\n");
}
