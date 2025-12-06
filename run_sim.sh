#!/bin/bash

# Get the directory of this script to run commands from the workspace root
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "============================================"
echo "Building and launching Autonomous Mapping..."
echo "============================================"

# Build the workspace
echo "--> Building with colcon..."
colcon build

# Source the workspace
echo "--> Sourcing the workspace..."
source install/setup.bash

# Launch the main application
echo "--> Launching simulation..."
ros2 launch robo_roomba_sim autonomous_mapping.launch.py