use hashbrown::HashMap;
use std::cmp::{max, min};

use crate::slice::Slice;

use super::fileslice::{RawFileSlice, TemplatedFileSlice};

#[derive(Debug, PartialEq, Clone, Hash)]
pub struct TemplatedFile {
    pub source_str: String,
    pub fname: String,
    pub templated_str: String,
    pub sliced_file: Vec<TemplatedFileSlice>,
    pub raw_sliced: Vec<RawFileSlice>,
    source_newlines: Vec<usize>,
    templated_newlines: Vec<usize>,
    #[cfg(feature = "unicode")]
    unicode_sliced_file: Vec<TemplatedFileSlice>,
    #[cfg(feature = "unicode")]
    unicode_raw_file: Vec<RawFileSlice>,
    #[cfg(feature = "unicode")]
    unicode_source_newlines: Vec<usize>,
    #[cfg(feature = "unicode")]
    unicode_templated_newlines: Vec<usize>,
}

impl TemplatedFile {
    pub fn new(
        source_str: String,
        fname: String,
        templated_str: Option<String>,
        sliced_file: Option<Vec<TemplatedFileSlice>>,
        raw_sliced: Option<Vec<RawFileSlice>>,
    ) -> Self {
        let templated_str_in = templated_str.clone().unwrap_or(source_str.clone());

        let (sliced_file, raw_sliced): (Vec<TemplatedFileSlice>, Vec<RawFileSlice>) =
            if let Some(s_file) = sliced_file.clone() {
                // If sliced_file is provided, ensure raw_sliced is also provided.
                match raw_sliced.clone() {
                    Some(r_file) => (s_file, r_file),
                    None => panic!("Templated file was sliced, but no raw slices provided."),
                }
            } else {
                // If sliced_file is None, ensure the file is not templated.
                if templated_str_in != source_str.clone() {
                    panic!("Cannot instantiate a templated file without slices!");
                }
                // Create "literal" slices for both sliced_file and raw_sliced.
                (
                    vec![TemplatedFileSlice::new(
                        "literal".to_string(),
                        Slice::from(0..source_str.len()),
                        Slice::from(0..source_str.len()),
                    )],
                    vec![RawFileSlice {
                        raw: source_str.clone(),
                        slice_type: "literal".to_string(),
                        source_idx: 0,
                        block_idx: 0,
                        tag: None,
                    }],
                )
            };

        let source_newlines = iter_indices_of_newlines(&source_str).collect();
        let templated_newlines = iter_indices_of_newlines(&templated_str_in).collect();

        // Consistency check raw string and slices.
        let mut pos = 0;
        for rfs in &raw_sliced {
            assert_eq!(
                rfs.source_idx, pos,
                "TemplatedFile. Consistency fail on running source length: {} != {}",
                pos, rfs.source_idx
            );
            pos += rfs.raw.len();
        }
        assert_eq!(
            pos,
            source_str.len(),
            "TemplatedFile. Consistency fail on total source length: {} != {}",
            pos,
            source_str.len()
        );

        // Consistency check templated string and slices.
        let mut previous_slice: Option<&TemplatedFileSlice> = None;
        for tfs in sliced_file.iter() {
            if let Some(prev_slice) = previous_slice {
                if tfs.templated_slice.start != prev_slice.templated_slice.stop {
                    panic!(
                        "Templated slices found to be non-contiguous. \
                        {:?} (starting {}) does not follow {:?} (starting {})",
                        tfs.templated_slice,
                        &templated_str_in[tfs.templated_slice.start..tfs.templated_slice.stop],
                        prev_slice.templated_slice,
                        &templated_str_in
                            [prev_slice.templated_slice.start..prev_slice.templated_slice.stop],
                    );
                }
            } else if tfs.templated_slice.start != 0 {
                panic!(
                    "First Templated slice not started at index 0 (found slice {:?})",
                    tfs.templated_slice
                );
            }
            previous_slice = Some(tfs);
        }

        if let Some(tfs) = sliced_file.last() {
            if let Some(templated) = templated_str.as_ref() {
                if tfs.templated_slice.stop != templated.len() {
                    panic!(
                        "Length of templated file mismatch with final slice: {} != {}.",
                        templated.len(),
                        tfs.templated_slice.stop
                    );
                }
            }
        }

        #[cfg(feature = "unicode")]
        {
            let (
                unicode_sliced_file,
                unicode_raw_file,
                unicode_source_newlines,
                unicode_templated_newlines,
            ) = get_unicode_data(&source_str, &templated_str_in, &sliced_file, &raw_sliced);

            return TemplatedFile {
                source_str,
                fname,
                templated_str: templated_str_in.to_string(),
                sliced_file,
                raw_sliced,
                source_newlines,
                templated_newlines,
                unicode_sliced_file,
                unicode_raw_file,
                unicode_source_newlines,
                unicode_templated_newlines,
            };
        }

        #[cfg(not(feature = "unicode"))]
        {
            TemplatedFile {
                source_str,
                fname,
                templated_str: templated_str_in.to_string(),
                sliced_file,
                raw_sliced,
                source_newlines,
                templated_newlines,
            }
        }
    }

    pub fn copy(
        source_str: String,
        fname: String,
        templated_str: String,
        sliced_file: Vec<TemplatedFileSlice>,
        raw_sliced: Vec<RawFileSlice>,
        source_newlines: Vec<usize>,
        templated_newlines: Vec<usize>,
    ) -> Self {
        #[cfg(feature = "unicode")]
        let (
            unicode_sliced_file,
            unicode_raw_file,
            unicode_source_newlines,
            unicode_templated_newlines,
        ) = get_unicode_data(&source_str, &templated_str, &sliced_file, &raw_sliced);
        TemplatedFile {
            source_str,
            fname,
            templated_str,
            sliced_file,
            raw_sliced,
            source_newlines,
            templated_newlines,
            #[cfg(feature = "unicode")]
            unicode_sliced_file,
            #[cfg(feature = "unicode")]
            unicode_raw_file,
            #[cfg(feature = "unicode")]
            unicode_source_newlines,
            #[cfg(feature = "unicode")]
            unicode_templated_newlines,
        }
    }

