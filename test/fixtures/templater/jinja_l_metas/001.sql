{% set some_condition %}TRUE{% endset %}

WITH cust AS
    (SELECT SNAPSHOT_DATE
    FROM DATAHUB.SNAPSHOT_DAILY
    WHERE {{some_condition}}
    )

SELECT DISTINCT cust.SNAPSHOT_DATE
FROM cust