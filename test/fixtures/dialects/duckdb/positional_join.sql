-- treat two data frames as a single table
SELECT
    df1.*,
    df2.*
FROM df1 POSITIONAL JOIN df2;
