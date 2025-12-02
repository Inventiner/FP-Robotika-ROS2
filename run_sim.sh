#!/bin/bash

# -------------------------------
# Tugbot ROS2 Run Script
# -------------------------------

SETUP_SCRIPT="install/setup.bash"

if [ ! -f "$SETUP_SCRIPT" ]; then
    echo "Workspace not built. Run install.sh first."
    exit 1
fi

echo "Launching Tugbot simulation and nodes..."

gnome-terminal \
    --tab --title="Gazebo Simulation" -- bash -c "
        echo 'Starting Gazebo Simulation...';
        source $SETUP_SCRIPT;
        ros2 launch tugbot_gazebo tugbot_depot.launch.py;
        exec bash
    "

gnome-terminal \
    --tab --title="Lidar Processor" -- bash -c "
        echo 'Starting Lidar Processor Node...';
        sleep 5;
        source $SETUP_SCRIPT;
        ros2 run my_robot_pkg lidar_processor;
        exec bash
    "

gnome-terminal \
    --tab --title="Robot Driver" -- bash -c "
        echo 'sStarting Robot Driver Node...';
        sleep 10;
        source $SETUP_SCRIPT;
        ros2 run my_robot_pkg robot_driver;
        exec bash
    "

echo "All nodes launched in new GNOME Terminal tabs."
