BEGIN TRY
    -- Table does not exist; object name resolution
    -- error not caught.
    SELECT * FROM NonexistentTable;
END TRY
BEGIN CATCH
    SELECT
        ERROR_NUMBER() AS ErrorNumber
       ,ERROR_MESSAGE() AS ErrorMessage;

    THROW
END CATCH
GO

THROW 50005, N'an error occurred', 1;

BEGIN TRY
    EXEC spSomeProc
END TRY
BEGIN CATCH
END CATCH;
