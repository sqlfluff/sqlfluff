# SQLFluff-rs

This package is an optional installation for [SQLFluff](https://github.com/sqlfluff/sqlfluff) and is **not** intended to be used as a standalone linting solution.

## Purpose

SQLFluff-rs serves as a Rust-based component that can be integrated with the main SQLFluff package. It is currently in development and should be considered experimental.

## Installation

This package is automatically handled when installing SQLFluff with the
appropriate optional dependencies. Direct installation is mainly useful for
development or debugging and is not the recommended end-user path.

To install from pip:
```sh
pip install sqlfluff[rs]
```

On supported CPython 3.10+ platforms, this resolves to a prebuilt ABI3 wheel.
That means the same wheel can be reused across newer CPython versions without a
separate wheel per interpreter.

If a wheel is not available for your platform, architecture, or Python
implementation, `pip` falls back to building from source. In that case you need:

- a Rust toolchain, typically installed with `rustup`
- a working C/C++ compiler toolchain for your platform
- Python headers and normal build tooling for native extensions

SQLFluff-rs is tested on more platforms and architecture combinations than we
currently publish Python wheels for. PyPI project storage limits mean we only
distribute wheels for the most common targets. Some platforms that are covered
by CI should therefore still reliably install from source despite not receiving
a prebuilt wheel.

For example, after installing Rust, a source install can still use the normal
SQLFluff extra:

```sh
pip install sqlfluff[rs]
```

Or to build this package directly from a checkout:

```sh
pip install ./sqlfluffrs
```

## Development Status

This is a supplementary component and is not meant to replace or function independently of the main SQLFluff package. For SQL linting, please use the main [SQLFluff](https://github.com/sqlfluff/sqlfluff) package.
