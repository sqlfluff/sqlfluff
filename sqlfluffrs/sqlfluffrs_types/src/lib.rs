pub mod config;
pub mod grammar_api;
pub mod grammar_inst;
pub mod grammar_tables;
pub mod identity;
pub mod marker;
pub mod matcher;
pub mod parser;
pub mod regex;
pub mod slice;
pub mod string;
pub mod templater;
pub mod token;
pub use config::fluffconfig::FluffConfig;
pub use grammar_api::{patterns as grammar_patterns, GrammarContext};
pub use grammar_inst::{GrammarFlags, GrammarId, GrammarInst, GrammarVariant};
pub use grammar_tables::{
    ChildrenIter, GrammarInstExt, GrammarTables, SimpleHintData, TableMemoryStats, TerminatorsIter,
};
pub use marker::PositionMarker;
pub use matcher::{BracketPairEntry, BracketPairSet, LexMatcher, LexMatcherConfig};
pub use parser::{ParseMode, RootGrammar, SimpleHint};
pub use regex::{RegexMode, RegexModeGroup};
pub use slice::Slice;
pub use templater::fileslice::{RawFileSlice, TemplatedFileSlice};
pub use templater::templatefile::TemplatedFile;
pub use token::{config::TokenConfig, Token};

/// Install the stderr `env_logger` backend (default level `warn`, overridable
/// via `RUST_LOG`) for `log` records from all crates. Every entry point
/// (Python module, binaries, examples) should call this; repeat calls are no-ops.
pub fn init_logging() {
    let env = env_logger::Env::default().filter_or("RUST_LOG", "warn");
    let _ = env_logger::Builder::from_env(env).try_init();
}
