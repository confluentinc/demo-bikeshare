terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
    }
    random = {
      source  = "hashicorp/random"
    }
  }
}

provider "confluent" {
    cloud_api_key = var.cc_api_key
    cloud_api_secret = var.cc_api_secret
}

## the theory is that with creating a new name each time we won't encounter as many errors during development
resource "random_pet" "env_name" {
}

resource "confluent_environment" "env" {
  display_name = "demo-bikeshare-${random_pet.env_name.id}"
}

data "confluent_schema_registry_region" "region" {
  cloud   = var.cloud
  region  = var.region
  package = var.sr_package
}

resource "confluent_service_account" "sa" {
  display_name = "demo-bikeshare-${random_pet.env_name.id}-service-account"
  description  = "Service account for the demo bikeshare application"
}

resource "confluent_role_binding" "rb" {
  principal   = "User:${confluent_service_account.sa.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.kafka.rbac_crn
}

resource "confluent_schema_registry_cluster" "sr" {
  package = var.sr_package

  environment {
    id = confluent_environment.env.id
  }

  region {
    id = data.confluent_schema_registry_region.region.id
  }
}

resource "confluent_api_key" "sr" {
  display_name = "schema-registry-api-key"
  description  = "Schema Registry API Key used for the bikeshare demo"
  owner {
    id          = confluent_service_account.sa.id
    api_version = confluent_service_account.sa.api_version
    kind        = confluent_service_account.sa.kind
  }

  managed_resource {
    id          = confluent_schema_registry_cluster.sr.id
    api_version = confluent_schema_registry_cluster.sr.api_version
    kind        = confluent_schema_registry_cluster.sr.kind

    environment {
      id = confluent_environment.env.id
    }
  }
}

resource "confluent_kafka_cluster" "kafka" {
  display_name = var.kafka_cluster_name
  availability = "SINGLE_ZONE"
  cloud        = var.cloud
  region       = var.region
  basic {}

  environment {
    id = confluent_environment.env.id
  }
}

resource "confluent_api_key" "kafka" {
  display_name = "kafka-api-key"
  description  = "Kafka API Key used for the bikeshare demo"
  owner {
    id          = confluent_service_account.sa.id
    api_version = confluent_service_account.sa.api_version
    kind        = confluent_service_account.sa.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.kafka.id
    api_version = confluent_kafka_cluster.kafka.api_version
    kind        = confluent_kafka_cluster.kafka.kind

    environment {
      id = confluent_environment.env.id
    }
  }
}

resource "confluent_flink_compute_pool" "flink" {
  display_name = var.flink_cluster_name
  cloud        = var.cloud
  region       = var.region
  max_cfu      = 5
  environment {
    id = confluent_environment.env.id
  }
}