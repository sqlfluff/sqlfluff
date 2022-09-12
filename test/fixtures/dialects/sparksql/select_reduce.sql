SELECT reduce(array(1, 2, 3), 0, (acc, x) -> acc + x); -- 6
SELECT reduce(array(1, 2, 3), 0, (acc, x) -> acc + x, acc -> acc * 10); -- 60
SELECT reduce(array(1, 2, 3, 4), -- 2.5
              named_struct('sum', 0, 'cnt', 0),
              (acc, x) -> named_struct('sum', acc.sum + x, 'cnt', acc.cnt + 1),
              acc -> acc.sum / acc.cnt) AS avg;
