#!/bin/bash

# Script to pull latest code, handle local changes, rebuild, and restart chatbot-central container
# Runs everything from one directory above the script.

set -e  # Exit immediately if any command fails

CONTAINER_NAME="chatbot-central"
IMAGE_NAME="chatbot-central"
PORT="8005"

# --- MOVE TO PROJECT ROOT (ONE DIR ABOVE SCRIPT) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "==============================="
echo "🔄 Restarting $CONTAINER_NAME..."
echo "📂 Working directory: $PROJECT_DIR"
echo "==============================="

# --- GIT UPDATE SECTION ---
if [ -d ".git" ]; then
  echo "📂 Checking for local Git changes..."

  # Detect local changes
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "⚠️  You have uncommitted local changes."
    echo "---------------------------------------"
    git status -s
    echo "---------------------------------------"
    echo "📄 Summary of changes:"
    git diff --stat
    echo "---------------------------------------"
    echo "What would you like to do?"
    echo "1) Commit and push changes"
    echo "2) Stash changes for later"
    echo "3) Discard local changes and overwrite with online version"
    echo "4) Cancel restart"
    read -p "Enter choice [1-4]: " choice

    case $choice in
      1)
        echo "📝 Committing and pushing changes..."
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
        git push origin main
        ;;
      2)
        echo "📦 Stashing changes..."
        git stash push -m "Auto-stash before restart" >/dev/null
        ;;
      3)
        echo "🗑️  Discarding local changes and pulling from origin/main..."
        git reset --hard HEAD
        git fetch origin main
        git reset --hard origin/main
        ;;
      4)
        echo "❌ Cancelled by user."
        exit 0
        ;;
      *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
    esac
  else
    echo "✅ No local changes found."
  fi

  echo "⬇️  Pulling latest changes from origin/main..."
  git pull origin main
else
  echo "⚠️  No Git repository found — skipping git pull."
fi

# --- DOCKER RESTART SECTION ---
# Stop container if running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  echo "🛑 Stopping running container..."
  docker stop $CONTAINER_NAME
fi

# Remove container if it exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
  echo "🗑️ Removing old container..."
  docker rm $CONTAINER_NAME
fi

# Rebuild the image
echo "🛠️ Rebuilding Docker image '$IMAGE_NAME'..."
docker build -t $IMAGE_NAME .

# Run the container
echo "🚀 Starting new container..."
docker run -d \
  --name $CONTAINER_NAME \
  --env-file .env \
  -p $PORT:$PORT \
  $IMAGE_NAME

echo "✅ $CONTAINER_NAME restarted successfully and running on port $PORT."
