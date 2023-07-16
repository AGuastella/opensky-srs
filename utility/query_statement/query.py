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

sql_merge_bard = """
    CREATE TABLE #temp (
    time datetime,
    icao24 char(8),
    flightcode varchar(255),
    country varchar(255),
    timeposition datetime,
    lastcontact datetime,
    longitude float,
    latitude float,
    baroaltitude int,
    onground bit,
    velocity int,
    truetrack int,
    verticalrate int,
    sensors varchar(255),
    geoaltitude int,
    squawk int,
    spi int,
    positionsource varchar(255)
    );

    MERGE INTO {table} t
        USING #temp AS v (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,geoaltitude,onground,velocity,truetrack,verticalrate,sensors,baroaltitude,squawk,spi,positionsource)
        ON t.onground = 0 AND t.icao24 = v.icao24
        -- Replace when the key exists
        WHEN MATCHED THEN
            UPDATE SET
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

    INSERT INTO #temp (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,baroaltitude,onground,velocity,truetrack,verticalrate,sensors,geoaltitude,squawk,spi,positionsource)
    SELECT ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?;

    DROP TABLE #temp;

"""

sql_merge_bard_chat = """
    SELECT
  t.time,
  t.icao24,
  t.flightcode,
  t.country,
  t.timeposition,
  t.lastcontact,
  t.longitude,
  t.latitude,
  t.baroaltitude,
  t.onground,
  t.velocity,
  t.truetrack,
  t.verticalrate,
  t.sensors,
  t.geoaltitude,
  t.squawk,
  t.spi,
  t.positionsource,
  v.country AS new_country,
  v.flightcode AS new_flightcode,
  v.timeposition AS new_timeposition,
  v.baroaltitude AS new_baroaltitude,
  v.velocity AS new_velocity,
  v.truetrack AS new_truetrack,
  v.verticalrate AS new_verticalrate,
  v.sensors AS new_sensors,
  v.geoaltitude AS new_geoaltitude,
  v.squawk AS new_squawk,
  v.spi AS new_spi,
  v.positionsource AS new_positionsource,
  t.distance + geography::Point(t.latitude, t.longitude, 4326).STDistance(geography::Point(v.latitude, v.longitude, 4326)) AS distance
  FROM {table} t
    LEFT JOIN (
    SELECT
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    FROM (VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)) AS v (time,icao24,flightcode,country,timeposition,lastcontact,longitude,latitude,baroaltitude,onground,velocity,truetrack,verticalrate,sensors,geoaltitude,squawk,spi,positionsource)
    ) v ON t.onground = 0 AND t.icao24 = v.icao24
ORDER BY t.time;
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
select_active_flights="""
            SELECT * FROM livestates WHERE onground=0
        """
distance_query="""
            SELECT SUM(DISTANCE) FROM livestates where lastcontact > DATEDIFF(s, '1970-01-01', GETUTCDATE()) - 86400;
        """