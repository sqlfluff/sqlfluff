-- Full backup to disk
BACKUP DATABASE AdventureWorks2022
TO DISK = 'Z:\SQLServerBackups\AdventureWorks2022.bak';

-- Log backup to a logical device
BACKUP LOG AdventureWorks2022
TO MyAdvWorks_FullRM_log1;

-- Differential backup with options
BACKUP DATABASE Sales
TO DISK = N'D:\Backups\Sales_diff.bak'
WITH DIFFERENTIAL,
    INIT,
    NAME = N'Sales differential',
    DESCRIPTION = 'Nightly differential',
    STATS = 10,
    CHECKSUM;

-- Copy-only backup with compression, to two devices
BACKUP DATABASE @db_name
TO DISK = @path_1, DISK = @path_2
WITH COPY_ONLY, COMPRESSION, FORMAT, NOSKIP;

-- Compression algorithm (SQL Server 2022)
BACKUP DATABASE Sales
TO DISK = 'D:\Backups\Sales.bak'
WITH COMPRESSION (ALGORITHM = QAT_DEFLATE);

-- Mirrored backup set
BACKUP DATABASE AdventureWorks2022
TO TAPE = '\\.\tape0', TAPE = '\\.\tape1'
MIRROR TO TAPE = '\\.\tape2', TAPE = '\\.\tape3'
WITH FORMAT, MEDIANAME = 'MyMedia', MEDIADESCRIPTION = 'Mirrored set';

-- Encrypted backup to URL
BACKUP DATABASE Sales
TO URL = 'https://mystorage.blob.core.windows.net/backups/Sales.bak'
WITH ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = BackupCert),
    RETAINDAYS = 30;

-- File and filegroup backup
BACKUP DATABASE Sales
FILEGROUP = 'SalesGroup1', FILEGROUP = 'SalesGroup2'
TO DISK = 'C:\MySQLServer\Backups\Sales\SalesFiles.bck';

-- Tail-log backup
BACKUP LOG Sales
TO DISK = 'D:\Backups\Sales_tail.trn'
WITH NORECOVERY, NO_TRUNCATE, EXPIREDATE = '2026-12-31';

-- Backup to URL with a credential
BACKUP DATABASE Sales
TO URL = 'https://mystorage.blob.core.windows.net/backups/Sales.bak'
WITH CREDENTIAL = 'mycredential', COMPRESSION;
