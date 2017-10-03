import boto3
import json
import os
import requests
from slacker import Slacker


def send_to_slack(message, attachment, channel, key):
    status = True
    print("sending slack message " + message)
    emoji = ":elasticbeanstalk:"

    if not channel.startswith('#'):
        channel = '#' + channel

    slack = Slacker(key)
    slack.chat.post_message(
        channel=channel,
        text=message,
        attachments=attachment,
        as_user="false",
        username="AWS Elastic Beanstalk Notifier",
        icon_emoji=emoji)

    return status


def send_to_victorops(rest_url, message):
    status = True

    response = requests.post(
        rest_url, data=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        print("Request to VictorOps returned an error " + response.status_code + " " + response.text)
        status = False

    return status


def lambda_handler(event, context):
    status = True
    managed_update = False
    response = None

    if 'slack_api_token' in os.environ:
        slack_api_token = os.environ['slack_api_token']
    else:
        print("FATAL: No slack api token set in the slack_api_token environment variable")
        status = False

    if 'slack_channel' in os.environ:
        slack_channel = os.environ['slack_channel']
    else:
        print("FATAL: No slack channel set in the slack_channel environment variable")
        status = False

    if status:
        region = event['region']
        event_name = event['detail']['eventName']

        # First let's see if this is a managed update event
        if event_name == "UpdateEnvironment":
            if 'optionSettings' in event['detail']['requestParameters']:
                for option in event['detail']['requestParameters']['optionSettings']:
                    print("Found option " + option['optionName'] + " value " + option['value'] + " namespace " + option['namespace'])

                    if option['namespace'] == 'aws:elasticbeanstalk:managedactions':
                        managed_update = True

        if managed_update:
            if 'solutionStackName' in event['detail']['requestParameters']:
                new_platform = event['detail']['requestParameters']['solutionStackName']
            else:
                print("ERROR: unable to read new platform from event")
                print("Received event: " + json.dumps(event, indent=2))
                new_platform = "Unknown"

            if 'environmentId' in event['detail']['requestParameters']:
                # We get the environment ID in the request, but need to lookup
                # the env name
                environment_id = event['detail']['requestParameters']['environmentId']
                client = boto3.client('elasticbeanstalk')

                try:
                    response = client.describe_environments(
                        EnvironmentIds=[environment_id]
                    )
                except Exception as e:
                    print("Failed to describe environment " + environment_id + " : " + str(e))
                    print("Received event: " + json.dumps(event, indent=2))
                    status = False

                if response:
                    environment_name = response['Environments'][0]['EnvironmentName']
                    application_name = response['Environments'][0]['ApplicationName']
                    current_platform = response['Environments'][0]['SolutionStackName']

                    print("environment id: " + environment_id)
                    print("environment_name: " + environment_name)
                    print("application name: " + application_name)
                    print("current platform: " + current_platform)
                    print("new platform: " + new_platform)

                    update_details_console_link = "https://" + region + \
                        ".console.aws.amazon.com" + \
                        "/elasticbeanstalk/home?region=" + region + \
                        "#/environment/managedActions?applicationName=" + \
                        application_name + \
                        "&environmentId=" + environment_id

                    slack_message = "Managed update applied to `" + \
                        environment_name + "` in " + region
                    slack_attachment = [
                        {
                            "fallback": "Check the EB console for details.",
                            "color": "#36a64f",
                            "title": "View Update Details in the AWS Console",
                            "title_link": update_details_console_link,
                                        "fields": [
                                            {
                                                "title": "Current Platform",
                                                "value": current_platform,
                                                "short": 'false'
                                            },
                                            {
                                                "title": "New Platform",
                                                "value": new_platform,
                                                "short": 'false'
                                            }
                                        ]
                        }
                    ]

                    status = send_to_slack(
                        slack_message,
                        slack_attachment,
                        slack_channel,
                        slack_api_token)

                    if 'victorops_webhook_url' in os.environ:
                        victorops_endpoint = os.environ['victorops_webhook_url']

                        if victorops_endpoint:
                            victorops_message = {
                                "message_type": "INFO",
                                "entity_id": "elasticbeanstalk/" +
                                environment_name,
                                "entity_display_name": "AWS Elastic Beanstalk",
                                "state_message": "Managed platform update applied to environment " +
                                environment_name}

                            send_to_victorops(
                                victorops_endpoint, victorops_message)
            else:
                print("FATAL: No environment ID specified in the event - unable to process")
                print("Received event: " + json.dumps(event, indent=2))
                status = False

    return status
