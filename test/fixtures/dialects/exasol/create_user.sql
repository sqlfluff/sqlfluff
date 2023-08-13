CREATE USER user_1 IDENTIFIED BY "h12_xhz";
CREATE USER user_2 IDENTIFIED AT LDAP
AS 'cn=user_2,dc=authorization,dc=exasol,dc=com';
CREATE USER user_3 IDENTIFIED BY KERBEROS PRINCIPAL '<user>@<realm>';
CREATE USER oidctestuser IDENTIFIED BY OPENID SUBJECT 'database-user@exasol.example';
