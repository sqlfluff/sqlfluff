use serde::{Deserialize, Serialize};

use crate::slice::Slice;

#[derive(Debug, PartialEq, Clone, Hash, Serialize, Deserialize)]
pub struct RawFileSlice {
    pub raw: String, // Source string
    pub slice_type: String,
    pub source_idx: usize, // Offset from beginning of source string
    // Block index, incremented on start or end block tags, e.g. "if", "for".
    // This is used in `BaseRule.discard_unsafe_fixes()` to reject any fixes
    // which span multiple templated blocks.
    pub block_idx: usize,
    // The command of a templated tag, e.g. "if", "for"
    // This is used in template tracing as a kind of cache to identify the kind
    // of template element this is without having to re-extract it each time.
    pub tag: Option<String>,
}

impl RawFileSlice {
    pub fn new(
        raw: String,
        slice_type: String,
        source_idx: usize,
        block_idx: Option<usize>,
        tag: Option<String>,
    ) -> Self {
        RawFileSlice {
            raw,
            slice_type,
            source_idx,
            block_idx: block_idx.unwrap_or_default(),
            tag,
        }
    }

    pub fn end_source_idx(&self) -> usize {
        // Return the closing index of this slice.
        let len: usize = self.raw.chars().count();
        self.source_idx + len
    }

    pub fn source_slice(&self) -> Slice {
        Slice::from(self.source_idx..self.end_source_idx())
    }

    pub fn is_source_only_slice(&self) -> bool {
        // Based on its slice_type, does it only appear in the *source*?
        // There are some slice types which are automatically source only.
        // There are *also* some which are source only because they render
        // to an empty string.
        // TODO: should any new logic go here?
        matches!(
            self.slice_type.as_str(),
            "comment" | "block_end" | "block_start" | "block_mid"
        )
    }
}

#[derive(Debug, PartialEq, Clone, Hash, Serialize, Deserialize)]
pub struct TemplatedFileSlice {
    pub slice_type: String,
    pub source_codepoint_slice: Slice,
    pub templated_codepoint_slice: Slice,
}

impl TemplatedFileSlice {
    pub fn new(
        slice_type: String,
        source_codepoint_slice: Slice,
        templated_codepoint_slice: Slice,
    ) -> Self {
        TemplatedFileSlice {
            slice_type,
            source_codepoint_slice,
            templated_codepoint_slice,
        }
    }
}
