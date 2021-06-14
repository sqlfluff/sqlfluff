UPDATE t1
SET a = jsonb_set(a, '{inbound,rules}'::text[], t2.c)
FROM (
         SELECT t3.c, jsonb_agg(t3.b) as updated_laws
         FROM (
                  SELECT p.b,
                         jsonb_set(rule, '{key}'::text[], concat('"', gen_random_uuid()::text, '"')::jsonb) AS c
                  FROM t1 p,
                       lateral jsonb_array_elements(p.massaction_rules -> 'hidebound' -> 'laws') AS law
                  WHERE p.massaction_laws -> 'hidebound' ->> 'laws' IS NOT NULL
              ) t3
         GROUP BY t3.c
     ) t2
WHERE t1.b = t2.a;
