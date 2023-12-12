CREATE TABLE $TABLE_NAME (
    last_updated BIGINT NOT NULL,
    station ROW<
        num_bikes_disabled BIGINT,
        num_docks_available BIGINT,
        is_installed BOOLEAN NOT NULL,
        vehicle_types_available ARRAY<
            ROW<vehicle_type_id STRING NOT NULL, `count` BIGINT NOT NULL> NOT NULL
        > NOT NULL,
        is_returning BOOLEAN NOT NULL,
        vehicle_docks_available ARRAY<
            ROW<vehicle_type_ids ARRAY<STRING NOT NULL> NOT NULL, `count` BIGINT NOT NULL> NOT NULL
        > NOT NULL,
        num_bikes_available BIGINT NOT NULL,
        is_renting BOOLEAN NOT NULL,
        station_id STRING NOT NULL,
        last_reported BIGINT NOT NULL,
        num_docks_disabled BIGINT
    > NOT NULL,
    ttl BIGINT NOT NULL,
    version STRING NOT NULL
);

