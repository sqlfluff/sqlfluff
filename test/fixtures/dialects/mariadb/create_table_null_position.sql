CREATE TABLE IF NOT EXISTS db_name.table_name
(
    updated_at1   timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    updated_at2   timestamp not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    updated_at3   timestamp default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null,
    updated_at4   timestamp
);
