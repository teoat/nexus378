#!/bin/bash

# 🚀 LAUNCH SIMPLE 9-WORKER SYSTEM
# One-click launcher for the collective worker system

echo "🚀 Launching Simple 9-Worker System..."
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📍 Working directory: $SCRIPT_DIR"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 and try again."
    exit 1
fi

# Check if required files exist
echo "🔍 Checking required files..."
required_files=("collective_worker_processor.py" "monitor_collective_system.py" "todo_master_reader.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files found"

# Launch the simple Python launcher
echo "🚀 Starting simple 9-worker system launcher..."
python3 launch_simple_9_workers.py

# Check if launch was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 System launched successfully!"
    echo "📱 8 worker processes + 1 monitor process are now running"
    echo "🔧 Workers: Processing TODOs from TODO_MASTER.md"
    echo "📊 Monitor: System health and performance dashboard"
else
    echo ""
    echo "💥 Failed to launch system"
    echo "Please check the error messages above"
fi

echo ""
echo "Press any key to exit..."
read -n 1
