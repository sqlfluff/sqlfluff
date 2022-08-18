CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) DEFERRABLE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) DEFERRABLE INITIALLY IMMEDIATE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) NOT DEFERRABLE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) NOT DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent) REFERENCES users(id) NOT DEFERRABLE INITIALLY IMMEDIATE
);
