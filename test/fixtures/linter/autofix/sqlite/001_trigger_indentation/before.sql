CREATE TRIGGER trig
AFTER UPDATE ON tab1
WHEN
old.a IS NOT new.a
OR old.b IS NOT new.b
  OR old.c IS NOT new.c
BEGIN
INSERT INTO tab2 (x) VALUES ('UPDATE');
END;
