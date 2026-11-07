SET ROLE DEFAULT;
SET ROLE NONE;
SET ROLE ALL;

SET ROLE 'reader';
SET ROLE 'reader', 'writer';
SET ROLE 'reader'@'localhost';

SET ROLE ALL EXCEPT 'writer';
SET ROLE ALL EXCEPT 'reader'@'localhost', 'writer';
