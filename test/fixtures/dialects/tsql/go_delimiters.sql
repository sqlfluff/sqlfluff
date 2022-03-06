-- It's possible to have multiple GO between batches.
-- It's also possible for a file to start with any number of GO.
GO GO
GO
SELECT foo FROM bar GO GO
SELECT foo FROM bar GO
GO
GO
SELECT foo FROM bar GO
