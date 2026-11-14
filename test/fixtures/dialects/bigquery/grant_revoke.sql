GRANT `roles/bigquery.dataViewer`
ON SCHEMA `myProject`.myDataset
TO "user:raha@example-pet-store.com", "user:sasha@example-pet-store.com";

GRANT `roles/bigquery.dataViewer`, `roles/bigquery.dataEditor`
ON TABLE `myProject.myDataset.myTable`
TO "serviceAccount:robot@example.iam.gserviceaccount.com";

GRANT `roles/bigquery.dataViewer`
ON VIEW myDataset.myView
TO "specialGroup:allAuthenticatedUsers";

GRANT `roles/bigquery.dataViewer`
ON EXTERNAL TABLE myDataset.myExternalTable
TO "domain:example.com";

GRANT `roles/aiplatform.user`, `roles/run.invoker`
ON PROJECT `my-vertex-project`
TO "connection:my-bq-project.us.my-connection",
    "connection:another-bq-project.eu.other-connection";

REVOKE `roles/bigquery.admin`
ON SCHEMA `myProject`.myDataset
FROM "group:example-team@example-pet-store.com",
    "serviceAccount:user@test-project.iam.gserviceaccount.com";

REVOKE `roles/run.invoker`
ON PROJECT `my-vertex-project`
FROM "connection:my-bq-project.us.my-connection";

GRANT `roles/bigquery.dataViewer`
ON TABLE my-project.mydataset.mytable
TO "user:raha@example-pet-store.com";
