$ErrorActionPreference = "Continue"
$PROJECT_ID = "genai-apac-2026-491004"
$REGION = "asia-southeast1"
$IMAGE_TAG = "latest"

Write-Host ">> Creating Secrets (if they don't exist)..."
$secrets = @("orcheflow-google-client-id", "orcheflow-google-client-secret", "orcheflow-database-url", "orcheflow-jwt-secret")
foreach ($secret in $secrets) {
    gcloud secrets describe $secret --project=$PROJECT_ID 2>$null
    if ($LASTEXITCODE -ne 0) {
        gcloud secrets create $secret --replication-policy="automatic" --project=$PROJECT_ID
        Write-Host "Created secret $secret"
    }
}

Write-Host ">> Deploying MCP Service..."
gcloud run deploy orcheflow-mcp `
    --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/orcheflow/orcheflow-mcp:${IMAGE_TAG}" `
    --region=$REGION --project=$PROJECT_ID `
    --service-account="orcheflow-runtime@${PROJECT_ID}.iam.gserviceaccount.com" `
    --vpc-connector="orcheflow-vpc-conn" --vpc-egress="all-traffic" `
    --allow-unauthenticated --max-instances=5 `
    --set-secrets="DATABASE_URL=orcheflow-database-url:latest" `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},ENVIRONMENT=production"

$MCP_URL = gcloud run services describe orcheflow-mcp --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host ">> Deploying Agents Service..."
gcloud run deploy orcheflow-agents `
    --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/orcheflow/orcheflow-agents:${IMAGE_TAG}" `
    --region=$REGION --project=$PROJECT_ID `
    --service-account="orcheflow-runtime@${PROJECT_ID}.iam.gserviceaccount.com" `
    --vpc-connector="orcheflow-vpc-conn" --vpc-egress="all-traffic" `
    --allow-unauthenticated --max-instances=5 `
    --set-secrets="DATABASE_URL=orcheflow-database-url:latest" `
    --set-env-vars="MCP_SERVER_URL=${MCP_URL},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},ENVIRONMENT=production"

$AGENTS_URL = gcloud run services describe orcheflow-agents --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host ">> Deploying API Service..."
gcloud run deploy orcheflow-api `
    --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/orcheflow/orcheflow-api:${IMAGE_TAG}" `
    --region=$REGION --project=$PROJECT_ID `
    --service-account="orcheflow-runtime@${PROJECT_ID}.iam.gserviceaccount.com" `
    --vpc-connector="orcheflow-vpc-conn" --vpc-egress="all-traffic" `
    --allow-unauthenticated --max-instances=10 `
    --set-secrets="DATABASE_URL=orcheflow-database-url:latest,JWT_SECRET=orcheflow-jwt-secret:latest,GOOGLE_CLIENT_ID=orcheflow-google-client-id:latest,GOOGLE_CLIENT_SECRET=orcheflow-google-client-secret:latest" `
    --set-env-vars="AGENT_SERVICE_URL=${AGENTS_URL},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},ENVIRONMENT=production"

$API_URL = gcloud run services describe orcheflow-api --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host "==========================="
Write-Host "    ORCHEFLOWAI DEMO URLs  "
Write-Host "==========================="
Write-Host "API:    $API_URL"
Write-Host "Agents: $AGENTS_URL"
Write-Host "MCP:    $MCP_URL"
