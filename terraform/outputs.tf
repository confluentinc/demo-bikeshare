output "environment" {
  value = confluent_environment.env
}

output "kafka_cluster" {
  value = confluent_kafka_cluster.kafka
}

output "flink_pool" {
  value = confluent_flink_compute_pool.flink
}

output "schema_registry_cluster" {
  value = confluent_schema_registry_cluster.sr
}

output "kafka_api_key"{
  value = confluent_api_key.kafka
  sensitive = true
}

output "schema_registry_api_key"{
  value = confluent_api_key.sr
  sensitive = true
}

output "service_account"{
  value = confluent_service_account.sa
  sensitive = true
}
