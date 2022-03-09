#!/bin/bash

echo "This script will run 'sqlfluff fix -f' on all our dialect fixtures"
echo "to look for critical errors."
echo "WARNING this will change the fixtures so do not commit these changes!"

DIALECTS=($( ls -d test/fixtures/dialects/*/ ))
for DIALECT in "${DIALECTS[@]}"
do
    echo "Testing $DIALECT SQL files fix without critical errors..."
    OUTPUT=$(sqlfluff fix -f ${DIALECT})
    echo "${OUTPUT}" | grep -i -q critical
    # exit error, if match
    if  [ $? -eq 0 ]; then
        echo "Critical errors found:"
        echo "${OUTPUT}" | grep -i "critical\|test/fixtures" | grep -i critical -A 1
        exit 1
    fi
done

echo "WARNING If running locally you should revert the changes."
