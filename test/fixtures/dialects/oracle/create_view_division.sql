-- A `/` inside a view is division; only one alone on its line is the
-- SQL*Plus buffer executor (see slash_batch_delimiter.sql).
CREATE VIEW myview AS
select 1 / 100 as z from dual;

create or replace view recent_samples as
select sample_time, nvl(bytes, 0) / 1024 / 1024 as size_mb
from io_stats
where sample_time > sysdate - 1/24;

create or replace view ratios as
select a / b as ratio
from t
/
