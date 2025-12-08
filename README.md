# ROS 2 Autonomous Mapping Robot (Roomba Simulation)

This project is a ROS 2 Humble and Gazebo Fortress simulation of a vacuum-cleaning robot that can autonomously explore and map an unknown environment. It uses a custom robot model and a "wall-following" algorithm to create a 2D map suitable for autonomous navigation.

<img width="1915" height="1072" alt="Screenshot of simulation" src="https://github.com/user-attachments/assets/c8febf14-3466-48fd-a8d8-001ceebcee64" />

## Features

-   **Custom Gazebo World:** A modified "Cafe on an Island" environment with fixed collision geometry for realistic physics.
-   **Custom Robot Model:** A stable, 4-wheeled robot with a Lidar sensor, built from scratch in URDF.
-   **Autonomous Exploration:** The robot uses a 4-state PID wall-following algorithm to intelligently trace the perimeter of the environment without human intervention.
-   **SLAM Integration:** Uses the standard `slam_toolbox` to generate a 2D occupancy grid map from Lidar data and odometry.
-   **Visualization:** Comes with a pre-configured RViz setup to visualize the map-building process in real-time.
-   **Indonesian Comments:** All helper scripts and source codes are commented in Bahasa Indonesia for educational purposes.

## Assets Used

This simulation relies on models provided by the community on the Gazebo Fuel platform:

-   **[Cafe Model](https://app.gazebosim.org/OpenRobotics/fuel/models/Cafe):** The primary environment for the robot. Created by Open Robotics.
-   **[Null Island Model](https://app.gazebosim.org/OpenRobotics/fuel/worlds/Null%20Island):** The island terrain used in the world. Created by Open Robotics.

## System Requirements

-   **OS:** Windows (WSL2 recommended) or Linux (Ubuntu 22.04 LTS)
-   **ROS Distribution:** ROS 2 Humble Hawksbill
-   **Simulator:** Gazebo Fortress
-   **Build Tool:** `colcon`

## Installation & Setup

1.  **Clone the Repository:**
    Clone this repository into your `ros2_ws/src` directory.
    ```bash
    cd ~/ros2_ws/src
    git clone <repository_url>
    ```

2.  **Install Dependencies:**
    Run the installation script to get all the necessary ROS 2 packages.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

    *Note: `install.sh` installs packages like `slam_toolbox`, `navigation2`, `ros_gz`, etc.*

3.  **Build the Workspace:**
    Compile the packages using `colcon`.
    ```bash
    cd ~/ros2_ws
    colcon build
    ```

## Usage Guide

### 1. Autonomous Mapping (Mapping Mode)

This mode allows the robot to explore the environment autonomously and generate a map.

**Run:**
```bash
./run_mapping.sh
```

**What it does:**
-   Launches Gazebo with the Cafe world.
-   Spawns the Roomba robot.
-   Starts `scan_remapper` and `odom_to_tf` nodes to bridge Gazebo and ROS 2.
-   Starts `slam_toolbox` for mapping.
-   Starts `cleaning_node.py` (Autonomous Wall Follower) to drive the robot.
-   Opens RViz to visualize the map being built.

**To Save the Map:**
Once the robot has explored enough, run the following command in a **new terminal**:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

### 2. Coverage Cleaning (Navigation Mode)

This mode uses an existing map to perform a cleaning task (zig-zag coverage pattern).

**Run:**
```bash
./run_cleaning.sh
```

*Note: You must have a saved map before running this, or configure the launch file to point to your map.*

### 3. Stopping the Simulation

To cleanly shut down all processes (Gazebo, RViz, ROS nodes):
```bash
./stop_sim.sh
```

## Project Structure

### `src/my_robot_pkg`
The "brain" of the robot. Contains the Python nodes for logic and control.
-   **`cleaning_node.py`**: Implementation of the Wall-Following algorithm (Finite State Machine).
-   **`coverage_cleaner.py`**: Node for coverage path planning (Zig-Zag pattern) using Nav2.
-   **`odom_to_tf.py`**: Converts Odometry messages to TF transforms (fixes simulation time issues).
-   **`scan_remapper.py`**: Remaps LaserScan frame IDs to match standard conventions (removes `roomba/` prefix).
-   **`tf_alias_helper.py`** & **`tf_prefix_remover.py`**: Helpers to manage TF frame names between Gazebo and ROS 2.

### `src/robo_roomba_sim`
The "body" and "world".
-   **`urdf/roomba.urdf.xacro`**: The robot description file.
-   **`worlds/indoor.sdf`**: The Gazebo world environment.
-   **`launch/`**: Launch files for different modes (`autonomous_mapping.launch.py`, `localization_launch.py`, etc.).
-   **`config/`**: Configuration files for SLAM and Nav2.

## Troubleshooting

-   **Robot not moving?** Check if `ros_gz_bridge` is running correctly. Verify `/cmd_vel` topic is connected.
-   **Map not appearing?** Ensure `scan_remapper` is running and `/scan` topic has data. Check TF tree (`ros2 run tf2_tools view_frames`).
-   **Build fails?** Make sure you have sourced ROS 2 (`source /opt/ros/humble/setup.bash`) before running `colcon build`.

---
*Created by Firania. Documented and Commented in Bahasa Indonesia.*