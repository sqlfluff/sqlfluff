INSERT INTO foo (bar) VALUES(current_timestamp);

INSERT INTO foo (bar, baz) VALUES(1, 2), (3, 4);

INSERT INTO foo (bar, baz) VALUES(1 + 1, 2), (3, 4);

INSERT INTO foo (bar) VALUES(DEFAULT);

INSERT INTO distributors AS d (did, dname) VALUES (8, 'Anvil Distribution');

INSERT INTO test (id, col1) OVERRIDING SYSTEM VALUE VALUES (1, 'val');

INSERT INTO test (id, col1) OVERRIDING USER VALUE VALUES (1, 'val');

INSERT INTO foo (bar) DEFAULT VALUES;

INSERT INTO films SELECT * FROM tmp_films WHERE date_prod < '2004-05-07';

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING *;

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING bar;

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING bar AS some_alias;

INSERT INTO foo (bar, baz) VALUES(1, 2)
RETURNING bar, baz;

INSERT INTO foo (bar, baz) VALUES(1, 2)
RETURNING bar AS alias1, baz AS alias2;

INSERT INTO foo (bar, baz) VALUES (1, 'var')
ON CONFLICT (bar) DO UPDATE SET baz = EXCLUDED.baz;

INSERT INTO foo (bar, baz) VALUES (1, 'var')
ON CONFLICT (bar) DO NOTHING;

INSERT INTO foo AS f (bar, baz) VALUES (1, 'var')
ON CONFLICT (bar) DO UPDATE SET baz = EXCLUDED.baz || ' (formerly ' || f.baz || ')'
WHERE f.zipcode != '21201';

INSERT INTO foo (bar, baz) VALUES (1, 'var')
ON CONFLICT ON CONSTRAINT foo_pkey DO NOTHING;

INSERT INTO foo (bar, baz) VALUES (1, 'var')
ON CONFLICT (bar) WHERE is_active DO NOTHING;

INSERT INTO foo (bar, baz) VALUES (1, 'var')
ON CONFLICT (bar) DO UPDATE SET (baz) = (SELECT baz FROM foobar WHERE bar = 1);

INSERT INTO megatable (megacolumn)
SELECT * FROM (
    VALUES ( 'megavalue' )
) AS tmp (megacolumn)
WHERE NOT EXISTS (
SELECT FROM megatable AS mt
    WHERE mt.megacolumn = tmp.megacolumn
)
ON CONFLICT DO NOTHING;

INSERT INTO abc (foo, bar)
SELECT foo, bar FROM baz
RETURNING quux
;
