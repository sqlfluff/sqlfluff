SELECT histogram(5)(number + 1) FROM system.numbers LIMIT 20;

SELECT histogram(10)(value) FROM data;

SELECT median(value) FROM data;

SELECT medianBFloat16(value) FROM data;

SELECT quantile(0.95)(response_time) FROM metrics;

SELECT quantile(0.5)(price) FROM sales;

SELECT quantile(price) FROM sales;

SELECT quantiles(0.25, 0.5, 0.75)(value) FROM data;

SELECT quantiles(0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)(click) AS quantiles_click_size
FROM clickhouse_table;

SELECT
    quantiles(0.25, 0.5, 0.75)(col1) AS q1,
    quantiles(0.1, 0.9)(col2) AS q2
FROM table1;

SELECT quantileBFloat16(0.75)(a), quantileBFloat16(0.75)(b) FROM example_table;

SELECT quantileDD(0.5)(value) FROM data;

SELECT quantileDeterministic(0.5)(value, id) FROM test_table;

SELECT quantileDeterministic(value, 1) FROM test_table;

SELECT quantilesDeterministic(0.25, 0.5, 0.75)(x, id) FROM test_table;

SELECT quantileExact(0.95)(value) FROM data;

SELECT quantilesExact(0.25, 0.5, 0.75, 0.9)(value) FROM data;

SELECT retention(date = '2020-01-01', date = '2020-01-02', date = '2020-01-03') AS r FROM events;

SELECT sequenceCount('(?1)(?2)')(timestamp, event_type = 1, event_type = 2) FROM user_events;

SELECT sequenceMatch('(?1)(?2)')(timestamp, event_type = 1, event_type = 2) FROM user_events;

SELECT studentTTest(sample_data, sample_index) FROM student_ttest;

SELECT studentTTest(0.95)(sample_data, sample_index) FROM student_ttest;

SELECT studentTTestOneSample()(value, 20.0) FROM student_ttest;

SELECT studentTTestOneSample(value, 20.0) FROM student_ttest;

SELECT studentTTestOneSample(0.95)(value, 20.0) FROM student_ttest;

SELECT sumMapFilteredWithOverflow([1, 4, 8])(statusMap.status, statusMap.requests) as summap_overflow, toTypeName(summap_overflow) FROM sum_map;
