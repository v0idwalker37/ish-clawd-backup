terraform {
  required_version = ">= 1.9"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  
  backend "gcs" {
    bucket = "ungouge-terraform-state-staging"
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
  default     = "staging"
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
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# Service accounts
resource "google_service_account" "api_gateway" {
  account_id   = "ungouge-api-gateway-${var.environment}"
  display_name = "Ungouge API Gateway Service Account"
  project      = var.project_id
}

resource "google_service_account" "cost_model" {
  account_id   = "ungouge-cost-model-${var.environment}"
  display_name = "Ungouge Cost Model Service Account"
  project      = var.project_id
}

resource "google_service_account" "quote_extractor" {
  account_id   = "ungouge-quote-extractor-${var.environment}"
  display_name = "Ungouge Quote Extractor Service Account"
  project      = var.project_id
}

resource "google_service_account" "webhook_handler" {
  account_id   = "ungouge-webhook-handler-${var.environment}"
  display_name = "Ungouge Webhook Handler Service Account"
  project      = var.project_id
}

# Cloud SQL (MySQL)
resource "google_sql_database_instance" "main" {
  name             = "ungouge-db-${var.environment}"
  database_version = "MYSQL_8_0"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier = "db-n1-standard-1"  # 1 vCPU, 3.75GB RAM (staging)
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
    
    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      binary_log_enabled = true
    }
    
    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }
  
  deletion_protection = false  # Allow deletion in staging
}

resource "google_sql_database" "database" {
  name     = "ungouge"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

# Redis (Memorystore)
resource "google_redis_instance" "cache" {
  name           = "ungouge-redis-${var.environment}"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  project        = var.project_id
  
  authorized_network = google_compute_network.vpc.id
  
  redis_version = "REDIS_7_0"
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "ungouge-vpc-${var.environment}"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "subnet" {
  name          = "ungouge-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id
}

# VPC Access Connector (for Cloud Run to access private resources)
resource "google_vpc_access_connector" "connector" {
  name          = "ungouge-vpc-connector-${var.environment}"
  region        = var.region
  project       = var.project_id
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  
  depends_on = [google_project_service.services]
}

# GCS Buckets
resource "google_storage_bucket" "uploaded_quotes" {
  name     = "ungouge-uploaded-quotes-${var.environment}"
  location = var.region
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 90  # Delete after 90 days (GDPR compliance)
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "generated_pdfs" {
  name     = "ungouge-generated-pdfs-${var.environment}"
  location = var.region
  project  = var.project_id
  
  uniform_bucket_level_access = true
}

# Pub/Sub Topics
resource "google_pubsub_topic" "payment_completed" {
  name    = "payment-completed-${var.environment}"
  project = var.project_id
}

resource "google_pubsub_topic" "quote_uploaded" {
  name    = "quote-uploaded-${var.environment}"
  project = var.project_id
}

resource "google_pubsub_topic" "pdf_generate" {
  name    = "pdf-generate-${var.environment}"
  project = var.project_id
}

# Cloud Run Services
module "api_gateway" {
  source = "../../modules/cloud-run"
  
  project_id            = var.project_id
  region                = var.region
  service_name          = "api-gateway-${var.environment}"
  image                 = "gcr.io/${var.project_id}/api-gateway:latest"
  service_account_email = google_service_account.api_gateway.email
  vpc_connector         = google_vpc_access_connector.connector.id
  
  cpu           = "1"
  memory        = "512Mi"
  min_instances = 1
  max_instances = 10
  concurrency   = 80
  
  allow_unauthenticated = true  # Public API
  
  env_vars = {
    ENVIRONMENT           = var.environment
    DATABASE_URL          = "postgresql+asyncpg://user:pass@${google_sql_database_instance.main.private_ip_address}/ungouge"
    REDIS_URL             = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
    COST_MODEL_SERVICE_URL = module.cost_model.service_url
    QUOTE_EXTRACTOR_SERVICE_URL = module.quote_extractor.service_url
  }
  
  secrets = {
    JWT_SECRET_KEY = {
      secret_name = "jwt-secret"
      version     = "latest"
    }
    STRIPE_SECRET_KEY = {
      secret_name = "stripe-secret-${var.environment}"
      version     = "latest"
    }
  }
}

module "cost_model" {
  source = "../../modules/cloud-run"
  
  project_id            = var.project_id
  region                = var.region
  service_name          = "cost-model-${var.environment}"
  image                 = "gcr.io/${var.project_id}/cost-model:latest"
  service_account_email = google_service_account.cost_model.email
  vpc_connector         = google_vpc_access_connector.connector.id
  
  cpu           = "2"
  memory        = "1Gi"
  min_instances = 1
  max_instances = 20
  concurrency   = 40
  
  env_vars = {
    ENVIRONMENT = var.environment
    REDIS_URL   = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
  }
}

module "quote_extractor" {
  source = "../../modules/cloud-run"
  
  project_id            = var.project_id
  region                = var.region
  service_name          = "quote-extractor-${var.environment}"
  image                 = "gcr.io/${var.project_id}/quote-extractor:latest"
  service_account_email = google_service_account.quote_extractor.email
  
  cpu             = "2"
  memory          = "2Gi"
  min_instances   = 0  # Can scale to zero (bursty workload)
  max_instances   = 50
  concurrency     = 10
  timeout_seconds = 300  # 5 minutes (Vision API can be slow)
  
  env_vars = {
    ENVIRONMENT    = var.environment
    GCP_PROJECT_ID = var.project_id
  }
}

module "webhook_handler" {
  source = "../../modules/cloud-run"
  
  project_id            = var.project_id
  region                = var.region
  service_name          = "webhook-handler-${var.environment}"
  image                 = "gcr.io/${var.project_id}/webhook-handler:latest"
  service_account_email = google_service_account.webhook_handler.email
  vpc_connector         = google_vpc_access_connector.connector.id
  
  cpu           = "1"
  memory        = "512Mi"
  min_instances = 1
  max_instances = 10
  concurrency   = 20
  
  allow_unauthenticated = true  # Stripe needs public access
  
  env_vars = {
    ENVIRONMENT    = var.environment
    DATABASE_URL   = "postgresql+asyncpg://user:pass@${google_sql_database_instance.main.private_ip_address}/ungouge"
    GCP_PROJECT_ID = var.project_id
  }
  
  secrets = {
    STRIPE_SECRET_KEY = {
      secret_name = "stripe-secret-${var.environment}"
      version     = "latest"
    }
    STRIPE_WEBHOOK_SECRET = {
      secret_name = "stripe-webhook-secret-${var.environment}"
      version     = "latest"
    }
  }
}

# Outputs
output "api_gateway_url" {
  value = module.api_gateway.service_url
}

output "database_private_ip" {
  value = google_sql_database_instance.main.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.cache.host
}
