import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable # <--- Import this
import xacro

def generate_launch_description():
    pkg_name = 'robo_roomba_sim'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Process the Robot URDF
    xacro_file = os.path.join(pkg_share, 'urdf', 'roomba.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml()

    # 2. Tell Gazebo where to find our local meshes/textures
    # We add the 'worlds' directory to the Gazebo Resource Path
    worlds_path = os.path.join(pkg_share, 'worlds')
    set_res_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH', 
        value=worlds_path
    )

    # 3. Launch Gazebo with the world
    world_file = os.path.join(pkg_share, 'worlds', 'indoor.sdf')
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file],
        output='screen'
    )

    # 4. Spawn the Robot (Adjusted for Cafe World coordinates)
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'roomba', '-x', '0.0', '-y', '-5.0', '-z', '0.75'],
        output='screen'
    )

    # 5. Robot State Publisher (publishes robot's internal transforms: base_link->lidar_link, etc.)
    # Add tf_prefix to match Gazebo's frame naming
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_desc},
            {'use_sim_time': True},
            {'frame_prefix': 'roomba/'}  # Match Gazebo's model prefix
        ]
    )

    # 6. Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/model/roomba/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
        ],
        remappings=[
            ('/model/roomba/tf', '/tf'),
        ],
        output='screen'
    )

    return LaunchDescription([
        set_res_path, # <--- Run this first
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        bridge,
    ])