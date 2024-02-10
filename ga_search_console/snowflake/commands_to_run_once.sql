-----------------------------------------GA DEV ENVIRONMENT----------------------------------------------
USE ROLE ACCOUNTADMIN;

USE DATABASE GA_DEV_DATABASE;
CREATE SCHEMA IF NOT EXISTS GASEARCHCONSOLE;
grant ownership on SCHEMA GASEARCHCONSOLE to role GA_DEV_ROLE revoke current grants;
USE SCHEMA GASEARCHCONSOLE;
CREATE or replace FILE FORMAT csv_format
type = csv
field_delimiter = ','
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
ESCAPE_UNENCLOSED_FIELD=NONE;

--NEXT TWO LINES NEEDS TO BE RUN WITH ACCOUNTADMIN ROLE

CREATE OR REPLACE STORAGE INTEGRATION GASEARCHCONSOLE_DEV_S3_INTEGRATION
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = S3
ENABLED = TRUE
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::aws_account:role/company-ga-search-console-dev-snowflake-role'
STORAGE_ALLOWED_LOCATIONS = ('s3://company-ga-search-console-dev-data/')
COMMENT = 'GA Search Console Data Storage Integration w/ S3 dev bucket';
grant ownership on INTEGRATION GASEARCHCONSOLE_DEV_S3_INTEGRATION to role GA_DEV_ROLE;

--NEXT COMMAND IS USED TO COPY STORAGE_AWS_IAM_USER_ARN AND STORAGE_AWS_EXTERNAL_ID
--INTO TRUST POLICY OF company-ga-search-console-dev-snowflake-role ROLE IN IAM
DESC INTEGRATION GASEARCHCONSOLE_DEV_S3_INTEGRATION;

CREATE OR REPLACE STAGE GASEARCHCONSOLE_DEV_STAGE
URL="s3://company-ga-search-console-dev-data/"
STORAGE_INTEGRATION = GASEARCHCONSOLE_DEV_S3_INTEGRATION
FILE_FORMAT=csv_format;

LIST @GASEARCHCONSOLE_DEV_STAGE;

--USING HISTORICAL DATA, WE CREATED THE TABLE. THIS IS, WE RUN THE PIECE OF CODE THAT GRABS HISTORICAL INFO, UP TO 4 DAYS BACK
create table RAW_GASEARCHCONSOLE (
SITE,
DATE,
QUERY,
CLICKS,
IMPRESSIONS,
CTR,
POSITION
) AS
select
$1 as site,
$2 as date,
$3 as query,
$4 as clicks,
$5 as impressions,
$6 as ctr,
$7 as position
from @GASEARCHCONSOLE_DEV_STAGE;

--NEXT COMMAND IS USED IN ORDER TO MODIFY SNS TOPIC AND ADD "Statement" KEY CONTENT IN SNS TOPIC DEFINITION
--IN ORDER TO ALLOW THE SNOWPIPE CREATIONS
select system$get_aws_sns_iam_policy('arn:aws:sns:us-east-1:aws_account:gasearchconsolesns');

--Create the Snowpipe
CREATE OR REPLACE PIPE GASEARCHCONSOLE_S3_RAW
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:aws_account:gasearchconsolesns'
AS
COPY INTO RAW_GASEARCHCONSOLE
FROM (
select
    $1 as site,
    $2 as date,
    $3 as query,
    $4 as clicks,
    $5 as impressions,
    $6 as ctr,
    $7 as position
from @GASEARCHCONSOLE_DEV_STAGE
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

grant USAGE on INTEGRATION GASEARCHCONSOLE_DEV_S3_INTEGRATION to role GA_STG_ROLE;
grant USAGE on INTEGRATION GASEARCHCONSOLE_DEV_S3_INTEGRATION to role GA_PROD_ROLE;

--FOR STAGE WE WILL RUN THIS COMMANDS ONLY ONCE:

USE role GA_STG_ROLE;
USE DATABASE GA_STG_DATABASE;
CREATE SCHEMA IF NOT EXISTS GASEARCHCONSOLE;
USE SCHEMA GASEARCHCONSOLE;
CREATE or replace FILE FORMAT csv_format
type = csv
field_delimiter = ','
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
ESCAPE_UNENCLOSED_FIELD=NONE;

CREATE OR REPLACE STAGE GASEARCHCONSOLE_STG_STAGE
URL="s3://company-ga-search-console-dev-data/"
STORAGE_INTEGRATION = GASEARCHCONSOLE_DEV_S3_INTEGRATION
FILE_FORMAT=csv_format;

create table RAW_GASEARCHCONSOLE (
SITE,
DATE,
QUERY,
CLICKS,
IMPRESSIONS,
CTR,
POSITION
) AS
select
$1 as site,
$2 as date,
$3 as query,
$4 as clicks,
$5 as impressions,
$6 as ctr,
$7 as position
from @GASEARCHCONSOLE_STG_STAGE;

CREATE OR REPLACE PIPE GASEARCHCONSOLE_S3_RAW
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:aws_account:gasearchconsolesns'
AS
COPY INTO RAW_GASEARCHCONSOLE
FROM (
select
    $1 as site,
    $2 as date,
    $3 as query,
    $4 as clicks,
    $5 as impressions,
    $6 as ctr,
    $7 as position
from @GASEARCHCONSOLE_STG_STAGE
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

--FOR PROD WE WILL RUN THIS COMMANDS ONLY ONCE:

USE role GA_PROD_ROLE;
USE DATABASE GA_PROD_DATABASE;
CREATE SCHEMA IF NOT EXISTS GASEARCHCONSOLE;
USE SCHEMA GASEARCHCONSOLE;
CREATE or replace FILE FORMAT csv_format
type = csv
field_delimiter = ','
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
ESCAPE_UNENCLOSED_FIELD=NONE;

CREATE OR REPLACE STAGE GASEARCHCONSOLE_PROD_STAGE
URL="s3://company-ga-search-console-dev-data/"
STORAGE_INTEGRATION = GASEARCHCONSOLE_DEV_S3_INTEGRATION
FILE_FORMAT=csv_format;

create table RAW_GASEARCHCONSOLE (
SITE,
DATE,
QUERY,
CLICKS,
IMPRESSIONS,
CTR,
POSITION
) AS
select
$1 as site,
$2 as date,
$3 as query,
$4 as clicks,
$5 as impressions,
$6 as ctr,
$7 as position
from @GASEARCHCONSOLE_PROD_STAGE;

CREATE OR REPLACE PIPE GASEARCHCONSOLE_S3_RAW
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:aws_account:gasearchconsolesns'
AS
COPY INTO RAW_GASEARCHCONSOLE
FROM (
select
    $1 as site,
    $2 as date,
    $3 as query,
    $4 as clicks,
    $5 as impressions,
    $6 as ctr,
    $7 as position
from @GASEARCHCONSOLE_PROD_STAGE
)
FILE_FORMAT=(FORMAT_NAME=csv_format);
