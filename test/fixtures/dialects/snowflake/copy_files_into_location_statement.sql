COPY FILES INTO '@stage/folder'
  FROM '@other_stage/folder';

COPY FILES INTO '@stage/folder'
  FROM '@other_stage/folder'
    FILES = ('data.csv', 'data2.csv');

COPY FILES INTO '@stage/folder'
  FROM '@other_stage/folder'
    PATTERN = '.*[.]parquet.*';

COPY FILES INTO '@stage/folder'
  FROM '@other_stage/folder'
    DETAILED_OUTPUT = TRUE;

COPY FILES INTO '@stage/folder'
  FROM '@other_stage/folder'
    FILES = ('data.csv', 'data2.csv')
    PATTERN = '.*[.]parquet.*'
    DETAILED_OUTPUT = TRUE;
