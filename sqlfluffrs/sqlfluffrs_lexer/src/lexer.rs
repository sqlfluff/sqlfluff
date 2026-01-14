use std::sync::Arc;

use log::debug;

use sqlfluffrs_types::{
    marker::PositionMarker,
    matcher::{LexMatcher, LexedElement},
    slice::Slice,
    templater::{fileslice::TemplatedFileSlice, templatefile::TemplatedFile},
    token::{CaseFold, Token},
};

use hashbrown::{HashMap, HashSet};

use std::{
    fmt::Display,
    ops::{Bound, RangeBounds},
};

use uuid::Uuid;

use itertools::multipeek;

pub struct BlockTracker {
    stack: Vec<Uuid>,
    map: HashMap<Slice, Uuid>,
}

impl Default for BlockTracker {
    fn default() -> Self {
        Self::new()
    }
}

impl BlockTracker {
    /// Create a new `BlockTracker`.
    pub fn new() -> Self {
        Self {
            stack: Vec::new(),
            map: HashMap::new(),
        }
    }

    /// Enter a block given a source slice (start, end).
    pub fn enter(&mut self, src_slice: Slice) {
        let uuid = *self.map.entry(src_slice).or_insert_with(Uuid::new_v4);

        log::debug!(
            "       Entering block stack @ {:?}: {} ({})",
            src_slice,
            uuid,
            if self.map.contains_key(&src_slice) {
                "cached"
            } else {
                "fresh"
            }
        );

        self.stack.push(uuid);
    }

    /// Exit the current block, removing it from the stack.
    pub fn exit(&mut self) {
        if let Some(uuid) = self.stack.pop() {
            log::debug!("       Exiting block stack: {}", uuid);
        } else {
            log::warn!("Attempted to exit an empty block stack!");
        }
    }

    /// Get the `Uuid` on top of the stack.
    ///
    /// # Panics
    /// This method panics if the stack is empty.
    pub fn top(&self) -> Uuid {
        *self
            .stack
            .last()
            .expect("Block stack is empty. Cannot get the top block.")
    }
}

#[derive(Debug)]
pub struct TemplateElement {
    pub raw: String,
    pub template_slice: Slice, // Slice equivalent
    pub matcher: LexMatcher,   // Reference to the lexer that matched this element
}

impl Display for TemplateElement {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "TemplatedElement(raw='{:?}', template_slice={}, matcher={})",
            self.raw, self.template_slice, self.matcher
        )
    }
}

impl TemplateElement {
    // Constructor to create a TemplateElement from a LexedElement and a template slice
    pub fn from_element(element: &LexedElement, template_slice: Slice) -> Self {
        Self {
            raw: element.raw.to_string(),
            template_slice,
            matcher: element.matcher.clone(),
        }
    }

    // Method to convert the TemplateElement to a RawSegment
    pub fn to_token<R>(&self, pos_marker: PositionMarker, subslice: Option<R>) -> Token
    where
        R: RangeBounds<usize>,
    {
        let raw_subslice = match subslice {
            Some(range) => {
                let start = match range.start_bound() {
                    Bound::Included(&start) => start,
                    Bound::Excluded(&start) => start + 1,
                    Bound::Unbounded => 0,
                };

                let end = match range.end_bound() {
                    Bound::Included(&end) => end + 1,
                    Bound::Excluded(&end) => end,
                    Bound::Unbounded => self.raw.len(),
                };

                &self.raw[start..end]
            }
            None => &self.raw,
        };
        self.matcher.construct_token(raw_subslice, pos_marker)
    }
}

#[derive(Debug, Clone)]
pub struct SQLLexError {
    pub description: Option<String>,
    pub line_no: usize,
    pub line_pos: usize,
    pub ignore: bool,
    pub warning: bool,
    pub fatal: bool,
    #[cfg(feature = "python")]
    code: Option<String>,
    #[cfg(feature = "python")]
    name: Option<String>,
    #[cfg(feature = "python")]
    identifier: String,
}

