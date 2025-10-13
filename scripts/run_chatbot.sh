#!/bin/bash

# Script to build and run the chatbot-central Docker container
# Runs everything from the directory above the script's location.

set -e  # Exit immediately if any command fails

CONTAINER_NAME="chatbot-central"
IMAGE_NAME="chatbot-central"
PORT="8005"

# --- MOVE TO PROJECT ROOT (ONE DIR ABOVE SCRIPT) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "==============================="
echo "🚀 Running $CONTAINER_NAME..."
echo "📂 Working directory: $PROJECT_DIR"
echo "==============================="

# Build the Docker image
echo "🛠️ Building Docker image '$IMAGE_NAME'..."
docker build -t $IMAGE_NAME .

# Check if a container with the same name already exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
  echo "⚠️ A container named '$CONTAINER_NAME' already exists. Removing it..."
  docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
  docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
fi

# Run the container
echo "🚀 Starting new container..."
docker run -d \
  --name $CONTAINER_NAME \
  --env-file .env \
  -p $PORT:$PORT \
  $IMAGE_NAME

echo "✅ $CONTAINER_NAME is now running on port $PORT."
