import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # 1. Launch our Simulation (Gazebo + Robot)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('robo_roomba_sim'), 
                         'launch', 'sim_launch.py')
        )
    )

    # 2. SLAM Toolbox with Custom Configuration
    # Using our custom config with Gazebo's natural frame names
    slam_params_file = os.path.join(get_package_share_directory("robo_roomba_sim"),
                                    "config", "mapper_params_online_async.yaml")
    
    start_async_slam_toolbox_node = Node(
        parameters=[
          slam_params_file,
          {'use_sim_time': True}
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen')

    # 3. Rviz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        sim_launch,
        start_async_slam_toolbox_node,
        rviz
    ])