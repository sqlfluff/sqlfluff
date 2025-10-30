use std::sync::Arc;

use log::debug;

use sqlfluffrs_types::{
    marker::PositionMarker,
    matcher::{LexMatcher, LexedElement},
    slice::Slice,
    templater::{fileslice::TemplatedFileSlice, templatefile::TemplatedFile},
    token::Token,
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

    /// Check if the block stack is empty.
    pub fn is_empty(&self) -> bool {
        self.stack.is_empty()
    }

    /// Get the size of the stack.
    pub fn stack_size(&self) -> usize {
        self.stack.len()
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
    code: Option<String>,
    name: Option<String>,
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
            code: Some("LXR".to_string()),
            name: None,
            identifier: "lexing".to_string(),
        }
    }

    fn source_signature(&self) -> ((String, usize, usize), String) {
        (
            self.check_tuple(),
            self.description
                .clone()
                .unwrap_or_else(|| "No description".to_string()),
        )
    }

    fn check_tuple(&self) -> (String, usize, usize) {
        (self.rule_code(), self.line_no, self.line_pos)
    }

    fn rule_code(&self) -> String {
        self.code.clone().unwrap_or("????".to_string())
    }

    fn rule_name(&self) -> String {
        self.name.clone().unwrap_or("????".to_string())
    }

    fn ignore_if_in(&mut self, ignore_iterable: &[String]) {
        self.ignore = ignore_iterable.contains(&self.identifier);
    }

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
                None,
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

#[cfg(test)]
mod tests {
    //     use super::*;
    //     use crate::matcher::LexMatcher;
    //     use sqlfluffrs_types::token::config::TokenConfig;
    //     use sqlfluffrs_types::RegexModeGroup;
    //     use std::io::Write;
    //     use std::time::Instant;

    //     fn init() {
    //         let _ = env_logger::builder()
    //             .format(|buf, record| writeln!(buf, "{}: {}", record.level(), record.args()))
    //             .is_test(true)
    //             .try_init();
    //     }

    //     #[test]
    //     fn test_parser_lexer_obj() {
    //         let test_cases = vec![
    //             // NOTE: The final empty string is the end of file marker
    //             ("a b", vec!["a", " ", "b", ""]),
    //             ("b.c", vec!["b", ".", "c", ""]),
    //             (
    //                 "abc \n \t def  ;blah",
    //                 vec!["abc", " ", "\n", " \t ", "def", "  ", ";", "blah", ""],
    //             ),
    //             // Test Quotes
    //             (
    //                 "abc\'\n \"\t\' \"de`f\"",
    //                 vec!["abc", "'\n \"\t'", " ", "\"de`f\"", ""],
    //             ),
    //             // Test Comments
    //             (
    //                 "abc -- comment \nblah",
    //                 vec!["abc", " ", "-- comment ", "\n", "blah", ""],
    //             ),
    //             (
    //                 "abc # comment \nblah",
    //                 vec!["abc", " ", "# comment ", "\n", "blah", ""],
    //             ),
    //             // Note the more complicated parsing of block comments.
    //             // This tests subdivision and trimming (incl the empty case)
    //             (
    //                 "abc /* comment \nblah*/",
    //                 vec!["abc", " ", "/* comment", " ", "\n", "blah*/", ""],
    //             ),
    //             (
    //                 "abc /*\n\t\n*/",
    //                 vec!["abc", " ", "/*", "\n", "\t", "\n", "*/", ""],
    //             ),
    //             // Test strings
    //             ("*-+bd/", vec!["*", "-", "+", "bd", "/", ""]),
    //             // Test Negatives and Minus
    //             ("2+4 -5", vec!["2", "+", "4", " ", "-", "5", ""]),
    //             (
    //                 "when 'Spec\\'s 23' like",
    //                 vec!["when", " ", "'Spec\\'s 23'", " ", "like", ""],
    //             ),
    //             (
    //                 "when \"Spec\\\"s 23\" like",
    //                 vec!["when", " ", "\"Spec\\\"s 23\"", " ", "like", ""],
    //             ),
    //         ];

    //         // Use a sample of matchers directly, without Dialect dependency.
    //         // For demonstration, here are some typical ANSI SQL matchers:

