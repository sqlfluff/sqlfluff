
CREATE TABLE emails (
    email CHAR(100) NOT NULL,
    email_domain CHAR(100) AS (SUBSTRING_INDEX(email, '@', -1)),
    email_domain2 CHAR(100) GENERATED ALWAYS AS (SUBSTRING_INDEX(email, '@', -1)) STORED,
    email_domain3 CHAR(100) GENERATED ALWAYS AS (SUBSTRING_INDEX(email, '@', -1)) VIRTUAL
);