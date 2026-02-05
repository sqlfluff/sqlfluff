"""Test for CV13 rule."""

import sqlfluff


def test_cv13_serial_postgres():
    """Test that CV13 flags SERIAL in PostgreSQL."""
    sql = "CREATE TABLE t (id SERIAL PRIMARY KEY);"
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="postgres")
    
    assert len(result) == 1
    assert "SERIAL" in result[0]["description"]
    assert "IDENTITY" in result[0]["description"]


def test_cv13_bigserial_postgres():
    """Test that CV13 flags BIGSERIAL in PostgreSQL."""
    sql = "CREATE TABLE t (id BIGSERIAL PRIMARY KEY);"
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="postgres")
    
    assert len(result) == 1
    assert "BIGSERIAL" in result[0]["description"]


def test_cv13_smallserial_postgres():
    """Test that CV13 flags SMALLSERIAL in PostgreSQL."""
    sql = "CREATE TABLE t (id SMALLSERIAL PRIMARY KEY);"
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="postgres")
    
    assert len(result) == 1
    assert "SMALLSERIAL" in result[0]["description"]


def test_cv13_pass_mysql():
    """Test that CV13 does not flag SERIAL in MySQL (rule is PostgreSQL-specific)."""
    sql = "CREATE TABLE t (id SERIAL PRIMARY KEY);"
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="mysql")
    
    assert len(result) == 0


def test_cv13_pass_identity_postgres():
    """Test that CV13 does not flag GENERATED AS IDENTITY."""
    sql = "CREATE TABLE t (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY);"
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="postgres")
    
    assert len(result) == 0


def test_cv13_multiple_columns():
    """Test that CV13 flags multiple SERIAL columns."""
    sql = """
    CREATE TABLE t (
        id SERIAL PRIMARY KEY,
        external_id BIGSERIAL,
        seq SMALLSERIAL
    );
    """
    result = sqlfluff.lint(sql, rules=["CV13"], dialect="postgres")
    
    # Should flag 3 violations
    assert len(result) == 3