impl SQLLexError {
    fn new(
        msg: Option<String>,
        pos: Option<PositionMarker>,
        line_no: Option<usize>,
        line_pos: Option<usize>,
        ignore: Option<bool>,
        fatal: Option<bool>,
        warning: Option<bool>,
    ) -> Self {
        Self {
            description: msg,
            line_no: pos.as_ref().map(|pm| pm.line_no()).or(line_no).unwrap_or(0),
            line_pos: pos
                .as_ref()
                .map(|pm| pm.line_pos())
                .or(line_pos)
                .unwrap_or(0),
            ignore: ignore.unwrap_or(false),
            warning: warning.unwrap_or(false),
            fatal: fatal.unwrap_or(false),
            #[cfg(feature = "python")]
            code: Some("LXR".to_string()),
            #[cfg(feature = "python")]
            name: None,
            #[cfg(feature = "python")]
            identifier: "lexing".to_string(),
        }
    }

    #[cfg(feature = "python")]
    fn source_signature(&self) -> ((String, usize, usize), String) {
        (
            self.check_tuple(),
            self.description
                .clone()
                .unwrap_or_else(|| "No description".to_string()),
        )
    }

    #[cfg(feature = "python")]
    fn check_tuple(&self) -> (String, usize, usize) {
        (self.rule_code(), self.line_no, self.line_pos)
    }

    #[cfg(feature = "python")]
    fn rule_code(&self) -> String {
        self.code.clone().unwrap_or("????".to_string())
    }

    #[cfg(feature = "python")]
    fn rule_name(&self) -> String {
        self.name.clone().unwrap_or("????".to_string())
    }

    #[cfg(feature = "python")]
    fn ignore_if_in(&mut self, ignore_iterable: &[String]) {
        self.ignore = ignore_iterable.contains(&self.identifier);
    }

    #[cfg(feature = "python")]
    fn warning_if_in(&mut self, warning_iterable: &[String]) {
        self.warning = warning_iterable.contains(&self.rule_code())
            || warning_iterable.contains(&self.rule_name());
    }
}

#[derive(Clone)]
pub struct Lexer {
    last_resort_lexer: LexMatcher,
    matchers: Vec<LexMatcher>,
}

impl Lexer {
    pub fn new(last_resort_lexer: Option<LexMatcher>, matchers: Vec<LexMatcher>) -> Self {
        let last_resort_lexer = last_resort_lexer.unwrap_or_else(|| {
            LexMatcher::regex_lexer(
                // dialect,
                "<unlexable>",
                r#"[^\t\n\ ]*"#,
                Token::unlexable_token_compat,
                None,
                None,
                None,
                None,
                None,
                None,
                CaseFold::None,
                None,
                |_| true,
                None,
            )
        });
        Self {
            last_resort_lexer,
            matchers,
        }
    }

    pub fn lex_string<'a>(&'a self, mut input: &'a str) -> Vec<LexedElement<'a>> {
        let mut element_buffer = Vec::with_capacity(input.len());

        while !input.is_empty() {
            if let Some((elements, match_length)) = self
                .lex_match(input)
                .or_else(|| self.last_resort_lexer.scan_match(input))
            {
                element_buffer.extend(elements);
                input = &input[match_length..];
            } else {
                panic!(
                    "Fatal. Unable to lex characters: {}",
                    &input[..input.chars().take(10).count()]
                );
            };
        }

        element_buffer
    }

