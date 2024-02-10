#!/usr/bin/python3.8
# -*- encoding: utf-8 -*-
"""
This module implements a class that establishes connection with GA Search Console
"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_search_console_service(secret_string):
    credentials = json.loads(secret_string)
    
    # Authenticate with Google Search Console
    credentials = service_account.Credentials.from_service_account_info(
        credentials, scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )
    
    # Create a Google Search Console service
    search_console_service = build('webmasters', 'v3', credentials=credentials)
    print("build success for ga console")
    return search_console_service

        