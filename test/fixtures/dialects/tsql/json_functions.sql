SELECT JSON_OBJECT(ABSENT ON NULL);

SELECT JSON_ARRAY('a', 1, 'b', 2);

SELECT JSON_ARRAY('a', 1, NULL, 2, NULL ON NULL);

SELECT JSON_OBJECT('name':'value', 'new':1);

SELECT JSON_OBJECT('name':'value', 'type':NULL ABSENT ON NULL)

SELECT JSON_OBJECT('name':'value', 'type':JSON_ARRAY(1, 2))

SELECT JSON_OBJECT('name':'value', 'type':JSON_OBJECT('type_id':1, 'name':'a'))

DECLARE @id_key nvarchar(10) = N'id', @id_value nvarchar(64) = NEWID();
SELECT JSON_OBJECT('user_name':USER_NAME(), @id_key:@id_value, 'sid':(SELECT @@SPID));

SELECT s.session_id, JSON_OBJECT('security_id':s.security_id, 'login':s.login_name, 'status':s.status) AS info
FROM sys.dm_exec_sessions AS s
WHERE s.is_user_process = 1;

SELECT JSON_ARRAY('a', JSON_OBJECT('name':'value', 'type':1));

SELECT JSON_ARRAY('a', JSON_OBJECT('name':'value', 'type':1), JSON_ARRAY(1, NULL, 2 NULL ON NULL));

DECLARE @id_value nvarchar(64) = NEWID();
SELECT JSON_ARRAY(1, @id_value, (SELECT @@SPID));

SELECT s.session_id, JSON_ARRAY(s.host_name, s.program_name, s.client_interface_name)
FROM sys.dm_exec_sessions AS s
WHERE s.is_user_process = 1;
