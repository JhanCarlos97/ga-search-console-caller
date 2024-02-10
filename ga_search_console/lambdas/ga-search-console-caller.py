import os
import json
import csv
import boto3
import logging
from io import StringIO
from botocore.exceptions import ClientError
from datetime import date as dt, timedelta, datetime
from handlers.connector import get_search_console_service
from handlers import notifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_S3_CLIENT = boto3.client("s3")
_BUCKET_NAME = os.environ["BUCKET_NAME"]
_SESSION = boto3.Session(region_name='us-east-1')
_SECRET_MANAGER_NAME = os.environ["SECRET_MANAGER_NAME"]
_ENV = os.environ["ENV"]

def get_credentials():
    # Retrieve the JSON credentials from Secrets Manager
    # Create a Secrets Manager client
    client = _SESSION.client(
        service_name='secretsmanager',
        region_name="us-east-1"
    )
    logger.info("Calling the secret %s", _SECRET_MANAGER_NAME)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=_SECRET_MANAGER_NAME
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response["SecretString"])["credentials_json"]

    return secret

def date_range_list(start_date, end_date):
    # Return generator for a list of dates (inclusive) between start_date and end_date (inclusive).
    # use it only to retrieve older data you don't have
    date_list = []
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date.strftime("%Y-%m-%d"))
        curr_date += timedelta(days=1)
    return date_list

def extract_data():
    try:
        notifier_message = ""
        site_to_notify = ""
        logger.info("Getting credentials")
        # Get Google Search Console credentials
        credentials = get_credentials()
        logger.info("Secrets for GA search Console grabbed")
        logger.info("Using GA search Console credentials to connect")
        # Create a Google Search Console service
        search_console_service = get_search_console_service(credentials)
        logger.info("GA search console service initiated")

        #Get sites URL to connect
        sites = search_console_service.sites().list().execute()
        logger.info("Sites URL retrieved")
        #Saving sites as list
        list_of_sites = [entry['siteUrl'] for entry in sites['siteEntry'] if entry['siteUrl'].startswith('sc-domain:')]
        # list_of_sites = ['define_here_site'] use this line if you want to run a specific one and change the start_date if needed

        for site in list_of_sites:
            
            _yesterday_date = str(dt.today() - timedelta(days=3))

            # USE THIS PIECE OF CODE IN CASE YOU WANT TO RETRIEVE MORE INFORMATION FOR A SPECIFIC SITE BY CHANGING START_DATE
            # start_date = "2023-01-01"
            # date_list = date_range_list(start_date,_yesterday_date)
            # for date in date_list:
            #     print("Calling %s data for %s", date, site)
            #     site_to_notify = site_to_notify + site
            #     response = search_console_service.searchanalytics().query(
            #         siteUrl=site,
            #         body={
            #             'startDate': date,
            #             'endDate': date,
            #             'dimensions': ['query'],
            #         }
            #     ).execute()

            #     site_name_formatted = site[10:]
            #     csv_data = []
            #     if "rows" in response:
            #         print("Generating csv file")
            #         for row in response["rows"]:
            #             query = row["keys"][0]
            #             clicks = row["clicks"]
            #             impressions = row["impressions"]
            #             ctr = row["ctr"]
            #             position = row["position"]
            #             #Adding the values to the nested list
            #             csv_data.append([site_name_formatted,date,query,clicks,impressions,ctr,position])

            #         csv_buffer = StringIO()
            #         csv_writer = csv.writer(csv_buffer)
            #         csv_writer.writerows(csv_data)

            #         site_to_notify = ""
            #         print(f"Processing {site_name_formatted} data")

            #         # Process the response and extract data
            #         year_month_day = date.replace("-","/")

            #         s3_key = f'{site_name_formatted}/{year_month_day}/data.csv'

            #         print(f"Saving data for {site_name_formatted} data")
            #         # Save extracted data to S3
            #         _S3_CLIENT.put_object(
            #             Bucket=_BUCKET_NAME,
            #             Key=s3_key,
            #             Body=csv_buffer.getvalue()
            #         )
            #     else:
            #         print(f"No data available yet for {date}")
            
            site_to_notify = site_to_notify + site
            site_name_formatted = site[10:]
            logger.info("Querying data for search console...")
            logger.info("Calling %s data for %s", _yesterday_date, site_name_formatted)
            response = search_console_service.searchanalytics().query(
                siteUrl=site,
                body={
                    'startDate': _yesterday_date,
                    'endDate': _yesterday_date,
                    'dimensions': ['query'],
                }
            ).execute()

            csv_data = []
            if "rows" in response:
                logger.info("Generating csv file")
                for row in response["rows"]:
                    site_url = row["keys"][0]
                    clicks = row["clicks"]
                    impressions = row["impressions"]
                    ctr = row["ctr"]
                    position = row["position"]
                    #Adding the values to the nested list
                    csv_data.append([site_name_formatted,_yesterday_date,site_url,clicks,impressions,ctr,position])

                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerows(csv_data)

                site_to_notify = ""
                logger.info(f"Processing {site_name_formatted} data")

                # Process the response and extract data
                year_month_day = _yesterday_date.replace("-","/")

                s3_key = f'{site_name_formatted}/{year_month_day}/data.csv'

                logger.info(f"Saving data for {site_name_formatted} data")
                # Save extracted data to S3
                _S3_CLIENT.put_object(
                    Bucket=_BUCKET_NAME,
                    Key=s3_key,
                    Body=csv_buffer.getvalue()
                )
            else:
                logger.info(f"No data available yet for {_yesterday_date}")
        
        return {
            'statusCode': 200,
            'body': 'Data proccesed into S3'
        }
    except Exception as e:
        logger.info(f'Error: {str(e)}')
        if site_to_notify:
            notifier_message = f'Error processing data for {site_to_notify} at {_ENV} environment'
            notifier.notify_slack_channel(notifier_message)
        else:
            notifier_message = f'Execution error, please check most recent logs at {_ENV} account'
            notifier.notify_slack_channel(notifier_message)
        return {
            'statusCode': 500,
            'body': str(e)
        }
    
def delete_files_s3():
    #use it only to force delete of files in s3 if needed
    desired_extension = '2023/10/22/data.csv'  # Replace with your desired file extension

    objects = _S3_CLIENT.list_objects(Bucket=_BUCKET_NAME)

    for obj in objects.get('Contents', []):
        object_key = obj['Key']
        if object_key.endswith(desired_extension):
            _S3_CLIENT.delete_object(Bucket=_BUCKET_NAME, Key=object_key)
            print(f"Deleted {object_key}")

def lambda_handler(event, context):
    return extract_data()