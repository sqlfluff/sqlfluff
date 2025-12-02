SELECT
    * REPLACE (movie_count+3 as movie_count, show_count*1000 as show_count)
FROM star_wars_owned_by_disney
;
