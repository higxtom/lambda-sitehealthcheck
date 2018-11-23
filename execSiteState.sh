#!/bin/bash

RES_DYNAMODB="'dynamodb', endpoint_url='http://localhost:8000'"
DDB_TABLE_NAME="SiteStatus"

python-lambda-local --function lambda_handler UrlStatusCheck.py event.json

