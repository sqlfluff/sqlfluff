-- Basic CREATE DCM PROJECT
CREATE DCM PROJECT my_dcm_project;
CREATE DCM PROJECT IF NOT EXISTS my_dcm_project;
CREATE OR REPLACE DCM PROJECT my_dcm_project;

-- With LOG_LEVEL
CREATE DCM PROJECT my_dcm_project
    LOG_LEVEL = DEBUG;

CREATE DCM PROJECT my_dcm_project
    LOG_LEVEL = INFO;

CREATE DCM PROJECT my_dcm_project
    LOG_LEVEL = WARN;

CREATE DCM PROJECT my_dcm_project
    LOG_LEVEL = ERROR;

-- With COMMENT
CREATE DCM PROJECT my_dcm_project
    COMMENT = 'My DCM project';

-- Full example
CREATE OR REPLACE DCM PROJECT my_dcm_project
    LOG_LEVEL = INFO
    COMMENT = 'Full DCM project example';
