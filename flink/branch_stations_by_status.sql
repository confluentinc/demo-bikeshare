CREATE TABLE station_online (
  id STRING NOT NULL,
  name STRING NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  capacity BIGINT,
  num_bikes_available BIGINT,
  availability_ratio DOUBLE,
  last_updated BIGINT NOT NULL,
  ttl BIGINT NOT NULL
);

CREATE TABLE station_offline (
  id STRING NOT NULL,
  name STRING NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  last_updated BIGINT NOT NULL,
  ttl BIGINT NOT NULL
);


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

INSERT INTO station_offline
SELECT CAST(station.station_id AS STRING),
       station.name, 
       station.lat, 
       station.lon, 
       last_updated, 
       ttl 
FROM station_status 
WHERE NOT station.is_renting;




