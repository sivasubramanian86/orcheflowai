provider "google" {
  project = var.project_id
  region  = var.region
}

variable "gcp_services" {
  type = list(string)
  default = [
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "alloydb.googleapis.com",
    "servicenetworking.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com"
  ]
}

resource "google_project_service" "services" {
  for_each = toset(var.gcp_services)
  project  = var.project_id
  service  = each.key

  disable_on_destroy = false
}

# GCS buckets for sample data
resource "google_storage_bucket" "data_ingest" {
  project       = var.project_id
  name          = "${var.project_id}-orcheflow-data"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
}

output "data_bucket_name" {
  value = google_storage_bucket.data_ingest.name
}
