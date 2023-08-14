import json
import utils

conn = utils.connect_postgres()

cur = conn.cursor()

def create_table():

    for table in ['arrival', 'departure']:
        cmd = """
                CREATE TABLE IF NOT EXISTS {table} (
                    flight_number VARCHAR(20) NOT NULL,
                    standard_time TIMESTAMP NOT NULL,
                    estimated_time JSONB NOT NULL,
                    location VARCHAR(30) NOT NULL,
                    airline varchar(30) NOT NULL,
                    international BOOLEAN NOT NULL,
                    flight_status JSONB NOT NULL,
                    PRIMARY KEY(flight_number, standard_time)
                )
            """.format(table=table)
        
        cur.execute(cmd)
        
        conn.commit()



def put_data(data, table):

    create_table()

    query = """
        INSERT INTO {table}(
            flight_number,
            standard_time,
            estimated_time,
            location,
            airline,
            international,
            flight_status
        )

        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (flight_number, standard_time) DO UPDATE
        SET flight_status = CASE
        WHEN excluded.flight_status->0->>'status' = {table}.flight_status->json_array_length({table}.flight_status::json)-1->>'status'
        THEN {table}.flight_status
        ELSE jsonb_concat({table}.flight_status, excluded.flight_status)
        END,
        estimated_time = CASE
        WHEN excluded.estimated_time->0->>'time' = {table}.estimated_time->json_array_length({table}.estimated_time::json)-1->>'time'
        THEN {table}.estimated_time
        ELSE jsonb_concat({table}.estimated_time, excluded.estimated_time)

        END;
        """.format(table=table)
    
    for i in range(len(data)):
        num = data.iloc[i]['FlightNumber']
        sta = data.iloc[i]['STASTD_DATE']
        stat = data.iloc[i]['FlightStatus']
        eta = data.iloc[i]['ETAETD_date']
        ori = data.iloc[i]['OrigDest']
        air = data.iloc[i]['Airline']
        intd = data.iloc[i]['IntDom']
    
        cur.execute(query, (num, sta, json.dumps(eta.tolist()), ori, air, bool(intd), json.dumps(stat.tolist())))

    conn.commit()

def main(**kwargs):
    data = kwargs['ti'].xcom_pull(task_ids='transform')

    arrival = data['arrival']
    departure = data['departure']

    put_data(arrival, 'arrival')
    put_data(departure, 'departure')

    conn.close()