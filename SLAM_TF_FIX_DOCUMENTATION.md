# SLAM TF Tree Fix - Complete Solution

## ROOT CAUSE ANALYSIS

The persistent "message filter dropping message" error from `slam_toolbox` was caused by a **missing TF transform** in the chain: `map -> odom -> base_link -> lidar_link`.

### Key Findings:

1. **URDF Configuration was CORRECT**: The `publish_odom_tf: false` setting prevented Gazebo from publishing transforms (which was causing the non-standard frame naming issues).

2. **Missing Link in TF Chain**: While Gazebo's DiffDrive plugin published `/odom` messages (nav_msgs/Odometry), no node was consuming these messages and publishing the corresponding `odom->base_link` TF transform.

3. **SLAM Toolbox Limitation**: In standard async mapping mode, `slam_toolbox` expects the `odom->base_link` transform to already exist. It only publishes `map->odom`. Without the middle transform, the TF tree was disconnected.

## THE SOLUTION: Separation of Concerns

### Architecture Overview:
```
┌─────────────────────────────────────────────────────────────┐
│                     TF Transform Chain                       │
│                                                              │
│  map ──────> odom ──────> base_link ──────> lidar_link     │
│       │           │              │                           │
│       │           │              │                           │
│  slam_toolbox  robot_localization  robot_state_publisher    │
│                   (EKF)                                      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities:

1. **Gazebo (DiffDrive Plugin)**
   - **Job**: Simulate physics and publish raw odometry data
   - **Publishes**: `/odom` topic (nav_msgs/Odometry)
   - **Does NOT**: Publish any TF transforms

2. **robot_localization (EKF Node)**
   - **Job**: Fuse odometry data and publish the base odometry transform
   - **Subscribes**: `/odom` topic
   - **Publishes**: `odom->base_link` TF transform

3. **slam_toolbox**
   - **Job**: Build map and localize robot in map frame
   - **Subscribes**: `/scan` topic + TF tree (needs `odom->base_link`)
   - **Publishes**: `map->odom` TF transform + `/map` topic

4. **robot_state_publisher**
   - **Job**: Publish robot's internal joint/link transforms
   - **Publishes**: `base_link->lidar_link`, `base_link->wheel_link`, etc.

## FILES MODIFIED

### 1. `/src/robo_roomba_sim/urdf/roomba.urdf.xacro`
**Status**: ✅ Already correct (no changes needed)

**Key Configuration**:
```xml
<gazebo>
  <plugin filename="libignition-gazebo-diff-drive-system.so" 
          name="ignition::gazebo::systems::DiffDrive">
    <!-- ... wheel parameters ... -->
    <topic>/cmd_vel</topic>
    <odom_topic>/odom</odom_topic>
    <frame_id>odom</frame_id>
    <child_frame_id>base_link</child_frame_id>
    
    <!-- CRITICAL: Disable TF publishing from Gazebo -->
    <publish_odom_tf>false</publish_odom_tf>
  </plugin>
</gazebo>

<gazebo reference="lidar_link">
  <sensor name="lidar" type="gpu_lidar">
    <!-- CRITICAL: Use frame, not frame_id, to prevent prefixing -->
    <frame>lidar_link</frame>
    <topic>/scan</topic>
    <!-- ... sensor parameters ... -->
  </sensor>
</gazebo>
```

### 2. `/src/robo_roomba_sim/launch/sim_launch.py`
**Changes**: Added `use_sim_time: True` to robot_state_publisher

**Key Configuration**:
```python
# Bridge only data topics (no TF)
bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
        '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
        '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
        # NOTE: No /tf bridging - ROS 2 handles all transforms
    ],
    output='screen'
)

# Robot state publisher with sim time
node_robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[
        {'robot_description': robot_desc},
        {'use_sim_time': True}  # Added this
    ]
)
```

### 3. `/src/robo_roomba_sim/launch/mapping_launch.py`
**Changes**: Added robot_localization EKF node + custom SLAM config

**Key Configuration**:
```python
# Robot Localization (EKF) - THE MISSING PIECE!
robot_localization_node = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node',
    output='screen',
    parameters=[
        os.path.join(get_package_share_directory("robo_roomba_sim"),
                    "config", "ekf.yaml"),
        {'use_sim_time': True}
    ]
)

