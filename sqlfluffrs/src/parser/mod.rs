//! Iterative parser implementation for SQLFluff
//!
//! This module contains an iterative (non-recursive) parser that uses an
//! explicit stack of frames to parse SQL grammar without stack overflow risks.

#[macro_use]
mod macros;
mod types;
mod frame;
mod core;
mod iterative;
pub(crate) mod utils;  // Make utils accessible to parser_old

// Re-export public types
pub use types::{Grammar, ParseMode, Node, ParseError, SegmentDef, Parsed, ParseErrorType, ParseContext};
pub use core::Parser;

// Internal re-exports for submodules
pub(crate) use frame::{ParseFrame, FrameState, FrameContext, BracketedState, DelimitedState};
