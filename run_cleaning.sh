#!/bin/bash

# Get the directory of this script to run commands from the workspace root
# (Mendapatkan direktori skrip ini untuk menjalankan perintah dari root workspace)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "============================================"
echo "Building and launching Coverage Cleaning..."
echo "============================================"

# Build the workspace
# (Membangun workspace)
echo "--> Building with colcon..."
colcon build

# Source the workspace
# (Source workspace agar environment variable ROS 2 termuat)
echo "--> Sourcing the workspace..."
source install/setup.bash

# Function to handle cleanup on exit
# (Fungsi untuk menangani pembersihan saat keluar)
cleanup() {
    echo ""
    echo "--> Stopping simulation..."
    # Kill the process group
    # (Menghentikan grup proses)
    kill 0
}

# Trap SIGINT (Ctrl+C) and EXIT to run cleanup
# (Menangkap sinyal SIGINT (Ctrl+C) dan EXIT untuk menjalankan pembersihan)
trap cleanup SIGINT EXIT

# Launch the simulation in the background
# (Menjalankan simulasi di background)
echo "--> Launching simulation (localization_launch.py)..."
ros2 launch robo_roomba_sim localization_launch.py &

# Wait for simulation to spin up
# (Menunggu simulasi berjalan sepenuhnya)
echo "--> Waiting 15 seconds for simulation to initialize..."
sleep 15

# Run the coverage cleaner node
# (Menjalankan node coverage cleaner)
echo "--> Starting Coverage Cleaner Node..."
ros2 run my_robot_pkg coverage_cleaner

# Wait for user to exit
# (Menunggu pengguna untuk keluar)
echo "--> Mission complete or node stopped. Press Ctrl+C to stop simulation."
wait
