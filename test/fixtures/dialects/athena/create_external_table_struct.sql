create external table my_database.my_table(
  `date` string,
  campaignId string,
  campaignName string,
  deleted string,
  campaignStatus string,
  app struct<appName:string,adamId:string>,
  servingStatus string,
  servingStateReasons string,
  countriesOrRegions array<string>,
  modificationTime string,
  totalBudget struct<amount:int,currency:string>,
  dailyBudget struct<amount:int,currency:string>,
  displayStatus string,
  supplySources array<string>,
  adChannelType string,
  orgId string,
  billingEvent string,
  countryOrRegionServingStateReasons string,
  other boolean,
  impressions int,
  taps int,
  installs int,
  newDownloads int,
  redownloads int,
  latOnInstalls int,
  latOffInstalls int,
  ttr int,
  avgCPA struct<amount:int,currency:string>,
  avgCPT struct<amount:int,currency:string>,
  avgCPM struct<amount:int,currency:string>,
  localSpend struct<amount:int,currency:string>,
  conversionRate int
)  PARTITIONED BY (field_partition string)
    ROW FORMAT DELIMITED
      FIELDS TERMINATED BY ','
      ESCAPED BY '\\'
      LINES TERMINATED BY '\n'
    LOCATION 's3://athena-examples-myregion/flight/csv/';
