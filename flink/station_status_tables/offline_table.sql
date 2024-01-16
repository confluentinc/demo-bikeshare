CREATE TABLE station_offline (
  id STRING NOT NULL,
  name STRING NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  last_updated BIGINT NOT NULL,
  ttl BIGINT NOT NULL
);