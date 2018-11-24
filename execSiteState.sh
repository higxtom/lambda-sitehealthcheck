#!/bin/bash

export BASE_ARN_URL="arn:aws:sns:us-west-2:626518033460:"
export ENDPOINT_URL="http://localhost:8000"
export SNS_TOPIC_INF="InfoNotification"
export SNS_TOPIC_ERR="ErrorNotification"
export DDB_TABLE_NAME="SiteStatus"

export URL_4TEST="https://www.lightbehindtheclouds.com/health.html"
#URL_4TEST="https://www.lightbehindtheclouds.com/notfound.html"

python-lambda-local --function lambda_handler UrlStatusCheck.py event.json

