# infra/secrets.tf — OrcheFlowAI Secret Manager configuration

resource "google_secret_manager_secret" "db_url" {
  secret_id = "orcheflow-database-url"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "orcheflow-jwt-secret"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_url_v1" {
  secret      = google_secret_manager_secret.db_url.id
  secret_data = "postgresql://dummy:dummy@127.0.0.1/dummy" # Placeholder, update after AlloyDB IP is known
}

resource "google_secret_manager_secret_version" "jwt_v1" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = "orcheflow-demo-secret-2026-key"
}
