//! PyO3 bindings for the arena tree.
//!
//! Exposes two Python classes:
//!
//! * `RsTree` — owns the arena (`Arc<Mutex<Arena>>`) for the lifetime of a
//!   parse; built via `RsMatchResult.apply_as_tree` and attached to the root
//!   segment as `_rs_tree`.
//! * `RsHandle` — a lightweight cursor `(arena, NodeId)` (a shared `Arc` plus an
//!   index, no subtree clone) that the Python `RsSegment` façade wraps.  Every
//!   accessor runs Rust-side; only thin handles and scalars cross FFI.
//!
//! The arena is shared behind `Arc<Mutex<…>>` so both classes are `Send` (the
//! linter moves the parse tree across worker threads).  Access is GIL-bound and
//! single-threaded in practice, so the mutex is uncontended; no lock is ever
//! held across a call back into Python.

use std::sync::{Arc, Mutex};

use pyo3::prelude::*;

use sqlfluffrs_python::marker::PyPositionMarker;

use super::arena::{Arena, NodeId};

/// The arena is shared behind `Arc<Mutex<…>>` rather than `Rc<RefCell<…>>` so
/// that `RsTree`/`RsHandle` are `Send` — the linter moves the parse tree (which
/// carries the tree on its root) across worker threads, and an `unsendable`
/// pyclass would panic when dropped off its origin thread.  All access is
/// GIL-bound and single-threaded in practice, so the mutex is uncontended; no
/// lock is ever held across a call back into Python.
type ArenaRef = Arc<Mutex<Arena>>;

/// Owner of an arena tree.  Dropping the last `RsTree`/`RsHandle` frees it.
#[pyclass(name = "RsTree", module = "sqlfluffrs")]
pub struct PyTree {
    inner: ArenaRef,
}

impl PyTree {
    pub(crate) fn new(arena: Arena) -> Self {
        PyTree {
            inner: Arc::new(Mutex::new(arena)),
        }
    }

    fn handle(&self, node: NodeId) -> PyHandle {
        PyHandle {
            inner: self.inner.clone(),
            node,
        }
    }

    /// Run a closure with read access to the underlying arena.
    ///
    /// This is the bridge for out-of-crate consumers (e.g. the rules crate's
    /// PyO3 bindings): it locks the arena once and hands a `&Arena` to `f`,
    /// keeping the `Arc<Mutex<…>>` encapsulated here.
    pub fn with_arena<R>(&self, f: impl FnOnce(&Arena) -> R) -> R {
        let guard = self.inner.lock().unwrap();
        f(&guard)
    }
}

#[pymethods]
impl PyTree {
    /// The root node handle.
    #[getter]
    fn root(&self) -> PyHandle {
        let root = self.inner.lock().unwrap().root();
        self.handle(root)
    }

    /// Number of nodes in the arena.
    fn __len__(&self) -> usize {
        self.inner.lock().unwrap().len()
    }

    /// Resolve a handle from a node uuid (used by fix anchoring in later
    /// milestones; available now for parity tests).
    fn node_by_uuid(&self, uuid: u128) -> Option<PyHandle> {
        let id = self.inner.lock().unwrap().node_by_uuid(uuid);
        id.map(|n| self.handle(n))
    }

    fn __repr__(&self) -> String {
        format!("RsTree(nodes={})", self.inner.lock().unwrap().len())
    }
}

/// A cursor into an arena tree.
#[pyclass(name = "RsHandle", module = "sqlfluffrs", skip_from_py_object)]
#[derive(Clone)]
pub struct PyHandle {
    inner: ArenaRef,
    node: NodeId,
}

impl PyHandle {
    fn wrap(&self, node: NodeId) -> PyHandle {
        PyHandle {
            inner: self.inner.clone(),
            node,
        }
    }

    fn wrap_many(&self, ids: Vec<NodeId>) -> Vec<PyHandle> {
        ids.into_iter().map(|n| self.wrap(n)).collect()
    }
}

#[pymethods]
impl PyHandle {
    // -- identity ------------------------------------------------------------

    #[getter]
    fn uuid(&self) -> u128 {
        self.inner.lock().unwrap().uuid(self.node)
    }

    fn __eq__(&self, other: &PyHandle) -> bool {
        // Same arena + same uuid.  (Handles into different arenas are never
        // equal even if uuids collided, which they don't in practice.)
        // Lock once: `Mutex` is not re-entrant, so comparing two handles into
        // the same arena must not take the lock twice.
        if !Arc::ptr_eq(&self.inner, &other.inner) {
            return false;
        }
        let arena = self.inner.lock().unwrap();
        arena.uuid(self.node) == arena.uuid(other.node)
    }

    fn __hash__(&self) -> u64 {
        // Lower 64 bits of the uuid; matches the façade's `__hash__`.
        self.inner.lock().unwrap().uuid(self.node) as u64
    }

    // -- payload -------------------------------------------------------------

    #[getter]
    fn raw(&self) -> String {
        self.inner.lock().unwrap().raw(self.node)
    }

    #[getter]
    fn raw_upper(&self) -> String {
        self.inner.lock().unwrap().raw_upper(self.node)
    }

    #[getter]
    #[pyo3(name = "type")]
    fn get_type(&self) -> String {
        self.inner.lock().unwrap().get_type(self.node)
    }

    fn is_type(&self, seg_type: Vec<String>) -> bool {
        let a = self.inner.lock().unwrap();
        seg_type.iter().any(|t| a.is_type(self.node, t))
    }

