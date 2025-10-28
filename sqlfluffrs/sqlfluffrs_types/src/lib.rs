pub mod config;
pub mod marker;
// pub mod matcher;
pub mod parser;
pub mod regex;
pub mod slice;
pub mod templater;
pub mod token;

pub use config::fluffconfig::FluffConfig;
// pub use matcher::LexMatcher;
pub use marker::PositionMarker;
pub use parser::{Grammar, ParseMode, SimpleHint};
pub use regex::{RegexMode, RegexModeGroup};
pub use slice::Slice;
pub use templater::fileslice::{RawFileSlice, TemplatedFileSlice};
pub use templater::templatefile::TemplatedFile;
pub use token::{Token, config::TokenConfig};
