#!/bin/bash

echo "============================================"
echo "Stopping all ROS 2 and Gazebo processes..."
echo "============================================"

# Kill all processes related to the launch file
pkill -f "ros2 launch robo_roomba_sim"

# Kill specific nodes and processes just in case
pkill -f gzserver
pkill -f gzclient
pkill -f rviz2
pkill -f cleaning_node
pkill -f slam_toolbox
pkill -f robot_state_publisher
pkill -f parameter_bridge

echo "============================================"
echo "All processes stopped."
echo "============================================"