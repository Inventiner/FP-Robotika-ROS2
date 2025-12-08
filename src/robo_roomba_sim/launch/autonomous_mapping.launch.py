import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, DeclareLaunchArgument
from launch_ros.actions import Node
import xacro # Corrected import

def generate_launch_description():
    # --- DECLARE LAUNCH ARGUMENTS ---
    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    # --- DEFINE PATHS ---
    pkg_sim_share = get_package_share_directory('robo_roomba_sim')

    # --- SIMULATION COMPONENTS ---
    xacro_file = os.path.join(pkg_sim_share, 'urdf', 'roomba.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml() # Corrected function call

    set_res_path = SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', os.path.join(pkg_sim_share, 'worlds'))
    world_file = os.path.join(pkg_sim_share, 'worlds', 'indoor.sdf')
    gazebo = ExecuteProcess(cmd=['ign', 'gazebo', '-r', world_file], output='screen')
    spawn_entity = Node(package='ros_gz_sim', executable='create', arguments=['-topic', 'robot_description', '-name', 'roomba', '-x', '0.0', '-y', '-5.0', '-z', '0.75'], output='screen')

    # --- ROS 2 NODES ---    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_desc},
            {'frame_prefix': 'roomba/'}
        ]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/model/roomba/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/world/cafe_on_null_island/model/roomba/link/base_link/sensor/bumper_sensor/contact@ros_gz_interfaces/msg/Contacts[ignition.msgs.Contacts',
        ],
        remappings=[
            ('/model/roomba/tf', '/tf'),
            ('/world/cafe_on_null_island/model/roomba/link/base_link/sensor/bumper_sensor/contact', '/bumper')
        ],
        output='screen'
    )

    slam_params_file = os.path.join(pkg_sim_share, "config", "mapper_params_online_async.yaml")
    start_async_slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file]
    )
    rviz_config_file = os.path.join(pkg_sim_share, 'rviz', 'mapping.rviz')
    rviz = Node(package='rviz2', executable='rviz2', name='rviz2', output='screen', arguments=['-d', rviz_config_file])
    autonomous_driver_node = Node(package='my_robot_pkg', executable='cleaning_node', name='autonomous_driver', output='screen')

    return LaunchDescription([
        declare_use_sim_time_argument,
        set_res_path,
        gazebo,
        spawn_entity,
        node_robot_state_publisher,
        bridge,
        start_async_slam_toolbox_node,
        rviz,
        autonomous_driver_node
    ])