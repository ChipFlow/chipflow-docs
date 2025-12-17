#!/bin/bash
# Idempotent GCP setup script for ChipFlow Docs Chat backend
# Usage: ./setup-gcp.sh [PROJECT_ID] [GITHUB_REPO]
#
# Example: ./setup-gcp.sh chipflow-platform ChipFlow/chipflow-docs

set -e

PROJECT_ID="${1:-chipflow-platform}"
GITHUB_REPO="${2:-ChipFlow/chipflow-docs}"
REGION="us-central1"
SERVICE_NAME="chipflow-docs-chat"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"
SA_NAME="github-actions-deployer"

echo "==> Setting up GCP project: $PROJECT_ID"
echo "==> GitHub repo: $GITHUB_REPO"

# Set the project
gcloud config set project "$PROJECT_ID"

# Enable required APIs (idempotent - no error if already enabled)
echo ""
echo "==> Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    iam.googleapis.com \
    iamcredentials.googleapis.com \
    sts.googleapis.com \
    --quiet

# Get project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
DEPLOYER_SA="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account for GitHub Actions (if not exists)
echo ""
echo "==> Creating service account for GitHub Actions..."
if ! gcloud iam service-accounts describe "$DEPLOYER_SA" --quiet 2>/dev/null; then
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="GitHub Actions Deployer" \
        --quiet
fi

# Grant required roles to the deployer service account
echo ""
echo "==> Granting roles to deployer service account..."
for role in "roles/run.admin" "roles/storage.admin" "roles/aiplatform.user"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$DEPLOYER_SA" \
        --role="$role" \
        --condition=None \
        --quiet 2>/dev/null || true
done

# Allow deployer to act as compute service account
gcloud iam service-accounts add-iam-policy-binding "$COMPUTE_SA" \
    --member="serviceAccount:$DEPLOYER_SA" \
    --role="roles/iam.serviceAccountUser" \
    --quiet 2>/dev/null || true

# Grant Vertex AI access to Cloud Run's compute service account
echo ""
echo "==> Granting Vertex AI access to compute service account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/aiplatform.user" \
    --condition=None \
    --quiet 2>/dev/null || true

# Set up Workload Identity Federation for GitHub Actions
echo ""
echo "==> Setting up Workload Identity Federation..."

# Create workload identity pool (if not exists)
if ! gcloud iam workload-identity-pools describe "$POOL_NAME" --location=global --quiet 2>/dev/null; then
    echo "    Creating workload identity pool..."
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --location="global" \
        --display-name="GitHub Actions Pool" \
        --quiet
fi

# Create OIDC provider (if not exists)
if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" --location=global --quiet 2>/dev/null; then
    echo "    Creating OIDC provider..."
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --location="global" \
        --workload-identity-pool="$POOL_NAME" \
        --display-name="GitHub Actions Provider" \
        --issuer-uri="https://token.actions.githubusercontent.com" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --attribute-condition="assertion.repository=='$GITHUB_REPO'" \
        --quiet
fi

# Allow GitHub Actions to impersonate the service account
echo ""
echo "==> Granting workload identity user to GitHub repo..."
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_SA" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${GITHUB_REPO}" \
    --quiet 2>/dev/null || true

# Get the workload identity provider resource name
WIF_PROVIDER="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"

# Set GitHub secrets
echo ""
echo "==> Setting GitHub secrets..."
echo "$WIF_PROVIDER" | gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --repo="$GITHUB_REPO"
echo "$DEPLOYER_SA" | gh secret set GCP_SERVICE_ACCOUNT --repo="$GITHUB_REPO"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "GitHub secrets have been set:"
echo "  - GCP_WORKLOAD_IDENTITY_PROVIDER"
echo "  - GCP_SERVICE_ACCOUNT"
echo ""
echo "Trigger deployment by:"
echo "  - Pushing to main with changes in chat-backend/"
echo "  - Or manually: gh workflow run deploy-chat-backend --repo $GITHUB_REPO"
