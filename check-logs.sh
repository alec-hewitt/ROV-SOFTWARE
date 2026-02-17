#!/bin/bash

# Check ROV logs on Pi
PI_USER="pi"
PI_HOST="192.168.1.12"
PI_PATH="/home/pi/ROV-SOFTWARE"

echo "📋 Checking ROV logs on Pi..."

# List log files
echo "📁 Log files available:"
ssh $PI_USER@$PI_HOST "ls -la $PI_PATH/logging/"

# Show most recent log file
echo ""
echo "📖 Most recent log content:"
ssh $PI_USER@$PI_HOST "cd $PI_PATH && ls -t logging/ROVLOG_*.log | head -1 | xargs cat | tail -50"
