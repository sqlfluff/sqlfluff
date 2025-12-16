//! Table-Driven Grammar Instruction Format
//!
//! This module defines the compact instruction format for representing SQL grammars
//! in a table-driven parser. Instead of Arc<Grammar> trees, we use flat arrays of
//! GrammarInst structs indexed by u32 IDs.
//!
//! # Memory Comparison
//!
//! Current (Arc-based):
//! - Grammar enum: 376 bytes per variant
//! - 42,000 Arc allocations
//! - Total: 40-60 MB
//!
//! Proposed (Table-driven):
//! - GrammarInst struct: 20 bytes per instruction
//! - 0 allocations (static data)
//! - Total: ~1 MB
//!
//! # Design Goals
//!
//! 1. **Compact size**: Target ≤20 bytes per instruction
//! 2. **Zero allocations**: All data in static tables
//! 3. **Cache-friendly**: Contiguous memory access
//! 4. **Type-safe**: Newtype wrappers for indices

use std::fmt;

use crate::ParseMode;

/// Grammar instruction variant discriminant (1 byte)
///
/// Maps to Grammar enum variants. Using u8 instead of Rust enum
/// for explicit size control and easier serialization.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum GrammarVariant {
    Sequence = 0,
    AnyNumberOf = 1,
    OneOf = 2,
    AnySetOf = 3,
    Delimited = 4,
    Bracketed = 5,
    Ref = 6,
    StringParser = 7,
    MultiStringParser = 8,
    TypedParser = 9,
    RegexParser = 10,
    Meta = 11,
    NonCodeMatcher = 12,
    Nothing = 13,
    Anything = 14,
    Empty = 15,
    Missing = 16,
    Token = 17,
}

// /// Parse mode for grammar matching (1 byte)
// #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
// #[repr(u8)]
// pub enum ParseMode {
//     Strict = 0,
//     Greedy = 1,
//     GreedyOnceStarted = 2,
// }

/// Grammar flags packed into 16 bits
///
/// Common boolean flags extracted from Grammar enum variants.
/// Using bitflags for compact representation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct GrammarFlags(u16);

impl GrammarFlags {
    // Flag bit positions
    pub const OPTIONAL: u16 = 1 << 0;
    pub const RESET_TERMINATORS: u16 = 1 << 1;
    pub const ALLOW_GAPS: u16 = 1 << 2;
    pub const ALLOW_TRAILING: u16 = 1 << 3; // For Delimited
    pub const OPTIONAL_DELIMITER: u16 = 1 << 4; // For Delimited
    pub const HAS_SIMPLE_HINT: u16 = 1 << 5; // Whether simple_hint_idx is valid
    pub const HAS_EXCLUDE: u16 = 1 << 6; // Whether exclude_idx is valid
    pub const HAS_ANTI_TEMPLATE: u16 = 1 << 7; // For RegexParser
    pub const IS_CONDITIONAL: u16 = 1 << 8; // For Meta - whether it's a Conditional Meta
                                            // Bits 9-15 reserved for future use

    /// Create empty flags
    #[inline]
    pub const fn empty() -> Self {
        Self(0)
    }

    /// Create flags from raw bits
    #[inline]
    pub const fn from_bits(bits: u16) -> Self {
        Self(bits)
    }

    /// Get raw bits
    #[inline]
    pub const fn bits(self) -> u16 {
        self.0
    }

    /// Check if a flag is set
    #[inline]
    pub const fn has(self, flag: u16) -> bool {
        (self.0 & flag) != 0
    }

    /// Set a flag
    #[inline]
    pub const fn with(self, flag: u16) -> Self {
        Self(self.0 | flag)
    }

    /// Clear a flag
    #[inline]
    pub const fn without(self, flag: u16) -> Self {
        Self(self.0 & !flag)
    }

    // Convenience methods for common flags
    #[inline]
    pub const fn optional(self) -> bool {
        self.has(Self::OPTIONAL)
    }

