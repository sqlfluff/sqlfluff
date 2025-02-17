SELECT column1, column2
FROM OPENQUERY ([testlinkedserver], 'select * from table_name');

UPDATE OPENQUERY (OracleSvr, 'SELECT name FROM joe.titles WHERE id = 101')
SET name = 'ADifferentName';

INSERT OPENQUERY (OracleSvr, 'SELECT name FROM joe.titles')
VALUES ('NewTitle');

DELETE OPENQUERY (OracleSvr, 'SELECT name FROM joe.titles WHERE name = ''NewTitle''');
