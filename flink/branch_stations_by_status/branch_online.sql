INSERT INTO station_online
SELECT CAST(station.station_id AS STRING), 
       station.name, 
       station.lat, 
       station.lon, 
       station.capacity, 
       station.num_bikes_available, 
       station.num_bikes_available * 1.0 / station.capacity as availability_ratio,
       last_updated, 
       ttl 
FROM station_status 
WHERE station.is_renting;