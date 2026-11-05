SELECT CASE 'a' || 'b' WHEN 'ab' THEN 1 ELSE 0 END;

SELECT CASE 'a' || 'b' WHEN 'ab' THEN 'x' ELSE 'y' END || 'z';
