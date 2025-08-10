-- PostgreSQL pg_trgm similarity operators
-- https://www.postgresql.org/docs/current/pgtrgm.html

-- text % text → boolean (similarity)
SELECT 'abc' % 'abd';

-- text <% text → boolean (word_similarity)
SELECT 'word' <% 'some word here';

-- text %> text → boolean (word_similarity reverse)
SELECT 'some word here' %> 'word';

-- text <<% text → boolean (strict_word_similarity)
SELECT 'text' <<% 'some text example';

-- text %>> text → boolean (strict_word_similarity reverse)
SELECT 'some text example' %>> 'text';

-- text <-> text → real (similarity distance)
SELECT 'str1' <-> 'str2';

-- text <<-> text → real (word_similarity distance)
SELECT 'item' <<-> 'some item value';

-- text <->> text → real (word_similarity distance reverse)
SELECT 'some item value' <->> 'item';

-- text <<<-> text → real (strict_word_similarity distance)
SELECT 'name' <<<-> 'some name field';

-- text <->>> text → real (strict_word_similarity distance reverse)
SELECT 'some name field' <->>> 'name';
