SELECT
    systems,
    planets,
    cities,
    cantinas,
    SUM(scum + villainy) as total_scum_and_villainy
FROM star_wars_locations
GROUP BY ALL
;

SELECT
    * EXCLUDE (cantinas, booths, scum, villainy),
    SUM(scum + villainy) as total_scum_and_villainy
FROM star_wars_locations
GROUP BY ALL
;

SELECT
    age,
    sum(civility) as total_civility
FROM star_wars_universe
GROUP BY ALL
ORDER BY ALL
;

SELECT
    x_wing,
    proton_torpedoes,
    --targeting_computer
FROM luke_whats_wrong
GROUP BY
    x_wing,
    proton_torpedoes,
;
