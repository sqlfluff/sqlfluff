pub mod config;
pub mod grammar_api;
pub mod grammar_inst;
pub mod grammar_tables;
pub mod marker;
pub mod matcher;
pub mod parser;
pub mod regex;
pub mod slice;
pub mod templater;
pub mod token;

#[cfg(test)]
mod grammar_tables_test;

#[cfg(feature = "python")]
pub use config::fluffconfig::python::PyFluffConfig;
pub use config::fluffconfig::FluffConfig;
pub use grammar_api::{patterns as grammar_patterns, GrammarContext};
pub use grammar_inst::{
    GrammarFlags, GrammarId, GrammarInst, GrammarVariant,
};
pub use grammar_tables::{
    ChildrenIter, GrammarInstExt, GrammarTables, SimpleHintData, TableMemoryStats, TerminatorsIter,
};
#[cfg(feature = "python")]
pub use marker::python::PyPositionMarker;
pub use marker::PositionMarker;
pub use matcher::LexMatcher;
pub use parser::{Grammar, ParseMode, RootGrammar, SimpleHint};
pub use regex::{RegexMode, RegexModeGroup};
pub use slice::Slice;
#[cfg(feature = "python")]
pub use templater::fileslice::python::{PyRawFileSlice, PyTemplatedFileSlice};
pub use templater::fileslice::{RawFileSlice, TemplatedFileSlice};
#[cfg(feature = "python")]
pub use templater::templatefile::python::PyTemplatedFile;
pub use templater::templatefile::TemplatedFile;
#[cfg(feature = "python")]
pub use token::python::PyToken;
pub use token::{config::TokenConfig, Token};