    pub fn raw_slices_spanning_source_slice(&self, source_slice: Slice) -> Vec<RawFileSlice> {
        // Special case: The source_slice is at the end of the file.
        let last_raw_slice = self.raw_sliced.last().unwrap();
        if source_slice.start >= last_raw_slice.source_idx + last_raw_slice.raw.len() {
            return vec![];
        }
        // First find the start index
        let mut raw_slice_idx = 0;
        // Move the raw pointer forward to the start of this patch
        while raw_slice_idx + 1 < self.raw_sliced.len()
            && self.raw_sliced[raw_slice_idx + 1].source_idx <= source_slice.start
        {
            raw_slice_idx += 1;
        }
        // Find slice index of the end of this patch.
        let mut slice_span = 1;
        while raw_slice_idx + slice_span < self.raw_sliced.len()
            && self.raw_sliced[raw_slice_idx + slice_span].source_idx < source_slice.stop
        {
            slice_span += 1;
        }
        // Return the raw slices:
        self.raw_sliced[raw_slice_idx..raw_slice_idx + slice_span].to_vec()
    }

    /// Convert a template
    pub fn templated_slice_to_source_slice(&self, template_slice: Slice) -> Slice {
        // If there are no sliced files, return the template slice
        if self.sliced_file.is_empty() {
            return template_slice;
        }

        // Find the indices of sliced files touching the template slice start position
        let (ts_start_sf_start, ts_start_sf_stop) =
            self.find_slice_indices_of_templated_pos(template_slice.start, None, true);

        // Get the sliced files within the found indices
        let ts_start_subsliced_file = &self.sliced_file[ts_start_sf_start..ts_start_sf_stop];

        // Work out the insertion point
        let insertion_point =
            self.get_insertion_point(ts_start_subsliced_file, template_slice.start);

        // Zero length slice
        if template_slice.start == template_slice.stop {
            // Is it on a join?
            if let Some(insertion_point) = insertion_point {
                return Slice::from(insertion_point..insertion_point);
            }
            // It's within a segment
            else if !ts_start_subsliced_file.is_empty()
                && ts_start_subsliced_file[0].slice_type == "literal"
            {
                let offset =
                    template_slice.start - ts_start_subsliced_file[0].templated_slice.start;
                return Slice::from(
                    ts_start_subsliced_file[0].source_slice.start + offset
                        ..(ts_start_subsliced_file[0].source_slice.start + offset),
                );
            } else {
                panic!("Attempting a single length slice within a templated section!");
            }
        }

        // Otherwise it's a slice with length.
        // Use a non inclusive match to get the end point.
        // Find the indices of sliced files touching the template slice end position
        let (ts_stop_sf_start, ts_stop_sf_stop) =
            self.find_slice_indices_of_templated_pos(template_slice.stop, None, false);

        // Update starting position based on insertion point
        let mut ts_start_sf_start = ts_start_sf_start;
        if insertion_point.is_some() {
            for elem in self.sliced_file.iter().skip(ts_start_sf_start) {
                if elem.source_slice.start != insertion_point.unwrap() {
                    ts_start_sf_start += 1;
                } else {
                    break;
                }
            }
        }

        // Collect relevant subslices
        let subslices = &self.sliced_file
            [min(ts_start_sf_start, ts_stop_sf_start)..max(ts_start_sf_stop, ts_stop_sf_stop)];

        if ts_start_sf_start == ts_start_sf_stop {
            if ts_start_sf_start > self.sliced_file.len() {
                panic!("Starting position higher than sliced file position");
            }
            if ts_start_sf_start < self.sliced_file.len() {
                return self.sliced_file[1].source_slice.clone();
            } else {
                return self.sliced_file.last().unwrap().source_slice.clone();
            }
        }

        // Define start and stop slices
        let start_slices = &self.sliced_file[ts_start_sf_start..ts_start_sf_stop];
        let stop_slices = if ts_stop_sf_start == ts_stop_sf_stop {
            vec![self.sliced_file[ts_stop_sf_start].clone()]
        } else {
            self.sliced_file[ts_stop_sf_start..ts_stop_sf_stop].to_vec()
        };

        // If it's a literal segment then we can get the exact position
        // otherwise we're greedy.

        // Start.
        let source_start = if insertion_point.is_some() {
            insertion_point.unwrap()
        } else if start_slices[0].slice_type == "literal" {
            let offset = template_slice.start - start_slices[0].templated_slice.start;
            start_slices[0].source_slice.start + offset
        } else {
            start_slices[0].source_slice.start
        };

        // Stop.
        let source_stop = if stop_slices.last().unwrap().slice_type == "literal" {
            let offset = stop_slices.last().unwrap().templated_slice.stop - template_slice.stop;
            stop_slices.last().unwrap().source_slice.stop - offset
        } else {
            stop_slices.last().unwrap().source_slice.stop
        };

        // Does this slice go backward?
        let (source_start, source_stop) = if source_start > source_stop {
            // If this happens, it's because one was templated and
            // the other isn't, or because a loop means that the segments
            // are in a different order.

            // Take the widest possible span in this case.
            (
                subslices
                    .iter()
                    .map(|elem| elem.source_slice.start)
                    .min()
                    .unwrap(),
                subslices
                    .iter()
                    .map(|elem| elem.source_slice.stop)
                    .max()
                    .unwrap(),
            )
        } else {
            (source_start, source_stop)
        };

        Slice::from(source_start..source_stop)
    }
}

