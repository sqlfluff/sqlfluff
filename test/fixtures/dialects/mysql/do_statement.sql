DO 1;
DO SLEEP(1);
do release_lock('lock_name');
DO 1, 2, SLEEP(0);
DO @a := 1;
DO (SELECT 1);
DO(0);
DO(1), (2);