    #[inline]
    pub const fn reset_terminators(self) -> bool {
        self.has(Self::RESET_TERMINATORS)
    }

    #[inline]
    pub const fn allow_gaps(self) -> bool {
        self.has(Self::ALLOW_GAPS)
    }

    #[inline]
    pub const fn allow_trailing(self) -> bool {
        self.has(Self::ALLOW_TRAILING)
    }

    #[inline]
    pub const fn optional_delimiter(self) -> bool {
        self.has(Self::OPTIONAL_DELIMITER)
    }

    #[inline]
    pub const fn has_simple_hint(self) -> bool {
        self.has(Self::HAS_SIMPLE_HINT)
    }

    #[inline]
    pub const fn has_exclude(self) -> bool {
        self.has(Self::HAS_EXCLUDE)
    }

    #[inline]
    pub const fn has_anti_template(self) -> bool {
        self.has(Self::HAS_ANTI_TEMPLATE)
    }

    #[inline]
    pub const fn is_conditional(self) -> bool {
        self.has(Self::IS_CONDITIONAL)
    }
}

/// Compact grammar instruction (20 bytes)
///
/// Replaces Arc<Grammar> with a flat, indexable structure.
/// All fields carefully packed to minimize size while maintaining alignment.
///
/// # Memory Layout (20 bytes total)
///
/// ```text
/// Offset  Size  Field
/// ------  ----  -----
/// 0       1     variant: GrammarVariant (u8)
/// 1       1     parse_mode: ParseMode (u8)
/// 2       2     flags: GrammarFlags (u16)
/// 4       4     first_child_idx: u32
/// 8       2     child_count: u16
/// 10      2     min_times: u16 (for AnyNumberOf/AnySetOf)
/// 12      4     first_terminator_idx: u32
/// 16      2     terminator_count: u16
/// 18      2     _padding: u16 (reserved)
/// ------  ----
/// Total:  20 bytes
/// ```
///
/// # Variant-Specific Data Packing
///
/// Different grammar variants reuse fields for their specific needs:
///
/// **Sequence, OneOf, AnyNumberOf, AnySetOf, Delimited, Bracketed**:
/// - Use `first_child_idx` + `child_count` for children
/// - Use `first_terminator_idx` + `terminator_count` for terminators
///
/// **AnyNumberOf, AnySetOf**:
/// - Use `min_times` field
/// - Use `max_times_idx` (stored in auxiliary table, indexed via first_child_idx)
///
/// **Delimited**:
/// - Use `delimiter_idx` (stored in auxiliary table)
/// - Use `min_delimiters` field (reuse min_times)
///
/// **Bracketed**:
/// - Use `bracket_pair_idx` (stored in auxiliary table, 2 consecutive u32s)
///
/// **Ref**:
/// - Use `name_idx` (stored in STRING_TABLE, indexed via first_child_idx)
/// - Use `exclude_idx` if HAS_EXCLUDE flag set
///
/// **StringParser, MultiStringParser, TypedParser**:
/// - Use `template_idx` (STRING_TABLE index via first_child_idx)
/// - For MultiStringParser: use child_count for template count
///
/// **RegexParser**:
/// - Use `regex_idx` (stored in auxiliary REGEX_TABLE)
/// - Use `anti_regex_idx` if HAS_ANTI_TEMPLATE flag set
///
/// **Token, Meta**:
/// - Use `name_idx` (STRING_TABLE index)
///
#[derive(Debug, Clone, Copy)]
#[repr(C)] // Explicit layout for predictable packing
pub struct GrammarInst {
    /// Grammar variant discriminant
    pub variant: GrammarVariant,

    /// Parse mode (Strict or Greedy)
    pub parse_mode: ParseMode,

    /// Packed boolean flags
    pub flags: GrammarFlags,

