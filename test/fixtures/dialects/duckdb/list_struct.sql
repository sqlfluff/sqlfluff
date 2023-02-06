SELECT
    ['A-Wing', 'B-Wing', 'X-Wing', 'Y-Wing'] as starfighter_list,
    {name: 'Star Destroyer', common_misconceptions: 'Can''t in fact destroy a star'} as star_destroyer_facts
;

SELECT
    starfighter_list[2:2] as dont_forget_the_b_wing
FROM (SELECT ['A-Wing', 'B-Wing', 'X-Wing', 'Y-Wing'] as starfighter_list);

SELECT 'I love you! I know'[:-3] as nearly_soloed;

SELECT
    planet.name,
    planet."Amount of sand"
FROM (SELECT {name: 'Tatooine', 'Amount of sand': 'High'} as planet)
;

