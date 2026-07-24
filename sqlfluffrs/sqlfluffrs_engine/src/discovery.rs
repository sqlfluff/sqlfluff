//! Native file discovery, mirroring `paths_from_path()`:
//! - directories are walked recursively;
//! - files are kept when their name ends with a configured `sql_file_exts`
//!   extension (case-insensitive);
//! - explicit file paths are always kept;
//! - `.sqlfluffignore` (gitignore-style) and `core.ignore_paths` are honored.

use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use regex::Regex;
use walkdir::WalkDir;

/// A compiled gitignore-style pattern, anchored at `base`.
pub struct IgnorePattern {
    regex: Regex,
    negated: bool,
}

/// A set of ignore patterns rooted at a base directory.
pub struct IgnoreSpec {
    base: PathBuf,
    patterns: Vec<IgnorePattern>,
}

impl IgnoreSpec {
    pub fn from_lines(base: &Path, text: &str) -> Self {
        let mut patterns = Vec::new();
        for raw in text.lines() {
            let line = raw.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            let (negated, body) = match line.strip_prefix('!') {
                Some(rest) => (true, rest),
                None => (false, line),
            };
            if let Some(regex) = glob_to_regex(body) {
                patterns.push(IgnorePattern { regex, negated });
            }
        }
        Self {
            base: base.to_path_buf(),
            patterns,
        }
    }

    /// Whether `path` is ignored by this spec. `None` means "no pattern applied".
    fn ignores(&self, path: &Path) -> Option<bool> {
        let rel = path.strip_prefix(&self.base).ok()?;
        let rel_str = rel.to_string_lossy().replace('\\', "/");
        let mut decision = None;
        for pat in &self.patterns {
            if pat.regex.is_match(&rel_str) {
                decision = Some(!pat.negated);
            }
        }
        decision
    }
}

/// Translate a gitignore-style glob into an anchored regex over the relative
/// path. Approximate but covers the common cases (`*`, `**`, `?`, `/` anchor).
fn glob_to_regex(pattern: &str) -> Option<Regex> {
    let anchored = pattern.starts_with('/');
    let body = pattern.trim_start_matches('/').trim_end_matches('/');
    if body.is_empty() {
        return None;
    }

    let mut re = String::new();
    // If not anchored, the pattern may match at any path segment boundary.
    re.push_str(if anchored { "^" } else { "(^|.*/)" });

    let bytes: Vec<char> = body.chars().collect();
    let mut i = 0;
    while i < bytes.len() {
        let c = bytes[i];
        match c {
            '*' => {
                if i + 1 < bytes.len() && bytes[i + 1] == '*' {
                    re.push_str(".*");
                    i += 1;
                } else {
                    re.push_str("[^/]*");
                }
            }
            '?' => re.push_str("[^/]"),
            '.' | '+' | '(' | ')' | '|' | '^' | '$' | '{' | '}' | '[' | ']' | '\\' => {
                re.push('\\');
                re.push(c);
            }
            other => re.push(other),
        }
        i += 1;
    }
    // Match either the exact path or anything beneath it (directory match).
    re.push_str("(/.*)?$");
    Regex::new(&re).ok()
}

/// Collect SQL files from the given input paths.
///
/// Takes primitives rather than a config object so both callers can drive it:
/// the standalone binary (reading a `ResolvedConfig`) and the Python-driven
/// engine entrypoint (reading the Python `FluffConfig`). `exts` are lowercased
/// `sql_file_exts`; `root_ignore_paths` are the top-level `core.ignore_paths`
/// patterns, anchored at `working_dir`. Inner `.sqlfluffignore` / config-file
/// `ignore_paths` encountered during the walk are honored automatically.
pub fn discover_files(
    paths: &[String],
    exts: &[String],
    root_ignore_paths: &[String],
    working_dir: &Path,
) -> Result<Vec<PathBuf>> {
    let ignore_paths = root_ignore_specs(root_ignore_paths, working_dir);

    let mut out = Vec::new();
    for path in paths {
        if path == "-" {
            continue; // stdin handled by the caller
        }
        let p = Path::new(path);
        // Walk an absolutized path so every entry compares against the
        // (absolute) ignore-spec bases; results are reported under the path
        // as typed.
        let abs = absolutize(p, working_dir);
        if abs.is_file() {
            // Explicit files are always included.
            out.push(p.to_path_buf());
        } else if abs.is_dir() {
            collect_dir(&abs, p, exts, &ignore_paths, &mut out)?;
        } else {
            anyhow::bail!("path does not exist: {}", path);
        }
    }
    Ok(out)
}

fn absolutize(path: &Path, working_dir: &Path) -> PathBuf {
    if path.is_absolute() {
        path.to_path_buf()
    } else {
        working_dir.join(path)
    }
}

