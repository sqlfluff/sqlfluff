-- Create and populate the target table.
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (user_id)
APPLY AS DELETE WHEN operation = "DELETE"
APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
SEQUENCE BY sequence_num
COLUMNS * EXCEPT (operation, sequence_num)
STORED AS SCD TYPE 1;

-- Create and populate the target table.
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (userid)
APPLY AS DELETE WHEN operation = "DELETE"
SEQUENCE BY sequencenum
COLUMNS * EXCEPT (operation, sequencenum)
STORED AS SCD TYPE 2;

-- Create and populate the target table.
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (userid)
SEQUENCE BY sequencenum
COLUMNS * EXCEPT (operation, sequencenum);

-- Create and populate the target table.
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (user_id)
IGNORE NULL UPDATES
WHERE state = "NY"
APPLY AS DELETE WHEN operation = "DELETE"
APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
SEQUENCE BY sequence_num
COLUMNS * EXCEPT (operation, sequence_num)
STORED AS SCD TYPE 1;

-- Create and populate the target table.
-- "APPLY CHANGES INTO" without a "COLUMNS" clause
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (user_id)
SEQUENCE BY sequence_num;

-- Create and populate the target table.
-- "APPLY CHANGES INTO" with a "TRACK HISTORY" clause
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (user_id)
IGNORE NULL UPDATES
WHERE state = "NY"
APPLY AS DELETE WHEN operation = "DELETE"
APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
SEQUENCE BY sequence_num
COLUMNS * EXCEPT (operation, sequence_num)
STORED AS SCD TYPE 1
TRACK HISTORY ON user_id;

-- Create and populate the target table.
-- "APPLY CHANGES INTO" with a "TRACK HISTORY ON * EXCEPT" clause
CREATE OR REFRESH STREAMING LIVE TABLE target;

APPLY CHANGES INTO live.target
FROM STREAM(cdc_data.users)
KEYS (user_id)
IGNORE NULL UPDATES
WHERE state = "NY"
APPLY AS DELETE WHEN operation = "DELETE"
APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
SEQUENCE BY sequence_num
COLUMNS * EXCEPT (operation, sequence_num)
STORED AS SCD TYPE 1
TRACK HISTORY ON * EXCEPT (state);