    pub fn lex_match<'a>(&'a self, input: &'a str) -> Option<(Vec<LexedElement<'a>>, usize)> {
        self.matchers
            .iter()
            .find_map(|matcher| matcher.scan_match(input))
    }

    fn map_template_slices(
        &self,
        elements: &[LexedElement],
        template: &TemplatedFile,
    ) -> Vec<TemplateElement> {
        let mut idx = 0;
        let mut templated_buff = Vec::new();

        for element in elements {
            let element_len = element.raw.chars().count();
            let template_slice = Slice::from(idx..idx + element_len);
            idx += element_len;

            // Create a TemplateElement from the LexedElement and the template slice
            let templated_element = TemplateElement::from_element(element, template_slice);
            templated_buff.push(templated_element);

            // // Validate that the slice matches the element's raw content
            let templated_substr: String = template
                .templated_str
                .chars()
                .skip(template_slice.start)
                .take(template_slice.len())
                .collect();

            if *templated_substr != *element.raw {
                panic!(
                    "Template and lexed elements do not match. This should never happen  {:?} != {:?}",
                    &element.raw, &templated_substr
                )
            }
        }

        templated_buff
    }

    fn elements_to_tokens(
        &self,
        elements: &[TemplateElement],
        templated_file: &Arc<TemplatedFile>,
        template_blocks_indent: bool,
    ) -> Vec<Token> {
        log::info!("Elements to Segments.");

        // Convert elements into segments using an iterator
        let mut segment_buffer: Vec<Token> =
            iter_tokens(elements, templated_file, template_blocks_indent);

        // Add an EndOfFile marker
        let eof_marker = if let Some(last_segment) = segment_buffer.last() {
            Token::end_of_file_token(
                last_segment
                    .pos_marker
                    .clone()
                    .expect("PositionMarker unset")
                    .end_point_marker(),
                false,
                None,
                HashSet::new(),
            )
        } else {
            Token::end_of_file_token(
                PositionMarker::from_point(0, 0, templated_file, None, None),
                false,
                None,
                HashSet::new(),
            )
        };
        segment_buffer.push(eof_marker);

        segment_buffer
    }

    pub fn lex(
        &self,
        raw: LexInput,
        template_blocks_indent: bool,
    ) -> (Vec<Token>, Vec<SQLLexError>) {
        let (template, str_buff) = match raw {
            LexInput::String(raw_str) => {
                let template = TemplatedFile::from(raw_str.clone());
                (Arc::new(template), raw_str)
            }
            LexInput::TemplatedFile(template_file) => {
                let str_buff = template_file.to_string();
                (template_file, str_buff)
            }
        };

        let lexed_elements = self.lex_string(&str_buff);
        let templated_buffer = self.map_template_slices(&lexed_elements, &template);
        let mut tokens =
            self.elements_to_tokens(&templated_buffer, &template, template_blocks_indent);

        // OPTIMIZATION: Pre-compute bracket pairs for O(1) lookup during parsing
        Self::compute_bracket_pairs(&mut tokens);

        let violations = Lexer::violations_from_tokens(&tokens);
        (tokens, violations)
    }

    /// Pre-compute matching bracket indices for all bracket tokens.
    /// This allows O(1) bracket lookup during parsing instead of O(n) scanning.
    fn compute_bracket_pairs(tokens: &mut [Token]) {
        // Stack to track opening brackets: (index, bracket_char)
        let mut bracket_stack: Vec<(usize, char)> = Vec::new();

        for idx in 0..tokens.len() {
            let raw = tokens[idx].raw();

            // Check if this is an opening bracket
            if let Some(open_char) = match raw.as_str() {
                "(" => Some('('),
                "[" => Some('['),
                "{" => Some('{'),
                _ => None,
            } {
                bracket_stack.push((idx, open_char));
            }
            // Check if this is a closing bracket
            else if let Some(expected_open) = match raw.as_str() {
                ")" => Some('('),
                "]" => Some('['),
                "}" => Some('{'),
                _ => None,
            } {
                // Try to match with the most recent opening bracket of the same type
                if let Some(pos) = bracket_stack.iter().rposition(|(_, c)| *c == expected_open) {
                    let (open_idx, _) = bracket_stack.remove(pos);
                    // Set bidirectional pointers
                    tokens[open_idx].matching_bracket_idx = Some(idx);
                    tokens[idx].matching_bracket_idx = Some(open_idx);
                }
                // If no matching opening bracket, leave as None (syntax error)
            }
        }
        // Any remaining opening brackets on the stack are unmatched - leave as None
    }

    fn violations_from_tokens(tokens: &[Token]) -> Vec<SQLLexError> {
        tokens
            .iter()
            .filter(|t| t.token_type == "unlexable")
            .map(|token| {
                SQLLexError::new(
                    Some(format!(
                        "Unable to lex characters: {}",
                        token.raw.chars().take(10).collect::<String>()
                    )),
                    token.pos_marker.clone(),
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            })
            .collect()
    }
}

