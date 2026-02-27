-- Basic application from package
CREATE APPLICATION my_app
  FROM APPLICATION PACKAGE my_package;

-- Application from package with version
CREATE APPLICATION my_app
  FROM APPLICATION PACKAGE my_package
  USING VERSION v1 PATCH 2
  DEBUG_MODE = TRUE
  COMMENT = 'test app';

-- Application from listing
CREATE APPLICATION my_app
  FROM LISTING my_listing
  COMMENT = 'marketplace app'
  AUTHORIZE_TELEMETRY_EVENT_SHARING = TRUE;

-- Application from package using stage path
CREATE APPLICATION my_app
  FROM APPLICATION PACKAGE my_package
  USING @my_stage/path/to/version
  TAG (env = 'dev');