#[cfg(feature = "unicode")]
fn get_unicode_data(
    source_str: &String,
    templated_str_in: &String,
    sliced_file: &Vec<TemplatedFileSlice>,
    raw_sliced: &Vec<RawFileSlice>,
) -> (
    Vec<TemplatedFileSlice>,
    Vec<RawFileSlice>,
    Vec<usize>,
    Vec<usize>,
) {
    let unicode_sliced_file = {
        let char_source_vec = source_str
            .char_indices()
            .map(|(i, _)| i)
            .collect::<Vec<_>>();
        let char_templated_vec = &templated_str_in
            .char_indices()
            .map(|(i, _)| i)
            .collect::<Vec<_>>();

        sliced_file
            .iter()
            .map(|slice| {
                let mut new_slice = slice.clone();

                new_slice.source_slice.start = char_source_vec
                    .iter()
                    .position(|&c| c == new_slice.source_slice.start)
                    .unwrap_or(char_source_vec.len());
                new_slice.source_slice.stop = char_source_vec
                    .iter()
                    .position(|&c| c == new_slice.source_slice.stop)
                    .unwrap_or(char_source_vec.len());
                new_slice.templated_slice.start = char_templated_vec
                    .iter()
                    .position(|&c| c == new_slice.templated_slice.start)
                    .unwrap_or(char_templated_vec.len());
                new_slice.templated_slice.stop = char_templated_vec
                    .iter()
                    .position(|&c| c == new_slice.templated_slice.stop)
                    .unwrap_or(char_templated_vec.len());

                new_slice
            })
            .collect()
    };
    let unicode_raw_file = {
        if raw_sliced.len() == 1 {
            raw_sliced.clone()
        } else {
            log::debug!("running raw utf to unicode conversion step.");
            let mut idx = 0;
            raw_sliced
                .clone()
                .iter()
                .map(|rs| {
                    let mut slice = rs.clone();
                    slice.source_idx = idx;
                    idx += slice.raw.chars().count();
                    slice
                })
                .collect::<Vec<_>>()
        }
    };
    let unicode_source_newlines = iter_codepoint_indices_of_newlines(source_str).collect();
    let unicode_templated_newlines = iter_codepoint_indices_of_newlines(templated_str_in).collect();
    (
        unicode_sliced_file,
        unicode_raw_file,
        unicode_source_newlines,
        unicode_templated_newlines,
    )
}

impl From<String> for TemplatedFile {
    fn from(raw: String) -> TemplatedFile {
        TemplatedFile::new(raw, String::from("<string>"), None, None, None)
    }
}

impl TemplatedFile {
    pub fn get_line_pos_of_char_pos(&self, char_pos: usize, source: bool) -> (usize, usize) {
        let ref_str = if source {
            &self.source_newlines
        } else {
            &self.templated_newlines
        };

        let nl_idx = ref_str.binary_search(&char_pos).unwrap_or_else(|x| x);

        if nl_idx > 0 {
            (
                (nl_idx + 1).try_into().unwrap(),
                char_pos - ref_str[nl_idx - 1],
            )
        } else {
            (1, char_pos + 1)
        }
    }

    /// Find a subset of the sliced file which touch this point.
    ///
    /// NB: the last_idx is exclusive, as the intent is to use this as a slice.
    fn find_slice_indices_of_templated_pos(
        &self,
        templated_pos: usize,
        start_idx: Option<usize>,
        inclusive: bool,
    ) -> (usize, usize) {
        let start_idx = start_idx.unwrap_or(0);
        let mut first_idx = None;
        let mut last_idx = start_idx;
        let mut found = false;

        // Work through the sliced file, starting at the start_idx if given
        // as an optimisation hint. The sliced_file is a list of TemplatedFileSlice
        // which reference parts of the templated file and where they exist in the
        // source.
        for (idx, elem) in self.sliced_file.iter().enumerate().skip(start_idx) {
            last_idx = idx + start_idx;
            if elem.templated_slice.stop >= templated_pos {
                if first_idx.is_none() {
                    first_idx = Some(idx + start_idx);
                }
                if elem.templated_slice.start > templated_pos
                    || (!inclusive && elem.templated_slice.start >= templated_pos)
                {
                    found = true;
                    break;
                }
            }
        }
        if !found {
            last_idx += 1;
        }

        if first_idx.is_none() {
            panic!("Position Not Found");
        }

        (first_idx.unwrap(), last_idx)
    }

    pub fn get_insertion_point(
        &self,
        subsliced_file: &[TemplatedFileSlice],
        template_slice_start: usize,
    ) -> Option<usize> {
        let mut insertion_point = None;

        for elem in subsliced_file {
            if elem.templated_slice.start == template_slice_start {
                let source_start = elem.source_slice.start;
                if insertion_point.is_none() || source_start < insertion_point.unwrap() {
                    insertion_point = Some(source_start);
                }
            }
            if elem.templated_slice.stop == template_slice_start {
                let source_stop = elem.source_slice.stop;
                if insertion_point.is_none() || source_stop < insertion_point.unwrap() {
                    insertion_point = Some(source_stop);
                }
            }
        }

        insertion_point
    }

    pub fn is_source_slice_literal(&self, source_slice: &Slice) -> bool {
        // No sliced file? Everything is literal
        if self.raw_sliced.is_empty() {
            return true;
        }

        // Zero length slice. It's a literal, because it's definitely not templated.
        if source_slice.start == source_slice.stop {
            return true;
        }

        let mut is_literal = true;
        for raw_slice in &self.raw_sliced {
            // Reset if we find a literal and we're up to the start
            // otherwise set false.
            if raw_slice.source_idx <= source_slice.start {
                is_literal = raw_slice.slice_type == "literal";
            } else if raw_slice.source_idx >= source_slice.stop {
                // We've gone past the end. Break and Return.
                break;
            } else {
                // We're in the middle. Check type
                if raw_slice.slice_type != "literal" {
                    is_literal = false;
                }
            }
        }

        is_literal
    }

    pub fn source_only_slices(&self) -> Vec<RawFileSlice> {
        self.raw_sliced
            .iter()
            .filter(|elem| elem.is_source_only_slice())
            .cloned()
            .collect()
    }

    pub fn source_position_dict_from_slice(&self, source_slice: &Slice) -> HashMap<String, usize> {
        let start = self.get_line_pos_of_char_pos(source_slice.start, true);
        let stop = self.get_line_pos_of_char_pos(source_slice.stop, true);
        let mut dict = HashMap::new();
        dict.insert("start_line_no".to_string(), start.0);
        dict.insert("start_line_pos".to_string(), start.1);
        dict.insert("start_file_pos".to_string(), source_slice.start);
        dict.insert("end_line_no".to_string(), stop.0);
        dict.insert("end_line_pos".to_string(), stop.1);
        dict.insert("end_file_pos".to_string(), source_slice.stop);
        dict
    }
}

impl std::fmt::Display for TemplatedFile {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.templated_str)
    }
}

