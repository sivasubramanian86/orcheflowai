# infra/alloydb.tf — OrcheFlowAI AlloyDB (PostgreSQL 15 + pgvector)
# Provisions a high-speed, AI-ready database cluster on Google Cloud.

# ── VPC Networking (required for AlloyDB Private IP) ─────────────────────────
resource "google_compute_network" "orcheflow_vpc" {
  name                    = "orcheflow-vpc"
  auto_create_subnetworks = true
  project                 = var.project_id
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "orcheflow-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.orcheflow_vpc.id
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.orcheflow_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# ── Serverless VPC Access (Cloud Run to AlloyDB) ──────────────────────────────
resource "google_vpc_access_connector" "connector" {
  name          = "orcheflow-vpc-conn"
  region        = var.region
  project       = var.project_id
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.orcheflow_vpc.name

  depends_on = [google_project_service.services]
}

# ── IAM for VPC Connector (Resolves 403s) ────────────────────────────────────
resource "google_project_iam_member" "vpc_connector_network_user" {
  project = var.project_id
  role    = "roles/compute.networkUser"
  member  = "serviceAccount:service-967518492968@gcp-sa-vpcaccess.iam.gserviceaccount.com"
}

# ── AlloyDB Cluster ───────────────────────────────────────────────────────────
resource "google_alloydb_cluster" "orcheflow_db" {
  cluster_id = "orcheflow-db-cluster"
  location   = var.region
  project    = var.project_id

  network_config {
    network = google_compute_network.orcheflow_vpc.id
  }

  initial_user {
    user     = "orcheflow"
    password = "change-me-in-secret-manager"
  }

  depends_on = [google_project_service.services, google_service_networking_connection.private_vpc_connection]
}

resource "google_alloydb_instance" "primary_instance" {
  cluster       = google_alloydb_cluster.orcheflow_db.name
  instance_id   = "primary-instance"
  instance_type = "PRIMARY"

  machine_config { cpu_count = 2 } # Minimum for AlloyDB

  availability_type = "ZONAL" # Slashes cost for dev/hackathon
}

output "database_ip" {
  value = google_alloydb_instance.primary_instance.ip_address
}
