//! Native config resolution, mirroring the layering that Python's `FluffConfig`
//! performs. Produces a single nested [`ConfigMap`] that is the source of truth
//! for the Rust pipeline (dialect, file discovery, parser limits) and is also
//! handed to the Python templaters via the embedded-interpreter bridge.
//!
//! Layering precedence (lowest → highest):
//!   embedded `default_config.cfg` → ancestor config files (outermost first) →
//!   `--config` extra file → CLI `--key value` overrides → inline `-- sqlfluff:`
//!   directives scanned from the file itself.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

/// SQLFluff's built-in defaults, embedded so resolution matches Python exactly.
const DEFAULT_CONFIG_CFG: &str = include_str!("../../../src/sqlfluff/core/default_config.cfg");

/// Config files searched for in each directory of the hierarchy.
const CONFIG_FILENAMES: &[&str] = &[
    "setup.cfg",
    "tox.ini",
    "pep8.ini",
    ".sqlfluff",
    "pyproject.toml",
];

/// A scalar or nested config value (mirrors entries in Python's `_configs`).
#[derive(Debug, Clone, PartialEq)]
pub enum ConfigValue {
    Str(String),
    Int(i64),
    Bool(bool),
    /// Explicit `None` (the cfg literal `None`/`none`).
    None,
    Section(ConfigMap),
}

pub type ConfigMap = BTreeMap<String, ConfigValue>;

/// Coerce a raw string value the way Python's `coerce_value` does.
pub fn coerce_value(raw: &str) -> ConfigValue {
    let trimmed = raw.trim();
    match trimmed.to_ascii_lowercase().as_str() {
        "none" => ConfigValue::None,
        "true" => ConfigValue::Bool(true),
        "false" => ConfigValue::Bool(false),
        _ => {
            if let Ok(i) = trimmed.parse::<i64>() {
                ConfigValue::Int(i)
            } else {
                ConfigValue::Str(trimmed.to_string())
            }
        }
    }
}

/// Deep-merge `src` into `dst` (mirrors Python's `nested_combine`): later values
/// win, sections recurse.
fn nested_combine(dst: &mut ConfigMap, src: ConfigMap) {
    for (k, v) in src {
        match (dst.get_mut(&k), v) {
            (Some(ConfigValue::Section(existing)), ConfigValue::Section(incoming)) => {
                nested_combine(existing, incoming);
            }
            (_, v) => {
                dst.insert(k, v);
            }
        }
    }
}

/// Insert a value at a dotted key path, creating intermediate sections.
fn insert_path(map: &mut ConfigMap, path: &[String], value: ConfigValue) {
    if path.is_empty() {
        return;
    }
    if path.len() == 1 {
        map.insert(path[0].clone(), value);
        return;
    }
    let entry = map
        .entry(path[0].clone())
        .or_insert_with(|| ConfigValue::Section(ConfigMap::new()));
    if let ConfigValue::Section(sub) = entry {
        insert_path(sub, &path[1..], value);
    } else {
        // Existing scalar where a section is needed: replace with a section.
        let mut sub = ConfigMap::new();
        insert_path(&mut sub, &path[1..], value);
        *entry = ConfigValue::Section(sub);
    }
}

/// Map an INI section header (e.g. `sqlfluff:templater:jinja`) to its key path.
/// The bare `sqlfluff` section maps to `core`; anything not under `sqlfluff`
/// is ignored.
fn ini_section_to_path(section: &str) -> Option<Vec<String>> {
    let mut parts = section.split(':');
    if parts.next()? != "sqlfluff" {
        return None;
    }
    let rest: Vec<String> = parts.map(|s| s.trim().to_string()).collect();
    if rest.is_empty() {
        Some(vec!["core".to_string()])
    } else {
        Some(rest)
    }
}

