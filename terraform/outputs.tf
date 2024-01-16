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

