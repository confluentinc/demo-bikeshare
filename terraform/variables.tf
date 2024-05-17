variable "region" {
  description = "AWS region - must be one that has Flink available (`confluent flink region list`)"
  type        = string
  default     = "us-east-2"
}

variable "flink_cluster_name" {
  description = "Name of the cluster"
  type        = string
  default     = "flink"
} 

variable "kafka_cluster_name" {
  description = "Name of the Kafka cluster"
  type        = string
  default     = "cluster_0"
}

variable "cloud" {
    description = "Cloud provider"
    type        = string
    default     = "AWS"
}

variable "sr_package"{
    description = "Schema Registry package"
    type        = string
    default     = "ADVANCED"
}

variable "cc_api_key" {
  description = "Confluent Cloud API Key (also referred as Cloud API ID)"
  type        = string
}

variable "cc_api_secret" {
  description = "Confluent Cloud API Secret"
  type        = string
  sensitive   = true
}

variable "run_flink_insert_statements" {
  description = "Run Flink insert statements"
  type        = bool
  default     = false
}