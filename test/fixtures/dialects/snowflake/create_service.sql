-- Basic service with specification file from stage
CREATE SERVICE my_service
  IN COMPUTE POOL my_pool
  FROM @my_stage SPECIFICATION_FILE = 'spec.yaml';

-- Service with inline specification
CREATE SERVICE IF NOT EXISTS my_db.my_schema.my_service
  IN COMPUTE POOL my_pool
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: main
        image: /my_db/my_schema/my_repo/my_image:latest
  $$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 3
  COMMENT = 'my service';

-- Service with specification template
CREATE SERVICE my_service
  IN COMPUTE POOL my_pool
  FROM @my_stage SPECIFICATION_TEMPLATE_FILE = 'spec.yaml'
  USING (key1 => 'value1', key2 => 'value2')
  AUTO_SUSPEND_SECS = 300
  AUTO_RESUME = TRUE
  LOG_LEVEL = 'INFO'
  QUERY_WAREHOUSE = my_wh
  TAG (env = 'prod', team = 'data');

-- Service with specification file (native app, no stage)
CREATE SERVICE my_service
  IN COMPUTE POOL my_pool
  FROM SPECIFICATION_FILE = 'spec.yaml'
  MIN_INSTANCES = 1
  MIN_READY_INSTANCES = 1
  MAX_INSTANCES = 5;
