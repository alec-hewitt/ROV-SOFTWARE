#!/bin/bash

# Quick Update Script
# Only copies changed files and rebuilds when needed

set -e

PI_USER="pi"
PI_HOST="192.168.1.12"
PI_PATH="/home/pi/ROV-SOFTWARE"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}⚡ Quick Update - Smart Deployment${NC}"
echo "====================================="

# Check if Pi is reachable
echo -e "${YELLOW}🔍 Checking Pi connection...${NC}"
if ! ping -c 1 $PI_HOST > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot reach Pi at $PI_HOST${NC}"
    exit 1
fi

# Function to check if requirements.txt changed
check_dependencies_changed() {
    if [ ! -f ".last_requirements_hash" ]; then
        echo "true"
        return
    fi
    
    current_hash=$(md5sum requirements.txt | cut -d' ' -f1)
    last_hash=$(cat .last_requirements_hash)
    
    if [ "$current_hash" != "$last_hash" ]; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to copy only changed files
copy_changed_files() {
    echo -e "${YELLOW}📤 Copying changed files to Pi...${NC}"
    
    # Create a temporary tar with only changed files
    rsync -av --delete \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='rov-venv' \
        --exclude='*.tar' \
        --exclude='.dockerignore' \
        --exclude='Dockerfile' \
        --exclude='docker-compose*.yml' \
        --exclude='*.sh' \
        --exclude='README.md' \
        --exclude='pyproject.toml' \
        --exclude='*.egg-info' \
        --exclude='dist' \
        --exclude='build' \
        . $PI_USER@$PI_HOST:$PI_PATH/
    
    echo -e "${GREEN}✅ Files copied${NC}"
}

# Function to rebuild and deploy full image
full_deploy() {
    echo -e "${YELLOW}🐳 Dependencies changed - rebuilding full image...${NC}"
    ./docker-update.sh
}

# Function to restart services with new code
restart_services() {
    echo -e "${YELLOW}🔄 Restarting services with new code...${NC}"
    ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose restart"
    echo -e "${GREEN}✅ Services restarted with new code${NC}"
}

# Main logic
deps_changed=$(check_dependencies_changed)

if [ "$deps_changed" = "true" ]; then
    echo -e "${YELLOW}📦 Dependencies changed - full rebuild needed${NC}"
    full_deploy
    # Save new hash
    md5sum requirements.txt | cut -d' ' -f1 > .last_requirements_hash
else
    echo -e "${GREEN}📝 Only code changes - quick update possible${NC}"
    copy_changed_files
    restart_services
fi

echo -e "${GREEN}✅ Update complete!${NC}"
echo ""
echo "Update type: $([ "$deps_changed" = "true" ] && echo "Full rebuild" || echo "Quick code update")"
echo "Time saved: $([ "$deps_changed" = "true" ] && echo "0" || echo "~2+ minutes")"
