#!/bin/bash
# Quick Build and Test Script for SLAM TF Fix

set -e  # Exit on error

echo "=================================="
echo "SLAM TF Fix - Build & Test Script"
echo "=================================="
echo ""

# Check if robot_localization is installed
echo "1. Checking dependencies..."
if ! dpkg -l | grep -q ros-humble-robot-localization; then
    echo "⚠️  Installing robot_localization..."
    sudo apt update
    sudo apt install -y ros-humble-robot-localization
else
    echo "✓ robot_localization is installed"
fi

# Build the workspace
echo ""
echo "2. Building workspace..."
cd ~/ros2_ws
colcon build --packages-select robo_roomba_sim --symlink-install

if [ $? -eq 0 ]; then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

# Source the workspace
echo ""
echo "3. Sourcing workspace..."
source install/setup.bash
echo "✓ Workspace sourced"

echo ""
echo "=================================="
echo "Build complete! Ready to test."
echo "=================================="
echo ""
echo "To launch the simulation, run:"
echo "  ros2 launch robo_roomba_sim mapping_launch.py"
echo ""
echo "To verify the TF tree, run in another terminal:"
echo "  ros2 run tf2_tools view_frames"
echo "  ros2 run tf2_ros tf2_echo odom base_link"
echo ""
