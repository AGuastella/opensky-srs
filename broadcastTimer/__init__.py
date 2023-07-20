import datetime
import logging

import azure.functions as func
import os
import json
import pyodbc
import pandas as pd
from utility.query_statement import query as q

server = 'openskysrs.database.windows.net'
database = 'openskydb'  
driver= '{ODBC Driver 17 for SQL Server}'

def main(mytimer: func.TimerRequest,signalRMessages: func.Out[str]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    try:
        username=os.getenv('Dbuser')
        password=os.getenv('Dbpass')
        print('STO A FA LA BRODCAST!!!!!!!')

        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                result_distance=cursor.execute(q.distance_query)
                distance=result_distance.fetchval()
            data = pd.read_sql(q.select_active_flights,conn).values.tolist()        
        
        data.append(distance)
        
        
        signalRMessages.set(json.dumps({
        'target': 'newMessage',
            'arguments': [data]
            }))
    except: 
        print("Impossibile reperire credenziali di accesso al db dal vault")
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
