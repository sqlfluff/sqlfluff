use crate::slice::Slice;

#[derive(Debug, Clone, Hash)]
pub struct SourceFix {
    edit: String,
    source_slice: Slice,
    templated_slice: Slice,
}

impl PartialEq for SourceFix {
    fn eq(&self, other: &Self) -> bool {
        self.edit == other.edit && self.source_slice == other.source_slice
    }
}
