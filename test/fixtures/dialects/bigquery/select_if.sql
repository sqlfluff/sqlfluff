SELECT
  client, firstHtml, vary,
  IF(_cdn_provider != '', 'CDN', 'Origin') AS source,
  COUNT(0) AS total
FROM
  `httparchive.almanac.requests`,
  UNNEST(split(REGEXP_REPLACE(REGEXP_REPLACE(LOWER(resp_vary), '\"', ''), '[, ]+|\\\\0', ','), ',')) AS vary
WHERE
  date = '2019-07-01'
GROUP BY
  client, firstHtml, vary, source
HAVING
  vary != '' AND vary IS NOT NULL
ORDER BY
  client DESC,
  firstHtml DESC,
  total DESC
