pub mod construction;
mod eq;
pub mod fix;
mod fmt;
pub mod path;
#[cfg(feature = "python")]
pub mod python;

use std::{
    fmt::Write,
    sync::{Arc, Weak},
};

use fix::SourceFix;
use hashbrown::{HashMap, HashSet};
use path::PathStep;
use uuid::Uuid;

use crate::marker::PositionMarker;

#[derive(Debug, Clone, PartialEq)]
pub enum TupleSerialisedSegment {
    Str(String, String),
    Nested(String, Vec<TupleSerialisedSegment>),
}

#[derive(Debug, Clone)]
pub struct Token {
    pub token_type: String,
    pub instance_types: Vec<String>,
    pub class_types: HashSet<String>,
    pub comment_separate: bool,
    pub is_meta: bool,
    pub allow_empty: bool,
    pub pos_marker: Option<PositionMarker>,
    pub raw: String,
    is_whitespace: bool,
    is_code: bool,
    is_comment: bool,
    _default_raw: String,
    pub indent_value: i32,
    pub is_templated: bool,
    pub block_uuid: Option<Uuid>,
    pub source_str: Option<String>,
    pub block_type: Option<String>,
    parent: Option<Weak<Token>>,
    parent_idx: Option<usize>,
    pub segments: Vec<Token>,
    preface_modifier: String,
    suffix: String,
    pub uuid: u128,
    pub source_fixes: Option<Vec<SourceFix>>,
    pub trim_start: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub cache_key: String,
}

impl Token {
    fn comments(&self) -> Vec<Token> {
        self.segments
            .clone()
            .into_iter()
            .filter(|s| s.is_type(&["comment"]))
            .collect::<Vec<_>>()
    }

    fn non_comments(&self) -> Vec<Token> {
        self.segments
            .clone()
            .into_iter()
            .filter(|s| !s.is_type(&["comment"]))
            .collect::<Vec<_>>()
    }

    /// Returns True if this segment is code.
    pub fn is_code(&self) -> bool {
        match self.is_raw() {
            true => self.is_code,
            false => self.segments.iter().any(|s| s.is_code()),
        }
    }

    fn code_indices(&self) -> Vec<usize> {
        self.segments
            .iter()
            .enumerate()
            .filter(|(_i, s)| s.is_code())
            .map(|(i, _s)| i)
            .collect()
    }

    pub fn is_comment(&self) -> bool {
        match self.is_raw() {
            true => self.is_comment,
            false => self.segments.iter().all(|s| s.is_comment()),
        }
    }

    pub fn is_whitespace(&self) -> bool {
        match self.is_raw() {
            true => self.is_whitespace,
            false => self.segments.iter().all(|s| s.is_whitespace()),
        }
    }

    pub fn raw(&self) -> String {
        self.raw.clone()
    }

    pub fn raw_upper(&self) -> String {
        self.raw.to_uppercase()
    }

    pub fn raw_segments(&self) -> Vec<Token> {
        match self.is_raw() {
            true => vec![self.clone()],
            false => self
                .segments
                .iter()
                .flat_map(|s| s.raw_segments())
                .collect::<Vec<_>>(),
        }
    }

    /// The set of full types for this token, including inherited.
    /// Adds the surrogate type for raw segments.
    pub fn class_types(&self) -> HashSet<String> {
        let mut full_types = self.instance_types.iter().cloned().collect::<HashSet<_>>();
        full_types.extend(self.class_types.clone());
        full_types
    }

    pub fn descendant_type_set(&self) -> HashSet<String> {
        self.segments
            .iter()
            .flat_map(|seg| {
                seg.descendant_type_set()
                    .union(&seg.class_types())
                    .cloned()
                    .collect::<HashSet<String>>()
            })
            .collect::<HashSet<String>>()
    }

    pub fn direct_descendant_type_set(&self) -> HashSet<String> {
        self.segments
            .iter()
            .flat_map(|seg| seg.class_types())
            .collect::<HashSet<String>>()
    }

    pub fn raw_segments_with_ancestors(&self) -> Vec<(Token, Vec<PathStep>)> {
        todo!()
    }

    pub fn source_fixes(&self) -> Vec<SourceFix> {
        match self.is_raw() {
            true => self.source_fixes.clone().unwrap_or_default(),
            false => self
                .segments
                .iter()
                .flat_map(|s| s.source_fixes())
                .collect(),
        }
    }

    pub fn first_non_whitespace_segment_raw_upper(&self) -> Option<String> {
        self.raw_segments().iter().find_map(|seg| {
            if !seg.raw_upper().trim().is_empty() {
                Some(seg.raw_upper().clone())
            } else {
                None
            }
        })
    }

