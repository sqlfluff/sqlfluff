alter user admin createdb;
alter user admin with createdb;

alter user admin nocreatedb;
alter user admin with nocreatedb;

alter user "dbuser" reset var;
alter user "dbuser" with reset var;

alter user admin createuser;
alter user admin with createuser;

alter user admin nocreateuser;
alter user admin with nocreateuser;

alter user admin syslog access restricted;
alter user admin with syslog access restricted;

alter user admin syslog access unrestricted;
alter user admin with syslog access unrestricted;

alter user iam_superuser password 'mdA51234567890123456780123456789012';
alter user iam_superuser with password 'mdA51234567890123456780123456789012';

alter user iam_superuser password DISABLE;
alter user iam_superuser with password DISABLE;

alter user admin password 'adminPass9' valid until '2017-12-31 23:59';
alter user admin with password 'adminPass9' valid until '2017-12-31 23:59';

alter user admin rename to sysadmin;
alter user admin with rename to sysadmin;

alter user admin connection limit 10;
alter user admin with connection limit 10;

alter user admin connection limit unlimited;
alter user admin with connection limit unlimited;

alter user dbuser session timeout 300;
alter user dbuser with session timeout 300;

alter user dbuser reset session timeout;
alter user dbuser with reset session timeout;

alter user dbuser set var to 100;
alter user dbuser with set var to 100;

alter user dbuser set var = 'hi';
alter user dbuser with set var = 'hi';

alter user dbuser set var to default;
alter user dbuser with set var to default;

alter user dbuser set var = default;
alter user dbuser with set var = default;

alter user dbuser reset var;
alter user dbuser with reset var;
