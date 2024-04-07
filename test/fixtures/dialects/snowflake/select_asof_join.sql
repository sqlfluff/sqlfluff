SELECT t.stock_symbol, t.trade_time, t.quantity, q.quote_time, q.price
  FROM trades t ASOF JOIN quotes q
    MATCH_CONDITION(t.trade_time >= quote_time)
    ON t.stock_symbol=q.stock_symbol
  ORDER BY t.stock_symbol;

SELECT t.stock_symbol, c.company_name, t.trade_time, t.quantity, q.quote_time, q.price
  FROM trades t ASOF JOIN quotes q
    MATCH_CONDITION(t.trade_time >= quote_time)
    ON t.stock_symbol=q.stock_symbol
    INNER JOIN companies c ON c.stock_symbol=t.stock_symbol
  ORDER BY t.stock_symbol;

SELECT *
  FROM trades_unixtime tu
    ASOF JOIN quotes_unixtime qu
    MATCH_CONDITION(tu.trade_time>=qu.quote_time);

SELECT * FROM preciptime p ASOF JOIN snowtime s MATCH_CONDITION(p.observed>=s.observed);

SELECT *
  FROM snowtime s
    ASOF JOIN raintime r
      MATCH_CONDITION(s.observed>=r.observed)
      ON s.state=r.state
    ASOF JOIN preciptime p
      MATCH_CONDITION(s.observed>=p.observed)
      ON s.state=p.state
  ORDER BY s.observed;

SELECT *
  FROM snowtime s
    ASOF JOIN raintime r
      MATCH_CONDITION(s.observed>r.observed)
      ON s.state=r.state
    ASOF JOIN preciptime p
      MATCH_CONDITION(s.observed<p.observed)
      ON s.state=p.state
    ORDER BY s.observed;
