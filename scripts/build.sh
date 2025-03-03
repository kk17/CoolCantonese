#!/usr/bin/env bash

set -euo pipefail
XTRACE=${XTRACE:-false}
if [ "$XTRACE" = "true" ]; then
    set -x
fi
IFS=$'\n\t'
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Default values
PROJECT_ID="${PROJECT_ID:-coolcantonese}"
SERVICE_NAME="${SERVICE_NAME:-coolcantonese}"
REGION="${REGION:-asia-southeast1}"
PORT="${PORT:-8888}"
PLATFORM="${PLATFORM:-managed}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"
MEMORY="${MEMORY:-512Mi}"
CPU="${CPU:-1}"
TRAFFIC="${TRAFFIC:-100}"  # Default to sending 100% traffic to new revision

# Default actions (all enabled by default)
DO_ALL=true
DO_BUILD=false
DO_PUSH=false
DO_DEPLOY=false

# Parse command line arguments
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -b|--build)
        DO_ALL=false
        DO_BUILD=true
        ;;
      -p|--push)
        DO_ALL=false
        DO_PUSH=true
        ;;
      -d|--deploy)
        DO_ALL=false
        DO_DEPLOY=true
        ;;
      -h|--help)
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --build         Only build the Docker image"
        echo "  --push          Only push the Docker image"
        echo "  --deploy        Only deploy to Cloud Run"
        echo "  --help          Show this help message"
        echo ""
        echo "Without options, all steps (build, push, deploy) are performed."
        exit 0
        ;;
      *)
        echo "Unknown option: $1"
        echo "Run '$0 --help' for usage information."
        exit 1
        ;;
    esac
    shift
  done
  if [ "$DO_ALL" = "true" ]; then
    DO_BUILD=true
    DO_PUSH=true
    DO_DEPLOY=true
  fi
}

# Check if user is authenticated with gcloud
check_auth() {
  echo "Verifying gcloud authentication..."
  ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "")
  if [ -z "$ACCOUNT" ]; then
    echo "Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
  fi
  echo "Authenticated as: $ACCOUNT"
  
  if [ "$DO_PUSH" = "true" ]; then
    echo "Setting up Docker authentication for Google Container Registry..."
    gcloud auth configure-docker --quiet
  fi
}

# Check if service already exists
check_service() {
  if [ "$DO_DEPLOY" != "true" ]; then
    return
  fi
  
  echo "Checking if service $SERVICE_NAME already exists in $REGION..."
  SERVICE_EXISTS=$(gcloud run services list --platform=$PLATFORM --region=$REGION --project=$PROJECT_ID --filter="metadata.name=$SERVICE_NAME" --format="value(metadata.name)" || echo "")

  if [ -n "$SERVICE_EXISTS" ]; then
    echo "Service $SERVICE_NAME already exists. Will update the existing service."
    UPDATE_MODE="true"
  else
    echo "Service $SERVICE_NAME does not exist. Will create a new service."
    UPDATE_MODE="false"
  fi
}

# Process .env file if it exists
process_env_file() {
  if [ "$DO_DEPLOY" != "true" ] || [ ! -f ".env" ]; then
    return
  fi
  
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
}

# Define image details
setup_image_names() {
  # Get image version from git commit short SHA if not provided
  if [ -z "${IMAGE_VERSION:-}" ]; then
    IMAGE_VERSION=$(git rev-parse --short HEAD)
  fi

  IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
  IMAGE_WITH_VERSION="$IMAGE_NAME:$IMAGE_VERSION"
  IMAGE_LATEST="$IMAGE_NAME:latest"
}

# Build Docker image
build_image() {
  if [ "$DO_BUILD" != "true" ]; then
    echo "Skipping build step..."
    return
  fi
  
  echo "Building Docker image with tags: $IMAGE_WITH_VERSION and $IMAGE_LATEST"
  docker build -t "$IMAGE_WITH_VERSION" -t "$IMAGE_LATEST" .
}

# Push Docker image to registry
push_image() {
  if [ "$DO_PUSH" != "true" ]; then
    echo "Skipping push step..."
    return
  fi
  
  echo "Pushing images to Google Container Registry..."
  docker push "$IMAGE_WITH_VERSION" || {
    echo "Error pushing image. If authentication failed, try running:"
    echo "gcloud auth login"
    echo "gcloud auth configure-docker"
    exit 1
  }
  docker push "$IMAGE_LATEST" || {
    echo "Error pushing latest tag. Continuing with deployment..."
  }
}

# Deploy service to Cloud Run
deploy_service() {
  if [ "$DO_DEPLOY" != "true" ]; then
    echo "Skipping deploy step..."
    return
  fi
  
  echo "Deploying to Cloud Run..."
  DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_WITH_VERSION \
    --platform $PLATFORM \
    --region $REGION \
    --project $PROJECT_ID \
    --port $PORT \
    --memory $MEMORY \
    --cpu $CPU"

  # Add environment variables
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
}

# Main function
main() {
  parse_args "$@"
  check_auth
  check_service
  setup_image_names
  build_image
  push_image
  process_env_file
  deploy_service
  
  echo "Process completed successfully!"
}

# Execute main function with all arguments
main "$@"
