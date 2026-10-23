SELECT percentile_approx(prior.x, 0.5) AS p
FROM t AS prior
INNER JOIN u AS curr ON prior.id = curr.id;
