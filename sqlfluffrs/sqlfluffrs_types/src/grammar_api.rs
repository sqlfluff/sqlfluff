//! Ergonomic API for Table-Driven Grammar Access
//!
//! This module provides high-level helpers for working with grammar tables
//! in parser handlers. It abstracts away raw index arithmetic and provides
//! type-safe, iterator-based access patterns.

use crate::grammar_inst::{GrammarId, GrammarInst, GrammarVariant};
use crate::grammar_tables::{GrammarInstExt, GrammarTables};

/// Context for grammar table access
///
/// Wraps GrammarTables with convenience methods for parser handlers.
/// Passed to handler functions instead of raw tables.
pub struct GrammarContext<'a> {
    tables: &'a GrammarTables,
}

impl<'a> GrammarContext<'a> {
    /// Create new context from tables
    pub const fn new(tables: &'a GrammarTables) -> Self {
        Self { tables }
    }

    /// Get instruction by ID
    #[inline]
    pub fn inst(&self, id: GrammarId) -> &GrammarInst {
        self.tables.get_inst(id)
    }

    /// Get instruction variant by ID
    #[inline]
    pub fn variant(&self, id: GrammarId) -> GrammarVariant {
        self.inst(id).variant
    }

    /// Check if instruction is optional
    #[inline]
    pub fn is_optional(&self, id: GrammarId) -> bool {
        self.inst(id).is_optional()
    }

    /// Get children as iterator
    #[inline]
    pub fn children(&self, id: GrammarId) -> impl Iterator<Item = GrammarId> + '_ {
        let inst = self.inst(id);
        inst.children_iter(self.tables.child_ids)
    }

    /// Get children as slice
    #[inline]
    pub fn children_slice(&self, id: GrammarId) -> &[u32] {
        let inst = self.inst(id);
        self.tables.get_children(inst)
    }

    /// Get number of children
    #[inline]
    pub fn children_count(&self, id: GrammarId) -> usize {
        self.inst(id).child_count as usize
    }

    /// Get terminators as iterator
    #[inline]
    pub fn terminators(&self, id: GrammarId) -> impl Iterator<Item = GrammarId> + '_ {
        let inst = self.inst(id);
        inst.terminators_iter(self.tables.terminators)
    }

    /// Get terminators as slice
    #[inline]
    pub fn terminators_slice(&self, id: GrammarId) -> &[u32] {
        let inst = self.inst(id);
        self.tables.get_terminators(inst)
    }

    /// Get number of terminators
    #[inline]
    pub fn terminators_count(&self, id: GrammarId) -> usize {
        self.inst(id).terminator_count as usize
    }

    /// Get Ref name (for Ref variant)
    #[inline]
    pub fn ref_name(&self, id: GrammarId) -> &'static str {
        let inst = self.inst(id);
        debug_assert_eq!(inst.variant, GrammarVariant::Ref);
        self.tables.get_string(inst.first_child_idx)
    }

    /// Get string template (for StringParser/TypedParser/Token variants)
    #[inline]
    pub fn template(&self, id: GrammarId) -> &'static str {
        let inst = self.inst(id);
        self.tables.get_string(inst.first_child_idx)
    }

    /// Get multiple string templates (for MultiStringParser)
    #[inline]
    pub fn templates(&self, id: GrammarId) -> Vec<&'static str> {
        let inst = self.inst(id);
        debug_assert_eq!(inst.variant, GrammarVariant::MultiStringParser);

        let start = inst.first_child_idx as usize;
        let count = inst.child_count as usize;

        // Templates are stored as sequential string indices in aux_data
        (0..count)
            .map(|i| {
                let str_idx = self.tables.aux_data[start + i];
                self.tables.get_string(str_idx)
            })
            .collect()
    }

    /// Get min_times (for AnyNumberOf/AnySetOf/Delimited)
    #[inline]
    pub fn min_times(&self, id: GrammarId) -> usize {
        self.inst(id).min_times as usize
    }

    /// Get max_times (for AnyNumberOf/AnySetOf, stored in aux_data)
    #[inline]
    pub fn max_times(&self, id: GrammarId) -> Option<usize> {
        let inst = self.inst(id);
        // max_times is stored in aux_data at index = first_child_idx
        // If value is u32::MAX, it means None (unbounded)
        let max_value = self.tables.get_aux(inst.first_child_idx);
        if max_value == u32::MAX {
            None
        } else {
            Some(max_value as usize)
        }
    }

    /// Get delimiter ID (for Delimited variant)
    #[inline]
    pub fn delimiter(&self, id: GrammarId) -> GrammarId {
        let inst = self.inst(id);
        debug_assert_eq!(inst.variant, GrammarVariant::Delimited);

        // Delimiter ID is stored in aux_data
        let delimiter_id = self.tables.get_aux(inst.first_child_idx);
        GrammarId::new(delimiter_id)
    }

    /// Get bracket pair (for Bracketed variant)
    #[inline]
    pub fn bracket_pair(&self, id: GrammarId) -> (GrammarId, GrammarId) {
        let inst = self.inst(id);
        debug_assert_eq!(inst.variant, GrammarVariant::Bracketed);

        // Bracket pair IDs are stored in aux_data as two consecutive u32s
        let start_idx = inst.first_child_idx as usize;
        let open_id = self.tables.aux_data[start_idx];
        let close_id = self.tables.aux_data[start_idx + 1];

        (GrammarId::new(open_id), GrammarId::new(close_id))
    }

    /// Get exclude grammar ID (if HAS_EXCLUDE flag set)
    #[inline]
    pub fn exclude(&self, id: GrammarId) -> Option<GrammarId> {
        let inst = self.inst(id);
        if inst.flags.has_exclude() {
            // Exclude ID is stored in aux_data
            let exclude_id = self.tables.get_aux(inst.first_child_idx + 1);
            Some(GrammarId::new(exclude_id))
        } else {
            None
        }
    }

    /// Access underlying tables (for advanced use)
    #[inline]
    pub fn tables(&self) -> &'a GrammarTables {
        self.tables
    }
}

