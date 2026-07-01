//! `sqlfluff-rs` — a Rust command entry point for SQLFluff's
//! templating → lexing → parsing pipeline.
//!
//! Commands: `render`, `parse`, `lex`. Argument parsing, config resolution and
//! file discovery are native Rust; templating (for anything beyond the `raw`
//! templater) is reverse-dispatched to the Python templaters via an embedded
//! interpreter (the `embed-python` feature). Lexing and parsing reuse the
//! existing `sqlfluffrs_lexer` / `sqlfluffrs_parser` crates.

mod cli;
mod output;
mod templating;

use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{Context, Result};
use clap::Parser as _;

use cli::{Cli, Command, CoreArgs};
use sqlfluffrs_engine::config::{ConfigMap, ConfigValue, ResolvedConfig};
use sqlfluffrs_engine::{discovery, pipeline};

const EXIT_SUCCESS: u8 = 0;
const EXIT_FAIL: u8 = 1;
const EXIT_ERROR: u8 = 2;

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(&cli) {
        Ok(code) => ExitCode::from(code),
        Err(e) => {
            eprintln!("Error: {e:#}");
            ExitCode::from(EXIT_ERROR)
        }
    }
}

/// A unit of work: a filename label plus its raw SQL contents.
struct Input {
    fname: String,
    /// Directory used as the base for config resolution.
    base_dir: PathBuf,
    raw: String,
}

fn run(cli: &Cli) -> Result<u8> {
    let core = cli.command.core();
    let overrides = build_cli_overrides(core);
    let cwd = std::env::current_dir().context("getting current directory")?;

    let base_config = ResolvedConfig::resolve(
        &cwd,
        core.config.as_deref(),
        core.ignore_local_config,
        overrides.clone(),
    )?;

    let inputs = gather_inputs(core, &base_config, &cwd)?;
    if inputs.is_empty() {
        eprintln!("No SQL files found.");
        return Ok(EXIT_SUCCESS);
    }

    let multiple = inputs.len() > 1;
    let mut worst = EXIT_SUCCESS;

    for input in inputs {
        // Resolve config relative to the file, then apply inline directives.
        let file_config = ResolvedConfig::resolve(
            &input.base_dir,
            core.config.as_deref(),
            core.ignore_local_config,
            overrides.clone(),
        )?
        .with_inline_directives(&input.raw);

        let code = match process(cli, &input, &file_config, multiple) {
            Ok(code) => code,
            Err(e) => {
                eprintln!("{}: error: {e:#}", input.fname);
                EXIT_ERROR
            }
        };
        worst = worst.max(code);
    }

    Ok(worst)
}

/// Build the `{core: {...}}` override map from CLI flags.
fn build_cli_overrides(core: &CoreArgs) -> ConfigMap {
    let mut core_section = ConfigMap::new();
    if let Some(d) = &core.dialect {
        core_section.insert("dialect".into(), ConfigValue::Str(d.clone()));
    }
    if let Some(t) = &core.templater {
        core_section.insert("templater".into(), ConfigValue::Str(t.clone()));
    }
    if let Some(enc) = &core.encoding {
        core_section.insert("encoding".into(), ConfigValue::Str(enc.clone()));
    }

    let mut out = ConfigMap::new();
    out.insert("core".into(), ConfigValue::Section(core_section));

    if let Some(lib) = &core.library_path {
        // Mirrors the `[sqlfluff:templater:jinja] library_path` location used by
        // the jinja templater.
        let mut jinja = ConfigMap::new();
        jinja.insert("library_path".into(), ConfigValue::Str(lib.clone()));
        let mut templater = ConfigMap::new();
        templater.insert("jinja".into(), ConfigValue::Section(jinja));
        out.insert("templater".into(), ConfigValue::Section(templater));
    }

    out
}

