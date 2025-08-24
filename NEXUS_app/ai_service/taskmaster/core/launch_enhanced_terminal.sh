#!/bin/bash
# Enhanced macOS Terminal Launcher - 12 Tabs
# Launches Terminal.app with enhanced collective system

echo "🚀 Enhanced macOS Terminal Launcher - 12 Tabs"
echo "=============================================="
echo " Opening Terminal.app with enhanced collective system"
echo ""

# Change to the correct directory
cd "$(dirname "$0")"
echo "�� Working directory: $(pwd)"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if virtual environment exists
if [ -d "../.venv" ]; then
    echo "✅ Virtual environment found at ../.venv"
else
    echo "❌ Virtual environment not found at ../.venv"
    echo "   Please run: python3 -m venv .venv"
    exit 1
fi

# Check if enhanced engines exist
echo ""
echo "🔍 Checking enhanced engines..."
enhanced_engines=(
    "enhanced_todo_processing_engine.py"
    "enhanced_task_breakdown_engine.py"
    "enhanced_dynamic_worker_coordinator.py"
)

for engine in "${enhanced_engines[@]}"; do
    if [ -f "$engine" ]; then
        echo "   ✅ $engine"
    else
        echo "   ❌ $engine - MISSING!"
        echo "   Please ensure all enhanced engines are created."
        exit 1
    fi
done

echo ""
echo "�� Launching Enhanced 12-Tab Terminal System..."
echo "   This will open Terminal.app with:"
echo "   - 8 Enhanced Collective Workers (Tabs 1-8)"
echo "   - Enhanced TODO Processing Engine (Tab 9)"
echo "   - Enhanced Task Breakdown Engine (Tab 10)"
echo "   - Enhanced Dynamic Worker Coordinator (Tab 11)"
echo "   - System Monitor (Tab 12)"
echo ""

# Launch the enhanced terminal system using Python
echo "🔧 Executing Python launcher..."
python3 launch_macos_12_tabs_enhanced.py

# Check if the Python launcher was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Enhanced Terminal System launched successfully!"
    echo ""
    echo "📱 Terminal.app window opened with 12 tabs:"
    echo "   Tab 1-8: Enhanced Collective Workers (Processing TODOs)"
    echo "   Tab 9: Enhanced TODO Processing Engine (Collective Intelligence)"
    echo "   Tab 10: Enhanced Task Breakdown Engine (Collaborative Microtasks)"
    echo "   Tab 11: Enhanced Dynamic Worker Coordinator (Capacity Management)"
    echo "   Tab 12: System Monitor (Real-time Analytics)"
    echo ""
    echo "🎯 Enhanced System Features:"
    echo "   - Capacity Limits: Max 5 active tasks, Max 12 total TODOs"
    echo "   - Conflict Prevention: Automatic task marking to prevent conflicts"
    echo "   - Collective Intelligence: Workers coordinate for optimal performance"
    echo "   - Enhanced Processing: 6-12 second intervals for faster processing"
    echo "   - Virtual Environment: All tabs use project .venv"
    echo "   - Custom Tab Titles: Easy identification of each component"
    echo ""
    echo "�� Each tab is now:"
    echo "   - In the correct directory (core)"
    echo "   - Using the virtual environment (.venv)"
    echo "   - Running the appropriate enhanced engine"
    echo "   - Ready for collective processing"
    echo ""
    echo "🚀 The enhanced collective system is now running!"
    echo "   Check each tab to see the engines in action"
else
    echo ""
    echo "❌ Failed to launch Enhanced Terminal System"
    echo "   Please check the error messages above"
    exit 1
fi

echo ""
echo "🎉 Enhanced Terminal System setup complete!"
echo "   You can now monitor all 12 tabs in the Terminal.app window"
