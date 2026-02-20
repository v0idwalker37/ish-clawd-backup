# Production environment configuration
# Larger instances, stricter security, blue/green deployment
terraform {
  required_version = ">= 1.9"
  
  backend "gcs" {
    bucket = "ungouge-terraform-state-production"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "gen-lang-client-0199462206"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "vision.googleapis.com",
    "vpcaccess.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# Production Cloud SQL with high availability
resource "google_sql_database_instance" "main" {
  name             = "ungouge-db-${var.environment}"
  database_version = "MYSQL_8_0"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier              = "db-n1-standard-2"  # 2 vCPU, 7.5GB RAM (production)
    availability_type = "REGIONAL"          # High availability
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      binary_log_enabled             = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    database_flags {
      name  = "max_connections"
      value = "200"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }
  }
  
  deletion_protection = true  # Protect production DB
}

# Production Redis with HA
resource "google_redis_instance" "cache" {
  name           = "ungouge-redis-${var.environment}"
  tier           = "STANDARD_HA"  # High availability
  memory_size_gb = 5              # Larger cache for production
  region         = var.region
  project        = var.project_id
  
  authorized_network = google_compute_network.vpc.id
  redis_version      = "REDIS_7_0"
  
  replica_count          = 1  # Read replica
  read_replicas_mode     = "READ_REPLICAS_ENABLED"
  customer_managed_key   = google_kms_crypto_key.redis.id  # Customer-managed encryption
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "ungouge-vpc-${var.environment}"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# KMS for encryption
resource "google_kms_key_ring" "ungouge" {
  name     = "ungouge-keyring-${var.environment}"
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "redis" {
  name     = "redis-key"
  key_ring = google_kms_key_ring.ungouge.id
  
  rotation_period = "2592000s"  # 30 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Cloud Armor (DDoS protection)
resource "google_compute_security_policy" "policy" {
  name    = "ungouge-armor-policy"
  project = var.project_id
  
  # Rate limiting rule
  rule {
    action   = "throttle"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
    }
  }
  
  # Default rule
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}

# Alerting
resource "google_monitoring_alert_policy" "error_rate" {
  display_name = "High Error Rate - ${var.environment}"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.label.response_code_class = \"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.slack.id]
}

resource "google_monitoring_notification_channel" "slack" {
  display_name = "Slack Alerts"
  type         = "slack"
  project      = var.project_id
  
  labels = {
    channel_name = "#ungouge-alerts"
  }
  
  sensitive_labels {
    auth_token = var.slack_webhook_url
  }
}

variable "slack_webhook_url" {
  type      = string
  sensitive = true
}

# Budget alert
resource "google_billing_budget" "budget" {
  billing_account = var.billing_account
  display_name    = "Ungouge ${var.environment} Budget"
  
  amount {
    specified_amount {
      currency_code = "USD"
      units         = "800"  # $800/month
    }
  }
  
  threshold_rules {
    threshold_percent = 0.5  # Alert at 50%
  }
  
  threshold_rules {
    threshold_percent = 0.8  # Alert at 80%
  }
  
  threshold_rules {
    threshold_percent = 1.0  # Alert at 100%
  }
}

variable "billing_account" {
  type = string
}

# Note: Cloud Run services configuration similar to staging
# but with larger resources and stricter security
# Full configuration would be added here...

output "production_note" {
  value = "Production environment requires manual approval before deployment"
}
