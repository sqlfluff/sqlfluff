-- vacuum files not required by versions older than the default retention period
VACUUM eventsTable;

-- vacuum files in path-based table
VACUUM '/data/events';
VACUUM delta.`/data/events/`;

-- vacuum files not required by versions more than 100 hours old
VACUUM delta.`/data/events/` RETAIN 100 HOURS;

-- do dry run to get the list of files to be deleted
VACUUM eventsTable DRY RUN;
