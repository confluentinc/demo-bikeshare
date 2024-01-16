INSERT INTO station_offline
SELECT CAST(station.station_id AS STRING),
       station.name, 
       station.lat, 
       station.lon, 
       last_updated, 
       ttl 
FROM station_status 
WHERE NOT station.is_renting;