    /// Index into CHILD_IDS table (or other meaning depending on variant)
    ///
    /// Used for:
    /// - Children start index (Sequence, OneOf, etc.)
    /// - Ref name index (Ref)
    /// - Template index (StringParser, etc.)
    /// - Regex index (RegexParser)
    pub first_child_idx: u32,

    /// Number of children (or other meaning depending on variant)
    ///
    /// Used for:
    /// - Children count (Sequence, OneOf, etc.)
    /// - Template count (MultiStringParser)
    pub child_count: u16,

    /// Minimum repetitions (AnyNumberOf, AnySetOf) or min_delimiters (Delimited)
    pub min_times: u16,

    /// Index into TERMINATORS table
    pub first_terminator_idx: u32,

    /// Number of terminators
    pub terminator_count: u16,

    /// Reserved for future use (maintains 4-byte alignment)
    pub _padding: u16,
}

// Compile-time size assertion
const _: () = assert!(std::mem::size_of::<GrammarInst>() == 20);

impl GrammarInst {
    /// Create a new instruction with default values
    pub const fn new(variant: GrammarVariant) -> Self {
        Self {
            variant,
            parse_mode: ParseMode::Strict,
            flags: GrammarFlags::empty(),
            first_child_idx: 0,
            child_count: 0,
            min_times: 0,
            first_terminator_idx: 0,
            terminator_count: 0,
            _padding: 0,
        }
    }

    /// Builder pattern: set parse mode
    #[inline]
    pub const fn with_parse_mode(mut self, mode: ParseMode) -> Self {
        self.parse_mode = mode;
        self
    }

    /// Builder pattern: set flags
    #[inline]
    pub const fn with_flags(mut self, flags: GrammarFlags) -> Self {
        self.flags = flags;
        self
    }

    /// Builder pattern: set children range
    #[inline]
    pub const fn with_children(mut self, start_idx: u32, count: u16) -> Self {
        self.first_child_idx = start_idx;
        self.child_count = count;
        self
    }

    /// Builder pattern: set terminators range
    #[inline]
    pub const fn with_terminators(mut self, start_idx: u32, count: u16) -> Self {
        self.first_terminator_idx = start_idx;
        self.terminator_count = count;
        self
    }

    /// Builder pattern: set min_times
    #[inline]
    pub const fn with_min_times(mut self, min: u16) -> Self {
        self.min_times = min;
        self
    }

    /// Get child IDs slice from CHILD_IDS table
    #[inline]
    pub fn children<'a>(&self, child_ids: &'a [u32]) -> &'a [u32] {
        let start = self.first_child_idx as usize;
        let end = start + self.child_count as usize;
        &child_ids[start..end]
    }

    /// Get terminator IDs slice from TERMINATORS table
    #[inline]
    pub fn terminators<'a>(&self, terminators: &'a [u32]) -> &'a [u32] {
        let start = self.first_terminator_idx as usize;
        let end = start + self.terminator_count as usize;
        &terminators[start..end]
    }

    /// Check if this instruction is optional
    #[inline]
    pub fn is_optional(&self) -> bool {
        // For AnyNumberOf/AnySetOf, also check min_times == 0
        if matches!(
            self.variant,
            GrammarVariant::AnyNumberOf | GrammarVariant::AnySetOf
        ) {
            return self.flags.optional() || self.min_times == 0;
        }
        self.flags.optional()
    }
}

impl fmt::Display for GrammarInst {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self.variant)?;
        if self.flags.optional() {
            write!(f, "?")?;
        }
        if self.child_count > 0 {
            write!(f, "[{}]", self.child_count)?;
        }
        Ok(())
    }
}

/// Newtype wrapper for grammar instruction IDs
///
/// Provides type safety when indexing into GRAMMAR_TABLE.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct GrammarId(pub u32);

impl GrammarId {
    pub const NONCODE: GrammarId = GrammarId(u32::MAX - 1); // Use a reserved value for NONCODE