/// Helper functions for common patterns
pub mod patterns {
    use super::*;

    /// Check if any child matches a predicate
    pub fn any_child<F>(ctx: &GrammarContext, id: GrammarId, mut predicate: F) -> bool
    where
        F: FnMut(GrammarId) -> bool,
    {
        ctx.children(id).any(|child| predicate(child))
    }

    /// Check if all children match a predicate
    pub fn all_children<F>(ctx: &GrammarContext, id: GrammarId, mut predicate: F) -> bool
    where
        F: FnMut(GrammarId) -> bool,
    {
        ctx.children(id).all(|child| predicate(child))
    }

    /// Find first child matching a predicate
    pub fn find_child<F>(ctx: &GrammarContext, id: GrammarId, mut predicate: F) -> Option<GrammarId>
    where
        F: FnMut(GrammarId) -> bool,
    {
        ctx.children(id).find(|&child| predicate(child))
    }

    /// Collect children matching a predicate
    pub fn filter_children<F>(
        ctx: &GrammarContext,
        id: GrammarId,
        mut predicate: F,
    ) -> Vec<GrammarId>
    where
        F: FnMut(GrammarId) -> bool,
    {
        ctx.children(id).filter(|&child| predicate(child)).collect()
    }

    /// Count children matching a predicate
    pub fn count_children<F>(ctx: &GrammarContext, id: GrammarId, mut predicate: F) -> usize
    where
        F: FnMut(GrammarId) -> bool,
    {
        ctx.children(id).filter(|&child| predicate(child)).count()
    }

    /// Check if instruction is a specific variant
    #[inline]
    pub fn is_variant(ctx: &GrammarContext, id: GrammarId, variant: GrammarVariant) -> bool {
        ctx.variant(id) == variant
    }