    //         let matchers = vec![
    //             LexMatcher::regex_lexer(
    //                 "whitespace",
    //                 r#"[^\S\r\n]+"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::whitespace_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 |_| true,
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "inline_comment",
    //                 r#"(--|#)[^\n]*"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::comment_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 Some(vec![String::from("--"), String::from("#")]),
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 |input| input.starts_with(['#', '-', '/']),
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "block_comment",
    //                 r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::comment_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 Some(Box::new(LexMatcher::regex_subdivider(
    //                     "newline",
    //                     r#"\r\n|\n"#,
    //                     |raw,
    //                      pos_marker,
    //                      class_types,
    //                      instance_types,
    //                      trim_start,
    //                      trim_chars,
    //                      quoted_value,
    //                      escape_replacement,
    //                      casefold| {
    //                         Token::newline_token(
    //                             raw,
    //                             pos_marker,
    //                             TokenConfig {
    //                                 class_types,
    //                                 instance_types,
    //                                 trim_start,
    //                                 trim_chars,
    //                                 quoted_value,
    //                                 escape_replacement,
    //                                 casefold,
    //                             },
    //                         )
    //                     },
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     |_| true,
    //                     None,
    //                 ))),
    //                 Some(Box::new(LexMatcher::regex_subdivider(
    //                     "whitespace",
    //                     r#"[^\S\r\n]+"#,
    //                     |raw,
    //                      pos_marker,
    //                      class_types,
    //                      instance_types,
    //                      trim_start,
    //                      trim_chars,
    //                      quoted_value,
    //                      escape_replacement,
    //                      casefold| {
    //                         Token::whitespace_token(
    //                             raw,
    //                             pos_marker,
    //                             TokenConfig {
    //                                 class_types,
    //                                 instance_types,
    //                                 trim_start,
    //                                 trim_chars,
    //                                 quoted_value,
    //                                 escape_replacement,
    //                                 casefold,
    //                             },
    //                         )
    //                     },
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     None,
    //                     |_| true,
    //                     None,
    //                 ))),
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 Some(extract_nested_block_comment),
    //                 |input| input.starts_with("/"),
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "single_quote",
    //                 r#"'([^'\\]|\\.|'')*'"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::code_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 Some((
    //                     r#"'((?:[^'\\]|\\.|'')*)'"#.to_string(),
    //                     RegexModeGroup::Index(1),
    //                 )),
    //                 Some((r#"\\'|''"#.to_string(), r#"'"#.to_string())),
    //                 None,
    //                 None,
    //                 |input| match input.as_bytes() {
    //                     [b'\'', ..] => true,                           // Single quote case
    //                     [b'R' | b'r', b'\'', ..] => true,              // r' or R'
    //                     [b'B' | b'b', b'\'', ..] => true,              // b' or B'
    //                     [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
    //                     [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
    //                     _ => false,
    //                 },
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "double_quote",
    //                 r#""(""|[^"\\]|\\.)*""#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::code_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 Some((
    //                     r#""((?:[^"\\]|\\.)*)""#.to_string(),
    //                     RegexModeGroup::Index(1),
    //                 )),
    //                 Some((r#"\\"|"""#.to_string(), r#"""#.to_string())),
    //                 None,
    //                 None,
    //                 |input| match input.as_bytes() {
    //                     [b'"', ..] => true,                           // Just a double quote
    //                     [b'R' | b'r', b'"', ..] => true,              // r" or R"
    //                     [b'B' | b'b', b'"', ..] => true,              // b" or B"
    //                     [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
    //                     [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
    //                     _ => false,
    //                 },
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "back_quote",
    //                 r#"`(?:[^`\\]|\\.)*`"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::code_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 Some((
    //                     r#"`((?:[^`\\]|\\.)*)`"#.to_string(),
    //                     RegexModeGroup::Index(1),
    //                 )),
    //                 Some((r#"\\`"#.to_string(), r#"`"#.to_string())),
    //                 None,
    //                 None,
    //                 |_| true,
    //                 None,
    //             ),
    //             LexMatcher::regex_lexer(
    //                 "numeric_literal",
    //                 r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
    //                 |raw,
    //                  pos_marker,
    //                  class_types,
    //                  instance_types,
    //                  trim_start,
    //                  trim_chars,
    //                  quoted_value,
    //                  escape_replacement,
    //                  casefold| {
    //                     Token::literal_token(
    //                         raw,
    //                         pos_marker,
    //                         TokenConfig {
    //                             class_types,
    //                             instance_types,
    //                             trim_start,
    //                             trim_chars,
    //                             quoted_value,
    //                             escape_replacement,
    //                             casefold,
    //                         },
    //                     )
    //                 },
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 None,
    //                 |input| {
    //                     input.starts_with([
    //                         'x', 'X', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    //                     ])
    //                 },
    //                 None,
    //             ),
    //         ];
    //         for matcher in &matchers {
    //             println!("Matcher: {}", matcher.name);
    //         }

