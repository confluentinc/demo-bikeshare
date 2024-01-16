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

resource "confluent_schema_registry_cluster" "sr" {
  package = var.sr_package

  environment {
    id = confluent_environment.env.id
  }

  region {
    id = data.confluent_schema_registry_region.region.id
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

resource "confluent_flink_compute_pool" "flink" {
  display_name = var.flink_cluster_name
  cloud        = var.cloud
  region       = var.region
  max_cfu      = 5
  environment {
    id = confluent_environment.env.id
  }
}