fn iter_tokens(
    lexed_elements: &[TemplateElement],
    templated_file: &Arc<TemplatedFile>,
    add_indents: bool,
) -> Vec<Token> {
    let mut tfs_idx = 0;
    let mut block_stack = BlockTracker::new();
    let mut templated_file_slices = multipeek(templated_file.sliced_file.iter().peekable());

    let mut yielded_elements: Vec<Token> = lexed_elements
        .iter()
        .enumerate()
        .flat_map(|(idx, element)| -> std::vec::IntoIter<Token> {
            log::debug!("  {}: {}. [tfs_idx = {}]", idx, element, tfs_idx);
            let mut consumed_length = 0;
            let mut stashed_source_idx = None;
            let mut segments = Vec::new();

            while let Some(tfs) = templated_file_slices.peek().cloned() {
                log::debug!("      {}: {:?}", tfs_idx, tfs);

                if is_zero_slice(&tfs.templated_codepoint_slice) {
                    let next_tfs = templated_file_slices.clone().peek().cloned();
                    segments.extend(handle_zero_length_slice(
                        tfs,
                        next_tfs.as_ref(),
                        &mut block_stack,
                        templated_file,
                        add_indents,
                    ));
                    tfs_idx += 1;
                    templated_file_slices.next();
                    continue;
                }

                match tfs.slice_type.as_str() {
                    "literal" => {
                        let tfs_offset = tfs.source_codepoint_slice.start as isize - tfs.templated_codepoint_slice.start as isize;

                        if element.template_slice.stop <= tfs.templated_codepoint_slice.stop {
                            debug!(
                                "     Consuming whole from literal. Existing Consumed: {}",
                                consumed_length
                            );
                            let slice_start = stashed_source_idx.unwrap_or_else(|| {
                                (element.template_slice.start as isize + consumed_length as isize + tfs_offset) as usize
                            });

                            segments.push(element.to_token(
                                PositionMarker::new(
                                    Slice::from(
                                        slice_start..(element.template_slice.stop as isize + tfs_offset) as usize,
                                    ),
                                    element.template_slice,
                                    templated_file,
                                    None,
                                    None,
                                ),
                                Some(consumed_length..),
                            ));

                            if element.template_slice.stop == tfs.templated_codepoint_slice.stop {
                                tfs_idx += 1;
                                templated_file_slices.next();
                            }
                            templated_file_slices.reset_peek();
                            break;
                        } else if element.template_slice.start == tfs.templated_codepoint_slice.stop {
                            debug!("     NOTE: Missed Skip");
                            tfs_idx += 1;
                            templated_file_slices.next();
                            continue;
                        } else {
                            debug!("     Consuming whole spanning literal");
                            if element.matcher.name == "whitespace" {
                                debug!(
                                    "     Consuming split whitespace from literal. Existing Consumed: {}",
                                    consumed_length,
                                );
                                let incremental_length =
                                    tfs.templated_codepoint_slice.stop - element.template_slice.start;
                                segments.push(element.to_token(
                                    PositionMarker::new(
                                        Slice::from(
                                            (element.template_slice.start as isize
                                                + consumed_length as isize
                                                + tfs_offset) as usize
                                                ..(tfs.templated_codepoint_slice.stop as isize + tfs_offset) as usize,
                                        ),
                                        element.template_slice,
                                        templated_file,
                                        None,
                                        None,
                                    ),
                                    Some(consumed_length..(consumed_length + incremental_length)),
                                ));
                                consumed_length += incremental_length;
                                tfs_idx += 1;
                                templated_file_slices.next();
                                continue;
                            } else {
                                debug!("     Spilling over literal slice.");
                                if stashed_source_idx.is_none() {
                                    stashed_source_idx =
                                        Some((element.template_slice.start as isize + tfs_offset) as usize);
                                        debug!(
                                            "     Stashing a source start. {:?}", stashed_source_idx
                                        );
                                }
                                tfs_idx += 1;
                                templated_file_slices.next();
                                continue;
                            }
                        }
                    }
                    "templated" | "block_start" | "escaped" => {
                        if !is_zero_slice(&tfs.templated_codepoint_slice) {
                            if tfs.slice_type == "block_start" {
                                block_stack.enter(tfs.source_codepoint_slice);
                            }

                            if element.template_slice.stop <= tfs.templated_codepoint_slice.stop {
                                let slice_start = stashed_source_idx
                                    .unwrap_or(tfs.source_codepoint_slice.start + consumed_length);
                                segments.push(element.to_token(
                                    PositionMarker::new(
                                        Slice::from(slice_start..tfs.source_codepoint_slice.stop),
                                        element.template_slice,
                                        templated_file,
                                        None,
                                        None,
                                    ),
                                    Some(consumed_length..),
                                ));

                                if element.template_slice.stop == tfs.templated_codepoint_slice.stop {
                                    tfs_idx += 1;
                                    templated_file_slices.next();
                                }
                                templated_file_slices.reset_peek();
                                break;
                            } else {
                                if stashed_source_idx.is_none() {
                                    stashed_source_idx = Some(tfs.source_codepoint_slice.start);
                                }
                                tfs_idx += 1;
                                templated_file_slices.next();
                                continue;
                            }
                        }
                    }
                    _ => panic!("Unexpected slice type: {}", tfs.slice_type),
                }
            }

            segments.into_iter()
        })
        .collect();

    while let Some(tfs) = templated_file_slices.next().cloned() {
        let next_tfs = templated_file_slices.peek().cloned();
        yielded_elements.extend(handle_zero_length_slice(
            &tfs,
            next_tfs.as_ref(),
            &mut block_stack,
            templated_file,
            add_indents,
        ));
    }

    yielded_elements
}

