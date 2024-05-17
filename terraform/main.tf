terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "1.67.1"
    }
    random = {
      source  = "hashicorp/random"
    }
  }
}

#########################
## Base Infrastructure ##
#########################

provider "confluent" {
    cloud_api_key = var.cc_api_key
    cloud_api_secret = var.cc_api_secret
}

data "confluent_organization" "main" {}

## env ##
## the theory is that with creating a new name each time we won't encounter as many errors during development
resource "random_pet" "env_name" {
}
resource "confluent_environment" "env" {
  display_name = "demo-bikeshare-${random_pet.env_name.id}"
}

## schema registry ##
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

## kafka ##
resource "confluent_kafka_cluster" "kafka" {
  display_name = var.kafka_cluster_name
  availability = "SINGLE_ZONE"
  cloud        = var.cloud
  region       = var.region
  standard {}

  environment {
    id = confluent_environment.env.id
  }
}

## flink ##
data "confluent_flink_region" "flink_region" {
  cloud   = var.cloud
  region  = var.region
}

resource "confluent_flink_compute_pool" "flink" {
  display_name = var.flink_cluster_name
  cloud        = var.cloud
  region       = var.region
  max_cfu      = 5
  environment {
    id = confluent_environment.env.id
  }
    depends_on = [
    confluent_role_binding.flink-statements-runner-environment-admin,
    confluent_role_binding.flink-admin-assigner,
    confluent_role_binding.flink-admin-rb,
    confluent_api_key.flink,
  ]
}

################
## API Access ##
################

## account ##
resource "confluent_service_account" "sa" {
  display_name = "demo-bikeshare-${random_pet.env_name.id}-service-account"
  description  = "Service account for the demo bikeshare application"
}

## schema registry ##
resource "confluent_role_binding" "sr" {
    principal = "User:${confluent_service_account.sa.id}"
    role_name = "ResourceOwner"
    crn_pattern = "${confluent_schema_registry_cluster.sr.resource_name}/subject=*"
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
  depends_on = [
    confluent_role_binding.sr
  ]
}

## kafka ##
resource "confluent_role_binding" "env_admin" {
  principal   = "User:${confluent_service_account.sa.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.kafka.rbac_crn
}

