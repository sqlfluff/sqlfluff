CREATE PROCEDURE dbo.Test_Begin_End
AS
BEGIN
	SELECT 'Weekend';

	select a from tbl1;

	select b from tbl2;
END;
GO

CREATE PROCEDURE [dbo].[usp_process_tran_log]
	  @out_vchCode uddt_output_code OUTPUT
	, @out_vchMsg uddt_output_msg OUTPUT
	, @in_debug INT = 1
AS
--*******************************************************************************************
SET NOCOUNT ON;
BEGIN
SELECT '8'
END;
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_process_tran_log]
	  @out_vchCode uddt_output_code OUTPUT
	, @out_vchMsg uddt_output_msg OUT
	, @in_debug INT = 1 READONLY
AS
--*******************************************************************************************
SET NOCOUNT ON;
BEGIN
SELECT '8'
END;
GO

ALTER PROCEDURE [dbo].[usp_process_tran_log]
	  @out_vchCode uddt_output_code OUTPUT
	, @out_vchMsg uddt_output_msg OUTPUT
	, @in_debug INT = 1
AS
SET NOCOUNT ON;
BEGIN
	BEGIN TRY
		SELECT '8';
	END TRY
	BEGIN CATCH
		SET @v_nSysErrorNum = ERROR_NUMBER();
		SET @v_vchCode = ERROR_LINE();
		SET @v_vchMsg = N'Missing control type.';
		SET @v_vchMsg = @v_vchMsg + N' SQL Error = ' + ERROR_MESSAGE();
		GOTO ERROR_HANDLER;
	END CATCH
END;
GO
