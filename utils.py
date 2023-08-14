import boto3
from datetime import datetime
import pytz
import os
import psycopg2

#required to set Nepal TImeezone as aws doesnot have Nepal region
tz = pytz.timezone('Asia/Kathmandu')


database = os.environ['DATABASE']
host = os.environ['HOST']
user = os.environ['DB_USER']
password = os.environ['PASSWORD']

#connect to postgres
def connect_postgres():
    conn = psycopg2.connect(database=database,
                            host=host,
                            user=user,
                            password=password,
                            port=5432
                        )
    return conn

#s3_client to conenct to s3
def s_client():
    return boto3.client("s3", region_name='us-east-1')

# Upload the received json to s3
def upload_file(file_name, bucket, resp):

    s3_client = s_client()
    
    s3_client.put_object(Bucket=bucket, Key=file_name, Body=resp)


# Make a file name based on datetime
def file_folder_name():
    curr_date = datetime.now(tz).strftime("%Y%m%d-%H%M%S")
    folder_date = datetime.now(tz).strftime("%Y-%m")

    return f'{folder_date}/{curr_date}'