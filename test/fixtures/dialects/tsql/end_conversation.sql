END CONVERSATION @dialog_handle;
END CONVERSATION @dialog_handle WITH CLEANUP;
END CONVERSATION @dialog_handle
    WITH ERROR = 1234 DESCRIPTION = 'The submitted data is not valid.';

END CONVERSATION @dialog_handle
END CONVERSATION @dialog_handle WITH CLEANUP
END CONVERSATION @dialog_handle
    WITH ERROR = @error_code DESCRIPTION = @error_description
END CONVERSATION @dialog_handle
    WITH ERROR = @error_code DESCRIPTION = N'An error has occurred.';
END CONVERSATION @dialog_handle
    WITH ERROR = 1234 DESCRIPTION = @error_description;
GO

CREATE PROCEDURE dbo.EndDialog
    @dialog_handle UNIQUEIDENTIFIER,
    @error_code INT,
    @error_description NVARCHAR(3000)
AS
BEGIN
    END CONVERSATION @dialog_handle;
    BEGIN
        END CONVERSATION @dialog_handle WITH CLEANUP
    END;
    END CONVERSATION @dialog_handle
        WITH ERROR = @error_code DESCRIPTION = @error_description
END;
GO
