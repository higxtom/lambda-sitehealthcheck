# coding: utf-8

import boto3
import json
import sys
import os
import traceback
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr

BASE_ARN_URL = os.environ['BASE_ARN_URL']
ENDPOINT_URL = os.environ['ENDPOINT_URL']
SNS_TOPIC_ERR = os.environ['SNS_TOPIC_ERR']
SNS_TOPIC_INF = os.environ['SNS_TOPIC_INF']
DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']
NOTICE_ERROR = "ERROR"
NOTICE_INFO = "INFO"

dynamodb = boto3.resource('dynamodb', endpoint_url=ENDPOINT_URL)

# lamber_handler : メイン処理
# --------------------------------------------------------------
#  DynamoDB にチェック対象のサイトURL、名前、前回ステータスを保持。
#  DB登録情報に従って、サイトの死活をチェックし、前回と異なっていれば、
#  SNSを経由して通知する。
#  サーバがダウンした場合は、SMSを通知するSNS TOPIC、
#  サーバが復帰した場合は、メールを通知するSNS TOPICに送信する。
#  それ以外の状態が変化しない場合は、通知は行わない。
# --------------------------------------------------------------
def lambda_handler(event, context):
    if len(SNS_TOPIC_INF) == 0 or len(SNS_TOPIC_ERR) == 0:
        print "Please set SNS_TOPICS_INF|ERR."
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
                send_notice(NOTICE_ERROR,site_name, target_url, current_state)
            else:
                print "Server is still DEAD."
        else:
            if prev_state == False:
                print "State has changed to ALIVE."
                put_site_status(target_url, site_name, current_state)
                send_notice(NOTICE_INFO, site_name, target_url, current_state)
            else:
                print "Server is good."
            
# check_health_status : サイトの死活監視
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

# send_notice : AWS SNSを使ったメッセージの送信
def send_notice(level, name, url, status):
    sns = boto3.client('sns')
    
    if level == NOTICE_ERROR:
        sns_topic_arn = BASE_ARN_URL + SNS_TOPIC_ERR
    else:
        sns_topic_arn = BASE_ARN_URL + SNS_TOPIC_INF
    
    if status == True:
        site_status = "ALIVE"
    else:
        site_status = "DEAD"

    subject = "[ServerMonitor - " + level + "] Server Status Changed."
    sns_message = "Site: [" + name + "] status changed to " + site_status + ".¥n Please check the servers."
    response = sns.publish(
        TopicArn=sns_topic_arn,
        Message=sns_message,
        Subject=subject
    )
    return response

# get_target_sites : チェック対象のサイト・URL情報の取得
def get_target_sites():

    try:
        table = dynamodb.Table(DDB_TABLE_NAME)
        resultset = table.scan()
        return resultset

    except:
        traceback.print_exc()

# put_site_status : チェック対象サイトの最新ステータス更新
def put_site_status(url, name, isAlive):
    site_table = dynamodb.Table('SiteStatus')
    site = {
        "Url": url,
        "SiteName": name,
        "IsAlive": isAlive
    }
    site_table.put_item(Item=site)
