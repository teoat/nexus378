#!/bin/bash
# Enhanced macOS Terminal Launcher - 12 Tabs
# One-click script to launch Terminal.app with enhanced collective system

echo "🚀 Enhanced macOS Terminal Launcher - 12 Tabs"
echo "=============================================="
echo " Opening Terminal.app with enhanced collective system"
echo ""

# Change to the correct directory
cd "$(dirname "$0")"
echo " Working directory: $(pwd)"

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

echo ""
echo " Launching Enhanced 12-Tab Terminal System..."
echo "   This will open Terminal.app with:"
echo "   - 8 Enhanced Collective Workers (Tabs 1-8)"
echo "   - Enhanced TODO Processing Engine (Tab 9)"
echo "   - Enhanced Task Breakdown Engine (Tab 10)"
echo "   - Enhanced Dynamic Worker Coordinator (Tab 11)"
echo "   - System Monitor (Tab 12)"
echo ""

# Launch the enhanced terminal system
python3 launch_macos_12_tabs_enhanced.py

echo ""
echo "✅ Enhanced Terminal System launcher completed."
echo "   Check Terminal.app for the new window with 12 tabs."
