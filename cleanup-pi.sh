#!/bin/bash

# Pi Cleanup Script
# Cleans up disk space on the Pi

set -e

PI_USER="pi"
PI_HOST="192.168.1.12"

echo "🧹 Cleaning up Pi disk space..."

# Clean up Docker
ssh $PI_USER@$PI_HOST "docker system prune -af --volumes"

# Clean up old images
ssh $PI_USER@$PI_HOST "docker image prune -af"

# Check disk space
echo "📊 Disk space after cleanup:"
ssh $PI_USER@$PI_HOST "df -h"

echo "✅ Cleanup complete!"
