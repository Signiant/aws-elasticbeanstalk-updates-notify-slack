import boto3
import json
import sys,os
from slacker import Slacker

def send_to_slack(message,channel,key):
    status = True
    print "sending slack message " + message
    emoji=":elasticbeanstalk:"

    if not channel.startswith( '#' ):
        channel = '#' + channel

    slack = Slacker(key)
    slack.chat.post_message(
        channel=channel,
        text=message,
        as_user="false",
        username="AWS EB Notifier",
        icon_emoji=emoji)

    return status

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    status=True

    return status
