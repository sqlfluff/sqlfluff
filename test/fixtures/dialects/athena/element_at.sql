SELECT
    COALESCE(
        element_at(rq.hiring_managers, 1),
        element_at(rq.hiring_managers, 2),
        rq.creator_id
    ) AS part1,
    element_at(pl.hiring_managers, 1).id AS part2,
    element_at(pl.hiring_managers, 2).id AS part3;
