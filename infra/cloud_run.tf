# infra/cloud_run.tf — OrcheFlowAI Cloud Run services (Vertex AI ADC, no API key)
terraform {
  required_version = ">= 1.7"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
  backend "gcs" {
    bucket = "genai-apac-2026-491004-tfstate"
    prefix = "orcheflow/state"
  }
}

variable "project_id"  { default = "genai-apac-2026-491004" }
variable "region"      { default = "us-central1" }
variable "image_tag"   { default = "latest" }
variable "repo"        { default = "orcheflow" }

locals {
  image_base = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repo}"
}

# ── Service Account (least privilege) ─────────────────────────────────────────
resource "google_service_account" "orcheflow_sa" {
  project      = var.project_id
  account_id   = "orcheflow-runtime"
  display_name = "OrcheFlowAI Cloud Run SA"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.orcheflow_sa.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.orcheflow_sa.email}"
}

resource "google_project_iam_member" "cloud_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.orcheflow_sa.email}"
}

# ── Shared environment variables (Vertex AI — no API key) ─────────────────────
locals {
  shared_env = [
    { name = "GOOGLE_CLOUD_PROJECT",  value = var.project_id },
    { name = "GOOGLE_CLOUD_LOCATION", value = var.region },
    { name = "GEMINI_ORCHESTRATOR_MODEL", value = "vertex-ai:gemini-2.5-flash" },
    { name = "GEMINI_SUBAGENT_MODEL",     value = "vertex-ai:gemini-2.0-flash" },
    { name = "ENVIRONMENT", value = "production" },
  ]
}

# ── MCP Server ─────────────────────────────────────────────────────────────────
resource "google_cloud_run_v2_service" "mcp" {
  name     = "orcheflow-mcp"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.orcheflow_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }

    containers {
      image = "${local.image_base}/orcheflow-mcp:${var.image_tag}"
      resources {
        limits     = { cpu = "1", memory = "512Mi" }
        cpu_idle   = true
      }
      dynamic "env" {
        for_each = local.shared_env
        content { 
          name  = env.value.name
          value = env.value.value 
        }
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "orcheflow-database-url"
            version = "latest"
          }
        }
      }
      ports { container_port = 8080 }
      liveness_probe {
        http_get { path = "/health" }
        initial_delay_seconds = 10
        period_seconds        = 30
      }
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# ── Agent Service ──────────────────────────────────────────────────────────────
resource "google_cloud_run_v2_service" "agents" {
  name     = "orcheflow-agents"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.orcheflow_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }

    containers {
      image = "${local.image_base}/orcheflow-agents:${var.image_tag}"
      resources {
        limits   = { cpu = "2", memory = "1Gi" }
        cpu_idle = true
      }
      dynamic "env" {
        for_each = local.shared_env
        content { 
          name  = env.value.name
          value = env.value.value 
        }
      }
      env {
        name  = "MCP_SERVER_URL"
        value = google_cloud_run_v2_service.mcp.uri
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "orcheflow-database-url"
            version = "latest"
          }
        }
      }
      ports { container_port = 8080 }
      liveness_probe {
        http_get { path = "/health" }
        initial_delay_seconds = 15
        period_seconds        = 30
      }
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# ── API Service ────────────────────────────────────────────────────────────────
resource "google_cloud_run_v2_service" "api" {
  name     = "orcheflow-api"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.orcheflow_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }

    containers {
      image = "${local.image_base}/orcheflow-api:${var.image_tag}"
      resources {
        limits   = { cpu = "1", memory = "512Mi" }
        cpu_idle = true
      }
      dynamic "env" {
        for_each = local.shared_env
        content { 
          name  = env.value.name
          value = env.value.value 
        }
      }
      env {
        name  = "AGENT_SERVICE_URL"
        value = google_cloud_run_v2_service.agents.uri
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "orcheflow-database-url"
            version = "latest"
          }
        }
      }
      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = "orcheflow-jwt-secret"
            version = "latest"
          }
        }
      }
      ports { container_port = 8080 }
      liveness_probe {
        http_get { path = "/v1/health" }
        initial_delay_seconds = 10
        period_seconds        = 30
      }
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Public API access
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "api_url"    { value = google_cloud_run_v2_service.api.uri }
output "agents_url" { value = google_cloud_run_v2_service.agents.uri }
output "mcp_url"    { value = google_cloud_run_v2_service.mcp.uri }
