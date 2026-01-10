//! Iterative parser implementation for SQLFluff
//!
//! This module contains an iterative (non-recursive) parser that uses an
//! explicit stack of frames to parse SQL grammar without stack overflow risks.

/// Verbose debug logging macro - only compiles logging code when verbose-debug feature is enabled.
/// This eliminates runtime overhead of debug logging in production builds.
#[macro_export]
macro_rules! vdebug {
    ($($arg:tt)*) => {
        #[cfg(feature = "verbose-debug")]
        log::debug!($($arg)*);
    };
}

mod cache;
mod core;
mod frame;
mod helpers; // Utility methods for Parser
mod match_result;
mod table_driven;
pub(crate) mod types;

#[cfg(feature = "python")]
pub mod python;

// Re-export public types
pub use core::Parser;
pub use match_result::{MatchResult, MetaSegmentType, TransparentInsert, TransparentType};
pub use sqlfluffrs_types::ParseMode;
pub use types::{Node, ParseError, ParseErrorType};

// Internal re-exports for submodules
pub(crate) use frame::{BracketedState, DelimitedState, FrameContext, FrameState};

// Re-export Python bindings when feature is enabled
#[cfg(feature = "python")]
pub use python::{PyMatchResult, PyNode, PyParseError, PyParser, RsParseError};
