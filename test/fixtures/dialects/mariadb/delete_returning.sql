DELETE FROM a WHERE a.foo = 'bar' RETURNING a.*;

DELETE FROM a WHERE a.foo = 'bar' RETURNING a.baz AS abaz;
