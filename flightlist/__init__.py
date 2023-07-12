import json
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
        
    #print(data[1:6])
    print(json.dumps(data[1:6]))
    #print(type(data[0][0]))
    return func.HttpResponse(
        body=json.dumps(data),
        mimetype="application/json"

    )