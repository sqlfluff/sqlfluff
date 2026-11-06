CREATE TABLE child (
    id INT,
    parent_id INT REFERENCES parent(id) MATCH SIMPLE
);

CREATE TABLE child_partial (
    id INT,
    parent_id INT REFERENCES parent(id) MATCH PARTIAL
);

CREATE TABLE child_full (
    id INT,
    parent_id INT REFERENCES parent(id) MATCH FULL
);

CREATE TABLE child_table_constraint (
    id INT,
    parent_id INT,
    FOREIGN KEY(parent_id) REFERENCES parent(id) MATCH SIMPLE ON DELETE CASCADE
);