fn handle_zero_length_slice(
    tfs: &TemplatedFileSlice,
    next_tfs: Option<&&TemplatedFileSlice>,
    block_stack: &mut BlockTracker,
    templated_file: &Arc<TemplatedFile>,
    add_indents: bool,
) -> impl Iterator<Item = Token> {
    let mut segments = Vec::new();
    assert!(is_zero_slice(&tfs.templated_codepoint_slice));

    // Backward jump detection
    if let Some(peek) = next_tfs {
        if tfs.slice_type.starts_with("block")
            && peek.source_codepoint_slice.start < tfs.source_codepoint_slice.start
        {
            log::debug!("      Backward jump detected. Inserting Loop Marker");
            let pos_marker = PositionMarker::from_point(
                tfs.source_codepoint_slice.start,
                tfs.templated_codepoint_slice.start,
                templated_file,
                None,
                None,
            );

            if add_indents {
                segments.push(Token::dedent_token(
                    pos_marker.clone(),
                    true,
                    None,
                    HashSet::new(),
                ));
            }

            segments.push(Token::template_loop_token(
                pos_marker.clone(),
                Some(block_stack.top()),
                HashSet::new(),
            ));

            if add_indents {
                segments.push(Token::indent_token(
                    pos_marker.clone(),
                    true,
                    None,
                    HashSet::new(),
                ));
            }

            return segments.into_iter();
        }
    }

    // Block handling
    if tfs.slice_type.starts_with("block") {
        if tfs.slice_type == "block_start" {
            block_stack.enter(tfs.source_codepoint_slice);
        } else if add_indents && (tfs.slice_type == "block_end" || tfs.slice_type == "block_mid") {
            let pos_marker = PositionMarker::from_point(
                tfs.source_codepoint_slice.start,
                tfs.templated_codepoint_slice.start,
                templated_file,
                None,
                None,
            );
            segments.push(Token::dedent_token(
                pos_marker,
                true,
                Some(block_stack.top()),
                HashSet::new(),
            ));
        }

        segments.push(Token::template_placeholder_token_from_slice(
            tfs.source_codepoint_slice,
            tfs.templated_codepoint_slice,
            tfs.slice_type.clone(),
            templated_file,
            Some(block_stack.top()),
            HashSet::new(),
        ));

        if tfs.slice_type == "block_end" {
            block_stack.exit();
        } else if add_indents && (tfs.slice_type == "block_start" || tfs.slice_type == "block_mid")
        {
            let pos_marker = PositionMarker::from_point(
                tfs.source_codepoint_slice.stop,
                tfs.templated_codepoint_slice.stop,
                templated_file,
                None,
                None,
            );
            segments.push(Token::indent_token(
                pos_marker,
                true,
                Some(block_stack.top()),
                HashSet::new(),
            ));
        }

        // Forward jump detection
        if let Some(peek) = next_tfs {
            if peek.source_codepoint_slice.start > tfs.source_codepoint_slice.stop {
                let mut placeholder_str = templated_file
                    .source_str
                    .chars()
                    .skip(tfs.source_codepoint_slice.stop)
                    .take(peek.source_codepoint_slice.start - tfs.source_codepoint_slice.stop)
                    .collect::<String>();
                if placeholder_str.chars().count() >= 20 {
                    placeholder_str = format!(
                        "... [{} unused template characters] ...",
                        placeholder_str.chars().count()
                    );
                }
                log::debug!("      Forward jump detected. Inserting placeholder");
                let pos_marker = PositionMarker::new(
                    Slice::from(tfs.source_codepoint_slice.stop..peek.source_codepoint_slice.start),
                    tfs.templated_codepoint_slice,
                    templated_file,
                    None,
                    None,
                );
                segments.push(Token::template_placeholder_token(
                    pos_marker,
                    placeholder_str,
                    "skipped_source".to_string(),
                    None,
                    HashSet::new(),
                ));
            }
        }

        return segments.into_iter();
    }

    // Default zero-length slice handling
    segments.push(Token::template_placeholder_token_from_slice(
        tfs.source_codepoint_slice,
        tfs.templated_codepoint_slice,
        tfs.slice_type.clone(),
        templated_file,
        None,
        HashSet::new(),
    ));

    segments.into_iter()
}