    fn class_types(&self) -> Vec<String> {
        self.inner.lock().unwrap().class_types(self.node)
    }

    fn instance_types(&self) -> Vec<String> {
        self.inner.lock().unwrap().instance_types(self.node)
    }

    /// `is_implicit` flag for Indent/Dedent metas (`None` for non-metas).
    fn is_implicit(&self) -> Option<bool> {
        self.inner.lock().unwrap().is_implicit(self.node)
    }

    fn trim_chars(&self) -> Option<Vec<String>> {
        self.inner.lock().unwrap().trim_chars(self.node)
    }

    fn quoted_value(&self) -> Option<(String, String)> {
        self.inner.lock().unwrap().quoted_value(self.node)
    }

    fn escape_replacements(&self) -> Option<Vec<(String, String)>> {
        self.inner.lock().unwrap().escape_replacements(self.node)
    }

    #[getter]
    fn segment_class(&self) -> Option<String> {
        self.inner.lock().unwrap().segment_class(self.node)
    }

    fn descendant_type_set(&self) -> Vec<String> {
        self.inner
            .lock()
            .unwrap()
            .descendant_type_set(self.node)
            .iter()
            .cloned()
            .collect()
    }

    #[getter]
    fn is_code(&self) -> bool {
        self.inner.lock().unwrap().is_code(self.node)
    }

    #[getter]
    fn is_whitespace(&self) -> bool {
        self.inner.lock().unwrap().is_whitespace(self.node)
    }

    #[getter]
    fn is_comment(&self) -> bool {
        self.inner.lock().unwrap().is_comment(self.node)
    }

    #[getter]
    fn is_meta(&self) -> bool {
        self.inner.lock().unwrap().is_meta(self.node)
    }

    fn is_raw(&self) -> bool {
        self.inner.lock().unwrap().is_raw(self.node)
    }

    #[getter]
    fn is_templated(&self) -> bool {
        self.inner.lock().unwrap().is_templated(self.node)
    }

    #[getter]
    fn pos_marker(&self) -> Option<PyPositionMarker> {
        self.inner
            .lock()
            .unwrap()
            .pos_marker(self.node)
            .map(PyPositionMarker)
    }

    // -- navigation ----------------------------------------------------------

    #[getter]
    #[pyo3(name = "children")]
    fn py_children(&self) -> Vec<PyHandle> {
        let ids = self.inner.lock().unwrap().children(self.node).to_vec();
        self.wrap_many(ids)
    }

    #[getter]
    #[pyo3(name = "parent")]
    fn py_parent(&self) -> Option<PyHandle> {
        let p = self.inner.lock().unwrap().parent(self.node);
        p.map(|n| self.wrap(n))
    }

    /// `(parent_handle, idx)` — mirrors `BaseSegment.get_parent`.
    fn get_parent(&self) -> Option<(PyHandle, usize)> {
        let gp = self.inner.lock().unwrap().get_parent(self.node);
        gp.map(|(n, idx)| (self.wrap(n), idx))
    }

    fn get_child(&self, seg_type: Vec<String>) -> Option<PyHandle> {
        let c = self.inner.lock().unwrap().get_child(self.node, &seg_type);
        c.map(|n| self.wrap(n))
    }

    fn get_children(&self, seg_type: Vec<String>) -> Vec<PyHandle> {
        let ids = self
            .inner
            .lock()
            .unwrap()
            .get_children(self.node, &seg_type);
        self.wrap_many(ids)
    }

    fn raw_segments(&self) -> Vec<PyHandle> {
        let ids = self.inner.lock().unwrap().raw_segments(self.node);
        self.wrap_many(ids)
    }

    #[pyo3(signature = (seg_type, recurse_into=true, no_recursive_seg_type=vec![], allow_self=true))]
    fn recursive_crawl(
        &self,
        seg_type: Vec<String>,
        recurse_into: bool,
        no_recursive_seg_type: Vec<String>,
        allow_self: bool,
    ) -> Vec<PyHandle> {
        let ids = self.inner.lock().unwrap().recursive_crawl(
            self.node,
            &seg_type,
            recurse_into,
            &no_recursive_seg_type,
            allow_self,
        );
        self.wrap_many(ids)
    }

    fn recursive_crawl_all(&self) -> Vec<PyHandle> {
        let ids = self.inner.lock().unwrap().recursive_crawl_all(self.node);
        self.wrap_many(ids)
    }

    /// Path from this node (an ancestor) down to `other`, as a list of
    /// `(parent_handle, idx, len, code_idxs)` tuples for building `PathStep`s.
    fn path_to(&self, other: &PyHandle) -> Vec<(PyHandle, usize, usize, Vec<usize>)> {
        // Handles into a different arena share no path (mirrors the Python façade
        // returning an empty path). Guard before indexing *this* arena with the
        // other handle's NodeId, which could otherwise alias or panic.
        if !Arc::ptr_eq(&self.inner, &other.inner) {
            return Vec::new();
        }
        let steps = self.inner.lock().unwrap().path_to(self.node, other.node);
        steps
            .into_iter()
            .map(|s| (self.wrap(s.node), s.idx, s.len, s.code_idxs))
            .collect()
    }

    fn __repr__(&self) -> String {
        let a = self.inner.lock().unwrap();
        format!(
            "RsHandle(type={:?}, raw={:?})",
            a.get_type(self.node),
            a.raw(self.node)
        )
    }
}
