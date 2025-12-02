# Tugbot Simple Obstacle Avoidance in ROS 2

This repository contains a complete ROS 2 workspace demonstrating a basic obstacle avoidance system for the Tugbot in the Gazebo simulator.

The system uses two simple Python nodes that work together:

1.  **Lidar Processor (`lidar_processor_node.py`)**: Subscribes to the Tugbot's laser scan data, detects if an obstacle is within a safety threshold, and publishes a simple `True`/`False` warning.
2.  **Robot Driver (`robot_driver_node.py`)**: Subscribes to the warning topic. It drives the robot forward when the path is clear (`False`) and stops and turns when an obstacle is detected (`True`).

## System Architecture

The data flows through the ROS 2 topics as follows:

```
[Gazebo Lidar Sensor]
       |
       | Publishes sensor_msgs/LaserScan
       v
/world/world_demo/model/tugbot/.../scan  (Topic)
       |
       | Subscribed by
       v
[Lidar Processor Node]
       |
       | Publishes std_msgs/Bool
       v
/collision_warning (Topic)
       |
       | Subscribed by
       v
[Robot Driver Node]
       |
       | Publishes geometry_msgs/Twist
       v
/model/tugbot/cmd_vel (Topic)
       |
       | Controls
       v
[Tugbot in Gazebo]
```

## Prerequisites

Before you begin, ensure you have the following installed on your system (Ubuntu 22.04 recommended):

*   **ROS 2 Humble Hawksbill**: [Installation Guide](https://docs.ros.org/en/humble/Installation.html)
*   **Gazebo Simulator**: Usually included with the `ros-humble-desktop` installation.
*   **Colcon**: The standard ROS 2 build tool (`sudo apt install python3-colcon-common-extensions`).
*   **Git**: For cloning this repository.

## Installation and Setup

This repository is a self-contained workspace, making setup straightforward.

### Installation Using Script

To simplify setup, you can use the provided install.sh script to build the workspace and prepare the environment automatically.

From the root of the workspace (PubSub-ROS2), run:

```
./install.sh
```

This script will:
- Source your ROS 2 environment
- Build all packages using colcon build
- Set up the necessary environment for simulation

> [!NOTE]  
> If the script fails, make sure it is executable:
> ```
> chmod +x install.sh
> ```

### Manual Installation 

#### 1. Clone the Repository

Clone this entire repository to your local machine.

```bash
git clone https://github.com/Inventiner/PubSub-ROS2.git
cd PubSub-ROS2
```

#### 2. Verify the File Structure

Your workspace (`PubSub-ROS2`) must contain the following structure for the build to succeed. The `tugbot_ros2_pkgs` is for the simulation, and `my_robot_pkg` is for your custom logic.

```
PubSub-ROS2/
├── src/
│   ├── tugbot_ros2_pkgs/      # Simulation package
│   │   └── ...
│   └── my_robot_pkg/          # Your custom package
│       ├── package.xml
│       ├── setup.cfg
│       ├── setup.py           # The setup file you provided
│       └── my_robot_pkg/
│           ├── __init__.py
│           ├── lidar_processor_node.py  <-- Lidar processing script
│           └── robot_driver_node.py     <-- Robot driving script
└── ...
```

#### 3. Build the Workspace

From the root of the workspace (`PubSub-ROS2`), run `colcon build`. This will compile the packages and make your Python nodes executable.

```bash
# Make sure you are in the root of the workspace (e.g., ~/)
colcon build 
```

## Running the Simulation

### Run the Simulation Using Script

Instead of launching each component in a separate terminal manually, you can use the provided script to automatically launch the simulation and all ROS 2 nodes in GNOME Terminal tabs.

1. Start the Simulation

From the root of your workspace, run:

```
./run_sim.sh
```
This script will:
- Launch Ignition Gazebo with the Tugbot
- Start the Lidar Processor node
- Start the Robot Driver node
- Each will open in a new GNOME Terminal tab for easy monitoring.

### 2. Stop the Simulation

To cleanly shut down all simulation components, use the provided stop_sim.sh script:
```
./stop_sim.sh

```

This script will stop:
- Ignition Gazebo
- Gazebo Classic (if running)
- Lidar Processor node
- Robot Driver node

> [!NOTE] Make sure stop_simulation.sh is executable:
> ``` chmod +x stop_sim.sh ```

### Manual Run
To run the full demo, you will need **three separate terminals**.

> [!IMPORTANT] 
> In **each new terminal** you open, you must first source the workspace's setup file. This allows ROS 2 to find the packages and executables you just built.

```bash
# From the root of your workspace (e.g., ~/PubSub-ROS2)
source install/setup.bash
```

---

#### **Terminal 1: Launch the Gazebo Simulation**

This command starts the Gazebo simulator with the Tugbot in the depot world.

```bash
ros2 launch tugbot_gazebo tugbot_depot.launch.py
```
Wait for the Gazebo window to appear and the robot model to load.

---

#### **Terminal 2: Run the Lidar Processor Node**

This node reads the Lidar data and publishes collision warnings. The executable name `lidar_processor` is defined in your `setup.py`.

```bash
ros2 run my_robot_pkg lidar_processor
```
You should see the output: `[INFO] [lidar_processor_node]: Lidar Processor Node started. Publishing danger warnings.`

---

#### **Terminal 3: Run the Robot Driver Node**

This node listens for the warnings and controls the robot. The executable name `robot_driver` is also defined in your `setup.py`. As soon as you run this, the robot will start moving.

```bash
ros2 run my_robot_pkg robot_driver
```
You should see the output: `[INFO] [robot_driver_node]: Robot Driver Node started. Awaiting warnings.` followed by `[INFO] [robot_driver_node]: Path is clear. Moving forward.`

Now, watch the robot in Gazebo! It will drive forward until it gets close to an object, at which point it will stop and turn away before continuing.

## Customization

You can easily tweak the robot's behavior by editing the Python scripts located in `src/my_robot_pkg/my_robot_pkg/`.

*   **To change the safety distance:**
    *   Edit `src/my_robot_pkg/my_robot_pkg/lidar_processor_node.py`.
    *   Modify the `self.safety_threshold` value (in meters).
    ```python
    # In LidarProcessorNode class
    self.safety_threshold = 0.5  # Change this value (e.g., to 0.75 for more caution)
    ```

*   **To change the robot's speed or turning rate:**
    *   Edit `src/my_robot_pkg/my_robot_pkg/robot_driver_node.py`.
    *   Modify the `command.linear.x` (forward speed) or `command.angular.z` (turning speed) values.
    ```python
    # In RobotDriverNode's collision_callback method
    command.linear.x = 0.2  # Forward speed in m/s
    command.angular.z = 0.5  # Turning speed in rad/s
    ```
