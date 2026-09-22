-- OPTIMIZE. https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize
OPTIMIZE events;

OPTIMIZE events WHERE date >= '2017-01-01';

OPTIMIZE events ZORDER BY (eventType);

OPTIMIZE events ZORDER BY (a, b);

OPTIMIZE events WHERE date >= current_timestamp() - INTERVAL 1 day ZORDER BY (eventType);

OPTIMIZE events FULL;

OPTIMIZE events FULL WHERE date >= '2025-01-01';

OPTIMIZE events FULL WHERE date >= '2025-01-01' ZORDER BY (a);
