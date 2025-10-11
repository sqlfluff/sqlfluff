pub mod config;
pub mod dialect;
pub mod lexer;
pub mod marker;
pub mod matcher;
#[cfg(feature = "python")]
pub mod python;
pub mod regex;
pub mod slice;
pub mod templater;
pub mod token;
// include!(concat!(env!("OUT_DIR"), "/dialect_matcher.rs"));

use crate::dialect::Dialect;
