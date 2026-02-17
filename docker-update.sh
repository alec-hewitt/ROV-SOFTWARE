#!/bin/bash

# Complete ROV Software Deployment Script
# Sets up Pi if needed, builds image locally, and deploys to Pi

set -e

PI_USER="pi"
PI_HOST="192.168.1.12"
PI_PATH="/home/pi/ROV-SOFTWARE"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚢 ROV Software Deployment${NC}"
echo "=============================="

# Function to check if Pi is reachable
check_pi_connection() {
    echo -e "${YELLOW}🔍 Checking Pi connection...${NC}"
    if ! ping -c 1 $PI_HOST > /dev/null 2>&1; then
        echo -e "${RED}❌ Cannot reach Pi at $PI_HOST${NC}"
        echo "Please check the IP address and network connection"
        exit 1
    fi
    echo -e "${GREEN}✅ Pi is reachable${NC}"
}

cleanup_pi() {
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
}

# Function to setup Pi if needed
setup_pi() {
    echo -e "${YELLOW}🔧 Setting up Pi directory structure...${NC}"
    ssh $PI_USER@$PI_HOST "mkdir -p $PI_PATH/logging $PI_PATH/config"
    
    echo -e "${YELLOW}📤 Copying Docker configuration files to Pi...${NC}"
    scp docker-compose.yml $PI_USER@$PI_HOST:$PI_PATH/
    scp docker-compose.prod.yml $PI_USER@$PI_HOST:$PI_PATH/ 2>/dev/null || echo "Note: docker-compose.prod.yml not found, using default"
    
    echo -e "${GREEN}✅ Pi setup complete${NC}"
}

# Function to deploy software
deploy_software() {
    echo -e "${YELLOW}🐳 Building ROV software Docker image for ARM64...${NC}"
    
    # Check if buildx is available and set up properly
    if docker buildx version > /dev/null 2>&1; then
        echo "Setting up buildx for ARM64 build..."
        
        # Create and use a new builder instance for ARM64
        docker buildx create --name arm64-builder --use --platform linux/arm64 2>/dev/null || true
        docker buildx inspect --bootstrap
        
        echo "Building for ARM64..."
        if ! docker buildx build --platform linux/arm64 -t rov-software --load .; then
            echo -e "${RED}❌ Docker build failed${NC}"
            exit 1
        fi
    else
        echo "Buildx not available, trying alternative approach..."
        # Try to build with platform flag
        if ! docker build --platform linux/arm64 -t rov-software .; then
            echo -e "${RED}❌ Docker build failed${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}📦 Saving image to tar file...${NC}"
    if ! docker save rov-software > rov-software.tar; then
        echo -e "${RED}❌ Failed to save Docker image${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📤 Copying to Pi...${NC}"
    if ! scp rov-software.tar $PI_USER@$PI_HOST:~/; then
        echo -e "${RED}❌ Failed to copy image to Pi${NC}"
        rm -f rov-software.tar
        exit 1
    fi
    
    echo -e "${YELLOW}🚀 Deploying on Pi...${NC}"
    if ! ssh $PI_USER@$PI_HOST "docker load < ~/rov-software.tar && cd $PI_PATH && docker-compose down --remove-orphans && docker-compose up -d"; then
        echo -e "${RED}❌ Deployment failed on Pi${NC}"
        echo "Attempting cleanup..."
        ssh $PI_USER@$PI_HOST "rm -f ~/rov-software.tar" 2>/dev/null || true
        rm -f rov-software.tar
        exit 1
    fi
    
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    rm rov-software.tar
    ssh $PI_USER@$PI_HOST "rm ~/rov-software.tar"
}

# Main execution
check_pi_connection
cleanup_pi
setup_pi
deploy_software

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Manage your Pi with:"
echo "  ./manage-pi.sh status    # Check status"
echo "  ./manage-pi.sh logs      # View logs"
echo "  ./manage-pi.sh restart   # Restart services"
