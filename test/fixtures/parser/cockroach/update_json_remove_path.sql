UPDATE t1 SET a = json_remove_path(a, '{nata,pastryLimits,0,pastryName}'::string[]) WHERE a -> 'nata' -> 'pastryLimits' -> 0 ->> 'pastryName' NOT IN ('PUFF', 'ROLL');