fn iter_indices_of_newlines(raw_str: &str) -> impl Iterator<Item = usize> + '_ {
    raw_str.match_indices('\n').map(|(idx, _)| idx)
}

#[cfg(feature = "unicode")]
fn iter_codepoint_indices_of_newlines(raw_str: &str) -> impl Iterator<Item = usize> + '_ {
    raw_str
        .char_indices()
        .filter(|(_i, c)| *c == '\n')
        .map(|(idx, _)| idx)
}

#[cfg(feature = "python")]
pub mod python {
    use std::hash::{DefaultHasher, Hash, Hasher};
    use std::sync::{Arc, Mutex};
    use std::time::Instant;

    use hashbrown::HashMap;
    use pyo3::IntoPyObjectExt;
    use pyo3::{prelude::*, types::PyType};

    use crate::slice::Slice;
    use crate::templater::fileslice::python::sqlfluff::{
        PySqlFluffRawFileSlice, PySqlFluffTemplatedFileSlice,
    };
    use crate::templater::fileslice::python::*;
    use crate::templater::fileslice::{RawFileSlice, TemplatedFileSlice};

    use super::TemplatedFile;
    use once_cell::sync::Lazy;

    // fn utf8_to_unicode_slices(tf: &TemplatedFile) -> Vec<PyTemplatedFileSlice> {
    //     log::debug!("running tf utf to unicode conversion step.");
    //     let char_source_vec = tf
    //         .source_str
    //         .char_indices()
    //         .map(|(i, _)| i)
    //         .collect::<Vec<_>>();
    //     let char_templated_vec = tf
    //         .templated_str
    //         .char_indices()
    //         .map(|(i, _)| i)
    //         .collect::<Vec<_>>();

    //     tf.sliced_file
    //         .iter()
    //         .map(|slice| {
    //             let mut new_slice = PyTemplatedFileSlice(slice.clone()); // Wrap TemplatedFileSlice in PyTemplatedFileSlice

    //             new_slice.0.source_slice.start = char_source_vec
    //                 .iter()
    //                 .position(|&c| c == new_slice.0.source_slice.start)
    //                 .unwrap_or(char_source_vec.len());
    //             new_slice.0.source_slice.stop = char_source_vec
    //                 .iter()
    //                 .position(|&c| c == new_slice.0.source_slice.stop)
    //                 .unwrap_or(char_source_vec.len());
    //             new_slice.0.templated_slice.start = char_templated_vec
    //                 .iter()
    //                 .position(|&c| c == new_slice.0.templated_slice.start)
    //                 .unwrap_or(char_templated_vec.len());
    //             new_slice.0.templated_slice.stop = char_templated_vec
    //                 .iter()
    //                 .position(|&c| c == new_slice.0.templated_slice.stop)
    //                 .unwrap_or(char_templated_vec.len());

    //             // log::debug!(
    //             //     "{:?}::{:?}",
    //             //     new_slice.0.source_slice, new_slice.0.templated_slice
    //             // );

    //             new_slice
    //         })
    //         .collect()
    // }

    // fn raw_slices_to_py(tf: &TemplatedFile) -> Vec<PyRawFileSlice> {
    //     log::debug!("running raw utf to unicode conversion step.");
    //     if tf.raw_sliced.len() == 1 {
    //         return tf.raw_sliced.clone().into_iter().map(Into::into).collect();
    //     }
    //     let mut idx = 0;
    //     tf.raw_sliced
    //         .iter()
    //         .map(|rs| {
    //             let mut slice = rs.clone();
    //             slice.source_idx = idx;
    //             idx += slice.raw.chars().count();
    //             PyRawFileSlice(slice)
    //         })
    //         .collect()
    // }

    #[pyclass(name = "RsTemplatedFile", frozen)]
    #[repr(transparent)]
    #[derive(Clone, PartialEq, Hash)]
    pub struct PyTemplatedFile(pub Arc<TemplatedFile>);

    #[pymethods]
    impl PyTemplatedFile {
        #[new]
        #[pyo3(signature = (source_str, fname, templated_str=None, sliced_file=None, raw_sliced=None))]
        pub fn new(
            source_str: String,
            fname: String,
            templated_str: Option<String>,
            sliced_file: Option<Vec<PyTemplatedFileSlice>>,
            raw_sliced: Option<Vec<PyRawFileSlice>>,
        ) -> Self {
            log::debug!("PyTemplatedFile::new");
            let tf = Arc::new(TemplatedFile::new(
                source_str,
                fname,
                templated_str,
                sliced_file.map(|x| x.into_iter().map(Into::into).collect()),
                raw_sliced.map(|x| x.into_iter().map(Into::into).collect()),
            ));
            // let unicode_sliced_file = utf8_to_unicode_slices(&tf);
            // let unicode_raw_sliced = raw_slices_to_py(&tf);
            Self(tf)
        }

        #[classmethod]
        pub fn from_string(_cls: &Bound<'_, PyType>, raw: String) -> Self {
            log::debug!("PyTemplatedFile::from_string");
            let tf = Arc::new(TemplatedFile::from(raw));
            // let unicode_sliced_file = utf8_to_unicode_slices(&tf);
            // let unicode_raw_sliced = raw_slices_to_py(&tf);
            Self(tf)
        }

        #[getter]
        fn source_str(&self) -> PyResult<String> {
            Ok(self.0.source_str.clone())
        }

        #[getter]
        fn fname(&self) -> PyResult<String> {
            Ok(self.0.fname.clone())
        }

        #[getter]
        fn templated_str(&self) -> PyResult<String> {
            Ok(self.0.templated_str.clone())
        }

        #[getter]
        fn sliced_file(&self) -> Vec<PyTemplatedFileSlice> {
            self.0
                .unicode_sliced_file
                .clone()
                .into_iter()
                .map(Into::into)
                .collect()
        }

        #[getter]
        fn raw_sliced(&self) -> Vec<PyRawFileSlice> {
            self.0
                .unicode_raw_file
                .clone()
                .into_iter()
                .map(Into::into)
                .collect()
        }

        #[getter("_source_newlines")]
        fn source_newlines(&self) -> PyResult<Vec<usize>> {
            let newlines = iter_indices_of_unicode_newlines(&self.0.source_str).collect();
            Ok(newlines)
        }