    //         let lexer = Lexer::new(None, Dialect::Ansi);

    //         for (raw, res) in test_cases {
    //             let (tokens, _) = lexer.lex(LexInput::String(raw.to_string()), true);
    //             for token in &tokens {
    //                 println!("{:?}", token);
    //             }
    //             assert_eq!(tokens.iter().map(|t| &t.raw).collect::<Vec<_>>(), res)
    //         }
    //     }

    //     #[test]
    //     fn test_unlexable_lex() {
    //         let raw = LexInput::String(
    //             r#"SELECT 1
    //         FROM table_2 WHERE a / b = 3   "  ;"#
    //                 .to_string(),
    //         );
    //         let lexer = Lexer::new(None, Dialect::Ansi);
    //         let (_tokens, violations) = lexer.lex(raw, true);

    //         assert_eq!(violations.len(), 1);
    //         assert_eq!(
    //             violations[0].description,
    //             Some("Unable to lex characters: \"".to_string())
    //         );
    //         assert_eq!(violations[0].line_no, 2);
    //         assert_eq!(violations[0].line_pos, 40);
    //     }

    //     #[test]
    //     fn test_scan_broken_quotes() {
    //         env_logger::try_init().ok();
    //         let lexer = Lexer::new(None, Dialect::Ansi);
    //         let test_case = lexer.lex_string(
    //             r#"SELECT 1
    //         FROM table_2 WHERE a / b = 3   "  ;"#,
    //         );
    //         for element in test_case {
    //             println!(r#"{} <"{}">"#, element.matcher.name, element.raw);
    //         }
    //     }

    //     #[test]
    //     fn test_scan_utf8() {
    //         init();

    //         let raw = LexInput::String(
    //             r#"SELECT amount+1 AS 'amount' FROM num1;

    // SELECT höhe+1 AS 'höhe' FROM num1;

    // SELECT amount*2 AS 'amount' FROM num1;

    // SELECT höhe*2 AS 'höhe' FROM num1;

    // SELECT employees.personal.name, neighbors.area FROM neighbors, employees
    // WHERE employees.personal.address.zipcode=neighbors.area.zipcode AND neighbors.num_neighbors > 1;

    // SELECT mitarbeiter.persönlicher.name, nachbarn.bereich FROM nachbarn, mitarbeiter
    // WHERE mitarbeiter.persönlicher.address.zipcode=nachbarn.gebiet.zipcode AND nachbarn.nummer_nachbarn > 1;

    // SELECT itemkey AS key, IMPLODE(itemprice) WITHIN GROUP (ORDER BY itemprice) AS prices
    //     FROM filtered GROUP BY itemkey ORDER BY itemkey;

    // SELECT ключтовара AS key, IMPLODE(ценатовара) WITHIN GROUP (ORDER BY ценатовара) AS цены
    //     FROM отфильтровано GROUP BY ключтовара ORDER BY ключтовара;

    // SELECT State, APPROXIMATE_PERCENTILE(sales USING PARAMETERS percentiles='0.5') AS median
    // FROM allsales GROUP BY state;

    // SELECT Χώρα, APPROXIMATE_PERCENTILE(πωλήσεις USING PARAMETERS percentiles='0.5') AS διάμεσος
    // FROM όλεςτιςπωλήσεις GROUP BY χώρα;

    // SELECT customer_state, customer_key, annual_income, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY annual_income)
    //       OVER (PARTITION BY customer_state) AS PERCENTILE_CONT
    //    FROM customer_dimension WHERE customer_state IN ('DC','WI') ORDER BY customer_state, customer_key;

