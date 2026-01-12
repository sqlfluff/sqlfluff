/// Phase 1 Baseline Benchmarks for Table-Driven Grammar Migration
///
/// This benchmark suite establishes baseline performance metrics before
/// migrating to table-driven grammar representation.
///
/// Metrics tracked:
/// - Parse time for various query types
/// - Memory allocations (requires manual profiling)
/// - Cache effectiveness
///
/// Run with: cargo bench --bench baseline_phase1
/// View results: target/criterion/report/index.html
use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};

use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

/// Helper to lex SQL into tokens
fn lex_sql(sql: &str) -> Vec<sqlfluffrs_types::Token> {
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    tokens
}

// ============================================================================
// Simple Queries (baseline for fast paths)
// ============================================================================

fn bench_simple_select(c: &mut Criterion) {
    let sql = "SELECT id, name FROM users WHERE age > 18";
    let tokens = lex_sql(sql);

    c.bench_function("baseline/simple_select", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_simple_insert(c: &mut Criterion) {
    let sql = "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)";
    let tokens = lex_sql(sql);

    c.bench_function("baseline/simple_insert", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_simple_update(c: &mut Criterion) {
    let sql = "UPDATE users SET age = 26 WHERE id = 1";
    let tokens = lex_sql(sql);

    c.bench_function("baseline/simple_update", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Complex JOINs (tests nested grammar matching)
// ============================================================================

fn bench_complex_join(c: &mut Criterion) {
    let sql = r#"
        SELECT
            u.id,
            u.name,
            o.order_date,
            SUM(oi.quantity * oi.price) AS total
        FROM users u
        INNER JOIN orders o ON u.id = o.user_id
        INNER JOIN order_items oi ON o.id = oi.order_id
        WHERE u.age > 18
          AND o.order_date >= '2024-01-01'
        GROUP BY u.id, u.name, o.order_date
        HAVING SUM(oi.quantity * oi.price) > 100
        ORDER BY total DESC
        LIMIT 10
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/complex_join", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_multiple_joins(c: &mut Criterion) {
    let sql = r#"
        SELECT *
        FROM t1
        JOIN t2 ON t1.id = t2.id
        JOIN t3 ON t2.id = t3.id
        JOIN t4 ON t3.id = t4.id
        JOIN t5 ON t4.id = t5.id
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/multiple_joins", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Nested Subqueries (tests recursion depth)
// ============================================================================

fn bench_nested_subqueries(c: &mut Criterion) {
    let sql = r#"
        SELECT *
        FROM (
            SELECT id, name
            FROM (
                SELECT id, name, age
                FROM users
                WHERE age > 18
            ) t1
            WHERE name LIKE 'A%'
        ) t2
        WHERE id IN (
            SELECT user_id
            FROM orders
            WHERE total > 100
        )
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/nested_subqueries", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_deeply_nested(c: &mut Criterion) {
    let sql = r#"
        SELECT * FROM (
            SELECT * FROM (
                SELECT * FROM (
                    SELECT * FROM (
                        SELECT * FROM t
                    ) a
                ) b
            ) c
        ) d
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/deeply_nested", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Window Functions (tests complex expressions)
// ============================================================================

fn bench_window_functions(c: &mut Criterion) {
    let sql = r#"
        SELECT
            id,
            name,
            salary,
            department,
            ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
            AVG(salary) OVER (PARTITION BY department) AS dept_avg,
            SUM(salary) OVER (ORDER BY hire_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS running_sum
        FROM employees
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/window_functions", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// CTEs (Common Table Expressions)
// ============================================================================

fn bench_cte(c: &mut Criterion) {
    let sql = r#"
        WITH regional_sales AS (
            SELECT region, SUM(amount) AS total_sales
            FROM orders
            GROUP BY region
        ),
        top_regions AS (
            SELECT region
            FROM regional_sales
            WHERE total_sales > (SELECT SUM(total_sales)/10 FROM regional_sales)
        )
        SELECT region,
               product,
               SUM(quantity) AS product_units,
               SUM(amount) AS product_sales
        FROM orders
        WHERE region IN (SELECT region FROM top_regions)
        GROUP BY region, product
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/cte", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_recursive_cte(c: &mut Criterion) {
    let sql = r#"
        WITH RECURSIVE t(n) AS (
            SELECT 1
            UNION ALL
            SELECT n+1 FROM t WHERE n < 100
        )
        SELECT sum(n) FROM t
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/recursive_cte", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Large Statements (tests scaling)
// ============================================================================

fn bench_large_insert(c: &mut Criterion) {
    let mut sql = String::from("INSERT INTO users (id, name, age) VALUES ");
    for i in 0..100 {
        if i > 0 {
            sql.push_str(", ");
        }
        sql.push_str(&format!("({}, 'user{}', {})", i, i, 20 + (i % 50)));
    }
    let tokens = lex_sql(&sql);

    c.bench_function("baseline/large_insert_100", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_many_columns_select(c: &mut Criterion) {
    let mut sql = String::from("SELECT ");
    for i in 0..100 {
        if i > 0 {
            sql.push_str(", ");
        }
        sql.push_str(&format!("col{}", i));
    }
    sql.push_str(" FROM table");
    let tokens = lex_sql(&sql);

    c.bench_function("baseline/select_100_columns", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Scaling Tests (measure how performance scales with size)
// ============================================================================

fn bench_scaling_by_column_count(c: &mut Criterion) {
    let mut group = c.benchmark_group("baseline/scaling_columns");

    for &count in &[10, 25, 50, 100, 200] {
        let mut sql = String::from("SELECT ");
        for i in 0..count {
            if i > 0 {
                sql.push_str(", ");
            }
            sql.push_str(&format!("col{}", i));
        }
        sql.push_str(" FROM table");
        let tokens = lex_sql(&sql);

        group.bench_with_input(BenchmarkId::from_parameter(count), &count, |b, _| {
            b.iter(|| {
                let mut parser =
                    Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
                parser.call_rule_as_root().expect("Parse failed")
            })
        });
    }

    group.finish();
}

fn bench_scaling_by_join_count(c: &mut Criterion) {
    let mut group = c.benchmark_group("baseline/scaling_joins");

    for &count in &[2, 5, 10, 15, 20] {
        let mut sql = String::from("SELECT * FROM t0 ");
        for i in 1..count {
            sql.push_str(&format!("JOIN t{} ON t{}.id = t{}.id ", i, i - 1, i));
        }
        let tokens = lex_sql(&sql);

        group.bench_with_input(BenchmarkId::from_parameter(count), &count, |b, _| {
            b.iter(|| {
                let mut parser =
                    Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
                parser.call_rule_as_root().expect("Parse failed")
            })
        });
    }

    group.finish();
}

// ============================================================================
// Cache Effectiveness Tests
// ============================================================================

fn bench_cache_on_vs_off(c: &mut Criterion) {
    let sql = "SELECT a FROM (SELECT b FROM (SELECT c FROM t))";
    let tokens = lex_sql(sql);

    let mut group = c.benchmark_group("baseline/cache_effectiveness");

    group.bench_function("cache_on", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.set_cache_enabled(true);
            parser.call_rule_as_root().expect("Parse failed")
        })
    });

    group.bench_function("cache_off", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.set_cache_enabled(false);
            parser.call_rule_as_root().expect("Parse failed")
        })
    });

    group.finish();
}

fn bench_repeated_parsing(c: &mut Criterion) {
    // Test if cache benefits appear across multiple parses of same query
    let sql = "SELECT id, name, age FROM users WHERE status = 'active'";
    let tokens = lex_sql(sql);

    c.bench_function("baseline/repeated_parse_with_cache", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.set_cache_enabled(true);
            // Parse twice to test cache effectiveness
            let _first = parser.call_rule_as_root().expect("Parse failed");
        })
    });
}

// ============================================================================
// Expression Complexity Tests
// ============================================================================

fn bench_nested_functions(c: &mut Criterion) {
    let sql = "SELECT CONCAT(UPPER(LEFT(name, 5)), LOWER(RIGHT(SUBSTRING(description, 10, 20), 5))) FROM users";
    let tokens = lex_sql(sql);

    c.bench_function("baseline/nested_functions", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

fn bench_complex_where(c: &mut Criterion) {
    let sql = r#"
        SELECT * FROM users
        WHERE (age > 18 AND status = 'active')
           OR (age > 65 AND status = 'retired')
           OR (premium = true AND age > 25)
           AND NOT (banned = true OR suspended = true)
           AND created_at > '2020-01-01'
    "#;
    let tokens = lex_sql(sql);

    c.bench_function("baseline/complex_where", |b| {
        b.iter(|| {
            let mut parser =
                Parser::new(black_box(&tokens), Dialect::Ansi, hashbrown::HashMap::new());
            parser.call_rule_as_root().expect("Parse failed")
        })
    });
}

// ============================================================================
// Benchmark Groups
// ============================================================================

criterion_group!(
    simple_queries,
    bench_simple_select,
    bench_simple_insert,
    bench_simple_update,
);

criterion_group!(
    complex_queries,
    bench_complex_join,
    bench_multiple_joins,
    bench_nested_subqueries,
    bench_deeply_nested,
);

criterion_group!(
    advanced_features,
    bench_window_functions,
    bench_cte,
    bench_recursive_cte,
);

criterion_group!(
    large_statements,
    bench_large_insert,
    bench_many_columns_select,
);

criterion_group!(
    scaling_tests,
    bench_scaling_by_column_count,
    bench_scaling_by_join_count,
);

criterion_group!(cache_tests, bench_cache_on_vs_off, bench_repeated_parsing,);

criterion_group!(
    expression_tests,
    bench_nested_functions,
    bench_complex_where,
);

criterion_main!(
    simple_queries,
    complex_queries,
    advanced_features,
    large_statements,
    scaling_tests,
    cache_tests,
    expression_tests,
);
