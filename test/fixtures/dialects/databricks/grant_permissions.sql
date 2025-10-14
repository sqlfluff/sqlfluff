-- Adding some permission examples from https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/?language=SQL

GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
GRANT USE SCHEMA ON SCHEMA main.default TO `finance-team`;
GRANT USE CATALOG ON CATALOG main TO `finance-team`;
GRANT EXECUTE ON FUNCTION prod.ml_team.iris_model TO `ml-team-acme`;
GRANT READ ON METASTORE TO 'principal';
GRANT SELECT ON VIEW schema.view TO `the_view_accessors`;
GRANT ALL PRIVILEGES ON CATALOG main TO `data-engineers`;