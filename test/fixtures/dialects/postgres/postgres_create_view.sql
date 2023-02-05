CREATE VIEW vista AS SELECT 'Hello World';

CREATE OR REPLACE VIEW vista AS SELECT 'Hello World';

CREATE VIEW vista AS SELECT text 'Hello World' AS hello;

CREATE TEMP VIEW vista AS SELECT text 'Hello World' AS hello;

CREATE TEMPORARY VIEW  vista AS SELECT text 'Hello World' AS hello;

CREATE VIEW comedies AS
    SELECT *
    FROM films
    WHERE kind = 'Comedy';

CREATE VIEW pg_comedies AS
    VALUES (1, 'one'), (2, 'two'), (3, 'three')
    WITH LOCAL CHECK OPTION;

CREATE VIEW pg_comedies AS
    SELECT *
    FROM comedies
    WHERE classification = 'PG' 
    WITH CASCADED CHECK OPTION;
create view foo with (security_invoker) as select 1;
create view foo with (security_barrier) as select 1;

create view foo with (security_invoker=BOOLEAN) as select 1;
create view foo with (security_barrier=BOOLEAN) as select 1;

create view foo with (check_option=local) as select * from OTHER_VIEW;
create view foo with (check_option=cascaded) as select * from OTHER_VIEW;

create view foo as select * from OTHER_VIEW with local check option;
create view foo as select * from OTHER_VIEW with cascaded check option;
