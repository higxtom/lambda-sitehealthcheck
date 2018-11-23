import boto3
import json
import sys
import os
import traceback
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr

BASE_ARN_URL = os.environ['BASE_ARN_URL']
ENDPOINT_URL = os.environ['ENDPOINT_URL']
SNS_TOPIC_NAME = os.environ['SNS_TOPIC_NAME']
DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

dynamodb = boto3.resource('dynamodb', endpoint_url=ENDPOINT_URL)

def lambda_handler(event, context):
    if len(SNS_TOPIC_NAME) == 0 :
        print "Please set SNS_TOPICS_NAME."
        sys.exit()

    rs = get_target_sites()
    for item in rs['Items']:
        target_url = item['Url']
        print target_url
        prev_state = item['IsAlive']
        site_name = item['SiteName']

        current_state = check_health_status(target_url)
        if current_state != True:
            if prev_state == True:
                print "Statu has changed to DEAD."
                put_site_status(target_url, site_name, current_state)
            else:
                print "Server is still DEAD."
        else:
            if prev_state == False:
                print "State has changed to ALIVE."
                put_site_status(target_url, site_name, current_state)
            else:
                print "Server is good."
            

def check_health_status(target_url):
    HTTP_OK = 200
    
    try:
        response = requests.get(target_url)
        print response.status_code

        if response.status_code != HTTP_OK:
            print "Target Site might be down."
            return False
        else:
            print "Target Site is alive."
            return True
    except Exception:
        traceback.print_exc()
        return False

def send_error(name, url, status_changed_servers):
    sns = boto3.client('sns')
    sns_message = "Server status changed. Please check the servers."
    
    subject = '[ServerMonitor] Server Status Changed.'
    response = sns.publish(
        TopicArn=SNS_TOPIC_NAME,
        Message=sns_message,
        Subject=subject
    )
    return response

def get_target_sites():

    try:
        table = dynamodb.Table(DDB_TABLE_NAME)
        resultset = table.scan()
        return resultset

    except:
        traceback.print_exc()

def put_site_status(url, name, isAlive):
    site_table = dynamodb.Table('SiteStatus')
    site = {
        "Url": url,
        "SiteName": name,
        "IsAlive": isAlive
    }
    site_table.put_item(Item=site)