/// Parse INI-style config text (`.sqlfluff`, `setup.cfg`, `tox.ini`) into a
/// nested [`ConfigMap`]. Only `sqlfluff`-prefixed sections are retained.
/// Follows Python's `configparser` defaults: `=` and `:` both delimit
/// key/value (whichever comes first), and a non-blank line indented deeper
/// than its option line continues that option's value (joined with `\n`,
/// blank lines preserved, like `empty_lines_in_values=True`).
pub fn parse_ini(text: &str) -> ConfigMap {
    let mut out = ConfigMap::new();
    let mut current_path: Option<Vec<String>> = None;
    // A key whose value may still grow via continuation lines.
    let mut pending: Option<(Vec<String>, Vec<String>)> = None;
    // Indent depth of the current option/section line — only deeper lines
    // continue the pending value (mirrors configparser's `cur_indent_level`).
    let mut indent_level = 0usize;

    let flush = |out: &mut ConfigMap, pending: &mut Option<(Vec<String>, Vec<String>)>| {
        if let Some((full, lines)) = pending.take() {
            // configparser joins with `\n` and strips the result.
            insert_path(out, &full, coerce_value(&lines.join("\n")));
        }
    };

    for raw_line in text.lines() {
        let line = raw_line.trim();
        // Full-line comments are skipped entirely, even inside a value.
        if line.starts_with('#') || line.starts_with(';') {
            continue;
        }
        // Blank lines are preserved inside a pending value.
        if line.is_empty() {
            if let Some((_, lines)) = &mut pending {
                lines.push(String::new());
            }
            continue;
        }
        let cur_indent = raw_line.chars().take_while(|c| c.is_whitespace()).count();
        if cur_indent > indent_level {
            if let Some((_, lines)) = &mut pending {
                lines.push(line.to_string());
                continue;
            }
        }
        // A new section or option line.
        indent_level = cur_indent;
        if line.starts_with('[') && line.ends_with(']') {
            flush(&mut out, &mut pending);
            let section = line[1..line.len() - 1].trim();
            current_path = ini_section_to_path(section);
            continue;
        }
        let Some(path) = &current_path else { continue };
        // Split on whichever delimiter appears first, like configparser.
        let delim = match (line.find('='), line.find(':')) {
            (Some(e), Some(c)) => Some(e.min(c)),
            (e, c) => e.or(c),
        };
        if let Some(idx) = delim {
            flush(&mut out, &mut pending);
            let mut full = path.clone();
            full.push(line[..idx].trim().to_string());
            pending = Some((full, vec![line[idx + 1..].trim().to_string()]));
        }
    }
    flush(&mut out, &mut pending);
    out
}

/// Recursively convert a TOML table where scalar entries stay in place
/// (used for nested sections under `[tool.sqlfluff.*]`).
fn toml_table_nested(tbl: &toml::Table) -> ConfigMap {
    let mut out = ConfigMap::new();
    for (k, v) in tbl {
        match v {
            toml::Value::Table(t) => {
                out.insert(k.clone(), ConfigValue::Section(toml_table_nested(t)));
            }
            other => {
                out.insert(k.clone(), toml_scalar(other));
            }
        }
    }
    out
}

fn toml_scalar(v: &toml::Value) -> ConfigValue {
    match v {
        toml::Value::String(s) => coerce_value(s),
        toml::Value::Integer(i) => ConfigValue::Int(*i),
        toml::Value::Boolean(b) => ConfigValue::Bool(*b),
        toml::Value::Float(f) => ConfigValue::Str(f.to_string()),
        toml::Value::Array(items) => {
            // sqlfluff stores list-like values as comma-joined strings.
            let joined = items
                .iter()
                .map(|i| match i {
                    toml::Value::String(s) => s.clone(),
                    other => other.to_string(),
                })
                .collect::<Vec<_>>()
                .join(",");
            ConfigValue::Str(joined)
        }
        toml::Value::Datetime(d) => ConfigValue::Str(d.to_string()),
        toml::Value::Table(_) => ConfigValue::Section(ConfigMap::new()),
    }
}

