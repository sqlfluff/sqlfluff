-- Test T-SQL keyword behavior as identifiers
-- In T-SQL, only RESERVED keywords require quoting as identifiers
-- UNRESERVED keywords and FUTURE_RESERVED keywords can be used as naked identifiers

-- 1. UNRESERVED KEYWORDS - Can be used as naked identifiers
SELECT
    Type,
    Value,
    Name,
    Date,
    Time,
    Format,
    Level,
    Path,
    Data,
    Server,
    Action,
    Cache,
    Edge,
    Hash,
    Filter,
    Profile
FROM TestTable;

-- 2. FUTURE RESERVED KEYWORDS - Can also be used as naked identifiers
-- These include: ALIAS, ARRAY, CLASS, DESTROY, END-EXEC, EVERY, LIKE_REGEX
SELECT
    Class,
    Array,
    Alias
FROM GameData;

-- 3. RESERVED KEYWORDS - Must be quoted or bracketed
SELECT
    [SELECT],     -- reserved, needs brackets
    [FROM],       -- reserved, needs brackets
    [WHERE],      -- reserved, needs brackets
    [ORDER],      -- reserved, needs brackets
    Name          -- not reserved, no brackets needed
FROM TestTable2;

-- 4. Mixed usage in CREATE TABLE
CREATE TABLE MyTable (
    -- Unreserved keywords - no quotes needed
    Type INT,
    Value VARCHAR(50),
    Format VARCHAR(20),

    -- Future reserved keywords - no quotes needed
    Class VARCHAR(50),
    Array VARCHAR(100),

    -- Reserved keywords - quotes/brackets required
    [SELECT] INT,
    [UPDATE] VARCHAR(50),

    -- Regular identifiers
    Name VARCHAR(100)
);

-- 5. Column references in various contexts
UPDATE MyTable
SET Type = 1, Value = 'test', Class = 'warrior'
WHERE Format = 'json';

INSERT INTO MyTable (Type, Value, Class, Name)
VALUES (1, 'test', 'wizard', 'player1');

SELECT Type, Value, Class
FROM MyTable
WHERE Type IN (1, 2, 3)
ORDER BY Class, Value;

-- 6. Aliases using unreserved keywords
SELECT
    t1.Type AS Type,
    t1.Value AS Value,
    t2.Class AS Class
FROM MyTable t1
JOIN GameData t2 ON t1.Name = t2.Name;

-- Example from user's issue
SELECT
  Nation, Race, Class, HairColor,
  Hp, Mp, Sp, Strong, Sta, Dex, Intel, Cha, Authority, Points, Gold, Bind, PX, PZ, PY, dwTime, strSkill, strItem,strSerial
FROM USERDATA;

-- More examples with various unreserved keywords as identifiers
SELECT
    Type, Value, Name, Date, Time, Path, Data, Format, Level, Server
FROM TestTable;

-- Unreserved keywords in WHERE clause
SELECT * FROM TestTable WHERE Type = 'test' AND Value > 10;

-- Unreserved keywords in JOIN
SELECT t1.Type, t2.Value
FROM Table1 t1
JOIN Table2 t2 ON t1.Name = t2.Name;

-- CREATE TABLE with unreserved keyword column names
CREATE TABLE MyTable (
    Type INT,
    Value VARCHAR(50),
    Name VARCHAR(100),
    Data VARBINARY(MAX),
    Format VARCHAR(20)
);

-- INSERT with unreserved keyword column names
INSERT INTO MyTable (Type, Value, Name, Data, Format)
VALUES (1, 'test', 'example', 0x123456, 'json');

-- UPDATE with unreserved keyword column names
UPDATE MyTable
SET Value = 'updated', Format = 'xml'
WHERE Type = 1;
