-- Basic compute pool
CREATE COMPUTE POOL my_pool
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = CPU_X64_XS;

-- Full compute pool with all options
CREATE COMPUTE POOL IF NOT EXISTS my_pool
  FOR APPLICATION my_app
  MIN_NODES = 2
  MAX_NODES = 10
  INSTANCE_FAMILY = GPU_NV_S
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  AUTO_SUSPEND_SECS = 3600
  PLACEMENT_GROUP = 'my_placement_group'
  TAG (env = 'prod', team = 'ml')
  COMMENT = 'GPU compute pool';
