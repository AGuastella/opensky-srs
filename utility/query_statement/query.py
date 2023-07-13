table = "livestates"

sql_merge= f"""
    MERGE INTO {table} t
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

sql_update_to_landed= f"""
    UPDATE {table}
    SET
        onground = 1
    WHERE onground = 0 AND icao24 = ?;
"""

# query that set to inactive all the flight that aren't detected anymore, from at least 5 minutes
sql_update_to_inactive= f"""
    UPDATE {table}
    SET
        onground = 1
    WHERE onground = 0 AND lastcontact < DATEDIFF(s, '1970-01-01', GETUTCDATE()) - 300;
"""
