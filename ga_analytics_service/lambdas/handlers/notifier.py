#!/usr/bin/python3.8
# -*- encoding: utf-8 -*-
import urllib3
import os
import json


def notify_slack_channel(message):

    message = '*GA Analytics Service Console*\n' + message

    url = os.environ["SLACK_CHANNEL_WEBHOOK"]
    slack_data = {
        "username": "GoogleAnalyticsDetectiveBOT",
        "icon_emoji": ":female-detective:",
        "channel" : "#company-ga-analytics-service-alerts",
        "blocks": [
            {
                "type": "section",
                "text": 
                    {
                        "type": "mrkdwn",
                        "text": message
                    } 
            }
        ]
    }
    http = urllib3.PoolManager()
    headers = {'Content-Type': "application/json"}
    response = http.urlopen('POST', url, headers=headers, body=json.dumps(slack_data))
    if response.status != 200:
        raise Exception(response.status, response.data.decode('utf-8'))



