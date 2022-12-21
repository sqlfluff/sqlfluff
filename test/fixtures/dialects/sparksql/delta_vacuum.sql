-- vacuum files not required by versions older than the default retention period
VACUUM EVENTSTABLE;

-- vacuum files in path-based table
VACUUM '/data/events';
VACUUM DELTA.`/data/events/`;

-- vacuum files not required by versions more than 100 hours old
VACUUM DELTA.`/data/events/` RETAIN 100 HOURS;

-- do dry run to get the list of files to be deleted
VACUUM EVENTSTABLE DRY RUN;
