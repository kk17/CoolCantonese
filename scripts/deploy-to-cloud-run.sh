#!/usr/bin/env bash

set -euo pipefail
XTRACE=${XTRACE:-false}
if [ "$XTRACE" = "true" ]; then
    set -x
fi
IFS=$'\n\t'
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

# Default values
PROJECT_ID="${PROJECT_ID:-coolcantonese}"
SERVICE_NAME="${SERVICE_NAME:-coolcantonese}"
REGION="${REGION:-asia-southeast1}"

# Get image version from git commit short SHA if not provided
if [ -z "${IMAGE_VERSION:-}" ]; then
    IMAGE_VERSION=$(git rev-parse --short HEAD)
fi

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
IMAGE_WITH_VERSION="$IMAGE_NAME:$IMAGE_VERSION"
IMAGE_LATEST="$IMAGE_NAME:latest"

PLATFORM="${PLATFORM:-managed}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"
MEMORY="${MEMORY:-512Mi}"
CPU="${CPU:-1}"
TRAFFIC="${TRAFFIC:-100}"  # Default to sending 100% traffic to new revision

# Check if service already exists
echo "Checking if service $SERVICE_NAME already exists in $REGION..."
SERVICE_EXISTS=$(gcloud run services list --platform=$PLATFORM --region=$REGION --project=$PROJECT_ID --filter="metadata.name=$SERVICE_NAME" --format="value(metadata.name)" || echo "")

if [ -n "$SERVICE_EXISTS" ]; then
    echo "Service $SERVICE_NAME already exists. Will update the existing service."
    UPDATE_MODE="true"
else
    echo "Service $SERVICE_NAME does not exist. Will create a new service."
    UPDATE_MODE="false"
fi

echo "Building Docker image with tags: $IMAGE_WITH_VERSION and $IMAGE_LATEST"
docker build -t "$IMAGE_WITH_VERSION" -t "$IMAGE_LATEST" .

echo "Pushing images to Google Container Registry..."
docker push "$IMAGE_WITH_VERSION"
docker push "$IMAGE_LATEST"

echo "Deploying to Cloud Run..."
DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_WITH_VERSION \
  --platform $PLATFORM \
  --region $REGION \
  --project $PROJECT_ID \
  --memory $MEMORY \
  --cpu $CPU"

# Process .env file if it exists
if [ -f ".env" ]; then
  echo "Found .env file, loading environment variables..."
  ENV_VARS_FROM_FILE=""
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
      continue
    fi
    # Extract the KEY=VALUE part (ignoring inline comments)
    var_def=$(echo "$line" | sed 's/[[:space:]]*#.*$//' | xargs)
    # Only process non-empty lines that contain an equals sign
    if [[ -n "$var_def" && "$var_def" == *"="* ]]; then
      # Add the variable to ENV_VARS_FROM_FILE
      if [[ -n "$ENV_VARS_FROM_FILE" ]]; then
        ENV_VARS_FROM_FILE="$ENV_VARS_FROM_FILE,$var_def"
      else
        ENV_VARS_FROM_FILE="$var_def"
      fi
    fi
  done < .env
  
  # Combine with existing ENV_VARS if any
  if [[ -n "$ENV_VARS_FROM_FILE" ]]; then
    if [[ -n "${ENV_VARS:-}" ]]; then
      ENV_VARS="$ENV_VARS,$ENV_VARS_FROM_FILE"
    else
      ENV_VARS="$ENV_VARS_FROM_FILE"
    fi
  fi
fi

# Add environment variables if specified
if [ -n "${ENV_VARS:-}" ]; then
  DEPLOY_CMD="$DEPLOY_CMD --set-env-vars $ENV_VARS"
fi

# Add authentication flag
if [ "$ALLOW_UNAUTHENTICATED" = "true" ]; then
  DEPLOY_CMD="$DEPLOY_CMD --allow-unauthenticated"
else
  DEPLOY_CMD="$DEPLOY_CMD --no-allow-unauthenticated"
fi

# Add traffic routing option for updates
if [ "$UPDATE_MODE" = "true" ] && [ "$TRAFFIC" != "100" ]; then
  DEPLOY_CMD="$DEPLOY_CMD --no-traffic"
fi

# Execute deployment command
echo "Executing: $DEPLOY_CMD"
eval $DEPLOY_CMD

# Handle traffic splitting for updates if not sending 100% traffic to new revision
if [ "$UPDATE_MODE" = "true" ] && [ "$TRAFFIC" != "100" ]; then
  echo "Updating traffic split to send $TRAFFIC% to the new revision..."
  LATEST_REVISION=$(gcloud run services describe $SERVICE_NAME --platform=$PLATFORM --region=$REGION --project=$PROJECT_ID --format="value(status.latestCreatedRevisionName)")
  
  TRAFFIC_CMD="gcloud run services update-traffic $SERVICE_NAME \
    --platform=$PLATFORM \
    --region=$REGION \
    --project=$PROJECT_ID \
    --to-revisions=$LATEST_REVISION=$TRAFFIC"
  
  echo "Executing: $TRAFFIC_CMD"
  eval $TRAFFIC_CMD
fi

echo "Deployment complete!"
