#!/bin/bash

echo "==================================================="
echo " Installing ROS 2 Dependencies for Humble... "
echo "==================================================="

# Update package lists
sudo apt update

# Install core robotics packages needed for this project
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-teleop-twist-keyboard

echo "==================================================="
echo " Installation complete! Ready to build. "
echo "==================================================="