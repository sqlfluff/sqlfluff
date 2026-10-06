CREATE OR ALTER DYNAMIC TABLE dt_custom_incremental (
    id NUMBER,
    amount NUMBER(13, 2) COMMENT 'Amount',
    updated_at TIMESTAMP_LTZ(9)
)
SCHEDULER = DISABLE
WAREHOUSE = wh
REFRESH_MODE = CUSTOM_INCREMENTAL
INITIALIZE = ON_SCHEDULE
COMMENT = 'custom incremental dynamic table'
REFRESH USING (
    MERGE INTO SELF AS target
    USING (
        SELECT
            id,
            amount,
            updated_at
        FROM src_table CHANGES(INFORMATION => DEFAULT)
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY id ORDER BY updated_at DESC
        ) = 1
    ) AS origin
    ON target.id = origin.id
    WHEN MATCHED AND origin.updated_at >= target.updated_at THEN UPDATE SET
        target.amount = origin.amount,
        target.updated_at = origin.updated_at
    WHEN NOT MATCHED THEN INSERT (id, amount, updated_at)
        VALUES (origin.id, origin.amount, origin.updated_at)
);

CREATE OR REPLACE DYNAMIC TABLE dt_custom_incremental_backfill (
    id NUMBER,
    amount NUMBER
)
TARGET_LAG = DOWNSTREAM
WAREHOUSE = wh
REFRESH_MODE = CUSTOM_INCREMENTAL
BACKFILL FROM legacy_table
START AT (STREAM => 'my_stream')
REFRESH USING (
    INSERT INTO SELF
    SELECT
        id,
        amount
    FROM src_table CHANGES(INFORMATION => APPEND_ONLY)
);

CREATE OR REPLACE DYNAMIC TABLE dt_custom_incremental_start_at_timestamp (
    id NUMBER
)
TARGET_LAG = '5 minutes'
WAREHOUSE = wh
REFRESH_MODE = CUSTOM_INCREMENTAL
START AT (TIMESTAMP => '2026-08-01 00:00:00'::TIMESTAMP_LTZ)
REFRESH USING (
    INSERT INTO SELF
    SELECT id FROM src_table CHANGES()
);

CREATE OR REPLACE DYNAMIC TABLE dt_custom_incremental_start_at_offset (
    id NUMBER
)
TARGET_LAG = '5 minutes'
WAREHOUSE = wh
REFRESH_MODE = CUSTOM_INCREMENTAL
START AT (OFFSET => -3600)
REFRESH USING (
    INSERT INTO SELF
    SELECT id FROM src_table CHANGES(INFORMATION => DEFAULT)
);
