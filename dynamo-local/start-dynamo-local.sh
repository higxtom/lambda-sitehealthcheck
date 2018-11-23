#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir ${SCRIPT_DIR}/_work
if [ ! -f ${SCRIPT_DIR}/_work/dynamodb_local_latest.zip ]; then
    curl https://s3-ap-northeast-1.amazonaws.com/dynamodb-local-tokyo/dynamodb_local_latest.zip -o ${SCRIPT_DIR}/_work/dynamodb_local_latest.zip
    cd ${SCRIPT_DIR}/_work && unzip ./dynamodb_local_latest.zip
    cd ${SCRIPT_DIR}/_work && java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
fi
cd ${SCRIPT_DIR}/_work && java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

