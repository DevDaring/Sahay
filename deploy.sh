#!/bin/bash
# Deployment script for Sahay application

echo "🚀 Starting Sahay deployment to GCP VM..."

# Server details
SERVER_IP="34.63.56.182"
SERVER_USER="debz"
PRIVATE_KEY="C:/Users/Debz/.ssh/id_rsa"
APP_DIR="/home/debz/sahay-app"

echo "📁 Creating application directory..."
ssh -i "$PRIVATE_KEY" "$SERVER_USER@$SERVER_IP" "mkdir -p $APP_DIR"

echo "📤 Uploading application files..."
# Upload all files except __pycache__, .git, and virtual environment
rsync -avz --progress \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='hack_venv' \
    --exclude='.vscode' \
    --exclude='*.log' \
    -e "ssh -i $PRIVATE_KEY" \
    ./ "$SERVER_USER@$SERVER_IP:$APP_DIR/"

echo "✅ File upload completed!"