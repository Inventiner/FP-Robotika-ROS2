#!/bin/bash

echo "Stopping simulation and ROS 2 nodes..."

# Stop Ignition Gazebo
echo "Stopping Ignition Gazebo..."
pkill -f 'ign gazebo*'
pkill -f gzserver     # Older versions of Ignition/Gazebo Classic
pkill -f gzclient     # If the GUI was launched

# Stop ROS 2 custom nodes
echo "Stopping custom ROS 2 nodes..."
pkill -f lidar_processor
pkill -f robot_driver
pkill -f tugbot_depot.launch.py

echo "✅ All simulation processes stopped."
