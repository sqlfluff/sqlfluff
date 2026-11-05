SELECT CASE 'a' || 'b' WHEN 'ab' THEN 'match' ELSE 'other' END;

SELECT CASE 'a' || CASE WHEN true THEN 'b' ELSE 'c' END
    WHEN 'ab' THEN 1 ELSE 0 END = 1;

SELECT CASE 'a' || 'b' || 'c'
    WHEN 'abc' THEN 'match' ELSE 'other' END || 'tail';

SELECT CASE ('a' || 'b') WHEN 'ab' THEN 1 ELSE 0 END;

SELECT CASE 1 + 2 WHEN 3 THEN 4 ELSE 0 END + 5;
