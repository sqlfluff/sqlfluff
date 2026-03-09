-- CREATE EXTERNAL DATA SOURCE pointing to Azure Blob Storage
CREATE EXTERNAL DATA SOURCE SqlOnDemandDemo
WITH (LOCATION = 'https://fabrictutorialdata.blob.core.windows.net/sampledata/Synapse');

-- CREATE EXTERNAL DATA SOURCE pointing to Azure Data Lake Storage Gen2
CREATE EXTERNAL DATA SOURCE nyctlc
WITH (LOCATION = 'https://azureopendatastorage.blob.core.windows.net/nyctlc/');

-- CREATE EXTERNAL DATA SOURCE for Delta Lake
CREATE EXTERNAL DATA SOURCE DeltaLakeStorage
WITH (LOCATION = 'https://fabrictutorialdata.blob.core.windows.net/sampledata/Synapse/delta-lake');

-- CREATE EXTERNAL DATA SOURCE with SAS credential
CREATE EXTERNAL DATA SOURCE AzureDataLakeStore
WITH (
    LOCATION = 'https://myaccount.dfs.core.windows.net/mycontainer',
    CREDENTIAL = SasCredential
);
