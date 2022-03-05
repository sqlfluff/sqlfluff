DELETE FROM films;

DELETE FROM ONLY films;

DELETE FROM films *;

DELETE FROM films AS f;

DELETE FROM films USING producers
  WHERE producer_id = producers.id AND producers.name = 'foo';

DELETE FROM films AS f USING producers AS p
  WHERE f.producer_id = p.id AND p.name = 'foo';

DELETE FROM films AS f USING producers AS p, actors AS a
  WHERE f.producer_id = p.id AND p.name = 'foo'
    AND f.actor_id = a.id AND a.name = 'joe cool';

DELETE FROM tasks WHERE CURRENT OF c_tasks;

DELETE FROM films WHERE kind <> 'Musical';

DELETE FROM tasks WHERE status = 'DONE' RETURNING *;

DELETE FROM tasks WHERE status = 'DONE' RETURNING actor_id;

DELETE FROM tasks WHERE status = 'DONE' RETURNING actor_id as a_id;

DELETE FROM tasks WHERE status = 'DONE' RETURNING actor_id, producer_id;

DELETE FROM tasks WHERE status = 'DONE' RETURNING actor_id as a_id, producer_id as p_id;

WITH test as (select foo from bar)
DELETE FROM films;
