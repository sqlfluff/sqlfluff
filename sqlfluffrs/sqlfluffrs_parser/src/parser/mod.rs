//! Iterative parser implementation for SQLFluff
//!
//! This module contains an iterative (non-recursive) parser that uses an
//! explicit stack of frames to parse SQL grammar without stack overflow risks.

#[macro_use]
mod macros;
pub(crate) mod types;
mod frame;
mod cache;
mod core;
#[macro_use]
mod handlers;
mod helpers;  // Utility methods for Parser
mod iterative;
mod utils;

// Re-export public types
pub use types::{Node, ParseError, SegmentDef, ParseErrorType, ParseContext};
pub use core::Parser;
pub use sqlfluffrs_types::{Grammar, ParseMode};

// Internal re-exports for submodules
pub(crate) use frame::{ParseFrame, FrameState, FrameContext, BracketedState, DelimitedState};
