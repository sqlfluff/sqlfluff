use crate::{
    parser::{Grammar, SegmentDef},
    Dialect,
};
use once_cell::sync::Lazy;

impl Dialect {
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static crate::parser::Grammar> {
        match name {
            // "SelectClauseElementSegment" => Some(&SELECT_CLAUSE_ELEMENT_GRAMMAR),
            // "SelectClauseModifierSegment" => Some(&SELECT_CLAUSE_MODIFIER_GRAMMAR),
            "CommaSegment" => Some(&COMMA_GRAMMAR),
            "SelectClauseSegment" => Some(&POSTGRES_SELECT_CLAUSE),
            "SelectClauseElementSegment" => Some(&SELECT_CLAUSE_ELEMENT_GRAMMAR),
            "SelectClauseModifierSegment" => Some(&Grammar::Empty),
            "Identifier" => Some(&Grammar::Empty),
            _ => None,
        }
    }
}

pub static ANSI_SELECT_CLAUSE: Lazy<SegmentDef> = Lazy::new(|| SegmentDef {
    name: "SelectClauseSegment",
    grammar: Grammar::Sequence {
        elements: vec![
            Grammar::Keyword {
                name: "SELECT",
                optional: false,
                allow_gaps: true,
            },
            Grammar::Ref {
                name: "SelectClauseModifierSegment",
                optional: true,
                allow_gaps: true,
            },
            Grammar::Delimited {
                elements: vec![Grammar::Ref {
                    name: "SelectClauseElementSegment",
                    optional: false,
                    allow_gaps: true,
                }],
                allow_trailing: true,
                optional: false,
                delimiter: Box::new(Grammar::Symbol(",")),
                terminators: vec![Grammar::Ref {
                    name: "SelectClauseTerminatorGrammar",
                    optional: false,
                    allow_gaps: true,
                }],
                allow_gaps: true,
            },
        ],
        optional: false,
        terminators: vec![],
        allow_gaps: true,
    },
});

// Simple placeholder grammar for SelectClauseElementSegment
pub static SELECT_CLAUSE_ELEMENT_GRAMMAR: Grammar = Grammar::Ref {
    name: "Identifier",
    optional: false,
    allow_gaps: true,
};

pub static COMMA_GRAMMAR: Grammar = Grammar::Symbol(",");

// Postgres-style SELECT clause
pub static POSTGRES_SELECT_CLAUSE: Lazy<Grammar> = Lazy::new(|| Grammar::Sequence {
    elements: vec![
        Grammar::Keyword {
            name: "SELECT",
            optional: false,
            allow_gaps: true,
        },
        Grammar::Ref {
            name: "SelectClauseModifierSegment",
            optional: true,
            allow_gaps: true,
        },
        Grammar::Delimited {
            elements: vec![Grammar::Ref {
                name: "SelectClauseElementSegment",
                optional: true,
                allow_gaps: true,
            }],
            delimiter: Box::new(Grammar::Ref {
                name: "CommaSegment",
                optional: false,
                allow_gaps: true,
            }),
            allow_trailing: true,
            optional: true,
            terminators: vec![],
            allow_gaps: true,
        },
    ],
    optional: false,
    terminators: vec![Grammar::Keyword {
        name: "FROM",
        optional: false,
        allow_gaps: true,
    }],
    allow_gaps: true,
});
