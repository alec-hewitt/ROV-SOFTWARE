#!/bin/bash

# Simple Pi Management Script
# Run from your laptop to manage the ROV software on Pi

set -e

PI_USER="pi"
PI_HOST="192.168.1.12"
PI_PATH="/home/pi/ROV-SOFTWARE"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🤖 Pi Management Script${NC}"
echo "=========================="

case "${1:-help}" in
    "status")
        echo -e "${YELLOW}📊 Checking Pi status...${NC}"
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose ps"
        ;;
    "logs")
        echo -e "${YELLOW}📋 Showing Pi logs...${NC}"
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose logs -f"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting services on Pi...${NC}"
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose restart"
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping services on Pi...${NC}"
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose down"
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    "start")
        echo -e "${YELLOW}🚀 Starting services on Pi...${NC}"
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && docker-compose up -d"
        echo -e "${GREEN}✅ Services started${NC}"
        ;;
    "update")
        echo -e "${YELLOW}🚀 Updating software on Pi...${NC}"
        ./docker-update.sh
        ;;
    "cleanup")
        echo -e "${YELLOW}🧹 Cleaning up Pi disk space...${NC}"
        ssh $PI_USER@$PI_HOST "docker system prune -af --volumes && docker image prune -af"
        echo -e "${GREEN}✅ Cleanup complete${NC}"
        ;;
    "help"|*)
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  status     Check container status on Pi"
        echo "  logs       View logs from Pi (Ctrl+C to exit)"
        echo "  restart    Restart services on Pi"
        echo "  stop       Stop services on Pi"
        echo "  start      Start services on Pi"
        echo "  update     Update and redeploy software on Pi"
        echo "  cleanup    Clean up Docker images and containers on Pi"
        echo "  help       Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 status     # Check if services are running"
        echo "  $0 logs       # View live logs"
        echo "  $0 restart    # Restart if something's wrong"
        echo "  $0 update     # Deploy latest changes"
        echo "  $0 cleanup    # Free up disk space on Pi"
        ;;
esac
