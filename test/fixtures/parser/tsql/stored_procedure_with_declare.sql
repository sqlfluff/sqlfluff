CREATE  OR ALTER   PROCEDURE [dbo].[SP_BEHAVIOR_NATIONAL]
AS
BEGIN
    DECLARE @wash_hands VARCHAR(50) = 'was_vaak_je_handen';
    DECLARE @keep_distance VARCHAR(50) = 'houd_1_5m_afstand';
    DECLARE @works_home VARCHAR(50) = 'werkt_thuis';
   
    SELECT 
        *
	FROM tablename
	WHERE column1 = @wash_hands
END;
