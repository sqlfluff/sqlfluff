pub(crate) mod lexer;

#[cfg(feature = "python")]
pub use lexer::python::{PyLexer, PySQLLexError};
pub use lexer::{LexInput, Lexer, TemplateElement};