    pub fn is_templated(&self) -> bool {
        let pos_marker = self.pos_marker.clone().expect("PositionMarker must be set");
        pos_marker.source_slice.start != pos_marker.source_slice.stop && !pos_marker.is_literal()
    }

    pub fn get_type(&self) -> String {
        self.token_type.clone()
    }

    pub fn is_type(&self, seg_types: &[&str]) -> bool {
        if self
            .instance_types
            .iter()
            .any(|s| seg_types.contains(&s.as_str()))
        {
            return true;
        }
        self.class_is_type(seg_types)
    }

    pub fn get_raw_segments(&self) -> Vec<Token> {
        todo!()
    }

    pub fn raw_trimmed(&self) -> String {
        let mut raw_buff = self.raw.clone();

        // Trim start sequences
        if let Some(trim_start) = &self.trim_start {
            for seq in trim_start {
                raw_buff = raw_buff.strip_prefix(seq).unwrap_or(&raw_buff).to_string();
            }
        }

        // Trim specified characters from both ends
        if let Some(trim_chars) = &self.trim_chars {
            raw_buff = self.raw.clone(); // Reset raw_buff before trimming chars

            for seq in trim_chars {
                while raw_buff.starts_with(seq) {
                    raw_buff = raw_buff.strip_prefix(seq).unwrap_or(&raw_buff).to_string();
                }
                while raw_buff.ends_with(seq) {
                    raw_buff = raw_buff.strip_suffix(seq).unwrap_or(&raw_buff).to_string();
                }
            }
        }

        raw_buff
    }

    fn _raw_normalized(&self) -> String {
        todo!()
    }

    pub fn raw_normalized(&self) -> String {
        todo!()
    }

    pub fn stringify(&self, ident: usize, tabsize: usize, code_only: bool) -> String {
        let mut buff = String::new();
        let preface = self.preface(ident, tabsize);
        writeln!(buff, "{}", preface).unwrap();

        if !code_only && self.comment_separate && !self.comments().is_empty() {
            if !self.comments().is_empty() {
                writeln!(buff, "{}Comments:", " ".repeat((ident + 1) * tabsize)).unwrap();
                for seg in &self.comments() {
                    let segment_string = seg.stringify(ident + 2, tabsize, code_only);
                    buff.push_str(&segment_string);
                }
            }

            if !self.non_comments().is_empty() {
                writeln!(buff, "{}Code:", " ".repeat((ident + 1) * tabsize)).unwrap();
                for seg in &self.non_comments() {
                    let segment_string = seg.stringify(ident + 2, tabsize, code_only);
                    buff.push_str(&segment_string);
                }
            }
        } else {
            for seg in &self.segments {
                if !code_only || seg.is_code {
                    let segment_string = seg.stringify(ident + 1, tabsize, code_only);
                    buff.push_str(&segment_string);
                }
            }
        }

        buff
    }

    pub fn edit(&self, raw: Option<String>, source_fixes: Option<Vec<SourceFix>>) -> Self {
        Self {
            raw: raw.unwrap_or(self.raw.clone()),
            source_fixes: Some(source_fixes.unwrap_or(self.source_fixes())),
            uuid: Uuid::new_v4().as_u128(),
            ..self.clone()
        }
    }

    pub fn _get_raw_segment_kwargs(&self) -> HashMap<String, String> {
        HashMap::new()
    }

    pub fn iter_unparseables(&self) -> Vec<Token> {
        self.segments
            .iter()
            .flat_map(|s| s.iter_unparseables())
            .collect()
    }

    pub fn set_parent(&mut self, parent: Arc<Token>, idx: usize) {
        self.parent = Some(Arc::downgrade(&parent));
        self.parent_idx = Some(idx);
    }

    pub fn class_is_type(&self, seg_types: &[&str]) -> bool {
        let seg_hash: HashSet<&str> = seg_types.iter().cloned().collect();
        !self
            .class_types
            .iter()
            .filter(|s| seg_hash.contains(s.as_str()))
            .collect::<Vec<_>>()
            .is_empty()
    }

    pub fn count_segments(&self, raw_only: bool) -> usize {
        if self.is_raw() {
            1
        } else {
            let self_count = if raw_only { 0 } else { 1 };
            self.segments
                .iter()
                .fold(0, |acc, s| acc + s.count_segments(raw_only) + self_count)
        }
    }

    pub fn is_raw(&self) -> bool {
        self.segments.len() == 0
    }

    pub fn block_type(&self) -> Option<String> {
        self.block_type.clone()
    }

