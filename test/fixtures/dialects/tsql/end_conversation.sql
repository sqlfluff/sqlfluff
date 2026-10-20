END CONVERSATION @dialog_handle;

END CONVERSATION '6f9619ff-8b86-d011-b42d-00c04fc964ff' WITH CLEANUP;

END CONVERSATION N'6f9619ff-8b86-d011-b42d-00c04fc964ff' WITH CLEANUP;

END CONVERSATION @dialog_handle
    WITH ERROR = 1234 DESCRIPTION = 'The submitted data is not valid.';

END CONVERSATION @dialog_handle
    WITH ERROR = @ErrorSave DESCRIPTION = N'An error has occurred.';

END CONVERSATION @dialog_handle
    WITH ERROR = @ErrorSave DESCRIPTION = @ErrorDesc;

END CONVERSATION @dialog_handle
SELECT 1 AS result;

CREATE PROCEDURE dbo.CloseDialog
AS
BEGIN
    END CONVERSATION @dialog_handle WITH CLEANUP;
    SELECT 1 AS result;
END;
GO

IF @ErrorSave <> 0
BEGIN
    END CONVERSATION @dialog_handle
        WITH ERROR = @ErrorSave DESCRIPTION = @ErrorDesc;
END;
