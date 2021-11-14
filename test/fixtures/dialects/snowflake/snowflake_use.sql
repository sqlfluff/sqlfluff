use role my_role;

use warehouse my_warehouse;

use database my_database;

use schema my_schema;

USE ROLE "MY_ROLE";

USE WAREHOUSE "MY_WAREHOUSE";

USE WAREHOUSE &warehouse;

USE WAREHOUSE &{warehouse};

USE WAREHOUSE MARKETING_&{environment};

USE WAREHOUSE &{environment}_MARKETING;

USE DATABASE "MY_DATABASE";

USE "MY_DATABASE";

USE SCHEMA "MY_DATABASE"."MY_SCHEMA";

USE SCHEMA "MY_SCHEMA";

USE "MY_DATABASE"."MY_SCHEMA";
