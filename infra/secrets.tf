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

resource "google_secret_manager_secret" "google_client_id" {
  secret_id = "orcheflow-google-client-id"
  project   = var.project_id
  replication { auto {} }
}

resource "google_secret_manager_secret" "google_client_secret" {
  secret_id = "orcheflow-google-client-secret"
  project   = var.project_id
  replication { auto {} }
}

resource "google_secret_manager_secret_version" "google_client_id_v1" {
  secret      = google_secret_manager_secret.google_client_id.id
  secret_data = var.google_client_id
}

resource "google_secret_manager_secret_version" "google_client_secret_v1" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = var.google_client_secret
}
