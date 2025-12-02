CREATE TABLE users (
	user_id INTEGER PRIMARY KEY ON CONFLICT ROLLBACK,
	user_name TEXT NOT NULL ON CONFLICT ABORT
);

ALTER TABLE users ADD COLUMN name TEXT UNIQUE ON CONFLICT FAIL;

create table imap_boxes (
    account_id integer not null,
    box_name text not null,
    unique (account_id, box_name) on conflict replace
);
