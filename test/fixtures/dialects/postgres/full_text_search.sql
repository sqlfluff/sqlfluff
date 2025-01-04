SELECT 'a fat cat sat on a mat and ate a fat rat'::tsvector @@ 'cat & rat'::tsquery;

SELECT 'fat & cow'::tsquery @@ 'a fat cat sat on a mat and ate a fat rat'::tsvector;

SELECT to_tsvector('fat cats ate fat rats') @@ to_tsquery('fat & rat');

SELECT 'fat cats ate fat rats'::tsvector @@ to_tsquery('fat & rat');

SELECT 'fat cats ate fat rats'::tsvector @@ to_tsquery('fat & rat');

SELECT to_tsvector('error is not fatal') @@ to_tsquery('fatal <-> error');

SELECT phraseto_tsquery('cats ate rats');

SELECT phraseto_tsquery('the cats ate the rats');

SELECT 'a:1 b:2'::tsvector || 'c:1 d:2 b:3'::tsvector;

SELECT 'fat | rat'::tsquery && 'cat'::tsquery;

SELECT 'fat | rat'::tsquery || 'cat'::tsquery;

SELECT to_tsquery('fat') <-> to_tsquery('rat');

SELECT 'cat'::tsquery @> 'cat & rat'::tsquery;

SELECT 'cat'::tsquery <@ 'cat & rat'::tsquery;

SELECT 'cat'::tsquery <@ '!cat & rat'::tsquery;

SELECT !! 'cat'::tsquery;
