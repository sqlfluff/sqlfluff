-- RESTORE with optional TABLE/TO and an arithmetic timestamp.
RESTORE TABLE employee TO VERSION AS OF 1;

RESTORE employee TO VERSION AS OF 1;

RESTORE TABLE employee VERSION AS OF 1;

RESTORE TABLE employee TO TIMESTAMP AS OF current_timestamp() - INTERVAL '1' HOUR;
