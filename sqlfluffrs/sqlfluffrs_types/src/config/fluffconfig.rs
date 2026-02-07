#[derive(Clone)]
pub struct FluffConfig {
    pub dialect: Option<String>,
    pub template_blocks_indent: bool,
}

impl FluffConfig {
    pub fn new(dialect: Option<String>, template_blocks_indent: bool) -> Self {
        Self {
            dialect,
            template_blocks_indent,
        }
    }
}
