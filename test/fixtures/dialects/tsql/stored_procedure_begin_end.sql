CREATE PROCEDURE dbo.Test_Begin_End
AS
BEGIN
	SELECT 'Weekend';
	
	select a from tbl1;
	
	select b from tbl2;
END
