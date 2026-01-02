SELECT
    TIMESTAMPDIFF(SECOND, b.bucket_start, t.block_timestamp) AS benchmark_staleness_seconds
FROM transmissions_enriched_gap_filled t
JOIN cex_benchmark b ON t.base = b.base;
