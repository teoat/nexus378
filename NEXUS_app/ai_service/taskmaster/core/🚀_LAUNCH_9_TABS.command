#!/bin/bash

# 🚀 LAUNCH 9-TAB COLLECTIVE WORKER SYSTEM
# One-click launcher for macOS

echo "🚀 Launching Collective Worker System..."
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

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only"
    echo "Please use the appropriate launcher for your operating system"
    exit 1
fi

# Launch the 9-tab system
echo "🚀 Starting 9-tab system launcher..."
python3 launch_macos_9_tabs.py

# Check if launch was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 System launched successfully!"
    echo "📱 Check your Terminal for the new 9-tab window"
    echo "🔧 Tabs 1-8: Worker processes"
    echo "📊 Tab 9: System monitor"
else
    echo ""
    echo "💥 Failed to launch system"
    echo "Please check the error messages above"
fi

echo ""
echo "Press any key to exit..."
read -n 1
