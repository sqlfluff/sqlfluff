CREATE ROW ACCESS POLICY
row_access_policy_name ON example_dataset.example_table
FILTER USING (TRUE);

CREATE OR REPLACE ROW ACCESS POLICY
row_access_policy_name ON example_dataset.example_table
GRANT TO ("user:someone@example.com")
FILTER USING (x = y);

CREATE ROW ACCESS POLICY IF NOT EXISTS
row_access_policy_name ON example_dataset.example_table
GRANT TO (
   "serviceAccount:example@example-project.iam.gserviceaccount.com",
   "group:some_group@example.com",
   "domain:example.com"
)
FILTER USING (email_column_name = SESSION_USER());

CREATE OR REPLACE ROW ACCESS POLICY IF NOT EXISTS
row_access_policy_name ON example_dataset.example_table
GRANT TO ("allAuthenticatedUsers")
FILTER USING (SESSION_USER() IN ("foo", "bar"));

CREATE ROW ACCESS POLICY
row_access_policy_name ON example_dataset.example_table
GRANT TO ("allUsers")
FILTER USING (example_dataset.exampleFunction(x, y));
