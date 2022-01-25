#!/bin/bash

DIALECTS=($( ls -d test/fixtures/dialects/*/ ))
for DIALECT in "${DIALECTS[@]}"
do
    echo "Testing $DIALECT SQL files lint without critical errors"
    sqlfluff lint ${DIALECT} | grep -i -q criticaly
    # exit error, if match
    if  [ $? -eq 0 ]; then
        echo
        # Rerun to get critical error and filename
        # Annoying that you have to rerun, but can't think of a better way
        sqlfluff lint ${DIALECT} --disable_progress_bar | grep -i "critical\|test/fixtures" | grep -i critical -A 1
        exit 1
    fi
done