/// Parse a `pyproject.toml`, extracting `[tool.sqlfluff...]`. Scalars directly
/// under `[tool.sqlfluff]` map to `core`; sub-tables become top-level sections.
pub fn parse_pyproject(text: &str) -> Result<ConfigMap> {
    let value: toml::Table = text.parse().context("parsing pyproject.toml")?;
    let Some(sqlfluff) = value
        .get("tool")
        .and_then(|t| t.get("sqlfluff"))
        .and_then(|s| s.as_table())
    else {
        return Ok(ConfigMap::new());
    };

    let mut out = ConfigMap::new();
    let mut core = ConfigMap::new();
    for (k, v) in sqlfluff {
        match v {
            toml::Value::Table(t) => {
                out.insert(k.clone(), ConfigValue::Section(toml_table_nested(t)));
            }
            other => {
                core.insert(k.clone(), toml_scalar(other));
            }
        }
    }
    if !core.is_empty() {
        nested_combine_into_section(&mut out, "core", core);
    }
    Ok(out)
}

fn nested_combine_into_section(out: &mut ConfigMap, name: &str, section: ConfigMap) {
    match out.get_mut(name) {
        Some(ConfigValue::Section(existing)) => nested_combine(existing, section),
        _ => {
            out.insert(name.to_string(), ConfigValue::Section(section));
        }
    }
}

/// Load and parse a single config file by extension/name.
fn load_config_file(path: &Path) -> Result<ConfigMap> {
    let text = std::fs::read_to_string(path)
        .with_context(|| format!("reading config file {}", path.display()))?;
    if path.file_name().and_then(|n| n.to_str()) == Some("pyproject.toml") {
        parse_pyproject(&text)
    } else {
        Ok(parse_ini(&text))
    }
}

/// Extract `core.ignore_paths` (comma-separated) from a single config file.
/// Used by file discovery to honor inner config files within a walked tree.
pub fn ignore_paths_from_file(path: &Path) -> Vec<String> {
    let Ok(text) = std::fs::read_to_string(path) else {
        return Vec::new();
    };
    let map = if path.file_name().and_then(|n| n.to_str()) == Some("pyproject.toml") {
        // Don't fail the walk over one bad inner file, but don't silently
        // drop its `ignore_paths` either (the main config resolution path,
        // `load_config_file`, propagates this same error).
        parse_pyproject(&text).unwrap_or_else(|e| {
            eprintln!("Warning: skipping config in {}: {e:#}", path.display());
            ConfigMap::new()
        })
    } else {
        parse_ini(&text)
    };
    if let Some(ConfigValue::Section(core)) = map.get("core") {
        if let Some(ConfigValue::Str(raw)) = core.get("ignore_paths") {
            return raw
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect();
        }
    }
    Vec::new()
}

/// The fully resolved configuration for a run.
#[derive(Debug, Clone)]
pub struct ResolvedConfig {
    pub map: ConfigMap,
}

impl ResolvedConfig {
    /// Build the base config: embedded defaults + ancestor config files for the
    /// working directory + `--config` extra + CLI overrides.
    pub fn resolve(
        working_dir: &Path,
        extra_config: Option<&str>,
        ignore_local_config: bool,
        cli_overrides: ConfigMap,
    ) -> Result<Self> {
        let mut map = parse_ini(DEFAULT_CONFIG_CFG);

        if !ignore_local_config {
            for dir in ancestor_dirs(working_dir) {
                for name in CONFIG_FILENAMES {
                    let candidate = dir.join(name);
                    if candidate.is_file() {
                        nested_combine(&mut map, load_config_file(&candidate)?);
                    }
                }
            }
        }

        if let Some(extra) = extra_config {
            nested_combine(&mut map, load_config_file(Path::new(extra))?);
        }

        nested_combine(&mut map, cli_overrides);
        Ok(Self { map })
    }

    /// Apply inline `-- sqlfluff:` directives scanned from a raw SQL file,
    /// returning a new (cloned) config (mirrors `process_raw_file_for_config`).
    pub fn with_inline_directives(&self, raw_sql: &str) -> Self {
        let mut map = self.map.clone();
        for line in raw_sql.lines() {
            let trimmed = line.trim_start();
            if trimmed.starts_with("-- sqlfluff") || trimmed.starts_with("--sqlfluff") {
                if let Some((path, value)) = parse_inline_directive(trimmed) {
                    insert_path(&mut map, &path, coerce_value(&value));
                }
            }
        }
        Self { map }
    }

