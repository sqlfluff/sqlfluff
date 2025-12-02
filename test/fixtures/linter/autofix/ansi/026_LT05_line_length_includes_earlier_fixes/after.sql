SELECT
    abs(round(foo_bar_report.metricx-xxx_yyy_report.metricx)) as col_c_rel_diff,
    abs(
        (
            round(foo_bar_report.metricx-xxx_yyy_report.metricx)
            /foo_bar_report.metricx
        )
        *100
    ) as metric_x_rel_diff
FROM foo_bar_report
LEFT JOIN xxx_yyy_report
    ON foo_bar_report.event_date = xxx_yyy_report.event_date;