    /// Create a new GrammarId
    #[inline]
    pub const fn new(id: u32) -> Self {
        Self(id)
    }

    /// Get the underlying u32 value
    #[inline]
    pub const fn get(self) -> u32 {
        self.0
    }

    /// Convenience: get instruction from GRAMMAR_TABLE
    #[inline]
    pub fn inst<'a>(self, grammar_table: &'a [GrammarInst]) -> &'a GrammarInst {
        &grammar_table[self.0 as usize]
    }
}

impl From<u32> for GrammarId {
    #[inline]
    fn from(id: u32) -> Self {
        Self(id)
    }
}

impl From<GrammarId> for u32 {
    #[inline]
    fn from(id: GrammarId) -> Self {
        id.0
    }
}

impl fmt::Display for GrammarId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "G{}", self.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_grammar_inst_size() {
        // Verify size is exactly 20 bytes
        assert_eq!(std::mem::size_of::<GrammarInst>(), 20);
        assert_eq!(std::mem::align_of::<GrammarInst>(), 4);
    }

    #[test]
    fn test_grammar_variant_size() {
        assert_eq!(std::mem::size_of::<GrammarVariant>(), 1);
    }

    #[test]
    fn test_parse_mode_size() {
        assert_eq!(std::mem::size_of::<ParseMode>(), 1);
    }

    #[test]
    fn test_grammar_flags_size() {
        assert_eq!(std::mem::size_of::<GrammarFlags>(), 2);
    }

    #[test]
    fn test_flags_operations() {
        let flags = GrammarFlags::empty()
            .with(GrammarFlags::OPTIONAL)
            .with(GrammarFlags::ALLOW_GAPS);

        assert!(flags.optional());
        assert!(flags.allow_gaps());
        assert!(!flags.reset_terminators());

        let flags = flags.without(GrammarFlags::OPTIONAL);
        assert!(!flags.optional());
        assert!(flags.allow_gaps());
    }

    #[test]
    fn test_builder_pattern() {
        let inst = GrammarInst::new(GrammarVariant::Sequence)
            .with_parse_mode(ParseMode::Greedy)
            .with_flags(GrammarFlags::empty().with(GrammarFlags::OPTIONAL))
            .with_children(10, 5)
            .with_terminators(20, 2);

        assert_eq!(inst.variant, GrammarVariant::Sequence);
        assert_eq!(inst.parse_mode, ParseMode::Greedy);
        assert!(inst.flags.optional());
        assert_eq!(inst.first_child_idx, 10);
        assert_eq!(inst.child_count, 5);
        assert_eq!(inst.first_terminator_idx, 20);
        assert_eq!(inst.terminator_count, 2);
    }

    #[test]
    fn test_children_slice() {
        let inst = GrammarInst::new(GrammarVariant::OneOf).with_children(5, 3);

        let child_ids = vec![0, 1, 2, 3, 4, 10, 11, 12, 13, 14];
        let children = inst.children(&child_ids);

        assert_eq!(children, &[10, 11, 12]);
    }

    #[test]
    fn test_is_optional() {
        // Regular optional flag
        let inst = GrammarInst::new(GrammarVariant::Sequence)
            .with_flags(GrammarFlags::empty().with(GrammarFlags::OPTIONAL));
        assert!(inst.is_optional());

        // AnyNumberOf with min_times = 0
        let inst = GrammarInst::new(GrammarVariant::AnyNumberOf).with_min_times(0);
        assert!(inst.is_optional());

        // AnyNumberOf with min_times = 1
        let inst = GrammarInst::new(GrammarVariant::AnyNumberOf).with_min_times(1);
        assert!(!inst.is_optional());
    }

    #[test]
    fn test_grammar_id() {
        let id = GrammarId::new(42);
        assert_eq!(id.get(), 42);
        assert_eq!(u32::from(id), 42);
        assert_eq!(format!("{}", id), "G42");
    }
}
