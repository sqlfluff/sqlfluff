SELECT
    abs(round(a.metricx-b.metricx)) as col_c_rel_diff,
    abs((round(a.metricx-b.metricx)/a.metricx)*100) as metric_x_rel_diff
FROM foo_bar_report a
LEFT JOIN xxx_yyy_report b
ON a.event_date = b.event_date;
