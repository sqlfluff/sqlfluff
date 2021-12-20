# Rule Tests

All the individual rule unit tests are defined in yml files.

Note that all the enumerated test names (test_1 etc.) were copied over from a previous format with an automated script. All new tests should be named descriptively with comments for more context if needed.

## Making a test case

### Writing a test for a query that should pass linting

A test for a passing query is declared like this:

```
descriptive_test_name:
  pass_str: select * from x
```

### Writing a test for a query that should fail linting

A test for a failing query is declared like this:

```
descriptive_test_name:
  fail_str: select * FROM x
```

and can optionally include a test for the fixed query that the rule returns:

```
descriptive_test_name:
  fail_str: select * FROM x
  fix_str: select * from x
```

### Rule Configuration

If your test needs additional rule configuration, this can be supplied through a `configs` key, such as:

```
test_keyword_as_identifier:
  fail_str: SELECT parameter

  configs:
    rules:
      L029:
        only_aliases: false
```

## Yaml Syntax

Using yaml make it really easy to flexibly create test cases. You can create single line test cases with explicit newlines and tabs using `\n` and `\t` when it makes sense, or create multi-line test cases which are much easier to read for longer queries.

A good reference on multiline yaml syntax can be found [here](https://yaml-multiline.info/).
