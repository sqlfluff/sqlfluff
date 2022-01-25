#!/bin/bash

DIALECTS=($( ls -d test/fixtures/dialects/*/ ))
for DIALECT in "${DIALECTS[@]}"
do
    echo "Testing $DIALECT SQL files lint without critical errors..."
    OUTPUT=$(sqlfluff lint ${DIALECT})
    echo "${OUTPUT}" | grep -i -q critical
    # exit error, if match
    if  [ $? -eq 0 ]; then
        echo "Critical errors found:"
        echo "${OUTPUT}" | grep -i "critical\|test/fixtures" | grep -i critical -A 1
        exit 1
    fi
done
