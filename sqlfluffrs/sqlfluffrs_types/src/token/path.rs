use super::Token;
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct PathStep {
    pub segment: Arc<Token>,
    pub idx: usize,
    pub len: usize,
    pub code_idxs: Vec<usize>,
}
