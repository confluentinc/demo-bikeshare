#! /bin/bash

cd ../terraform
terraform init
terraform apply -auto-approve

## pull basics
export CC_ENV=$(terraform output -json | jq -r .environment.value.id)
export KAFKA_CLUSTER=$(terraform output -json | jq -r .kafka_cluster.value.display_name)
export FLINK_POOL=$(terraform output -json | jq -r .flink_pool.value.id)
export SERVICE_ACCOUNT=$(terraform output -json | jq -r .service_account.value.id)

## pull credentials
bootstrapEndpoint=$(terraform output -json | jq -r .kafka_cluster.value.bootstrap_endpoint)
export BOOTSTRAP_SERVER=$(echo $bootstrapEndpoint | sed 's/[^:]*:\/\///')  ## strip off the protocol
export KAFKA_API_KEY=$(terraform output -json | jq -r .kafka_api_key.value.id)
export KAFKA_API_SECRET=$(terraform output -json | jq -r .kafka_api_key.value.secret)
export SCHEMA_REGISTRY_URL=$(terraform output -json | jq -r .schema_registry_cluster.value.rest_endpoint)
export SCHEMA_REGISTRY_API_KEY=$(terraform output -json | jq -r .schema_registry_api_key.value.id)
export SCHEMA_REGISTRY_API_SECRET=$(terraform output -json | jq -r .schema_registry_api_key.value.secret)

# echo "Bootstrap Server: $BOOTSTRAP_SERVER"
# echo "Kafka API Key: $KAFKA_API_KEY"
# echo "Kafka API Secret: $KAFKA_API_SECRET"
# echo "Schema Registry URL: $SCHEMA_REGISTRY_URL"
# echo "Schema Registry API Key: $SCHEMA_REGISTRY_API_KEY"
# echo "Schema Registry API Secret: $SCHEMA_REGISTRY_API_SECRET"

## fill out client properties template 
cd ..
envsubst < client.properties.template > client.properties

## check to see if we need to login
cd flink
output="$(confluent --help 2>&1)" # Redirects stderr to stdout
if ! echo "$output" | grep -q "flink"; then
    confluent login --no-browser
fi

## create flink tables
confluent environment use $CC_ENV
confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql "$(cat station_status_tables/online_table.sql | tr -d '\n' | xargs)"
confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql "$(cat station_status_tables/offline_table.sql | tr -d '\n' | xargs)"