    // SELECT état_du_client, clé_client, revenu_annuel, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY revenu_annuel)
    //       OVER (PARTITION BY état_du_client) AS PERCENTILE_CONT
    //    FROM dimension_client WHERE état_du_client IN ('Provence','Сhampagne') ORDER BY état_du_client, clé_client;

    // SELECT customer_state, customer_key, annual_income,
    //       PERCENTILE_DISC(.2) WITHIN GROUP(ORDER BY annual_income)
    //       OVER (PARTITION BY customer_state) AS PERCENTILE_DISC
    //    FROM customer_dimension
    //    WHERE customer_state IN ('DC','WI')
    //    AND customer_key < 300
    //    ORDER BY customer_state, customer_key;

    // SELECT état_du_client, clé_client, revenu_annuel,
    //       PERCENTILE_DISC(.2) WITHIN GROUP(ORDER BY annual_income)
    //       OVER (PARTITION BY état_du_client) AS PERCENTILE_DISC
    //    FROM dimension_client
    //    WHERE état_du_client IN ('Provence','Сhampagne')
    //    AND clé_client < 300
    //    ORDER BY état_du_client, clé_client;

    // SELECT customer_state, customer_key, annual_income, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY annual_income)
    //       OVER (PARTITION BY customer_state) AS PERCENTILE_CONT
    //    FROM customer_dimension WHERE customer_state IN ('DC','WI') AND customer_key < 300
    //    ORDER BY customer_state, customer_key;

    // SELECT état_du_client, clé_client, revenu_annuel, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY revenu_annuel)
    //       OVER (PARTITION BY état_du_client) AS PERCENTILE_CONT
    //    FROM dimension_client WHERE état_du_client IN ('Provence','Сhampagne') AND clé_client < 300
    //    ORDER BY état_du_client, clé_client;

    // SELECT store_region, store_city||', '||store_state location, store_name, number_of_employees FROM store.store_dimension
    //      LIMIT 2 OVER (PARTITION BY store_region ORDER BY number_of_employees ASC);

    // SELECT регион_магазина, город_магазина||', '||область_магазина местоположение, имя_магазина, количество_сотрудников FROM магазины.измерение_магазины
    //      LIMIT 2 OVER (PARTITION BY регион_магазина ORDER BY количество_сотрудников ASC);

    // SELECT PREDICT_LINEAR_REG(waiting USING PARAMETERS model_name='myLinearRegModel') FROM
    // faithful ORDER BY id;

    // SELECT PREDICT_LINEAR_REG(attente USING PARAMETERS model_name='monRegModèleLinéaire') FROM
    // fidèle ORDER BY id;

    // SELECT INFER_EXTERNAL_TABLE_DDL('/data/people/*.parquet'
    //         USING PARAMETERS format = 'parquet', table_name = 'employees');

    // SELECT INFER_EXTERNAL_TABLE_DDL('/data/άνθρωποι/*.parquet'
    //         USING PARAMETERS format = 'parquet', table_name = 'εργαζόμενοι');

    // SELECT PREDICT_ARIMA(temperature USING PARAMETERS model_name='arima_temp', start=100, npredictions=10) OVER(ORDER BY time) FROM temp_data;

    // SELECT PREDICT_ARIMA(температура USING PARAMETERS model_name='arima_temp', start=100, npredictions=10) OVER(ORDER BY time) FROM временные_данные;

    // SELECT INFER_TABLE_DDL ('/data/*.json'
    //     USING PARAMETERS table_name='restaurants', format='json',
    // max_files=3, max_candidates=3);

    // SELECT INFER_TABLE_DDL ('/data/*.json'
    //     USING PARAMETERS table_name='εστιατόρια', format='json',
    // max_files=3, max_candidates=3);

    // SELECT PURGE_TABLE('store.store_sales_fact');

    // SELECT PURGE_TABLE('المتجر.متجر_مبيعات_المتجر');

    // SELECT MSE(obs, prediction) OVER()
    //    FROM (SELECT eruptions AS obs,
    //                 PREDICT_LINEAR_REG (waiting USING PARAMETERS model_name='myLinearRegModel') AS prediction
    //          FROM faithful_testing) AS PredictionOutput;

    // SELECT MSE(наблюдения, предсказания) OVER()
    //    FROM (SELECT извержения AS наблюдения,
    //                 PREDICT_LINEAR_REG (ожидания USING PARAMETERS model_name='myLinearRegModel') AS прогноз
    //          FROM верное_испытание) AS РезультатПрогноза;

