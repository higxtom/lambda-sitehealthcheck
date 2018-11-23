import os
import uuid
import boto3

endpoint_url = "http://localhost:8000"
dynamodb = boto3.resource('dynamodb', endopoint_url=endpoint_url)
site_table = dynamodb.Table('SiteStatus')
site = {
    "Url": "https://www.lightbehindtheclouds.com/health.html",
    "SiteName": "Health check page on Light Behind the Clouds.",
    "isAlive": True
}
site_table.put_item(Item=site)
