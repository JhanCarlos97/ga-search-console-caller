import os
import json
import csv
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import date as dt, timedelta, datetime
from handlers.connector import get_search_console_service
from handlers import notifier
import pandas as pd
import io


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_S3_CLIENT = boto3.client("s3")
_KEY_NAME = os.environ["KEY_NAME"]
_RUN_FLAG_HISTORICAL_DATASET = os.environ["RUN_FLAG_HISTORICAL_DATASET"]
_START_DATE_HISTORICAL_DATASET = os.environ["START_DATE_HISTORICAL_DATASET"]
_END_DATE_HISTORICAL_DATASET = os.environ["END_DATE_HISTORICAL_DATASET"]
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


def iterate_dates(start_date, end_date):
    date_format = "%Y-%m-%d"
    current_date = datetime.strptime(start_date, date_format)
    end_date = datetime.strptime(end_date, date_format)

    while current_date <= end_date:
        extract_data(current_date.strftime(date_format))
        current_date += timedelta(days=1)
    return True


def extract_data(current_date):
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
        column_names = ['Site Name', 'Current Date', 'Site URL', 'Clicks', 'Impressions', 'CTR', 'Position']

        for site in list_of_sites:
            

            site_to_notify = site_to_notify + site
            site_name_formatted = site[10:]
            logger.info("Querying data for search console...")
            logger.info("Calling %s data for %s", current_date, site_name_formatted)
            response = search_console_service.searchanalytics().query(
                siteUrl=site,
                body={
                    'startDate': current_date,
                    'endDate': current_date,
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
                    csv_data.append([site_name_formatted,current_date,site_url,clicks,impressions,ctr,position])

                # Create dataframe
                df = pd.DataFrame(csv_data, columns=column_names)
                
        
                logger.info(f"Processing {_KEY_NAME} data")
        
                # Process the response and extract data
                year_month_day = current_date.replace("-","_")
        
                s3_bucket = _BUCKET_NAME
                s3_key = f'{_KEY_NAME}/{year_month_day}_data.parquet'
        
                logger.info(f"Saving data for {_KEY_NAME} data")
    

                # Write DataFrame to BytesIO object
                parquet_buffer = io.BytesIO()
                df.to_parquet(parquet_buffer, engine='pyarrow')
            
                # Reset buffer position to the beginning
                parquet_buffer.seek(0)
            
                # Upload BytesIO object to S3
                
                s3_client = boto3.client('s3')
                s3_client.upload_fileobj(parquet_buffer, s3_bucket, s3_key)

            else:
                logger.info(f"No data available yet for {current_date}")
        
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
    print(_RUN_FLAG_HISTORICAL_DATASET)
    if _RUN_FLAG_HISTORICAL_DATASET == 'True' :
        iterate_dates(_START_DATE_HISTORICAL_DATASET,_END_DATE_HISTORICAL_DATASET)
    else :
        _yesterday_date = str(dt.today() - timedelta(days=1))
        return extract_data(_yesterday_date)
    