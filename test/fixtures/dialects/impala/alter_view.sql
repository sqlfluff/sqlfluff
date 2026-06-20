ALTER VIEW db.my_view AS SELECT col1 FROM db.src;

ALTER VIEW db.my_view RENAME TO db.new_view;

ALTER VIEW db.my_view SET OWNER USER view_owner;
