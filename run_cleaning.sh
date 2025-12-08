#!/bin/bash

# Get the directory of this script to run commands from the workspace root
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "============================================"
echo "Building and launching Coverage Cleaning..."
echo "============================================"

# Build the workspace
echo "--> Building with colcon..."
colcon build

# Source the workspace
echo "--> Sourcing the workspace..."
source install/setup.bash

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "--> Stopping simulation..."
    # Kill the process group
    kill 0
}

# Trap SIGINT (Ctrl+C) and EXIT to run cleanup
trap cleanup SIGINT EXIT

# Launch the simulation in the background
echo "--> Launching simulation (localization_launch.py)..."
ros2 launch robo_roomba_sim localization_launch.py &

# Wait for simulation to spin up
echo "--> Waiting 15 seconds for simulation to initialize..."
sleep 15

# Run the coverage cleaner node
echo "--> Starting Coverage Cleaner Node..."
ros2 run my_robot_pkg coverage_cleaner

# Wait for user to exit
echo "--> Mission complete or node stopped. Press Ctrl+C to stop simulation."
wait
