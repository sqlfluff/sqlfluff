SELECT * EXCLUDE (jar_jar_binks, midichlorians) FROM star_wars;

SELECT
    sw.* EXCLUDE (jar_jar_binks, midichlorians),
    ff.* EXCLUDE cancellation
FROM star_wars sw, firefly ff
;

SELECT * FROM star_wars;
