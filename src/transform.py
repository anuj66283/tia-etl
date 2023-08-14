import json
import pandas as pd
import utils

s3_client = utils.s_client()

def clean_data(bucket, f_name):
    data = s3_client.get_object(Bucket=bucket, Key=f_name)
    data = json.loads(data['Body'].read().decode("utf-8"))

    #get the time of extraction
    timestamp = data['timestamp']

    df1 = pd.DataFrame(data['data']['arrivals'])
    df2 = pd.DataFrame(data['data']['departure'])

    df = pd.concat([df1, df2], ignore_index=True)

    #sometimes api sends duplicate value so remove it
    df = df.drop_duplicates()
    
    #return only the files whose flightstatus is known
    return df[df['FlightStatus'].notna()], timestamp


def prevent_duplicates(bucket):

    resp = s3_client.list_objects(Bucket=bucket)

    #get list of all files in s3 bucket
    files = sorted(resp['Contents'], key=lambda obj: obj['LastModified'])


    if len(files)>1:
        #get the recently and second to last recently modifed files
        file_names = [files[-2]['Key'], files[-1]['Key']]

        past_data, past_time = clean_data(bucket, file_names[0])
        present_data, present_time = clean_data(bucket, file_names[1])

        #join data so that if any flights are in past data only are omitted
        df = past_data.merge(present_data, on='FlightNumber', how='right')

        #get the common flights as only their FlightStatus needs to be updated
        inner_join_elements = df[df.notnull().all(axis=1)]

        flight_numbers = inner_join_elements['FlightNumber']

        #change FlightStatus type to list of dictionaries
        present_data['FlightStatus'] = present_data['FlightStatus'].apply(lambda x: [{'status': x, 'timestamp': present_time}])
        present_data['ETAETD_date'] = present_data['ETAETD_date'].apply(lambda x: [{'time': x, 'timestamp': present_time}])


        past_data.set_index('FlightNumber', inplace=True)
        present_data.set_index('FlightNumber', inplace=True)


        for z in flight_numbers:
            #check if the FlightStatus of flight has been modified
            a = present_data.at[z, 'FlightStatus'][0]['status']
            b = past_data.at[z, 'FlightStatus']
            
            #if same then change the timestamp to present data to past
            if a == b:
                present_data.at[z, 'FlightStatus'][0]['timestamp'] = past_time


        present_data.reset_index(inplace=True)

    #if the data is only in receently fetched file
    else:
        file_name = files[0]['Key']
        present_data, present_time = clean_data(bucket, file_name)
        
        present_data['FlightStatus'] = present_data['FlightStatus'].apply(lambda x: [{'status': x, 'timestamp': present_time}])
        present_data['ETAETD_date'] = present_data['ETAETD_date'].apply(lambda x: [{'time': x, 'timestamp': present_time}])


    #convert 1 and 0 to True and False 
    present_data['IntDom'] = present_data['IntDom'].astype('int').astype('bool')

    return present_data

#seperate above data as arrival and departure
def sep_data(bucket):
    df = prevent_duplicates(bucket)
    departure = df[df['type']=='Departure']
    arrival = df[df['type']=='Arrival']

    arrival = arrival.drop(columns='type')
    departure = departure.drop(columns='type')
    
    #as we cannot directly pass tuples so we are passing as dict
    return {'arrival':arrival, 'departure':departure}