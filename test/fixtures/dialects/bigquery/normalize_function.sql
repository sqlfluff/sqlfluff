SELECT
    col1,
    NORMALIZE('\u00ea', NFD) AS a,
    NORMALIZE('\u0065\u0302', NFD) AS b,
    NORMALIZE_AND_CASEFOLD('\u00ea', NFD) AS c,
    NORMALIZE_AND_CASEFOLD('\u0065\u0302', NFD) AS d;

SELECT a, b, a = b as normalized
FROM (SELECT NORMALIZE('\u00ea') as a, NORMALIZE('\u0065\u0302') as b);

WITH EquivalentNames AS (
  SELECT name
  FROM UNNEST([
      'Jane\u2004Doe',
      'John\u2004Smith',
      'Jane\u2005Doe',
      'Jane\u2006Doe',
      'John Smith']) AS name
)
SELECT
  NORMALIZE(name, NFKC) AS normalized_name,
  COUNT(*) AS name_count
FROM EquivalentNames
GROUP BY 1;

SELECT
  a, b,
  NORMALIZE(a) = NORMALIZE(b) as normalized,
  NORMALIZE_AND_CASEFOLD(a) = NORMALIZE_AND_CASEFOLD(b) as normalized_with_case_folding
FROM (SELECT 'The red barn' AS a, 'The Red Barn' AS b);

SELECT a, b,
  NORMALIZE_AND_CASEFOLD(a, NFD)=NORMALIZE_AND_CASEFOLD(b, NFD) AS nfd,
  NORMALIZE_AND_CASEFOLD(a, NFC)=NORMALIZE_AND_CASEFOLD(b, NFC) AS nfc,
  NORMALIZE_AND_CASEFOLD(a, NFKD)=NORMALIZE_AND_CASEFOLD(b, NFKD) AS nkfd,
  NORMALIZE_AND_CASEFOLD(a, NFKC)=NORMALIZE_AND_CASEFOLD(b, NFKC) AS nkfc
