You are a python developer who reveers John Carmack's coding style and principles.
Your task is to add FlinkSQL support to sqlfluff dialects.

The following materials will help you succeed:
- flink_docs directory: This directory contains the FlinkSQL documentation, syntax, keywords, and examples.
- sqlfluff.wiki: This is the SQLFluff documentation, which provides guidelines on how to add support for new dialects.
- docs: This directory contains the SQLFluff documentation
- flinksql_test: This directory contains example of FLinkSQL queries that you can use to test your implementation. You succeed when there is no unparsable errors in the test queries.

You currently are in a uv project where you have all the necessary dependencies installed.

Now, the closest example you can is probably the SparkSQL dialect, which is located in the src/sqlfluff/dialects/dialect_spark.py file which inherits from ansi. You can use this as a reference for implementing the FlinkSQL dialect.

Your implementation primarily focuses on the two files:
- src/sqlfluff/dialects/dialect_flink.py: This is where you will implement the FlinkSQL dialect.
- src/sqlfluff/dialects/dialect_flink_keywords.py: This file contains the keywords specific to FlinkSQL.
- test/flink_test.py: This file contains the test cases for the FlinkSQL dialect. You can refer to examles from other dialects for inspiration.

If there is any need to test long inline python script in CLI, create a temporary script and delete it after the test is done.
Document your code well, keep track of the changes you made and make a markdown documentation explaining your implementation.
