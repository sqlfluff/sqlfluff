-- Basic managed account
CREATE MANAGED ACCOUNT my_reader_account
  ADMIN_NAME = 'admin_user',
  ADMIN_PASSWORD = 'TestPassword123!';

-- Managed account with TYPE
CREATE MANAGED ACCOUNT my_reader_account
  ADMIN_NAME = 'admin_user',
  ADMIN_PASSWORD = 'TestPassword123!',
  TYPE = READER
  COMMENT = 'reader account for partner';
