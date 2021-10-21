SELECT a.key, a.val
FROM a LEFT SEMI JOIN b ON (a.key = b.key)
