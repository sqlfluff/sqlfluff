RENAME TABLE my_db.my_table TO my_db.my_new_table;

RENAME DATABASE my_db TO other_db;

RENAME DATABASE my_db TO other_db, my_db2 TO other_pg;

RENAME DICTIONARY dict_A TO dict_B;

RENAME DICTIONARY dict_A TO dict_B, dict_A TO dict_B;

RENAME DICTIONARY db0.dict_A TO db1.dict_B;

RENAME TABLE my_db.my_table TO my_db.my_new_table, my_table2 TO my_new_table2 ON CLUSTER toto;
