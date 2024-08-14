SELECT test FROM toto FORMAT CSV;

SELECT 1 FORMAT CSV;

SELECT 1 as test FORMAT CSV;

SELECT test FROM dual where test = '1' FORMAT CSV;

SELECT test FROM dual where test = '1' FORMAT CSV SETTINGS format_csv_delimiter = ',';