pub fn is_zero_slice(s: &Slice) -> bool {
    s.start == s.stop
}

pub enum LexInput {
    String(String),
    TemplatedFile(Arc<TemplatedFile>),
}

#[cfg(feature = "python")]
pub mod python {
    use std::str::FromStr;

    use super::{LexInput, Lexer, SQLLexError};
    use pyo3::{
        prelude::*,
        types::{PyDict, PyList, PyTuple},
    };
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_types::config::fluffconfig::python::PyFluffConfig;
    use sqlfluffrs_types::marker::python::PyPositionMarker;
    use sqlfluffrs_types::templater::templatefile::python::{
        PySqlFluffTemplatedFile, PyTemplatedFile,
    };
    use sqlfluffrs_types::token::python::PyToken;

    #[derive(FromPyObject)]
    pub enum PyLexInput {
        #[pyo3(transparent, annotation = "str")]
        String(String),
        #[pyo3(transparent, annotation = "TemplatedFile")]
        PySqlFluffTemplatedFile(PySqlFluffTemplatedFile),
        #[pyo3(transparent, annotation = "TemplatedFile")]
        PyTemplatedFile(PyTemplatedFile),
    }

    impl From<PyLexInput> for LexInput {
        fn from(value: PyLexInput) -> Self {
            match value {
                PyLexInput::String(s) => LexInput::String(s),
                PyLexInput::PySqlFluffTemplatedFile(py_sql_fluff_templated_file) => {
                    LexInput::TemplatedFile(py_sql_fluff_templated_file.into())
                }
                PyLexInput::PyTemplatedFile(py_templated_file) => {
                    LexInput::TemplatedFile(py_templated_file.into())
                }
            }
        }
    }

    #[pyclass(name = "RsSQLLexerError", module = "sqlfluffrs")]
    #[repr(transparent)]
    pub struct PySQLLexError(SQLLexError);

    #[pymethods]
    impl PySQLLexError {
        #[new]
        fn new(
            description: Option<String>,
            pos: Option<PyPositionMarker>,
            line_no: Option<usize>,
            line_pos: Option<usize>,
            ignore: Option<bool>,
            fatal: Option<bool>,
            warning: Option<bool>,
        ) -> Self {
            Self(SQLLexError::new(
                description,
                pos.map(Into::into),
                line_no,
                line_pos,
                ignore,
                fatal,
                warning,
            ))
        }

