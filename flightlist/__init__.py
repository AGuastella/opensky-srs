import json
import math
import pyodbc
import azure.functions as func
import pandas as pd
import azure.functions as func
import os
from utility.query_statement import query as q

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    server = 'openskysrs.database.windows.net'
    database = 'openskydb'
    driver= '{ODBC Driver 17 for SQL Server}'

    try:
        username=os.getenv('Dbuser')
        password=os.getenv('Dbpass')


        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:

            
            data = pd.read_sql(q.select_active_flights,conn).values.tolist()
            with conn.cursor() as cursor:
                result_distance=cursor.execute(q.distance_query)
                distance=result_distance.fetchval()
            

        # Replace NaN values with null
        #data_with_null = [[v if not (isinstance(v, float) and math.isnan(v)) else None for v in sublist] for sublist in data]

        data_with_null = [[None if (isinstance(v, float) and math.isnan(v)) else v for v in sublist] for sublist in data]
        data_with_null.append(distance)
        # Convert data to JSON
        json_data = json.dumps(data_with_null)

        # Return JSON response
    
    except:
        print("Impossibile reperire credenziali di accesso al db dal vault")
        json_data= json.dumps([0])
    
    return func.HttpResponse(body=json_data, mimetype="application/json")
    
    '''return func.HttpResponse(
        body=json.dumps(data, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x),
        mimetype="application/json"

    )'''