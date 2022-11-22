CREATE TABLE mydataset.newtable
LIKE mydataset.sourcetable
;

CREATE TABLE mydataset.newtable
LIKE mydataset.sourcetable
AS SELECT * FROM mydataset.myothertable
;

CREATE TABLE mydataset.newtable
COPY mydataset.sourcetable
;

CREATE TABLE mydataset.newtable_clone
CLONE mydataset.sourcetable
;
