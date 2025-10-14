
REVOKE CREATE TABLE ON SCHEMA main.default FROM `finance-team`;
REVOKE USE SCHEMA ON SCHEMA main.default FROM `finance-team`;
REVOKE USE CATALOG ON CATALOG main FROM `finance-team`;
REVOKE EXECUTE ON FUNCTION prod.ml_team.iris_model FROM `ml-team-acme`;
REVOKE READ ON METASTORE FROM 'principal';
REVOKE SELECT ON VIEW schema.view FROM `the_view_accessors`;