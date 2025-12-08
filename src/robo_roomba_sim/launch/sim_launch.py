import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable
import xacro

def generate_launch_description():
    pkg_name = 'robo_roomba_sim'
    pkg_share = get_package_share_directory(pkg_name)

    xacro_file = os.path.join(pkg_share, 'urdf', 'roomba.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml()

    worlds_path = os.path.join(pkg_share, 'worlds')
    set_res_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH', 
        value=worlds_path
    )

    world_file = os.path.join(pkg_share, 'worlds', 'indoor.sdf')
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file],
        output='screen'
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'roomba', '-x', '0.0', '-y', '-5.0', '-z', '0.75'],
        output='screen'
    )

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_desc},
            {'use_sim_time': True}
        ]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/world/cafe_on_null_island/model/roomba/link/base_link/sensor/bumper_sensor/contact@ros_gz_interfaces/msg/Contacts[ignition.msgs.Contacts',
        ],
        remappings=[
            ('/scan', '/scan_raw'),
            ('/world/cafe_on_null_island/model/roomba/link/base_link/sensor/bumper_sensor/contact', '/bumper'),
        ],
        output='screen'
    )

    odom_to_tf_node = Node(
        package='my_robot_pkg',
        executable='odom_to_tf',
        name='odom_to_tf',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    scan_remapper_node = Node(
        package='my_robot_pkg',
        executable='scan_remapper',
        name='scan_remapper',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        set_res_path,
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        bridge,
        odom_to_tf_node,
        scan_remapper_node,
    ])