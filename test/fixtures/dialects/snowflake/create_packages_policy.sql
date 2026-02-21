-- Basic packages policy
CREATE PACKAGES POLICY my_packages_policy
  LANGUAGE PYTHON
  ALLOWLIST = ('numpy', 'pandas');

-- Full packages policy
CREATE OR REPLACE PACKAGES POLICY IF NOT EXISTS my_packages_policy
  LANGUAGE PYTHON
  ALLOWLIST = ('numpy', 'pandas==1.2.3')
  BLOCKLIST = ('os', 'subprocess')
  ADDITIONAL_CREATION_BLOCKLIST = ('requests')
  COMMENT = 'restrict python packages';