        #[getter]
        fn desc(&self) -> Option<String> {
            self.0.description.clone()
        }

        #[getter]
        fn line_pos(&self) -> usize {
            self.0.line_pos
        }

        #[getter]
        fn line_no(&self) -> usize {
            self.0.line_no
        }

        #[getter]
        fn ignore(&self) -> bool {
            self.0.ignore
        }

        #[getter]
        fn warning(&self) -> bool {
            self.0.warning
        }

        #[getter]
        fn fatal(&self) -> bool {
            self.0.fatal
        }

        fn source_signature(&self) -> ((String, usize, usize), String) {
            self.0.source_signature()
        }

        fn ignore_if_in(&mut self, ignore_iterable: Vec<String>) {
            self.0.ignore_if_in(&ignore_iterable)
        }

        fn warning_if_in(&mut self, ignore_iterable: Vec<String>) {
            self.0.warning_if_in(&ignore_iterable)
        }

        fn rule_code(&self) -> String {
            self.0.rule_code()
        }

        fn rule_name(&self) -> String {
            self.0.rule_name()
        }

        fn to_dict<'py>(&self, py: Python<'py>) -> Bound<'py, PyDict> {
            let dict = PyDict::new(py);
            dict.set_item("start_line_no", self.line_no()).unwrap();
            dict.set_item("start_line_pos", self.line_pos()).unwrap();
            dict.set_item("code", self.rule_code()).unwrap();
            dict.set_item("description", self.desc()).unwrap();
            dict.set_item("name", self.rule_name()).unwrap();
            dict.set_item("warning", self.warning()).unwrap();
            dict
        }
    }

    // impl Into<SQLLexError> for PySQLLexError {
    //     fn into(self) -> SQLLexError {
    //         self.0
    //     }
    // }

    impl From<SQLLexError> for PySQLLexError {
        fn from(value: SQLLexError) -> Self {
            Self(value)
        }
    }

    #[pyclass(name = "RsLexer", subclass, module = "sqlfluffrs")]
    #[repr(transparent)]
    #[derive(Clone)]
    pub struct PyLexer(pub Lexer);

    #[pymethods]
    impl PyLexer {
        #[new]
        #[pyo3(signature = (config=None, last_resort_lexer=None, dialect=None))]
        pub fn new(
            config: Option<PyFluffConfig>,
            last_resort_lexer: Option<&Bound<'_, PyDict>>,
            dialect: Option<&str>,
        ) -> Self {
            let _last_resort_lexer = last_resort_lexer;
            let cfg_dialect = config
                .and_then(|cfg| cfg.0.dialect.map(|d| Dialect::from_str(&d).ok()))
                .flatten();
            let in_dialect = dialect.and_then(|d| Dialect::from_str(d).ok());
            if cfg_dialect.is_some() && in_dialect.is_some() {
                panic!("Lexer does not support setting both `config` and `dialect`.")
            }
            let dialect = cfg_dialect.unwrap_or_else(|| in_dialect.expect("Dialect not defined"));
            Self(Lexer::new(None, dialect.get_lexers().to_vec()))
        }

        #[pyo3(signature = (input, template_blocks_indent = true))]
        pub fn _lex<'py>(
            &self,
            py: Python<'py>,
            input: PyLexInput,
            template_blocks_indent: bool,
        ) -> Result<Bound<'py, PyTuple>, PyErr> {
            let (tokens, violations) = self.0.lex(input.into(), template_blocks_indent);

            let token_tuple = PyTuple::new(
                py,
                tokens.into_iter().map(Into::into).collect::<Vec<PyToken>>(),
            )?;
            let violation_list = PyList::new(
                py,
                violations
                    .into_iter()
                    .map(Into::into)
                    .collect::<Vec<PySQLLexError>>(),
            )?;

            let obj = (token_tuple, violation_list);
            obj.into_pyobject(py)
        }
    }
}
