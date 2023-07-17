# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
import json
import pyodbc
import pandas as pd
import azure.functions as func
from utility.query_statement import query as q
server = 'openskysrs.database.windows.net'
database = 'openskydb'
username = 'CloudSA2b425ff0'
password = 'colajanni<3'   
driver= '{ODBC Driver 17 for SQL Server}'
def main(nome:str,signalRMessages: func.Out[str]) -> str:
    
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
    return "ciao"

