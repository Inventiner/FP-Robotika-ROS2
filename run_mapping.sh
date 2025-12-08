#!/bin/bash

# Get the directory of this script to run commands from the workspace root
# (Mendapatkan direktori skrip ini untuk menjalankan perintah dari root workspace)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "============================================"
echo "Building and launching Autonomous Mapping..."
echo "============================================"

# Build the workspace
# (Membangun workspace menggunakan colcon)
echo "--> Building with colcon..."
colcon build

# Source the workspace
# (Source workspace untuk memuat environment)
echo "--> Sourcing the workspace..."
source install/setup.bash

# Launch the main application
# (Menjalankan aplikasi utama simulasi)
echo "--> Launching simulation..."
ros2 launch robo_roomba_sim autonomous_mapping.launch.py