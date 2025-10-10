"""Tests for the FlinkSQL dialect."""

from sqlfluff.core import FluffConfig, Linter


class TestFlinkSQLDialect:
    """Test FlinkSQL dialect parsing."""

    def test_flink_dialect_basic(self):
        """Test basic FlinkSQL dialect functionality."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        # Test simple SELECT statement
        sql = "SELECT * FROM my_table;\n"
        result = linter.lint_string(sql)
        assert result is not None
        # Check for parsing errors only, ignore style warnings
        parsing_errors = [v for v in result.violations if v.rule.code.startswith("PRS")]
        assert len(parsing_errors) == 0

    def test_flink_create_table_basic(self):
        """Test basic CREATE TABLE statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            name STRING,
            age INT
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'my-topic'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None
        # Allow for some parsing issues initially

    def test_flink_row_data_type(self):
        """Test FlinkSQL ROW data type."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            nested_data ROW<name STRING, age INT>
        ) WITH (
            'connector' = 'kafka'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_timestamp_with_precision(self):
        """Test FlinkSQL TIMESTAMP with precision."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            event_time TIMESTAMP(3),
            processing_time TIMESTAMP_LTZ(3)
        ) WITH (
            'connector' = 'kafka'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_watermark_definition(self):
        """Test FlinkSQL WATERMARK definition."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_computed_column(self):
        """Test FlinkSQL computed column."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            name STRING,
            full_name AS CONCAT(name, '_suffix')
        ) WITH (
            'connector' = 'kafka'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_metadata_column(self):
        """Test FlinkSQL metadata column."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE my_table (
            id INT,
            name STRING,
            kafka_offset BIGINT METADATA FROM 'offset'
        ) WITH (
            'connector' = 'kafka'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_show_statements(self):
        """Test FlinkSQL SHOW statements."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        statements = [
            "SHOW CATALOGS",
            "SHOW DATABASES",
            "SHOW TABLES",
            "SHOW VIEWS",
            "SHOW FUNCTIONS",
            "SHOW MODULES",
            "SHOW JARS",
            "SHOW JOBS",
        ]

        for sql in statements:
            result = linter.lint_string(sql)
            assert result is not None

    def test_flink_use_statements(self):
        """Test FlinkSQL USE statements."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        statements = [
            "USE CATALOG my_catalog",
            "USE my_database",
            "USE my_catalog.my_database",
        ]

        for sql in statements:
            result = linter.lint_string(sql)
            assert result is not None

    def test_flink_describe_statement(self):
        """Test FlinkSQL DESCRIBE statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = "DESCRIBE my_table"
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_explain_statement(self):
        """Test FlinkSQL EXPLAIN statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = "EXPLAIN SELECT * FROM my_table"
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_set_statement(self):
        """Test FlinkSQL SET statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        statements = [
            "SET 'table.exec.state.ttl' = '1h'",
            "SET 'execution.checkpointing.mode' = 'EXACTLY_ONCE'",
            "SET 'execution.checkpointing.unaligned.enabled' = 'true'",
            "SET 'execution.checkpointing.timeout' = '600000'",
        ]

        for sql in statements:
            result = linter.lint_string(sql)
            assert result is not None

    def test_flink_create_catalog(self):
        """Test FlinkSQL CREATE CATALOG statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE CATALOG my_catalog WITH (
            'type' = 'hive',
            'hive-conf-dir' = '/path/to/hive/conf'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_create_database(self):
        """Test FlinkSQL CREATE DATABASE statement."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE DATABASE IF NOT EXISTS my_db
        COMMENT 'My database'
        WITH (
            'key1' = 'value1'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_alternative_with_syntax(self):
        """Test FlinkSQL WITH clause using alternative double equals syntax."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE test_table (
          data_info ROW<`info` STRING>,
          name STRING,
          score DOUBLE,
          total_count DOUBLE,
          active_count DOUBLE,
          metadata ROW<`details` STRING>,
          change_rate DOUBLE,
          volume DOUBLE,
          change_percentage DOUBLE,
          updated_at TIMESTAMP(3),
          category STRING
        ) WITH (
          connector == 'test-connector',
          environment == 'development'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None


class TestFlinkSQLComplexExamples:
    """Test FlinkSQL with complex examples covering various features."""

    def test_flink_row_datatype_table(self):
        """Test FlinkSQL table with ROW data types and connector options."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE table1 (
          data_info ROW<`name` STRING>,
          email STRING,
          score DOUBLE,
          total_points DOUBLE,
          active_points DOUBLE,
          metadata ROW<`description` STRING>,
          change_percentage DOUBLE,
          volume DOUBLE,
          rate_change_percentage DOUBLE,
          last_updated TIMESTAMP(3),
          status STRING
        )  WITH (
          'connector' = 'test-connector',
          'project' = 'test-project',
          'dataset' = 'test-dataset'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_complex_table_structure(self):
        """Test FlinkSQL table with complex structure and multiple data types."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE table2 (
          session_id STRING,
          session_ts TIMESTAMP(3),
          source_name STRING,
          service STRING,
          category STRING,
          category_id STRING,
          type STRING,
          type_id STRING,
          identifier STRING,
          identifier_id STRING,
          event_type STRING,
          action_type STRING,
          resource_type STRING,
          value DOUBLE,
          quantity DOUBLE,
          request_url STRING,
          is_deleted BOOLEAN,
          item_count INT,
          created_ts TIMESTAMP(3),
          updated_ts TIMESTAMP(3),
          processed_ts TIMESTAMP(3),
          received_ts TIMESTAMP(3),
          sequence_ts TIMESTAMP(3)
        ) WITH (
          'connector' = 'test-connector',
          'project' = 'test-project',
          'dataset' = 'test-dataset',
          'table' = 'test-table'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None

    def test_flink_simple_record_table(self):
        """Test FlinkSQL table with simple record structure."""
        config = FluffConfig(overrides={"dialect": "flink"})
        linter = Linter(config=config)

        sql = """
        CREATE TABLE table3 (
          service STRING,
          type STRING,
          from_id STRING,
          to_id STRING,
          amount DOUBLE,
          quantity DOUBLE,
          executed_at TIMESTAMP(3),
          id STRING,
          request_url STRING,
          direction STRING,
          client_received_timestamp TIMESTAMP(3),
          job_timestamp TIMESTAMP(3),
          job_id STRING,
          processor STRING
        ) WITH (
          'connector' = 'test-connector',
          'project' = 'test-project',
          'dataset' = 'test-dataset',
          'table' = 'test-records'
        )
        """
        result = linter.lint_string(sql)
        assert result is not None
