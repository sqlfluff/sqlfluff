-- Basic restore from disk
RESTORE DATABASE testdb
FROM DISK = 'c:\tmp'
WITH RECOVERY,
    REPLACE,
    MOVE 'data file' TO 'c:\tmp\database.mdf',
    MOVE 'log file' TO 'c:\tmp\logfile.ldf';

-- Restore with NORECOVERY
RESTORE DATABASE mydb
FROM DISK = 'D:\Backups\mydb.bak'
WITH NORECOVERY;

-- Restore with STANDBY
RESTORE DATABASE mydb
FROM DISK = 'D:\Backups\mydb.bak'
WITH STANDBY = 'D:\Backups\mydb_standby.bak';

-- Restore with multiple options
RESTORE DATABASE mydb
FROM DISK = 'D:\Backups\mydb.bak'
WITH RECOVERY,
    REPLACE,
    STATS = 10,
    CHECKSUM;

-- Restore with variable for database name
RESTORE DATABASE @database_name
FROM DISK = @backup_path
WITH RECOVERY, REPLACE;

-- Restore from tape
RESTORE DATABASE testdb
FROM TAPE = '\\.\TAPE0'
WITH RECOVERY;

-- Restore from URL (Azure blob storage)
RESTORE DATABASE mydb
FROM URL = 'https://myaccount.blob.core.windows.net/mycontainer/mydb.bak'
WITH RECOVERY;

-- Restore with file and filegroup options
RESTORE DATABASE mydb
FILE = 'mydb_data',
FILEGROUP = 'PRIMARY'
FROM DISK = 'D:\Backups\mydb.bak'
WITH RECOVERY;

-- Restore with media and transfer options
RESTORE DATABASE mydb
FROM DISK = 'D:\Backups\mydb.bak'
WITH MEDIANAME = 'MyBackupSet',
    BLOCKSIZE = 65536,
    BUFFERCOUNT = 10,
    MAXTRANSFERSIZE = 1048576;

-- Restore with no truncate (tail log backup)
RESTORE DATABASE mydb
FROM DISK = 'D:\Backups\mydb.bak'
WITH NO_TRUNCATE,
    NORECOVERY;
