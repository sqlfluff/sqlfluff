SELECT json_value(raw_data, '$."action_type"' RETURNING smallint);
SELECT json_value(raw_data, '$."name"' RETURNING text);
SELECT json_value(raw_data, '$."price"' RETURNING numeric);
SELECT json_value(raw_data, '$."active"' RETURNING boolean);
SELECT json_value(raw_data, '$."timestamp"' RETURNING timestamp);
SELECT json_value(raw_data, '$."id"');