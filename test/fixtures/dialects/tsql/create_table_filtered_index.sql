-- Test inline filtered index in CREATE TABLE
CREATE TABLE T (
    C int,

    INDEX UX_T_C UNIQUE (C) where (C = 1)
)

-- Test inline filtered index with INCLUDE
CREATE TABLE T2 (
    C int,
    D int,

    INDEX IX_T2 UNIQUE NONCLUSTERED (C) INCLUDE (D) WHERE (C > 0)
)

-- Test inline index without filter (existing functionality)
CREATE TABLE T3 (
    C int,

    INDEX IX_T3 UNIQUE CLUSTERED (C)
)
