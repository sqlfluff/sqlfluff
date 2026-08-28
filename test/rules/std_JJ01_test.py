"""Tests JJ01 in a parallel environment.

This rule has had issues in the past with raising exceptions
in parallel environments because it tries to access the
templater.
"""

import pickle

from sqlfluff.core import FluffConfig, Linter


def test_lint_jj01_pickled_config():
    """Tests the error catching behavior of _lint_path_parallel_wrapper().

    Test on MultiThread runner because otherwise we have pickling issues.
    """
    fname = "test/fixtures/linter/jinja_spacing.sql"
    fresh_cfg = FluffConfig(overrides={"dialect": "ansi", "rules": "JJ01"})
    # Parse the file with the fresh config.
    linter = Linter(config=fresh_cfg)
    parsed = next(linter.parse_path(fname))
    rule_pack = linter.get_rulepack(config=fresh_cfg)
    rule = rule_pack.rules[0]
    # Check we got the right rule.
    assert rule.code == "JJ01"
    # Pickle the config and rehydrate to simulate threaded operation
    pickled = pickle.dumps(fresh_cfg)
    unpickled_cfg = pickle.loads(pickled)
    # Crawl with the pickled config. Check we don't get an error.
    linting_errors, _, fixes, _ = rule.crawl(
        parsed.tree,
        dialect=unpickled_cfg.get("dialect_obj"),
        fix=True,
        templated_file=parsed.parsed_variants[0].templated_file,
        ignore_mask=None,
        fname=fname,
        config=unpickled_cfg,  # <- NOTE: This is the important part.
    )
    # Check we successfully got the right results.
    assert len(linting_errors) == 1
    assert linting_errors[0].check_tuple() == ("JJ01", 3, 15)


def test_lint_jj01_custom_delimiters():
    """Test JJ01 works with custom Jinja delimiters."""
    sql = "SELECT * FROM <%foo%>"
    config = FluffConfig.from_string(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "rules = JJ01\n"
        "templater = jinja\n"
        "[sqlfluff:templater:jinja]\n"
        "variable_start_string = <%\n"
        "variable_end_string = %>\n"
        "[sqlfluff:templater:jinja:context]\n"
        "foo = bar\n"
    )
    linter = Linter(config=config)
    result = linter.lint_string(sql)
    assert len(result.violations) == 1
    assert result.violations[0].check_tuple()[0] == "JJ01"


def test_lint_jj01_mixed_custom_and_default_delimiters():
    """Custom variable delimiters coexist with default block delimiters."""
    sql = "{%if true%}SELECT <%foo%> AS x{%endif%}\n"
    config = FluffConfig.from_string(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "rules = JJ01\n"
        "templater = jinja\n"
        "[sqlfluff:templater:jinja]\n"
        "variable_start_string = <%\n"
        "variable_end_string = %>\n"
        "[sqlfluff:templater:jinja:context]\n"
        "foo = bar\n"
    )
    linter = Linter(config=config)
    result = linter.lint_string(sql)
    jj01 = [v for v in result.violations if v.rule_code() == "JJ01"]
    assert len(jj01) == 3
