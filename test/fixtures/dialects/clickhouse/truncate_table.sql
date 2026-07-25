TRUNCATE TABLE IF EXISTS default.users;
TRUNCATE TABLE default.users ON CLUSTER clstr;
TRUNCATE TABLE default.users SYNC;
TRUNCATE default.users ASYNC;
