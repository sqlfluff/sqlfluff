-- Suspend service
ALTER SERVICE my_service SUSPEND;

-- Resume service
ALTER SERVICE IF EXISTS my_service RESUME;

-- Set properties
ALTER SERVICE my_service SET
  MIN_INSTANCES = 2
  MAX_INSTANCES = 5
  LOG_LEVEL = 'WARN'
  AUTO_SUSPEND_SECS = 600
  COMMENT = 'updated service';

-- Unset properties
ALTER SERVICE my_service UNSET MIN_INSTANCES, MAX_INSTANCES, COMMENT;

-- Update specification from stage
ALTER SERVICE my_service
  FROM @my_stage SPECIFICATION_FILE = 'new_spec.yaml';

-- Restore volume from snapshot
ALTER SERVICE my_service
  RESTORE VOLUME 'data_vol'
  INSTANCES 0, 1
  FROM SNAPSHOT my_snapshot;
