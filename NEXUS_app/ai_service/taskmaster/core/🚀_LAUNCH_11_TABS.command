#!/bin/bash

# 🚀 LAUNCH 11-TAB COLLECTIVE WORKER SYSTEM
# 8 Core Workers + 3 Processing Engines

echo "🚀 Launching 11-Tab Collective Worker System..."
echo "=================================================="

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
required_files=(
    "collective_worker_processor.py"
    "monitor_collective_system.py" 
    "todo_master_reader.py"
    "todo_processing_engine.py"
    "task_breakdown_engine.py"
    "launch_11_tab_system.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files found"

# Launch the 11-tab system
echo "🚀 Starting 11-tab system launcher..."
python3 launch_11_tab_system.py

# Check if launch was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 System launched successfully!"
    echo "📱 11-tab system is now running:"
    echo "   🔧 Tabs 1-8: Core Worker Processes"
    echo "   🔧 Tab 9: TODO Processing Engine"
    echo "   ⚡ Tab 10: Task Breakdown Engine"
    echo "   📊 Tab 11: System Monitor & Analytics"
    echo ""
    echo "💡 System Features:"
    echo "   - 8 Core Workers processing TODOs with 15-second intervals"
    echo "   - TODO Processing Engine managing lifecycle and updates"
    echo "   - Task Breakdown Engine converting complex TODOs to microtasks"
    echo "   - Real-time monitoring and analytics"
    echo "   - Automatic TODO_MASTER.md updates after completion"
else
    echo ""
    echo "💥 Failed to launch system"
    echo "Please check the error messages above"
fi

echo ""
echo "Press any key to exit..."
read -n 1
