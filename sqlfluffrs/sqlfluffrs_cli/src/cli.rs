//! Command-line argument definitions (clap), mirroring the subset of the
//! Python `sqlfluff` CLI that this Rust entry point implements: `render`,
//! `parse`, and `lex`.

use clap::{Args, Parser, Subcommand, ValueEnum};

/// SQLFluff — Rust command entry point (render / parse / lex).
#[derive(Debug, Parser)]
#[command(name = "sqlfluff-rs", version, about, disable_help_subcommand = true)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Debug, Subcommand)]
pub enum Command {
    /// Lex SQL files and emit the resulting tokens.
    Lex(LexArgs),
    /// Parse SQL files and emit the parse tree.
    Parse(ParseArgs),
    /// Render templated SQL files and emit the templated result.
    Render(RenderArgs),
}

/// Options shared by every command (a subset of the Python "core options").
#[derive(Debug, Args, Clone)]
pub struct CoreArgs {
    /// One or more files or directories to process; `-` reads from stdin.
    #[arg(value_name = "PATH", required = true)]
    pub paths: Vec<String>,

    /// The dialect of SQL to operate on (e.g. `ansi`, `postgres`).
    #[arg(short = 'd', long)]
    pub dialect: Option<String>,

    /// The templater to use (e.g. `raw`, `jinja`, `python`, `placeholder`, `dbt`).
    #[arg(short = 't', long)]
    pub templater: Option<String>,

    /// Include an additional config file (`.sqlfluff`/cfg format) at the lowest priority.
    #[arg(long, value_name = "PATH")]
    pub config: Option<String>,

    /// Ignore config files in the default search locations.
    #[arg(long)]
    pub ignore_local_config: bool,

    /// The encoding to use when reading files (default: autodetect/utf-8).
    #[arg(long)]
    pub encoding: Option<String>,

    /// Override the Jinja library path.
    #[arg(long, value_name = "PATH")]
    pub library_path: Option<String>,

    /// When reading from stdin, treat input as if it lived at this path (for config).
    #[arg(long, value_name = "PATH")]
    pub stdin_filename: Option<String>,

    /// Increase verbosity (stackable: -v, -vv, ...).
    #[arg(short = 'v', long, action = clap::ArgAction::Count)]
    pub verbose: u8,

    /// Disable colored output.
    #[arg(short = 'n', long = "nocolor")]
    pub nocolor: bool,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq, ValueEnum, Default)]
pub enum OutputFormat {
    #[default]
    Human,
    Json,
    Yaml,
    None,
}

#[derive(Debug, Args, Clone)]
pub struct LexArgs {
    #[command(flatten)]
    pub core: CoreArgs,

    /// Output format.
    #[arg(short = 'f', long, value_enum, default_value_t = OutputFormat::Human)]
    pub format: OutputFormat,

    /// Write output to a file instead of stdout.
    #[arg(long, value_name = "PATH")]
    pub write_output: Option<String>,
}

#[derive(Debug, Args, Clone)]
pub struct RenderArgs {
    #[command(flatten)]
    pub core: CoreArgs,
}

#[derive(Debug, Args, Clone)]
pub struct ParseArgs {
    #[command(flatten)]
    pub core: CoreArgs,

    /// Output format.
    #[arg(short = 'f', long, value_enum, default_value_t = OutputFormat::Human)]
    pub format: OutputFormat,

    /// Output only the code-affecting elements (skip whitespace etc.).
    #[arg(short = 'c', long)]
    pub code_only: bool,

    /// Include meta segments (indents, dedents, placeholders) in the output.
    #[arg(short = 'm', long)]
    pub include_meta: bool,

    /// Write output to a file instead of stdout.
    #[arg(long, value_name = "PATH")]
    pub write_output: Option<String>,
}

impl Command {
    /// Access the shared core options regardless of subcommand.
    pub fn core(&self) -> &CoreArgs {
        match self {
            Command::Lex(a) => &a.core,
            Command::Parse(a) => &a.core,
            Command::Render(a) => &a.core,
        }
    }

    /// The `--write-output` path, for the subcommands that support it.
    pub fn write_output(&self) -> Option<&str> {
        match self {
            Command::Lex(a) => a.write_output.as_deref(),
            Command::Parse(a) => a.write_output.as_deref(),
            Command::Render(_) => None,
        }
    }
}
