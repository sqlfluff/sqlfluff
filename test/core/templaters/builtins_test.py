from sqlfluff.core.templaters.builtins.dbt import DBT_BUILTINS


def test_relation_emulator_magic_methods():
    """Test all the magic methods defined on RelationEmulator."""
    # tests for 'this'
    t = DBT_BUILTINS["this"]
    assert str(t) == "this_model"
    assert t.something is t
    assert str(t.database) == "this_database"
    assert str(t.schema) == "this_schema"
    assert str(t.name) == "this_model"
    assert str(t.identifier) == "this_model"
    assert str(t.type) == "this_model"
    assert str(t.something_new) == "this_model"
    assert t.is_table is True
    assert t.is_view is True
    assert t.is_materialized_view is True
    assert t.is_cte is True
    assert t.is_dynamic_table is True
    assert t.is_iceberg_format is True
    assert t.is_something_new is True
    assert t.something() is t
    assert t.something().something() is t
    assert t.something().something is t
    assert str(t.include()) == "this_model"
    assert str(t.include(database=False)) == "this_model"
    assert str(t.some_new_method()) == "this_model"
    assert str(t.something().something) == "this_model"

    # tests for 'ref'
    r = DBT_BUILTINS["ref"]("ref_model")
    assert str(r) == "ref_model"
    assert r.something is r
    assert str(r.database) == "this_database"
    assert str(r.schema) == "this_schema"
    assert str(r.name) == "ref_model"
    assert str(r.identifier) == "ref_model"
    assert str(r.type) == "ref_model"
    assert str(r.something_new) == "ref_model"
    assert r.is_table is True
    assert r.is_view is True
    assert r.is_materialized_view is True
    assert r.is_cte is True
    assert r.is_dynamic_table is True
    assert r.is_iceberg_format is True
    assert r.is_something_new is True
    assert r.something() is r
    assert r.something().something() is r
    assert r.something().something is r
    assert str(r.include()) == "ref_model"
    assert str(r.include(database=False)) == "ref_model"
    assert str(r.some_new_method()) == "ref_model"
    assert str(r.something().something) == "ref_model"

    # tests for versioned 'ref'
    r = DBT_BUILTINS["ref"]("ref_model", version=2)
    assert str(r) == "ref_model"
    assert r.something is r
    assert str(r.database) == "this_database"
    assert str(r.schema) == "this_schema"
    assert str(r.name) == "ref_model"
    assert str(r.identifier) == "ref_model"
    assert str(r.type) == "ref_model"
    assert str(r.something_new) == "ref_model"
    assert r.is_table is True
    assert r.is_view is True
    assert r.is_materialized_view is True
    assert r.is_cte is True
    assert r.is_dynamic_table is True
    assert r.is_iceberg_format is True
    assert r.is_something_new is True
    assert r.something() is r
    assert r.something().something() is r
    assert r.something().something is r
    assert str(r.include()) == "ref_model"
    assert str(r.include(database=False)) == "ref_model"
    assert str(r.some_new_method()) == "ref_model"
    assert str(r.something().something) == "ref_model"

    # tests for 'ref' from project/package
    r = DBT_BUILTINS["ref"]("package", "ref_model")
    assert str(r) == "ref_model"
    assert r.something is r
    assert str(r.database) == "this_database"
    assert str(r.schema) == "this_schema"
    assert str(r.name) == "ref_model"
    assert str(r.identifier) == "ref_model"
    assert str(r.type) == "ref_model"
    assert str(r.something_new) == "ref_model"
    assert r.is_table is True
    assert r.is_view is True
    assert r.is_materialized_view is True
    assert r.is_cte is True
    assert r.is_dynamic_table is True
    assert r.is_iceberg_format is True
    assert r.is_something_new is True
    assert r.something() is r
    assert r.something().something() is r
    assert r.something().something is r
    assert str(r.include()) == "ref_model"
    assert str(r.include(database=False)) == "ref_model"
    assert str(r.some_new_method()) == "ref_model"
    assert str(r.something().something) == "ref_model"

    # tests for versioned 'ref' from project/package
    r = DBT_BUILTINS["ref"]("package", "ref_model", version=2)
    assert str(r) == "ref_model"
    assert r.something is r
    assert str(r.database) == "this_database"
    assert str(r.schema) == "this_schema"
    assert str(r.name) == "ref_model"
    assert str(r.identifier) == "ref_model"
    assert str(r.type) == "ref_model"
    assert str(r.something_new) == "ref_model"
    assert r.is_table is True
    assert r.is_view is True
    assert r.is_materialized_view is True
    assert r.is_cte is True
    assert r.is_dynamic_table is True
    assert r.is_iceberg_format is True
    assert r.is_something_new is True
    assert r.something() is r
    assert r.something().something() is r
    assert r.something().something is r
    assert str(r.include()) == "ref_model"
    assert str(r.include(database=False)) == "ref_model"
    assert str(r.some_new_method()) == "ref_model"
    assert str(r.something().something) == "ref_model"

    # tests for 'source'
    s = DBT_BUILTINS["source"]("sourcename", "tablename")
    assert str(s) == "sourcename_tablename"
    assert s.something is s
    assert str(s.database) == "this_database"
    assert str(s.schema) == "this_schema"
    assert str(s.name) == "sourcename_tablename"
    assert str(s.identifier) == "sourcename_tablename"
    assert str(s.type) == "sourcename_tablename"
    assert str(s.something_new) == "sourcename_tablename"
    assert s.is_table is True
    assert s.is_view is True
    assert s.is_materialized_view is True
    assert s.is_cte is True
    assert s.is_dynamic_table is True
    assert s.is_iceberg_format is True
    assert s.is_something_new is True
    assert s.something() is s
    assert s.something().something() is s
    assert s.something().something is s
    assert str(s.include()) == "sourcename_tablename"
    assert str(s.include(database=False)) == "sourcename_tablename"
    assert str(s.some_new_method()) == "sourcename_tablename"
    assert str(s.something().something) == "sourcename_tablename"
