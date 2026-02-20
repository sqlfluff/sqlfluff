SELECT 'metadata' AS key from foo;

-- Test Hexadecimal Integer Literal
SELECT 0x01 AS hex1;
SELECT 0xFF AS hex2;
SELECT 0xDEADBEEF AS hex3;
SELECT CASE WHEN TRUE THEN 0x01 ELSE 0x00 END;
SELECT 0x01 | 0x02 AS bitwise_or;

SELECT *
from l.vss as _stage
where _stage.valid_from <> _stage.valid_to
qualify max(_stage.valid_to) over w = _stage.valid_to
window w as (partition by _stage._id, _stage.os_id order by _stage._id)
order by _id asc, valid_from asc
;
