# Delta Lake

[Delta Lake](https://delta.io/) is an open-source storage framework that integrates
with Spark.

Since dialects in SQLFluff do not strictly adhere to their specifications and can
contain a wider set of functionality, Delta syntax has been added to the SparkSQL
dialect. This causes no adverse affects to the core dialect, other than the potential
possibility of code parsing correctly that will not execute if Delta Lake is not
configured.

Test cases for Delta Lake are located here for easier identification.
