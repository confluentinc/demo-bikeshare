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
