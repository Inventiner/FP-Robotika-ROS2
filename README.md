# ROS 2 Autonomous Mapping Robot (Roomba Simulation)

This project is a ROS 2 Humble and Gazebo Fortress simulation of a vacuum-cleaning robot that can autonomously explore and map an unknown environment. It uses a custom robot model and a "wall-following" algorithm to create a 2D map suitable for autonomous navigation.

<img width="1915" height="1072" alt="Screenshot of simulation" src="https://github.com/user-attachments/assets/c8febf14-3466-48fd-a8d8-001ceebcee64" />

## Features

-   **Custom Gazebo World:** A modified "Cafe on an Island" environment with fixed collision geometry for realistic physics.
-   **Custom Robot Model:** A stable, 4-wheeled robot with a Lidar sensor, built from scratch in URDF.
-   **Autonomous Exploration:** The robot uses a 4-state PID wall-following algorithm to intelligently trace the perimeter of the environment without human intervention.
-   **SLAM Integration:** Uses the standard `slam_toolbox` to generate a 2D occupancy grid map from Lidar data and odometry.
-   **Visualization:** Comes with a pre-configured RViz setup to visualize the map-building process in real-time.

## Assets Used

This simulation would not be possible without the excellent free models provided by the community on the Gazebo Fuel platform.

-   **[Cafe Model](https://app.gazebosim.org/OpenRobotics/fuel/models/Cafe):** The primary environment for the robot, used as a local asset. Created by Open Robotics.
-   **[Null Island Model](https://app.gazebosim.org/OpenRobotics/fuel/worlds/Null%20Island):** The island terrain used in the world. Created by Open Robotics.

These assets are used in accordance with their respective licenses.

## System Requirements

-   Ubuntu 22.04
-   ROS 2 Humble Hawksbill
-   Gazebo Fortress (comes with the full ROS 2 desktop install)
-   `colcon` build tool

## Installation & Setup

1.  **Clone the Repository:**
    Clone this repository into your `ros2_ws/src` directory.

2.  **Install Dependencies:**
    Run the installation script to get all the necessary ROS 2 packages.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

3.  **Build the Workspace:**
    Compile the packages using `colcon`.
    ```bash
    colcon build
    ```

## How to Run

This project is designed for autonomous mapping. The main launch file will start the simulation, the mapping node, and the robot's autonomous driving logic all at once.

1.  **Source the Workspace:**
    Open a terminal and navigate to your `ros2_ws`.
    ```bash
    source install/setup.bash
    ```

2.  **Run the Simulation:**
    Use the provided script to launch everything.
    ```bash
    chmod +x run_sim.sh
    ./run_sim.sh
    ```

    This will open:
    -   A Gazebo window with the robot in the cafe.
    -   An RViz window to visualize the map.
    -   The robot will start moving and mapping on its own.

3.  **Stop the Simulation:**
    To cleanly shut down all processes (Gazebo, RViz, ROS nodes), use the stop script.
    ```bash
    chmod +x stop_sim.sh
    ./stop_sim.sh
    ```
    (Using `Ctrl+C` in the launch terminal also works, but this is a failsafe).

## Project Structure

-   `src/my_robot_pkg`: The "brain" of the robot. Contains the Python node for autonomous wall-following (`cleaning_node.py`).
-   `src/robo_roomba_sim`: The "body" and "world" of the robot. Contains the URDF model, Gazebo world file, launch files, and RViz configurations.

## Next Steps

After successfully generating and saving a map using `autonomous_mapping`, the next phase is to use that map for path planning and full-coverage cleaning using the Nav2 stack.