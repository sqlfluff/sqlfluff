-- Add files
ALTER DATABASE WideWorldImporters
ADD FILE (
    NAME = data1,
    FILENAME = 'D:\data\data1.ndf',
    SIZE = 5MB,
    MAXSIZE = 100MB,
    FILEGROWTH = 5MB
);
GO

ALTER DATABASE WideWorldImporters
ADD FILE
    (NAME = data2, FILENAME = 'D:\data\data2.ndf'),
    (NAME = [data 3], FILENAME = N'D:\data\data3.ndf')
TO FILEGROUP fg1;
GO

-- Add log files
ALTER DATABASE WideWorldImporters
ADD LOG FILE (NAME = log2, FILENAME = 'D:\log\log2.ldf');

ALTER DATABASE CURRENT
ADD LOG FILE
    (NAME = log3, FILENAME = 'D:\log\log3.ldf'),
    (NAME = log4, FILENAME = 'D:\log\log4.ldf');
GO

-- Remove a file
ALTER DATABASE WideWorldImporters
REMOVE FILE data1;

ALTER DATABASE WideWorldImporters REMOVE FILE [data 3];
GO

-- Modify a file
ALTER DATABASE WideWorldImporters
MODIFY FILE (NAME = data2, SIZE = 200MB);

ALTER DATABASE WideWorldImporters
MODIFY FILE (NAME = data2, NEWNAME = data2b);

ALTER DATABASE WideWorldImporters
MODIFY FILE (
    NAME = N'data2b',
    NEWNAME = N'data2',
    FILENAME = 'E:\data\data2.ndf',
    SIZE = 20MB,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 10%
);

ALTER DATABASE WideWorldImporters
MODIFY FILE (NAME = data2, OFFLINE);
GO

-- Add and remove a filegroup
ALTER DATABASE WideWorldImporters
ADD FILEGROUP fg1;

ALTER DATABASE CURRENT ADD FILEGROUP [fg 2];

ALTER DATABASE WideWorldImporters
ADD FILEGROUP fg_filestream CONTAINS FILESTREAM;

ALTER DATABASE WideWorldImporters
ADD FILEGROUP fg_memory_optimized CONTAINS MEMORY_OPTIMIZED_DATA;

ALTER DATABASE WideWorldImporters
REMOVE FILEGROUP fg1;
GO

-- Modify a filegroup
ALTER DATABASE WideWorldImporters
MODIFY FILEGROUP [PRIMARY] DEFAULT;

ALTER DATABASE WideWorldImporters
MODIFY FILEGROUP fg1 NAME = fg2;

ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 READONLY;
ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 READWRITE;
ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 READ_ONLY;
ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 READ_WRITE;
ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 AUTOGROW_SINGLE_FILE;
ALTER DATABASE WideWorldImporters MODIFY FILEGROUP fg2 AUTOGROW_ALL_FILES;
GO

-- The new keywords can still be used as identifiers
SELECT
    offline,
    readwrite,
    autogrow_all_files,
    autogrow_single_file
FROM dbo.settings;
