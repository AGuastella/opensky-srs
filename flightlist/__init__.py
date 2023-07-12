import json
import math
import pyodbc
import azure.functions as func
import pandas as pd
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    server = 'openskysrs.database.windows.net'
    database = 'openskydb'
    username = 'CloudSA2b425ff0'
    password = 'colajanni<3'   
    driver= '{ODBC Driver 17 for SQL Server}'
    select_query="""
SELECT * FROM liveinfo
"""
    distance_query="""
SELECT SUM(DISTANCE) FROM LIVEINFO
"""
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:

           
           data = pd.read_sql(select_query,conn).values.tolist()
           with conn.cursor() as cursor:
             result_distance=cursor.execute(distance_query)
             distance=result_distance.fetchval()
        

    # Replace NaN values with null
    #data_with_null = [[v if not (isinstance(v, float) and math.isnan(v)) else None for v in sublist] for sublist in data]

    data_with_null = [[None if (isinstance(v, float) and math.isnan(v)) else v for v in sublist] for sublist in data]
    data_with_null.append(distance)
    # Convert data to JSON
    json_data = json.dumps(data_with_null)

    # Return JSON response
    return func.HttpResponse(body=json_data, mimetype="application/json")
    
    '''return func.HttpResponse(
        body=json.dumps(data, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x),
        mimetype="application/json"

    )'''