
-- Alter connection rotate keys
ALTER CONNECTION test rotate keys;

-- Alter default privileges
ALTER DEFAULT PRIVILEGES FOR ROLE mike GRANT SELECT ON TABLES TO joe;
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT SELECT ON TABLES TO managers;

-- Alter name
ALTER CONNECTION test RENAME TO test2;
ALTER INDEX test RENAME TO test2;
ALTER MATERIALIZED VIEW test RENAME TO test2;
ALTER SOURCE test RENAME TO test2;
ALTER SINK test RENAME TO test2;
ALTER TABLE test RENAME TO test2;
ALTER VIEW test RENAME TO test2;
ALTER SECRET test RENAME TO test2;

-- Alter index enable
ALTER INDEX test_idx SET ENABLED;

-- Alter secret value
ALTER SECRET IF EXISTS name AS value;
ALTER SECRET name AS value;

-- Alter Sink size
ALTER SOURCE IF EXISTS sink_name SET ( SIZE 'xsmall' );

-- Alter Source size
ALTER SINK IF EXISTS source_name SET ( SIZE 'xsmall' );
