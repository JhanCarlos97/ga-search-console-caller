#!/usr/bin/python3.8
# -*- encoding: utf-8 -*-
"""
This module implements a class that establishes connection with GA Search Console
"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_analytics_service(secret_string):
    # Set up credentials
    credentials_dict = json.loads(secret_string)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    
    #local run
    #credentials = Credentials.from_service_account_file('google_api.json')
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']

    # Set up the API client
    ga4_client = build('analyticsdata', 'v1beta', credentials=credentials)
    print("Build success for Google Analytics")
    return ga4_client