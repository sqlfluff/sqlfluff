-- check deferrable in table constrain segment
CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) DEFERRABLE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) DEFERRABLE INITIALLY IMMEDIATE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) NOT DEFERRABLE
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) NOT DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE messages(
    msg_id TEXT,
    parent_id TEXT,
    FOREIGN KEY(parent_id) REFERENCES users(id) NOT DEFERRABLE INITIALLY IMMEDIATE
);

-- check deferrable in column constrain segment
CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) DEFERRABLE
);

CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) DEFERRABLE INITIALLY IMMEDIATE
);

CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) NOT DEFERRABLE
);

CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) NOT DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT, 
  trackartist INTEGER REFERENCES artist(artistid) NOT DEFERRABLE INITIALLY IMMEDIATE
);
