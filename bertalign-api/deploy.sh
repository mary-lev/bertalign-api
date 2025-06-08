#!/bin/bash

# Bertalign API Deployment Script for Google Cloud Run
# Usage: ./deploy.sh <version> [project-id]

set -e  # Exit on any error

# Configuration
VERSION=${1:-v0.1}
PROJECT_ID=${2:-"bertalign-demo-202406"}
SERVICE_NAME="bertalign-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${VERSION}"

echo "🚀 Deploying Bertalign API ${VERSION} to Cloud Run..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not installed. Please install Google Cloud SDK."
    exit 1
fi

# Set the project
echo "📋 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Build Docker image
echo "🔨 Building Docker image..."
# docker build -t ${IMAGE_NAME} .

# Push to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
# docker push ${IMAGE_NAME}
gcloud builds submit --tag ${IMAGE_NAME} .

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --memory 8Gi \
    --cpu 4 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --allow-unauthenticated \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo "🏥 Health check: ${SERVICE_URL}/health"

# Test the health endpoint
echo "🔍 Testing health endpoint..."
if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed - service may still be starting up"
fi