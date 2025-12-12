SELECT json_serialize('"test"'::json RETURNING bytea);
SELECT json_serialize('"test"'::json RETURNING text);
SELECT json_serialize('"test"'::json);
SELECT json_serialize('{"key": "value"}'::json RETURNING bytea);
SELECT json_serialize('{"key": "value"}'::json RETURNING text);
SELECT json_serialize('{"key": "value"}'::json);