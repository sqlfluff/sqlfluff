CREATE VIEW a
AS
    SELECT
        c
    FROM table1
    INNER JOIN table2 ON (table1.id = table2.id);

CREATE OR REPLACE VIEW vw_appt_latest AS (
  WITH most_current as (
      SELECT
            da.*
      FROM dim_appt da
      WHERE da.current_appt_id IS NULL
      )
  SELECT * from most_current
);
