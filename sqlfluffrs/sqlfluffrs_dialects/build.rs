//! Cargo build script for `sqlfluffrs_dialects`.
//!
//! Generated dialect source files (`src/dialect/<name>/parser.rs`,
//! `src/dialect/<name>/matcher.rs`, `src/dialect/mod.rs`) are **not** checked
//! into version control.  They are produced by running
//!
//! ```text
//! python utils/rustify.py build
//! ```
//!
//! from the repository root.
//!
//! ## Rebuild logic
//!
//! The script avoids both over- and under-building:
//!
//! * It emits `cargo:rerun-if-changed` for every Python dialect source file
//!   and every build-utility script, so Cargo tracks them precisely.
//! * It re-runs code generation when `mod.rs` is absent **or** when any
//!   watched Python file is newer than `mod.rs` (Makefile-style mtime check).
//!
//! This means the generated sources are kept in sync automatically — a
//! developer who edits a dialect definition and runs `cargo build` gets fresh
//! Rust sources without running `tox -e generate-rs` manually.
//!
//! ## Installation from a git VCS URL
//!
//! When building via `pip install git+...#subdirectory=sqlfluffrs`, pip
//! creates an isolated build environment that only has packages listed in
//! `[build-system] requires` (`maturin` + `sqlfluff`).  The script prepends
//! `<repo_root>/src` to `PYTHONPATH` so the build sub-scripts can import
//! `sqlfluff` directly from the cloned source tree.
//!
//! This also allows for `uvx sqlfluff` or `uv tool sqlfluff` using
//! `--with sqlfluffrs@<git+...#subdirectory=sqlfluffrs>` to install from
//! a branch or fork without a published release, and have the Rust
//! sources generated correctly from that branch's Python code.

use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    // CARGO_MANIFEST_DIR is the absolute path to `sqlfluffrs_dialects/`
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR")
        .expect("CARGO_MANIFEST_DIR not set – this script must be run by cargo");

    let crate_root = PathBuf::from(&manifest_dir);

    // Directory structure:
    //   <repo_root>/
    //     sqlfluffrs/
    //       sqlfluffrs_dialects/   ← CARGO_MANIFEST_DIR
    //     src/sqlfluff/dialects/
    //     utils/
    let repo_root = crate_root
        .parent() // sqlfluffrs/
        .and_then(|p| p.parent()) // <repo_root>/
        .map(PathBuf::from)
        .expect("Cannot determine repo root from CARGO_MANIFEST_DIR");

    let mod_rs = crate_root.join("src").join("dialect").join("mod.rs");

    // Always re-run if this script itself changes.
    println!("cargo:rerun-if-changed=build.rs");

    // -----------------------------------------------------------------------
    // Collect the Python source files that influence generated output.
    // -----------------------------------------------------------------------
    let sources = collect_python_sources(&repo_root);

    // Register every source with Cargo so incremental rebuilds are precise.
    for src in &sources {
        println!("cargo:rerun-if-changed={}", src.display());
    }

    // -----------------------------------------------------------------------
    // Staleness check: regenerate when mod.rs is absent or older than any
    // Python source (Makefile-style mtime comparison).
    // -----------------------------------------------------------------------
    if !needs_regeneration(&mod_rs, &sources) {
        return;
    }

    // -----------------------------------------------------------------------
    // Run code generation.
    // -----------------------------------------------------------------------
    let rustify = repo_root.join("utils").join("rustify.py");
    if !rustify.exists() {
        panic!(
            "\n\
             sqlfluffrs_dialects: generated source files are missing and \
             utils/rustify.py was not found at '{rustify}'.\n\
             Please run `tox -e generate-rs` from the repository root.\n",
            rustify = rustify.display()
        );
    }

    let python = find_python();
    println!(
        "cargo:warning=sqlfluffrs_dialects: regenerating dialect sources \
         with '{python}' …"
    );

    // Prepend <repo_root>/src to PYTHONPATH so that rustify.py and the build
    // sub-scripts can import sqlfluff directly from the source tree without a
    // full installation (maturin's isolated PEP 517 build env has no pip).
    let src_dir = repo_root.join("src");
    let sep = if cfg!(target_os = "windows") {
        ";"
    } else {
        ":"
    };
    let pythonpath = match std::env::var("PYTHONPATH") {
        Ok(existing) if !existing.is_empty() => {
            format!("{}{}{}", src_dir.display(), sep, existing)
        }
        _ => src_dir.to_string_lossy().into_owned(),
    };

    let status = Command::new(&python)
        .arg(&rustify)
        .arg("build")
        .env("PYTHONPATH", &pythonpath)
        .current_dir(&repo_root)
        .status()
        .unwrap_or_else(|e| {
            panic!(
                "Failed to launch '{python} {rustify}': {e}",
                rustify = rustify.display()
            )
        });

    if !status.success() {
        panic!(
            "Code-generation failed (exit code: {code:?}).\n\
             Run `tox -e generate-rs` manually to see the full error.",
            code = status.code()
        );
    }
}

