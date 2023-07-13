import azure.functions as func
import pandas as pd
import requests
import pyodbc

from utility.italianairspace import italianairspace as it
from utility.query_statement import query as q

server = 'openskysrs.database.windows.net'
database = 'openskydb'
username = 'CloudSA2b425ff0'
password = 'colajanni<3'   
driver= '{ODBC Driver 17 for SQL Server}'

def main(req: func.HttpRequest) -> func.HttpResponse:

    r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232')
    j = r.json()
    states = j['states']
    t = j['time']
    df = pd.DataFrame(j)

    list_of_lists = df.apply(lambda row: [row['time']] + row['states'], axis=1).tolist()

    on_air = [l for l in list_of_lists if not l[9] and it.is_in_italian_airspace(l[7], l[6])]
    on_ground = [[l[1]] for l in list_of_lists if l[9] and it.is_in_italian_airspace(l[7], l[6])]
   
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.fast_executemany = True
            
            # MERGE+INSERT: update delle info dei voli ATTIVI
            cursor.executemany(q.sql_merge, on_air)
            cursor.commit()
            
            # UPDATE voli attivi. Un volo diventa non attivo se:
            # - passa allo stato unground
            if len(on_ground) > 0:
                cursor.executemany(q.sql_update_to_landed, on_ground)
                cursor.commit()

            cursor.execute(q.sql_update_to_inactive)
            cursor.commit()

            conn.commit()
             
        
  
    return func.HttpResponse(states[7][0])
    