CREATE TABLE station_online (
  id STRING NOT NULL,
  name STRING NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  num_docks_available BIGINT,
  num_bikes_available BIGINT,
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
SELECT station.station_id, station.name, station.lat, station.lon, station.num_docks_available, station.num_bikes_available, last_updated, ttl 
FROM station_status 
WHERE station.is_renting;

INSERT INTO station_offline
SELECT station.station_id, station.name, station.lat, station.lon, last_updated, ttl 
FROM station_status 
WHERE NOT station.is_renting;


