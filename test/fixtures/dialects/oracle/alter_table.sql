-- AlterTableColumnClausesSegment
ALTER TABLE table_name RENAME COLUMN old_column_name TO new_column_name;

-- AlterTableConstraintClauses
ALTER TABLE table_name
ADD CONSTRAINT constraint_name
FOREIGN KEY (column_name) REFERENCES other_table_name (other_column_name);
