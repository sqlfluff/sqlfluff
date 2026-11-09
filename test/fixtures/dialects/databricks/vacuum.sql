-- VACUUM. https://docs.databricks.com/aws/en/sql/language-manual/delta-vacuum
VACUUM t;

VACUUM t DRY RUN;

VACUUM t FULL;

VACUUM t LITE;

VACUUM t RETAIN 168 HOURS DRY RUN;

VACUUM t LITE DRY RUN;
