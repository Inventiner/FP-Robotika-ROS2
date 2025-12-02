#!/bin/bash

# -------------------------------
# Tugbot ROS2 Setup Script
# -------------------------------

set -e

echo "Setting up Tugbot ROS2 workspace..."

# Install dependencies
echo "Installing ROS 2 and build tool dependencies..."
sudo apt update
sudo apt install -y \
    ros-humble-desktop \
    ros-humble-ros-gz \
    python3-colcon-common-extensions

# Source ROS 2 setup
source /opt/ros/humble/setup.bash

# Build the workspace
echo "Building the workspace..."

# Create missing directory
MAP_DIR="src/tugbot_ros2_pkgs/tugbot_navigation2/map"

if [ ! -d "$MAP_DIR" ]; then
    echo "Creating missing directory: $MAP_DIR"
    mkdir -p "$MAP_DIR"
else
    echo "Directory exists: $MAP_DIR"
fi

colcon build --symlink-install

source install/setup.bash

echo "Tugbot workspace setup complete!"
echo "To run the simulation, simply run \"run_sim.sh\" script "