    pub fn recursive_crawl(
        &self,
        seg_types: &[&str],
        recurse_into: bool,
        no_recursive_seg_type: Option<&[&str]>,
        allow_self: bool,
    ) -> Vec<Token> {
        let seg_type_set: HashSet<String> = seg_types.iter().map(|s| s.to_string()).collect();
        let seg_type_vec: Vec<&str> = seg_types.iter().cloned().collect();
        let no_recursive_set: HashSet<&str> = no_recursive_seg_type
            .unwrap_or(&[])
            .iter()
            .cloned()
            .collect();

        let mut results = Vec::new();

        // Check if self matches the given segment types
        if allow_self && self.is_type(&seg_type_vec) {
            results.push(self.clone());
        }

        // If no matching descendants, terminate early
        if self.descendant_type_set().is_disjoint(&seg_type_set) {
            return results;
        }

        // Recursively process child segments
        for seg in &self.segments {
            if !no_recursive_set.contains(seg.token_type.as_str()) {
                results.extend(seg.recursive_crawl(
                    seg_types,
                    recurse_into,
                    no_recursive_seg_type,
                    true,
                ));
            }
        }

        results
    }

    pub fn path_to(self, other: Self) -> Vec<PathStep> {
        // Return empty if they are the same segment.
        if self == other {
            return vec![];
        }

        // If there are no child segments, return empty.
        if self.segments.is_empty() {
            return vec![];
        }

        // Identifying the highest parent we can using any preset parent values.
        let mut midpoint = other.clone();
        let mut lower_path = Vec::new();

        while let Some(weak_parent) = &midpoint.parent.clone().as_ref() {
            if let Some(parent) = weak_parent.upgrade() {
                let parent_idx = midpoint.parent_idx.expect("Parent index must be set.");

                lower_path.push(PathStep {
                    segment: Arc::clone(&parent),
                    idx: parent_idx,
                    len: parent.segments.len(),
                    code_idxs: parent.code_indices().clone(),
                });

                midpoint = Arc::unwrap_or_clone(parent);
                if midpoint == self {
                    break;
                }
            } else {
                break;
            }
        }

        // Reverse the path so far
        lower_path.reverse();

        // If we have already found the parent, return.
        if midpoint == self {
            return lower_path;
        }
        // If we've gone all the way up to the file segment, return empty.
        if midpoint.class_is_type(&["file"]) {
            return vec![];
        }
        // Check if midpoint is within self's range.
        if !(self.get_start_loc() <= midpoint.get_start_loc()
            && midpoint.get_start_loc() <= self.get_end_loc())
        {
            return vec![];
        }

        // Now, work downward from `self` toward `midpoint`.
        for (idx, seg) in self.segments.clone().iter().enumerate() {
            // Set the parent if it's not already set.
            let seg = seg.clone();
            seg.clone().set_parent(Arc::new(self.clone()), idx);

            let step = PathStep {
                segment: Arc::new(self.clone()),
                idx: idx,
                len: self.segments.clone().len(),
                code_idxs: self.code_indices().clone(),
            };

            // If we found the target
            if seg == midpoint {
                let mut result = vec![step];
                result.extend(lower_path);
                return result;
            }

            // Check recursively if a path exists
            let res = seg.path_to(midpoint.clone());
            if !res.is_empty() {
                let mut result = vec![step];
                result.extend(res);
                result.extend(lower_path);
                return result;
            }
        }

        // Not found.
        vec![]
    }

    pub fn get_start_loc(&self) -> (usize, usize) {
        self.pos_marker
            .clone()
            .expect("PositionMarker unset")
            .working_loc()
    }

    pub fn get_end_loc(&self) -> (usize, usize) {
        self.pos_marker
            .clone()
            .expect("PositionMarker unset")
            .working_loc_after(&self.raw)
    }

