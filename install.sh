#!/bin/bash

echo "==================================================="
echo " Installing ROS 2 Dependencies for Humble... "
echo "==================================================="

# Update package lists
# (Memperbarui daftar paket)
sudo apt update

# Install core robotics packages needed for this project
# (Menginstal paket robotika inti yang dibutuhkan untuk proyek ini)
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-ros-gz-interfaces \
  ros-humble-teleop-twist-keyboard

echo "==================================================="
echo " Installation complete! Ready to build. "
echo "==================================================="