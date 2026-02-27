use hashbrown::HashMap;
use std::cmp::Ordering;
use std::fmt::Display;
use std::sync::Arc;

use crate::slice::Slice;
use crate::templater::templatefile::TemplatedFile;

#[derive(Debug, Clone)]
pub struct PositionMarker {
    pub source_slice: Slice,
    pub templated_slice: Slice,
    pub templated_file: Arc<TemplatedFile>,
    pub working_line_no: usize,
    pub working_line_pos: usize,
}

impl PositionMarker {
    #[must_use]
    pub fn new(
        source_slice: Slice,
        templated_slice: Slice,
        templated_file: &Arc<TemplatedFile>,
        working_line_no: Option<usize>,
        working_line_pos: Option<usize>,
    ) -> Self {
        let (working_line_no, working_line_pos) = match (working_line_no, working_line_pos) {
            (Some(working_line_no), Some(working_line_pos)) => (working_line_no, working_line_pos),
            _ => templated_file.get_line_pos_of_char_pos(source_slice.start, false),
        };

        Self {
            source_slice,
            templated_slice,
            templated_file: Arc::clone(templated_file),
            working_line_no,
            working_line_pos,
        }
    }

    #[must_use]
    pub fn working_loc(&self) -> (usize, usize) {
        (self.working_line_no, self.working_line_pos)
    }

    #[must_use]
    pub fn working_loc_after(&self, raw: &str) -> (usize, usize) {
        // Infer next position based on the raw string
        self.infer_next_position(raw, self.working_line_no, self.working_line_pos)
    }

    #[must_use]
    pub fn infer_next_position(
        &self,
        raw: &str,
        line_no: usize,
        line_pos: usize,
    ) -> (usize, usize) {
        // Placeholder for position inference logic
        // Example implementation: move forward by the length of the string
        let lines: Vec<&str> = raw.split('\n').collect();
        if lines.len() > 1 {
            let num_lines: usize = lines.len();
            let last_line_len: usize = lines.last().unwrap().len();
            (line_no + num_lines - 1, last_line_len + 1)
        } else {
            let first_line_len: usize = raw.len();
            (line_no, line_pos + first_line_len)
        }
    }

    #[must_use]
    pub fn source_position(&self) -> (usize, usize) {
        self.templated_file
            .get_line_pos_of_char_pos(self.source_slice.start, true)
    }

    #[must_use]
    pub fn templated_position(&self) -> (usize, usize) {
        self.templated_file
            .get_line_pos_of_char_pos(self.source_slice.start, false)
    }

    #[must_use]
    pub fn line_no(&self) -> usize {
        self.source_position().0
    }

    #[must_use]
    pub fn line_pos(&self) -> usize {
        self.source_position().1
    }

    #[must_use]
    pub fn to_source_string(&self) -> String {
        let (line, pos) = self.source_position();
        format!("[L:{line:3}, P:{pos:3}]")
    }

    #[must_use]
    pub fn start_point_marker(&self) -> Self {
        PositionMarker::from_point(
            self.source_slice.start,
            self.templated_slice.start,
            &self.templated_file,
            Some(self.working_line_no),
            Some(self.working_line_pos),
        )
    }

    #[must_use]
    pub fn end_point_marker(&self) -> Self {
        PositionMarker::from_point(
            self.source_slice.stop,
            self.templated_slice.stop,
            &self.templated_file,
            None,
            None,
        )
    }

    #[must_use]
    pub fn is_point(&self) -> bool {
        slice_is_point(&self.source_slice) && slice_is_point(&self.templated_slice)
    }

    #[must_use]
    pub fn with_working_position(&self, line_no: usize, line_pos: usize) -> Self {
        PositionMarker {
            working_line_no: line_no,
            working_line_pos: line_pos,
            ..self.clone()
        }
    }

    #[must_use]
    pub fn is_literal(&self) -> bool {
        self.templated_file
            .is_source_slice_literal(&self.source_slice)
    }

    #[must_use]
    pub fn source_str(&self) -> String {
        self.templated_file
            .source_str
            .chars()
            .skip(self.source_slice.start)
            .take(self.source_slice.len())
            .collect::<String>()
    }

    #[must_use]
    pub fn to_source_dict(&self) -> HashMap<String, usize> {
        self.templated_file
            .source_position_dict_from_slice(&self.source_slice)
    }

    #[must_use]
    pub fn from_point(
        source_point: usize,
        templated_point: usize,
        templated_file: &Arc<TemplatedFile>,
        working_line_no: Option<usize>,
        working_line_pos: Option<usize>,
    ) -> Self {
        let source_slice = Slice::from(source_point..source_point);
        let templated_slice = Slice::from(templated_point..templated_point);

        PositionMarker::new(
            source_slice,
            templated_slice,
            templated_file,
            working_line_no,
            working_line_pos,
        )
    }

    #[must_use]
    pub fn from_points(start_marker: &PositionMarker, end_marker: &PositionMarker) -> Self {
        if start_marker.templated_file != end_marker.templated_file {
            panic!("Markers must refer to the same templated file.");
        }

        PositionMarker::new(
            start_marker.source_slice,
            start_marker.templated_slice,
            &start_marker.templated_file,
            Some(start_marker.working_line_no),
            Some(start_marker.working_line_pos),
        )
    }

    #[must_use]
    pub fn from_child_markers(markers: &[Option<PositionMarker>]) -> Self {
        let mut source_start = usize::MAX;
        let mut source_stop = usize::MIN;
        let mut templated_start = usize::MAX;
        let mut templated_stop = usize::MIN;

        let mut templated_file = None;

        for marker in markers.iter().filter_map(|m| m.as_ref()) {
            source_start = source_start.min(marker.source_slice.start);
            source_stop = source_stop.max(marker.source_slice.stop);
            templated_start = templated_start.min(marker.templated_slice.start);
            templated_stop = templated_stop.max(marker.templated_slice.stop);

            if templated_file.is_none() {
                templated_file = Some(marker.templated_file.clone());
            }
            if templated_file.as_ref() != Some(&marker.templated_file) {
                panic!("Markers must refer to the same templated file.");
            }
        }

        let source_slice = Slice::from(source_start..source_stop);
        let templated_slice = Slice::from(templated_start..templated_stop);

        PositionMarker::new(
            source_slice,
            templated_slice,
            &templated_file.unwrap(),
            None,
            None,
        )
    }
}

impl Eq for PositionMarker {}

impl PartialEq for PositionMarker {
    fn eq(&self, other: &Self) -> bool {
        self.working_loc() == other.working_loc()
    }
}

impl PartialOrd for PositionMarker {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for PositionMarker {
    fn cmp(&self, other: &Self) -> Ordering {
        self.working_loc().cmp(&other.working_loc())
    }
}

impl Display for PositionMarker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.to_source_string())
    }
}

#[must_use]
pub fn slice_is_point(test_slice: &Slice) -> bool {
    test_slice.start == test_slice.stop
}
