#! /bin/bash

cd ../terraform
terraform init
terraform apply -auto-approve

export CC_ENV=$(terraform output -json | jq -r .environment.value.id)
export KAFKA_CLUSTER=$(terraform output -json | jq -r .kafka_cluster.value.display_name)
export FLINK_POOL=$(terraform output -json | jq -r .flink_pool.value.id)

## check to see if we need to login
cd ../flink
output="$(confluent --help 2>&1)" # Redirects stderr to stdout
if ! echo "$output" | grep -q "flink"; then
    confluent login --no-browser
fi

confluent environment use $CC_ENV
confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql "$(cat station_status_tables/online_table.sql | tr -d '\n' | xargs)"
confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql="$(cat station_status_tables/offline_table.sql | tr -d '\n' | xargs)"