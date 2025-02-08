ALTER CORTEX SEARCH SERVICE mysvc SET WAREHOUSE = my_new_wh;
ALTER CORTEX SEARCH SERVICE mysvc SET COMMENT = 'new_comment';
ALTER CORTEX SEARCH SERVICE mysvc set target_lag = '1 hour';
ALTER CORTEX SEARCH SERVICE mysvc SUSPEND SERVING;
alter cortex search service mysvc resume indexing;
alter cortex search service if exists mysvc suspend indexing;
ALTER CORTEX SEARCH SERVICE mysvc SET WAREHOUSE = my_new_wh;
ALTER CORTEX SEARCH SERVICE mysvc SET COMMENT = 'new_comment' target_lag = '1 hour';
