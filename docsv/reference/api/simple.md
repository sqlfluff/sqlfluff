# simple

The simple API provides high-level functions for linting, fixing, and parsing SQL strings.

## Classes

### APIParsingError

An exception which holds a set of violations.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `violations` | `list[SQLBaseError]` | — |  |
| `args` | `Any` | — |  |

## Functions

### fix

```python
fix(sql, dialect=None, rules=None, exclude_rules=None, config=None, config_path=None, fix_even_unparsable=None) → str
```

Fix a SQL string.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sql` | `str` | — | The SQL to be fixed. |
| `dialect` | `Optional[str]` | `None` | A reference to the dialect of the SQL to be fixed. Defaults to `ansi`. |
| `rules` | `Optional[list[str]]` | `None` | A subset of rule references to fix for. Defaults to None. |
| `exclude_rules` | `Optional[list[str]]` | `None` | A subset of rule references to avoid fixing for. Defaults to None. |
| `config` | `Optional[fluffconfig.FluffConfig]` | `None` | A configuration object to use for the operation. Defaults to None. |
| `config_path` | `Optional[str]` | `None` | A path to a .sqlfluff config, which is only used if a `config` is not already provided. Defaults to None. |
| `fix_even_unparsable` | `Optional[bool]` | `None` | Optional override for the corresponding SQLFluff configuration value. |

**Returns:**

`str` — :obj:`str` for the fixed SQL if possible.

### get_simple_config

```python
get_simple_config(dialect=None, rules=None, exclude_rules=None, config_path=None) → fluffconfig.FluffConfig
```

Get a config object from simple API arguments.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dialect` | `Optional[str]` | `None` |  |
| `rules` | `Optional[list[str]]` | `None` |  |
| `exclude_rules` | `Optional[list[str]]` | `None` |  |
| `config_path` | `Optional[str]` | `None` |  |

**Returns:**

`fluffconfig.FluffConfig` — See return type above

### lint

```python
lint(sql, dialect=None, rules=None, exclude_rules=None, config=None, config_path=None) → list[dict[str, Any]]
```

Lint a SQL string.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sql` | `str` | — | The SQL to be linted. |
| `dialect` | `Optional[str]` | `None` | A reference to the dialect of the SQL to be linted. Defaults to `ansi`. |
| `rules` | `Optional[list[str]]` | `None` | A list of rule references to lint for. Defaults to None. |
| `exclude_rules` | `Optional[list[str]]` | `None` | A list of rule references to avoid linting for. Defaults to None. |
| `config` | `Optional[fluffconfig.FluffConfig]` | `None` | A configuration object to use for the operation. Defaults to None. |
| `config_path` | `Optional[str]` | `None` | A path to a .sqlfluff config, which is only used if a `config` is not already provided. Defaults to None. |

**Returns:**

`list[dict[str, Any]]` — :obj:`list[dict[str, Any]]` for each violation found.

### parse

```python
parse(sql, dialect=None, config=None, config_path=None) → dict[str, Any]
```

Parse a SQL string.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sql` | `str` | — | The SQL to be parsed. |
| `dialect` | `Optional[str]` | `None` | A reference to the dialect of the SQL to be parsed. Defaults to `ansi`. |
| `config` | `Optional[fluffconfig.FluffConfig]` | `None` | A configuration object to use for the operation. Defaults to None. |
| `config_path` | `Optional[str]` | `None` | A path to a .sqlfluff config, which is only used if a `config` is not already provided. Defaults to None. |

**Returns:**

`dict[str, Any]` — :obj:`Dict[str, Any]` JSON containing the parsed structure.

**Note:** In the case of multiple potential variants from the raw source file
    only the first variant is returned by the simple API. For access to
    the other variants, use the underlying main API directly.
