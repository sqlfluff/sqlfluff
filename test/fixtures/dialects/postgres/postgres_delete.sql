DELETE FROM films WHERE kind <> 'Musical';

DELETE FROM films;

DELETE FROM tasks WHERE status = 'DONE' RETURNING *;

DELETE FROM tasks WHERE CURRENT OF c_tasks;

DELETE FROM some_table
USING other_table
WHERE other_table.col = some_table.col