        #[getter("_templated_newlines")]
        fn templated_newlines(&self) -> PyResult<Vec<usize>> {
            let newlines = iter_indices_of_unicode_newlines(&self.0.templated_str).collect();
            Ok(newlines)
        }

        fn __str__(&self) -> PyResult<String> {
            Ok(self.0.templated_str.clone())
        }

        fn __repr__(&self) -> PyResult<String> {
            Ok(String::from("<TemplatedFile>"))
        }

        fn __eq__(&self, other: &Self) -> bool {
            self.0 == other.0
        }

        fn __hash__(&self) -> u64 {
            let mut hasher = DefaultHasher::new();
            self.0.hash(&mut hasher);
            hasher.finish()
        }

        fn get_line_pos_of_char_pos(
            &self,
            char_pos: usize,
            source: bool,
        ) -> PyResult<(usize, usize)> {
            Ok(self.0.get_line_pos_of_char_pos(char_pos, source))
        }

        pub fn is_source_slice_literal(&self, source_slice: Slice) -> bool {
            self.0.is_source_slice_literal(&source_slice)
        }

        pub fn source_position_dict_from_slice(
            &self,
            source_slice: Slice,
        ) -> HashMap<String, usize> {
            self.0.source_position_dict_from_slice(&source_slice)
        }
    }

    impl PyTemplatedFile {
        fn from_python(
            source_str: String,
            fname: String,
            templated_str: String,
            sliced_file: Vec<TemplatedFileSlice>,
            raw_sliced: Vec<RawFileSlice>,
            source_newlines: Vec<usize>,
            templated_newlines: Vec<usize>,
        ) -> Self {
            // let t1 = Instant::now();
            log::debug!("PyTemplatedFile::from_python: {}", fname);
            // let source_newlines = iter_indices_of_newlines(&source_str).collect();
            // let templated_newlines = iter_indices_of_newlines(&templated_str).collect();
            let tf = Arc::new(TemplatedFile::copy(
                source_str,
                fname,
                templated_str,
                sliced_file,
                raw_sliced,
                source_newlines,
                templated_newlines,
            ));
            // let unicode_sliced_file = utf8_to_unicode_slices(&tf);
            // let unicode_raw_sliced = raw_slices_to_py(&tf);
            // let t2 = t1.elapsed();
            // log::debug!("PyTemplatedFile::from_python: took {:?}", t2.as_nanos());
            Self(tf)
        }

        fn py_raw_slices(raw_sliced: &[PyRawFileSlice]) -> Vec<RawFileSlice> {
            if raw_sliced.len() == 1 {
                return raw_sliced
                    .into_iter()
                    .map(|s| s.0.clone())
                    .collect::<Vec<_>>();
            }
            let mut idx = 0;
            raw_sliced
                .iter()
                .map(|rs| {
                    let mut slice = rs.0.clone();
                    slice.source_idx = idx;
                    idx += slice.raw.len();
                    slice
                })
                .collect()
        }

        fn unicode_to_utf8_slices(
            source_str: &str,
            templated_str: &str,
            sliced_file: &[PyTemplatedFileSlice],
        ) -> Vec<TemplatedFileSlice> {
            if source_str.len()
                == sliced_file
                    .last()
                    .map(|s| s.0.source_slice.stop)
                    .unwrap_or(0)
                && source_str.len()
                    == sliced_file
                        .last()
                        .map(|s| s.0.templated_slice.stop)
                        .unwrap_or(0)
            {
                return sliced_file.iter().map(|ts| ts.0.clone()).collect();
            }
            let char_source_vec = source_str.char_indices().enumerate().collect::<Vec<_>>();
            let char_templated_vec = templated_str.char_indices().enumerate().collect::<Vec<_>>();

            sliced_file
                .iter()
                .map(|py_slice| {
                    let mut new_slice = py_slice.0.clone(); // Extract TemplatedFileSlice and clone it

                    new_slice.source_slice.start = char_source_vec
                        .get(new_slice.source_slice.start)
                        .map(|c| c.0)
                        .unwrap_or_else(|| char_source_vec.len());
                    new_slice.source_slice.stop = char_source_vec
                        .get(new_slice.source_slice.stop)
                        .map(|c| c.0)
                        .unwrap_or_else(|| char_source_vec.len());
                    new_slice.templated_slice.start = char_templated_vec
                        .get(new_slice.templated_slice.start)
                        .map(|c| c.0)
                        .unwrap_or_else(|| char_templated_vec.len());
                    new_slice.templated_slice.stop = char_templated_vec
                        .get(new_slice.templated_slice.stop)
                        .map(|c| c.0)
                        .unwrap_or_else(|| char_templated_vec.len());

                    // log::debug!("{:?}", new_slice);

                    new_slice
                })
                .collect()
        }
    }

    // impl From<TemplatedFile> for PyTemplatedFile {
    //     fn from(value: TemplatedFile) -> Self {
    //         PyTemplatedFile(value)
    //     }
    // }

    // impl Into<TemplatedFile> for PyTemplatedFile {
    //     fn into(self) -> TemplatedFile {
    //         self.tf
    //     }
    // }

    impl From<Arc<TemplatedFile>> for PyTemplatedFile {
        fn from(value: Arc<TemplatedFile>) -> Self {
            log::debug!("PyTemplatedFile::from<ArcTemplated> {}", value.fname);
            // let unicode_sliced_file = utf8_to_unicode_slices(&value);
            // let unicode_raw_sliced = raw_slices_to_py(&value);
            Self(value)
        }
    }

    impl Into<Arc<TemplatedFile>> for PyTemplatedFile {
        fn into(self) -> Arc<TemplatedFile> {
            log::debug!("PyTemplatedFile::into<ArcTemplated>");
            self.0
        }
    }

    impl<'py> IntoPyObject<'py> for PySqlFluffTemplatedFile {
        type Target = PyAny;
        type Output = Bound<'py, Self::Target>;
        type Error = PyErr;

        fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
            log::debug!("PySFTemplatedFile::into_py {}", self.0 .0.fname.clone());
            // let tf = Arc::new(TemplatedFile {
            //     source_str: self.0.tf.source_str.clone(),
            //     fname: self.0.tf.fname.clone(),
            //     templated_str: self.0.tf.templated_str.clone(),
            //     sliced_file: self.0.tf.sliced_file.clone(),
            //     raw_sliced: self.0.tf.raw_sliced.clone(),
            //     source_newlines: self.0.tf.source_newlines.clone(),
            //     templated_newlines: self.0.tf.templated_newlines.clone(),
            // });
            // let unicode_sliced_file = utf8_to_unicode_slices(&tf);
            // let unicode_raw_sliced = raw_slices_to_py(&tf);
            // PyTemplatedFile {
            //     tf: self.0.tf,
            //     unicode_sliced_file: self.0.unicode_sliced_file,
            //     unicode_raw_sliced: self.0.raw_sliced(),
            // }
            self.0.into_bound_py_any(py)
        }
    }

    static PY_TEMPLATED_FILE_CACHE: Lazy<Mutex<HashMap<String, Arc<TemplatedFile>>>> =
        Lazy::new(|| Mutex::new(HashMap::new()));

    #[derive(Clone)]
    pub struct PySqlFluffTemplatedFile(pub PyTemplatedFile);

    impl<'py> FromPyObject<'py> for PySqlFluffTemplatedFile {
        fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
            // let t1 = Instant::now();
            let source_str = obj.getattr("source_str")?.extract::<String>()?;
            let fname = obj.getattr("fname")?.extract::<String>()?;
            let templated_str = obj.getattr("templated_str")?.extract::<String>()?;

            let key = format!("{}:{}:{}", fname, &source_str, &templated_str);
            let mut cache = PY_TEMPLATED_FILE_CACHE.lock().unwrap();

            if let Some(cached) = cache.get(&key) {
                return Ok(Self(PyTemplatedFile(cached.clone())));
            }

            let py_sliced_file = obj
                .getattr("sliced_file")?
                .extract::<Vec<PySqlFluffTemplatedFileSlice>>()?
                .into_iter()
                .map(Into::into)
                .collect::<Vec<_>>();
            let sliced_file = PyTemplatedFile::unicode_to_utf8_slices(
                &source_str,
                &templated_str,
                &py_sliced_file,
            );

            let py_raw_sliced = obj
                .getattr("raw_sliced")?
                .extract::<Vec<PySqlFluffRawFileSlice>>()?
                .into_iter()
                .map(Into::into)
                .collect::<Vec<_>>();
            let raw_sliced = PyTemplatedFile::py_raw_slices(&py_raw_sliced);

            let py_source_newlines = obj.getattr("_source_newlines")?.extract::<Vec<usize>>()?;
            let py_templated_newlines = obj
                .getattr("_templated_newlines")?
                .extract::<Vec<usize>>()?;

            // let t2 = t1.elapsed();
            // log::debug!("PySqlFluffTemplatedFile::extract_bound: {}", t2.as_nanos());

            let tf = Self(
                PyTemplatedFile::from_python(
                    source_str,
                    fname,
                    templated_str,
                    sliced_file,
                    raw_sliced,
                    py_source_newlines,
                    py_templated_newlines,
                )
                .into(),
            );

            cache.insert(key, tf.0 .0.clone());
            Ok(tf)
        }
    }

    impl Into<PyTemplatedFile> for PySqlFluffTemplatedFile {
        fn into(self) -> PyTemplatedFile {
            self.0
        }
    }

    impl Into<Arc<TemplatedFile>> for PySqlFluffTemplatedFile {
        fn into(self) -> Arc<TemplatedFile> {
            self.0 .0
        }
    }

    fn iter_indices_of_unicode_newlines(raw_str: &str) -> impl Iterator<Item = usize> + '_ {
        raw_str
            .char_indices()
            .enumerate()
            .filter(|&(_i, (_ci, c))| c == '\n')
            .map(|(i, (_, _))| i)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Clone)]
    struct TestFileArgs {
        fname: String,
        sliced_file: Vec<TemplatedFileSlice>,
        templated_str: Option<String>,
        raw_sliced: Vec<RawFileSlice>,
        source_str: String,
    }

    fn simple_file_kwargs() -> TestFileArgs {
        TestFileArgs {
            fname: "test.sql".to_string(),
            source_str: "01234\n6789{{foo}}fo\nbarss".to_string(),
            templated_str: Some("01234\n6789x\nfo\nbarss".to_string()),
            sliced_file: vec![
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(0..10),
                    Slice::from(0..10),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(10..17),
                    Slice::from(10..12),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(17..25),
                    Slice::from(12..20),
                ),
            ],
            raw_sliced: vec![
                RawFileSlice::new("x".repeat(10), "literal".to_string(), 0, None, None),
                RawFileSlice::new("x".repeat(7), "templated".to_string(), 10, None, None),
                RawFileSlice::new("x".repeat(8), "literal".to_string(), 17, None, None),
            ],
        }
    }

    fn complex_raw_sliced() -> Vec<RawFileSlice> {
        vec![
            RawFileSlice::new("x".repeat(13), "literal".to_string(), 0, None, None),
            RawFileSlice::new("x".repeat(16), "comment".to_string(), 13, None, None),
            RawFileSlice::new("x".repeat(15), "literal".to_string(), 29, None, None),
            RawFileSlice::new("x".repeat(24), "block_start".to_string(), 44, None, None),
            RawFileSlice::new("x".repeat(13), "literal".to_string(), 68, None, None),
            RawFileSlice::new("x".repeat(5), "templated".to_string(), 81, None, None),
            RawFileSlice::new("x".repeat(24), "literal".to_string(), 86, None, None),
            RawFileSlice::new("x".repeat(13), "templated".to_string(), 110, None, None),
            RawFileSlice::new("x".repeat(9), "literal".to_string(), 123, None, None),
            RawFileSlice::new("x".repeat(12), "block_end".to_string(), 132, None, None),
            RawFileSlice::new("x".repeat(11), "literal".to_string(), 144, None, None),
            RawFileSlice::new("x".repeat(24), "block_start".to_string(), 155, None, None),
            RawFileSlice::new("x".repeat(10), "literal".to_string(), 179, None, None),
            RawFileSlice::new("x".repeat(5), "templated".to_string(), 189, None, None),
            RawFileSlice::new("x".repeat(9), "literal".to_string(), 194, None, None),
            RawFileSlice::new("x".repeat(12), "block_end".to_string(), 203, None, None),
            RawFileSlice::new("x".repeat(15), "literal".to_string(), 215, None, None),
        ]
    }

    fn complex_file_kwargs() -> TestFileArgs {
        let raw_sliced = complex_raw_sliced();

        TestFileArgs {
            fname: "test.sql".to_string(),
            sliced_file: vec![
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(0..13),
                    Slice::from(0..13),
                ),
                TemplatedFileSlice::new(
                    "comment".to_string(),
                    Slice::from(13..29),
                    Slice::from(13..13),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(29..44),
                    Slice::from(13..28),
                ),
                TemplatedFileSlice::new(
                    "block_start".to_string(),
                    Slice::from(44..68),
                    Slice::from(28..28),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(68..81),
                    Slice::from(28..41),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(81..86),
                    Slice::from(41..42),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(86..110),
                    Slice::from(42..66),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(68..86),
                    Slice::from(66..76),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(68..81),
                    Slice::from(76..89),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(81..86),
                    Slice::from(89..90),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(86..110),
                    Slice::from(90..114),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(68..86),
                    Slice::from(114..125),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(68..81),
                    Slice::from(125..138),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(81..86),
                    Slice::from(138..139),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(86..110),
                    Slice::from(139..163),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(110..123),
                    Slice::from(163..166),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(123..132),
                    Slice::from(166..175),
                ),
                TemplatedFileSlice::new(
                    "block_end".to_string(),
                    Slice::from(132..144),
                    Slice::from(175..175),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(144..155),
                    Slice::from(175..186),
                ),
                TemplatedFileSlice::new(
                    "block_start".to_string(),
                    Slice::from(155..179),
                    Slice::from(186..186),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(179..189),
                    Slice::from(186..196),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(189..194),
                    Slice::from(196..197),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(194..203),
                    Slice::from(197..206),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(179..189),
                    Slice::from(206..216),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(189..194),
                    Slice::from(216..217),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(194..203),
                    Slice::from(217..226),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(179..189),
                    Slice::from(226..236),
                ),
                TemplatedFileSlice::new(
                    "templated".to_string(),
                    Slice::from(189..194),
                    Slice::from(236..237),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(194..203),
                    Slice::from(237..246),
                ),
                TemplatedFileSlice::new(
                    "block_end".to_string(),
                    Slice::from(203..215),
                    Slice::from(246..246),
                ),
                TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(215..230),
                    Slice::from(246..261),
                ),
            ],
            raw_sliced: raw_sliced.clone(),
            source_str: raw_sliced
                .iter()
                .map(|slice| &*slice.raw)
                .collect::<String>(),
            templated_str: None,
        }
    }

    #[test]
    fn test_indices_of_newlines() {
        let test_cases = vec![
            ("", vec![]),
            ("foo", vec![]),
            ("foo\nbar", vec![3]),
            ("\nfoo\n\nbar\nfoo\n\nbar\n", vec![0, 4, 5, 9, 13, 14, 18]),
        ];

        for (raw_str, positions) in test_cases {
            assert_eq!(
                iter_indices_of_newlines(raw_str).collect::<Vec<_>>(),
                positions
            );
        }
    }

    #[test]
    fn test_templated_file_find_slice_indices_of_templated_pos() {
        let complex_file_kwargs = complex_file_kwargs();
        let simple_file_kwargs = simple_file_kwargs();
        let test_cases: Vec<(usize, bool, TestFileArgs, usize, usize)> = vec![
            (100, true, complex_file_kwargs.clone(), 10, 11),
            (13, true, complex_file_kwargs.clone(), 0, 3),
            (28, true, complex_file_kwargs.clone(), 2, 5),
            // Check end slicing.
            (12, true, simple_file_kwargs.clone(), 1, 3),
            (20, true, simple_file_kwargs.clone(), 2, 3),
            // Check inclusivity
            (13, false, complex_file_kwargs.clone(), 0, 1),
        ];

        for (templated_position, inclusive, tf_kwargs, sliced_idx_start, sliced_idx_stop) in
            test_cases
        {
            let file = TemplatedFile::new(
                tf_kwargs.source_str,
                tf_kwargs.fname,
                tf_kwargs.templated_str,
                Some(tf_kwargs.sliced_file),
                Some(tf_kwargs.raw_sliced),
            );
            let (res_start, res_stop) =
                file.find_slice_indices_of_templated_pos(templated_position, None, inclusive);
            assert_eq!(res_start, sliced_idx_start);
            assert_eq!(res_stop, sliced_idx_stop);
        }
    }

    #[test]
    fn test_templated_file_templated_slice_to_source_slice() {
        let complex_file_kwargs = complex_file_kwargs();
        let simple_file_kwargs = simple_file_kwargs();
        let test_cases: Vec<(
            String,
            String,
            Option<String>,
            Slice,
            Slice,
            bool,
            Vec<TemplatedFileSlice>,
            Vec<RawFileSlice>,
        )> = vec![
            // Simple example
            (
                "foo.sql".to_string(),
                "x".repeat(20).to_string(),
                None,
                Slice::from(5..10),
                Slice::from(5..10),
                true,
                vec![TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(0..20),
                    Slice::from(0..20),
                )],
                vec![RawFileSlice::new(
                    "x".repeat(20),
                    "literal".to_string(),
                    0,
                    None,
                    None,
                )],
            ),
            // Trimming the end of a literal (with things that follow).
            (
                "test.sql".to_string(),
                complex_file_kwargs.source_str.clone(),
                None,
                Slice::from(10..13),
                Slice::from(10..13),
                true,
                complex_file_kwargs.sliced_file.clone(),
                complex_file_kwargs.raw_sliced.clone(),
            ),
            // Unrealistic, but should still work
            (
                "foo.sql".to_string(),
                "x".repeat(70).to_string(),
                None,
                Slice::from(5..10),
                Slice::from(55..60),
                true,
                vec![TemplatedFileSlice::new(
                    "literal".to_string(),
                    Slice::from(50..70),
                    Slice::from(0..20),
                )],
                vec![
                    RawFileSlice::new("x".repeat(50), "literal".to_string(), 0, None, None),
                    RawFileSlice::new("x".repeat(20), "literal".to_string(), 50, None, None),
                ],
            ),
            // Spanning a template
            (
                "test.sql".to_string(),
                "01234\n6789{{foo}}fo\nbarss".to_string(),
                Some("01234\n6789x\nfo\nbarss".to_string()),
                Slice::from(5..15),
                Slice::from(5..20),
                false,
                vec![
                    TemplatedFileSlice::new(
                        "literal".to_string(),
                        Slice::from(0..10),
                        Slice::from(0..10),
                    ),
                    TemplatedFileSlice::new(
                        "templated".to_string(),
                        Slice::from(10..17),
                        Slice::from(10..12),
                    ),
                    TemplatedFileSlice::new(
                        "literal".to_string(),
                        Slice::from(17..25),
                        Slice::from(12..20),
                    ),
                ],
                vec![
                    RawFileSlice::new("x".repeat(10), "literal".to_string(), 0, None, None),
                    RawFileSlice::new("x".repeat(7), "templated".to_string(), 10, None, None),
                    RawFileSlice::new("x".repeat(8), "literal".to_string(), 17, None, None),
                ],
            ),
            // Handling templated
            (
                simple_file_kwargs.clone().fname,
                simple_file_kwargs.clone().source_str,
                simple_file_kwargs.clone().templated_str,
                Slice::from(5..15),
                Slice::from(0..25),
                false,
                simple_file_kwargs
                    .sliced_file
                    .iter()
                    .map(|slc| {
                        TemplatedFileSlice::new(
                            "templated".to_string(),
                            slc.source_slice.clone(),
                            slc.templated_slice.clone(),
                        )
                    })
                    .collect(),
                simple_file_kwargs
                    .raw_sliced
                    .iter()
                    .map(|slc| {
                        RawFileSlice::new(
                            slc.raw.clone(),
                            "templated".to_string(),
                            slc.source_idx.clone(),
                            None,
                            None,
                        )
                    })
                    .collect(),
            ),
            // Handling single length slices
            (
                simple_file_kwargs.fname.clone(),
                simple_file_kwargs.source_str.clone(),
                simple_file_kwargs.templated_str.clone(),
                Slice::from(10..10),
                Slice::from(10..10),
                true,
                simple_file_kwargs.sliced_file.clone(),
                simple_file_kwargs.raw_sliced.clone(),
            ),
            (
                simple_file_kwargs.fname.clone(),
                simple_file_kwargs.source_str.clone(),
                simple_file_kwargs.templated_str.clone(),
                Slice::from(12..12),
                Slice::from(17..17),
                true,
                simple_file_kwargs.sliced_file.clone(),
                simple_file_kwargs.raw_sliced.clone(),
            ),
            // Dealing with single length elements
            {
                let extended_source_str = simple_file_kwargs.source_str.clone() + &"x".repeat(10);
                let extended_sliced_file: Vec<TemplatedFileSlice> = {
                    let mut sliced_file = simple_file_kwargs.sliced_file.clone();
                    sliced_file.push(TemplatedFileSlice::new(
                        "comment".to_string(),
                        Slice::from(25..35),
                        Slice::from(20..20),
                    ));
                    sliced_file
                };
                let extended_raw_sliced: Vec<RawFileSlice> = {
                    let mut raw_sliced = simple_file_kwargs.raw_sliced.clone();
                    raw_sliced.push(RawFileSlice::new(
                        "x".repeat(10),
                        "comment".to_string(),
                        25,
                        None,
                        None,
                    ));
                    raw_sliced
                };
                (
                    "foo.sql".to_string(),
                    extended_source_str,
                    None,
                    Slice::from(20..20),
                    Slice::from(25..25),
                    true,
                    extended_sliced_file,
                    extended_raw_sliced,
                )
            },
            // Just more test coverage
            (
                complex_file_kwargs.fname.clone(),
                complex_file_kwargs.source_str.clone(),
                complex_file_kwargs.templated_str.clone(),
                Slice::from(43..43),
                Slice::from(87..87),
                true,
                complex_file_kwargs.sliced_file.clone(),
                complex_file_kwargs.raw_sliced.clone(),
            ),
            (
                complex_file_kwargs.fname.clone(),
                complex_file_kwargs.source_str.clone(),
                complex_file_kwargs.templated_str.clone(),
                Slice::from(13..13),
                Slice::from(13..13),
                true,
                complex_file_kwargs.sliced_file.clone(),
                complex_file_kwargs.raw_sliced.clone(),
            ),
            (
                complex_file_kwargs.fname.clone(),
                complex_file_kwargs.source_str.clone(),
                complex_file_kwargs.templated_str.clone(),
                Slice::from(186..186),
                Slice::from(155..155),
                true,
                complex_file_kwargs.sliced_file.clone(),
                complex_file_kwargs.raw_sliced.clone(),
            ),
            // // Backward slicing.
            (
                complex_file_kwargs.fname.clone(),
                complex_file_kwargs.source_str.clone(),
                complex_file_kwargs.templated_str.clone(),
                Slice::from(100..130),
                Slice::from(68..110),
                false,
                complex_file_kwargs.sliced_file.clone(),
                complex_file_kwargs.raw_sliced.clone(),
            ),
        ];

        for (
            fname,
            source_str,
            templated_str,
            in_slice,
            out_slice,
            is_literal,
            sliced_file,
            raw_sliced,
        ) in test_cases
        {
            let file = TemplatedFile::new(
                source_str,
                fname,
                templated_str,
                Some(sliced_file),
                Some(raw_sliced),
            );
            let source_slice = file.templated_slice_to_source_slice(in_slice.clone());
            let literal_test = file.is_source_slice_literal(&source_slice);
            assert_eq!(
                (is_literal, source_slice.clone()),
                (literal_test, out_slice)
            );
        }
    }

    // #[test]
    // fn test_raw_templater() {
    //     let mut t = RawTemplater::new();
    //     let instr = "SELECT * FROM {{blah}}";
    //     let tf = t.process(instr, "test");
    //     assert_eq!(instr, &tf.source_str);
    // }
}
