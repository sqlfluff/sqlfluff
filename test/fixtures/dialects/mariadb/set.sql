SET max_error_count=128;
SET skip_parallel_replication=ON;
SET GLOBAL max_error_count=256;
SET GLOBAL innodb_sync_spin_loops=120;
SET some_bool_param = ON;
SET some_bool_param = OFF;
SET some_bool_param = TRUE;
SET some_bool_param = FALSE;
SET some_bool_param = 0;
SET some_bool_param = 1;
SET a = 1, b = 2;
SET @abc = 1 + 2;
SET @abc = (SELECT 1);
SET @id = (SELECT id FROM table1 WHERE field = TRUE LIMIT 1);
SET @abc = 1;
SET @my_var = 1;
SET @my$currency = 1;
SET @sha256enabled = 1;
SET sql_log_bin = ON;
SET sql_log_bin = OFF;
