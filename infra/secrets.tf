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

# Values will be updated manually or via a separate lifecycle step to avoid plain-text storage in TF state.
# For the hackathon, we provision the slots.
