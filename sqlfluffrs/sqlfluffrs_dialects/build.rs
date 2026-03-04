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
//! This build script detects when those files are absent (e.g. fresh
//! `git clone`) and runs the code-generation step automatically, so that
//! both plain `cargo build` and `pip install git+...` succeed without
//! manual pre-steps.
//!
//! When building via pip/maturin the isolated build environment does not have
//! pip, so the script cannot install packages.  Instead, the repo's `src/`
//! directory is prepended to `PYTHONPATH` before calling `rustify.py`,
//! making `sqlfluff` importable directly from the source tree without any
//! installation step.
//!
//! **Regular developer workflow** (generated files already on disk) exits
//! immediately — the generation step is skipped entirely.

use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    // CARGO_MANIFEST_DIR is the absolute path to `sqlfluffrs_dialects/`
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR")
        .expect("CARGO_MANIFEST_DIR not set – this script must be run by cargo");

    let crate_root = PathBuf::from(&manifest_dir);
    let dialect_dir = crate_root.join("src").join("dialect");
    let mod_rs = dialect_dir.join("mod.rs");

    // Always re-run when this script changes.
    println!("cargo:rerun-if-changed=build.rs");

    if mod_rs.exists() {
        // Generated files are already present – nothing to do.
        println!("cargo:rerun-if-changed={}", mod_rs.display());
        return;
    }

    // -----------------------------------------------------------------------
    // Generated files are missing.  Locate the repo root and run rustify.py.
    // -----------------------------------------------------------------------
    //
    // Directory structure:
    //   <repo_root>/
    //     sqlfluffrs/
    //       sqlfluffrs_dialects/   ← CARGO_MANIFEST_DIR
    //     utils/
    //       rustify.py
    //
    let repo_root = crate_root
        .parent() // sqlfluffrs/
        .and_then(|p| p.parent()) // <repo_root>/
        .map(PathBuf::from)
        .expect("Cannot determine repo root from CARGO_MANIFEST_DIR");

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
        "cargo:warning=sqlfluffrs_dialects: dialect sources missing – \
         running code generation with '{python}' …"
    );

    // Prepend <repo_root>/src to PYTHONPATH so that rustify.py can import
    // sqlfluff directly from the source tree.  This avoids needing pip (which
    // is absent in maturin's isolated PEP 517 build environment).
    let src_dir = repo_root.join("src");
    let pythonpath = match std::env::var("PYTHONPATH") {
        Ok(existing) if !existing.is_empty() => {
            format!("{}:{}", src_dir.display(), existing)
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

    // Tell cargo to watch the generated mod.rs once it exists.
    if mod_rs.exists() {
        println!("cargo:rerun-if-changed={}", mod_rs.display());
    }
}

/// Locate a usable Python interpreter.
///
/// Preference order:
/// 1. `MATURIN_PYTHON_INTERPRETER` – set by maturin during PEP 517 builds.
/// 2. Active virtual-environment (`VIRTUAL_ENV`).
/// 3. Common names on `PATH`.
fn find_python() -> String {
    // 1. Maturin's interpreter (always has the build requirements installed).
    if let Ok(p) = std::env::var("MATURIN_PYTHON_INTERPRETER") {
        if Path::new(&p).exists() {
            return p;
        }
    }

    // 2. Active virtual-environment interpreter.
    if let Ok(venv) = std::env::var("VIRTUAL_ENV") {
        let candidate = PathBuf::from(&venv).join("bin").join("python");
        if candidate.exists() {
            return candidate.to_string_lossy().into_owned();
        }
    }

    // 3. Common fallback names on PATH.
    for name in &["python3", "python", "python3.13", "python3.12", "python3.11"] {
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
