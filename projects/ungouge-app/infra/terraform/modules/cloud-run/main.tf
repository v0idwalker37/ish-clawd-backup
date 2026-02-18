terraform {
  required_version = ">= 1.9"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
}

variable "image" {
  description = "Container image URL"
  type        = string
}

variable "env_vars" {
  description = "Environment variables"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secret environment variables from Secret Manager"
  type = map(object({
    secret_name = string
    version     = string
  }))
  default = {}
}

variable "cpu" {
  description = "CPU allocation"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "concurrency" {
  description = "Max concurrent requests per instance"
  type        = number
  default     = 80
}

variable "timeout_seconds" {
  description = "Request timeout"
  type        = number
  default     = 60
}

variable "vpc_connector" {
  description = "VPC connector for private network access"
  type        = string
  default     = null
}

variable "service_account_email" {
  description = "Service account email"
  type        = string
}

variable "allow_unauthenticated" {
  description = "Allow public access"
  type        = bool
  default     = false
}

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    timeout = "${var.timeout_seconds}s"

    service_account = var.service_account_email

    dynamic "vpc_access" {
      for_each = var.vpc_connector != null ? [1] : []
      content {
        connector = var.vpc_connector
        egress    = "PRIVATE_RANGES_ONLY"
      }
    }

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        cpu_idle = true
      }

      startup_probe {
        http_get {
          path = "/health/live"
          port = tonumber(split(":", var.service_name)[1] == "api-gateway" ? "8000" : split(":", var.service_name)[1] == "cost-model" ? "8001" : split(":", var.service_name)[1] == "quote-extractor" ? "8002" : "8003")
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health/live"
          port = tonumber(split(":", var.service_name)[1] == "api-gateway" ? "8000" : split(":", var.service_name)[1] == "cost-model" ? "8001" : split(":", var.service_name)[1] == "quote-extractor" ? "8002" : "8003")
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 30
        failure_threshold     = 3
      }

      # Environment variables
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secrets from Secret Manager
      dynamic "env" {
        for_each = var.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_name
              version = env.value.version
            }
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM: Allow public access if needed
resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  description = "Service URL"
  value       = google_cloud_run_v2_service.service.uri
}

output "service_name" {
  description = "Service name"
  value       = google_cloud_run_v2_service.service.name
}
