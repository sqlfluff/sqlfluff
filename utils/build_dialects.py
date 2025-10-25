"""For autogenerating rust dialects."""

from sqlfluff.core.dialects import dialect_readout


def generate_use():
    """Generates the `use` statements."""
    print()
    print("/* dialect mods */")
    for dialect in dialect_readout():
        print(f"pub mod {dialect.label.lower()};")
        print(
            f"use crate::dialect::{dialect.label.lower()}::matcher::{{"
            f"{dialect.label.upper()}_KEYWORDS, "
            f"{dialect.label.upper()}_LEXERS}};"
        )
    print()
    print("use crate::matcher::LexMatcher;")
    print("use std::str::FromStr;")


def generate_dialect_enum():
    """Generate the dialect enum and associated functions."""
    dialects = ",\n    ".join(
        [dialect.label.capitalize() for dialect in dialect_readout()]
    )
    dialect_match = ",\n            ".join(
        [
            f"Dialect::{d.label.capitalize()} => &{d.label.upper()}_LEXERS"
            for d in dialect_readout()
        ]
    )
    dialect_reserved_keywords = ",\n            ".join(
        [
            f"Dialect::{d.label.capitalize()} => &{d.label.upper()}_KEYWORDS"
            for d in dialect_readout()
        ]
    )
    dialect_strings = ",\n            ".join(
        [
            f'"{d.label}" => Ok(Dialect::{d.label.capitalize()})'
            for d in dialect_readout()
        ]
    )
    print(
        f"""
#[derive(Debug, Eq, PartialEq, Hash, Copy, Clone)]
pub enum Dialect {{
    {dialects},
}}

impl Dialect {{
    pub(crate) fn get_reserved_keywords(&self) -> &'static Vec<String> {{
        match self {{
            {dialect_reserved_keywords},
        }}
    }}

    pub fn get_lexers(&self) -> &'static Vec<LexMatcher> {{
        match self {{
            {dialect_match},
        }}
    }}
}}

impl FromStr for Dialect {{
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {{
        match s {{
            {dialect_strings},
            _ => Err(()),
        }}
    }}
}}"""
    )


if __name__ == "__main__":
    print("/* This is a generated file! */")
    print()
    generate_use()
    generate_dialect_enum()
