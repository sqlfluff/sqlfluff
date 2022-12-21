SELECT @@global.time_zone;
SELECT @@session.time_zone;
SELECT @@global.version;
SELECT @@session.rand_seed1;
SELECT CONVERT_TZ(NOW(), @@global.time_zone, '+00:00')
