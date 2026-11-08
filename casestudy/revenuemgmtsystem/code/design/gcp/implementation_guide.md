# Google Cloud Implementation Guide: ZenithStays Platform

> **Note (as of November 7, 2026):** This is the deployment plan from the design phase (December 2025), not a tested runbook. Step 1 builds a container from `../backend`, but this repository includes no backend Dockerfile. The "Market Tools" Cloud Function in Step 3 is not defined in any Terraform here. Check service names and Terraform resources against current Google Cloud documentation before following it.

## 1. Overview
This guide supports the deployment of the ZenithStays architecture on **Google Cloud Platform (GCP)** using **Terraform**.
It focuses on Cloud Run (Compute), Firestore (Database), and Vertex AI (Agents).

### 1.1 Prerequisites
*   Google Cloud CLI (`gcloud`) installed.
*   Terraform v1.5+ installed.
*   GCP Project ID enabled with billing.

---

## 2. Infrastructure as Code (Terraform)

### 2.1 Project Structure
```text
/infrastructure-gcp
  ├── main.tf
  ├── variables.tf
  ├── modules/
      ├── compute/ (Cloud Run)
      ├── data/ (Firestore)
      ├── ai/ (Vertex AI)
```

### 2.2 Data Layer (Firestore)
File: `modules/data/main.tf`
```hcl
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

resource "google_firestore_index" "composite_index" {
  project = var.project_id
  database = google_firestore_database.database.name
  collection = "reservations"
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  fields {
    field_path = "checkInDate"
    order      = "ASCENDING"
  }
}
```

### 2.3 Compute Layer (Cloud Run)
File: `modules/compute/main.tf`
```hcl
resource "google_cloud_run_v2_service" "backend" {
  name     = "zenith-backend-api"
  location = var.region
  
  template {
    containers {
      image = "gcr.io/${var.project_id}/zenith-backend:latest"
      env {
        name  = "DB_TYPE"
        value = "firestore"
      }
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
    }
  }
}

# Make it public (if needed) or restricted via Load Balancer
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### 2.4 Agentic AI Layer (Vertex AI Agents)
File: `modules/ai/main.tf`
This module enables the Vertex AI API and creates the Agent app. Note that deep Agent configuration often happens in the console or via specific API calls, as Terraform support for GenAppBuilder is emerging.

```hcl
resource "google_project_service" "vertex_ai" {
  service = "aiplatform.googleapis.com"
}

resource "google_project_service" "agent_builder" {
  service = "discoveryengine.googleapis.com"
}
```

---

## 3. Deployment Steps

### Step 1: Container Build
Build your Node.js backend and push to Google Container Registry (GCR) or Artifact Registry.
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/zenith-backend:latest ../backend
```

### Step 2: Terraform Init & Apply
```bash
cd infrastructure-gcp
terraform init
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

### Step 3: Vertex AI Configuration
1.  Go to **Vertex AI Agent Builder** in the console.
2.  Create a new **Agent App**.
3.  Connect it to the "Market Tools" Cloud Function (you would define and deploy it yourself; see the note at the top).
4.  Test the agent in the "Preview" pane.

---

## 4. Monitoring
*   **Cloud Run Dashboard**: Built-in metrics for latency and container instance count.
*   **Log Explorer**: Aggregates all logs from Cloud Run and Vertex AI.
