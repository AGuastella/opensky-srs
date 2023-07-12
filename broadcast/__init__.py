import requests
import json
import pyodbc
import azure.functions as func
import pandas as pd
def main(req: func.HttpRequest,signalRMessages: func.Out[str]) -> func.HttpResponse:

    server = 'openskysrs.database.windows.net'
    database = 'openskydb'
    username = 'CloudSA2b425ff0'
    password = 'colajanni<3'   
    driver= '{ODBC Driver 17 for SQL Server}'
    select_query="""
SELECT * FROM livestates WHERE onground=0
"""
    distance_query="""
SELECT SUM(DISTANCE) FROM LIVEINFO
"""
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        #with conn.cursor() as cursor:
           # result_records=cursor.execute(select_query)
           # result_distance=cursor.execute(distance_query)
            #df=pd.DataFrame(result_records.fetchall()).values.tolist()
           # distance=result_distance.fetchval()
           
           data = pd.read_sql(select_query,conn).values.tolist()
           with conn.cursor() as cursor:
             result_distance=cursor.execute(distance_query)
             distance=result_distance.fetchval()
        
    #signalRMessages.set(json.dumps({
    #   'target': 'newMessage',
    #    'arguments': [ str(5) ]
    #    }))
    
#    for flight in data:
#        print(flight[0])
#        print(type(flight[0]))
#        signalRMessages.set(json.dumps({
#       'target': 'newMessage',
#        'arguments': [flight]
#        }))
    type(distance)
    data.append(distance)
    signalRMessages.set(json.dumps({
       'target': 'newMessage',
        'arguments': [data]
        }))
    #signalRMessages.set(json.dumps({
    #   'target': 'newDistance',
    #    'arguments': [str(distance)]
    #    }))
     #   signalRMessages.set(json.dumps({
     #  'target': 'newMessage',
     #   'arguments': [{
     #       'data':[data],
     #       'distance':distance}]
     #   }))
    print("done")    
    #return func.HttpResponse("DONE")
