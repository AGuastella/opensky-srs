import azure.functions as func
#from opensky_api import OpenSkyApi
import pandas as pd
import requests
import pyodbc
import json
#from sqlalchemy import create_engine

import pandas
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    server = 'openskysrs.database.windows.net'
    database = 'openskydb'
    username = 'CloudSA2b425ff0'
    password = 'colajanni<3'   
    driver= '{ODBC Driver 17 for SQL Server}'


    
    r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232')
    j= r.json()
    states=j['states']
    t=j['time']
    df=pd.DataFrame(j)
    list_of_lists = df.apply(lambda row: [row['time']] + row['states'], axis=1).tolist()
    sql_statement1="""
    INSERT INTO liveinfo (time,icao24,flightcode,country,timeposition,
    lastcontact,longitude,latitude,
    baroaltitude,onground,velocity,truetrack,verticalrate,sensors,
    geoaltitude,squawk,spi,positionsource) 
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    sql="""INSERT INTO figa VALUES (?,?)"""
    
    sql_statement="""
    MERGE INTO liveinfo t
USING (VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)) AS v (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,geoaltitude,onground,velocity,truetrack,verticalrate,sensors,baroaltitude,squawk,spi,positionsource)
ON t.icao24 = v.icao24
-- Replace when the key exists
WHEN MATCHED THEN
    UPDATE SET
        t."time" = v."time",
        t.country=v.country,
        t.flightcode=v.flightcode,
        t.timeposition=v.timeposition,
        t.baroaltitude=v.baroaltitude,
        t.velocity=v.velocity,
        t.verticalrate=v.verticalrate,
        t.truetrack=v.truetrack,
        t.sensors=v.sensors,
        t.geoaltitude=v.geoaltitude,
        t.squawk=v.squawk,
        t.positionsource=v.positionsource,
        t.lastcontact=v.lastcontact,
		t.latitude=v.latitude,
		t.longitude=v.longitude,
		t.onground=v.onground,
		t.spi=v.spi,
		t.distance=t.distance+geography::Point(t.latitude, t.longitude, 4326).STDistance(geography::Point(v.latitude, v.longitude, 4326))
-- Insert new keys
WHEN NOT MATCHED THEN
    INSERT (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,baroaltitude,onground,velocity,truetrack,verticalrate,sensors,geoaltitude,squawk,spi,positionsource)
    VALUES (v."time",v.icao24,v.flightcode,v.country,v.timeposition,v.lastcontact,v.longitude,v.latitude,v.baroaltitude,v.onground,v.velocity,v.truetrack,v.verticalrate,v.sensors,v.geoaltitude,v.squawk,v.spi,v.positionsource);

    """
    
    
    
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
#           cursor.execute(sql_statement1,t,states[2][0],states[1][1],states[1][2],states[1][3],states[1][4],float(states[1][5]),
#                           float(states[1][6]),float(states[1][7]),str(states[1][8]).lower(),float(states[1][9]),float(states[1][10]),
#                           float(states[1][11]),states[1][12],float(states[1][13]),states[1][14],
#                           str(states[1][15]).lower(),states[1][16])
#            for state in states:
#                cursor.execute(sql_statement,t,state[0],state[1],state[2],state[3],state[4],state[5],
#                state[6],state[7],str(state[8]).lower(),state[9],state[10],
#                state[11],state[12],state[13],state[14],
#                str(state[15]).lower(),state[16])
             #cursor.execute(sql,1,False)
             cursor.fast_executemany = True
             cursor.executemany(sql_statement, list_of_lists)
             cursor.commit()
             conn.commit()
             
        
  
    return func.HttpResponse(states[7][0])
    
