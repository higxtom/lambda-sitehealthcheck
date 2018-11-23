import boto3
import json
import sys
import os
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr

SNS_TOPICS_NAME = "TOPICS"
DDB_TABLE_NAME = "SiteStatus"

URL_200_4TEST = "https://www.lightbehindtheclouds.com/health.html"
URL_404_4TEST = "https://www.lightbehindtheclouds.com/notfound.html"
ENDPOINT_URL = "http://localhost:8000"

dynamodb = boto3.resource('dynamodb', endpoint_url=ENDPOINT_URL)

def lambda_handler(event, context):
    if len(SNS_TOPICS_NAME) == 0 :
        print "Please set SNS_TOPICS_NAME."
        sys.exit()
    check_health_status(URL_404_4TEST)
    put_site_status("https://www.lightbehindtheclouds.com/health.html", "Health check page on Light Behind the Clouds.", True)
    put_site_status("https://www.lightbehindtheclouds.com/notfound.html", "Bad page on Light Behind the Clouds.", False)


def check_health_status(target_url):

    try:
        response = requests.get(target_url)
        print response.status_code

        if response.status_code != 200:
            print "Target Site might be down."
        else:
            print "Target Site is alive."
    except Exception:
        print "Exception occurred."

def send_error(name, url, status_changed_servers):
    sns = boto3.client('sns')
    sns_message = "Server status changed. Please check the servers."
    
    subject = '[ServerMonitor] Server Status Changed.'
    response = sns.publish(
        TopicArn=SNS_TOPICS_NAME,
        Message=sns_message,
        Subject=subject
    )
    return response

def get_previous_status(url):

    isAlive = True
    try:
        items = dynamodb.table(DDB_TABLE_NAME).get_item(Key={"url": url})
        isAlive = items['url']['isAlive']
    except:
        isAlive = None
    return isAlive

def put_site_status(url, name, isAlive):
    site_table = dynamodb.Table('SiteStatus')
    site = {
        "Url": url,
        "SiteName": name,
        "IsAlive": isAlive
    }
    site_table.put_item(Item=site)