# Launch order matters: EKF first, then SLAM
return LaunchDescription([
    sim_launch,
    robot_localization_node,  # Establishes odom->base_link
    start_async_slam_toolbox_node,  # Establishes map->odom
    rviz
])
```

### 4. `/src/robo_roomba_sim/config/ekf.yaml` (NEW FILE)
**Purpose**: Configures robot_localization to consume `/odom` and publish TF

**Key Settings**:
```yaml
ekf_filter_node:
  ros__parameters:
    frequency: 30.0
    two_d_mode: true
    
    # Frame configuration
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom  # We work in odom frame (SLAM handles map)
    
    # Odometry input
    odom0: /odom
    odom0_config: [false, false, false,    # position (not used directly)
                   false, false, false,    # orientation (not used directly)
                   true,  true,  false,    # x_vel, y_vel (USED)
                   false, false, true,     # yaw_rate (USED)
                   false, false, false]    # acceleration (not available)
```

### 5. `/src/robo_roomba_sim/config/mapper_params_online_async.yaml` (NEW FILE)
**Purpose**: Custom SLAM toolbox configuration

**Key Settings**:
```yaml
slam_toolbox:
  ros__parameters:
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    
    mode: mapping
    publish_tf: true
    
    # ... additional tuning parameters ...
```

## VERIFICATION STEPS

After rebuilding and launching the simulation, verify the fix:

### 1. Check TF Tree Structure
```bash
ros2 run tf2_tools view_frames
```
**Expected**: A connected tree showing `map -> odom -> base_link -> lidar_link`

### 2. Test odom->base_link Transform
```bash
ros2 run tf2_ros tf2_echo odom base_link
```
**Expected**: Continuous transform output (no "frame does not exist" error)

### 3. Check Lidar Frame ID
```bash
ros2 topic echo --once /scan
```
**Expected**: 
```
header:
  frame_id: lidar_link  # Clean, no prefixes
```

### 4. Verify SLAM is Working
```bash
# Monitor slam_toolbox logs
ros2 topic echo /slam_toolbox/feedback
```
**Expected**: No "queue is full" errors, map should be building

### 5. RViz Configuration
- Set Fixed Frame: `map`
- Add displays: Map, LaserScan, RobotModel, TF
- **Expected**: Map builds as robot moves, all transforms visible

## BUILD AND RUN

```bash
# 1. Build the workspace
cd ~/ros2_ws
colcon build --packages-select robo_roomba_sim

# 2. Source the setup
source install/setup.bash

# 3. Launch the mapping simulation
ros2 launch robo_roomba_sim mapping_launch.py
```

## DEPENDENCIES

Ensure `robot_localization` is installed:
```bash
sudo apt install ros-humble-robot-localization
```

## WHY THIS FIX WORKS

1. **Single Responsibility**: Each component does one job well
   - Gazebo: Physics simulation only
   - robot_localization: Odometry fusion and TF publishing
   - slam_toolbox: Mapping and localization
   - robot_state_publisher: Robot internal transforms

2. **Proper TF Chain**: Every transform in the chain `map->odom->base_link->lidar_link` is now published by a dedicated node

3. **Time Synchronization**: All nodes use `use_sim_time: True` for consistent timing

4. **Standard ROS 2 Architecture**: This follows the recommended Nav2/SLAM stack design pattern

## TROUBLESHOOTING

### If you still see "queue is full" errors:
- Check: `ros2 topic hz /odom` (should be ~30-50 Hz)
- Check: `ros2 topic hz /scan` (should be ~10 Hz)
- Verify all nodes have `use_sim_time: True`

### If TF tree is still disconnected:
- Check: `ros2 node list` (ensure ekf_filter_node is running)
- Check: `ros2 topic echo /odom` (ensure odometry data is flowing)
- Check: `ros2 param get /ekf_filter_node world_frame` (should be "odom")

### If map isn't building:
- In RViz, ensure Fixed Frame is set to "map"
- Check: `ros2 topic echo /map` (should receive updates as robot moves)
- Drive the robot around to gather more scan data

---

**Solution implemented**: December 2, 2025  
**Tested on**: ROS 2 Humble, Ubuntu 22.04, Gazebo Fortress