fn root_ignore_specs(root_ignore_paths: &[String], working_dir: &Path) -> Vec<IgnoreSpec> {
    let patterns = root_ignore_paths.join("\n");
    if patterns.is_empty() {
        Vec::new()
    } else {
        vec![IgnoreSpec::from_lines(working_dir, &patterns)]
    }
}

/// Walk `abs_dir` (absolute, so paths line up with the ignore-spec bases) and
/// collect matching files, reported relative to `orig_dir` (the path as the
/// caller typed it).
fn collect_dir(
    abs_dir: &Path,
    orig_dir: &Path,
    exts: &[String],
    ignore_paths: &[IgnoreSpec],
    out: &mut Vec<PathBuf>,
) -> Result<()> {
    // Load `.sqlfluffignore` files we encounter, applying them to their subtree.
    let mut specs: Vec<IgnoreSpec> = Vec::new();

    for entry in WalkDir::new(abs_dir).sort_by_file_name() {
        let entry = entry.with_context(|| format!("walking {}", abs_dir.display()))?;
        let path = entry.path();

        if entry.file_type().is_file()
            && path.file_name() == Some(std::ffi::OsStr::new(".sqlfluffignore"))
        {
            if let Some(parent) = path.parent() {
                let text = std::fs::read_to_string(path).unwrap_or_default();
                specs.push(IgnoreSpec::from_lines(parent, &text));
            }
            continue;
        }

        // Inner config files contribute `ignore_paths` for their subtree.
        if entry.file_type().is_file() && is_config_filename(path) {
            if let Some(parent) = path.parent() {
                let patterns = crate::config::ignore_paths_from_file(path);
                if !patterns.is_empty() {
                    specs.push(IgnoreSpec::from_lines(parent, &patterns.join("\n")));
                }
            }
            continue;
        }

        if !entry.file_type().is_file() {
            continue;
        }
        if !matches_ext(path, exts) {
            continue;
        }
        if is_ignored(path, &specs) || is_ignored(path, ignore_paths) {
            continue;
        }
        out.push(orig_dir.join(path.strip_prefix(abs_dir).unwrap_or(path)));
    }
    Ok(())
}

fn is_ignored(path: &Path, specs: &[IgnoreSpec]) -> bool {
    specs
        .iter()
        .filter_map(|s| s.ignores(path))
        .next_back()
        .unwrap_or(false)
}

fn is_config_filename(path: &Path) -> bool {
    matches!(
        path.file_name().and_then(|n| n.to_str()),
        Some(".sqlfluff" | "setup.cfg" | "tox.ini" | "pep8.ini" | "pyproject.toml")
    )
}

fn matches_ext(path: &Path, exts: &[String]) -> bool {
    let name = path
        .file_name()
        .and_then(|n| n.to_str())
        .map(|n| n.to_ascii_lowercase())
        .unwrap_or_default();
    exts.iter().any(|ext| name.ends_with(ext.as_str()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn glob_matches_nested() {
        let re = glob_to_regex("*.sql").unwrap();
        assert!(re.is_match("a/b/c.sql"));
        assert!(!re.is_match("a/b/c.txt"));
    }

    #[test]
    fn question_mark_does_not_cross_separators() {
        let re = glob_to_regex("a?b.sql").unwrap();
        assert!(re.is_match("axb.sql"));
        assert!(!re.is_match("a/b.sql"));
    }

    #[test]
    fn anchored_glob() {
        let re = glob_to_regex("/build").unwrap();
        assert!(re.is_match("build/x.sql"));
        assert!(!re.is_match("src/build/x.sql"));
    }

    #[test]
    fn relative_dir_honors_root_ignore_paths() {
        // Regression: a relative input path used to bypass `core.ignore_paths`
        // because the walked (relative) entries never matched the absolute
        // ignore-spec base.
        let base =
            std::env::temp_dir().join(format!("sqlfluffrs_discovery_test_{}", std::process::id()));
        let proj = base.join("proj");
        std::fs::create_dir_all(proj.join("ignored")).unwrap();
        std::fs::write(proj.join("keep.sql"), "select 1").unwrap();
        std::fs::write(proj.join("ignored").join("skip.sql"), "select 1").unwrap();

        let exts = vec![".sql".to_string()];
        let ignore = vec!["ignored/".to_string()];
        let found = discover_files(&["proj".to_string()], &exts, &ignore, &base).unwrap();
        assert_eq!(found, vec![PathBuf::from("proj").join("keep.sql")]);

        std::fs::remove_dir_all(&base).unwrap();
    }

    #[test]
    fn ext_matching_is_case_insensitive() {
        let exts = vec![".sql".to_string(), ".sql.j2".to_string()];
        assert!(matches_ext(Path::new("Foo.SQL"), &exts));
        assert!(matches_ext(Path::new("foo.sql.j2"), &exts));
        assert!(!matches_ext(Path::new("foo.py"), &exts));
    }
}
