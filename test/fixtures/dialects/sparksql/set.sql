SET spark.sql.variable.substitute = FALSE;

SET -v;

SET;

SET spark.sql.variable.substitute;

SET spark.sql.cache.serializer=org.apache.spark.sql.execution.columnar.DefaultCachedBatchSerializer;