    // SELECT ps[0] as q0, ps[1] as q1, ps[2] as q2, ps[3] as q3, ps[4] as q4
    // FROM (SELECT APPROXIMATE_PERCENTILE(sales USING PARAMETERS percentiles='0, 0.25, 0.5, 0.75, 1')
    // AS ps FROM allsales GROUP BY state) as s1;

    // SELECT pz[0] as q0, pz[1] as q1, pz[2] as q2, pz[3] as q3, pz[4] as q4
    // FROM (SELECT APPROXIMATE_PERCENTILE(Verkäufe USING PARAMETERS percentiles='0, 0.25, 0.5, 0.75, 1')
    // AS pz FROM alleVerkäufe GROUP BY Staat) as s1;

    // SELECT id.name, major, GPA FROM students
    //    WHERE id = ROW('alice',119, ARRAY['alice@example.com','ap16@cs.example.edu']);

    // SELECT ид.имя, курс, СРБАЛЛ FROM студенты
    //    WHERE ид = ROW('алиса',119, ARRAY['alice@example.com','ap16@cs.example.edu']);

    // SELECT E'first part o'
    //     'f a long line';

    // SELECT E'πρώτο μέρος μι'
    //     'ας μακράς γραμμής';

    // SELECT STRING_TO_ARRAY(name USING PARAMETERS collection_delimiter=' ') FROM employee;

    // SELECT STRING_TO_ARRAY(имя USING PARAMETERS collection_delimiter=' ') FROM сотрудники;

    // -- ALTER SCHEMA block
    // ALTER SCHEMA ms OWNER TO dbadmin CASCADE;

    // ALTER SCHEMA επιμελητεία OWNER TO διαχειριστής CASCADE;

    // ALTER SCHEMA логистика OWNER TO алиса CASCADE;

    // ALTER SCHEMA s1, s2 RENAME TO s3, s4;

    // ALTER SCHEMA εμπορικός, s2 RENAME TO продажи, s4;

    // -- ALTER TABLE block
    // ALTER TABLE public.store_orders ADD COLUMN expected_ship_date date;

    // ALTER TABLE public.κατάστημα_παραγγελίες ADD COLUMN αναμενόμενη_ημερομηνία_αποστολής date;

    // ALTER TABLE public.заказы_магазина ADD COLUMN ожиддаемая_дата_отгрузки date;

    // ALTER TABLE t33 OWNER TO Alice;

    // ALTER TABLE επιμελητεία OWNER TO διαχειριστής;

    // ALTER TABLE заказы OWNER TO алиса;

    // -- ARRAY block
    // SELECT (ARRAY['مسؤل', 'διαχειριστής', 'логистика', 'd', 'e'])[1];

    // -- Cast w/ whitespace
    // SELECT amount_of_honey :: FLOAT
    // FROM bear_inventory;

    // SELECT ποσότητα_μελιού :: FLOAT
    // FROM αρκούδα_αποθήκη;

    // SELECT количество_мёда :: FLOAT
    // FROM медвежий_склад;

    // -- COMMENT ON block
    // COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'alias of APPROXIMATE_PERCENTILE with 0.5 as its parameter';
    // COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'ψευδώνυμο APPROXIMATE_PERCENTILE με 0,5 ως παράμετρό του';
    // COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'псевдоним APPROXIMATE_PERCENTILE с 0,5 в качестве параметра';

    // COMMENT ON SCHEMA public  IS 'All users can access this schema';
    // COMMENT ON SCHEMA public  IS 'Όλοι οι χρήστες έχουν πρόσβαση σε αυτό το σχήμα';
    // COMMENT ON SCHEMA public  IS 'Все пользователи могут получить доступ к этой схеме';

    // -- COPY block
    // COPY public.customer_dimension (
    //     customer_since FORMAT 'YYYY'
    // )
    //    FROM STDIN
    //    DELIMITER ','
    //    NULL AS 'null'
    //    ENCLOSED BY '"';

    // COPY παραγγελίες.παραγγελίες_ανά_ημέρα (
    //     πελάτη_αφού FORMAT 'YYYY'
    // )
    //    FROM STDIN
    //    DELIMITER ','
    //    NULL AS 'null'
    //    ENCLOSED BY '"';