    /// Look up a scalar value by dotted path, returning its string form.
    pub fn get_str(&self, path: &[&str]) -> Option<String> {
        match self.get(path)? {
            ConfigValue::Str(s) => Some(s.clone()),
            ConfigValue::Int(i) => Some(i.to_string()),
            ConfigValue::Bool(b) => Some(b.to_string()),
            ConfigValue::None | ConfigValue::Section(_) => None,
        }
    }

    fn get(&self, path: &[&str]) -> Option<&ConfigValue> {
        let mut cur = &self.map;
        for (i, key) in path.iter().enumerate() {
            let v = cur.get(*key)?;
            if i + 1 == path.len() {
                return Some(v);
            }
            match v {
                ConfigValue::Section(sub) => cur = sub,
                _ => return None,
            }
        }
        None
    }

    /// The boolean entries of the `[sqlfluff:indentation]` section, as required
    /// by the Rust parser's `indent_config` (mirrors `rust_parser.py`).
    pub fn indentation_bools(&self) -> BTreeMap<String, bool> {
        let mut out = BTreeMap::new();
        if let Some(ConfigValue::Section(section)) = self.map.get("indentation") {
            for (k, v) in section {
                if let ConfigValue::Bool(b) = v {
                    out.insert(k.clone(), *b);
                }
            }
        }
        out
    }

    /// Resolved dialect name, if any.
    pub fn dialect(&self) -> Option<String> {
        self.get_str(&["core", "dialect"])
    }

    /// Resolved templater name (defaults to `jinja` per `default_config.cfg`).
    pub fn templater(&self) -> String {
        self.get_str(&["core", "templater"])
            .unwrap_or_else(|| "jinja".to_string())
    }

    /// Parser resource limits, read from `core` (falling back to the
    /// `default_config.cfg` values). Mirrors what `RustParser` threads in.
    pub fn parse_limits(&self) -> crate::pipeline::ParseLimits {
        let d = crate::pipeline::ParseLimits::default();
        let get_usize = |key: &str, dflt: usize| -> usize {
            self.get_str(&["core", key])
                .and_then(|s| s.parse::<usize>().ok())
                .unwrap_or(dflt)
        };
        crate::pipeline::ParseLimits {
            max_parser_iterations: get_usize("rust_parser_max_iterations", d.max_parser_iterations),
            parser_warn_threshold: get_usize("rust_parser_warn_threshold", d.parser_warn_threshold),
            max_parse_depth: get_usize("max_parse_depth", d.max_parse_depth),
            max_parse_nodes: get_usize("max_parse_nodes", d.max_parse_nodes),
        }
    }

    /// Whether template blocks should emit indent meta segments (default true).
    pub fn template_blocks_indent(&self) -> bool {
        self.indentation_bools()
            .get("template_blocks_indent")
            .copied()
            .unwrap_or(true)
    }

    /// Comma-separated `core.ignore_paths` as a trimmed, non-empty list.
    pub fn ignore_paths(&self) -> Vec<String> {
        self.get_str(&["core", "ignore_paths"])
            .unwrap_or_default()
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect()
    }

    /// Comma-separated `sql_file_exts` as a list (lowercased, dot-prefixed).
    pub fn sql_file_exts(&self) -> Vec<String> {
        self.get_str(&["core", "sql_file_exts"])
            .unwrap_or_else(|| ".sql".to_string())
            .split(',')
            .map(|s| s.trim().to_ascii_lowercase())
            .filter(|s| !s.is_empty())
            .collect()
    }
}

/// Parse a single inline directive line (`-- sqlfluff:dialect:postgres`) into a
/// key path and value. Returns `None` if malformed.
fn parse_inline_directive(line: &str) -> Option<(Vec<String>, String)> {
    let line = line.trim_start_matches('-').trim();
    let rest = line.strip_prefix("sqlfluff:")?;
    // Colon-separated: all but the last segment form the key path.
    let parts: Vec<&str> = rest.split(':').map(|s| s.trim()).collect();
    if parts.len() < 2 {
        return None;
    }
    let (value_parts, key_parts) = (parts.last().unwrap(), &parts[..parts.len() - 1]);
    let mut path: Vec<String> = key_parts.iter().map(|s| s.to_string()).collect();
    // A single-element key targets the `core` section.
    if path.len() == 1 {
        path.insert(0, "core".to_string());
    }
    Some((path, value_parts.to_string()))
}

