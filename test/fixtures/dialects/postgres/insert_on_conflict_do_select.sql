-- PostgreSQL 19: ON CONFLICT ... DO SELECT
INSERT INTO distributors (did, dname) VALUES (11, 'Global Electronics')
    ON CONFLICT (did) DO SELECT
    RETURNING *;

INSERT INTO distributors AS d (did, dname) VALUES (12, 'Micro Devices Inc')
    ON CONFLICT (did) DO SELECT WHERE d.dname != EXCLUDED.dname
    RETURNING *;

INSERT INTO distributors (did, dname) VALUES (13, 'Advanced Systems')
    ON CONFLICT (did) DO SELECT FOR UPDATE
    RETURNING *;

INSERT INTO distributors (did, dname) VALUES (14, 'Example Parts')
    ON CONFLICT (did) DO SELECT FOR NO KEY UPDATE
    RETURNING did;

INSERT INTO distributors (did, dname) VALUES (15, 'Sample Supply')
    ON CONFLICT (did) DO SELECT FOR SHARE
    RETURNING did;

INSERT INTO distributors AS d (did, dname) VALUES (16, 'Test Traders')
    ON CONFLICT ON CONSTRAINT distributors_pkey DO SELECT FOR KEY SHARE WHERE d.active
    RETURNING d.did, d.dname;
