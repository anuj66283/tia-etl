import requests
from fake_useragent import UserAgent
import json
import utils
from datetime import datetime
import pytz

#used to set nepali timezone
tz = pytz.timezone('Asia/Kathmandu')

#use a random user agent so we will not be blocked
ua = UserAgent(browsers=['edge', 'chrome']).random

#get data form url
def get_data():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.7',
        'Host': 'www.tiairport.com.np',
        'Referer': 'https://www.tiairport.com.np/all-flights',
        'User-Agent': ua
    }

    uri = 'https://www.tiairport.com.np/flight_details_2'

    a = requests.get(uri, headers=headers).json()

    #add a new key timestamp to record the time in which data was fetched
    a['timestamp'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    return a

#upload data to s3
def put_data(bucket):
    resp = json.dumps(get_data())

    f_name = utils.file_folder_name()

    utils.upload_file(f'{f_name}.json', bucket=bucket, resp=resp)