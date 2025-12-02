CREATE SINK quotes_sink
  FROM quotes
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'quotes-sink')
  FORMAT JSON
  ENVELOPE DEBEZIUM
  WITH (SIZE = '3xsmall');

CREATE SINK frank_quotes_sink
  FROM frank_quotes
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'frank-quotes-sink')
  FORMAT JSON
  ENVELOPE DEBEZIUM
  WITH (SIZE = '3xsmall');

CREATE SINK frank_quotes_cluster
  IN CLUSTER my_cluster
  FROM frank_quotes
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'frank-quotes-sink')
  FORMAT JSON
  ENVELOPE DEBEZIUM;