    pub fn recursive_crawl_all(&self, reverse: bool) -> Box<dyn Iterator<Item = &Token> + '_> {
        if reverse {
            Box::new(
                self.segments
                    .iter()
                    .rev()
                    .flat_map(move |seg| seg.recursive_crawl_all(reverse))
                    .chain(std::iter::once(self)),
            )
        } else {
            Box::new(
                std::iter::once(self).chain(
                    self.segments
                        .iter()
                        .flat_map(move |seg| seg.recursive_crawl_all(reverse)),
                ),
            )
        }
    }

    fn preface(&self, ident: usize, tabsize: usize) -> String {
        let padding = " ".repeat(ident * tabsize);
        let padded_type = format!("{}{}{}:", padding, self.preface_modifier, self.get_type());

        let pos = self.pos_marker.clone();
        let suffix = self.suffix.clone();

        let preface = format!(
            "{:<20}|{:<60}  {}",
            pos.clone()
                .expect("PositionMarker unset")
                .to_source_string(),
            padded_type,
            suffix
        );

        preface.trim_end().to_string()
    }

    pub fn to_tuple(
        &self,
        code_only: Option<bool>,
        show_raw: Option<bool>,
        include_meta: Option<bool>,
    ) -> TupleSerialisedSegment {
        let code_only = code_only.unwrap_or_default();
        let show_raw = show_raw.unwrap_or_default();
        let include_meta = include_meta.unwrap_or_default();
        // If `show_raw` is true and there are no child segments, return (type, raw)
        if show_raw && self.segments.is_empty() {
            return TupleSerialisedSegment::Str(self.get_type(), self.raw.clone());
        }

        // Determine filtering criteria for child segments
        let filtered_segments: Vec<TupleSerialisedSegment> = self
            .segments
            .iter()
            .filter(|seg| {
                if code_only {
                    seg.is_code && !seg.is_meta
                } else {
                    include_meta || !seg.is_meta
                }
            })
            .map(|seg| seg.to_tuple(Some(code_only), Some(show_raw), Some(include_meta)))
            .collect();

        TupleSerialisedSegment::Nested(self.get_type(), filtered_segments)
    }

    pub fn copy(
        &self,
        segments: Option<Vec<Token>>,
        parent: Option<Arc<Token>>,
        parent_idx: Option<usize>,
    ) -> Token {
        let mut new_segment = self.clone();
        new_segment.parent = parent.as_ref().map(Arc::downgrade).into();
        new_segment.parent_idx = parent_idx.into();

        if let Some(ref segs) = segments {
            new_segment.segments = segs.clone();
        } else {
            new_segment.segments = self
                .segments
                .iter()
                .enumerate()
                .map(|(idx, seg)| {
                    seg.copy(
                        None,
                        Some(Arc::new(new_segment.clone())).into(),
                        Some(idx).into(),
                    )
                })
                .collect();
        }

        new_segment
    }

    pub fn position_segments(segments: &[Token], parent_pos: PositionMarker) -> Vec<Token> {
        assert!(
            !segments.is_empty(),
            "position_segments called on empty sequence."
        );
        let mut line_no = parent_pos.working_line_no;
        let mut line_pos = parent_pos.working_line_pos;

        let mut segment_buffer = Vec::new();

        for (idx, segment) in segments.iter().enumerate() {
            let old_position = segment.pos_marker.clone();
            let mut new_position = segment.pos_marker.clone();

            // If position is missing, try to infer it
            if new_position.is_none() {
                let mut start_point = None;
                if idx > 0 {
                    let prev_seg: &Token = &segment_buffer[idx - 1];
                    if let Some(ref pos_marker) = prev_seg.pos_marker {
                        start_point = Some(pos_marker.end_point_marker());
                    }
                } else {
                    start_point = Some(parent_pos.start_point_marker());
                }

                // Search forward for the end point
                let mut end_point = None;
                for fwd_seg in &segments[idx + 1..] {
                    if let Some(ref pos_marker) = fwd_seg.pos_marker {
                        end_point = Some(pos_marker.start_point_marker());
                        break;
                    }
                }

                new_position = match (start_point, end_point) {
                    (Some(start), Some(end)) if start != end => {
                        Some(PositionMarker::from_points(&start, &end))
                    }
                    (Some(start), _) => Some(start),
                    (_, Some(end)) => Some(end),
                    _ => panic!("Unable to position new segment"),
                };
            }

            let new_position = new_position.expect("Position should be assigned");
            let new_position = new_position.with_working_position(line_no, line_pos);
            let (new_line_no, new_line_pos) =
                new_position.infer_next_position(&segment.raw, line_no, line_pos);
            line_no = new_line_no;
            line_pos = new_line_pos;

            // If position changed, recursively process child segments before copying
            let new_segment =
                if !segment.segments.is_empty() && old_position != Some(new_position.clone()) {
                    let child_segments =
                        Token::position_segments(&segment.segments, new_position.clone());
                    segment.copy(Some(child_segments.into()), None, None)
                } else {
                    segment.copy(None, None, None)
                };

            segment_buffer.push(new_segment);
        }

        segment_buffer
    }

    // /// Simplifies the structure of the token recursively for serialization.
    // pub fn structural_simplify(&self) -> HashMap<String, Option<serde_json::Value>> {
    //     let mut result = HashMap::new();
    //     let key = self.get_type();

    //     if self.segments.is_empty() {
    //         // If there are no child segments, return the raw value.
    //         result.insert(key, Some(serde_json::Value::String(self.raw.clone())));
    //     } else {
    //         // Simplify all child segments recursively.
    //         let mut child_results = Vec::new();
    //         for segment in &self.segments {
    //             child_results.push(serde_json::Value::Object(
    //                 segment.structural_simplify(),
    //             ));
    //         }

    //         // Check for duplicate keys in child results.
    //         let mut subkeys = Vec::new();
    //         for child in &child_results {
    //             if let serde_json::Value::Object(map) = child {
    //                 subkeys.extend(map.keys().cloned());
    //             }
    //         }

    //         if subkeys.len() != subkeys.iter().collect::<std::collections::HashSet<_>>().len() {
    //             // If there are duplicate keys, use a list of child objects.
    //             result.insert(key, Some(serde_json::Value::Array(child_results)));
    //         } else {
    //             // Otherwise, merge child objects into a single map.
    //             let mut merged_map = HashMap::new();
    //             for child in child_results {
    //                 if let serde_json::Value::Object(map) = child {
    //                     for (k, v) in map {
    //                         merged_map.insert(k, v);
    //                     }
    //                 }
    //             }
    //             result.insert(key, Some(serde_json::Value::Object(merged_map)));
    //         }
    //     }

    //     result
    // }
}

