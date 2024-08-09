/* Checks for functions that use `FROM` */

SELECT extract('year' FROM DATE '1992-09-20');

SELECT extract('year' FROM '1992-09-20'::DATE);

VALUES (extract('year' FROM DATE '1992-09-20'));

SELECT extract('hour' FROM TIMESTAMP '1992-09-20 20:38:48');

SELECT extract('hour' FROM TIMESTAMPTZ '1992-09-20 20:38:48');

SELECT extract('hour' FROM TIME '14:21:13');
