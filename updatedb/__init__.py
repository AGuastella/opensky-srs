# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import azure.functions as func
import pandas as pd
import pyodbc
import time
from utility.italianairspace import italianairspace as it
from utility.query_statement import query as q

server = 'openskysrs.database.windows.net'
database = 'openskydb'
username = 'CloudSA2b425ff0'
password = 'colajanni<3'   
driver= '{ODBC Driver 17 for SQL Server}'

def main(j: dict) -> str:
    
    df = pd.DataFrame(j)
    #print(df)
    list_of_lists = df.apply(lambda row: [int(time.time())] + row['states'], axis=1).tolist()

    on_air = [l for l in list_of_lists if not l[9] and it.is_in_italian_airspace(l[7], l[6])]
    on_ground = [[l[1]] for l in list_of_lists if l[9] and it.is_in_italian_airspace(l[7], l[6])]
   
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password,autocommit=True) as conn:
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
        #print("Ioooooooo")
        
        return "ok"