-- `stream` is not reserved: a bare table named `stream` is not a streaming
-- read, and the STREAM keyword is only a prefix when a table follows it.
SELECT * FROM stream;

SELECT * FROM stream AS s;

-- STREAM marks a streaming read of a table or a table function.
SELECT * FROM STREAM source;

SELECT * FROM STREAM read_files('/path');
