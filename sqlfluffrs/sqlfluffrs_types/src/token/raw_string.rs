#[derive(Debug, Clone)]
pub struct RawString {
    raw: String,
    raw_upper: String,
}

impl RawString {
    pub fn new(raw: String) -> Self {
        let raw_upper = raw.to_uppercase();
        Self { raw, raw_upper }
    }

    pub fn as_str(&self) -> &str {
        &self.raw
    }

    pub fn upper(&self) -> &str {
        &self.raw_upper
    }
}
