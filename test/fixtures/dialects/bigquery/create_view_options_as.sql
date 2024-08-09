CREATE OR REPLACE VIEW foo
AS (SELECT * from bar);

CREATE OR REPLACE VIEW foo
OPTIONS (description = 'copy of bar')
AS (SELECT * from bar);

CREATE OR REPLACE VIEW IF NOT EXISTS foo
OPTIONS (description = 'copy of bar')
AS (SELECT * from bar);

CREATE OR REPLACE VIEW foo
(
  x OPTIONS (description = 'x'),
  y OPTIONS (description = 'y')
)
OPTIONS (description = 'view_column_name_list')
AS (SELECT x, y from bar);