resource "confluent_role_binding" "kafka_cluster" {
  principal   = "User:${confluent_service_account.sa.id}"
  role_name   = "DeveloperWrite"
  crn_pattern = "${confluent_kafka_cluster.kafka.rbac_crn}/kafka=${confluent_kafka_cluster.kafka.id}"
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

## flink ##

## service account to execute a Flink statements
resource "confluent_service_account" "flink-statements-runner" {
  display_name = "${random_pet.env_name.id}-statements-runner"
  description  = "Service account for running Flink Statements in the bikeshare demo"
}

resource "confluent_role_binding" "flink-statements-runner-environment-admin" {
  principal   = "User:${confluent_service_account.flink-statements-runner.id}"
  role_name   = "EnvironmentAdmin"
  crn_pattern = confluent_environment.env.resource_name
}

## service account that owns Flink API Key
resource "confluent_service_account" "flink-admin" {
  display_name = "${random_pet.env_name.id}-flink-manager"
  description  = "Service account that has got full access to Flink resources in an environment"
}

resource "confluent_role_binding" "flink-admin-rb" {
  principal   = "User:${confluent_service_account.flink-admin.id}"
  role_name   = "FlinkAdmin"
  crn_pattern = confluent_environment.env.resource_name
}

resource "confluent_role_binding" "flink-dev-rb" {
  principal   = "User:${confluent_service_account.flink-admin.id}"
  role_name   = "FlinkDeveloper"
  crn_pattern = confluent_environment.env.resource_name
}

resource "confluent_role_binding" "flink-admin-assigner" {
  principal   = "User:${confluent_service_account.flink-admin.id}"
  role_name   = "Assigner"
  crn_pattern = "${data.confluent_organization.main.resource_name}/service-account=${confluent_service_account.flink-statements-runner.id}"
}


resource "confluent_api_key" "flink" {
  display_name = "flink-api-key"
  description  = "Flink API Key used for the Bikeshare Demo"
  owner {
    id          = confluent_service_account.flink-admin.id
    api_version = confluent_service_account.flink-admin.api_version
    kind        = confluent_service_account.flink-admin.kind
  }

  managed_resource {
    id          = data.confluent_flink_region.flink_region.id
    api_version = data.confluent_flink_region.flink_region.api_version
    kind        = data.confluent_flink_region.flink_region.kind

    environment {
      id = confluent_environment.env.id
    }
  }
  depends_on    = [
    confluent_role_binding.kafka_cluster
  ]
}


############
## Topics ##
############

resource "confluent_kafka_topic" "station_status" {
    topic_name = "station_status"
    rest_endpoint = confluent_kafka_cluster.kafka.rest_endpoint
    credentials {
        key = confluent_api_key.kafka.id
        secret = confluent_api_key.kafka.secret
    }
    kafka_cluster {
        id = confluent_kafka_cluster.kafka.id
    }
    
    ## prevents issues with deletion
    depends_on = [
      confluent_role_binding.sr,
      confluent_schema_registry_cluster.sr,
      confluent_role_binding.env_admin,
      confluent_api_key.sr
    ]
}

#############
## Schemas ##
#############

resource "confluent_schema" "station_status" {
    subject_name = "station_status"
    format = "JSON"
    schema = file("../schemas/station_status.json")
    rest_endpoint = confluent_schema_registry_cluster.sr.rest_endpoint
    credentials {
        key = confluent_api_key.sr.id
        secret = confluent_api_key.sr.secret
    }
    schema_registry_cluster {
        id = confluent_schema_registry_cluster.sr.id
    }
    depends_on = [
      confluent_kafka_topic.station_status
    ]
}

###############
## Flink SQL ##
###############

resource "confluent_flink_statement" "create_online_table" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.env.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flink.id
  }
  principal {
    id = confluent_service_account.flink-statements-runner.id
  }
  properties = {
    "sql.current-catalog"  = confluent_environment.env.display_name
    "sql.current-database" = confluent_kafka_cluster.kafka.display_name
  }
  statement     = file("../flink/station_status_tables/online_table.sql")
  rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.flink.id
    secret = confluent_api_key.flink.secret
  }
}

resource "confluent_flink_statement" "create_offline_table" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.env.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flink.id
  }
  principal {
    id = confluent_service_account.flink-statements-runner.id
  }
  properties = {
    "sql.current-catalog"  = confluent_environment.env.display_name
    "sql.current-database" = confluent_kafka_cluster.kafka.display_name
  }
  statement     = file("../flink/station_status_tables/offline_table.sql")
  rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.flink.id
    secret = confluent_api_key.flink.secret
  }
}

resource "confluent_flink_statement" "branch_offline_stations" {
  count = var.run_flink_insert_statements ? 1 : 0
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.env.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flink.id
  }
  principal {
    id = confluent_service_account.flink-statements-runner.id
  }
  properties = {
    "sql.current-catalog"  = confluent_environment.env.display_name
    "sql.current-database" = confluent_kafka_cluster.kafka.display_name
  }
  statement     = file("../flink/branch_stations_by_status/branch_offline.sql")
  rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.flink.id
    secret = confluent_api_key.flink.secret
  }
}

resource "confluent_flink_statement" "branch_online_stations" {
  count = var.run_flink_insert_statements ? 1 : 0
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.env.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.flink.id
  }
  principal {
    id = confluent_service_account.flink-statements-runner.id
  }
  properties = {
    "sql.current-catalog"  = confluent_environment.env.display_name
    "sql.current-database" = confluent_kafka_cluster.kafka.display_name
  }
  statement     = file("../flink/branch_stations_by_status/branch_online.sql")
  rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
  credentials {
    key    = confluent_api_key.flink.id
    secret = confluent_api_key.flink.secret
  }
}