/// Collect the inputs to process, either from stdin (`-`) or by discovering
/// files from the given paths.
fn gather_inputs(core: &CoreArgs, config: &ResolvedConfig, cwd: &Path) -> Result<Vec<Input>> {
    if core.paths.iter().any(|p| p == "-") {
        let mut raw = String::new();
        std::io::stdin()
            .read_to_string(&mut raw)
            .context("reading stdin")?;
        let (fname, base_dir) = match &core.stdin_filename {
            Some(f) => {
                let p = PathBuf::from(f);
                let dir = p
                    .parent()
                    .map(|d| d.to_path_buf())
                    .unwrap_or_else(|| cwd.to_path_buf());
                (f.clone(), dir)
            }
            None => ("stdin".to_string(), cwd.to_path_buf()),
        };
        return Ok(vec![Input {
            fname,
            base_dir,
            raw,
        }]);
    }

    let files = discovery::discover_files(
        &core.paths,
        &config.sql_file_exts(),
        &config.ignore_paths(),
        cwd,
    )?;
    let mut inputs = Vec::with_capacity(files.len());
    for path in files {
        let raw = std::fs::read_to_string(&path)
            .with_context(|| format!("reading {}", path.display()))?;
        let base_dir = path
            .parent()
            .map(|d| d.to_path_buf())
            .unwrap_or_else(|| cwd.to_path_buf());
        inputs.push(Input {
            fname: path.to_string_lossy().to_string(),
            base_dir,
            raw,
        });
    }
    Ok(inputs)
}

/// Dispatch one input through the requested command.
fn process(cli: &Cli, input: &Input, config: &ResolvedConfig, multiple: bool) -> Result<u8> {
    let templater_name = config.templater();
    let outcome = templating::template(&input.raw, &input.fname, &templater_name, config)?;

    let mut exit = EXIT_SUCCESS;
    for err in &outcome.errors {
        eprintln!("{}: templating: {err}", input.fname);
        exit = exit.max(EXIT_FAIL);
    }
    if outcome.variants.is_empty() {
        return Ok(exit.max(EXIT_FAIL));
    }

    match &cli.command {
        Command::Render(_) => {
            let body = output::render_output(&outcome.variants);
            print_body(input, &body, multiple, None)?;
        }
        Command::Lex(args) => {
            let dialect = pipeline::resolve_dialect_by_name(config.dialect().as_deref())?;
            let variant = &outcome.variants[0];
            let (tokens, lex_errors) =
                pipeline::lex_variant(variant, dialect, config.template_blocks_indent());
            let body = output::lex_output(&tokens, args.format)?;
            print_body(input, &body, multiple, args.write_output.as_deref())?;
            for err in lex_errors {
                eprintln!("{}: lexing: {err}", input.fname);
                exit = exit.max(EXIT_FAIL);
            }
        }
        Command::Parse(args) => {
            let dialect = pipeline::resolve_dialect_by_name(config.dialect().as_deref())?;
            let variant = &outcome.variants[0];
            let (tokens, lex_errors) =
                pipeline::lex_variant(variant, dialect, config.template_blocks_indent());
            for err in &lex_errors {
                eprintln!("{}: lexing: {err}", input.fname);
                exit = exit.max(EXIT_FAIL);
            }
            let node = pipeline::parse_tokens(
                &tokens,
                dialect,
                config.indentation_bools(),
                config.parse_limits(),
            )?;
            let body = output::parse_output(
                &node,
                &input.fname,
                args.format,
                args.code_only,
                args.include_meta,
            )?;
            print_body(input, &body, multiple, args.write_output.as_deref())?;
        }
    }

    Ok(exit)
}

/// Emit a command's output, optionally to a file, with a per-file header when
/// more than one input is being processed.
fn print_body(input: &Input, body: &str, multiple: bool, write_output: Option<&str>) -> Result<()> {
    if let Some(path) = write_output {
        let mut f =
            std::fs::File::create(path).with_context(|| format!("creating output file {path}"))?;
        f.write_all(body.as_bytes())?;
        return Ok(());
    }
    if multiple {
        println!("== [{}] ==", input.fname);
    }
    print!("{body}");
    if !body.ends_with('\n') && !body.is_empty() {
        println!();
    }
    Ok(())
}
