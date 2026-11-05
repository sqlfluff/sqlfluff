use std::{fmt::Display, ops::Range};

use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Hash, Eq, Clone, Copy, Serialize, Deserialize)]
pub struct Slice {
    pub start: usize,
    pub stop: usize,
}

impl From<Range<usize>> for Slice {
    fn from(value: Range<usize>) -> Self {
        Self {
            start: value.start,
            stop: value.end,
        }
    }
}

impl Slice {
    pub fn slice_is_point(test_slice: &Range<usize>) -> bool {
        test_slice.start == test_slice.end
    }

    pub fn len(&self) -> usize {
        self.stop - self.start
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

impl Display for Slice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "slice({}, {}, None)", self.start, self.stop)
    }
}