/// Directories from the working dir up to the filesystem root, ordered
/// outermost (root) first so nearer directories override.
fn ancestor_dirs(start: &Path) -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = start.ancestors().map(|p| p.to_path_buf()).collect();
    dirs.reverse();
    dirs
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ini_sections_map_to_paths() {
        let cfg = parse_ini(
            "[sqlfluff]\ndialect = postgres\n[sqlfluff:indentation]\nindented_joins = True\n",
        );
        let rc = ResolvedConfig { map: cfg };
        assert_eq!(rc.dialect().as_deref(), Some("postgres"));
        assert_eq!(rc.indentation_bools().get("indented_joins"), Some(&true));
    }

    #[test]
    fn ini_colon_delimiter_and_continuations() {
        // configparser accepts `:` as a delimiter and indented continuation
        // lines (joined with newlines).
        let cfg = parse_ini(
            "[sqlfluff]\ndialect: postgres\nignore_paths =\n    foo\n    bar\ntemplater = raw\n",
        );
        let rc = ResolvedConfig { map: cfg };
        assert_eq!(rc.dialect().as_deref(), Some("postgres"));
        assert_eq!(rc.templater(), "raw");
        let Some(ConfigValue::Section(core)) = rc.map.get("core") else {
            panic!("no core section");
        };
        assert_eq!(
            core.get("ignore_paths"),
            Some(&ConfigValue::Str("foo\nbar".to_string()))
        );
    }

    #[test]
    fn ini_indent_semantics_match_configparser() {
        // Pinned against Python configparser (empty_lines_in_values=True):
        // - an indented key is a new entry when nothing is pending;
        // - blank lines inside a value are preserved;
        // - full-line comments inside a value are skipped;
        // - a deeper-indented line is a continuation even if it looks like a
        //   section header or key.
        let cfg = parse_ini(
            "[sqlfluff]\n    dialect = postgres\n[sqlfluff:a]\nk =\n    foo\n\n    # c\n    bar\n    x = y\n",
        );
        let rc = ResolvedConfig { map: cfg };
        assert_eq!(rc.dialect().as_deref(), Some("postgres"));
        let Some(ConfigValue::Section(a)) = rc.map.get("a") else {
            panic!("no a section");
        };
        // configparser value is "\nfoo\n\nbar\nx = y"; coerce_value trims ends.
        assert_eq!(
            a.get("k"),
            Some(&ConfigValue::Str("foo\n\nbar\nx = y".to_string()))
        );
        assert_eq!(a.get("x"), None);
    }

    #[test]
    fn ini_first_delimiter_wins() {
        // `=` before `:` splits at `=`, and vice versa — like configparser.
        let cfg = parse_ini("[sqlfluff:x]\na = b:c\nd: e=f\n");
        let Some(ConfigValue::Section(x)) = cfg.get("x") else {
            panic!("no x section");
        };
        assert_eq!(x.get("a"), Some(&ConfigValue::Str("b:c".to_string())));
        assert_eq!(x.get("d"), Some(&ConfigValue::Str("e=f".to_string())));
    }

    #[test]
    fn inline_directive_targets_core() {
        let (path, value) = parse_inline_directive("-- sqlfluff:dialect:bigquery").unwrap();
        assert_eq!(path, vec!["core".to_string(), "dialect".to_string()]);
        assert_eq!(value, "bigquery");
    }

    #[test]
    fn defaults_parse() {
        let rc = ResolvedConfig {
            map: parse_ini(DEFAULT_CONFIG_CFG),
        };
        assert_eq!(rc.templater(), "jinja");
        assert!(rc.sql_file_exts().contains(&".sql".to_string()));
    }
}
