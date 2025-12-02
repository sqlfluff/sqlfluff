SELECT
  word.*,
  paragraph.id AS paragraph_id
FROM word
INNER JOIN paragraph ON paragraph.page_id = word.page_id
WHERE
  word.character_range @> paragraph.character_range
  AND word.character_range <@ paragraph.character_range
  AND word.character_range && paragraph.character_range
  AND word.character_range << paragraph.character_range
  AND word.character_range >> paragraph.character_range
  AND word.character_range &> paragraph.character_range
  AND word.character_range &< paragraph.character_range
  AND word.character_range -|- paragraph.character_range
  AND word.character_range + paragraph.character_range
  AND word.character_range * paragraph.character_range
  AND word.character_range - paragraph.character_range
