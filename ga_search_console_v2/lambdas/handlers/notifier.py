#!/usr/bin/python3.8
# -*- encoding: utf-8 -*-
import urllib3
import os
import json


def notify_slack_channel(message):

    message = '*GA Search Console*\n' + message

    url = os.environ["SLACK_CHANNEL_WEBHOOK"]
    slack_data = {
        "username": "GASearchConsoleDetectiveBOT",
        "icon_emoji": ":female-detective:",
        "channel" : "#company-ga-search-console-alerts",
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



