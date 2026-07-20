DELETE FROM db.t1 WHERE id = 1;

DELETE t1 FROM db.t1 t1 JOIN db.t2 t2 ON t1.id = t2.id WHERE t2.active = true;
