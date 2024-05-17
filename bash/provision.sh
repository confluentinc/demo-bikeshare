#! /bin/bash

TERRAFORM_MAX_RETRIES=3 
TERRAFORM_RETRY_INTERVAL=30

cd terraform
terraform init

attempt=1
while true; do
    echo "Attempt $attempt"
    terraform apply -auto-approve
    if [ $? -eq 0 ]; then
        break
    fi
    if [ $attempt -eq $TERRAFORM_MAX_RETRIES ]; then
        echo "Max attempts reached. Exiting..."
        exit 1
    fi
    echo "Command failed. Retrying in $(($attempt * $TERRAFORM_RETRY_INTERVAL)) seconds..."
    sleep $(($attempt * TERRAFORM_RETRY_INTERVAL))
    attempt=$(($attempt + 1))
done

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