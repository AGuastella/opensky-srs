import azure.functions as func
import pandas as pd
import requests
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    server = 'openskysrs.database.windows.net'
    database = 'openskydb'
    username = 'CloudSA2b425ff0'
    password = 'colajanni<3'   
    driver= '{ODBC Driver 17 for SQL Server}'

    sql_merge="""
        MERGE INTO livestates t
        USING (VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)) AS v (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,geoaltitude,onground,velocity,truetrack,verticalrate,sensors,baroaltitude,squawk,spi,positionsource)
        ON t.onground = 0 AND t.icao24 = v.icao24
        -- Replace when the key exists
        WHEN MATCHED THEN
            UPDATE SET
                -- t."time" = v."time", -- Is not necessary to update the time, since is only referred at the last update's timestamp
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

    sql_update_to_inactive="""
        UPDATE livestates
        SET
            onground = 1
        WHERE icao24 = ?;
    """

    r = requests.get('https://opensky-network.org/api/states/all?lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232')
    j = r.json()
    states = j['states']
    t = j['time']
    df = pd.DataFrame(j)
    list_of_lists = df.apply(lambda row: [row['time']] + row['states'], axis=1).tolist()

    on_air = [l for l in list_of_lists if not l[9]]
    on_ground = [[l[1]] for l in list_of_lists if l[9]]

    
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.fast_executemany = True
            
            # MERGE+INSERT: update delle info dei voli ATTIVI
            cursor.executemany(sql_merge, on_air)
            cursor.commit()
            
            # UPDATE voli attivi. Un volo diventa non attivo se:
            # - passa allo stato unground
            if len(on_ground) > 0:
                cursor.executemany(sql_update_to_inactive, on_ground)
                cursor.commit()

            #cursor.executemany(sql_passing_onground)
            #cursor.commit()

            conn.commit()
             
        
  
    return func.HttpResponse(states[7][0])
    
