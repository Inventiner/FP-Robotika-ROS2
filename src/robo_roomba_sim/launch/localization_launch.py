import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Define paths
    # (Definisikan jalur paket)
    pkg_sim_share = get_package_share_directory('robo_roomba_sim')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Declare launch arguments
    # (Deklarasi argumen launch)
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
    
    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_sim_share, 'maps', 'cafe_map.yaml'),
        description='Full path to map file to load')
    
    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_sim_share, 'config', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use')
    
    # Use the launch arguments
    # (Gunakan argumen launch)
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    # 1. Launch the simulation environment
    # (1. Jalankan lingkungan simulasi)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim_share, 'launch', 'sim_launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 2. Launch the Nav2 stack
    # (2. Jalankan stack Nav2)
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_file,
            'params_file': params_file,
        }.items()
    )

    # 3. Launch RViz for visualization
    # (3. Jalankan RViz untuk visualisasi)
    rviz_config_file = os.path.join(pkg_sim_share, 'rviz', 'navigation.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_map_cmd,
        declare_params_file_cmd,
        sim_launch,
        nav2_bringup_launch,
        rviz_node
    ])