    // COPY заказы.заказы_на_день (
    //     клиент_с_даты FORMAT 'YYYY'
    // )
    //    FROM STDIN
    //    DELIMITER ','
    //    NULL AS 'null'
    //    ENCLOSED BY '"';

    // -- CREATE PROJECTION block
    // CREATE PROJECTION public.employee_dimension_super
    //     AS SELECT * FROM public.employee_dimension
    //     ORDER BY employee_key
    //     SEGMENTED BY hash(employee_key) ALL NODES;

    // CREATE PROJECTION εμπορικός.παραγγελίες_ανά_ημέρα
    //     AS SELECT * FROM εμπορικός.παραγγελίες
    //     ORDER BY employee_key
    //     SEGMENTED BY hash(employee_key) ALL NODES;

    // CREATE PROJECTION продажи.продажи_на_по_клиенту
    //     AS SELECT * FROM продажи.продажи_на_сегодня
    //     ORDER BY клиент
    //     SEGMENTED BY hash(клиент) ALL NODES;

    // -- CREATE SCHEMA block
    // CREATE SCHEMA s3 DEFAULT INCLUDE SCHEMA PRIVILEGES;
    // CREATE SCHEMA εμπορικός DEFAULT INCLUDE SCHEMA PRIVILEGES;
    // CREATE SCHEMA продажи DEFAULT INCLUDE SCHEMA PRIVILEGES;

    // -- unquoted identifiers
    // SELECT * FROM логистика.εμπορικός;

    // SELECT * FROM логистика.εμπορικός1;
    // SELECT * FROM логистика.εμπορικός_;
    // SELECT * FROM логистика.s$ales$;
    // SELECT * FROM логистика._εμπορικός;
    // SELECT * FROM логистика._1234εμπορικός;

    // SELECT * FROM логистика1.εμπορικός;
    // SELECT * FROM логистика_.εμπορικός;
    // SELECT * FROM $public$.εμπορικός;
    // SELECT * FROM _логистика.εμπορικός;
    // SELECT * FROM _1234логистика.εμπορικός;

    // SELECT * FROM логистика1.εμπορικός1;
    // SELECT * FROM логистика1_.εμπορικός1_;
    // SELECT * FROM $public1_$.s$ales1_$;

    // -- quoted identifiers
    // SELECT * FROM "12логистика"."12344εμπορικός";
    // SELECT * FROM "_1234логистика"."_1234εμπορικός";
    // "#
    //                 .to_string(),
    //         );
    //         let (template, str_buff) = match raw {
    //             LexInput::String(raw_str) => {
    //                 let template = TemplatedFile::from(raw_str.clone());
    //                 (Arc::new(template), raw_str)
    //             }
    //             LexInput::TemplatedFile(template_file) => {
    //                 let str_buff = template_file.to_string();
    //                 (template_file, str_buff)
    //             }
    //         };

    //         let lexer = Lexer::new(None, Dialect::Ansi);
    //         let t0 = Instant::now();
    //         let test_case = lexer.lex_string(&str_buff);
    //         let duration = t0.elapsed(); // Calculate elapsed time
    //         println!("lex_string time: {:?}", duration);
    //         // for element in test_case {
    //         //     println!(r#"{} <"{}">"#, element.matcher.name, element.raw);
    //         // }
    //         let templated_buffer = lexer.map_template_slices(&test_case, &template);
    //         // for e in x {
    //         //     println!(
    //         //         "{} : {} : {} - {}",
    //         //         e.matcher.name, e.raw, e.template_slice.start, e.template_slice.end
    //         //     )
    //         // }
    //         let duration = t0.elapsed(); // Calculate elapsed time
    //         println!("map_template_slices time: {:?}", duration);
    //         let _tokens = lexer.elements_to_tokens(&templated_buffer, &template, false);
    //         // for token in tokens {
    //         //     println!(
    //         //         "{}: {} : '{}'",
    //         //         token.pos_marker.to_source_string(),
    //         //         token.token_type.unwrap_or("None".to_string()),
    //         //         token.raw.escape_debug(),
    //         //     )
    //         // }
    //         let duration = t0.elapsed(); // Calculate elapsed time
    //         println!("Execution time: {:?}", duration);
    //     }
}