/// Returns `true` when code generation must run.
///
/// Generation is required when:
/// * `mod.rs` does not exist (fresh clone or cleaned build), or
/// * any Python source file is *strictly newer* than `mod.rs` (a dialect or
///   build script was edited since the last generation run).
fn needs_regeneration(mod_rs: &Path, sources: &[PathBuf]) -> bool {
    let mod_mtime = match mod_rs.metadata().and_then(|m| m.modified()) {
        Ok(t) => t,
        Err(_) => return true, // mod.rs missing or unreadable → must generate
    };

    sources.iter().any(|src| {
        src.metadata()
            .and_then(|m| m.modified())
            .map(|src_mtime| src_mtime > mod_mtime)
            .unwrap_or(false)
    })
}

/// Collect the Python source files whose content influences generated output.
///
/// Includes:
/// * `src/sqlfluff/dialects/dialect_*.py` – one per SQL dialect
/// * `utils/rustify.py` and `utils/build_*.py` – code-generation scripts
fn collect_python_sources(repo_root: &Path) -> Vec<PathBuf> {
    let mut sources = Vec::new();

    // Dialect definitions
    let dialects_dir = repo_root.join("src").join("sqlfluff").join("dialects");
    if let Ok(entries) = std::fs::read_dir(&dialects_dir) {
        for entry in entries.filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("py") {
                let stem = path
                    .file_stem()
                    .and_then(|s| s.to_str())
                    .unwrap_or_default();
                if stem.starts_with("dialect_") {
                    sources.push(path);
                }
            }
        }
    }

    // Build utility scripts
    let utils_dir = repo_root.join("utils");
    for name in &[
        "rustify.py",
        "build_dialect.py",
        "build_dialects.py",
        "build_lexers.py",
        "build_parsers.py",
    ] {
        let p = utils_dir.join(name);
        if p.exists() {
            sources.push(p);
        }
    }

    let lookbehind = repo_root
        .join("src")
        .join("sqlfluff")
        .join("core")
        .join("parser")
        .join("grammar")
        .join("lookbehind.py");
    if lookbehind.exists() {
        sources.push(lookbehind);
    }

    sources
}

/// Locate a usable Python interpreter.
///
/// Preference order:
/// 1. `MATURIN_PYTHON_INTERPRETER` – set by maturin during PEP 517 builds.
/// 2. Active virtual-environment (`VIRTUAL_ENV`).
/// 3. Common names on `PATH`.
fn find_python() -> String {
    // 1. Maturin's interpreter.
    if let Ok(p) = std::env::var("MATURIN_PYTHON_INTERPRETER") {
        if Path::new(&p).exists() {
            return p;
        }
    }

    // 2. Active virtual-environment interpreter.
    if let Ok(venv) = std::env::var("VIRTUAL_ENV") {
        #[cfg(target_os = "windows")]
        let candidate = PathBuf::from(&venv).join("Scripts").join("python.exe");
        #[cfg(not(target_os = "windows"))]
        let candidate = PathBuf::from(&venv).join("bin").join("python");
        if candidate.exists() {
            return candidate.to_string_lossy().into_owned();
        }
    }

    // 3. Common fallback names on PATH.
    for name in &[
        "python3",
        "python",
        "python3.14",
        "python3.13",
        "python3.12",
        "python3.11",
        "python3.10",
        "python3.9",
    ] {
        if Command::new(name)
            .arg("--version")
            .output()
            .map(|o| o.status.success())
            .unwrap_or(false)
        {
            return (*name).to_string();
        }
    }

    "python3".to_string()
}