    /// Check if instruction is a Ref to a specific name
    pub fn is_ref_to(ctx: &GrammarContext, id: GrammarId, name: &str) -> bool {
        let inst = ctx.inst(id);
        if inst.variant != GrammarVariant::Ref {
            return false;
        }
        ctx.ref_name(id) == name
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grammar_inst::{GrammarFlags, ParseMode};
    use crate::grammar_tables::SimpleHintData;

    #[test]
    fn test_grammar_context() {
        static INSTRUCTIONS: &[GrammarInst] = &[
            GrammarInst::new(GrammarVariant::Sequence)
                .with_children(0, 2)
                .with_terminators(0, 1),
            GrammarInst::new(GrammarVariant::Ref).with_children(0, 0), // name_idx = 0
            GrammarInst::new(GrammarVariant::Token).with_children(1, 0), // type_idx = 1
        ];
        static CHILD_IDS: &[u32] = &[1, 2];
        static TERMINATORS: &[u32] = &[2];
        static STRINGS: &[&str] = &["SelectStatement", "keyword"];
        static AUX_DATA: &[u32] = &[];
        static REGEX_PATTERNS: &[&str] = &[];
        static SIMPLE_HINTS: &[SimpleHintData] = &[];

        let tables = GrammarTables::new(
            INSTRUCTIONS,
            CHILD_IDS,
            TERMINATORS,
            STRINGS,
            AUX_DATA,
            REGEX_PATTERNS,
            SIMPLE_HINTS,
        );

        let ctx = GrammarContext::new(&tables);

        let seq_id = GrammarId::new(0);
        assert_eq!(ctx.variant(seq_id), GrammarVariant::Sequence);
        assert_eq!(ctx.children_count(seq_id), 2);
        assert_eq!(ctx.terminators_count(seq_id), 1);

        let children: Vec<_> = ctx.children(seq_id).collect();
        assert_eq!(children, vec![GrammarId::new(1), GrammarId::new(2)]);

        let ref_id = GrammarId::new(1);
        assert_eq!(ctx.ref_name(ref_id), "SelectStatement");
    }

    #[test]
    fn test_pattern_helpers() {
        static INSTRUCTIONS: &[GrammarInst] = &[
            GrammarInst::new(GrammarVariant::Sequence).with_children(0, 3),
            GrammarInst::new(GrammarVariant::Ref),
            GrammarInst::new(GrammarVariant::Token),
            GrammarInst::new(GrammarVariant::Ref),
        ];
        static CHILD_IDS: &[u32] = &[1, 2, 3];
        static TERMINATORS: &[u32] = &[];
        static STRINGS: &[&str] = &[];
        static AUX_DATA: &[u32] = &[];
        static REGEX_PATTERNS: &[&str] = &[];
        static SIMPLE_HINTS: &[SimpleHintData] = &[];

        let tables = GrammarTables::new(
            INSTRUCTIONS,
            CHILD_IDS,
            TERMINATORS,
            STRINGS,
            AUX_DATA,
            REGEX_PATTERNS,
            SIMPLE_HINTS,
        );

        let ctx = GrammarContext::new(&tables);
        let seq_id = GrammarId::new(0);

        // Test any_child
        assert!(patterns::any_child(&ctx, seq_id, |id| {
            ctx.variant(id) == GrammarVariant::Token
        }));

        // Test all_children
        assert!(!patterns::all_children(&ctx, seq_id, |id| {
            ctx.variant(id) == GrammarVariant::Ref
        }));

        // Test count_children
        let ref_count =
            patterns::count_children(&ctx, seq_id, |id| ctx.variant(id) == GrammarVariant::Ref);
        assert_eq!(ref_count, 2);

        // Test find_child
        let token_child =
            patterns::find_child(&ctx, seq_id, |id| ctx.variant(id) == GrammarVariant::Token);
        assert_eq!(token_child, Some(GrammarId::new(2)));
    }
}
