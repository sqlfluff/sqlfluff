pub mod config;
pub mod dialect;
pub mod lexer;
pub mod marker;
pub mod matcher;
pub mod regex;
pub mod slice;
pub mod templater;
pub mod token;
#[cfg(feature = "python")]
pub mod python;
// include!(concat!(env!("OUT_DIR"), "/dialect_matcher.rs"));

use crate::dialect::matcher::{Dialect, get_lexers};
