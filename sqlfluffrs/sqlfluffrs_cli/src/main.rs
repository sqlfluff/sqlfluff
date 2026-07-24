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

use cli::{Cli, Command, CoreArgs, OutputFormat};
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

    // Open `--write-output` once, up front, so multiple inputs append to the
    // same file rather than each truncating the previous one's output.
    let mut out_file = match cli.command.write_output() {
        Some(path) => Some(
            std::fs::File::create(path).with_context(|| format!("creating output file {path}"))?,
        ),
        None => None,
    };

    // json/yaml results are collected per file and emitted as ONE document at
    // the end — per-file documents (or `== [..] ==` headers) concatenated into
    // the stream would not be valid json/yaml.
    let mut machine_docs: Vec<output::MachineDoc> = Vec::new();

    for input in inputs {
        // Resolve config relative to the file, then apply inline directives.
        let file_config = ResolvedConfig::resolve(
            &input.base_dir,
            core.config.as_deref(),
            core.ignore_local_config,
            overrides.clone(),
        )?
        .with_inline_directives(&input.raw);

        let code = match process(
            cli,
            &input,
            &file_config,
            multiple,
            out_file.as_mut(),
            &mut machine_docs,
        ) {
            Ok(code) => code,
            Err(e) => {
                eprintln!("{}: error: {e:#}", input.fname);
                EXIT_ERROR
            }
        };
        worst = worst.max(code);
    }

    if let Some(body) = output::machine_output(machine_docs, machine_format(cli))? {
        emit(&body, out_file.as_mut())?;
    }

    Ok(worst)
}

/// The output format of the current command (`Human` for `render`, which has
/// no format flag).
fn machine_format(cli: &Cli) -> OutputFormat {
    match &cli.command {
        Command::Lex(a) => a.format,
        Command::Parse(a) => a.format,
        Command::Render(_) => OutputFormat::Human,
    }
}

/// Write a complete output body to the `--write-output` file or stdout.
fn emit(body: &str, out_file: Option<&mut std::fs::File>) -> Result<()> {
    match out_file {
        Some(f) => {
            f.write_all(body.as_bytes())?;
            if !body.ends_with('\n') && !body.is_empty() {
                writeln!(f)?;
            }
        }
        None => {
            print!("{body}");
            if !body.ends_with('\n') && !body.is_empty() {
                println!();
            }
        }
    }
    Ok(())
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

/// Dispatch one input through the requested command. Human-readable output is
/// printed immediately; json/yaml results are pushed onto `machine_docs` for
/// the caller to emit as one document.
fn process(
    cli: &Cli,
    input: &Input,
    config: &ResolvedConfig,
    multiple: bool,
    mut out_file: Option<&mut std::fs::File>,
    machine_docs: &mut Vec<output::MachineDoc>,
) -> Result<u8> {
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
            print_body(input, &body, multiple, out_file.as_deref_mut())?;
        }
        Command::Lex(args) => {
            let dialect = pipeline::resolve_dialect_by_name(config.dialect().as_deref())?;
            let variant = &outcome.variants[0];
            let (tokens, lex_errors) =
                pipeline::lex_variant(variant, dialect, config.template_blocks_indent());
            match args.format {
                OutputFormat::Human => {
                    let body = output::lex_human(&tokens);
                    print_body(input, &body, multiple, out_file.as_deref_mut())?;
                }
                OutputFormat::Json | OutputFormat::Yaml => {
                    machine_docs.push(output::MachineDoc::Lex {
                        filepath: input.fname.clone(),
                        tokens: output::lex_records(&tokens),
                    });
                }
                OutputFormat::None => {}
            }
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
            // Grammar failures come back embedded as unparsable sections, not
            // as `Err`, so surface them in the exit code (like Python's PRS
            // violations).
            for err in node.unparsable_summaries() {
                eprintln!("{}: parsing: {err}", input.fname);
                exit = exit.max(EXIT_FAIL);
            }
            match args.format {
                OutputFormat::Human => {
                    let body = output::parse_human(&node, args.code_only);
                    print_body(input, &body, multiple, out_file)?;
                }
                OutputFormat::Json | OutputFormat::Yaml => {
                    machine_docs.push(output::MachineDoc::Parse(output::parse_record(
                        &node,
                        &input.fname,
                        args.code_only,
                        args.include_meta,
                    )?));
                }
                OutputFormat::None => {}
            }
        }
    }

    Ok(exit)
}

/// Emit a command's output — to the shared `--write-output` file when one is
/// open, otherwise stdout — with a per-file header when more than one input is
/// being processed.
fn print_body(
    input: &Input,
    body: &str,
    multiple: bool,
    out_file: Option<&mut std::fs::File>,
) -> Result<()> {
    if let Some(f) = out_file {
        if multiple {
            writeln!(f, "== [{}] ==", input.fname)?;
        }
        f.write_all(body.as_bytes())?;
        if !body.ends_with('\n') && !body.is_empty() {
            writeln!(f)?;
        }
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
