-- Test PostgreSQL function expansion syntax
SELECT (JSONB_EACH_TEXT(data)).* FROM table1;
SELECT (JSONB_EACH_TEXT(w.inventory_events)).* FROM public.widget AS w;
SELECT (JSON_EACH(config)).* FROM settings;
SELECT (JSONB_EACH(items)).* FROM inventory;
SELECT
    id,
    (JSONB_EACH_TEXT(data)).*,
    (JSON_EACH(metadata)).*
FROM table1;
SELECT (JSONB_EACH_TEXT(COALESCE(data, '{}'::jsonb))).* FROM table1;