#[cfg(test)]
mod tests {
    use crate::matcher::TokenGenerator;
    use crate::slice::Slice;
    use crate::templater::templatefile::TemplatedFile;

    use super::*;

    /// Roughly generate test segments.
    ///
    /// This function isn't totally robust, but good enough
    /// for testing. Use with caution.
    fn generate_test_segments(elems: &[&str]) -> Vec<Token> {
        let mut buff = vec![];
        let templated_file = Arc::new(TemplatedFile::from(
            elems.iter().cloned().collect::<String>(),
        ));
        let mut idx = 0;

        for elem in elems {
            let elem = &**elem;
            if elem == "<indent>" {
                buff.push(Token::indent_token(
                    PositionMarker::from_point(idx, idx, &templated_file, None, None),
                    false,
                    None,
                    HashSet::new(),
                    None,
                ));
                continue;
            } else if elem == "<dedent>" {
                buff.push(Token::dedent_token(
                    PositionMarker::from_point(idx, idx, &templated_file, None, None),
                    false,
                    None,
                    HashSet::new(),
                ));
                continue;
            }
            let (token_fn, instance_types, cache_key): (TokenGenerator, Vec<String>, String) =
                match elem {
                    " " | "\t" => (
                        Token::whitespace_token,
                        Vec::new(),
                        Uuid::new_v4().to_string(),
                    ),
                    "\n" => (Token::newline_token, Vec::new(), Uuid::new_v4().to_string()),
                    "(" => (
                        Token::symbol_token,
                        Vec::from_iter(["start_bracket".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    ")" => (
                        Token::symbol_token,
                        Vec::from_iter(["end_bracket".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    "[" => (
                        Token::symbol_token,
                        Vec::from_iter(["start_square_bracket".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    "]" => (
                        Token::symbol_token,
                        Vec::from_iter(["end_square_bracket".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    s if s.starts_with("--") => (
                        Token::comment_token,
                        Vec::from_iter(["inline_comment".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    s if s.starts_with("\"") => (
                        Token::code_token,
                        Vec::from_iter(["double_quote".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    s if s.starts_with("'") => (
                        Token::code_token,
                        Vec::from_iter(["single_quote".to_string()]),
                        Uuid::new_v4().to_string(),
                    ),
                    _ => (Token::code_token, Vec::new(), Uuid::new_v4().to_string()),
                };

            buff.push(token_fn(
                elem.into(),
                PositionMarker::new(
                    Slice {
                        start: idx,
                        stop: idx + elem.len(),
                    },
                    Slice {
                        start: idx,
                        stop: idx + elem.len(),
                    },
                    &templated_file,
                    None,
                    None,
                ),
                HashSet::new(),
                instance_types,
                None,
                None,
                cache_key,
            ));
            idx += elem.len();
        }

        buff
    }

    fn raw_segments() -> Vec<Token> {
        generate_test_segments(&vec!["foobar", ".barfoo"])
    }

    #[test]
    /// Test niche case of calling get_raw_segments on a raw segment.
    fn test_parser_raw_get_raw_segments() {
        for s in raw_segments() {
            assert_eq!(s.raw_segments(), [s]);
        }
    }
}
