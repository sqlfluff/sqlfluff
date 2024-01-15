SELECT
    t.*,
    p.price
FROM trades AS t ASOF JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;

SELECT *
FROM trades AS t ASOF LEFT JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;

SELECT *
FROM trades AS t ASOF RIGHT JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;

SELECT *
FROM trades AS t ASOF FULL OUTER JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;

SELECT *
FROM trades AS t ASOF ANTI JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;

SELECT *
FROM trades AS t ASOF SEMI JOIN prices AS p
    ON t.symbol = p.symbol AND t.when >= p.when;


-- ASOF joins can also specify join conditions on matching column names with
-- the USING syntax, but the last attribute in the list must be the inequality,
-- which will be greater than or equal to (>=):
SELECT *
FROM trades ASOF JOIN prices USING (symbol, "when");
-- Returns symbol, trades.when, price (but NOT prices.when)

SELECT
    t.symbol,
    t.when AS trade_when,
    p.when AS price_when,
    price
FROM trades AS t ASOF LEFT JOIN prices AS p USING (symbol, "when");
