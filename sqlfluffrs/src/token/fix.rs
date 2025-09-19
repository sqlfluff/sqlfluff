use crate::slice::Slice;

#[derive(Debug, Clone)]
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

impl std::hash::Hash for SourceFix {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.edit.hash(state);
        self.source_slice.hash(state);
    }
}
